# MCP3008 SPI ADC Example (lgpio)

This example demonstrates high-speed SPI communication using the lgpio framework with the MCP3008 8-channel 10-bit Analog-to-Digital Converter (ADC).

## Overview

The MCP3008 is a popular, low-cost ADC chip that provides 8 analog input channels with 10-bit resolution (0-1023). It communicates via SPI and is commonly used for reading analog sensors on Raspberry Pi boards that lack built-in ADC.

**Key Features:**
- 8 single-ended or 4 differential input channels
- 10-bit resolution (1024 discrete levels)
- SPI interface (up to 3.6 MHz at 5V, 1.35 MHz at 2.7V)
- Low power consumption
- Single supply operation (2.7V - 5.5V)

**Common Applications:**
- Reading analog sensors (temperature, light, potentiometers)
- Joystick/gamepad input
- Battery voltage monitoring
- Analog audio input
- Environmental sensing

## About lgpio and SPI

lgpio is a modern C library for Linux GPIO and peripheral access, designed as a successor to deprecated sysfs GPIO and the pigpio library. It uses the kernel's character device interface (`/dev/gpiochip*`, `/dev/spidev*`) introduced in Linux 4.8+.

**SPI (Serial Peripheral Interface)** is a synchronous serial communication protocol that enables high-speed data transfer between a master (Raspberry Pi) and slave devices (MCP3008). SPI is faster than I2C and commonly used for:
- Displays (OLED, LCD, e-paper)
- ADC/DAC chips
- SD cards and flash memory
- High-speed sensors

**Key advantages of lgpio:**
- Works on all Raspberry Pi models including Pi 5
- Modern kernel interface (character device)
- No root privileges required (with proper permissions)
- Actively maintained

## Hardware Requirements

### Components
1. **Raspberry Pi** (any model with SPI support)
2. **MCP3008** ADC chip (DIP-16 package recommended for breadboard)
3. **Breadboard** and jumper wires
4. **Optional:** Analog sensors or potentiometer (10kΩ recommended)

**Where to buy:**
- MCP3008: Available from Adafruit, SparkFun, Amazon (~$3-5)
- Alternative: MCP3004 (4-channel version, pin-compatible)

## Wiring Diagram

### MCP3008 Pinout (DIP-16 Package)

```
         MCP3008
    ┌───────────────┐
CH0 │1            16│ VDD  → 3.3V
CH1 │2            15│ VREF → 3.3V
CH2 │3            14│ AGND → GND
CH3 │4            13│ CLK  → GPIO 11 (SCLK)
CH4 │5            12│ DOUT → GPIO 9  (MISO)
CH5 │6            11│ DIN  → GPIO 10 (MOSI)
CH6 │7            10│ CS   → GPIO 8  (CE0)
CH7 │8             9│ DGND → GND
    └───────────────┘
```

### Connection Table

| MCP3008 Pin | Pin Name | Raspberry Pi Pin | BCM GPIO | Description |
|-------------|----------|------------------|----------|-------------|
| 1-8         | CH0-CH7  | -                | -        | Analog inputs (connect sensors here) |
| 9           | DGND     | Pin 6, 9, 14, etc| GND      | Digital ground |
| 10          | CS/SHDN  | Pin 24           | GPIO 8   | Chip Select (CE0) |
| 11          | DIN      | Pin 19           | GPIO 10  | Master Out Slave In (MOSI) |
| 12          | DOUT     | Pin 21           | GPIO 9   | Master In Slave Out (MISO) |
| 13          | CLK      | Pin 23           | GPIO 11  | SPI Clock (SCLK) |
| 14          | AGND     | Pin 6, 9, 14, etc| GND      | Analog ground (connect to same GND) |
| 15          | VREF     | Pin 1 or 17      | 3.3V     | Reference voltage (max input voltage) |
| 16          | VDD      | Pin 1 or 17      | 3.3V     | Supply voltage |

### Raspberry Pi SPI Pins (All Models)

| Function | BCM GPIO | Physical Pin | Description |
|----------|----------|--------------|-------------|
| MOSI     | GPIO 10  | Pin 19       | Master Out Slave In (data to MCP3008) |
| MISO     | GPIO 9   | Pin 21       | Master In Slave Out (data from MCP3008) |
| SCLK     | GPIO 11  | Pin 23       | Serial Clock |
| CE0      | GPIO 8   | Pin 24       | Chip Enable 0 (primary SPI device) |
| CE1      | GPIO 7   | Pin 26       | Chip Enable 1 (secondary SPI device) |

**Note:** This example uses CE0 (GPIO 8). To use CE1, change `SPI_CHANNEL` to 1 in the code.

### Testing Setup: Potentiometer Connection

To test the ADC, connect a 10kΩ potentiometer to channel 0:

```
Potentiometer:
  Pin 1 (CCW) → GND
  Pin 2 (Wiper) → MCP3008 CH0 (pin 1)
  Pin 3 (CW) → 3.3V
```

