#!/usr/bin/env python3
# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Remote SSH Test Uploader for Linux ARM Platform.

This module handles uploading and executing test binaries on remote Linux ARM
targets via SSH/SCP, with real-time output streaming back to PlatformIO's test
framework.

Features:
    - Automatic test binary upload via SCP
    - Remote execution with exit code capture
    - Real-time output streaming
    - Configurable SSH authentication (password, key)
    - Error handling and timeout support

Usage:
    This module is automatically invoked by PlatformIO when:
        pio test

    Configuration in platformio.ini:
        [env:raspberrypi_4b]
        test_transport = ssh
        test_port = pi@raspberrypi.local:/tmp/test_program

Security:
    - SSH host key verification disabled by default (for CI/CD automation)
    - Use strict checking for production: test_strict_host_check = yes
    - Requires SSH key or password authentication
    - Command injection protection via shlex.quote

See REMOTE_TESTING.md for detailed documentation.
"""

import os
import shlex
import shutil
import subprocess
import sys
import time

from ssh_utils import SSHConnectionConfig, SSHCommandBuilder, parse_upload_port
from platform_config import get_platform_config


class RemoteTestUploader:
    """
    Handles uploading and executing test binaries on remote Linux ARM targets via SSH.

    This class manages the complete remote testing workflow:
        1. Parse test configuration (host, port, credentials)
        2. Upload test binary via SCP
        3. Execute tests remotely with output streaming
        4. Capture and return exit code

    Attributes:
        target: Build target from PlatformIO.
        source: List of source files (test binary path).
        env: PlatformIO environment object.
        upload_port: SSH connection string (user@host:/path).
        user: SSH username.
        host: SSH hostname or IP address.
        remote_path: Remote path for test binary.
        ssh_port: SSH port number (default: 22).
        ssh_key: Path to SSH private key file (optional).

    Examples:
        Typically invoked automatically by PlatformIO test framework:

        >>> uploader = RemoteTestUploader(target, source, env)
        >>> exit_code = uploader.run()

    See Also:
        - docs/TESTING.md: Remote testing documentation
        - platform.on_test_upload: Integration with PlatformIO
    """

    def __init__(self, target, source, env):
        """
        Initialize the remote test uploader.

        Args:
            target: Build target from PlatformIO.
            source: List of source files (test binary path).
            env: PlatformIO environment object for configuration retrieval.
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import SSHDefaults

        self.target = target
        self.source = source
        self.env = env
        self.upload_port = None
        self.user = None
        self.host = None
        self.remote_path = None
        self.ssh_port = SSHDefaults.PORT
        self.ssh_key = None

        # Load platform configuration for defaults
        self._config = get_platform_config()

    def _get_config_default(self, key: str, fallback_default):
        """
        Get configuration default value from config files.

        Args:
            key: Configuration key
            fallback_default: Fallback value if not in config files

        Returns:
            Configuration value from config file, or fallback_default
        """
        return self._config.get(key, fallback_default)

    def parse_test_port(self):
        """
        Parse test_port configuration into connection components.

        Supported formats:
            - user@host:/path/to/test_binary
            - user@host (uses default path)
            - host:/path (uses default user)
            - host (uses defaults for both)

        Raises:
            Exception: If test_port and upload_port are both not configured.

        Note:
            Falls back to upload_port if test_port is not specified.
            Default values can be overridden via test_username and test_path options.
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import SSHDefaults

        # Get test_port (preferred) or fallback to upload_port
        self.upload_port = self.env.GetProjectOption("test_port", None)
        if not self.upload_port:
            self.upload_port = self.env.GetProjectOption("upload_port", None)

        if not self.upload_port:
            raise Exception(
                "test_port or upload_port is not configured. Add to platformio.ini:\n"
                "  test_port = user@hostname:/path/to/test_binary\n"
                "  or\n"
                "  upload_port = user@hostname:/path/to/test_binary"
            )

        # Get defaults from project options (with config file fallback)
        default_user = self.env.GetProjectOption("test_username", self._get_config_default("test_username", SSHDefaults.USER))
        default_path = self.env.GetProjectOption("test_path", self._get_config_default("test_path", SSHDefaults.TEST_PATH))

        # Use shared parser
        try:
            self.user, self.host, self.remote_path = parse_upload_port(
                self.upload_port,
                default_user=default_user,
                default_path=default_path
            )
        except ValueError as e:
            raise Exception(str(e))

        # Get SSH configuration (with config file fallback)
        self.ssh_port = self.env.GetProjectOption("test_ssh_port",
            self._get_config_default("test_ssh_port", SSHDefaults.PORT))
        if not self.ssh_port:
            self.ssh_port = self.env.GetProjectOption("upload_ssh_port",
                self._get_config_default("upload_ssh_port", SSHDefaults.PORT))

        self.ssh_key = self.env.GetProjectOption("test_ssh_key",
            self._get_config_default("test_ssh_key", None))
        if not self.ssh_key:
            self.ssh_key = self.env.GetProjectOption("upload_ssh_key",
                self._get_config_default("upload_ssh_key", None))

    def check_ssh_available(self):
        """
        Check if SSH and SCP are available on the system.

        Raises:
            Exception: If SSH or SCP is not found in system PATH.

        Note:
            Provides platform-specific installation instructions for missing tools.
        """
        if not shutil.which("ssh"):
            raise Exception(
                "SSH is not installed. Please install it using your system package manager:\n"
                "  Linux: sudo apt install openssh-client\n"
                "  macOS: SSH is pre-installed"
            )
        if not shutil.which("scp"):
            raise Exception(
                "SCP is not installed. Please install it using your system package manager:\n"
                "  Linux: sudo apt install openssh-client\n"
                "  macOS: SCP is pre-installed"
            )

    def build_ssh_command(self, remote_command=None):
        """
        Build SSH command with proper authentication.

        Args:
            remote_command: Optional command to execute on remote host.

        Returns:
            list: SSH command parts ready for subprocess execution.

        Raises:
            Exception: If SSH configuration is invalid.

        Note:
            Automatically configures port, key authentication, and host key verification.
        """
        # Create SSH config
        try:
            config = SSHConnectionConfig(
                user=self.user,
                host=self.host,
                port=self.ssh_port,
                key=self.ssh_key,
                strict_host_check=False
            )
        except (ValueError, FileNotFoundError) as e:
            raise Exception(str(e))

        # Build SSH command using shared builder
        builder = SSHCommandBuilder(config)
        return builder.build_ssh_command(remote_command)

    def build_scp_command(self, local_file, remote_file):
        """
        Build SCP command for file upload.

        Args:
            local_file: Path to local file to upload.
            remote_file: Remote destination path.

        Returns:
            list: SCP command parts ready for subprocess execution.

        Raises:
            Exception: If SSH configuration is invalid.

        Note:
            Uses shared SSH configuration (port, key, host verification).
        """
        # Create SSH config
        try:
            config = SSHConnectionConfig(
                user=self.user,
                host=self.host,
                port=self.ssh_port,
                key=self.ssh_key,
                strict_host_check=False
            )
        except (ValueError, FileNotFoundError) as e:
            raise Exception(str(e))

        # Build SCP command using shared builder
        builder = SSHCommandBuilder(config)
        return builder.build_scp_command(local_file, remote_file)

    def upload_test_binary(self) -> int:
        """
        Upload test binary to remote target via SCP.

        Uploads the test binary and makes it executable on the remote host.

        Returns:
            int: Exit code (0 for success).

        Raises:
            Exception: If upload fails, timeout occurs, or chmod fails.

        Note:
            Default timeout: 120 seconds (configurable via test_upload_timeout).
            Automatically runs 'chmod +x' on the uploaded binary.
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import Timeouts

        source_file = str(self.source[0])

        print(f"\nUploading test binary to {self.user}@{self.host}:{self.remote_path}")

        # Upload the binary with timeout protection
        upload_timeout = self.env.GetProjectOption("test_upload_timeout",
            self._get_config_default("test_upload_timeout", Timeouts.TEST_UPLOAD))
        cmd = self.build_scp_command(source_file, self.remote_path)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=upload_timeout)
        except subprocess.TimeoutExpired:
            raise Exception(
                f"Test upload timeout after {upload_timeout} seconds. "
                "Increase timeout with 'test_upload_timeout' option in platformio.ini"
            )

        if result.returncode != 0:
            raise Exception(
                f"Failed to upload test binary:\n"
                f"Command: {' '.join(cmd)}\n"
                f"Error: {result.stderr}"
            )

        # Make it executable (use shlex.quote to prevent command injection)
        chmod_cmd = self.build_ssh_command(f"chmod +x {shlex.quote(self.remote_path)}")
        try:
            result = subprocess.run(chmod_cmd, capture_output=True, text=True, timeout=Timeouts.CHMOD)
        except subprocess.TimeoutExpired:
            raise Exception("Timeout while setting executable permission on remote test binary")

        if result.returncode != 0:
            raise Exception(
                f"Failed to make test binary executable:\n"
                f"Error: {result.stderr}"
            )

        print(f"Upload successful: {self.remote_path}")
        return 0

    def _build_test_command(self) -> str:
        """
        Build remote test execution command with exit code capture.

        Returns:
            Remote shell command string
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import TestConstants

        # Use shlex.quote to prevent command injection via remote_path
        return f"{shlex.quote(self.remote_path)}; echo \"{TestConstants.EXIT_CODE_MARKER}$?\""

    def _stream_test_output(self, process, test_timeout: int) -> int:
        """
        Stream test output from remote process and extract exit code.

        Args:
            process: subprocess.Popen instance
            test_timeout: Timeout in seconds

        Returns:
            Exit code from test execution

        Raises:
            Exception: If test execution times out
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import TestConstants

        exit_code = 0

        try:
            # Stream output line by line
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break

                # Check for exit code marker
                if TestConstants.EXIT_CODE_MARKER in line:
                    exit_code = self._extract_exit_code(line)
                else:
                    # Print to console (PlatformIO captures this)
                    print(line, end="")

            # Wait for process to complete with timeout
            process.wait(timeout=test_timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise Exception(
                f"Test execution timeout after {test_timeout} seconds. "
                "Increase timeout with 'test_timeout' option in platformio.ini"
            )

        return exit_code

    def _extract_exit_code(self, line: str) -> int:
        """
        Extract exit code from marker line.

        Args:
            line: Output line containing exit code marker

        Returns:
            Extracted exit code, or 0 if extraction fails
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import TestConstants

        try:
            return int(line.split(TestConstants.EXIT_CODE_MARKER)[1].strip())
        except (IndexError, ValueError):
            return 0

    def execute_test_binary(self) -> int:
        """
        Execute test binary on remote target and stream output.

        Returns:
            Exit code from test execution
        """
        # Lazy import to avoid breaking platform loading
        from platform_constants import Timeouts

        print(f"\nExecuting tests on {self.user}@{self.host}...")
        print("=" * 80)

        # Build and execute test command
        test_command = self._build_test_command()
        cmd = self.build_ssh_command(test_command)
        test_timeout = self.env.GetProjectOption("test_timeout",
            self._get_config_default("test_timeout", Timeouts.TEST_EXECUTION))

        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Stream output and get exit code
        try:
            exit_code = self._stream_test_output(process, test_timeout)
        finally:
            print("=" * 80)

        return exit_code

    def run(self) -> int:
        """
        Run the complete remote testing workflow.

        Orchestrates the complete remote testing workflow:
            1. Parse configuration
            2. Check prerequisites
            3. Upload test binary
            4. Execute tests
            5. Return exit code

        Returns:
            int: Exit code from test execution (0 for success, non-zero for failure).

        Note:
            Handles all exceptions and returns appropriate exit codes.
            Provides user-friendly error messages for common failures.
        """
        try:
            # Parse configuration
            self.parse_test_port()

            # Check prerequisites
            self.check_ssh_available()

            # Upload test binary
            self.upload_test_binary()

            # Execute tests and return exit code
            exit_code = self.execute_test_binary()

            if exit_code == 0:
                print("\nTests PASSED")
            else:
                print(f"\nTests FAILED (exit code: {exit_code})")

            return exit_code

        except subprocess.TimeoutExpired as e:
            print(f"\nERROR: Operation timed out after {e.timeout} seconds", file=sys.stderr)
            print("Increase timeout with 'test_timeout' or 'test_upload_timeout' option in platformio.ini", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as e:
            print(f"\nERROR: Remote command failed: {e}", file=sys.stderr)
            print(f"Exit code: {e.returncode}", file=sys.stderr)
            if e.stderr:
                print(f"Error output: {e.stderr}", file=sys.stderr)
            return e.returncode
        except (OSError, FileNotFoundError) as e:
            print(f"\nERROR: File operation failed: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"\nERROR: Configuration error: {e}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nERROR: Operation cancelled by user", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"\nERROR: Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1


def upload_test(target, source, env) -> int:
    """
    Entry point called by PlatformIO test framework.

    This function is registered as the upload handler for tests and is
    automatically invoked when 'pio test' is executed with test_transport=ssh.

    Args:
        target: Build target from PlatformIO.
        source: List of source files (test binary path).
        env: PlatformIO environment object.

    Returns:
        int: Exit code from test execution (0 for success).

    Examples:
        Automatically called by PlatformIO test framework:

        >>> # platformio.ini
        >>> [env:raspberrypi_4b]
        >>> test_transport = ssh
        >>> test_port = pi@raspberrypi.local:/tmp/test

        >>> # Command line
        >>> $ pio test

    See Also:
        - RemoteTestUploader: Main implementation class
        - platform.on_test_upload: Platform integration
    """
    uploader = RemoteTestUploader(target, source, env)
    return uploader.run()


# Allow this script to be run standalone for testing
if __name__ == "__main__":
    print("This script is designed to be called by PlatformIO test framework.")
    print("Use 'pio test' to run tests with this uploader.")
    sys.exit(1)
