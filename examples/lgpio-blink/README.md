# lgpio LED Blink Example

This example demonstrates using the lgpio framework to blink an LED on a Raspberry Pi.

## About lgpio

lgpio is a modern C library for Linux GPIO access, designed as a successor to deprecated sysfs GPIO and the pigpio library. It uses the GPIO character device (`/dev/gpiochip*`) introduced in Linux kernel 4.8.

**Key advantages:**
- Works on all Raspberry Pi models including Pi 5
- Modern kernel GPIO interface (character device)
- No root privileges required (with proper udev rules)
- Actively maintained

## Hardware Setup

1. Connect an LED with appropriate resistor (330Ω recommended) to GPIO 23 (BCM numbering)
2. Connect the LED cathode (short leg) to ground

GPIO 23 is physical pin 16 on the 40-pin header.

## System Requirements

Before building, install the lgpio library on your target system:

```bash
# On Raspberry Pi OS or Debian/Ubuntu
sudo apt update
sudo apt install -y liblgpio-dev liblgpio1
```

## Building

```bash
# From this directory
pio run

# Clean build
pio run --target clean

# Build and display size
pio run --target size
```

## Running

Transfer the compiled program to your Raspberry Pi and run:

```bash
# The binary will be in .pio/build/raspberrypi_3b/program
./.pio/build/raspberrypi_3b/program
```

The LED should blink 10 times (1 second on, 1 second off).

## Supported Boards

This example works on all Raspberry Pi boards:
- Raspberry Pi 1 Model B
- Raspberry Pi 2 Model B
- Raspberry Pi 3 Model B
- Raspberry Pi 4 Model B
- Raspberry Pi Zero
- Raspberry Pi 5 (when board definition is added)

To build for a different board, edit `platformio.ini` and change the `board` value.

## Cross-Compilation

This platform supports cross-compilation from Linux x86_64, macOS, and Windows systems. See the main platform README for setup instructions.

## GPIO Permissions

For running without root privileges, add a udev rule:

```bash
# Create /etc/udev/rules.d/99-gpio.rules
SUBSYSTEM=="gpio*", KERNEL=="gpiochip*", MODE="0666"

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Troubleshooting

**"Failed to open gpiochip0":**
- Check that `/dev/gpiochip0` exists
- Verify lgpio library is installed
- Check file permissions on `/dev/gpiochip0`

**Compilation errors:**
- Ensure `liblgpio-dev` is installed
- Verify you're using PlatformIO Core 6.0+

## References

- lgpio documentation: http://abyz.me.uk/lg/lgpio.html
- lgpio GitHub: https://github.com/joan2937/lg