**IMPORTANT VOLTAGE WARNING:**
- MCP3008 VREF sets the maximum input voltage
- If VREF = 3.3V, analog inputs must NOT exceed 3.3V
- Exceeding VREF can damage the chip
- For 5V sensors, use a voltage divider or level shifter

## System Requirements

### Enable SPI Interface

SPI is disabled by default on Raspberry Pi. Enable it using:

```bash
# Method 1: Using raspi-config (recommended)
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable

# Method 2: Using command line
sudo raspi-config nonint do_spi 0

# Verify SPI is enabled (should show "SPI on")
raspi-config nonint get_spi
```

After enabling, reboot:
```bash
sudo reboot
```

Verify SPI devices exist:
```bash
ls -l /dev/spidev*
# Should show: /dev/spidev0.0 and /dev/spidev0.1
```

### Install lgpio Library

On your target Raspberry Pi:

```bash
# Update package list
sudo apt update

# Install lgpio library and development files
sudo apt install -y liblgpio-dev liblgpio1
```

### SPI Permissions

To run without root privileges, set SPI device permissions:

```bash
# Temporary (until reboot)
sudo chmod 666 /dev/spidev0.0

# Permanent (create udev rule)
sudo tee /etc/udev/rules.d/99-spi.rules > /dev/null << 'EOF'
SUBSYSTEM=="spidev", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Building

### Cross-Compilation (from development machine)

```bash
# From this directory
pio run

# Build for specific board
pio run -e raspberrypi_4b

# Clean build artifacts
pio run --target clean

# Build and display size
pio run --target size
```

### Supported Build Targets

This example supports all Raspberry Pi models:
- `raspberrypi_3b` (default)
- `raspberrypi_4b`
- `raspberrypi_400`
- `raspberrypi_cm4`
- `raspberrypi_zero2w`
- `raspberrypi_5_64bit` (Pi 5 with 64-bit architecture)

## Deployment and Running

### Manual Deployment

Transfer the compiled binary to your Raspberry Pi:

```bash
# The binary will be in .pio/build/<board_name>/program
scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:~/lgpio-spi-adc

# SSH to Pi and run
ssh pi@raspberrypi.local
./lgpio-spi-adc
```

### Automated Deployment (Upload)

Use PlatformIO's upload feature:

```bash
# Setup (first time only)
ssh-copy-id pi@raspberrypi.local

# Build and upload automatically
pio run -e raspberrypi_4b_upload -t upload

# This will:
# 1. Build the project
# 2. Transfer via SCP to pi@raspberrypi.local
# 3. Automatically run the program
```

Edit `platformio.ini` to customize upload target:
```ini
[env:raspberrypi_4b_upload]
upload_port = pi@raspberrypi.local:/home/pi/lgpio-spi-adc
upload_run_after = true
upload_run_command = sudo /home/pi/lgpio-spi-adc
```

## Expected Output

With a potentiometer connected to channel 0:

```
MCP3008 SPI ADC Example (lgpio framework)
=========================================

Opening SPI device 0.0...
SPI device opened successfully (handle: 3)
SPI speed: 1000000 Hz (1.00 MHz)

MCP3008 Configuration:
  - 8 channels (0-7)
  - 10-bit resolution (0-1023)
  - Reference voltage: 3.3V
  - Single-ended mode

Reading all channels 10 times...
Press Ctrl+C to exit

=== Reading 1/10 ===
  Channel 0:  512 (0x200) |  50.05% | 1.651V
  Channel 1:    0 (0x000) |   0.00% | 0.000V
  Channel 2:    0 (0x000) |   0.00% | 0.000V
  Channel 3:    0 (0x000) |   0.00% | 0.000V
  Channel 4:    0 (0x000) |   0.00% | 0.000V
  Channel 5:    0 (0x000) |   0.00% | 0.000V
  Channel 6:    0 (0x000) |   0.00% | 0.000V
  Channel 7:    0 (0x000) |   0.00% | 0.000V

=== Reading 2/10 ===
  Channel 0: 1023 (0x3FF) | 100.00% | 3.300V
  ...
