# Changelog

All notable changes to the platform-linux_arm project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

## [1.8.0] - 2025-11-15 - "The Quality Release"

**This release focuses on code quality, testing, security, and developer experience improvements.**

**🎉 Highlights:**
- **81 comprehensive unit tests** with 42% code coverage
- **Type hints (PEP 484)** for better IDE support and type safety
- **Configuration file support** for global defaults
- **libgpiod cross-compilation** on Windows and macOS
- **Security documentation** and vulnerability fixes
- **Python code quality** improvements across the board

---

### Added

- **VSCode Integration**
  - Custom tasks for SSH monitoring (examples/vscode/tasks.json)
  - Comprehensive VSCode integration guide (docs/VSCODE.md)
  - Workaround for PlatformIO GUI Monitor button limitation
  - Welcome message on first platform use with setup instructions
  - Updated example projects to include .vscode/tasks.json
  - Prominent README notice for VSCode users

- **libgpiod Framework Cross-Compilation** (#78, #82, #86, #94)
  - Windows cross-compilation via MSYS2 (#82)
  - macOS cross-compilation support (#94)
  - Ubuntu cross-compilation from source (#86)
  - Comprehensive build scripts and documentation

- **Configuration File Support** (#73, #97)
  - Global configuration: `~/.platformio/.platform-linux_arm.ini`
  - Project-local configuration: `./.platform-linux_arm.ini`
  - Configurable defaults for upload, test, and SSH settings
  - Automatic configuration discovery and merging

- **Comprehensive Unit Testing** (#71)
  - 81 unit tests using pytest framework
  - 42% code coverage (platform_constants: 100%, ssh_utils: 98%)
  - Automated testing in CI/CD (Python 3.8-3.12)
  - Developer guide (DEVELOPER.md) with testing instructions
  - Coverage reporting with HTML and XML output

- **Type Hints (PEP 484)** (#65)
  - Type annotations for platform_constants.py (100% coverage)
  - Type hints for platform.py core methods
  - mypy configuration for static type checking
  - CI/CD integration with automated mypy checks
  - Improved IDE autocomplete and type safety

- **Security Documentation** (#91)
  - Phase 1 security documentation complete
  - Threat model and risk assessment
  - Security controls and mitigation strategies
  - Best practices guide for secure deployments

- **Hardware Test Matrix** (#79)
  - Comprehensive board × framework compatibility matrix
  - Architecture support documentation (32-bit/64-bit)
  - Host OS × target board testing matrix
  - CI/CD test coverage tracking

### Fixed

- **Security Vulnerabilities**
  - Critical command injection vulnerabilities patched
  - Timeout protection on all subprocess calls
  - Input validation and sanitization throughout codebase

- **Build System**
  - Prevent lgpio build contamination between architectures (#96)
  - Fix libgpiod Windows MSYS2 path translation issues
  - Lazy imports to prevent platform load failures (#78)
  - Missing environ import in libgpiod.py

- **CI/CD**
  - Fix pip cache configuration for requirements-dev.txt
  - Proper toolchain path exports in Windows workflow
  - C++ bindings disabled for Windows cross-compilation

- **Upload & Run**
  - Fix `upload_run_after` path handling with clear directory/file distinction
  - Path ending with `/` → treated as directory, program name appended
  - Path without trailing `/` → treated as full file path
  - Display destination and final executable path in upload output
  - Register custom config options in platform.json (eliminates warnings)
  - Monitor target now skips execution when `upload_run_after=true` (prevents duplicate runs)

### Changed

- **Code Quality Improvements**
  - Comprehensive PEP 257 docstrings across Python codebase (#93)
  - Extract magic values to named constants (#90)
  - Improve error handling specificity (#89)
  - Break down long methods for better maintainability (#68, #83)
  - Standardize return values across upload/test methods (#95)

- **Refactoring**
  - Extract SSH command building to shared ssh_utils module (#77)
  - Add comprehensive unit tests for ssh_utils (#88)
  - Improved code organization and modularity

### Documentation

- Complete research documentation published to GitHub Wiki
- Enhanced developer contribution guide (DEVELOPER.md)
- Security documentation and best practices
- Hardware test matrix with compatibility tracking
- libgpiod setup and cross-compilation guides
- Removed archived research (now on Wiki)

### Performance

- CI/CD workflow optimization with comprehensive caching (#92)
  - 75% reduction in build times
  - Windows toolchain caching (300MB each)
  - Built library caching (libgpiod, lgpio)
  - macOS Homebrew toolchain caching

## [1.7.0] - 2025-11-13 - "The Modernization Release"

**This is a major modernization release forked from the original platformio/platform-linux_arm repository (last updated May 2022, abandoned for 3.5 years).**

**🎉 Highlights:**
- **First PlatformIO platform with Raspberry Pi 5 support**
- **Modern lgpio framework** supporting all Raspberry Pi models (1-5)
- **Remote development workflows** (deployment, debugging, testing)
- **15 comprehensive examples** (increased from 5)
- **10 board definitions** (increased from 4)
- **Professional development tools** with complete documentation

**Modernization Scope:**
- 110+ commits over 5 days
- ~15,000 lines of code added/modified
- ~10,000 lines of documentation added
- 30+ major features implemented
- Complete CI/CD infrastructure

---

### Added
- **Custom upload/deployment protocol support** for automated binary deployment to remote targets (#36)
  - SCP upload protocol (secure copy via SSH)
  - Rsync upload protocol (efficient incremental transfer)
  - SSH upload protocol (alternative transfer method)
  - Manual upload mode with instructions
  - Post-upload execution support (`upload_run_after`, `upload_run_command`)
  - Comprehensive upload configuration options (SSH port, key file, custom flags)
  - Flexible target specification formats (`user@host:/path`)
  - Complete upload documentation (`docs/UPLOAD.md`)
  - Remote deployment example project (`examples/remote-deployment/`)
- **Remote debugging support** via GDB over SSH for IDE-integrated debugging (#35)
  - gdbserver-ssh debug tool (automatic SSH tunnel setup)
  - gdb-remote debug tool (manual TCP debugging)
  - Support for remote debugging on Raspberry Pi and ARM SBC targets
  - VS Code integration with launch configurations
  - Complete debugging documentation (`docs/DEBUGGING.md`)
  - Remote debugging example project (`examples/remote-debugging/`)
- **Remote test execution** via SSH for automated hardware testing (#37)
  - Cross-compiled test binaries deployed and executed on target hardware
  - Real-time test output streaming from remote device
  - Unity test framework integration
  - CI/CD pipeline support for hardware-in-the-loop testing
  - Complete testing documentation (`REMOTE_TESTING.md`)
  - Remote testing example project (`examples/remote-testing/`)
- **Hardware PWM support** via Linux PWM subsystem (sysfs) for lgpio framework (#34)
  - Complete PWM HAL library (`framework-lgpio/pwm-hal.c`, `framework-lgpio/pwm-hal.h`)
  - Core API: `pwm_init()`, `pwm_write()`, `pwm_deinit()`
  - Extended API: `pwm_set_frequency()`, `pwm_set_polarity()`, `pwm_get_status()`
  - Automatic Raspberry Pi model detection (Pi 1-4 vs Pi 5)
  - PWM permission setup scripts and systemd service
  - Comprehensive PWM setup guide (`docs/PWM_SETUP.md`)
  - PWM examples: LED fading (`examples/lgpio-pwm-fade/`) and servo control (`examples/lgpio-pwm-servo/`)
- **Orange Pi Zero board support** (Allwinner H2+/H3 SoC) (#29)
  - Board definition for Orange Pi Zero with 256MB/512MB RAM variants
  - Compatible with lgpio, pigpio, and wiringpi frameworks
  - Orange Pi GPIO example (`examples/orangepi-lgpio-blink/`)
- **Additional lgpio framework examples** for hardware communication
  - SPI communication with MCP3008 ADC (`examples/lgpio-spi-adc/`) (#40)
  - I2C sensor communication with BME280 (`examples/lgpio-i2c-sensor/`) (#39)
- **Bare-metal serial communication example** (`examples/baremetal-uart/`) (#41)
  - UART/serial communication using POSIX termios API
  - Bidirectional communication with echo test and interactive modes
  - Comprehensive serial port configuration examples
- **Multi-threading example** with producer-consumer pattern (`examples/baremetal-threads/`) (#42)
  - POSIX threads (pthreads) for concurrent execution
  - Thread-safe circular queue with mutex locks and condition variables
  - 2 producer threads and 3 consumer threads
  - Demonstrates proper synchronization and resource cleanup
- Comprehensive RST documentation (`docs/platforms/linux_arm.rst`) for PlatformIO registry submission
- Testing matrix documentation (`docs/TESTING.md`) covering all boards, frameworks, and architectures
- Framework comparison table and migration guide in RST format
- Documentation implementation plan (`docs/DOCUMENTATION_PLAN.md`)
- Support for 64-bit ARM (aarch64) cross-compilation
- Architecture-aware library selection for lgpio (multiarch support)
- 64-bit build testing in CI/CD for Raspberry Pi 5
- Example configurations for new boards and 64-bit builds
- Raspberry Pi 400, Compute Module 4, and Zero 2W board definitions
- WiringPi GC2 fork integration with Raspberry Pi 5 support
- lgpio framework as primary/recommended GPIO library
- pigpio framework support (deprecated, legacy support for Pi 1-4)
- CI/CD workflow with GitHub Actions for automated build testing
- Bare-metal example (`baremetal-hello`)
- Modern GPIO framework examples (`lgpio-blink`, `pigpio-blink`)
- Comprehensive architecture documentation (32-bit vs 64-bit)

### Changed
- **BREAKING**: Prioritized lgpio as recommended framework over pigpio and WiringPi
- Deprecated pigpio framework (Pi 5 incompatible, maintenance mode)
- Updated WiringPi to GC2 community fork with Pi 5 support
- Improved cross-compilation detection for Linux x86_64, macOS, and Windows
- Enhanced build scripts with architecture detection (armv7 vs aarch64)
- Updated documentation to reflect Pi 5 compatibility requirements
- Refined framework selection guidance based on hardware and use case

### Fixed
- Multi-platform cross-compilation support (Linux, macOS Intel/ARM, Windows)
- Architecture-aware lgpio library linking (armhf and aarch64)
- CI build failures by properly building lgpio for ARM targets
- Documentation claims corrected for macOS and Windows testing status
- Native ARM Linux toolchain handling (automatic system GCC detection)

### Deprecated
- pigpio framework for new projects (use lgpio instead)
- WiringPi for new projects (legacy compatibility only)

## [1.6.0] - 2025-11-09

This is a major modernization release forked from the original platform-linux_arm repository (last updated 2022).

### Added
- Raspberry Pi 4 Model B board definition
- Raspberry Pi 5 board definition (first platform version with Pi 5 support)
- lgpio framework support for modern GPIO access
- Multi-platform cross-compilation support (Linux x86_64, macOS, Windows)
- Native ARM Linux build support (automatic toolchain detection)
- Comprehensive research and modernization roadmap (`research/` directory)
- Project documentation (`CLAUDE.md`, research workflow)
- CI/CD workflow with GitHub Actions
- Bare-metal application support

### Changed
- Updated for PlatformIO Core 6.0+ compatibility
- Converted README from plain text to Markdown
- Switched documentation URLs to HTTP (from HTTPS)
- Cleaned up unnecessary files from repository
- Updated package dependencies to use "platformio" owner namespace
- Moved vendor URL to "homepage" field in platform manifest
- Added keywords field to platform manifest
- Set minimum PlatformIO Core requirement to 5.0

### Fixed
- Cross-compilation toolchain detection for multiple platforms
- Platform detection for linux_x86_64 and other non-ARM systems
- Build system compatibility with modern PlatformIO Core
- Repository structure and organization

## [1.5.1] - Previous Release

### Changed
- Minor updates and bug fixes (see git history for details)

## [1.5.0] - Previous Release

### Changed
- Platform updates and improvements (see git history for details)

## [1.4.6] - Previous Release

### Changed
- Incremental improvements (see git history for details)

## [1.4.5] - Previous Release

### Changed
- Bug fixes and enhancements (see git history for details)

## [1.4.4] - Previous Release

### Changed
- Platform maintenance updates (see git history for details)

## [1.4.3] - Previous Release

### Fixed
- Resolved issue #7 (see git history for details)

## [1.4.2] - Previous Release

### Changed
- Platform updates (see git history for details)

## [1.4.1] - Previous Release

### Changed
- Minor improvements (see git history for details)

## [1.4.0] - Previous Release

### Changed
- Platform updates (see git history for details)

## [1.3.0] - Previous Release

### Changed
- Feature updates (see git history for details)

## [1.2.0] - Previous Release

### Added
- Features from requests #3 and #4

## [1.1.0] - Previous Release

### Changed
- Initial platform improvements

## [1.0.0] - Initial Release

### Added
- Initial platform-linux_arm implementation
- Basic Raspberry Pi support (Pi 1B, 2B, 3B, Zero)
- WiringPi framework support
- Cross-compilation from macOS x86_64

---

## Version Comparison Links

For detailed commit history between versions:
- [Unreleased changes](https://github.com/sfo2001/platform-linux_arm/compare/v1.7.0...HEAD)
- [1.7.0 changes](https://github.com/sfo2001/platform-linux_arm/compare/v1.6.0...v1.7.0)
- [1.6.0 changes](https://github.com/sfo2001/platform-linux_arm/compare/v1.5.1...v1.6.0)

## Migration Guides

### Upgrading to 1.7.0 from 1.6.0

**Framework Changes:**
- **Recommended**: Migrate to lgpio framework for all new projects
- **Pi 5 users**: Must use lgpio (pigpio is NOT compatible)
- **Legacy projects**: pigpio and WiringPi still supported for Pi 1-4

**64-bit Support:**
- Enable 64-bit builds by adding `board_build.arch = aarch64` to platformio.ini
- Requires 64-bit Raspberry Pi OS on target device
- Requires 64-bit cross-compilation toolchain (`gcc-aarch64-linux-gnu`)

**Example Migration:**

```ini
# Old (1.6.0)
[env:raspberrypi_5]
platform = linux_arm
board = raspberrypi_5
framework = wiringpi  # May have issues on Pi 5

# New (1.7.0)
[env:raspberrypi_5]
platform = linux_arm
board = raspberrypi_5
framework = lgpio     # Recommended for Pi 5
board_build.arch = aarch64  # Optional: for 64-bit builds
```

### Upgrading to 1.6.0 from 1.5.x

**Breaking Changes:**
- Minimum PlatformIO Core version is now 5.0 (was 3.x)

**New Features:**
- PlatformIO Core 6.0 compatibility
- Raspberry Pi 4 and Pi 5 support
- Modern GPIO frameworks (lgpio)

---

**Note**: Detailed release notes for versions prior to 1.6.0 are limited. For complete history, see the [git commit log](https://github.com/sfo2001/platform-linux_arm/commits).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
