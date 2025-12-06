# Hardware Test Matrix

This document defines the comprehensive hardware testing matrix for platform-linux_arm, covering all supported Raspberry Pi models, frameworks, architectures, and build workflows.

## Overview

The test matrix ensures compatibility across:
- **Hardware**: Raspberry Pi 1, 3, 5 (representative models spanning all generations)
- **Frameworks**: WiringPi, lgpio, pigpio
- **Architectures**: ARMv6 (32-bit), ARMv7 (32-bit), AArch64 (64-bit)
- **Build Workflows**: Native (on-device), Cross-compilation (Ubuntu, Windows)
- **Operating Systems**: Official Raspberry Pi OS (Bookworm) for each model

---

## Hardware Models

### Raspberry Pi 1 Model B
- **SoC**: BCM2835
- **Architecture**: ARMv6 (32-bit only)
- **CPU**: 700 MHz single-core ARM1176JZF-S
- **RAM**: 512 MB
- **Recommended OS**: Raspberry Pi OS Bookworm (32-bit)
  - **Version**: Latest stable Bookworm release
  - **Variant**: Lite or Full
  - **Download**: https://www.raspberrypi.com/software/operating-systems/
  - **Note**: ARMv6 requires 32-bit OS only; 64-bit not supported

### Raspberry Pi 3 Model B
- **SoC**: BCM2837
- **Architecture**: ARMv8-A (32-bit or 64-bit)
- **CPU**: 1.2 GHz quad-core Cortex-A53
- **RAM**: 1 GB
- **Recommended OS**: Raspberry Pi OS Bookworm (32-bit or 64-bit)
  - **Version**: Latest stable Bookworm release
  - **Variant**: Lite or Full
  - **32-bit**: Maximum compatibility, stable
  - **64-bit**: Better performance, modern toolchain
  - **Download**: https://www.raspberrypi.com/software/operating-systems/

### Raspberry Pi 5
- **SoC**: BCM2712
- **Architecture**: ARMv8.2-A (64-bit recommended)
- **CPU**: 2.4 GHz quad-core Cortex-A76
- **RAM**: 4 GB / 8 GB variants
- **Recommended OS**: Raspberry Pi OS Bookworm (64-bit)
  - **Version**: Bookworm or later (minimum requirement)
  - **Variant**: Lite or Full
  - **Note**: Requires Bookworm or later; legacy versions not supported
  - **Download**: https://www.raspberrypi.com/software/operating-systems/

---

## Framework Compatibility Matrix

| Framework | Pi 1 (ARMv6) | Pi 3 (ARMv7/8) | Pi 5 (ARMv8.2) | Notes |
|-----------|--------------|----------------|----------------|-------|
| **WiringPi** | Yes - Supported | Yes - Supported | Yes - Supported | GC2 fork with Pi 5 support (GCLK not on Pi 5) |
| **lgpio** | Yes - Supported | Yes - Supported | Yes - Supported | Modern library, full Pi 5 support with RP1 I/O |
| **pigpio** | Yes - Supported | Yes - Supported | Not supported | Pi 1-4 only; not Pi 5 compatible |

### Framework Details

#### WiringPi
- **Version**: GC2 (Grazer Computer Club) maintained fork
- **URL**: https://github.com/WiringPi/WiringPi
- **Compatibility**: All Raspberry Pi models (1-5)
- **Pi 5 Notes**: GCLK function not supported on Pi 5
- **Use Cases**: Legacy projects, GPIO control, I2C, SPI
- **Cross-compilation**: **NOT SUPPORTED** - must build natively on Raspberry Pi

#### lgpio
- **Version**: Modern C library for Linux GPIO
- **URL**: http://abyz.me.uk/lg/index.html
- **Compatibility**: All Raspberry Pi models (1-5)
- **Pi 5 Notes**: Full support including RP1 I/O controller
- **Use Cases**: Modern GPIO projects, recommended for new development
- **Cross-compilation**: Supported (native or cross-compile)

#### pigpio
- **Version**: Feature-rich GPIO library
- **URL**: http://abyz.me.uk/rpi/pigpio/
- **Compatibility**: Raspberry Pi 1-4 only
- **Pi 5 Notes**: **NOT COMPATIBLE** with Pi 5
- **Use Cases**: Microsecond timing, PWM, servo control
- **Cross-compilation**: Supported for Pi 1-4 only

---

## Architecture and Toolchain Matrix

