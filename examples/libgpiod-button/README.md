# libgpiod Button Input with Interrupts Example

This example demonstrates GPIO input with edge detection (interrupts) using libgpiod v1.x API.

## Description

Monitors a button connected to GPIO 24 and detects both press (falling edge) and release (rising edge) events. Also blinks an LED on GPIO 23 when button is pressed.

## Hardware Setup

### Button
Connect a push button:
- **GPIO 24** (Physical pin 18) → One side of button
- **GND** (Physical pin 6, 9, 14, 20, 25, 30, 34, or 39) → Other side of button
- Internal pull-up resistor is enabled in software

### LED (Optional)
Connect an LED with current-limiting resistor (220Ω - 1kΩ) to:
- **GPIO 23** (Physical pin 16) → LED anode (+)
- **GND** → LED cathode (-)

## Building

```bash
pio run
```

## Running

### Locally (on Raspberry Pi)

```bash
.pio/build/raspberrypi_5/program
```

Press Ctrl+C to exit.

### Remote Deployment

Configure upload in `platformio.ini`:

```ini
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/libgpiod_button
upload_run_after = true
```

Then:

```bash
pio run --target upload
```

## Features

- Edge detection (both rising and falling edges)
- Debouncing via timeout
- LED feedback on button press
- Graceful shutdown with Ctrl+C
- Non-blocking event monitoring

## API Concepts

### Edge Detection

libgpiod supports three edge detection modes:
- **Rising edge**: Signal transitions from LOW to HIGH
- **Falling edge**: Signal transitions from HIGH to LOW
- **Both edges**: Detects all transitions

### Event Monitoring

```c
// Request edge events
gpiod_line_request_both_edges_events(line, "button");

// Wait for events with timeout
struct timespec timeout = {1, 0};  // 1 second
int ret = gpiod_line_event_wait(line, &timeout);

if (ret > 0) {
    // Event occurred, read it
    struct gpiod_line_event event;
    gpiod_line_event_read(line, &event);

    if (event.event_type == GPIOD_LINE_EVENT_RISING_EDGE) {
        printf("Button released\n");
    } else {
        printf("Button pressed\n");
    }
}
```

## References

- libgpiod Documentation: https://libgpiod.readthedocs.io/
- Setup Guide: ../../docs/LIBGPIOD_SETUP.md
- Framework Comparison: ../../docs/FRAMEWORKS.md
