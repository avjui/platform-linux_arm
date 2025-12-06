# BME280 I2C Sensor Example (lgpio)

This example demonstrates I2C bus communication using the lgpio framework with the BME280 environmental sensor, which measures temperature, humidity, and atmospheric pressure.

## Overview

The BME280 is a highly integrated environmental sensor combining temperature, humidity, and pressure sensing in a single chip. It communicates via I2C (or SPI) and is one of the most popular sensors for IoT and weather monitoring projects.

**Key Features:**
- 3-in-1 sensor: temperature, humidity, and pressure
- I2C interface (address 0x76 or 0x77)
- High accuracy: ±1°C, ±3% RH, ±1 hPa
- Low power consumption (~3.6µA @ 1Hz)
- Small form factor (2.5mm x 2.5mm)
- Wide voltage range: 1.71V - 3.6V

**Common Applications:**
- Weather stations
- Indoor climate monitoring
- Altitude measurement (barometric altimeter)
- HVAC systems
- Smart home automation
- Drone/UAV altitude sensing
- Health and fitness devices

## About lgpio and I2C

lgpio is a modern C library for Linux GPIO and peripheral access, designed as a successor to deprecated sysfs GPIO and the pigpio library. It uses the kernel's character device interface (`/dev/gpiochip*`, `/dev/i2c*`) introduced in Linux 4.8+.

**I2C (Inter-Integrated Circuit)** is a synchronous serial communication protocol that enables multiple devices to share a common two-wire bus. I2C is ideal for:
- Connecting multiple sensors on the same bus (up to 127 devices)
- Short-distance communication (on-board devices)
- Simple wiring (only 2 signal wires: SDA and SCL)
- Sensors, displays, EEPROMs, RTCs, and other peripherals

**Key advantages of lgpio:**
- Works on all Raspberry Pi models including Pi 5
- Modern kernel interface (character device)
- No daemon required (unlike pigpio)
- Actively maintained
- Direct hardware access

## Hardware Requirements

### Components
1. **Raspberry Pi** (any model with I2C support - all models)
2. **BME280 sensor module** (I2C breakout board recommended)
3. **Breadboard** and jumper wires (or direct wiring)

**Where to buy:**
- BME280 modules: Available from Adafruit, SparkFun, Amazon (~$5-15)
- Look for: "BME280 I2C breakout" or "GY-BME280"
- Alternative: BMP280 (temperature + pressure only, same pinout)

**Note:** Most BME280 breakout boards include:
- Voltage regulator (allows 3.3V or 5V power)
- Pull-up resistors on SDA/SCL (required for I2C)
- Level shifting (if needed)

## Wiring Diagram

### BME280 Module Pinout (Typical Breakout Board)

```
    BME280 Breakout
    ┌─────────────┐
VIN │●            │  → 3.3V (Pin 1 or 17)
GND │●            │  → GND (Pin 6, 9, 14, 20, etc)
SCL │●            │  → GPIO 3 (Pin 5) - I2C Clock
SDA │●            │  → GPIO 2 (Pin 3) - I2C Data
    └─────────────┘
```

### Connection Table

| BME280 Pin | Raspberry Pi Pin | BCM GPIO | Description |
|------------|------------------|----------|-------------|
| VIN or VCC | Pin 1 or 17      | 3.3V     | Power supply (3.3V recommended) |
| GND        | Pin 6, 9, 14, etc| GND      | Ground |
| SCL        | Pin 5            | GPIO 3   | I2C Clock (with 1.8kΩ pull-up) |
| SDA        | Pin 3            | GPIO 2   | I2C Data (with 1.8kΩ pull-up) |

### Raspberry Pi I2C Pins (All Models)

| Function | BCM GPIO | Physical Pin | Description |
|----------|----------|--------------|-------------|
| SDA      | GPIO 2   | Pin 3        | I2C Data (bidirectional) |
| SCL      | GPIO 3   | Pin 5        | I2C Clock |

**Important Notes:**
- The Raspberry Pi has built-in 1.8kΩ pull-up resistors on I2C pins
- Most BME280 breakout boards also include pull-ups (this is fine - parallel resistors are acceptable)
- Use I2C bus 1 (`/dev/i2c-1`) - this is the default user-accessible I2C bus
- I2C bus 0 is reserved for HAT EEPROM on 40-pin models

