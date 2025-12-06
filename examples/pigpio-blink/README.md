# pigpio Blink Example

This example demonstrates GPIO control using the pigpio framework on Raspberry Pi.

## Hardware Requirements

- Raspberry Pi (models 1, 2, 3, or 4)
- LED connected to GPIO 23 (BCM numbering) with appropriate resistor
- Ground connection

**IMPORTANT**: This example is **NOT compatible with Raspberry Pi 5** due to the new RP1 I/O controller. For Pi 5, use the `lgpio-blink` example instead.

## System Dependencies

Before building or running this example, install the pigpio library on your target Raspberry Pi:

```bash
sudo apt update
sudo apt install -y libpigpio-dev pigpio
```

## Building

Cross-compile from Linux x86_64:

```bash
pio run
```

## Running on Target

Copy the compiled binary to your Raspberry Pi and run:

```bash
# On your Raspberry Pi
./.pio/build/raspberrypi_3b/program
```

Note: GPIO access typically requires root privileges. You may need to run with `sudo` or configure GPIO permissions.

## Wiring Diagram

```
Raspberry Pi GPIO 23 --> LED Anode (+)
LED Cathode (-) --> 220Ω Resistor --> GND
```

## Framework Features

pigpio provides:
- Precise timing and PWM
- Servo control
- Waveform generation
- I2C, SPI, serial communication
- Remote GPIO control via pigpiod daemon

For more information, visit: http://abyz.me.uk/rpi/pigpio/

## Compatibility

| Board | Compatible |
|-------|-----------|
| Raspberry Pi 1 | Yes |
| Raspberry Pi 2 | Yes |
| Raspberry Pi 3 | Yes |
| Raspberry Pi 4 | Yes |
| Raspberry Pi 5 | No (use lgpio) |
| Raspberry Pi Zero | Yes |
