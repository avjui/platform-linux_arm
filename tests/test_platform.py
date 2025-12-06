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

"""Unit tests for platform.py module."""

import os
import sys
import platform as stdlib_platform  # Import stdlib platform first to avoid circular import
import importlib.util
from unittest.mock import Mock, patch, MagicMock, mock_open
import pytest

# Add parent directory to path for imports (after stdlib platform is imported)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platformio import exception

# Import platform.py module explicitly to avoid conflict with stdlib platform module
_platform_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "platform.py"
)
spec = importlib.util.spec_from_file_location("platform_module", _platform_path)
platform_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(platform_module)

# Make platform module available to patches
sys.modules['platform_module'] = platform_module


class TestLinuxArmPlatformInit:
    """Test cases for Linux_armPlatform initialization."""

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_init_loads_config(self, mock_base_init, mock_get_config, mock_platform_manifest):
        """Test that initialization loads platform configuration."""
        from platform_module import Linux_armPlatform

        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_base_init.return_value = None

        platform = Linux_armPlatform(mock_platform_manifest)

        mock_get_config.assert_called_once()
        assert platform._config == mock_config


class TestIsNative:
    """Test cases for _is_native static method."""

    @patch('platform_module.get_systype')
    def test_is_native_on_linux_arm(self, mock_get_systype):
        """Test _is_native returns True on linux_arm."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'linux_arm'
        assert Linux_armPlatform._is_native() is True

    @patch('platform_module.get_systype')
    def test_is_native_on_linux_aarch64(self, mock_get_systype):
        """Test _is_native returns True on linux_aarch64."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'linux_aarch64'
        assert Linux_armPlatform._is_native() is True

    @patch('platform_module.get_systype')
    def test_is_native_on_linux_x86_64(self, mock_get_systype):
        """Test _is_native returns False on linux_x86_64."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'linux_x86_64'
        assert Linux_armPlatform._is_native() is False

    @patch('platform_module.get_systype')
    def test_is_native_on_darwin_x86_64(self, mock_get_systype):
        """Test _is_native returns False on darwin_x86_64."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'darwin_x86_64'
        assert Linux_armPlatform._is_native() is False

    @patch('platform_module.get_systype')
    def test_is_native_on_windows(self, mock_get_systype):
        """Test _is_native returns False on Windows."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'windows_amd64'
        assert Linux_armPlatform._is_native() is False


class TestPackagesProperty:
    """Test cases for packages property (toolchain selection)."""

    @patch('platform_module.get_systype')
    @patch('platform_module.PlatformBase.packages', new_callable=lambda: property(lambda self: {
        'toolchain-gccarmlinuxgnueabi': {},
        'framework-wiringpi': {}
    }))
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_packages_excludes_toolchain_on_native_arm(
        self, mock_base_init, mock_get_config, mock_base_packages, mock_get_systype, mock_platform_manifest
    ):
        """Test packages property excludes toolchain on native ARM."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'linux_arm'
        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)
        packages = platform.packages

        assert 'toolchain-gccarmlinuxgnueabi' not in packages
        assert 'framework-wiringpi' in packages

    @patch('platform_module.get_systype')
    @patch('platform_module.PlatformBase.packages', new_callable=lambda: property(lambda self: {
        'toolchain-gccarmlinuxgnueabi': {},
        'framework-wiringpi': {}
    }))
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_packages_keeps_toolchain_on_darwin_x86_64(
        self, mock_base_init, mock_get_config, mock_base_packages, mock_get_systype, mock_platform_manifest
    ):
        """Test packages property keeps toolchain on macOS x86_64."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'darwin_x86_64'
        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)
        packages = platform.packages

        assert 'toolchain-gccarmlinuxgnueabi' in packages
        assert 'framework-wiringpi' in packages

    @patch('platform_module.get_systype')
    @patch('platform_module.PlatformBase.packages', new_callable=lambda: property(lambda self: {
        'toolchain-gccarmlinuxgnueabi': {},
        'framework-wiringpi': {}
    }))
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_packages_excludes_toolchain_on_linux_x86_64(
        self, mock_base_init, mock_get_config, mock_base_packages, mock_get_systype, mock_platform_manifest
    ):
        """Test packages property excludes toolchain on Linux x86_64."""
        from platform_module import Linux_armPlatform

        mock_get_systype.return_value = 'linux_x86_64'
        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)
        packages = platform.packages

        assert 'toolchain-gccarmlinuxgnueabi' not in packages


class TestConfigureDefaultPackages:
    """Test cases for configure_default_packages method."""

    @patch('platform_module.Linux_armPlatform._is_native')
    @patch('platform_module.PlatformBase.configure_default_packages')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_configure_blocks_wiringpi_cross_compilation(
        self, mock_base_init, mock_get_config, mock_base_configure, mock_is_native, mock_platform_manifest
    ):
        """Test that WiringPi cross-compilation is blocked."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_is_native.return_value = False  # Cross-compilation
        mock_base_configure.return_value = {}

        platform = Linux_armPlatform(mock_platform_manifest)

        variables = {"pioframework": ["wiringpi"]}
        targets = []

        with pytest.raises(exception.PlatformioException, match="does not support cross-compilation"):
            platform.configure_default_packages(variables, targets)

    @patch('platform_module.Linux_armPlatform._is_native')
    @patch('platform_module.PlatformBase.configure_default_packages')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_configure_allows_wiringpi_on_native(
        self, mock_base_init, mock_get_config, mock_base_configure, mock_is_native, mock_platform_manifest
    ):
        """Test that WiringPi is allowed on native ARM."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_is_native.return_value = True  # Native execution
        mock_base_configure.return_value = {}

        platform = Linux_armPlatform(mock_platform_manifest)

        variables = {"pioframework": ["wiringpi"]}
        targets = []

        # Should not raise exception
        result = platform.configure_default_packages(variables, targets)
        assert result == {}
        mock_base_configure.assert_called_once_with(variables, targets)

    @patch('platform_module.Linux_armPlatform._is_native')
    @patch('platform_module.PlatformBase.configure_default_packages')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_configure_allows_non_wiringpi_cross_compilation(
        self, mock_base_init, mock_get_config, mock_base_configure, mock_is_native, mock_platform_manifest
    ):
        """Test that non-WiringPi frameworks work with cross-compilation."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_is_native.return_value = False  # Cross-compilation
        mock_base_configure.return_value = {}

        platform = Linux_armPlatform(mock_platform_manifest)

        variables = {"pioframework": ["lgpio"]}
        targets = []

        # Should not raise exception
        result = platform.configure_default_packages(variables, targets)
        assert result == {}