| Architecture | Compiler Prefix | Target Hardware | OS Requirement | Notes |
|--------------|----------------|-----------------|----------------|-------|
| **ARMv6** (32-bit) | `arm-linux-gnueabihf-` | Pi 1, Pi Zero | 32-bit OS only | Legacy architecture |
| **ARMv7** (32-bit) | `arm-linux-gnueabihf-` | Pi 2, 3, 4, 5 | 32-bit or 64-bit OS | Backward compatible |
| **AArch64** (64-bit) | `aarch64-linux-gnu-` | Pi 3, 4, 5 | 64-bit OS required | Modern 64-bit |

### Toolchain Installation

#### Ubuntu/Debian Linux
```bash
# For ARMv6/ARMv7 (32-bit)
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf gdb-multiarch

# For AArch64 (64-bit)
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu gdb-multiarch
```

#### macOS
```bash
# Install Homebrew cross-compilation toolchains
brew tap messense/macos-cross-toolchains

# For ARMv6/ARMv7 (32-bit)
brew install arm-unknown-linux-gnueabihf

# For AArch64 (64-bit)
brew install aarch64-unknown-linux-gnu
```

#### Windows
**Option 1: WSL2 (Recommended)**
```bash
# Install WSL2 with Ubuntu
wsl --install -d Ubuntu-22.04

# Inside WSL, install toolchains (same as Ubuntu above)
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
```

**Option 2: Native Windows Toolchain**
- Download ARM GNU Toolchain from https://developer.arm.com/downloads/-/gnu-a
- Extract and add to PATH
- Note: Limited testing; WSL2 recommended for better compatibility

---

## Build Workflow Matrix

### Workflow 1: Native Compilation (On Raspberry Pi)

| Hardware | OS | Framework | Architecture | Test Type |
|----------|----|-----------|--------------| ----------|
| Pi 1 | Bookworm 32-bit | WiringPi | ARMv6 | Basic GPIO, Build |
| Pi 1 | Bookworm 32-bit | lgpio | ARMv6 | Basic GPIO, Build |
| Pi 1 | Bookworm 32-bit | pigpio | ARMv6 | Basic GPIO, Build |
| Pi 3 | Bookworm 32-bit | WiringPi | ARMv7 | Basic GPIO, Build |
| Pi 3 | Bookworm 32-bit | lgpio | ARMv7 | Basic GPIO, Build |
| Pi 3 | Bookworm 32-bit | pigpio | ARMv7 | Basic GPIO, Build |
| Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Basic GPIO, Build |
| Pi 3 | Bookworm 64-bit | pigpio | AArch64 | Basic GPIO, Build |
| Pi 5 | Bookworm 64-bit | WiringPi | AArch64 | Basic GPIO, Build |
| Pi 5 | Bookworm 64-bit | lgpio | AArch64 | Basic GPIO, Build |

**Setup Requirements:**
- Raspberry Pi hardware with Raspberry Pi OS installed
- PlatformIO Core 6.0+ installed
- Install platform: `pio pkg install --global --platform file://.`
- SSH access configured for remote workflows

**Test Commands:**
```bash
# Build project
pio run

# Run tests
pio test

# Upload and run (for remote development)
pio run --target upload
```

### Workflow 2: Cross-Compilation from Ubuntu

| Host OS | Target Hardware | Framework | Architecture | Toolchain | Test Type |
|---------|-----------------|-----------|--------------|-----------|-----------|
| Ubuntu 22.04+ | Pi 1 | lgpio | ARMv6 (32-bit) | arm-linux-gnueabihf | Build, Deploy |
| Ubuntu 22.04+ | Pi 1 | pigpio | ARMv6 (32-bit) | arm-linux-gnueabihf | Build, Deploy |
| Ubuntu 22.04+ | Pi 3 | lgpio | ARMv7 (32-bit) | arm-linux-gnueabihf | Build, Deploy |
| Ubuntu 22.04+ | Pi 3 | pigpio | ARMv7 (32-bit) | arm-linux-gnueabihf | Build, Deploy |
| Ubuntu 22.04+ | Pi 3 | lgpio | AArch64 (64-bit) | aarch64-linux-gnu | Build, Deploy |
| Ubuntu 22.04+ | Pi 3 | pigpio | AArch64 (64-bit) | aarch64-linux-gnu | Build, Deploy |
| Ubuntu 22.04+ | Pi 5 | lgpio | AArch64 (64-bit) | aarch64-linux-gnu | Build, Deploy |

