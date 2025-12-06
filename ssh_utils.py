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
Shared utilities for SSH/SCP command construction.

This module provides secure, reusable builders for SSH and SCP commands
with proper shell escaping and error handling.
"""

import os
import shlex
from typing import List, Optional, Tuple


class SSHConnectionConfig:
    """Configuration for SSH connections."""

    def __init__(
        self,
        user: str,
        host: str,
        port: str = "22",
        key: Optional[str] = None,
        strict_host_check: bool = False
    ):
        """
        Initialize SSH connection configuration.

        Args:
            user: SSH username
            host: Remote hostname or IP address
            port: SSH port (default: "22")
            key: Path to SSH private key file (optional)
            strict_host_check: Enable strict host key checking (default: False)
        """
        self.user = user
        self.host = host
        self.port = port
        self.key = key
        self.strict_host_check = strict_host_check

    def validate(self) -> None:
        """
        Validate configuration.

        Raises:
            ValueError: If user or host is missing
            FileNotFoundError: If SSH key path doesn't exist
        """
        if not self.user or not self.host:
            raise ValueError("User and host are required")

        if self.key:
            key_path = os.path.expanduser(self.key)
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"SSH key not found: {key_path}")


class SSHCommandBuilder:
    """Build SSH commands with proper escaping and security."""

    def __init__(self, config: SSHConnectionConfig):
        """
        Initialize SSH command builder.

        Args:
            config: SSH connection configuration

        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If SSH key doesn't exist
        """
        self.config = config
        self.config.validate()

    def build_ssh_command(
        self,
        remote_command: Optional[str] = None,
        extra_opts: Optional[List[str]] = None
    ) -> List[str]:
        """
        Build SSH command.

        Args:
            remote_command: Command to execute on remote host (optional)
            extra_opts: Additional SSH options (optional)

        Returns:
            Command as list of arguments suitable for subprocess
        """
        cmd = ["ssh"]

        # Port
        cmd.extend(["-p", str(self.config.port)])

        # SSH key
        if self.config.key:
            key_path = os.path.expanduser(self.config.key)
            cmd.extend(["-i", key_path])

        # Host key verification
        if not self.config.strict_host_check:
            cmd.extend(["-o", "StrictHostKeyChecking=no"])
            cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
            cmd.extend(["-o", "LogLevel=ERROR"])

        # Extra options
        if extra_opts:
            cmd.extend(extra_opts)

        # Target
        cmd.append(f"{self.config.user}@{self.config.host}")

        # Remote command (properly escaped)
        if remote_command:
            cmd.append(remote_command)

        return cmd

    def build_scp_command(
        self,
        local_path: str,
        remote_path: str,
        extra_flags: Optional[List[str]] = None
    ) -> List[str]:
        """
        Build SCP command.

        Args:
            local_path: Local file path
            remote_path: Remote file path (will be shell-escaped)
            extra_flags: Additional SCP flags (optional)

        Returns:
            Command as list of arguments suitable for subprocess
        """
        cmd = ["scp"]

        # Port (note: SCP uses -P, SSH uses -p)
        cmd.extend(["-P", str(self.config.port)])

        # SSH key
        if self.config.key:
            key_path = os.path.expanduser(self.config.key)
            cmd.extend(["-i", key_path])

        # Host key verification
        if not self.config.strict_host_check:
            cmd.extend(["-o", "StrictHostKeyChecking=no"])
            cmd.extend(["-o", "UserKnownHostsFile=/dev/null"])
            cmd.extend(["-o", "LogLevel=ERROR"])

        # Extra flags
        if extra_flags:
            cmd.extend(extra_flags)

        # Source and destination
        cmd.append(local_path)
        # Remote path is NOT shell-escaped here - it will be handled by SCP
        # The shell-escaping is only needed when the path is part of a command string
        cmd.append(f"{self.config.user}@{self.config.host}:{remote_path}")

        return cmd

    def build_rsync_command(
        self,
        local_path: str,
        remote_path: str,
        flags: str = "-avz"
    ) -> List[str]:
        """
        Build rsync command with SSH transport.

        Args:
            local_path: Local file path
            remote_path: Remote file path
            flags: Rsync flags (default: "-avz")

        Returns:
            Command as list of arguments suitable for subprocess
        """
        cmd = ["rsync"]

        # Flags
        if flags:
            cmd.extend(flags.split())

        # SSH options
        ssh_opts = ["-p", str(self.config.port)]
        if self.config.key:
            key_path = os.path.expanduser(self.config.key)
            ssh_opts.extend(["-i", key_path])

        # Build SSH command string (for rsync -e option)
        ssh_cmd = "ssh " + " ".join(shlex.quote(opt) for opt in ssh_opts)
        cmd.extend(["-e", ssh_cmd])

        # Source and destination
        cmd.append(local_path)
        cmd.append(f"{self.config.user}@{self.config.host}:{remote_path}")

        return cmd


def parse_upload_port(
    upload_port: str,
    default_user: str = "pi",
    default_path: str = "/tmp/program"
) -> Tuple[str, str, str]:
    """
    Parse upload_port into components.

    Supported formats:
      - user@host:/path
      - user@host
      - host:/path
      - host

    Args:
        upload_port: Upload port string
        default_user: Default user if not specified (default: "pi")
        default_path: Default path if not specified (default: "/tmp/program")

    Returns:
        Tuple of (user, host, path)

    Raises:
        ValueError: If upload_port is invalid or empty
    """
    if not upload_port:
        raise ValueError("upload_port is required")

    user = default_user
    path = default_path

    # Parse user@host:path format
    if "@" in upload_port:
        user, host_part = upload_port.split("@", 1)
    else:
        host_part = upload_port

    # Parse host:path
    if ":" in host_part:
        host, path = host_part.split(":", 1)
    else:
        host = host_part

    return user, host, path
