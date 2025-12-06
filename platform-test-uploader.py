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
Remote SSH Test Uploader for Linux ARM Platform

This script uploads test binaries to a remote Linux ARM target via SSH,
executes them, and streams the output back to PlatformIO's test framework.
"""

import os
import shutil
import subprocess
import sys
import time


class RemoteTestUploader:
    """
    Handles uploading and executing test binaries on remote Linux ARM targets via SSH.
    """

    def __init__(self, target, source, env):
        self.target = target
        self.source = source
        self.env = env
        self.upload_port = None
        self.user = None
        self.host = None
        self.remote_path = None
        self.ssh_port = "22"
        self.ssh_key = None

    def parse_test_port(self):
        """
        Parse test_port configuration.
        Supported formats:
          - user@host:/path/to/test_binary
          - user@host
          - host:/path
          - host
        """
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

        # Default values
        self.user = self.env.GetProjectOption("test_username", "pi")
        self.remote_path = self.env.GetProjectOption("test_path", "/tmp/test_program")

        # Parse user@host:path format
        upload_port = self.upload_port

        # Extract user if specified
        if "@" in upload_port:
            user_part, host_part = upload_port.split("@", 1)
            self.user = user_part
        else:
            host_part = upload_port

        # Extract host and path
        if ":" in host_part:
            self.host, path_part = host_part.split(":", 1)
            self.remote_path = path_part
        else:
            self.host = host_part

        # Get SSH configuration
        self.ssh_port = self.env.GetProjectOption("test_ssh_port", "22")
        if not self.ssh_port:
            self.ssh_port = self.env.GetProjectOption("upload_ssh_port", "22")

        self.ssh_key = self.env.GetProjectOption("test_ssh_key", None)
        if not self.ssh_key:
            self.ssh_key = self.env.GetProjectOption("upload_ssh_key", None)

    def check_ssh_available(self):
        """Check if SSH is available on the system."""
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
        """Build SSH command with proper authentication."""
        cmd = ["ssh"]
        cmd.extend(["-p", str(self.ssh_port)])

        if self.ssh_key:
            key_path = os.path.expanduser(self.ssh_key)
            if not os.path.exists(key_path):
                raise Exception(f"SSH key file not found: {key_path}")
            cmd.extend(["-i", key_path])

        # Disable strict host key checking for automated testing
        # (can be overridden with custom SSH config)
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
        cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
        cmd.extend(["-o", "LogLevel=ERROR"])

        cmd.append(f"{self.user}@{self.host}")

        if remote_command:
            cmd.append(remote_command)

        return cmd

    def build_scp_command(self, local_file, remote_file):
        """Build SCP command for file upload."""
        cmd = ["scp"]
        cmd.extend(["-P", str(self.ssh_port)])

        if self.ssh_key:
            key_path = os.path.expanduser(self.ssh_key)
            cmd.extend(["-i", key_path])

        # Disable strict host key checking
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
        cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
        cmd.extend(["-o", "LogLevel=ERROR"])

        cmd.append(local_file)
        cmd.append(f"{self.user}@{self.host}:{remote_file}")

        return cmd

    def upload_test_binary(self):
        """Upload test binary to remote target via SCP."""
        source_file = str(self.source[0])

        print(f"\nUploading test binary to {self.user}@{self.host}:{self.remote_path}")

        # Upload the binary
        cmd = self.build_scp_command(source_file, self.remote_path)
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(
                f"Failed to upload test binary:\n"
                f"Command: {' '.join(cmd)}\n"
                f"Error: {result.stderr}"
            )

        # Make it executable
        chmod_cmd = self.build_ssh_command(f"chmod +x {self.remote_path}")
        result = subprocess.run(chmod_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(
                f"Failed to make test binary executable:\n"
                f"Error: {result.stderr}"
            )

        print(f"Upload successful: {self.remote_path}")

    def execute_test_binary(self):
        """
        Execute test binary on remote target and stream output.
        Returns the exit code of the test execution.
        """
        print(f"\nExecuting tests on {self.user}@{self.host}...")
        print("=" * 80)

        # Build command to execute the test
        # We want to capture both stdout and stderr, and get the exit code
        test_command = f"{self.remote_path}; echo \"__EXIT_CODE__:$?\""

        cmd = self.build_ssh_command(test_command)

        # Execute and stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        exit_code = 0
        output_lines = []

        # Stream output line by line
        for line in iter(process.stdout.readline, ""):
            if not line:
                break

            # Check for exit code marker
            if "__EXIT_CODE__:" in line:
                try:
                    exit_code = int(line.split("__EXIT_CODE__:")[1].strip())
                except (IndexError, ValueError):
                    pass
            else:
                # Print to console (PlatformIO captures this)
                print(line, end="")
                output_lines.append(line)

        process.wait()
        print("=" * 80)

        return exit_code

    def run(self):
        """Main entry point for the test uploader."""
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

        except Exception as e:
            print(f"\nERROR: {str(e)}", file=sys.stderr)
            return 1


def upload_test(target, source, env):
    """
    Entry point called by PlatformIO test framework.
    This function is registered as the upload handler for tests.
    """
    uploader = RemoteTestUploader(target, source, env)
    return uploader.run()


# Allow this script to be run standalone for testing
if __name__ == "__main__":
    print("This script is designed to be called by PlatformIO test framework.")
    print("Use 'pio test' to run tests with this uploader.")
    sys.exit(1)