**Setup Requirements:**
- Ubuntu 22.04 LTS or later
- PlatformIO Core 6.0+ installed
- Cross-compilation toolchain installed (see above)
- Target Raspberry Pi accessible via SSH
- SSH keys configured for passwordless access

**Test Commands:**
```bash
# Build for target
pio run

# Deploy to target hardware
pio run --target upload

# Run remote tests
pio test
```

**Example platformio.ini:**
```ini
[env:raspberrypi_3b]
platform = https://github.com/sfo2001/platform-linux_arm.git
framework = lgpio
board = raspberrypi_3b
board_build.arch = aarch64  ; For 64-bit OS

; Remote deployment
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/program
upload_run_after = true

; Remote testing
test_transport = ssh
test_port = pi@raspberrypi.local:/tmp/test_program

; Remote debugging
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local
```

### Workflow 3: Cross-Compilation from Windows

| Host OS | Target Hardware | Framework | Architecture | Toolchain | Test Type |
|---------|-----------------|-----------|--------------|-----------|-----------|
| Windows 11 (WSL2) | Pi 1 | lgpio | ARMv6 (32-bit) | arm-linux-gnueabihf | Build, Deploy |
| Windows 11 (WSL2) | Pi 3 | lgpio | ARMv7 (32-bit) | arm-linux-gnueabihf | Build, Deploy |
| Windows 11 (WSL2) | Pi 3 | lgpio | AArch64 (64-bit) | aarch64-linux-gnu | Build, Deploy |
| Windows 11 (WSL2) | Pi 5 | lgpio | AArch64 (64-bit) | aarch64-linux-gnu | Build, Deploy |

**Setup Requirements:**
- Windows 11 with WSL2 enabled
- Ubuntu 22.04 LTS in WSL2
- PlatformIO Core 6.0+ installed in WSL
- Cross-compilation toolchain installed in WSL
- Target Raspberry Pi accessible via SSH from WSL

**Test Commands (in WSL):**
```bash
# Same as Ubuntu workflow above
pio run
pio run --target upload
pio test
```

**Note**: Native Windows toolchain testing has limited coverage; WSL2 is the recommended approach.

---

## Complete Test Matrix

### Priority 1: Core Functionality Tests

| Test ID | Hardware | OS | Framework | Architecture | Build Host | Test Description |
|---------|----------|----|-----------|--------------| -----------|------------------|
| P1-01 | Pi 1 | Bookworm 32-bit | lgpio | ARMv6 32-bit | Native (Pi 1) | Basic GPIO toggle, native build |
| P1-02 | Pi 3 | Bookworm 32-bit | lgpio | ARMv7 32-bit | Native (Pi 3) | Basic GPIO toggle, native build |
| P1-03 | Pi 5 | Bookworm 64-bit | lgpio | AArch64 | Native (Pi 5) | Basic GPIO toggle, native build |
| P1-04 | Pi 3 | Bookworm 32-bit | lgpio | ARMv7 32-bit | Ubuntu 22.04 | Cross-compile, remote deploy |
| P1-05 | Pi 5 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | Cross-compile, remote deploy |
| P1-06 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Windows 11 WSL2 | Cross-compile, remote deploy |

### Priority 2: Framework Coverage Tests

| Test ID | Hardware | OS | Framework | Architecture | Build Host | Test Description |
|---------|----------|----|-----------|--------------| -----------|------------------|
| P2-01 | Pi 1 | Bookworm 32-bit | pigpio | ARMv6 32-bit | Native (Pi 1) | PWM and timing functionality |
| P2-02 | Pi 3 | Bookworm 32-bit | pigpio | ARMv7 32-bit | Native (Pi 3) | PWM and timing functionality |
| P2-03 | Pi 3 | Bookworm 32-bit | WiringPi | ARMv7 32-bit | Native (Pi 3) | WiringPi GPIO (native only) |
| P2-04 | Pi 5 | Bookworm 64-bit | WiringPi | AArch64 | Native (Pi 5) | WiringPi GPIO (native only) |
| P2-05 | Pi 5 | Bookworm 64-bit | lgpio | AArch64 | Native (Pi 5) | Advanced GPIO with RP1 I/O |

### Priority 3: Remote Workflows Tests

