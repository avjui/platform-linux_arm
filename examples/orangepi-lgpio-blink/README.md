# Orange Pi Zero - LED Blink Example

This example demonstrates GPIO control on the Orange Pi Zero using the lgpio framework.

## Hardware Requirements

- Orange Pi Zero (256MB or 512MB variant)
- LED and 220Ω resistor (optional, for external LED)
- Jumper wires

## GPIO Pin

This example uses PA6 (GPIO 6), which is physical pin 7 on the Orange Pi Zero 13-pin header.

### Pin Mapping
- **Physical Pin 7**: PA6 (GPIO 6)
- Connect LED cathode (short leg) to GND (pin 9)
- Connect LED anode (long leg) to PA6 through 220Ω resistor

## Building

```bash
# Change directory to example
cd platform-linux_arm/examples/orangepi-lgpio-blink

# Build project
pio run

# Run program (requires root privileges for GPIO access)
sudo .pio/build/orangepi_zero/program

# Clean build files
pio run --target clean
```

## Notes

- This example must be run directly on the Orange Pi Zero (not cross-compiled)
- Root privileges are required for GPIO access via lgpio
- The lgpio framework is the modern replacement for deprecated sysfs GPIO
- For different GPIO pins, modify the `GPIO_PIN` define in src/blink.c

## Orange Pi Zero GPIO Layout

The Orange Pi Zero has a 13-pin header with the following GPIO pins:
- PA6, PA7, PA8, PA9, PA10, PA11, PA12, PA13, PA14, PA15, PA16, PA17, PA18, PA19, PA20, PA21

Refer to the [Orange Pi Zero documentation](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero.html) for complete pinout details.
