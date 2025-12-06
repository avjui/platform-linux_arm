# Linux ARM: development platform for [PlatformIO](https://platformio.org)

[![Examples](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml/badge.svg)](https://github.com/sfo2001/platform-linux_arm/actions/workflows/examples.yml)

Linux ARM is a Unix-like and mostly POSIX-compliant computer operating system (OS) assembled under the model of free and open-source software development and distribution. This platform enables building native applications for ARM-based Linux systems (Raspberry Pi, Orange Pi) using PlatformIO Core 6.0+.

**Key Features:**
- Cross-compilation support from Linux x86_64, macOS (Intel/ARM), and Windows
- Native compilation on ARM Linux systems
- **Automated deployment** to remote targets via SCP, rsync, or SSH
- **Remote test execution** with automated SSH deployment and real-time results
- **Remote debugging** with GDB/gdbserver over SSH (IDE-integrated)
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

## Remote Debugging

The platform supports **IDE-integrated remote debugging** using GDB/gdbserver over SSH. This enables debugging ARM Linux applications running on Raspberry Pi from your development machine.

### Quick Start

1. **Build with debug symbols:**
   ```ini
   [env:debug]
   platform = linux_arm
   board = raspberrypi_4b
   framework = lgpio

   build_flags =
       -O0           ; No optimization
       -g3           ; Full debug info
       -ggdb         ; GDB-specific format

   upload_protocol = scp
   upload_port = pi@raspberrypi.local:/home/pi/myapp

   debug_tool = gdbserver-ssh
   debug_port = pi@raspberrypi.local
   ```

2. **Upload and start debugging:**
   ```bash
   # Upload debug build
   pio run -t upload

   # Start debugging session
   pio debug
   ```

### Features

- **SSH-tunneled debugging** - Secure connection using existing SSH authentication
- **IDE integration** - Works with VS Code, CLion, and other PlatformIO-compatible IDEs (see [docs/VSCODE.md](docs/VSCODE.md))
- **Automatic setup** - Platform handles gdbserver connection and symbol loading
- **Architecture support** - Automatic GDB selection for 32-bit (ARMv7) and 64-bit (AArch64)

### Prerequisites

**On development machine:**
- Cross-compilation toolchain with GDB:
  ```bash
  # Linux (32-bit ARM)
  sudo apt install gcc-arm-linux-gnueabihf gdb-multiarch

  # Linux (64-bit ARM)
  sudo apt install gcc-aarch64-linux-gnu gdb-multiarch

  # macOS
  brew tap messense/macos-cross-toolchains
  brew install arm-unknown-linux-gnueabihf
  # or for 64-bit: aarch64-unknown-linux-gnu
  ```

**On target device (Raspberry Pi):**
- gdbserver (usually pre-installed on Raspberry Pi OS)
- SSH server running

### Debug Tools

The platform provides two debugging methods:

#### 1. `gdbserver-ssh` (Recommended)
Uses SSH tunnel to connect GDB to gdbserver. This is secure, automatic, and works from anywhere with SSH access.

```ini
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local
```

#### 2. `gdb-remote` (Manual)
Direct TCP connection to manually-started gdbserver. Useful for advanced scenarios or debugging already-running processes.

```ini
debug_tool = gdb-remote
debug_port = raspberrypi.local:2345
```

### Debugging Workflow

**In VS Code:**
1. Set breakpoints by clicking line gutters
2. Press F5 or click "Start Debugging"
3. Use debug toolbar to step through code
4. Inspect variables in the Variables panel

**In CLI:**
```bash
pio debug

(gdb) break main              # Set breakpoint
(gdb) run                     # Start program
(gdb) next                    # Step over
(gdb) print local_var         # Inspect variable
(gdb) backtrace               # View call stack
(gdb) continue                # Continue execution
```

### See Also

- **VS Code Integration Guide:** [`docs/VSCODE.md`](docs/VSCODE.md) - Complete VS Code setup, IntelliSense, debugging, and troubleshooting
- **Debugging Guide:** [`docs/DEBUGGING.md`](docs/DEBUGGING.md) - Comprehensive remote debugging reference
- **Example Project:** [`examples/remote-debugging/`](examples/remote-debugging/) - Working debugging example with 7+ scenarios
- **PlatformIO Debug Docs:** https://docs.platformio.org/en/latest/plus/debugging.html

## Remote Test Execution

The platform supports **automated remote test execution** on ARM Linux targets. Tests are cross-compiled on your development machine, deployed via SSH, executed on the target hardware, and results are streamed back in real-time.

### Quick Start

1. **Configure test transport** in `platformio.ini`:
   ```ini
   [env:raspberrypi_3b]
   platform = linux_arm
   board = raspberrypi_3b

   ; Upload configuration (reused for tests)
   upload_protocol = scp
   upload_port = pi@raspberrypi.local:/tmp/program

   ; Test configuration
   test_transport = ssh
   test_build_src = yes  ; Include src/ files in test builds
   ```

2. **Write tests** using Unity framework:
   ```c
   #include <unity.h>

   void test_example(void) {
       TEST_ASSERT_EQUAL(42, my_function());
   }

   int main(int argc, char **argv) {
       UNITY_BEGIN();
       RUN_TEST(test_example);
       return UNITY_END();
   }
   ```

3. **Run tests:**
   ```bash
   pio test
   ```

### Features

- **Automated SSH deployment** - Tests are uploaded and executed automatically
- **Real-time results** - Test output streamed back to host as it runs
- **CI/CD ready** - Perfect for GitHub Actions, GitLab CI, Jenkins
- **Hardware testing** - Run integration tests on actual GPIO, I2C, SPI devices
- **Multiple targets** - Run same tests on different boards in parallel

### Use Cases

1. **Unit Tests** - Test business logic on target architecture
2. **Integration Tests** - Test hardware interaction (GPIO, sensors, displays)
3. **System Tests** - End-to-end testing on real hardware
4. **CI/CD Pipelines** - Automated testing before deployment

### Example Output

```
Testing remote-testing:raspberrypi_3b [PASSED]
===========================================

test/test_math/test_main.c:18:test_addition      [PASSED]
test/test_math/test_main.c:24:test_subtraction   [PASSED]
test/test_gpio/test_main.c:31:test_led_blink     [PASSED]

----------------------
3 Tests 0 Failures 0 Ignored
OK
```

### See Also

- **Testing Guide:** [`REMOTE_TESTING.md`](REMOTE_TESTING.md) - Comprehensive testing guide with CI/CD examples
- **Example Project:** [`examples/remote-testing/`](examples/remote-testing/) - Complete working example
- **PlatformIO Testing Docs:** https://docs.platformio.org/en/latest/advanced/unit-testing/

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
