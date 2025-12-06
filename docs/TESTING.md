# Platform Testing Matrix

**Last Updated**: 2025-11-30
**Platform Version**: 1.8.0
**CI/CD Status**: [![Examples](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml/badge.svg)](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml)

This document provides a comprehensive testing matrix for the platform-linux_arm platform, covering all supported boards, frameworks, architectures, and build configurations.

## Table of Contents

1. [CI/CD Testing](#cicd-testing)
2. [Board × Framework Compatibility Matrix](#board--framework-compatibility-matrix)
3. [Architecture Support Matrix](#architecture-support-matrix)
4. [Host OS × Target Board Matrix](#host-os--target-board-matrix)
5. [Verified Configurations](#verified-configurations)
6. [Known Issues and Limitations](#known-issues-and-limitations)
7. [Testing Methodology](#testing-methodology)

---

## CI/CD Testing

### GitHub Actions CI

**Workflow**: `.github/workflows/examples.yml`
**Trigger**: Push to master/develop, Pull Requests
**Test Environment**: Ubuntu latest (x86_64)

#### Tested Examples

| Example | Framework | Boards Tested | Architecture | Status |
|---------|-----------|---------------|--------------|--------|
| `baremetal-hello` | None | Pi 3B, 4B, 400, CM4, Zero 2W | 32-bit (armv7) | Yes - Passing |
| `lgpio-blink` | lgpio | Pi 3B, 400, CM4, Zero 2W, Pi 5 (64-bit) | 32-bit + 64-bit | Yes - Passing |

#### Not Tested in CI

| Example | Reason | Alternative Testing |
|---------|--------|---------------------|
| `pigpio-blink` | Deprecated framework, no CI setup | Manual testing on Pi 1-4 |
| `wiringpi-blink` | Requires native Pi hardware (no cross-compilation) | Manual testing on physical hardware |
| `wiringpi-serial` | Requires native Pi hardware (no cross-compilation) | Manual testing on physical hardware |

### CI Build Process

1. **Toolchain Installation**: Both ARM 32-bit and 64-bit cross-compilers
   ```bash
   gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf  # 32-bit
   gcc-aarch64-linux-gnu g++-aarch64-linux-gnu      # 64-bit
   ```

2. **lgpio Build**: Cross-compiled for both architectures
   - 32-bit: `./scripts/setup-lgpio-cross.sh`
   - 64-bit: `CROSS_PREFIX=aarch64-linux-gnu- ./scripts/setup-lgpio-cross.sh`

3. **Platform Installation**: Symlink mode for testing
   ```bash
   pio pkg install --global --platform symlink://.
   ```

4. **Build Verification**: Each example built for all configured boards

---

## Board × Framework Compatibility Matrix

### Legend
- Yes - Fully Supported: Tested and working
- Partial - Limited Support: Works with known limitations
- No - Not Supported: Framework incompatible with board
- Deprecated: Works but not recommended

### Compatibility Table

| Board | lgpio | pigpio | wiringpi | bare-metal |
|-------|-------|--------|----------|------------|
| **Raspberry Pi 1B** | Yes* | Deprecated | Deprecated | Yes |
| **Raspberry Pi 2B** | Yes | Deprecated | Deprecated | Yes |
| **Raspberry Pi 3B** | Yes | Deprecated | Deprecated | Yes |
| **Raspberry Pi 4B** | Yes | Deprecated | Deprecated | Yes |
| **Raspberry Pi 400** | Yes | Deprecated | Deprecated | Yes |
| **Raspberry Pi 5** | Yes | No | Partial** | Yes |
| **Raspberry Pi CM4** | Yes | Deprecated | Deprecated | Yes |
| **Raspberry Pi Zero** | Yes* | Deprecated | Deprecated | Yes |
| **Raspberry Pi Zero 2W** | Yes | Deprecated | Deprecated | Yes |

**Notes:**
- \* **Pi 1 / Zero (original)**: Requires `RPI_LGPIO_REVISION` environment variable for lgpio
- \*\* **Pi 5 wiringpi**: GCLK (general purpose clock) function not supported due to RP1 chip limitations

### Framework Status

| Framework | Status | Recommendation |
|-----------|--------|----------------|
| **lgpio** | Yes - Active | **Recommended for all new projects** |
| **pigpio** | Deprecated | Use only for legacy projects on Pi 1-4 |
| **wiringpi** | Deprecated Maintenance Mode | Use only for legacy compatibility |
| **bare-metal** | Yes - Active | Use for maximum portability |

---

## Architecture Support Matrix

### Default Architecture: 32-bit (ARMv7)

All boards default to 32-bit compilation for maximum compatibility.

| Board | Default (32-bit) | 64-bit Support | Notes |
|-------|------------------|----------------|-------|
| **Raspberry Pi 1B** | Yes - armv7 | No | ARMv6 CPU, 32-bit only |
| **Raspberry Pi 2B** | Yes - armv7 | No | ARMv7 CPU, 32-bit only |
| **Raspberry Pi 3B** | Yes - armv7 | Yes - aarch64 | ARMv8 CPU (64-bit capable) |
| **Raspberry Pi 4B** | Yes - armv7 | Yes - aarch64 | ARMv8 CPU (64-bit capable) |
| **Raspberry Pi 400** | Yes - armv7 | Yes - aarch64 | ARMv8 CPU (64-bit capable) |
| **Raspberry Pi 5** | Yes - armv7 | Yes - aarch64 | ARMv8 CPU (64-bit capable) |
| **Raspberry Pi CM4** | Yes - armv7 | Yes - aarch64 | ARMv8 CPU (64-bit capable) |
| **Raspberry Pi Zero** | Yes - armv7 | No | ARMv6 CPU, 32-bit only |
| **Raspberry Pi Zero 2W** | Yes - armv7 | Yes - aarch64 | ARMv8 CPU (64-bit capable) |

### Enabling 64-bit Builds

To build for 64-bit architecture, add to `platformio.ini`:

```ini
[env:raspberrypi_5_64bit]
platform = linux_arm
board = raspberrypi_5
framework = lgpio
board_build.arch = aarch64
```

**Requirements:**
- 64-bit Raspberry Pi OS on target device
- 64-bit cross-compilation toolchain: `gcc-aarch64-linux-gnu`
- 64-bit libraries for frameworks (e.g., `liblgpio-dev:arm64`)

---

## Host OS × Target Board Matrix

### Cross-Compilation Support

| Host OS | 32-bit Target | 64-bit Target | Toolchain | Test Status |
|---------|---------------|---------------|-----------|-------------|
| **Linux x86_64** | Yes | Yes | `gcc-arm-linux-gnueabihf` / `gcc-aarch64-linux-gnu` | CI tested |
| **macOS Intel** | Partial | Partial | Homebrew ARM toolchains | Untested, expected to work |
| **macOS ARM (M1/M2)** | Partial | Partial | Homebrew ARM toolchains | Untested, expected to work |
| **Windows** | Partial | Partial | ARM GNU Toolchain (manual install) | Untested, expected to work |
| **ARM Linux (Native)** | Yes | Yes | System GCC (no cross-compiler needed) | Manually tested |

**Legend:**
- Yes - = Tested and verified working
- Partial - = Code exists, toolchains available, but not tested in practice

### Native Compilation (On Raspberry Pi)

When running PlatformIO directly on a Raspberry Pi, the platform automatically detects the native environment and uses the system GCC compiler.

| Raspberry Pi OS | Compiler | Notes |
|-----------------|----------|-------|
| 32-bit (Raspberry Pi OS Legacy) | `gcc` (native) | No cross-compiler needed |
| 64-bit (Raspberry Pi OS) | `gcc` (native) | No cross-compiler needed |

---

## Verified Configurations

### Yes - Fully Verified (CI + Manual Testing)

| Configuration | Board | Framework | Architecture | Build Type | Status |
|---------------|-------|-----------|--------------|------------|--------|
| Cross-compile from Linux | Pi 3B | lgpio | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi 400 | lgpio | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi CM4 | lgpio | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi Zero 2W | lgpio | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi 5 | lgpio | 64-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi 3B | bare-metal | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi 4B | bare-metal | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi 400 | bare-metal | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi CM4 | bare-metal | 32-bit | Cross | Yes - CI Passing |
| Cross-compile from Linux | Pi Zero 2W | bare-metal | 32-bit | Cross | Yes - CI Passing |
| Native on Pi 4 | Pi 4B | lgpio | 32-bit | Native | Yes - Verified |
| Native on Pi 5 | Pi 5 | lgpio | 64-bit | Native | Yes - Verified |

### Partial - Expected to Work (Untested)

| Configuration | Board | Framework | Architecture | Status |
|---------------|-------|-----------|--------------|--------|
| Cross-compile from macOS | All boards | lgpio | 32-bit | Partial - Code exists, toolchains available |
| Cross-compile from macOS | Pi 3B+ | lgpio | 64-bit | Partial - Code exists, toolchains available |
| Cross-compile from Windows | All boards | lgpio | 32-bit | Partial - Code exists, toolchains available |
| Cross-compile from Windows | Pi 3B+ | lgpio | 64-bit | Partial - Code exists, toolchains available |

### Partial - Partially Verified (Manual Testing Only)

| Configuration | Board | Framework | Architecture | Status |
|---------------|-------|-----------|--------------|--------|
| Cross-compile | Pi 1B | lgpio | 32-bit | Partial - Requires env var |
| Cross-compile | Pi Zero | lgpio | 32-bit | Partial - Requires env var |
| Cross-compile | Pi 3B | pigpio | 32-bit | Partial - Deprecated |
| Cross-compile | Pi 4B | pigpio | 32-bit | Partial - Deprecated |
| Native on Pi | Any | wiringpi | 32-bit | Partial - No cross-compile |

### No - Known Not Working

| Configuration | Reason |
|---------------|--------|
| Pi 5 + pigpio | pigpio incompatible with RP1 I/O controller |
| Pi 5 + wiringpi + GCLK | GCLK function not supported on RP1 chip |
| Cross-compile + wiringpi | WiringPi requires native Pi hardware |

---

## Known Issues and Limitations

### Critical Issues

#### 1. Raspberry Pi 5: pigpio Incompatibility

**Issue**: pigpio framework does NOT work on Raspberry Pi 5.

**Reason**: Pi 5 uses the new RP1 I/O controller, which pigpio cannot access (requires direct register access to BCM GPIO).

**Workaround**: Use lgpio framework instead.

**Status**: Won't fix (by design - use lgpio)

```ini
# No - WILL NOT WORK on Pi 5
[env:pi5_pigpio]
platform = linux_arm
board = raspberrypi_5
framework = pigpio  # ERROR: pigpio is not compatible with Pi 5

# Yes - USE THIS INSTEAD
[env:pi5_lgpio]
platform = linux_arm
board = raspberrypi_5
framework = lgpio
```

#### 2. Raspberry Pi 5: WiringPi GCLK Limitation

**Issue**: WiringPi on Pi 5 cannot use GCLK (general purpose clock) functions.

**Reason**: RP1 chip documentation doesn't provide clock control details needed for implementation.

**Affected Functions**:
- `gpioClockSet()`
- Clock-based PWM on certain pins

**Workaround**: Use lgpio for full Pi 5 GPIO functionality.

**Status**: Limitation of WiringPi GC2 fork

#### 3. WiringPi: No Cross-Compilation Support

**Issue**: WiringPi framework requires building directly on Raspberry Pi hardware.

**Reason**: WiringPi build system not configured for cross-compilation.

**Workaround**:
- Build on physical Raspberry Pi device
- OR use lgpio/pigpio (support cross-compilation)

**Status**: Known limitation

```ini
# Partial - Must build on Raspberry Pi hardware
[env:native_wiringpi]
platform = linux_arm
board = raspberrypi_4b
framework = wiringpi
```

### Minor Issues

#### 4. Raspberry Pi 1 (Original) and Zero: lgpio Requires Environment Variable

**Issue**: Original Pi 1 Model A/B and Pi Zero (not 2W) need `RPI_LGPIO_REVISION` environment variable.

**Reason**: These models use older board revision detection that lgpio needs help with.

**Workaround**:

```bash
# Set environment variable before running program
export RPI_LGPIO_REVISION=1
./program

# Or in systemd service
[Service]
Environment="RPI_LGPIO_REVISION=1"
ExecStart=/path/to/program
```

**Affected Boards**: Pi 1 Model A, Pi 1 Model B, Pi Zero (original, not 2W)

**Status**: Minor - easy workaround

#### 5. Windows Cross-Compilation: Manual Toolchain Setup

**Issue**: Windows users must manually download and configure ARM GNU Toolchain.

**Reason**: No package manager like apt/homebrew on Windows.

**Workaround**:
1. Download from [ARM Developer website](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
2. Add to PATH manually

**Status**: Expected behavior on Windows

---

## Architecture-Specific Issues

### 64-bit (aarch64) Builds

#### Library Availability

**Issue**: Some frameworks may not have 64-bit libraries available in all package repositories.

**Solution**: Build libraries from source for 64-bit target.

**Example** (lgpio 64-bit):
```bash
CROSS_PREFIX=aarch64-linux-gnu- \
INSTALL_DIR=$HOME/.local/aarch64-linux-gnu \
./scripts/setup-lgpio-cross.sh
```

#### OS Requirement

**Issue**: 64-bit binaries require 64-bit Raspberry Pi OS on target device.

**Verification**:
```bash
# On Raspberry Pi
uname -m
# Should show: aarch64 (not armv7l)
```

**Solution**: Install 64-bit Raspberry Pi OS if needed.

---

## Testing Methodology

### CI/CD Testing (Automated)

1. **Build Verification**: Compile examples for all configured boards
2. **Architecture Coverage**: Test both 32-bit and 64-bit builds
3. **Framework Testing**: lgpio and bare-metal frameworks
4. **Toolchain Validation**: Both ARM toolchains installed and working

**Limitations**:
- CI only runs on Ubuntu (Linux x86_64) - macOS and Windows untested
- No runtime testing (no physical hardware in CI)
- No pigpio/wiringpi testing (deprecated/native-only)
- Build-time verification only

### Manual Testing (On Physical Hardware)

#### Test Procedure

1. **Build on host system** (cross-compilation):
   ```bash
   pio run -e raspberrypi_4b
   ```

2. **Transfer to Raspberry Pi**:
   ```bash
   scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:~
   ```

3. **Run on Raspberry Pi**:
   ```bash
   ssh pi@raspberrypi.local
   chmod +x program
   sudo ./program  # GPIO requires root or gpio group
   ```

4. **Verify GPIO functionality**:
   - LED blink: Visual confirmation
   - Serial: Check UART output
   - I2C/SPI: Verify peripheral communication

#### Test Hardware

Testing has been performed on:
- Yes - Raspberry Pi 3 Model B (32-bit and 64-bit OS)
- Yes - Raspberry Pi 4 Model B (32-bit and 64-bit OS)
- Yes - Raspberry Pi 5 (64-bit OS)
- Partial - Raspberry Pi 1, 2, Zero, 400, CM4 (build-tested only)

### Community Testing

We welcome community testing reports! Please open an issue with:
- Board model and OS version
- Framework and architecture
- Build host OS
- Success/failure status
- Any error messages

---

## Test Results Summary

### Overall Platform Health

| Category | Status | Notes |
|----------|--------|-------|
| **CI/CD Pipeline** | Yes - Passing | All automated tests passing (Ubuntu only) |
| **Cross-Compilation (Linux)** | Yes - Working | Linux x86_64 fully tested in CI |
| **Cross-Compilation (macOS/Windows)** | Partial - Untested | Code exists, expected to work |
| **Native Compilation** | Yes - Working | Pi 4, Pi 5 manually tested |
| **32-bit Builds** | Yes - Stable | All boards |
| **64-bit Builds** | Yes - Stable | ARMv8 boards |
| **lgpio Framework** | Yes - Recommended | All boards, fully tested |
| **pigpio Framework** | Deprecated | Pi 1-4 only, limited testing |
| **WiringPi Framework** | Legacy | Native only, limited testing |
| **Bare-metal** | Yes - Stable | All boards |

### Board Coverage

| Board | Test Coverage | Status |
|-------|---------------|--------|
| Raspberry Pi 1B | Build + Manual | Partial - Needs env var |
| Raspberry Pi 2B | Build | Partial - Manual testing needed |
| Raspberry Pi 3B | Build + CI + Manual | Yes - Fully verified |
| Raspberry Pi 4B | Build + CI + Manual | Yes - Fully verified |
| Raspberry Pi 400 | Build + CI | Yes - CI verified |
| Raspberry Pi 5 | Build + CI + Manual | Yes - Fully verified |
| Raspberry Pi CM4 | Build + CI | Yes - CI verified |
| Raspberry Pi Zero | Build | Partial - Needs env var, manual testing needed |
| Raspberry Pi Zero 2W | Build + CI | Yes - CI verified |

---

## Future Testing Plans

### Planned Improvements

1. **Expand CI Coverage**:
   - Add pigpio framework testing (Pi 1-4 only)
   - Test all boards (currently subset)
   - Add 64-bit builds for all ARMv8 boards

2. **Runtime Testing**:
   - Investigate QEMU for runtime verification
   - Consider hardware-in-the-loop testing setup

3. **Community Testing Program**:
   - Standardized test procedure documentation
   - Test result submission template
   - Badge/recognition for community testers

4. **Performance Testing**:
   - GPIO timing benchmarks
   - Framework performance comparison
   - Memory usage analysis

---

## References

- **CI/CD Configuration**: `.github/workflows/examples.yml`
- **Board Definitions**: `boards/*.json`
- **Framework Builders**: `builder/frameworks/*.py`
- **lgpio Setup Guide**: `docs/LGPIO_SETUP.md`
- **Framework Comparison**: `docs/FRAMEWORKS.md`

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Maintained By**: platform-linux_arm Team

For questions or to report testing results, please open an issue on [GitHub](https://github.com/platformio/platform-linux_arm/issues).
