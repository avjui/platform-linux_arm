# Configuration File Support

The Linux ARM platform supports configuration files to set global defaults, reducing duplication across projects and simplifying project configuration.

## Overview

Instead of repeating configuration in every project's `platformio.ini`, you can define defaults in `.platform-linux_arm.ini` files that are automatically loaded by the platform.

### Benefits

- **DRY (Don't Repeat Yourself)**: Set defaults once, use across all projects
- **User-specific defaults**: Different team members can have their own global defaults
- **Project-specific overrides**: Each project can override global defaults as needed
- **Less boilerplate**: Minimal configuration in `platformio.ini`
- **Backward compatible**: Works with existing projects without any changes

## Configuration File Locations

The platform searches for configuration files in the following locations (in priority order):

1. **Project-local**: `./.platform-linux_arm.ini` (in project root directory)
2. **Global**: `~/.platformio/.platform-linux_arm.ini` (in PlatformIO home directory)

### Priority Rules

Configuration values are resolved in the following order (highest to lowest priority):

1. **platformio.ini**: Values explicitly set in project configuration
2. **Project-local config**: `./.platform-linux_arm.ini` in project directory
3. **Global config**: `~/.platformio/.platform-linux_arm.ini` in PlatformIO home
4. **Hard-coded defaults**: Platform's built-in default values

**Example**: If `upload_timeout` is set in all locations:
- `platformio.ini`: `upload_timeout = 600` ← **Used**
- Project-local config: `upload_timeout = 400`
- Global config: `upload_timeout = 300`
- Hard-coded default: `upload_timeout = 300`

## Configuration File Format

Configuration files use standard INI format with a `[defaults]` section:

```ini
[defaults]
# SSH connection defaults
upload_user = pi
upload_ssh_port = 22

# Upload configuration
upload_timeout = 300
upload_path = /tmp/program

# Test configuration
test_timeout = 600
test_username = pi
```

## Supported Configuration Options

### SSH Connection Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `upload_user` | string | `pi` | Default SSH username for upload operations |
| `upload_ssh_port` | integer | `22` | SSH port for upload connections |
| `upload_ssh_key` | string | None | Path to SSH private key for upload |
| `test_ssh_port` | integer | `22` | SSH port for test connections |
| `test_ssh_key` | string | None | Path to SSH private key for testing |

### Upload Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `upload_path` | string | `/tmp/program` | Default remote path for uploaded binaries |
| `upload_timeout` | integer | `300` | Upload operation timeout (seconds) |
| `upload_flags` | string | `-avz` | Default flags for rsync upload protocol |
| `upload_run_timeout` | integer | `300` | Timeout for remote execution after upload (seconds) |

### Test Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `test_username` | string | `pi` | Default SSH username for test operations |
| `test_path` | string | `/tmp/test_program` | Default remote path for test binaries |
| `test_upload_timeout` | integer | `300` | Test binary upload timeout (seconds) |
| `test_timeout` | integer | `600` | Test execution timeout (seconds) |

## Usage Examples

### Example 1: Global Configuration

Create a global configuration file for all your projects:

```bash
# Create global config directory
mkdir -p ~/.platformio

# Create global config file
nano ~/.platformio/.platform-linux_arm.ini
```

**~/.platformio/.platform-linux_arm.ini:**
```ini
[defaults]
# My Raspberry Pi uses a custom SSH port
upload_ssh_port = 2222
test_ssh_port = 2222

# I prefer longer timeouts for slower connections
upload_timeout = 600
test_timeout = 1200

# Default username
upload_user = pi
```

**Project platformio.ini** (minimal configuration):
```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b

# Only specify the unique parts
upload_port = raspberrypi.local:/home/pi/myapp
```

### Example 2: Project-Specific Overrides

Use different settings for a specific project:

**~/.platformio/.platform-linux_arm.ini** (global defaults):
```ini
[defaults]
upload_user = pi
upload_timeout = 300
```

**.platform-linux_arm.ini** (project-local, overrides global):
```ini
[defaults]
# This project uses a different user
upload_user = admin

# This project needs longer timeout
upload_timeout = 600
```

**platformio.ini** (can still override everything):
```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b

upload_port = server.local:/opt/myapp
# Explicitly override for this specific target
upload_timeout = 900
```

### Example 3: SSH Key Authentication

Set up SSH key authentication globally:

**~/.platformio/.platform-linux_arm.ini:**
```ini
[defaults]
upload_ssh_key = ~/.ssh/raspberry_pi_key
test_ssh_key = ~/.ssh/raspberry_pi_key
upload_user = pi
```

Now all projects automatically use SSH key authentication without needing to specify it in each `platformio.ini`.

### Example 4: CI/CD Configuration

For continuous integration environments with slower connections:

**.platform-linux_arm.ini** (in project root, committed to git):
```ini
[defaults]
# CI/CD environments may need longer timeouts
upload_timeout = 900
test_timeout = 1800
test_upload_timeout = 600

# CI/CD may use different paths
upload_path = /tmp/ci_build
test_path = /tmp/ci_test
```

### Example 5: Multiple Device Setup

Manage different device configurations using project-local configs:

**Project A** (Raspberry Pi 4):
```bash
# .platform-linux_arm.ini
[defaults]
upload_user = pi
upload_ssh_port = 22
upload_path = /home/pi/app_a
```

**Project B** (Orange Pi):
```bash
# .platform-linux_arm.ini
[defaults]
upload_user = orangepi
upload_ssh_port = 2222
upload_path = /opt/app_b
```

## Installation

### Global Configuration

1. Create the PlatformIO configuration directory:
   ```bash
   mkdir -p ~/.platformio
   ```

2. Copy the example configuration:
   ```bash
   cp .platform-linux_arm.ini.example ~/.platformio/.platform-linux_arm.ini
   ```

3. Edit the configuration:
   ```bash
   nano ~/.platformio/.platform-linux_arm.ini
   ```

### Project-Local Configuration

1. Copy the example to your project root:
   ```bash
   cp .platform-linux_arm.ini.example .platform-linux_arm.ini
   ```

2. Edit as needed:
   ```bash
   nano .platform-linux_arm.ini
   ```

3. *(Optional)* Add to version control if you want to share with team:
   ```bash
   git add .platform-linux_arm.ini
   git commit -m "Add platform configuration"
   ```

## Debugging Configuration

To verify which configuration files are loaded and what values are active, you can run the configuration loader standalone:

```bash
cd /path/to/platform-linux_arm
python3 platform_config.py
```

This will display:
- Loaded configuration files
- All active configuration values
- Search paths

## Migration from platformio.ini

If you have existing projects with repeated configuration, you can easily migrate:

**Before** (duplicated in every project):
```ini
# Project 1: platformio.ini
[env]
upload_timeout = 300
upload_user = pi
upload_ssh_port = 22

# Project 2: platformio.ini (same values repeated!)
[env]
upload_timeout = 300
upload_user = pi
upload_ssh_port = 22
```

**After** (DRY with global config):
```ini
# ~/.platformio/.platform-linux_arm.ini (once)
[defaults]
upload_timeout = 300
upload_user = pi
upload_ssh_port = 22
```

```ini
# Project platformio.ini (minimal, only project-specific settings)
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b
upload_port = raspberrypi.local:/home/pi/project1

[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b
upload_port = raspberry3.local:/home/pi/project2
```

## Backward Compatibility

Configuration file support is **fully backward compatible**:

- **Existing projects work without changes**: If no config files are present, the platform uses hard-coded defaults
- **Optional feature**: You only create config files if you need them
- **No breaking changes**: platformio.ini values always take precedence over config files

## See Also

- [Upload Documentation](UPLOAD.md) - Remote deployment guide
- [Testing Documentation](TESTING.md) - Remote testing guide
- [Debugging Documentation](DEBUGGING.md) - Remote debugging guide
- [Example Configuration](.platform-linux_arm.ini.example) - Example config file with all options

## Related Issues

- Issue #73: Add Configuration File Support