### I2C Address Selection

BME280 sensors can have one of two I2C addresses:
- **0x76** (118 decimal) - SDO pin connected to GND (most common)
- **0x77** (119 decimal) - SDO pin connected to VDD

Most breakout boards default to 0x76. This example automatically scans both addresses.

### Multiple Sensors on Same Bus

I2C allows multiple devices on the same bus. To connect multiple BME280 sensors:
1. Use different I2C addresses (one sensor at 0x76, another at 0x77)
2. Connect SDA/SCL in parallel to all sensors
3. Each sensor needs separate VDD and GND connections

```
Raspberry Pi        BME280 #1 (0x76)    BME280 #2 (0x77)
GPIO 2 (SDA) ────┬─── SDA ──────────────── SDA
GPIO 3 (SCL) ────┼─── SCL ──────────────── SCL
3.3V ────────────┼─── VIN ──────────────── VIN
GND ─────────────┴─── GND ──────────────── GND
```

## System Requirements

### Enable I2C Interface

I2C is disabled by default on Raspberry Pi. Enable it using:

```bash
# Method 1: Using raspi-config (recommended)
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable

# Method 2: Using command line
sudo raspi-config nonint do_i2c 0

# Verify I2C is enabled (should show "I2C on")
raspi-config nonint get_i2c
```

After enabling, reboot:
```bash
sudo reboot
```

Verify I2C devices exist:
```bash
ls -l /dev/i2c*
# Should show: /dev/i2c-1 (and possibly /dev/i2c-0 on older models)
```

### Install lgpio Library

On your target Raspberry Pi:

```bash
# Update package list
sudo apt update

# Install lgpio library and development files
sudo apt install -y liblgpio-dev liblgpio1
```

### Install I2C Tools (Optional but Recommended)

I2C tools help verify sensor connectivity:

```bash
# Install i2c-tools package
sudo apt install -y i2c-tools

# Scan I2C bus for connected devices
i2cdetect -y 1

# Example output with BME280 at 0x76:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 70: -- -- -- -- -- -- 76 --
```

### I2C Permissions

To run without root privileges, set I2C device permissions:

```bash
# Temporary (until reboot)
sudo chmod 666 /dev/i2c-1

# Permanent (create udev rule)
sudo tee /etc/udev/rules.d/99-i2c.rules > /dev/null << 'EOF'
SUBSYSTEM=="i2c-dev", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Alternatively, add your user to the `i2c` group:
```bash
sudo usermod -aG i2c $USER
# Log out and back in for changes to take effect
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
- `raspberrypi_1b` - Original Raspberry Pi
- `raspberrypi_2b` - Raspberry Pi 2
- `raspberrypi_3b` (default) - Raspberry Pi 3
- `raspberrypi_4b` - Raspberry Pi 4
- `raspberrypi_400` - Raspberry Pi 400
- `raspberrypi_cm4` - Compute Module 4
- `raspberrypi_zero` - Raspberry Pi Zero
- `raspberrypi_zero2w` - Raspberry Pi Zero 2 W
- `raspberrypi_5_64bit` - Raspberry Pi 5 (64-bit)

All models have I2C support on GPIO 2/3.

## Deployment and Running

### Manual Deployment

Transfer the compiled binary to your Raspberry Pi:

```bash
# The binary will be in .pio/build/<board_name>/program
scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:~/lgpio-i2c-sensor

# SSH to Pi and run
ssh pi@raspberrypi.local
./lgpio-i2c-sensor
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
upload_port = pi@raspberrypi.local:/home/pi/lgpio-i2c-sensor
upload_run_after = true
upload_run_command = sudo /home/pi/lgpio-i2c-sensor
```

## Expected Output

When the BME280 is properly connected and working:

