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

"""Shared pytest fixtures for platform-linux_arm tests."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest

# Add parent directory to path to import platform modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_env():
    """Create a mock PlatformIO environment object."""
    env = Mock()
    env.GetProjectOption = Mock(side_effect=lambda key, default=None: default)
    return env


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_platform_manifest(temp_project_dir):
    """Create a mock platform.json manifest file."""
    manifest_path = temp_project_dir / "platform.json"
    manifest_path.write_text('{"name": "linux_arm", "version": "1.7.0"}')
    return str(manifest_path)


@pytest.fixture
def mock_board_config():
    """Create a mock board configuration object."""
    board = Mock()
    board.manifest = {
        "build": {
            "arch": "armv7"
        }
    }
    board.get = Mock(side_effect=lambda key, default=None:
        board.manifest.get(key.replace("build.", "build.").split(".")[0], {}).get(
            key.split(".")[-1] if "." in key else key, default
        )
    )
    return board


@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess.run call."""
    result = Mock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    return result


@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess.run call."""
    result = Mock()
    result.returncode = 1
    result.stdout = ""
    result.stderr = "Error occurred"
    return result


@pytest.fixture
def sample_config_file(temp_project_dir):
    """Create a sample .platform-linux_arm.ini config file."""
    config_path = temp_project_dir / ".platform-linux_arm.ini"
    config_path.write_text("""[defaults]
upload_timeout = 600
upload_user = testuser
upload_ssh_port = 2222
""")
    return config_path