```

**Output Explanation:**
- **Channel X**: Channel number (0-7)
- **Raw value**: 10-bit ADC reading (0-1023 decimal and hex)
- **Percentage**: Input voltage as percentage of VREF
- **Voltage**: Calculated voltage (assuming 3.3V VREF)

## Code Structure

### Key Functions

**`read_adc(int h, int channel)`**
- Reads 10-bit value from specified MCP3008 channel
- Handles SPI protocol communication
- Returns: 0-1023 or -1 on error

**`adc_to_percentage(int adc_value)`**
- Converts ADC reading to percentage (0-100%)

**`adc_to_voltage(int adc_value)`**
- Converts ADC reading to voltage (assumes 3.3V VREF)

### MCP3008 SPI Protocol

The MCP3008 uses a 3-byte SPI transaction:

**Transmit (TX):**
```
Byte 0: 0x01             (start bit)
Byte 1: 0x8C             (single-ended mode + channel select)
Byte 2: 0x00             (don't care)
```

**Receive (RX):**
```
Byte 0: 0xXX             (don't care)
Byte 1: 0bxxxxxx98       (null bit + MSB bits 9-8)
Byte 2: 0b76543210       (LSB bits 7-0)
```

For channel 0 in single-ended mode:
```
TX: [0x01, 0x80, 0x00]
RX: [0xXX, 0x0Y, 0xZZ]  → Result = ((Y & 0x03) << 8) | ZZ
```

### lgpio SPI Functions Used

- **`lgSpiOpen(dev, channel, speed, flags)`**: Opens SPI device
  - `dev`: SPI bus number (0 = `/dev/spidev0.X`)
  - `channel`: Chip select (0 = CE0, 1 = CE1)
  - `speed`: SPI clock speed in Hz
  - `flags`: SPI mode and configuration

- **`lgSpiXfer(handle, tx, rx, count)`**: Performs full-duplex SPI transfer
  - `handle`: SPI handle from lgSpiOpen
  - `tx`: Transmit buffer
  - `rx`: Receive buffer
  - `count`: Number of bytes to transfer

- **`lgSpiClose(handle)`**: Closes SPI device

## SPI vs I2C: When to Use Each

| Feature | SPI | I2C |
|---------|-----|-----|
| **Speed** | Fast (MHz range) | Moderate (kHz range) |
| **Wiring** | 4+ wires (MOSI, MISO, CLK, CS) | 2 wires (SDA, SCL) |
| **Devices per bus** | Limited by CS pins | Many (127 addresses) |
| **Complexity** | More complex | Simpler |
| **Best for** | High-speed data (displays, ADC) | Many slow devices (sensors) |

**Use SPI when:**
- High data transfer speed is needed (displays, audio)
- Full-duplex communication is required
- Single or few devices on bus

**Use I2C when:**
- Many devices on same bus
- Lower wiring complexity is desired
- Speed is not critical

## Troubleshooting

### "Failed to open SPI device"

**Check SPI is enabled:**
```bash
ls -l /dev/spidev*
# Should list: /dev/spidev0.0 and /dev/spidev0.1
```

If no devices, enable SPI:
```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

**Check permissions:**
```bash
sudo chmod 666 /dev/spidev0.0
```

### Reading 0 or 1023 on all channels

- **All zeros**: Check VDD and VREF are connected to 3.3V
- **All 1023**: Check wiring, especially ground connections
- **Noisy readings**: Add 0.1µF ceramic capacitor between VDD and GND

### Incorrect readings

- Verify VREF voltage matches expected range (use multimeter)
- Check analog input is within 0-VREF range
- Ensure AGND and DGND are connected to same ground
- Verify SPI wiring (MOSI, MISO, CLK, CS)

### Compilation errors

```bash
# Ensure lgpio is installed
sudo apt install liblgpio-dev liblgpio1

# For cross-compilation, see docs/LGPIO_SETUP.md
```

## Advanced Usage

### Multiple MCP3008 Devices

To use multiple MCP3008 chips:
1. Connect second chip to CE1 instead of CE0
2. Open second SPI channel: `lgSpiOpen(0, 1, speed, flags)`

### Higher SPI Speed

The MCP3008 supports up to:
- **3.6 MHz** at 5V (VDD = 5V)
- **1.35 MHz** at 2.7V (VDD = 2.7V)

For 3.3V operation, 1-2 MHz is safe. Increase speed in code:
```c
#define SPI_SPEED 2000000   // 2 MHz
```

### Differential Mode

For differential inputs (measure voltage difference between two channels):
```c
// Channel 0+ vs 0- (pins 1 and 2)
tx[1] = (0x00 | 0) << 4;  // Differential mode + channel pair
```

### Continuous Sampling

For faster sampling, remove the `sleep(2)` delay and run in a tight loop.

## References

- **MCP3008 Datasheet**: https://www.microchip.com/en-us/product/MCP3008
- **lgpio Documentation**: http://abyz.me.uk/lg/lgpio.html
- **lgpio GitHub**: https://github.com/joan2937/lg
- **SPI on Raspberry Pi**: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#serial-peripheral-interface-spi
- **Raspberry Pi Pinout**: https://pinout.xyz/

## Next Steps

After mastering this example, try:
1. **Display Example**: Connect SSD1306 OLED display via SPI
2. **Data Logging**: Log sensor readings to file or database
3. **Web Interface**: Create web dashboard for ADC readings
4. **Multiple Channels**: Read multiple sensors simultaneously
5. **Signal Processing**: Add averaging, filtering, or threshold detection

## License

This example is part of the platform-linux_arm PlatformIO platform.
Licensed under Apache License 2.0.