```
BME280 I2C Sensor Example (lgpio framework)
============================================

Scanning for BME280 at address 0x76...
✓ BME280 found at address 0x76

Opening I2C device 1 at address 0x76...
I2C device opened successfully (handle: 3)
Initializing BME280 sensor...
✓ Sensor initialized successfully

BME280 Configuration:
  - Temperature: 1x oversampling
  - Pressure: 1x oversampling
  - Humidity: 1x oversampling
  - Mode: Normal (continuous)
  - Standby: 1000ms

Reading sensor data 10 times...
Press Ctrl+C to exit

=== Reading 1/10 ===
  Temperature:  22.45 °C
  Humidity:     45.23 %
  Pressure:    1013.25 hPa

=== Reading 2/10 ===
  Temperature:  22.47 °C
  Humidity:     45.18 %
  Pressure:    1013.28 hPa

...
```

**Output Explanation:**
- **Temperature**: Ambient temperature in degrees Celsius
- **Humidity**: Relative humidity as percentage (0-100%)
- **Pressure**: Atmospheric pressure in hectopascals (hPa) or millibars

**Typical Values:**
- Temperature: -40°C to +85°C (sensor range), typically 15-30°C indoors
- Humidity: 0-100%, typically 30-60% indoors
- Pressure: 300-1100 hPa, typically 980-1050 hPa at sea level

**Note:** Pressure varies with altitude:
- Sea level: ~1013 hPa
- 500m elevation: ~955 hPa
- 1000m elevation: ~899 hPa

## Code Structure

### Key Functions

**`scan_for_bme280(int *addr)`**
- Scans I2C bus for BME280 sensor at addresses 0x76 and 0x77
- Returns: 0 on success, -1 if sensor not found
- Sets `addr` to the found I2C address

**`bme280_init(int h)`**
- Initializes BME280 sensor
- Verifies chip ID
- Performs soft reset
- Reads calibration data
- Configures measurement settings
- Returns: 0 on success, -1 on error

**`bme280_read_calibration(int h)`**
- Reads factory calibration coefficients from sensor
- Required for compensating raw measurements
- Called automatically by `bme280_init()`

**`bme280_read_data(int h, float *temp, float *press, float *hum)`**
- Reads raw sensor data
- Applies compensation formulas using calibration data
- Returns temperature (°C), pressure (hPa), and humidity (%)

**`bme280_compensate_temperature(int32_t adc_T)`**
- Converts raw temperature ADC value to degrees Celsius
- Calculates `t_fine` (needed for pressure/humidity compensation)
- Uses factory calibration coefficients

**`bme280_compensate_pressure(int32_t adc_P)`**
- Converts raw pressure ADC value to hectopascals
- Requires `t_fine` from temperature compensation

**`bme280_compensate_humidity(int32_t adc_H)`**
- Converts raw humidity ADC value to percentage
- Requires `t_fine` from temperature compensation

### BME280 Communication Protocol

The BME280 uses register-based I2C communication:

**Reading a Register:**
```c
// Read single byte from register 0xD0 (Chip ID)
uint8_t chip_id;
lgI2cReadByteData(handle, 0xD0);
```

**Writing a Register:**
```c
// Write 0xB6 to register 0xE0 (soft reset)
lgI2cWriteByteData(handle, 0xE0, 0xB6);
```

**Reading Multiple Bytes:**
```c
// Read 8 bytes starting from register 0xF7 (sensor data)
uint8_t data[8];
lgI2cReadI2CBlockData(handle, 0xF7, data, 8);
```

### Measurement Flow

1. **Initialization:**
   - Verify chip ID (should be 0x60 for BME280)
   - Soft reset sensor
   - Read 33 bytes of calibration data
   - Configure oversampling and mode

2. **Continuous Measurement:**
   - Read 8 bytes from registers 0xF7-0xFE
   - Parse into 20-bit pressure, temperature, humidity
   - Apply compensation using calibration data
   - Temperature must be calculated first (produces `t_fine`)

3. **Compensation Formulas:**
   - Formulas from BME280 datasheet (Bosch Sensortec)
   - Uses integer arithmetic for efficiency
   - Calibration coefficients are sensor-specific

### lgpio I2C Functions Used

- **`lgI2cOpen(bus, address, flags)`**: Opens I2C device
  - `bus`: I2C bus number (1 = `/dev/i2c-1`)
  - `address`: 7-bit I2C device address (0x76 or 0x77)
  - `flags`: Reserved (use 0)

- **`lgI2cReadByteData(handle, reg)`**: Reads single byte from register
  - Returns byte value (0-255) or negative error code

