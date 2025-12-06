# libgpiod LED Blink Example (v2 API)

This example demonstrates basic GPIO output using the **libgpiod v2.x API**.

## Description

Blinks an LED connected to GPIO 23 (BCM numbering) with a 1-second interval using the modern libgpiod v2 API.

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
upload_port = pi@raspberrypi.local:/home/pi/libgpiod_blink_v2
upload_run_after = true
```

Then:

```bash
pio run --target upload
```

## API Version

This example uses the **libgpiod v2.x API**:
- Modern, object-oriented design
- More flexible configuration options
- Better support for bulk operations
- Recommended for new projects (Debian Bookworm, Ubuntu 22.04+)

For the simpler v1.x API, see `../libgpiod-blink/`

## Code Structure

```c
// Open GPIO chip
struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");

// Create request configuration
struct gpiod_request_config *req_cfg = gpiod_request_config_new();
gpiod_request_config_set_consumer(req_cfg, "blink-example");

// Create line configuration
struct gpiod_line_config *line_cfg = gpiod_line_config_new();
gpiod_line_config_set_direction_default(line_cfg, GPIOD_LINE_DIRECTION_OUTPUT);
gpiod_line_config_set_output_value_default(line_cfg, 0);

// Request lines
struct gpiod_line_request *request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

// Toggle GPIO
gpiod_line_request_set_value(request, 23, 1);  // High
gpiod_line_request_set_value(request, 23, 0);  // Low

// Cleanup
gpiod_line_request_release(request);
gpiod_line_config_free(line_cfg);
gpiod_request_config_free(req_cfg);
gpiod_chip_close(chip);
```

## References

- libgpiod v2 Documentation: https://libgpiod.readthedocs.io/en/latest/
- Setup Guide: ../../docs/LIBGPIOD_SETUP.md
- Framework Comparison: ../../docs/FRAMEWORKS.md