class TestGetUploadProtocol:
    """Test cases for _get_upload_protocol method."""

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_get_upload_protocol_valid_scp(
        self, mock_base_init, mock_get_config, mock_platform_manifest, mock_env
    ):
        """Test getting valid SCP upload protocol."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)
        mock_env.GetProjectOption = Mock(return_value="scp")

        protocol = platform._get_upload_protocol(mock_env)
        assert protocol == "scp"

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_get_upload_protocol_invalid(
        self, mock_base_init, mock_get_config, mock_platform_manifest, mock_env
    ):
        """Test that invalid upload protocol raises exception."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)
        mock_env.GetProjectOption = Mock(return_value="invalid_protocol")

        with pytest.raises(exception.PlatformioException, match="Unknown upload protocol"):
            platform._get_upload_protocol(mock_env)


class TestCheckUploadTool:
    """Test cases for _check_upload_tool method."""

    @patch('shutil.which')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_check_upload_tool_available(
        self, mock_base_init, mock_get_config, mock_which, mock_platform_manifest
    ):
        """Test check passes when tool is available."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_which.return_value = "/usr/bin/scp"

        platform = Linux_armPlatform(mock_platform_manifest)

        # Should not raise exception
        platform._check_upload_tool("scp")
        mock_which.assert_called_once_with("scp")

    @patch('shutil.which')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_check_upload_tool_missing(
        self, mock_base_init, mock_get_config, mock_which, mock_platform_manifest
    ):
        """Test check raises exception when tool is missing."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_which.return_value = None

        platform = Linux_armPlatform(mock_platform_manifest)

        with pytest.raises(exception.PlatformioException, match="is not installed"):
            platform._check_upload_tool("rsync")


