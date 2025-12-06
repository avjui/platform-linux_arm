# Troubleshooting Guide

This guide covers common issues and solutions when using the platform-linux_arm platform for PlatformIO.

## Table of Contents

1. [Build Errors](#build-errors)
2. [Cross-Compilation Issues](#cross-compilation-issues)
3. [Framework-Specific Issues](#framework-specific-issues)
4. [Runtime Errors](#runtime-errors)
5. [Platform Installation Issues](#platform-installation-issues)
6. [Raspberry Pi 5 Specific Issues](#raspberry-pi-5-specific-issues)
7. [Architecture and Toolchain Issues](#architecture-and-toolchain-issues)
8. [Frequently Asked Questions](#frequently-asked-questions)

---

## Topic-Specific Troubleshooting Guides

For specialized issues, refer to these dedicated troubleshooting guides:

| Topic | Guide | Description |
|-------|-------|-------------|
| **Remote Debugging** | [DEBUGGING.md](DEBUGGING.md#troubleshooting) | GDB connection issues, .gdbinit setup, common warnings |
| **Upload/Deployment** | [UPLOAD.md](UPLOAD.md#troubleshooting) | SSH connection, SCP transfer, permission issues |
| **Remote Testing** | [REMOTE_TESTING.md](REMOTE_TESTING.md#troubleshooting) | Test execution, SSH setup, CI/CD integration |
| **lgpio Setup** | [LGPIO_SETUP.md](LGPIO_SETUP.md#troubleshooting) | Cross-compilation, library installation |
| **libgpiod Setup** | [LIBGPIOD_SETUP.md](LIBGPIOD_SETUP.md#troubleshooting) | Library configuration, header files |
| **PWM Configuration** | [PWM_SETUP.md](PWM_SETUP.md#troubleshooting) | PWM initialization, sysfs access |

---

## Build Errors

### Error: `arm-linux-gnueabihf-gcc: command not found`

**Problem**: Cross-compilation toolchain is not installed.

**Solution**:

```bash
# Linux
sudo apt update
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# macOS
brew tap messense/macos-cross-toolchains
brew install arm-unknown-linux-gnueabihf

# Windows
# Download from: https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads
# Extract and add to PATH
```

**Verification**:

```bash
arm-linux-gnueabihf-gcc --version
```

---

### Error: `aarch64-linux-gnu-gcc: command not found`

**Problem**: 64-bit ARM cross-compilation toolchain is not installed.

**Solution**:

```bash
# Linux
sudo apt update
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# macOS
brew tap messense/macos-cross-toolchains
brew install aarch64-unknown-linux-gnu
```

**Verification**:

```bash
aarch64-linux-gnu-gcc --version
```

---

### Error: `fatal error: lgpio.h: No such file or directory`

**Problem**: lgpio library headers not found for cross-compilation.

**Solution**:

Build lgpio library for the target architecture:

```bash
# For 32-bit ARM
./scripts/setup-lgpio-cross.sh

# For 64-bit ARM
CROSS_PREFIX=aarch64-linux-gnu- \
INSTALL_DIR=$HOME/.local/aarch64-linux-gnu \
./scripts/setup-lgpio-cross.sh
```

**Alternative**: Install system packages (Linux only):

```bash
# 32-bit libraries
sudo dpkg --add-architecture armhf
sudo apt update
sudo apt install liblgpio-dev:armhf

# 64-bit libraries
sudo dpkg --add-architecture arm64
sudo apt update
sudo apt install liblgpio-dev:arm64
```

---

### Error: `fatal error: pigpio.h: No such file or directory`

**Problem**: pigpio library headers not found.

**Solution**:

Install pigpio on your Raspberry Pi target device (pigpio is for native builds or requires manual cross-compilation setup):

```bash
# On Raspberry Pi
sudo apt update
sudo apt install libpigpio-dev pigpio
```

**Note**: Cross-compilation with pigpio requires additional setup. Consider using lgpio instead for easier cross-compilation.

---

### Error: `fatal error: wiringPi.h: No such file or directory`

**Problem**: WiringPi framework requires native build on Raspberry Pi hardware.

**Solution**:

WiringPi does not support cross-compilation in this platform. Build directly on Raspberry Pi:

```bash
# On Raspberry Pi
sudo apt update
sudo apt install wiringpi

# Or build from source
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
./build debian
sudo apt install ./wiringpi-*.deb
```

**Recommendation**: Use lgpio framework instead for cross-compilation support.

---

## Cross-Compilation Issues

### Issue: Build succeeds but binary doesn't run on Raspberry Pi

**Possible Causes**:

1. **Architecture mismatch**: 64-bit binary on 32-bit OS
2. **Missing libraries**: Target device lacks required libraries
3. **Wrong board selected**: Board definition doesn't match actual hardware

**Solutions**:

**1. Verify target OS architecture:**

```bash
# On Raspberry Pi
uname -m
# armv7l = 32-bit OS
# aarch64 = 64-bit OS
```

**2. Match build architecture to OS:**

```ini
# For 32-bit Raspberry Pi OS (default)
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio
# No board_build.arch needed (defaults to 32-bit)

# For 64-bit Raspberry Pi OS
[env:raspberrypi_4b_64bit]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio
board_build.arch = aarch64
```

**3. Install required libraries on target:**

```bash
# On Raspberry Pi
sudo apt update
sudo apt install liblgpio1  # For lgpio
sudo apt install pigpio     # For pigpio
sudo apt install wiringpi   # For wiringpi
```

---

### Issue: "cannot execute binary file: Exec format error"

**Problem**: Binary architecture doesn't match target device.

**Diagnosis**:

```bash
# Check binary architecture
file .pio/build/raspberrypi_4b/program

# Should show:
# 32-bit: "ELF 32-bit LSB executable, ARM"
# 64-bit: "ELF 64-bit LSB executable, ARM aarch64"
```

**Solution**:

Rebuild with correct architecture setting (see previous section).

---

## Framework-Specific Issues

### lgpio: Error "lgGpiochipOpen failed: -1"

**Problem**: Cannot open GPIO chip device.

**Solutions**:

**1. Run with sudo (temporary):**

```bash
sudo ./program
```

**2. Add user to gpio group (permanent):**

```bash
# On Raspberry Pi
sudo usermod -a -G gpio $USER
# Log out and log back in for changes to take effect
```

**3. Verify gpiochip device exists:**

```bash
ls -l /dev/gpiochip*
# Should show: crw-rw---- 1 root gpio ... /dev/gpiochip0
```

---

### lgpio: "GPIO already claimed" error

**Problem**: GPIO pin is already in use by another process or not properly released.

**Solutions**:

**1. Ensure previous program exited cleanly:**

Check that `lgGpiochipClose(h)` is called before program exits.

**2. Kill any running programs using GPIO:**

```bash
# Find processes using GPIO
sudo lsof /dev/gpiochip0

# Kill specific process
sudo kill <PID>
```

**3. Reboot Raspberry Pi (if persistent):**

```bash
sudo reboot
```

---

### lgpio: Raspberry Pi 1 / Zero - "Can't determine Pi revision"

**Problem**: Original Pi 1 Model A/B and Pi Zero (not 2W) need board revision hint.

**Solution**:

Set environment variable before running:

```bash
export RPI_LGPIO_REVISION=1
./program
```

**For systemd services:**

```ini
[Service]
Environment="RPI_LGPIO_REVISION=1"
ExecStart=/path/to/program
```

**Why**: These early models use older board revision detection that lgpio needs help with.

---

### pigpio: Error "pigpio initialisation failed"

**Problem**: pigpiod daemon not running or permission denied.

**Solutions**:

**1. Start pigpio daemon:**

```bash
sudo pigpiod
```

**2. Run program with sudo:**

```bash
sudo ./program
```

**3. Add to system startup:**

```bash
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

---

### pigpio: Raspberry Pi 5 - "pigpio initialisation failed"

**Problem**: pigpio is NOT compatible with Raspberry Pi 5.

**Why**: Pi 5 uses the new RP1 I/O controller, which pigpio cannot access (requires direct BCM GPIO register access).

**Solution**:

**Migrate to lgpio framework:**

```ini
# Change from pigpio
[env:raspberrypi_5]
platform = linux_arm
board = raspberrypi_5
framework = lgpio  # Use lgpio instead of pigpio
```

See [Framework Migration Guide](platforms/linux_arm.rst#migration-guide) for code migration examples.

---

### WiringPi: Cross-compilation error

**Problem**: WiringPi build fails during cross-compilation.

**Why**: WiringPi framework in this platform requires native build on Raspberry Pi hardware.

**Solutions**:

**Option 1: Build natively on Raspberry Pi**

Transfer your project to Raspberry Pi and build there:

```bash
# On Raspberry Pi
pio run
```

**Option 2: Use lgpio framework instead**

lgpio supports full cross-compilation:

```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio  # Use lgpio instead of wiringpi
```

---

### WiringPi: Raspberry Pi 5 - GCLK function not working

**Problem**: `gpioClockSet()` or clock-based PWM fails on Pi 5.

**Why**: RP1 chip documentation doesn't provide clock control details needed for implementation (limitation of WiringPi GC2 fork).

**Solution**:

**For Pi 5, use lgpio for full GPIO functionality:**

```ini
[env:raspberrypi_5]
platform = linux_arm
board = raspberrypi_5
framework = lgpio
```

---

## Runtime Errors

### Error: "Permission denied" when accessing GPIO

**Problem**: Program doesn't have permission to access GPIO devices.

**Solutions**:

**1. Run with sudo (quick test):**

```bash
sudo ./program
```

**2. Add user to gpio group (permanent):**

```bash
sudo usermod -a -G gpio $USER
# Log out and log back in
```

**3. Verify gpio group exists and device permissions:**

```bash
ls -l /dev/gpiochip0
# Should show: crw-rw---- 1 root gpio
```

---

### Error: Program compiles but LED doesn't blink

**Possible Causes**:

1. **Wrong GPIO pin number**
2. **LED not properly connected**
3. **GPIO pin already used by system**
4. **Pin numbering scheme confusion**

**Debugging Steps**:

**1. Verify GPIO pin number:**

All frameworks in this platform use **BCM GPIO numbering** (not physical pin numbers or WiringPi numbering).

Check pinout: https://pinout.xyz/

**2. Test with known-good LED circuit:**

- LED anode (long leg) → GPIO pin
- LED cathode (short leg) → 220Ω resistor → Ground

**3. Check if pin is reserved:**

Some GPIO pins are used by default for other functions (I2C, SPI, serial). Check Raspberry Pi documentation.

**4. Test with different pin:**

Try GPIO 23, which is generally safe to use.

---

### Segmentation Fault on startup

**Possible Causes**:

1. **lgpio**: GPIO chip not properly opened
2. **pigpio**: pigpiod not running
3. **Memory corruption**: Buffer overflow or null pointer

**Solutions**:

**1. Add error checking:**

```c
// lgpio
int h = lgGpiochipOpen(0);
if (h < 0) {
    printf("Failed to open gpiochip: %d\n", h);
    return 1;
}

// pigpio
if (gpioInitialise() < 0) {
    printf("Failed to initialize pigpio\n");
    return 1;
}
```

**2. Run with debugger:**

```bash
gdb ./program
run
backtrace
```

**3. Check system logs:**

```bash
dmesg | tail
```

---

## Platform Installation Issues

### Error: "Platform 'linux_arm' not found"

**Problem**: Platform not installed.

**Solution**:

```bash
# Install from PlatformIO registry
pio pkg install --global --platform platformio/linux_arm

# Or install development version from GitHub
pio pkg install --global --platform https://github.com/platformio/platform-linux_arm.git
```

---

### Error: "Could not find the package with 'platformio/linux_arm' requirements"

**Problem**: Registry connectivity issue or platform not yet published.

**Solutions**:

**1. Install from GitHub:**

```bash
pio pkg install --global --platform https://github.com/platformio/platform-linux_arm.git
```

**2. Check internet connection:**

```bash
ping registry.platformio.org
```

**3. Update PlatformIO Core:**

```bash
pio upgrade
# or
pip install -U platformio
```

---

## Raspberry Pi 5 Specific Issues

### Summary: Raspberry Pi 5 Framework Compatibility

| Framework | Pi 5 Support | Notes |
|-----------|--------------|-------|
| **lgpio** | Yes - Full support | **Recommended** |
| **pigpio** | Not compatible | Use lgpio instead |
| **WiringPi** | Partial - Limited | GCLK function not available |
| **bare-metal** | Yes - Full support | Direct system calls |

**Recommendation**: Always use **lgpio** for Raspberry Pi 5 projects.

---

### Issue: Any framework failing on Pi 5

**First, verify you're actually running on Pi 5:**

```bash
cat /proc/cpuinfo | grep Model
# Should show: Raspberry Pi 5 Model B Rev X.X
```

**Then check framework compatibility** (see table above).

---

## Architecture and Toolchain Issues

### Issue: Wrong toolchain prefix being used

**Symptoms**: Build fails with errors like `arm-linux-gnueabihf-gcc not found` when you expected `aarch64-linux-gnu-gcc` (or vice versa).

**Diagnosis**:

Check build output for:
```
Cross-compiling for ARM Linux (ARMv7 32-bit)
Using toolchain prefix: arm-linux-gnueabihf-
```
or
```
Cross-compiling for ARM Linux (AArch64/ARMv8 64-bit)
Using toolchain prefix: aarch64-linux-gnu-
```

**Solution**:

Explicitly set architecture in `platformio.ini`:

```ini
# Force 32-bit
[env:raspberrypi_4b_32bit]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio
# board_build.arch defaults to armv7 (32-bit)

# Force 64-bit
[env:raspberrypi_4b_64bit]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio
board_build.arch = aarch64
```

---

### Issue: Library linking fails with "cannot find -llgpio"

**Problem**: lgpio library not found for target architecture.

**Solution**:

Run the setup script for correct architecture:

```bash
# 32-bit ARM
./scripts/setup-lgpio-cross.sh

# 64-bit ARM
CROSS_PREFIX=aarch64-linux-gnu- \
INSTALL_DIR=$HOME/.local/aarch64-linux-gnu \
./scripts/setup-lgpio-cross.sh
```

**Verification**:

```bash
# 32-bit
ls $HOME/.local/arm-linux-gnueabihf/lib/liblgpio.*

# 64-bit
ls $HOME/.local/aarch64-linux-gnu/lib/liblgpio.*
```

---

## Frequently Asked Questions

### Q: Can I use this platform on Windows?

**A**: Yes, but with manual toolchain setup:

1. Download ARM GNU Toolchain from [ARM Developer website](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
2. Extract and add to PATH
3. Follow cross-compilation instructions

**Note**: Windows support is implemented but not extensively tested. Linux or macOS is recommended for cross-compilation.

---

### Q: Can I use this platform on macOS?

**A**: Yes! Install toolchains via Homebrew:

```bash
# For 32-bit ARM cross-compilation
brew tap messense/macos-cross-toolchains
brew install arm-unknown-linux-gnueabihf

# For 64-bit ARM cross-compilation
brew install aarch64-unknown-linux-gnu
```

---

### Q: Do I need a Raspberry Pi to develop?

**A**: No! Cross-compilation allows you to:
- Develop on Linux x86_64, macOS, or Windows
- Build ARM binaries without Raspberry Pi hardware
- Transfer compiled binaries to Raspberry Pi for execution

However, runtime testing requires actual Raspberry Pi hardware.

---

### Q: Which framework should I use?

**Quick recommendations:**

- **New projects, any Pi model**: Use **lgpio**
- **Raspberry Pi 5**: Use **lgpio** (only fully compatible option)
- **Advanced PWM/timing on Pi 1-4**: Use **pigpio**
- **Migrating from Arduino**: Consider **lgpio** (easier than WiringPi cross-compilation)
- **Maximum portability**: Use **bare-metal** (no framework)

See [Framework Comparison](platforms/linux_arm.rst#framework-comparison) for detailed comparison.

---

### Q: Can I debug my program remotely?

**A**: Yes. The platform supports comprehensive remote debugging via GDB over SSH.

See [DEBUGGING.md](DEBUGGING.md) for complete guide covering:
- GDB setup and configuration
- SSH-tunneled debugging
- IDE integration (VS Code, CLion)
- Common issues and solutions
- PlatformIO-specific setup

---

### Q: How do I speed up the build process?

**Tips:**

1. **Use ccache** (compilation cache):
   ```bash
   sudo apt install ccache
   export PATH=/usr/lib/ccache:$PATH
   ```

2. **Enable parallel builds**:
   ```ini
   [env]
   build_flags = -j$(nproc)
   ```

3. **Build only what you need**:
   ```bash
   # Build specific environment
   pio run -e raspberrypi_4b
   ```

---

### Q: My build is very slow on macOS

**Issue**: Some Homebrew cross-compiler packages can be slower than expected.

**Alternative**: Consider using ARM GNU Toolchain directly from ARM Developer website, or use Docker with a Linux environment.

---

### Q: Can I use this with PlatformIO IDE (VSCode)?

**A**: Yes! This platform works with:
- PlatformIO IDE (VSCode extension)
- PlatformIO Core (command line)
- Any IDE that supports PlatformIO

---

### Q: How do I transfer files to Raspberry Pi automatically?

**A**: Add custom upload script to `platformio.ini`:

```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio

upload_protocol = custom
upload_command = scp $SOURCE pi@raspberrypi.local:~
```

Then run:

```bash
pio run --target upload
```

---

## Still Having Issues?

If your issue isn't covered here:

1. **Check Documentation**:
   - [Platform Documentation](platforms/linux_arm.rst)
   - [Testing Matrix](TESTING.md)
   - [Contributing Guide](../CONTRIBUTING.md)

2. **Search GitHub Issues**:
   - [Open Issues](https://github.com/platformio/platform-linux_arm/issues)
   - [Closed Issues](https://github.com/platformio/platform-linux_arm/issues?q=is%3Aissue+is%3Aclosed)

3. **Ask for Help**:
   - Open a new issue with:
     - Platform version
     - Host OS and version
     - Target board
     - Framework
     - Error messages
     - Steps to reproduce

4. **PlatformIO Community**:
   - Visit [community.platformio.org](https://community.platformio.org)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Maintained By**: platform-linux_arm Team
