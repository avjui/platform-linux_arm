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

"""Unit tests for ssh_utils module."""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest

# Add parent directory to path to import ssh_utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ssh_utils import SSHConnectionConfig, SSHCommandBuilder, parse_upload_port


class TestSSHConnectionConfig:
    """Test cases for SSHConnectionConfig class."""

    def test_init_with_minimal_params(self):
        """Test initialization with only required parameters."""
        config = SSHConnectionConfig(user="testuser", host="testhost")

        assert config.user == "testuser"
        assert config.host == "testhost"
        assert config.port == "22"
        assert config.key is None
        assert config.strict_host_check is False

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        config = SSHConnectionConfig(
            user="pi",
            host="192.168.1.100",
            port="2222",
            key="~/.ssh/id_rsa",
            strict_host_check=True
        )

        assert config.user == "pi"
        assert config.host == "192.168.1.100"
        assert config.port == "2222"
        assert config.key == "~/.ssh/id_rsa"
        assert config.strict_host_check is True

    def test_init_with_custom_port(self):
        """Test initialization with custom port."""
        config = SSHConnectionConfig(
            user="admin",
            host="example.com",
            port="8022"
        )

        assert config.port == "8022"

    def test_validate_success_without_key(self):
        """Test validation passes with valid config without SSH key."""
        config = SSHConnectionConfig(user="testuser", host="testhost")

        # Should not raise any exception
        config.validate()

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_validate_success_with_existing_key(self, mock_expanduser, mock_exists):
        """Test validation passes with existing SSH key."""
        mock_expanduser.return_value = "/home/user/.ssh/id_rsa"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="testuser",
            host="testhost",
            key="~/.ssh/id_rsa"
        )

        # Should not raise any exception
        config.validate()
        mock_expanduser.assert_called_once_with("~/.ssh/id_rsa")
        mock_exists.assert_called_once_with("/home/user/.ssh/id_rsa")

    def test_validate_missing_user_raises_error(self):
        """Test validation raises ValueError when user is missing."""
        config = SSHConnectionConfig(user="", host="testhost")

        with pytest.raises(ValueError, match="User and host are required"):
            config.validate()

    def test_validate_missing_host_raises_error(self):
        """Test validation raises ValueError when host is missing."""
        config = SSHConnectionConfig(user="testuser", host="")

        with pytest.raises(ValueError, match="User and host are required"):
            config.validate()

    def test_validate_missing_user_and_host_raises_error(self):
        """Test validation raises ValueError when both user and host are missing."""
        config = SSHConnectionConfig(user="", host="")

        with pytest.raises(ValueError, match="User and host are required"):
            config.validate()

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_validate_nonexistent_key_raises_error(self, mock_expanduser, mock_exists):
        """Test validation raises FileNotFoundError when SSH key doesn't exist."""
        mock_expanduser.return_value = "/home/user/.ssh/missing_key"
        mock_exists.return_value = False

        config = SSHConnectionConfig(
            user="testuser",
            host="testhost",
            key="~/.ssh/missing_key"
        )

        with pytest.raises(FileNotFoundError, match="SSH key not found: /home/user/.ssh/missing_key"):
            config.validate()

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_validate_expands_tilde_in_key_path(self, mock_expanduser, mock_exists):
        """Test that validation expands ~ in SSH key path."""
        mock_expanduser.return_value = "/home/user/.ssh/id_rsa"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="testuser",
            host="testhost",
            key="~/.ssh/id_rsa"
        )

        config.validate()
        mock_expanduser.assert_called_once_with("~/.ssh/id_rsa")