| Test ID | Hardware | OS | Framework | Architecture | Build Host | Test Description |
|---------|----------|----|-----------|--------------| -----------|------------------|
| P3-01 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | SCP upload protocol |
| P3-02 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | rsync upload protocol |
| P3-03 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | SSH upload protocol |
| P3-04 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | Remote testing via SSH |
| P3-05 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | Remote debugging (gdbserver-ssh) |
| P3-06 | Pi 5 | Bookworm 64-bit | lgpio | AArch64 | Windows 11 WSL2 | Remote testing via SSH |

### Priority 4: Architecture Coverage Tests

| Test ID | Hardware | OS | Framework | Architecture | Build Host | Test Description |
|---------|----------|----|-----------|--------------| -----------|------------------|
| P4-01 | Pi 3 | Bookworm 32-bit | lgpio | ARMv7 32-bit | Ubuntu 22.04 | 32-bit cross-compile |
| P4-02 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | Ubuntu 22.04 | 64-bit cross-compile |
| P4-03 | Pi 3 | Bookworm 64-bit | lgpio | AArch64 | macOS | 64-bit cross-compile (optional) |

---

## Test Setup Guide

### Hardware Setup

#### Required Equipment
1. **Raspberry Pi Models**:
   - Raspberry Pi 1 Model B (or Pi Zero for ARMv6 testing)
   - Raspberry Pi 3 Model B (or 3B+)
   - Raspberry Pi 5
2. **Power Supplies**: Official USB-C (Pi 5) or microUSB (Pi 1/3) power supplies
3. **Storage**: MicroSD cards (16 GB minimum, 32 GB recommended)
4. **Networking**: Ethernet cables or WiFi connectivity
5. **Test Peripherals** (optional):
   - LEDs and resistors for GPIO testing
   - Breadboard and jumper wires
   - USB-to-serial adapter for console access

#### Network Configuration
1. **Static IP Assignment** (recommended):
   ```bash
   # Edit /etc/dhcpcd.conf on Raspberry Pi
   interface eth0
   static ip_address=192.168.1.100/24
   static routers=192.168.1.1
   static domain_name_servers=192.168.1.1
   ```

2. **mDNS/Avahi** (alternative):
   ```bash
   # Access Pi by hostname
   ssh pi@raspberrypi.local
   ```

3. **SSH Key Setup**:
   ```bash
   # Generate SSH key on host machine
   ssh-keygen -t ed25519 -C "pio-testing"

   # Copy to Raspberry Pi
   ssh-copy-id pi@raspberrypi.local
   ```

### Software Setup

#### Raspberry Pi Target Setup

1. **Flash Raspberry Pi OS**:
   - Download appropriate version for each Pi model
   - Use Raspberry Pi Imager: https://www.raspberrypi.com/software/
   - Configure WiFi and SSH during imaging (recommended)

2. **Initial Configuration**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install dependencies
   sudo apt install -y gdbserver build-essential git

   # Enable SSH (if not done during imaging)
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

3. **Framework Libraries** (if testing natively):
   ```bash
   # For lgpio
   sudo apt install -y liblgpio-dev

   # For pigpio
   sudo apt install -y pigpio python3-pigpio

   # For WiringPi (native build only)
   # Will be installed by PlatformIO platform
   ```

#### Build Host Setup (Ubuntu)

1. **Install PlatformIO**:
   ```bash
   # Via Python pip
   pip install -U platformio

   # Or via installer script
   curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py -o get-platformio.py
   python3 get-platformio.py
   ```

2. **Install Cross-Compilation Toolchains**:
   ```bash
   sudo apt update
   sudo apt install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
   sudo apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
   sudo apt install -y gdb-multiarch
   ```

3. **Install Platform**:
   ```bash
   # From local repository
   pio pkg install --global --platform file://path/to/platform-linux_arm

   # Or from GitHub
   pio pkg install --global --platform https://github.com/sfo2001/platform-linux_arm.git
   ```

#### Build Host Setup (Windows WSL2)

1. **Install WSL2**:
   ```powershell
   # In PowerShell (Administrator)
   wsl --install -d Ubuntu-22.04
   ```

2. **Configure WSL2** (follow Ubuntu setup above)

3. **Network Considerations**:
   - WSL2 has NAT networking; SSH to Raspberry Pi works normally
   - Ensure Windows Firewall allows WSL2 connections

#### Build Host Setup (macOS)

1. **Install Homebrew**:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install PlatformIO and Toolchains**:
   ```bash
   # PlatformIO
   pip3 install -U platformio

   # Cross-compilation toolchains
   brew tap messense/macos-cross-toolchains
   brew install arm-unknown-linux-gnueabihf
   brew install aarch64-unknown-linux-gnu
   ```