- **`lgI2cWriteByteData(handle, reg, value)`**: Writes single byte to register
  - Returns 0 on success, negative on error

- **`lgI2cReadI2CBlockData(handle, reg, buffer, count)`**: Reads multiple bytes
  - Reads `count` bytes starting from `reg` into `buffer`
  - Returns bytes read or negative error code

- **`lgI2cClose(handle)`**: Closes I2C device

## I2C vs SPI: When to Use Each

| Feature | I2C | SPI |
|---------|-----|-----|
| **Wiring** | 2 wires (SDA, SCL) | 4+ wires (MOSI, MISO, CLK, CS) |
| **Speed** | Moderate (100kHz-3.4MHz) | Fast (MHz range) |
| **Devices per bus** | Many (up to 127) | Limited by CS pins |
| **Complexity** | Simpler | More complex |
| **Best for** | Many slow devices | High-speed data transfers |

**Use I2C when:**
- Connecting multiple sensors to the same bus
- Wiring simplicity is important
- Moderate speed is acceptable (most sensors)
- Sensors are close to the Raspberry Pi

**Use SPI when:**
- High data transfer speed is needed (displays, audio, ADC)
- Full-duplex communication is required
- Single or few devices on bus

**BME280 Note:** The BME280 supports both I2C and SPI. This example uses I2C for simplicity.

## Troubleshooting

### "BME280 not found on I2C bus"

**Step 1: Verify I2C is enabled**
```bash
ls -l /dev/i2c*
# Should list: /dev/i2c-1
```

If not present, enable I2C:
```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

**Step 2: Check sensor is detected**
```bash
# Install i2c-tools if needed
sudo apt install i2c-tools

# Scan I2C bus
i2cdetect -y 1

# Should show:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# ...
# 70: -- -- -- -- -- -- 76 --
```

If `i2cdetect` doesn't show device at 0x76 or 0x77:
- Check wiring (especially SDA/SCL connections)
- Verify power is connected (VIN to 3.3V, GND to GND)
- Try a different BME280 module (hardware failure)
- Check for shorts or loose connections

**Step 3: Verify wiring**
```
BME280 VIN  → Raspberry Pi 3.3V (Pin 1 or 17)
BME280 GND  → Raspberry Pi GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
BME280 SCL  → Raspberry Pi GPIO 3 (Pin 5)
BME280 SDA  → Raspberry Pi GPIO 2 (Pin 3)
```

### "Failed to open I2C device"

**Check permissions:**
```bash
ls -l /dev/i2c-1
# Should show: crw-rw-rw- or crw-rw---- with group i2c

# Fix permissions temporarily:
sudo chmod 666 /dev/i2c-1

# Or add user to i2c group permanently:
sudo usermod -aG i2c $USER
# Log out and back in
```

### Unrealistic Readings

**All zeros or random values:**
- Sensor not properly initialized
- Wiring issue (especially power)
- Corrupted calibration data

**Temperature too high:**
- BME280 self-heats when reading continuously
- Use longer standby time or forced mode
- Ensure good airflow around sensor

**Pressure doesn't match weather report:**
- Weather reports show sea-level adjusted pressure
- Your reading is absolute pressure at your altitude
- To convert to sea-level: `P_sea = P * (1 - 0.0065*h/288.15)^-5.255`
  where `h` is altitude in meters

**Humidity stuck at 0% or 100%:**
- Check humidity configuration register (0xF2)
- Ensure calibration data read correctly
- Sensor may be damaged

### Compilation Errors

```bash
# Ensure lgpio is installed on target Pi
sudo apt install liblgpio-dev liblgpio1

# For cross-compilation, see platform documentation
# lgpio headers must be available in toolchain
```

### "Invalid chip ID" Error

If you see:
```
Invalid chip ID: 0x58 (expected 0x60)
```

You likely have a **BMP280** (no humidity) instead of BME280:
- BMP280 chip ID is 0x58
- BME280 chip ID is 0x60
- BMP280 has same pinout but no humidity sensor
- This code requires BME280 specifically

## Advanced Usage

### Changing Oversampling

Higher oversampling reduces noise but increases measurement time and power:

```c
// In bme280_init(), modify configuration:

