# Linux ARM: development platform for [PlatformIO](https://platformio.org)

[![Examples](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml/badge.svg)](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml)

Linux ARM is a Unix-like and mostly POSIX-compliant computer operating system (OS) assembled under the model of free and open-source software development and distribution. This platform enables building native applications for ARM-based Linux systems (Raspberry Pi, Orange Pi) using PlatformIO Core 6.0+.

**Key Features:**
- Cross-compilation support from Linux x86_64, macOS (Intel/ARM), and Windows
- Native compilation on ARM Linux systems
- **Automated deployment** to remote targets via SCP, rsync, or SSH
- Support for Raspberry Pi 1-5, Pi 400, Compute Module 4, and Zero/Zero 2W
- Support for Orange Pi Zero (Allwinner H2+/H3)
- Modern GPIO frameworks: lgpio (Pi 5 compatible) and pigpio
- Legacy WiringPi framework for compatibility
- Bare-metal C/C++ application support

* [Home](https://registry.platformio.org/platforms/platformio/linux_arm) (home page in the PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/platforms/linux_arm.html) (advanced usage, packages, boards, frameworks, etc.)

# Cross-Compilation Setup

This platform supports cross-compilation from various host systems. The platform automatically detects your system and configures the appropriate toolchain.

## Linux (x86_64)

Install the ARM cross-compilation toolchain:

```bash
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
```

## macOS (Intel or Apple Silicon)

Install using Homebrew:

```bash
brew install arm-linux-gnueabihf-binutils
```

Or download the ARM GNU Toolchain from the [ARM Developer website](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads).

## Windows

Download and install the ARM GNU Toolchain from the [ARM Developer website](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads). Make sure the toolchain binaries are in your PATH.

## Native ARM Linux

When running PlatformIO directly on a Raspberry Pi or other ARM Linux system, the platform uses the system's native GCC compiler. No additional toolchain installation is required.

# Architecture Support (32-bit vs 64-bit)

This platform supports both 32-bit ARM (ARMv7) and 64-bit ARM (AArch64/ARMv8) architectures.

## Default: 32-bit ARM (ARMv7)

By default, all boards use 32-bit cross-compilation for maximum compatibility. This works with both 32-bit and 64-bit Raspberry Pi OS installations.

**Toolchain requirements:**
```bash
# Linux
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# macOS
brew tap messense/macos-cross-toolchains
brew install arm-unknown-linux-gnueabihf
```

## 64-bit ARM (AArch64) - Optional

For Raspberry Pi 4, Pi 5, Pi 400, and CM4 running a 64-bit OS, you can build 64-bit binaries by setting `board_build.arch = aarch64` in your `platformio.ini`:

```ini
[env:raspberrypi_5_64bit]
platform = linux_arm
board = raspberrypi_5
framework = lgpio
board_build.arch = aarch64
```

**Toolchain requirements:**
```bash
# Linux
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# macOS
brew tap messense/macos-cross-toolchains
brew install aarch64-unknown-linux-gnu
```

**Note:** 64-bit builds require a 64-bit Raspberry Pi OS installation on the target device. For cross-compilation setup with lgpio framework, you'll also need the 64-bit library:

```bash
# For cross-compilation with lgpio on 64-bit targets
sudo dpkg --add-architecture arm64
sudo apt install liblgpio-dev:arm64
```

# Supported Boards

## Raspberry Pi Boards

- `raspberrypi_1b` - Raspberry Pi 1 Model B
- `raspberrypi_2b` - Raspberry Pi 2 Model B
- `raspberrypi_3b` - Raspberry Pi 3 Model B
- `raspberrypi_4b` - Raspberry Pi 4 Model B
- `raspberrypi_400` - Raspberry Pi 400 (keyboard computer, 1.8GHz)
- `raspberrypi_5` - Raspberry Pi 5 (lgpio recommended, WiringPi has GCLK limitation)
- `raspberrypi_cm4` - Raspberry Pi Compute Module 4
- `raspberrypi_zero` - Raspberry Pi Zero
- `raspberrypi_zero2w` - Raspberry Pi Zero 2 W

## Orange Pi Boards

- `orangepi_zero` - Orange Pi Zero (Allwinner H2+/H3, 256MB/512MB RAM)

# Usage

1. [Install PlatformIO](https://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = linux_arm
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/platformio/platform-linux_arm.git
board = ...
...
```

# Frameworks

This platform supports multiple frameworks for GPIO access:

## lgpio Framework (Recommended for new projects)

Modern GPIO library supporting all Raspberry Pi models including Pi 5:

```ini
[env:raspberrypi_5]
platform = linux_arm
framework = lgpio
board = raspberrypi_5
```

**System requirements:**
```bash
sudo apt install liblgpio-dev liblgpio1
```

See `examples/lgpio-blink/` for a complete example.

## pigpio Framework

Advanced GPIO library with precise timing, PWM, and servo control (Pi 1-4 only):

```ini
[env:raspberrypi_4b]
platform = linux_arm
framework = pigpio
board = raspberrypi_4b
```

**System requirements:**
```bash
sudo apt install libpigpio-dev pigpio
```

**Note:** pigpio is NOT compatible with Raspberry Pi 5. Use lgpio for Pi 5.

See `examples/pigpio-blink/` for a complete example.

## WiringPi Framework (GC2 Fork)

Classic GPIO library with Arduino-like API, now maintained by GC2 (Grazer Computer Club) with Pi 5 support:

```ini
[env:raspberrypi_5]
platform = linux_arm
framework = wiringpi
board = raspberrypi_5
```

**System requirements:**
```bash
sudo apt install wiringpi
```

Or build from source:
```bash
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
./build debian
sudo apt install ./wiringpi-*.deb
```

**Pi 5 Limitations:** The GCLK (general purpose clock) functionality is not supported on Pi 5 due to RP1 chip documentation limitations. For full Pi 5 GPIO functionality, use the lgpio framework instead.

**Note:** WiringPi currently requires building directly on a Raspberry Pi device (cross-compilation is not supported for WiringPi).

See `examples/wiringpi-blink/` and `examples/wiringpi-serial/` for complete examples.

## Bare-Metal Application (No Framework)

Create a simple C/C++ application without any framework:

```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b
; No framework specified - bare-metal C application
```

See `examples/baremetal-hello/` for a complete example.

# Building and Running

## Build a project

```bash
# From your project directory
pio run

# Build for specific environment
pio run -e raspberrypi_4b

# Clean build artifacts
pio run --target clean
```

## Upload and deploy to remote target

The platform supports **automated deployment** to remote Raspberry Pi or Orange Pi devices via SCP, rsync, or SSH:

```bash
# Upload using configured protocol
pio run --target upload

# Or combined: build + upload
pio run -t upload
```

**Quick setup** in `platformio.ini`:

```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp
```

**Supported upload protocols:**
- **`scp`** - Secure copy (recommended, simple and reliable)
- **`rsync`** - Incremental sync (faster for repeated uploads)
- **`ssh`** - SSH with piped input (alternative method)
- **`manual`** - Shows instructions only (default)

**See detailed documentation:**
- Complete guide: [`docs/UPLOAD.md`](docs/UPLOAD.md)
- Working example: [`examples/remote-deployment/`](examples/remote-deployment/)

## Run the compiled program

### Option 1: Automated upload and execution

Configure automatic execution after upload:

```ini
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp
upload_run_after = true
```

Then run:
```bash
pio run -t upload  # Builds, uploads, and runs automatically
```

### Option 2: Manual transfer and execution

Transfer the compiled binary to your Raspberry Pi and run it:

```bash
# Copy to target
scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:/home/pi/

# SSH and run
ssh pi@raspberrypi.local
sudo /home/pi/program  # Use sudo for GPIO access
```

# Configuration

Please navigate to [documentation](https://docs.platformio.org/page/platforms/linux_arm.html).
