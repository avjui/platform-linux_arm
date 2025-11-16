# Linux ARM: development platform for [PlatformIO](https://platformio.org)

[![Examples](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml/badge.svg)](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml)

> This is an actively maintained fork of the official [platformio/platform-linux_arm](https://github.com/platformio/platform-linux_arm) platform (last updated May 2022). Adds Raspberry Pi 5 support, lgpio framework, remote development workflows, and additional examples. See [CHANGELOG.md](CHANGELOG.md) for details.

Linux ARM platform enables building native applications for ARM-based Linux systems (Raspberry Pi, Orange Pi, etc.) using PlatformIO Core 6.0+. Supports both cross-compilation from your development machine and native compilation on ARM devices.

## Key Features

- Cross-compilation from Linux x86_64, macOS (Intel/ARM), and Windows
- Native compilation on ARM Linux systems
- Remote workflows: automated deployment, testing, and debugging over SSH
- Multiple GPIO frameworks: lgpio (Pi 5 compatible), pigpio, WiringPi
- Board support: Raspberry Pi 1-5, Pi 400, CM4, Zero/Zero 2W, Orange Pi Zero
- Architecture support: 32-bit (ARMv7) and 64-bit (AArch64)

## Documentation

- [Platform Documentation](docs/platforms/linux_arm.rst) - Complete platform reference
- [Installation & Setup](#installation) - Quick start guide
- [Configuration Files](docs/CONFIGURATION.md) - Global defaults and project overrides
- [Remote Deployment](docs/UPLOAD.md) - Upload programs via SCP/rsync/SSH
- [Remote Debugging](docs/DEBUGGING.md) - GDB debugging over SSH
- [Testing Guide](docs/TESTING.md) - Automated remote test execution
- [VS Code Integration](docs/VSCODE.md) - IDE setup and debugging
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Contributing](CONTRIBUTING.md) - How to contribute

> **Note for VS Code users:** The PlatformIO GUI's "Monitor" button is for serial ports only and does not work with this platform. For SSH monitoring support, copy [examples/vscode/tasks.json](examples/vscode/tasks.json) to your project's `.vscode/` folder. See [docs/VSCODE.md](docs/VSCODE.md) for details.

> **📌 VS Code Users:** The PlatformIO GUI's "Monitor" button doesn't work with this platform (it's for serial ports only). Copy [examples/vscode/tasks.json](examples/vscode/tasks.json) to your project's `.vscode/` folder for SSH monitoring support. See [docs/VSCODE.md](docs/VSCODE.md) for details.

## Installation

### 1. Install PlatformIO

If you haven't already:
```bash
pip install -U platformio
```

Or install [PlatformIO IDE](https://platformio.org/install/ide) for VS Code, CLion, or other IDEs.

### 2. Install Cross-Compilation Toolchain

Choose based on your development machine:

**Linux (x86_64):**
```bash
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
```

**macOS (Intel or Apple Silicon):**
```bash
brew tap messense/macos-cross-toolchains
brew install arm-unknown-linux-gnueabihf
```

**Windows:**
Download the [ARM GNU Toolchain](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) and add to PATH.

**Native ARM Linux (Raspberry Pi):**
No toolchain needed - uses system GCC.

### 3. Create Your Project

Create a `platformio.ini` file:

```ini
[env:raspberrypi_4b]
platform = https://github.com/sfo2001/platform-linux_arm.git
board = raspberrypi_4b
framework = lgpio

; Optional: Remote deployment
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp
```

Or use a stable release:
```ini
platform = linux_arm@^1.8.0
```

## Quick Start Examples

### Basic GPIO Blink (lgpio)

```c
#include <lgpio.h>
#include <stdio.h>
#include <unistd.h>

#define LED_PIN 17

int main(void) {
    int h = lgGpiochipOpen(4);  // gpiochip4 on Pi 5, gpiochip0 on older
    if (h < 0) return 1;

    lgGpioClaimOutput(h, 0, LED_PIN, 0);

    while(1) {
        lgGpioWrite(h, LED_PIN, 1);
        sleep(1);
        lgGpioWrite(h, LED_PIN, 0);
        sleep(1);
    }

    lgGpiochipClose(h);
    return 0;
}
```

See `examples/` directory for more:
- `lgpio-blink/` - Basic GPIO control
- `lgpio-i2c-sensor/` - I2C sensor reading (BME280)
- `lgpio-pwm-fade/` - Hardware PWM LED fading
- `lgpio-spi-adc/` - SPI communication (MCP3008)
- `baremetal-threads/` - Multi-threading with POSIX threads
- `remote-deployment/` - Automated deployment example
- `remote-debugging/` - Remote debugging setup

## Security Considerations

This platform uses SSH for remote operations (upload, test, debug). Review security configuration:

- Security Guidelines: See [SECURITY.md](SECURITY.md) for security documentation
- SSH Key Setup: Use dedicated SSH keys for PlatformIO (not personal keys)
- Timeouts: Configure timeouts to prevent hung connections
- Host Verification: Enable strict host key checking in production environments

Quick Security Checklist:
- [ ] Using dedicated SSH key (not personal key)
- [ ] SSH key permissions set to 600 (`chmod 600 ~/.ssh/key`)
- [ ] Host key verification enabled for production
- [ ] Timeouts configured appropriately
- [ ] No credentials committed to version control

For detailed security configuration, see [SECURITY.md](SECURITY.md).

Recent Security Improvements (v1.7.1):
- Fixed command injection vulnerabilities (CVSS 8.0-9.0)
- Added timeout protection against DoS attacks
- Added security documentation

## Supported Boards

| Board ID | Description | Frameworks | Architectures |
|----------|-------------|------------|---------------|
| `raspberrypi_1b` | Raspberry Pi 1 Model B | lgpio, wiringpi | ARMv6 (32-bit) |
| `raspberrypi_2b` | Raspberry Pi 2 Model B | lgpio, pigpio, wiringpi | ARMv7 (32-bit) |
| `raspberrypi_3b` | Raspberry Pi 3 Model B | lgpio, pigpio, wiringpi | ARMv8 (32/64-bit) |
| `raspberrypi_4b` | Raspberry Pi 4 Model B | lgpio, pigpio, wiringpi | ARMv8 (32/64-bit) |
| `raspberrypi_5` | Raspberry Pi 5 | lgpio, wiringpi | ARMv8 (32/64-bit) |
| `raspberrypi_400` | Raspberry Pi 400 | lgpio, pigpio, wiringpi | ARMv8 (32/64-bit) |
| `raspberrypi_cm4` | Compute Module 4 | lgpio, pigpio, wiringpi | ARMv8 (32/64-bit) |
| `raspberrypi_zero` | Raspberry Pi Zero | lgpio, wiringpi | ARMv6 (32-bit) |
| `raspberrypi_zero2w` | Raspberry Pi Zero 2 W | lgpio, pigpio, wiringpi | ARMv8 (32/64-bit) |
| `orangepi_zero` | Orange Pi Zero (H2+/H3) | lgpio | ARMv7 (32-bit) |

**Note:** pigpio is not compatible with Raspberry Pi 5. Use lgpio for Pi 5.

## GPIO Frameworks

### lgpio (Recommended)

GPIO library supporting all Raspberry Pi models including Pi 5.

```ini
[env:my_project]
framework = lgpio
```

Features: Digital I/O, I2C, SPI, hardware PWM
Setup: See [docs/LGPIO_SETUP.md](docs/LGPIO_SETUP.md) and [docs/PWM_SETUP.md](docs/PWM_SETUP.md)

### pigpio

GPIO library with microsecond timing (Pi 1-4 only, not compatible with Pi 5).

```ini
[env:my_project]
framework = pigpio
```

Note: Deprecated - use lgpio for new projects.

### WiringPi (GC2 Fork)

Arduino-like API with Pi 5 support (GCLK limitation on Pi 5).

```ini
[env:my_project]
framework = wiringpi
```

Note: Cross-compilation not supported - must build on target device.

See [docs/FRAMEWORKS.md](docs/FRAMEWORKS.md) for detailed comparison.

## Building and Deploying

### Build Locally
```bash
pio run
```

### Upload to Remote Device
```bash
pio run --target upload
```

Requires `upload_protocol` configuration - see [docs/UPLOAD.md](docs/UPLOAD.md).

### Run Tests on Hardware
```bash
pio test
```

Requires `test_transport = ssh` - see [docs/TESTING.md](docs/TESTING.md).

### Debug Remotely
```bash
pio debug
```

Requires `debug_tool = gdbserver-ssh` - see [docs/DEBUGGING.md](docs/DEBUGGING.md) and [docs/VSCODE.md](docs/VSCODE.md).

## Advanced Configuration

### 64-bit ARM (AArch64)

For Raspberry Pi 4/5/400/CM4 running 64-bit OS:

```ini
[env:raspberrypi_5_64bit]
platform = linux_arm
board = raspberrypi_5
framework = lgpio
board_build.arch = aarch64
```

Requires 64-bit toolchain:
```bash
# Linux
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# macOS
brew install aarch64-unknown-linux-gnu
```

### Custom Build Flags

```ini
[env:custom]
build_flags =
    -O2
    -Wall
    -DMY_CUSTOM_DEFINE
```

### Multiple Environments

```ini
[env:cross_compile]
platform = linux_arm
board = raspberrypi_4b

[env:native]
platform = native
; For testing on development machine
```

See [Platform Documentation](docs/platforms/linux_arm.rst) for all configuration options.

## Project Structure

```
your-project/
├── platformio.ini        # Project configuration
├── src/
│   └── main.c           # Your source code
├── include/             # Header files
├── lib/                 # Project libraries
└── test/                # Unit tests
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/sfo2001/platform-linux_arm/issues)
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.

## Acknowledgments

- Original platform by [PlatformIO](https://platformio.org)
- lgpio library by [joan2937](http://abyz.me.uk/lg/lgpio.html)
- pigpio library by [joan2937](http://abyz.me.uk/rpi/pigpio/)
- WiringPi GC2 fork by [Grazer Computer Club](https://github.com/WiringPi/WiringPi)

---

**Version**: 1.8.0
**Maintained by**: [@sfo2001](https://github.com/sfo2001)
**Original**: [platformio/platform-linux_arm](https://github.com/platformio/platform-linux_arm)