### Test Execution

#### Example Test Projects

Test projects are available in `examples/`:
- `examples/wiringpi-blink/`: WiringPi GPIO toggle
- `examples/lgpio-blink/`: lgpio GPIO toggle
- `examples/remote-deployment/`: Remote upload testing
- `examples/remote-testing/`: Remote test execution
- `examples/remote-debugging/`: Remote GDB debugging

#### Running Tests

1. **Native Build and Test**:
   ```bash
   cd examples/lgpio-blink
   pio run
   .pio/build/raspberrypi_3b/program
   ```

2. **Cross-Compile and Deploy**:
   ```bash
   cd examples/lgpio-blink
   pio run --target upload
   ```

3. **Remote Testing**:
   ```bash
   cd examples/remote-testing
   pio test
   ```

4. **Remote Debugging**:
   ```bash
   cd examples/remote-debugging
   pio debug
   ```

### Test Result Documentation

For each test, document:
1. **Test ID**: From matrix above
2. **Date**: YYYY-MM-DD
3. **Tester**: Name/username
4. **Hardware**: Exact model and revision
5. **OS Version**: Output of `cat /etc/os-release`
6. **Build Host**: OS and version
7. **PlatformIO Version**: Output of `pio --version`
8. **Result**: Pass/Fail
9. **Build Log**: Saved to `logs/test-{id}-build.log`
10. **Runtime Log**: Saved to `logs/test-{id}-runtime.log`
11. **Notes**: Any issues or observations

**Example Result Entry**:
```markdown
### Test P1-03: Pi 5 Native Build with lgpio

- **Date**: 2025-01-15
- **Tester**: johndoe
- **Hardware**: Raspberry Pi 5 (8GB)
- **OS Version**: Raspberry Pi OS Bookworm 64-bit (2024-11-19)
- **Build Host**: Same (native)
- **PlatformIO Version**: 6.1.15
- **Result**: Yes - PASS
- **Build Time**: 8.2s
- **Notes**: GPIO toggle working correctly, no issues
```

---

## Known Limitations

### WiringPi Framework
- **Cross-compilation not supported**: Must build natively on Raspberry Pi
- **Reason**: WiringPi library requires access to `/dev/mem` and hardware-specific GPIO mappings
- **Workaround**: Use lgpio for cross-compilation workflows

### Pi 5 Compatibility
- **pigpio not supported**: pigpio does not support Pi 5 hardware
- **Use lgpio instead**: lgpio has full Pi 5 support including RP1 I/O controller

### ARMv6 (Pi 1) Compatibility
- **64-bit not supported**: Pi 1 uses ARMv6 which is 32-bit only
- **Limited performance**: Single-core 700 MHz CPU
- **Use Lite OS**: Recommend Raspberry Pi OS Lite for better performance

### Windows Native Toolchain
- **Limited testing**: Native Windows ARM toolchain has minimal test coverage
- **WSL2 recommended**: Use WSL2 with Ubuntu for better compatibility

---

## Test Automation

### CI/CD Integration

Future work to integrate automated testing:
1. GitHub Actions workflows for cross-compilation
2. Self-hosted runners on Raspberry Pi hardware for native builds
3. Automated hardware-in-the-loop testing with GPIO validation
4. Nightly builds against latest Raspberry Pi OS images

### Test Scripts

Basic test automation scripts:
```bash
# scripts/test-all-boards.sh
# Automates building for all board configurations

# scripts/test-remote-deploy.sh
# Automates remote deployment testing

# scripts/test-frameworks.sh
# Tests all framework combinations
```

---

## References

- **Raspberry Pi OS Downloads**: https://www.raspberrypi.com/software/operating-systems/
- **PlatformIO Documentation**: https://docs.platformio.org/
- **Platform Repository**: https://github.com/sfo2001/platform-linux_arm
- **WiringPi (GC2)**: https://github.com/WiringPi/WiringPi
- **lgpio Library**: http://abyz.me.uk/lg/index.html
- **pigpio Library**: http://abyz.me.uk/rpi/pigpio/

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-14 | 1.0 | Initial hardware test matrix document |

---

## Contributing

To add new test configurations or results:
1. Fork the repository
2. Add test results to `test-results/` directory
3. Update this document with new test cases
4. Submit pull request with test logs and results

For questions or issues, please open an issue on GitHub: https://github.com/sfo2001/platform-linux_arm/issues