class TestParseUploadPort:
    """Test cases for _parse_upload_port method."""

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_parse_upload_port_full_format(
        self, mock_base_init, mock_get_config, mock_platform_manifest, mock_env
    ):
        """Test parsing full user@host:/path format."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)

        user, host, path = platform._parse_upload_port("pi@raspberrypi:/tmp/prog", mock_env)

        assert user == "pi"
        assert host == "raspberrypi"
        assert path == "/tmp/prog"

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_parse_upload_port_none_raises_error(
        self, mock_base_init, mock_get_config, mock_platform_manifest, mock_env
    ):
        """Test that None upload_port raises exception."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)

        with pytest.raises(exception.PlatformioException, match="upload_port is not configured"):
            platform._parse_upload_port(None, mock_env)

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_parse_upload_port_empty_raises_error(
        self, mock_base_init, mock_get_config, mock_platform_manifest, mock_env
    ):
        """Test that empty upload_port raises exception."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)

        with pytest.raises(exception.PlatformioException, match="upload_port is not configured"):
            platform._parse_upload_port("", mock_env)


class TestDetermineGdbExecutable:
    """Test cases for _determine_gdb_executable method."""

    @patch('shutil.which')
    @patch('platform_module.Linux_armPlatform._is_native')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_determine_gdb_native(
        self, mock_base_init, mock_get_config, mock_is_native, mock_which, mock_platform_manifest
    ):
        """Test GDB executable determination on native ARM."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_is_native.return_value = True
        mock_which.return_value = "gdb"  # Mock shutil.which() to find gdb

        platform = Linux_armPlatform(mock_platform_manifest)

        gdb_path = platform._determine_gdb_executable("armv7")
        assert gdb_path == "gdb"

    @patch('shutil.which')
    @patch('platform_module.Linux_armPlatform._is_native')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_determine_gdb_cross_aarch64(
        self, mock_base_init, mock_get_config, mock_is_native, mock_which, mock_platform_manifest
    ):
        """Test GDB executable for cross-compilation to aarch64."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_is_native.return_value = False

        # Mock shutil.which() to simulate arch-specific GDB being available
        # Return None for gdb-multiarch, return the command for arch-specific GDB
        def which_side_effect(cmd):
            if cmd == "aarch64-linux-gnu-gdb":
                return cmd
            return None
        mock_which.side_effect = which_side_effect

        platform = Linux_armPlatform(mock_platform_manifest)

        gdb_path = platform._determine_gdb_executable("aarch64")
        assert gdb_path == "aarch64-linux-gnu-gdb"

    @patch('shutil.which')
    @patch('platform_module.Linux_armPlatform._is_native')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_determine_gdb_cross_armv7(
        self, mock_base_init, mock_get_config, mock_is_native, mock_which, mock_platform_manifest
    ):
        """Test GDB executable for cross-compilation to armv7."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()
        mock_is_native.return_value = False

        # Mock shutil.which() to simulate arch-specific GDB being available
        # Return None for gdb-multiarch, return the command for arch-specific GDB
        def which_side_effect(cmd):
            if cmd == "arm-linux-gnueabihf-gdb":
                return cmd
            return None
        mock_which.side_effect = which_side_effect

        platform = Linux_armPlatform(mock_platform_manifest)

        gdb_path = platform._determine_gdb_executable("armv7")
        assert gdb_path == "arm-linux-gnueabihf-gdb"


class TestGetConfigDefault:
    """Test cases for _get_config_default method."""

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_get_config_default_from_config(
        self, mock_base_init, mock_get_config, mock_platform_manifest
    ):
        """Test getting config value from config file."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_config = Mock()
        mock_config.get = Mock(return_value=600)
        mock_get_config.return_value = mock_config

        platform = Linux_armPlatform(mock_platform_manifest)

        value = platform._get_config_default("upload_timeout", 300)
        assert value == 600
        mock_config.get.assert_called_once_with("upload_timeout", 300)

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_get_config_default_fallback(
        self, mock_base_init, mock_get_config, mock_platform_manifest
    ):
        """Test getting config value falls back to default."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_config = Mock()
        mock_config.get = Mock(return_value=300)  # Returns fallback
        mock_get_config.return_value = mock_config

        platform = Linux_armPlatform(mock_platform_manifest)

        value = platform._get_config_default("upload_timeout", 300)
        assert value == 300


class TestShowManualUploadInstructions:
    """Test cases for _show_manual_upload_instructions method."""

    @patch('builtins.print')
    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_show_manual_upload_instructions(
        self, mock_base_init, mock_get_config, mock_print, mock_platform_manifest
    ):
        """Test manual upload instructions display."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)

        source = ["/path/to/binary"]
        result = platform._show_manual_upload_instructions(source)

        assert result == 0
        # Verify some key output was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("MANUAL UPLOAD" in str(call) for call in print_calls)


class TestAddDebugToBoard:
    """Test cases for _add_debug_to_board method."""

    @patch('platform_module.get_platform_config')
    @patch('platform_module.PlatformBase.__init__')
    def test_add_debug_to_board(
        self, mock_base_init, mock_get_config, mock_platform_manifest, mock_board_config
    ):
        """Test adding debug configuration to board."""
        from platform_module import Linux_armPlatform

        mock_base_init.return_value = None
        mock_get_config.return_value = Mock()

        platform = Linux_armPlatform(mock_platform_manifest)

        board = platform._add_debug_to_board(mock_board_config)

        assert "debug" in board.manifest
        assert "tools" in board.manifest["debug"]
        assert "gdbserver-ssh" in board.manifest["debug"]["tools"]
        assert "gdb-remote" in board.manifest["debug"]["tools"]
        assert "default" in board.manifest["debug"]
        assert board.manifest["debug"]["default"] == "gdbserver-ssh"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
