# libgpiod LED Blink Example (v1 API)

This example demonstrates basic GPIO output using the **libgpiod v1.x API**.

## Description

Blinks an LED connected to GPIO 23 (BCM numbering) with a 1-second interval.

## Hardware Setup

Connect an LED with current-limiting resistor (220Ω - 1kΩ) to:
- **GPIO 23** (Physical pin 16) → LED anode (+)
- **GND** (Physical pin 6, 9, 14, 20, 25, 30, 34, or 39) → LED cathode (-)

## GPIO State Persistence

Partial - **Important**: By default, the GPIO may revert to input mode when the program exits.

To enable persistent GPIO state on Raspberry Pi, add to `/boot/firmware/config.txt`:

```
dtparam=strict_gpiod
```

Then reboot.

## Building

```bash
pio run
```

## Running

### Locally (on Raspberry Pi)

```bash
.pio/build/raspberrypi_5/program
```

### Remote Deployment

Configure upload in `platformio.ini`:

```ini
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/libgpiod_blink
upload_run_after = true
```

Then:

```bash
pio run --target upload
```

## API Version

This example uses the **libgpiod v1.x API**:
- Simpler, function-based API
- Widely deployed (Debian Bullseye, Ubuntu 20.04)
- Good for beginners

For the modern v2.x API, see `../libgpiod-blink-v2/`

## Code Structure

```c
// Open GPIO chip
struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");

// Get GPIO line
struct gpiod_line *line = gpiod_chip_get_line(chip, 23);

// Request line as output
gpiod_line_request_output(line, "blink", 0);

// Toggle GPIO
gpiod_line_set_value(line, 1);  // High
gpiod_line_set_value(line, 0);  // Low

// Cleanup
gpiod_line_release(line);
gpiod_chip_close(chip);
```

## References

- libgpiod Documentation: https://libgpiod.readthedocs.io/
- Setup Guide: ../../docs/LIBGPIOD_SETUP.md
- Framework Comparison: ../../docs/FRAMEWORKS.md
