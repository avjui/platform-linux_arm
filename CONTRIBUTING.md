# Contributing to platform-linux_arm

Thank you for your interest in contributing to the platform-linux_arm project! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment Setup](#development-environment-setup)
4. [How to Contribute](#how-to-contribute)
5. [Adding New Boards](#adding-new-boards)
6. [Testing Changes](#testing-changes)
7. [Submitting Pull Requests](#submitting-pull-requests)
8. [Code Style Guidelines](#code-style-guidelines)
9. [Commit Message Format](#commit-message-format)
10. [Community and Support](#community-and-support)

---

## Code of Conduct

This project adheres to the PlatformIO [Code of Conduct](https://github.com/platformio/.github/blob/develop/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **PlatformIO Core** installed (version 5.0 or later)
   ```bash
   pip install -U platformio
   ```

2. **ARM Cross-Compilation Toolchain** (for testing cross-compilation)
   ```bash
   # Linux
   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
   sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

   # macOS
   brew tap messense/macos-cross-toolchains
   brew install arm-unknown-linux-gnueabihf
   brew install aarch64-unknown-linux-gnu
   ```

3. **Git** for version control
   ```bash
   git --version
   ```

4. **(Optional) Raspberry Pi hardware** for runtime testing

---

## Development Environment Setup

### 1. Fork and Clone

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/platform-linux_arm.git
cd platform-linux_arm
```

### 2. Add Upstream Remote

Add the original repository as upstream:

```bash
git remote add upstream https://github.com/platformio/platform-linux_arm.git
git fetch upstream
```

### 3. Install Platform in Development Mode

Install the platform locally using symlink mode for live development:

```bash
pio pkg install --global --platform symlink://.
```

This allows you to make changes to the platform code and immediately test them without reinstalling.

### 4. Set Up lgpio for Cross-Compilation (Optional)

If you plan to test lgpio framework examples:

```bash
# 32-bit ARM
./scripts/setup-lgpio-cross.sh

# 64-bit ARM
CROSS_PREFIX=aarch64-linux-gnu- \
INSTALL_DIR=$HOME/.local/aarch64-linux-gnu \
./scripts/setup-lgpio-cross.sh
```

---

## How to Contribute

We welcome various types of contributions:

### Bug Reports

If you find a bug, please open an issue with:
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Platform information (OS, PlatformIO version, board)
- Error messages or logs

### Feature Requests

For new features or enhancements:
- Describe the feature and its use case
- Explain why it would be valuable
- Provide examples if possible

### Documentation Improvements

Documentation improvements are always welcome:
- Fix typos or clarify instructions
- Add examples or use cases
- Update outdated information

### Code Contributions

See sections below for detailed instructions on code contributions.

---

## Adding New Boards

To add support for a new Raspberry Pi board:

### 1. Create Board Definition File

Create a new JSON file in `boards/` directory:

```bash
# Example: boards/raspberrypi_new.json
```

**Board definition template:**

```json
{
  "build": {
    "core": "linux-arm",
    "cpu": "cortex-a72",
    "f_cpu": "1500000000L",
    "mcu": "bcm2711",
    "arch": "armv7"
  },
  "frameworks": [
    "lgpio",
    "pigpio",
    "wiringpi"
  ],
  "name": "Raspberry Pi New Model",
  "upload": {
    "maximum_ram_size": 1073741824,
    "maximum_size": 1073741824
  },
  "url": "https://www.raspberrypi.com/products/raspberry-pi-new/",
  "vendor": "Raspberry Pi"
}
```

**Key fields to customize:**

- `build.cpu`: ARM CPU model (e.g., `cortex-a53`, `cortex-a72`, `cortex-a76`)
- `build.f_cpu`: CPU frequency in Hz (e.g., `1500000000L` for 1.5 GHz)
- `build.mcu`: Broadcom SoC model (e.g., `bcm2711`, `bcm2712`)
- `build.arch`: Architecture (`armv7` for 32-bit, `aarch64` for 64-bit capable)
- `frameworks`: Supported frameworks (lgpio always, pigpio if Pi 1-4, wiringpi for compatibility)
- `upload.maximum_ram_size`: RAM in bytes
- `url`: Official product page

### 2. Add Board Documentation

Add board entry to `docs/platforms/linux_arm.rst`:

```rst
* - :ref:`board_linux_arm_raspberrypi_new`
  - BCM2711
  - 1500MHz
  - 1GB
  - lgpio, pigpio, wiringpi
```

### 3. Test the Board

Create a test environment in an example project:

```ini
[env:raspberrypi_new]
platform = linux_arm
board = raspberrypi_new
framework = lgpio
```

Test building:

```bash
pio run -e raspberrypi_new
```

### 4. Update Testing Matrix

Update `docs/TESTING.md` with the new board's test status.

---

## Testing Changes

### Build Testing (Required)

**Test all examples:**

```bash
# Test all examples with your changes
cd examples/baremetal-hello
pio run

cd ../lgpio-blink
pio run
```

**Test both architectures (if board supports 64-bit):**

```bash
# 32-bit (default)
pio run -e raspberrypi_4b

# 64-bit
pio run -e raspberrypi_4b_64bit
```

### Runtime Testing (Highly Recommended)

If you have Raspberry Pi hardware:

1. **Build on your development machine:**
   ```bash
   pio run -e raspberrypi_4b
   ```

2. **Transfer binary to Raspberry Pi:**
   ```bash
   scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:~
   ```

3. **Run on Raspberry Pi:**
   ```bash
   ssh pi@raspberrypi.local
   chmod +x program
   sudo ./program  # GPIO requires root or gpio group membership
   ```

4. **Verify functionality:**
   - GPIO operations work correctly
   - No runtime errors
   - Expected behavior observed

### CI/CD Testing

Our GitHub Actions CI automatically tests:
- Cross-compilation on Ubuntu (Linux x86_64)
- `baremetal-hello` example for multiple boards
- `lgpio-blink` example for multiple boards (32-bit and 64-bit)

Make sure your changes pass CI before submitting a PR.

---

## Submitting Pull Requests

### 1. Create a Feature Branch

Create a descriptive branch name:

```bash
git checkout -b feature/add-pi-new-board
# or
git checkout -b fix/lgpio-architecture-detection
```

### 2. Make Your Changes

- Follow the [Code Style Guidelines](#code-style-guidelines)
- Write clear, descriptive commit messages
- Test your changes thoroughly

### 3. Update Documentation

If your changes affect:
- **User-facing behavior**: Update `docs/platforms/linux_arm.rst`
- **Testing status**: Update `docs/TESTING.md`
- **Breaking changes**: Update `CHANGELOG.md`
- **New features**: Update `README.md`

### 4. Commit Your Changes

Follow our [Commit Message Format](#commit-message-format):

```bash
git add .
git commit -m "feat(boards): add Raspberry Pi New Model support"
```

### 5. Push to Your Fork

```bash
git push origin feature/add-pi-new-board
```

### 6. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template:
   - **Title**: Clear, descriptive summary
   - **Description**: What changes you made and why
   - **Testing**: How you tested the changes
   - **Related Issues**: Link any related issues

### 7. Respond to Review Feedback

- Address reviewer comments promptly
- Make requested changes in new commits
- Push updates to your branch (PR will update automatically)

---

## Code Style Guidelines

### Python Code

Follow [PEP 8](https://pep8.org/) style guidelines:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 100 characters (prefer 80)
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

**Example:**

```python
def configure_cross_compiler(env, target_arch):
    """Configure cross-compilation toolchain for target architecture."""
    if target_arch == "aarch64":
        env.Replace(_BINPREFIX="aarch64-linux-gnu-")
    else:
        env.Replace(_BINPREFIX="arm-linux-gnueabihf-")
```

### JSON Configuration Files

- **Indentation**: 2 spaces
- **Sorting**: Keys should be alphabetically sorted within sections
- **Validation**: Ensure valid JSON syntax

**Example:**

```json
{
  "build": {
    "arch": "armv7",
    "cpu": "cortex-a72",
    "f_cpu": "1500000000L",
    "mcu": "bcm2711"
  },
  "frameworks": ["lgpio", "pigpio", "wiringpi"],
  "name": "Raspberry Pi 4 Model B"
}
```

### reStructuredText Documentation

- **Headings**: Use consistent heading hierarchy
  ```rst
  Title (H1)
  ==========

  Section (H2)
  ------------

  Subsection (H3)
  ~~~~~~~~~~~~~~~
  ```
- **Code blocks**: Always specify language
  ```rst
  .. code-block:: bash

     pio run
  ```
- **Tables**: Use list-table for complex tables
- **Line length**: Soft limit of 100 characters

### Markdown Documentation

- **Headings**: Use ATX-style headings (`#`, `##`, etc.)
- **Code blocks**: Always specify language
  ````markdown
  ```bash
  pio run
  ```
  ````
- **Links**: Use reference-style links for repeated URLs
- **Line length**: Soft limit of 100 characters

---

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring (no feature or bug fix)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build config)
- **perf**: Performance improvements

### Scopes

- `boards`: Board definitions
- `frameworks`: Framework support (lgpio, pigpio, wiringpi)
- `lgpio`: lgpio-specific changes
- `pigpio`: pigpio-specific changes
- `wiringpi`: wiringpi-specific changes
- `ci`: CI/CD configuration
- `docs`: Documentation
- `arch`: Architecture support (32-bit/64-bit)
- `platform`: Platform core changes

### Examples

```
feat(boards): add Raspberry Pi 400 board definition

Add board definition for Raspberry Pi 400 with BCM2711 SoC.
Includes support for lgpio, pigpio, and wiringpi frameworks.

Closes #123
```

```
fix(lgpio): correct multiarch library detection for aarch64

The library path detection was failing on 64-bit systems.
Now checks both /usr/lib/aarch64-linux-gnu and
/usr/local/lib/aarch64-linux-gnu.

Fixes #456
```

```
docs: update testing matrix with Pi 5 compatibility notes

Clarified that pigpio does NOT work on Pi 5 due to RP1 I/O
controller. Added recommendation to use lgpio instead.
```

---

## Community and Support

### Getting Help

- **Documentation**: Check [docs/platforms/linux_arm.rst](docs/platforms/linux_arm.rst)
- **Issues**: Search [existing issues](https://github.com/platformio/platform-linux_arm/issues)
- **PlatformIO Community**: Visit [community.platformio.org](https://community.platformio.org)

### Communication

- **GitHub Issues**: For bugs, features, and questions
- **Pull Requests**: For code contributions
- **Discussions**: For general questions and ideas

### Recognition

Contributors are recognized in:
- Git commit history
- Release notes (CHANGELOG.md)
- Project documentation

---

## Development Workflow Summary

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/platform-linux_arm.git
cd platform-linux_arm

# 2. Install in development mode
pio pkg install --global --platform symlink://.

# 3. Create feature branch
git checkout -b feature/my-new-feature

# 4. Make changes and test
pio run -d examples/lgpio-blink

# 5. Commit with conventional commit message
git commit -m "feat(scope): add awesome feature"

# 6. Push to your fork
git push origin feature/my-new-feature

# 7. Open Pull Request on GitHub
```

---

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the project.

---

## Questions?

If you have questions about contributing, please:
1. Check this guide thoroughly
2. Search existing issues and discussions
3. Open a new issue with the "question" label

Thank you for contributing to platform-linux_arm!