// Temperature oversampling x16 (vs x1 default)
// Pressure oversampling x16 (vs x1 default)
// Humidity oversampling x16 (vs x1 default)
uint8_t ctrl_meas = (BME280_OVERSAMPLING_16X << 5) |
                    (BME280_OVERSAMPLING_16X << 2) |
                    BME280_MODE_NORMAL;
lgI2cWriteByteData(h, BME280_REG_CTRL_MEAS, ctrl_meas);
```

**Oversampling vs Performance:**
| Oversampling | Current (µA) | Time (ms) | Noise Reduction |
|--------------|--------------|-----------|-----------------|
| 1x           | 3.6          | 6.4       | Baseline        |
| 2x           | 5.6          | 8.7       | √2 better       |
| 4x           | 9.4          | 13.3      | 2x better       |
| 16x          | 28.6         | 37.5      | 4x better       |

### Forced Mode (On-Demand Measurements)

For battery-powered applications, use forced mode instead of normal mode:

```c
// Configure forced mode (sensor sleeps between measurements)
uint8_t ctrl_meas = (BME280_OVERSAMPLING_1X << 5) |
                    (BME280_OVERSAMPLING_1X << 2) |
                    BME280_MODE_FORCED;

// Take measurement
lgI2cWriteByteData(h, BME280_REG_CTRL_MEAS, ctrl_meas);
usleep(10000);  // Wait for measurement to complete
bme280_read_data(h, &temp, &press, &hum);
```

### IIR Filter

Enable the internal IIR filter to reduce short-term fluctuations:

```c
// In bme280_init(), modify config register:
// Filter coefficient 16 (vs off)
lgI2cWriteByteData(h, BME280_REG_CONFIG, 0x10);
```

**Filter Coefficients:**
- 0: Filter off
- 1: Coefficient 2
- 2: Coefficient 4
- 3: Coefficient 8
- 4: Coefficient 16 (smoothest)

### Altitude Calculation

Calculate altitude from pressure:

```c
#define SEA_LEVEL_PRESSURE 1013.25  // hPa, adjust for your location

float calculate_altitude(float pressure) {
    return 44330.0 * (1.0 - pow(pressure / SEA_LEVEL_PRESSURE, 0.1903));
}
```

**Note:** For accurate altitude, use current sea-level pressure from local weather station.

### Data Logging

Log sensor data to file:

```c
FILE *fp = fopen("sensor_log.csv", "a");
fprintf(fp, "%ld,%.2f,%.2f,%.2f\n",
        time(NULL), temperature, humidity, pressure);
fclose(fp);
```

## Application Ideas

After mastering this example, try:

1. **Weather Station**: Log data to database, create web dashboard
2. **Indoor Air Quality Monitor**: Combine with CO2 and VOC sensors
3. **Altitude Logger**: Record altitude profile for hiking/drone flights
4. **Greenhouse Controller**: Monitor and control climate
5. **Home Automation**: Integrate with Home Assistant or OpenHAB
6. **Alert System**: Send notifications when conditions exceed thresholds
7. **MQTT Publisher**: Send sensor data to IoT platform
8. **E-ink Display**: Show current conditions on e-paper display

## References

- **BME280 Datasheet**: https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/
- **BME280 Application Notes**: https://www.bosch-sensortec.com/media/boschsensortec/downloads/application_notes_1/bst-bme280-an004.pdf
- **lgpio Documentation**: http://abyz.me.uk/lg/lgpio.html
- **lgpio GitHub**: https://github.com/joan2937/lg
- **I2C on Raspberry Pi**: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#i2c
- **Raspberry Pi Pinout**: https://pinout.xyz/
- **i2c-tools Manual**: https://manpages.debian.org/testing/i2c-tools/i2cdetect.8.en.html

## Datasheets and Specifications

- **BME280**: https://cdn-shop.adafruit.com/datasheets/BST-BME280_DS001-10.pdf
- **BMP280** (pressure/temp only): https://cdn-shop.adafruit.com/datasheets/BST-BMP280-DS001-11.pdf
- **I2C Specification**: https://www.nxp.com/docs/en/user-guide/UM10204.pdf

## License

This example is part of the platform-linux_arm PlatformIO platform.
Licensed under Apache License 2.0.
