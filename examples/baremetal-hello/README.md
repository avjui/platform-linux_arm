# Bare-Metal Hello World Example

This example demonstrates building a simple C application for Linux ARM without using any framework (bare-metal).

## Description

A minimal "Hello World" program that:
- Uses standard C library (stdio.h)
- No hardware-specific framework required
- Can be cross-compiled from x86_64/ARM64 hosts
- Detects the target Raspberry Pi model from build flags

## Building

```bash
# Build for Raspberry Pi 3
pio run -e raspberrypi_3b

# Build for Raspberry Pi 4
pio run -e raspberrypi_4b

# Clean build artifacts
pio run --target clean
```

## Running

After building, run the program on your Raspberry Pi:

```bash
# For Raspberry Pi 3
.pio/build/raspberrypi_3b/program

# For Raspberry Pi 4
.pio/build/raspberrypi_4b/program
```

## Cross-Compilation

This example can be cross-compiled from:
- Linux x86_64
- macOS (Intel or Apple Silicon)
- Windows x86_64

Make sure you have the ARM cross-compilation toolchain installed:

**Linux:**
```bash
sudo apt install gcc-arm-linux-gnueabihf
```

**macOS:**
```bash
brew install arm-linux-gnueabihf-binutils
```

**Windows:**
Download and install the ARM GNU Toolchain from the ARM Developer website.

## Note

Unlike the WiringPi examples, this bare-metal example does not require running on actual Raspberry Pi hardware for compilation. It can be cross-compiled on any supported host platform.
