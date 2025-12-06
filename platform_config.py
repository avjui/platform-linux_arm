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
Platform Configuration File Support

Provides support for .platform-linux_arm.ini configuration files to set
global defaults, reducing duplication across projects.

Configuration File Locations (in priority order):
    1. Project-local: ./.platform-linux_arm.ini
    2. Global: ~/.platformio/.platform-linux_arm.ini

Configuration Priority:
    platformio.ini > project-local config > global config > hard-coded defaults

Supported Configuration Options:
    [defaults]
    upload_timeout = 300
    upload_user = pi
    upload_ssh_port = 22
    upload_path = /tmp/program
    upload_run_timeout = 300
    test_timeout = 600
    test_upload_timeout = 300
    test_username = pi
    test_path = /tmp/test_program
    test_ssh_port = 22

Example Usage:
    >>> config = PlatformConfig()
    >>> timeout = config.get('upload_timeout', 300)
    >>> user = config.get('upload_user', 'pi')

See Also:
    - Issue #73: Add Configuration File Support
    - CLAUDE.md: Project documentation
"""

import configparser
import os
from pathlib import Path
from typing import Optional, Union


class PlatformConfig:
    """
    Configuration file loader for platform-linux_arm.

    Loads and merges configuration from global and project-local config files,
    providing a simple interface for retrieving configuration values with
    proper priority handling.

    Attributes:
        _config: Merged configuration from all sources
        _global_path: Path to global config file
        _project_path: Path to project-local config file
        _loaded_files: List of successfully loaded config files

    Examples:
        >>> config = PlatformConfig()
        >>> upload_timeout = config.get('upload_timeout', default=300)
        >>> upload_user = config.get('upload_user', default='pi')

    Note:
        Configuration files use INI format with a [defaults] section.
        If a config file doesn't exist or can't be read, it's silently skipped.
    """

    # Configuration file name
    CONFIG_FILENAME = ".platform-linux_arm.ini"

    # Configuration section name
    CONFIG_SECTION = "defaults"

    def __init__(self, project_dir: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            project_dir: Optional project directory path. If None, uses current
                working directory. This is used to locate project-local config.

        Note:
            Config files are loaded immediately during initialization.
            Missing config files are silently ignored (backward compatible).
        """
        self._config = {}
        self._loaded_files = []

        # Determine configuration file paths
        self._global_path = self._get_global_config_path()
        self._project_path = self._get_project_config_path(project_dir)

        # Load configurations (global first, then project-local)
        self._load_config_files()

    def _get_global_config_path(self) -> Path:
        """
        Get path to global configuration file.

        Returns:
            Path to ~/.platformio/.platform-linux_arm.ini

        Note:
            Uses PLATFORMIO_CORE_DIR environment variable if set,
            otherwise defaults to ~/.platformio/
        """
        # Check for PLATFORMIO_CORE_DIR environment variable
        platformio_dir = os.environ.get('PLATFORMIO_CORE_DIR')
        if platformio_dir:
            return Path(platformio_dir) / self.CONFIG_FILENAME

        # Default to ~/.platformio/
        return Path.home() / ".platformio" / self.CONFIG_FILENAME

    def _get_project_config_path(self, project_dir: Optional[str] = None) -> Path:
        """
        Get path to project-local configuration file.

        Args:
            project_dir: Optional project directory path. If None, uses current
                working directory.

        Returns:
            Path to project-local .platform-linux_arm.ini
        """
        if project_dir:
            return Path(project_dir) / self.CONFIG_FILENAME

        # Use current working directory
        return Path.cwd() / self.CONFIG_FILENAME

    def _load_config_file(self, config_path: Path) -> dict:
        """
        Load a single configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary of configuration key-value pairs from [defaults] section.
            Returns empty dict if file doesn't exist or can't be read.

        Note:
            Errors are silently ignored for backward compatibility.
            Only the [defaults] section is read.
        """
        if not config_path.exists():
            return {}

        try:
            parser = configparser.ConfigParser()
            parser.read(config_path)

            # Extract [defaults] section
            if self.CONFIG_SECTION in parser:
                self._loaded_files.append(str(config_path))
                return dict(parser[self.CONFIG_SECTION])

            return {}

        except (configparser.Error, OSError, IOError):
            # Silently ignore errors for backward compatibility
            return {}

    def _load_config_files(self):
        """
        Load and merge configuration files.

        Loads configurations in priority order (lowest to highest):
            1. Global config (~/.platformio/.platform-linux_arm.ini)
            2. Project-local config (./.platform-linux_arm.ini)

        Note:
            Project-local config overrides global config.
            Missing files are silently ignored.
        """
        # Load global config (lowest priority)
        global_config = self._load_config_file(self._global_path)
        self._config.update(global_config)

        # Load project-local config (higher priority - overrides global)
        project_config = self._load_config_file(self._project_path)
        self._config.update(project_config)

    def get(self, key: str, default: Optional[Union[str, int, bool]] = None) -> Optional[Union[str, int, bool]]:
        """
        Get configuration value with fallback to default.

        Args:
            key: Configuration key (e.g., 'upload_timeout', 'upload_user')
            default: Default value if key is not found in config files

        Returns:
            Configuration value from config file, or default if not found.
            Type matches the default parameter's type.

        Examples:
            >>> config = PlatformConfig()
            >>> timeout = config.get('upload_timeout', 300)  # returns int
            >>> user = config.get('upload_user', 'pi')  # returns str

        Note:
            Type conversion is automatic based on the default parameter type.
            If default is int, the config value is converted to int.
            If default is bool, the config value is converted to bool.
        """
        value = self._config.get(key)

        if value is None:
            return default

        # Type conversion based on default parameter type
        if default is not None:
            if isinstance(default, bool):
                # Handle boolean conversion
                return value.lower() in ('true', 'yes', '1', 'on')
            elif isinstance(default, int):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(default, float):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default

        return value

    def has_key(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: Configuration key to check

        Returns:
            True if key exists in loaded configuration, False otherwise
        """
        return key in self._config

    def get_loaded_files(self) -> list:
        """
        Get list of successfully loaded configuration files.

        Returns:
            List of file paths that were successfully loaded

        Examples:
            >>> config = PlatformConfig()
            >>> print(config.get_loaded_files())
            ['/home/user/.platformio/.platform-linux_arm.ini']

        Note:
            Useful for debugging to see which config files are active.
        """
        return self._loaded_files.copy()

    def get_all(self) -> dict:
        """
        Get all configuration key-value pairs.

        Returns:
            Dictionary of all loaded configuration

        Note:
            Useful for debugging and testing.
        """
        return self._config.copy()


# Global configuration instance (lazy loaded)
_global_config_instance = None


def get_platform_config(project_dir: Optional[str] = None) -> PlatformConfig:
    """
    Get or create global platform configuration instance.

    Args:
        project_dir: Optional project directory path

    Returns:
        PlatformConfig instance

    Note:
        Uses a singleton pattern for efficiency - config is loaded once
        and reused across multiple calls within the same PlatformIO session.
    """
    global _global_config_instance

    if _global_config_instance is None:
        _global_config_instance = PlatformConfig(project_dir)

    return _global_config_instance


# Allow standalone testing
if __name__ == "__main__":
    print("Platform Configuration Loader")
    print("=" * 60)

    config = PlatformConfig()
    loaded_files = config.get_loaded_files()

    if loaded_files:
        print(f"\nLoaded configuration files:")
        for file_path in loaded_files:
            print(f"  - {file_path}")

        print(f"\nConfiguration values:")
        all_config = config.get_all()
        if all_config:
            for key, value in sorted(all_config.items()):
                print(f"  {key} = {value}")
        else:
            print("  (no configuration found)")
    else:
        print("\nNo configuration files found.")
        print(f"\nSearched locations:")
        print(f"  - {config._global_path}")
        print(f"  - {config._project_path}")
        print(f"\nCreate a configuration file to set defaults:")
        print(f"  mkdir -p ~/.platformio")
        print(f"  nano ~/.platformio/{PlatformConfig.CONFIG_FILENAME}")
