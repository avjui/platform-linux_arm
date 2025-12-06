# lgpio Setup Guide for Cross-Compilation

This guide explains how to set up lgpio for cross-compiling ARM Linux applications with PlatformIO.

## Why lgpio?

**lgpio** is the modern, recommended GPIO library for Raspberry Pi:

- Yes - **Works on ALL Pi models** (Pi 1-5, Zero, CM4, etc.)
- Yes - **Future-proof** - uses kernel `/dev/gpiochip` interface
- Yes - **Recommended by Joan** (pigpio's author) and Raspberry Pi Foundation
- Yes - **Pi 5 compatible** (pigpio is NOT)
- Yes - **Cross-compilation friendly**

**Why not pigpio?**
> Joan (pigpio author): *"pigpio does not work on the Pi 5, I do not think it can be made to work. lgpio will work."*

## Installation Options

### Option 1: Build from Source (Recommended for Cross-Compilation)

This is the most reliable method for cross-compiling:

```bash
# 1. Install ARM cross-compiler if not already installed
sudo apt install gcc-arm-linux-gnueabihf

# 2. Clone and build lgpio
cd /tmp
git clone https://github.com/joan2937/lg.git
cd lg

# 3. Build library for ARM
make CC=arm-linux-gnueabihf-gcc AR=arm-linux-gnueabihf-ar

# 4. Install to cross-compiler sysroot
sudo make install \
    prefix=/usr/local/arm-linux-gnueabihf \
    CC=arm-linux-gnueabihf-gcc

# 5. Update the lgpio framework builder to use this path
# (see builder/frameworks/lgpio.py)
```

### Option 2: System Package with Multi-Arch (Advanced)

If you want to use Ubuntu's packaged version:

```bash
# 1. Add armhf architecture
sudo dpkg --add-architecture armhf

# 2. Configure apt sources for armhf
# Edit /etc/apt/sources.list and add:
deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports noble main universe

# 3. Update and install
sudo apt update
sudo apt install liblgpio-dev:armhf liblgpio1:armhf
```

**Note**: Multi-arch can have dependency conflicts. Option 1 is recommended.

## 64-bit ARM (AArch64) Cross-Compilation

For building 64-bit binaries for Raspberry Pi 4/5/400/CM4 with 64-bit OS:

### Option 1: Build from Source for AArch64 (Recommended)

```bash
# 1. Install AArch64 cross-compiler
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# 2. Clone and build lgpio
cd /tmp
git clone https://github.com/joan2937/lg.git
cd lg

# 3. Build library for AArch64
make CC=aarch64-linux-gnu-gcc AR=aarch64-linux-gnu-ar

# 4. Install to cross-compiler sysroot
sudo make install \
    prefix=/usr/local/aarch64-linux-gnu \
    CC=aarch64-linux-gnu-gcc
```

### Option 2: System Package with Multi-Arch (Advanced)

```bash
# 1. Add arm64 architecture
sudo dpkg --add-architecture arm64

# 2. Configure apt sources for arm64
# Edit /etc/apt/sources.list and add:
deb [arch=arm64] http://ports.ubuntu.com/ubuntu-ports noble main universe

# 3. Update and install
sudo apt update
sudo apt install liblgpio-dev:arm64 liblgpio1:arm64
```

The platform will automatically detect the aarch64 libraries when you set `board_build.arch = aarch64` in your `platformio.ini`.

## Raspberry Pi 1 (Original Models A/B/A+/B+) Support

lgpio supports Pi 1, but requires a workaround for old-style revision codes:

```bash
# Set environment variable before running your program
export RPI_LGPIO_REVISION=800012  # For Pi 1 Model B Rev 2
# 0002 (old-style) = 800012 (new-style)
```

Add this to your platformio.ini for Pi 1:

```ini
[env:raspberrypi_1b]
platform = linux_arm
board = raspberrypi_1b
framework = lgpio
build_flags =
    -DRPI_LGPIO_REVISION=800012
upload_flags =
    --target-remote-extra-args="-e RPI_LGPIO_REVISION=800012"
```

## Verifying Installation

After building from source, verify the installation:

```bash
# Check headers
ls /usr/local/arm-linux-gnueabihf/include/lgpio.h

# Check library
ls /usr/local/arm-linux-gnueabihf/lib/liblgpio.*
```

## Using lgpio in Your Project

In `platformio.ini`:

```ini
[env:raspberrypi_4b]
platform = linux_arm
board = raspberrypi_4b  ; or any Pi 1-5
framework = lgpio
```

Example code:

```c
#include <stdio.h>
#include <lgpio.h>
#include <unistd.h>

#define GPIO_PIN 23

int main() {
    int h = lgGpiochipOpen(0);  // Open GPIO chip 0
    if (h < 0) {
        fprintf(stderr, "Failed to open GPIO chip\n");
        return 1;
    }

    // Claim GPIO as output
    lgGpioClaimOutput(h, 0, GPIO_PIN, 0);

    // Blink LED
    for (int i = 0; i < 10; i++) {
        lgGpioWrite(h, GPIO_PIN, 1);  // HIGH
        sleep(1);
        lgGpioWrite(h, GPIO_PIN, 0);  // LOW
        sleep(1);
    }

    lgGpiochipClose(h);
    return 0;
}
```

## Troubleshooting

### Error: `lgpio.h: No such file or directory`

The framework builder needs to know where lgpio headers are installed. Check:

1. Headers are in `/usr/local/arm-linux-gnueabihf/include/`
2. Framework builder includes correct `-I` path (see `builder/frameworks/lgpio.py`)

### Error: `cannot find -llgpio`

The linker can't find the lgpio library. Check:

1. Library is in `/usr/local/arm-linux-gnueabihf/lib/`
2. Framework builder includes correct `-L` path

### Pi 1 Revision Error

If lgpio reports revision errors on Pi 1, set the `RPI_LGPIO_REVISION` environment variable (see above).

## References

- lgpio Documentation: http://abyz.me.uk/lg/
- lgpio GitHub: https://github.com/joan2937/lg
- Raspberry Pi GPIO White Paper: https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/A-history-of-GPIO-usage-on-Raspberry-Pi-devices-and-current-best-practices