class TestSSHCommandBuilder:
    """Test cases for SSHCommandBuilder class."""

    @patch('os.path.exists')
    def test_init_with_valid_config(self, mock_exists):
        """Test initialization with valid configuration."""
        config = SSHConnectionConfig(user="testuser", host="testhost")
        builder = SSHCommandBuilder(config)

        assert builder.config == config

    @patch('os.path.exists')
    def test_init_validates_config(self, mock_exists):
        """Test initialization calls validate on config."""
        config = SSHConnectionConfig(user="", host="testhost")

        with pytest.raises(ValueError, match="User and host are required"):
            SSHCommandBuilder(config)

    @patch('os.path.exists')
    def test_build_ssh_command_basic(self, mock_exists):
        """Test basic SSH command construction."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command()

        assert cmd[0] == "ssh"
        assert "-p" in cmd
        assert "22" in cmd
        assert "-o" in cmd
        assert "StrictHostKeyChecking=no" in cmd
        assert "UserKnownHostsFile=/dev/null" in cmd
        assert "LogLevel=ERROR" in cmd
        assert "pi@raspberrypi.local" in cmd

    @patch('os.path.exists')
    def test_build_ssh_command_with_remote_command(self, mock_exists):
        """Test SSH command with remote command."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command(remote_command="ls -la /home/pi")

        assert "pi@raspberrypi.local" in cmd
        assert "ls -la /home/pi" in cmd
        assert cmd[-1] == "ls -la /home/pi"

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_build_ssh_command_with_ssh_key(self, mock_expanduser, mock_exists):
        """Test SSH command with SSH key."""
        mock_expanduser.return_value = "/home/user/.ssh/id_rsa"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            key="~/.ssh/id_rsa"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command()

        assert "-i" in cmd
        assert "/home/user/.ssh/id_rsa" in cmd

    @patch('os.path.exists')
    def test_build_ssh_command_with_custom_port(self, mock_exists):
        """Test SSH command with custom port."""
        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            port="2222"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command()

        assert "-p" in cmd
        port_idx = cmd.index("-p")
        assert cmd[port_idx + 1] == "2222"

    @patch('os.path.exists')
    def test_build_ssh_command_with_extra_options(self, mock_exists):
        """Test SSH command with extra options."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command(extra_opts=["-v", "-C"])

        assert "-v" in cmd
        assert "-C" in cmd

    @patch('os.path.exists')
    def test_build_ssh_command_without_strict_host_checking(self, mock_exists):
        """Test SSH command has no strict host checking by default."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command()

        assert "-o" in cmd
        assert "StrictHostKeyChecking=no" in cmd
        assert "UserKnownHostsFile=/dev/null" in cmd

    @patch('os.path.exists')
    def test_build_ssh_command_with_strict_host_checking(self, mock_exists):
        """Test SSH command with strict host checking enabled."""
        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            strict_host_check=True
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command()

        # Should NOT include StrictHostKeyChecking=no when enabled
        assert "StrictHostKeyChecking=no" not in cmd
        assert "UserKnownHostsFile=/dev/null" not in cmd

    @patch('os.path.exists')
    def test_build_scp_command_basic(self, mock_exists):
        """Test basic SCP command construction."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_scp_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        assert cmd[0] == "scp"
        assert "-P" in cmd  # Note: SCP uses -P, not -p
        assert "22" in cmd
        assert "/tmp/program" in cmd
        assert "pi@raspberrypi.local:/home/pi/program" in cmd

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_build_scp_command_with_ssh_key(self, mock_expanduser, mock_exists):
        """Test SCP command with SSH key."""
        mock_expanduser.return_value = "/home/user/.ssh/id_rsa"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            key="~/.ssh/id_rsa"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_scp_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        assert "-i" in cmd
        assert "/home/user/.ssh/id_rsa" in cmd

    @patch('os.path.exists')
    def test_build_scp_command_with_custom_port(self, mock_exists):
        """Test SCP command with custom port."""
        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            port="2222"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_scp_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        assert "-P" in cmd  # SCP uses -P for port
        port_idx = cmd.index("-P")
        assert cmd[port_idx + 1] == "2222"

    @patch('os.path.exists')
    def test_build_scp_command_with_extra_flags(self, mock_exists):
        """Test SCP command with extra flags."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_scp_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program",
            extra_flags=["-r", "-v"]
        )

        assert "-r" in cmd
        assert "-v" in cmd

    @patch('os.path.exists')
    def test_build_scp_command_port_uses_capital_p(self, mock_exists):
        """Test that SCP command uses -P (not -p) for port parameter."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_scp_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        # Find -P flag
        assert "-P" in cmd
        # Ensure -p is not used (SSH uses -p, SCP uses -P)
        port_flags = [flag for flag in cmd if flag in ["-p", "-P"]]
        assert "-P" in port_flags
        assert "-p" not in port_flags

    @patch('os.path.exists')
    def test_build_rsync_command_basic(self, mock_exists):
        """Test basic rsync command construction."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_rsync_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        assert cmd[0] == "rsync"
        assert "-avz" in cmd
        assert "-e" in cmd
        assert "/tmp/program" in cmd
        assert "pi@raspberrypi.local:/home/pi/program" in cmd

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_build_rsync_command_with_ssh_key(self, mock_expanduser, mock_exists):
        """Test rsync command with SSH key."""
        mock_expanduser.return_value = "/home/user/.ssh/id_rsa"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            key="~/.ssh/id_rsa"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_rsync_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        # Find the -e flag and check SSH command contains key
        e_idx = cmd.index("-e")
        ssh_cmd = cmd[e_idx + 1]
        assert "ssh" in ssh_cmd
        assert "/home/user/.ssh/id_rsa" in ssh_cmd

    @patch('os.path.exists')
    def test_build_rsync_command_with_custom_flags(self, mock_exists):
        """Test rsync command with custom flags."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi.local")
        builder = SSHCommandBuilder(config)

        cmd = builder.build_rsync_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program",
            flags="-av --delete"
        )

        assert "-av" in cmd
        assert "--delete" in cmd

    @patch('os.path.exists')
    def test_build_rsync_command_ssh_string_properly_escaped(self, mock_exists):
        """Test that rsync SSH command string is properly escaped."""
        config = SSHConnectionConfig(
            user="pi",
            host="raspberrypi.local",
            port="2222"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_rsync_command(
            local_path="/tmp/program",
            remote_path="/home/pi/program"
        )

        # Find the -e flag
        e_idx = cmd.index("-e")
        ssh_cmd = cmd[e_idx + 1]

        # Should start with "ssh "
        assert ssh_cmd.startswith("ssh ")
        # Port should be included
        assert "2222" in ssh_cmd


class TestParseUploadPort:
    """Test cases for parse_upload_port function."""

    def test_parse_full_format_user_host_path(self):
        """Test parsing user@host:/path format."""
        user, host, path = parse_upload_port("pi@raspberrypi.local:/home/pi/program")

        assert user == "pi"
        assert host == "raspberrypi.local"
        assert path == "/home/pi/program"

    def test_parse_user_host_format(self):
        """Test parsing user@host format (no path)."""
        user, host, path = parse_upload_port("admin@example.com")

        assert user == "admin"
        assert host == "example.com"
        assert path == "/tmp/program"  # default path

    def test_parse_host_path_format(self):
        """Test parsing host:/path format (no user)."""
        user, host, path = parse_upload_port("raspberrypi.local:/opt/myapp")

        assert user == "pi"  # default user
        assert host == "raspberrypi.local"
        assert path == "/opt/myapp"

    def test_parse_host_only_format(self):
        """Test parsing host format (no user, no path)."""
        user, host, path = parse_upload_port("192.168.1.100")

        assert user == "pi"  # default user
        assert host == "192.168.1.100"
        assert path == "/tmp/program"  # default path

    def test_parse_with_custom_default_user(self):
        """Test parsing with custom default user."""
        user, host, path = parse_upload_port(
            "example.com",
            default_user="admin"
        )

        assert user == "admin"
        assert host == "example.com"
        assert path == "/tmp/program"

    def test_parse_with_custom_default_path(self):
        """Test parsing with custom default path."""
        user, host, path = parse_upload_port(
            "pi@raspberrypi.local",
            default_path="/home/pi/myapp"
        )

        assert user == "pi"
        assert host == "raspberrypi.local"
        assert path == "/home/pi/myapp"

    def test_parse_with_both_custom_defaults(self):
        """Test parsing with both custom defaults."""
        user, host, path = parse_upload_port(
            "example.com",
            default_user="root",
            default_path="/opt/app"
        )

        assert user == "root"
        assert host == "example.com"
        assert path == "/opt/app"

    def test_parse_empty_upload_port_raises_error(self):
        """Test that empty upload_port raises ValueError."""
        with pytest.raises(ValueError, match="upload_port is required"):
            parse_upload_port("")

    def test_parse_none_upload_port_raises_error(self):
        """Test that None upload_port raises ValueError."""
        with pytest.raises(ValueError, match="upload_port is required"):
            parse_upload_port(None)

    def test_parse_complex_path(self):
        """Test parsing with complex path containing special characters."""
        user, host, path = parse_upload_port("pi@raspberrypi.local:/home/pi/my app/program")

        assert user == "pi"
        assert host == "raspberrypi.local"
        assert path == "/home/pi/my app/program"

    def test_parse_ipv4_address(self):
        """Test parsing with IPv4 address as host."""
        user, host, path = parse_upload_port("root@192.168.1.100:/root/app")

        assert user == "root"
        assert host == "192.168.1.100"
        assert path == "/root/app"

    def test_parse_localhost(self):
        """Test parsing with localhost."""
        user, host, path = parse_upload_port("user@localhost:/tmp/test")

        assert user == "user"
        assert host == "localhost"
        assert path == "/tmp/test"


class TestSSHCommandBuilderIntegration:
    """Integration tests for SSHCommandBuilder with various scenarios."""

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_complete_workflow_ssh_with_all_options(self, mock_expanduser, mock_exists):
        """Test complete SSH workflow with all options."""
        mock_expanduser.return_value = "/home/user/.ssh/custom_key"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="deploy",
            host="production.example.com",
            port="8022",
            key="~/.ssh/custom_key",
            strict_host_check=True
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_ssh_command(
            remote_command="systemctl restart app",
            extra_opts=["-v"]
        )

        assert cmd[0] == "ssh"
        assert "-p" in cmd
        assert "8022" in cmd
        assert "-i" in cmd
        assert "/home/user/.ssh/custom_key" in cmd
        assert "-v" in cmd
        assert "deploy@production.example.com" in cmd
        assert "systemctl restart app" in cmd
        # Strict host checking enabled, so should NOT have these options
        assert "StrictHostKeyChecking=no" not in cmd

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_complete_workflow_scp_with_all_options(self, mock_expanduser, mock_exists):
        """Test complete SCP workflow with all options."""
        mock_expanduser.return_value = "/home/user/.ssh/deploy_key"
        mock_exists.return_value = True

        config = SSHConnectionConfig(
            user="deploy",
            host="production.example.com",
            port="8022",
            key="~/.ssh/deploy_key"
        )
        builder = SSHCommandBuilder(config)

        cmd = builder.build_scp_command(
            local_path="/tmp/app.tar.gz",
            remote_path="/opt/releases/app.tar.gz",
            extra_flags=["-C"]
        )

        assert cmd[0] == "scp"
        assert "-P" in cmd  # SCP uses -P
        assert "8022" in cmd
        assert "-i" in cmd
        assert "/home/user/.ssh/deploy_key" in cmd
        assert "-C" in cmd
        assert "/tmp/app.tar.gz" in cmd
        assert "deploy@production.example.com:/opt/releases/app.tar.gz" in cmd

    @patch('os.path.exists')
    def test_minimal_configuration_all_commands(self, mock_exists):
        """Test minimal configuration works for all command types."""
        config = SSHConnectionConfig(user="pi", host="raspberrypi")
        builder = SSHCommandBuilder(config)

        # SSH command
        ssh_cmd = builder.build_ssh_command()
        assert "pi@raspberrypi" in ssh_cmd

        # SCP command
        scp_cmd = builder.build_scp_command("/tmp/src", "/tmp/dst")
        assert "pi@raspberrypi:/tmp/dst" in scp_cmd

        # Rsync command
        rsync_cmd = builder.build_rsync_command("/tmp/src", "/tmp/dst")
        assert "pi@raspberrypi:/tmp/dst" in rsync_cmd


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
