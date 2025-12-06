# PWM Hardware Abstraction Layer (HAL) Setup Guide

Complete guide for setting up and using hardware PWM on Raspberry Pi with the Linux ARM platform.

## Table of Contents

- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)
- [References](#references)

## Overview

The PWM HAL provides a user-friendly C interface for hardware PWM control using the Linux kernel PWM subsystem. It offers:

- **GPIO pin-based API**: Automatically maps GPIO pins to PWM chip/channel
- **Hardware PWM**: Precise timing without CPU overhead
- **Universal compatibility**: Works on all Raspberry Pi models (1-5)
- **Comprehensive error handling**: Clear error messages for permissions, busy channels, invalid pins
- **Kernel-based**: Uses standard Linux `/sys/class/pwm` interface (sysfs)

### Use Cases

- **LED control**: Brightness control, smooth fading effects
- **Motor control**: Speed control, soft start/stop
- **Servo motors**: Position control (50 Hz PWM)
- **Audio**: Tone generation, buzzer control
- **Power regulation**: DC-DC converters, voltage regulation

## Hardware Requirements

### Raspberry Pi Models

All Raspberry Pi models with 40-pin GPIO headers:

| Model | PWM Chip | PWM Channels | Notes |
|-------|----------|--------------|-------|
| Pi 1 (A, B, A+, B+) | pwmchip0 | 2 | Original models |
| Pi 2 Model B | pwmchip0 | 2 | |
| Pi 3 (A+, B, B+) | pwmchip0 | 2 | |
| Pi 4 Model B | pwmchip0 | 2 | Most popular |
| Pi 400 | pwmchip0 | 2 | Keyboard form factor |
| Compute Module 4 | pwmchip0 | 2 | Industrial module |
| Pi Zero (W, WH) | pwmchip0 | 2 | Compact |
| Pi Zero 2 W | pwmchip0 | 2 | Quad-core |
| Pi 5 | pwmchip2, pwmchip3 | 4 | RP1 chip, 4 channels |

### PWM-Capable GPIO Pins

#### Pi 1-4 (BCM283x SoC)

| GPIO | PWM Channel | Alt Function | Default | Notes |
|------|-------------|--------------|---------|-------|
| 12   | PWM0        | ALT0         | -       | Primary PWM0 pin |
| 13   | PWM1        | ALT0         | -       | Primary PWM1 pin |
| 18   | PWM0        | ALT5         | ✓       | **Recommended** (conflicts with GPIO 12) |
| 19   | PWM1        | ALT5         | ✓       | **Recommended** (conflicts with GPIO 13) |

**Important**: GPIO 12 and 18 share PWM0. GPIO 13 and 19 share PWM1. Cannot use both simultaneously.

#### Pi 5 (RP1 I/O Controller)

| GPIO | PWM Channel | PWM Chip | Notes |
|------|-------------|----------|-------|
| 12   | PWM0        | pwmchip2 | Channel 0 |
| 13   | PWM1        | pwmchip2 | Channel 1 |
| 18   | PWM0        | pwmchip2 | Channel 0 (conflicts with GPIO 12) |
| 19   | PWM1        | pwmchip2 | Channel 1 (conflicts with GPIO 13) |

Pi 5 has additional PWM channels via pwmchip3 (GPIO 2, 3) - future support planned.

## Software Requirements

### Operating System

- Raspberry Pi OS (Bookworm or later recommended)
- Ubuntu for Raspberry Pi
- Other ARM Linux distributions with kernel 4.8+

### Kernel Requirements

- Linux kernel 4.8+ (GPIO character device support)
- PWM subsystem enabled (standard in Raspberry Pi OS)

### Device Tree Overlay

PWM must be enabled in the device tree:

**For Pi 1-4**, edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

**For Pi 5**, edit `/boot/firmware/config.txt`:
```bash
sudo nano /boot/firmware/config.txt
```

Add one of the following overlays:

#### Single Channel (GPIO 18)

```
dtoverlay=pwm,pin=18,func=2
```

#### Dual Channel (GPIO 18 + 19)

```
dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2
```

#### Custom GPIO Pins

```
dtoverlay=pwm,pin=12,func=4     # GPIO 12 (ALT0)
dtoverlay=pwm,pin=13,func=4     # GPIO 13 (ALT0)
```

**Important**: Reboot after making changes:
```bash
sudo reboot
```

### Verify Device Tree Overlay

Check if PWM hardware is detected:

**Pi 1-4**:
```bash
ls /sys/class/pwm/pwmchip0
```

**Pi 5**:
```bash
ls /sys/class/pwm/pwmchip2
```

Expected output:
```
device  export  npwm  power  subsystem  uevent  unexport
```

## Quick Start

### 1. Enable Device Tree Overlay

```bash
# Pi 1-4
echo "dtoverlay=pwm,pin=18,func=2" | sudo tee -a /boot/config.txt

# Pi 5
echo "dtoverlay=pwm,pin=18,func=2" | sudo tee -a /boot/firmware/config.txt

# Reboot
sudo reboot
```

### 2. Setup Permissions

```bash
cd /path/to/platform-linux_arm
sudo ./scripts/setup-pwm-perms.sh
```

### 3. Build Example

```bash
cd examples/lgpio-pwm-fade
pio run -e raspberrypi_4b
```

### 4. Run Example

```bash
sudo ./.pio/build/raspberrypi_4b/program
```

You should see the LED fading in and out!

## Detailed Setup

### Step 1: Device Tree Configuration

#### Understanding Device Tree Overlays

Device tree overlays configure hardware peripherals at boot time. PWM overlays:

- Export PWM hardware to the kernel
- Configure GPIO pin alternate functions
- Make PWM channels available in `/sys/class/pwm`

#### Available Overlays

| Overlay | Pins | Channels | Use Case |
|---------|------|----------|----------|
| `pwm` | 1 GPIO | 1 channel | Single LED/motor |
| `pwm-2chan` | 2 GPIOs | 2 channels | Dual LED/motor |
| `pwm-ir-tx` | 1 GPIO | 1 channel | IR transmitter |

#### Overlay Parameters

```
dtoverlay=pwm[,OPTIONS]
```

Options:
- `pin=N` - GPIO pin number (12, 13, 18, or 19)
- `func=N` - Alternate function (2 for GPIO 18/19, 4 for GPIO 12/13)

#### Configuration Examples

**LED on GPIO 18**:
```
dtoverlay=pwm,pin=18,func=2
```

**Two LEDs on GPIO 18 and 19**:
```
dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2
```

**Motor on GPIO 12**:
```
dtoverlay=pwm,pin=12,func=4
```

### Step 2: Permissions Setup

#### Manual Setup

Export PWM channel:
```bash
# Pi 1-4 (pwmchip0, channel 0)
echo 0 | sudo tee /sys/class/pwm/pwmchip0/export

# Pi 5 (pwmchip2, channel 0)
echo 0 | sudo tee /sys/class/pwm/pwmchip2/export
```

Set permissions:
```bash
# Pi 1-4
sudo chown -R root:gpio /sys/class/pwm/pwmchip0/pwm0
sudo chmod -R ug+rw /sys/class/pwm/pwmchip0/pwm0

# Pi 5
sudo chown -R root:gpio /sys/class/pwm/pwmchip2/pwm0
sudo chmod -R ug+rw /sys/class/pwm/pwmchip2/pwm0
```

Add user to gpio group:
```bash
sudo usermod -a -G gpio $USER
# Log out and back in for changes to take effect
```

#### Automated Setup Script

Use the provided script for automatic configuration:

```bash
sudo ./scripts/setup-pwm-perms.sh
```

Script features:
- Auto-detects Pi model (pwmchip0 vs pwmchip2)
- Exports multiple channels (default: 2)
- Sets group ownership (default: gpio)
- Configures read/write permissions
- Validates configuration

Options:
```bash
sudo ./scripts/setup-pwm-perms.sh --chip 0      # Force pwmchip0 (Pi 1-4)
sudo ./scripts/setup-pwm-perms.sh --chip 2      # Force pwmchip2 (Pi 5)
sudo ./scripts/setup-pwm-perms.sh --channels 1  # Export only 1 channel
sudo ./scripts/setup-pwm-perms.sh --help        # Show all options
```

### Step 3: Systemd Service (Optional)

Automatically setup PWM permissions on boot:

**Install service**:
```bash
sudo cp scripts/platformio-pwm.service /etc/systemd/system/
sudo systemctl enable platformio-pwm.service
sudo systemctl start platformio-pwm.service
```

**Check status**:
```bash
sudo systemctl status platformio-pwm.service
```

**View logs**:
```bash
sudo journalctl -u platformio-pwm.service
```

**Uninstall service**:
```bash
sudo systemctl stop platformio-pwm.service
sudo systemctl disable platformio-pwm.service
sudo rm /etc/systemd/system/platformio-pwm.service
```

## API Reference

### Core Functions

#### pwm_init()

Initialize PWM on a GPIO pin with specified frequency.

```c
int pwm_init(int pin, uint32_t freq_hz);
```

**Parameters**:
- `pin` - GPIO pin number (12, 13, 18, or 19)
- `freq_hz` - Frequency in Hz (1 Hz to 100 MHz)

**Returns**:
- `PWM_SUCCESS` (0) on success
- Error code on failure (see [Error Codes](#error-codes))

**Example**:
```c
// Initialize GPIO 18 at 1 kHz
int result = pwm_init(18, 1000);
if (result != PWM_SUCCESS) {
    fprintf(stderr, "Error: %s\n", pwm_error_string(result));
}
```

---

#### pwm_write()

Set PWM duty cycle as a percentage.

```c
int pwm_write(int pin, float duty_cycle_percent);
```

**Parameters**:
- `pin` - GPIO pin number
- `duty_cycle_percent` - Duty cycle (0.0 to 100.0%)

**Returns**:
- `PWM_SUCCESS` (0) on success
- Error code on failure

**Example**:
```c
// Set 75% duty cycle (75% power)
pwm_write(18, 75.0);

// Turn off (0% duty cycle)
pwm_write(18, 0.0);

// Full power (100% duty cycle)
pwm_write(18, 100.0);
```

---

#### pwm_deinit()

Disable and release PWM channel.

```c
int pwm_deinit(int pin);
```

**Parameters**:
- `pin` - GPIO pin number

**Returns**:
- `PWM_SUCCESS` (0) on success
- Error code on failure

**Example**:
```c
// Cleanup when done
pwm_deinit(18);
```

---

### Extended Functions

#### pwm_set_frequency()

Change PWM frequency without changing duty cycle.

```c
int pwm_set_frequency(int pin, uint32_t freq_hz);
```

**Parameters**:
- `pin` - GPIO pin number
- `freq_hz` - New frequency in Hz

**Returns**:
- `PWM_SUCCESS` (0) on success
- Error code on failure

**Example**:
```c
// Change frequency to 5 kHz
pwm_set_frequency(18, 5000);
```

**Note**: Changing frequency may cause brief output glitch.

---

#### pwm_set_polarity()

Set PWM output polarity (normal or inverted).

```c
int pwm_set_polarity(int pin, pwm_polarity_t polarity);
```

**Parameters**:
- `pin` - GPIO pin number
- `polarity` - `PWM_POLARITY_NORMAL` or `PWM_POLARITY_INVERTED`

**Returns**:
- `PWM_SUCCESS` (0) on success
- Error code on failure

**Example**:
```c
// Normal polarity (high = active)
pwm_set_polarity(18, PWM_POLARITY_NORMAL);

// Inverted polarity (low = active)
pwm_set_polarity(18, PWM_POLARITY_INVERTED);
```

**Note**: PWM must be initialized first. Output is temporarily disabled during polarity change.

---

#### pwm_get_status()

Query current PWM status and configuration.

```c
int pwm_get_status(int pin, pwm_status_t *status);
```

**Parameters**:
- `pin` - GPIO pin number
- `status` - Pointer to `pwm_status_t` structure

**Returns**:
- `PWM_SUCCESS` (0) on success
- Error code on failure

**Example**:
```c
pwm_status_t status;
if (pwm_get_status(18, &status) == PWM_SUCCESS) {
    printf("Frequency: %u Hz\n", status.frequency_hz);
    printf("Duty Cycle: %.1f%%\n", status.duty_cycle_percent);
    printf("Enabled: %s\n", status.is_enabled ? "yes" : "no");
}
```

**Status Structure**:
```c
typedef struct {
    int gpio_pin;              // GPIO pin number
    int pwm_chip;              // PWM chip (0 or 2)
    int pwm_channel;           // Channel (0 or 1)
    bool is_enabled;           // Output enabled
    bool is_exported;          // Channel exported
    uint32_t frequency_hz;     // Frequency (Hz)
    float duty_cycle_percent;  // Duty cycle (%)
    pwm_polarity_t polarity;   // Polarity
    uint64_t period_ns;        // Period (nanoseconds)
    uint64_t duty_cycle_ns;    // Duty cycle (nanoseconds)
} pwm_status_t;
```

---

#### pwm_is_enabled()

Check if PWM channel is enabled.

```c
bool pwm_is_enabled(int pin);
```

**Parameters**:
- `pin` - GPIO pin number

**Returns**:
- `true` if enabled
- `false` if disabled or not initialized

**Example**:
```c
if (pwm_is_enabled(18)) {
    printf("PWM is active\n");
}
```

---

### Utility Functions

#### pwm_error_string()

Get human-readable error message.

```c
const char* pwm_error_string(pwm_error_t error);
```

**Parameters**:
- `error` - Error code

**Returns**:
- Pointer to static error message string

**Example**:
```c
int result = pwm_init(18, 1000);
if (result != PWM_SUCCESS) {
    printf("Error: %s\n", pwm_error_string(result));
}
```

---

#### pwm_pin_is_valid()

Check if GPIO pin supports PWM.

```c
bool pwm_pin_is_valid(int pin);
```

**Parameters**:
- `pin` - GPIO pin number

**Returns**:
- `true` if pin supports PWM
- `false` otherwise

**Example**:
```c
if (!pwm_pin_is_valid(18)) {
    printf("GPIO 18 does not support PWM\n");
}
```

---

#### pwm_get_chip_channel()

Get PWM chip and channel for a GPIO pin.

```c
int pwm_get_chip_channel(int pin, int *chip, int *channel);
```

**Parameters**:
- `pin` - GPIO pin number
- `chip` - Pointer to store chip number (output)
- `channel` - Pointer to store channel number (output)

**Returns**:
- `PWM_SUCCESS` (0) on success
- `PWM_ERROR_INVALID_PIN` if not a PWM pin

**Example**:
```c
int chip, channel;
if (pwm_get_chip_channel(18, &chip, &channel) == PWM_SUCCESS) {
    printf("GPIO 18 -> pwmchip%d, channel %d\n", chip, channel);
}
```

---

### Error Codes

```c
typedef enum {
    PWM_SUCCESS = 0,              // Success
    PWM_ERROR_INVALID_PIN = -1,   // GPIO pin does not support PWM
    PWM_ERROR_PERMISSION = -2,    // Permission denied
    PWM_ERROR_BUSY = -3,          // Channel already in use
    PWM_ERROR_NOT_EXPORTED = -4,  // Channel not exported
    PWM_ERROR_INVALID_PARAM = -5, // Invalid parameter value
    PWM_ERROR_IO = -6,            // I/O error accessing sysfs
    PWM_ERROR_NOT_ENABLED = -7,   // Channel not enabled
    PWM_ERROR_HARDWARE = -8       // Hardware-specific limitation
} pwm_error_t;
```

---

### Complete Example

```c
#include <stdio.h>
#include "pwm-hal.h"

int main() {
    int pin = 18;
    int freq = 1000;  // 1 kHz

    // Validate pin
    if (!pwm_pin_is_valid(pin)) {
        printf("Invalid PWM pin\n");
        return 1;
    }

    // Initialize PWM
    int result = pwm_init(pin, freq);
    if (result != PWM_SUCCESS) {
        printf("Error: %s\n", pwm_error_string(result));
        return 1;
    }

    // Set 50% duty cycle
    pwm_write(pin, 50.0);

    // Query status
    pwm_status_t status;
    pwm_get_status(pin, &status);
    printf("Frequency: %u Hz\n", status.frequency_hz);

    // Cleanup
    pwm_deinit(pin);

    return 0;
}
```

## Troubleshooting

### Permission denied (PWM_ERROR_PERMISSION)

**Symptoms**:
```
ERROR: Failed to initialize PWM: Permission denied (run setup-pwm-perms.sh)
```

**Causes**:
1. PWM permissions not setup
2. User not in gpio group
3. Wrong file ownership

**Solutions**:

1. Run setup script:
   ```bash
   sudo ./scripts/setup-pwm-perms.sh
   ```

2. Add user to gpio group:
   ```bash
   sudo usermod -a -G gpio $USER
   # Log out and back in
   ```

3. Manual permission fix:
   ```bash
   # Pi 1-4
   sudo chown -R root:gpio /sys/class/pwm/pwmchip0/pwm0
   sudo chmod -R ug+rw /sys/class/pwm/pwmchip0/pwm0

   # Pi 5
   sudo chown -R root:gpio /sys/class/pwm/pwmchip2/pwm0
   sudo chmod -R ug+rw /sys/class/pwm/pwmchip2/pwm0
   ```

---

### PWM channel not exported (PWM_ERROR_NOT_EXPORTED)

**Symptoms**:
```
ERROR: Failed to initialize PWM: PWM channel not exported
```

**Causes**:
1. Device tree overlay not loaded
2. Wrong pwmchip for Pi model
3. Kernel PWM subsystem disabled

**Solutions**:

1. Check device tree overlay:
   ```bash
   # Pi 1-4
   grep pwm /boot/config.txt

   # Pi 5
   grep pwm /boot/firmware/config.txt
   ```

2. Add overlay if missing:
   ```bash
   # Pi 1-4
   echo "dtoverlay=pwm,pin=18,func=2" | sudo tee -a /boot/config.txt

   # Pi 5
   echo "dtoverlay=pwm,pin=18,func=2" | sudo tee -a /boot/firmware/config.txt

   sudo reboot
   ```

3. Verify pwmchip exists:
   ```bash
   # Pi 1-4
   ls /sys/class/pwm/pwmchip0

   # Pi 5
   ls /sys/class/pwm/pwmchip2
   ```

4. Check kernel config:
   ```bash
   zcat /proc/config.gz | grep PWM
   # Should see: CONFIG_PWM=y, CONFIG_PWM_BCM2835=y
   ```

---

### GPIO pin does not support PWM (PWM_ERROR_INVALID_PIN)

**Symptoms**:
```
ERROR: GPIO 17 does not support PWM
Valid PWM pins: 12, 13, 18, 19
```

**Cause**:
Invalid GPIO pin specified.

**Solution**:
Use a valid PWM pin: 12, 13, 18, or 19

---

### PWM channel already in use (PWM_ERROR_BUSY)

**Symptoms**:
```
ERROR: Failed to initialize PWM: PWM channel already in use
```

**Causes**:
1. Another process using the same PWM channel
2. GPIO pin conflict (12/18 share PWM0, 13/19 share PWM1)
3. Channel already exported by another program

**Solutions**:

1. Check for other processes:
   ```bash
   sudo lsof | grep pwm
   ps aux | grep lgpio
   ```

2. Kill competing processes:
   ```bash
   sudo killall lgpio-pwm-fade
   ```

3. Unexport and re-export channel:
   ```bash
   # Pi 1-4
   echo 0 | sudo tee /sys/class/pwm/pwmchip0/unexport
   sudo ./scripts/setup-pwm-perms.sh

   # Pi 5
   echo 0 | sudo tee /sys/class/pwm/pwmchip2/unexport
   sudo ./scripts/setup-pwm-perms.sh
   ```

4. Use different PWM channel:
   - If using GPIO 18 (PWM0), try GPIO 13 (PWM1)
   - If using GPIO 12 (PWM0), try GPIO 19 (PWM1)

---

### LED not turning on/off

**Causes**:
1. LED polarity reversed
2. Resistor value too high
3. GPIO pin not configured
4. Hardware damage

**Solutions**:

1. Check LED polarity:
   - Long leg (anode) to GPIO pin through resistor
   - Short leg (cathode, flat side) to GND

2. Test with known working frequency:
   ```c
   pwm_init(18, 1000);
   pwm_write(18, 100.0);  // Full brightness
   ```

3. Test GPIO with non-PWM code:
   ```bash
   # Use lgpio-blink example to verify GPIO works
   cd examples/lgpio-blink
   pio run && sudo ./.pio/build/raspberrypi_4b/program
   ```

4. Check wiring with multimeter:
   - Measure voltage at GPIO pin (should be 3.3V when high)
   - Check continuity through resistor and LED

---

### LED flickering or unstable

**Causes**:
1. Frequency too low
2. Duty cycle at extreme values (0% or 100%)
3. Power supply noise
4. Software PWM interference

**Solutions**:

1. Increase frequency:
   ```c
   pwm_init(18, 5000);  // 5 kHz instead of 1 kHz
   ```

2. Avoid extreme duty cycles:
   ```c
   // Use 1% instead of 0%
   pwm_write(18, 1.0);

   // Use 99% instead of 100%
   pwm_write(18, 99.0);
   ```

3. Add capacitor across LED (optional):
   - 10-100 µF electrolytic capacitor
   - Positive terminal to GPIO pin
   - Negative terminal to GND

---

### Frequency limited or duty cycle clamped

**Symptoms**:
- Cannot set frequency above certain value
- Duty cycle limited to specific range

**Cause**:
Hardware limitations of PWM peripheral.

**Raspberry Pi PWM Limits**:
- Frequency: 1 Hz to ~100 MHz (practical: 1 Hz to 10 MHz)
- Duty cycle: 0.0% to 100.0%
- Resolution: Dependent on frequency (higher frequency = lower resolution)

**Solutions**:

1. Stay within practical limits:
   - LED control: 500 Hz - 10 kHz
   - Motor control: 1 kHz - 25 kHz
   - Servo control: 50 Hz
   - Audio: 20 Hz - 20 kHz

2. Check hardware datasheet:
   - BCM2835: 19.2 MHz base clock
   - BCM2711 (Pi 4): 54 MHz base clock
   - RP1 (Pi 5): TBD

---

### Manual Testing and Diagnostics

Check PWM status manually:

```bash
# Pi 1-4 examples (pwmchip0, channel 0)
PWM_BASE="/sys/class/pwm/pwmchip0/pwm0"

# Check if exported
ls $PWM_BASE

# Read period (nanoseconds)
cat $PWM_BASE/period

# Read duty cycle (nanoseconds)
cat $PWM_BASE/duty_cycle

# Read enable status
cat $PWM_BASE/enable

# Read polarity
cat $PWM_BASE/polarity

# Manually control PWM
echo 1000000 | sudo tee $PWM_BASE/period        # 1 kHz (1,000,000 ns period)
echo 500000 | sudo tee $PWM_BASE/duty_cycle     # 50% duty cycle
echo 1 | sudo tee $PWM_BASE/enable              # Enable output
```

**For Pi 5**, replace `pwmchip0` with `pwmchip2`.

## Advanced Topics

### Multi-Channel PWM

Use both PWM channels simultaneously:

```c
// Initialize both channels
pwm_init(18, 1000);  // PWM0 on GPIO 18
pwm_init(13, 1000);  // PWM1 on GPIO 13

// Control independently
pwm_write(18, 75.0);   // 75% on PWM0
pwm_write(13, 25.0);   // 25% on PWM1

// Cleanup both
pwm_deinit(18);
pwm_deinit(13);
```

**Note**: Cannot use GPIO 12 and 18 simultaneously (both use PWM0). Cannot use GPIO 13 and 19 simultaneously (both use PWM1).

---

### Servo Motor Control

Servos require 50 Hz PWM with 1-2 ms pulse width:

```c
#include "pwm-hal.h"

#define SERVO_PIN  18
#define SERVO_FREQ 50  // 50 Hz (20 ms period)

int main() {
    pwm_init(SERVO_PIN, SERVO_FREQ);

    // Servo positions (typical):
    // 0° = 5% duty cycle (1 ms pulse)
    // 90° = 7.5% duty cycle (1.5 ms pulse)
    // 180° = 10% duty cycle (2 ms pulse)

    pwm_write(SERVO_PIN, 5.0);    // 0 degrees
    sleep(1);

    pwm_write(SERVO_PIN, 7.5);    // 90 degrees
    sleep(1);

    pwm_write(SERVO_PIN, 10.0);   // 180 degrees
    sleep(1);

    pwm_deinit(SERVO_PIN);
    return 0;
}
```

See `examples/lgpio-pwm-servo/` for complete servo control example.

---

### LED Brightness Control

Human eye perceives brightness logarithmically. For smooth fading, use gamma correction:

```c
// Gamma correction table for LED brightness
// Maps linear 0-100 to perceived brightness
float gamma_correct(float linear) {
    return pow(linear / 100.0, 2.2) * 100.0;
}

// Fade LED with gamma correction
for (int i = 0; i <= 100; i++) {
    float corrected = gamma_correct(i);
    pwm_write(18, corrected);
    usleep(20000);  // 20 ms delay
}
```

---

### Motor Speed Control

Control DC motor speed with PWM:

```c
#include "pwm-hal.h"

#define MOTOR_PIN  18
#define MOTOR_FREQ 25000  // 25 kHz (inaudible, smooth)

void set_motor_speed(float speed) {
    // speed: 0.0 (stop) to 100.0 (full speed)
    pwm_write(MOTOR_PIN, speed);
}

int main() {
    pwm_init(MOTOR_PIN, MOTOR_FREQ);

    // Ramp up speed
    for (int speed = 0; speed <= 100; speed += 10) {
        set_motor_speed(speed);
        sleep(1);
    }

    // Emergency stop
    set_motor_speed(0);

    pwm_deinit(MOTOR_PIN);
    return 0;
}
```

**Note**: Requires motor driver circuit (H-bridge). Never connect motor directly to GPIO!

---

### PWM Frequency Selection

Choose frequency based on application:

| Application | Frequency | Notes |
|-------------|-----------|-------|
| LED (visible) | 500 Hz - 2 kHz | Flicker-free to human eye |
| LED (camera) | 5 kHz - 10 kHz | Prevents camera flicker |
| Servo motor | 50 Hz | Standard servo frequency |
| DC motor | 10 kHz - 25 kHz | Inaudible, smooth operation |
| Buzzer/tone | 20 Hz - 20 kHz | Audio range |
| Heating element | 1 Hz - 10 Hz | Thermal mass, slow response |

---

### PWM Duty Cycle Resolution

Higher frequencies reduce duty cycle resolution:

| Frequency | Period (ns) | Resolution (at 19.2 MHz clock) |
|-----------|-------------|--------------------------------|
| 100 Hz    | 10,000,000  | ~192 steps |
| 1 kHz     | 1,000,000   | ~19 steps |
| 10 kHz    | 100,000     | ~2 steps |
| 100 kHz   | 10,000      | < 1 step |

For fine control, use lower frequencies.

---

### Kernel PWM vs Software PWM

| Feature | Kernel PWM (this HAL) | Software PWM (lgpio) |
|---------|-----------------------|----------------------|
| Precision | Nanosecond | Microsecond |
| CPU usage | None (hardware) | High (busy-wait) |
| Jitter | None | Significant |
| Frequency | 1 Hz - 100 MHz | 1 Hz - 100 kHz |
| Pins | 2 or 4 (limited) | All GPIO (unlimited) |
| Setup | Device tree + permissions | None (immediate) |

Use hardware PWM (this HAL) when:
- Precise timing required (servo, motor)
- Low CPU usage desired
- High frequency needed

Use software PWM (lgpio) when:
- Need many PWM outputs
- Quick prototyping
- Imprecise timing acceptable

---

### Cross-Compilation

Build PWM examples for ARM on development machine:

```bash
# Install ARM toolchain (Ubuntu/Debian)
sudo apt install gcc-arm-linux-gnueabihf

# Build lgpio for ARM
./scripts/setup-lgpio-cross.sh

# Build example
cd examples/lgpio-pwm-fade
pio run -e raspberrypi_4b

# Deploy to Pi
scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:/home/pi/

# Run on Pi
ssh pi@raspberrypi.local
sudo ./program
```

See [LGPIO_SETUP.md](LGPIO_SETUP.md) for detailed cross-compilation instructions.

## References

### Documentation

- [Linux PWM Subsystem](https://www.kernel.org/doc/Documentation/pwm.txt) - Kernel PWM documentation
- [Raspberry Pi Device Tree Overlays](https://github.com/raspberrypi/firmware/blob/master/boot/overlays/README) - PWM overlay options
- [sysfs PWM Guide](https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html) - Practical PWM usage
- [lgpio Documentation](http://abyz.me.uk/lg/lgpio.html) - lgpio library reference

### Hardware

- [BCM2835 ARM Peripherals](https://www.raspberrypi.org/app/uploads/2012/02/BCM2835-ARM-Peripherals.pdf) - Pi 1-4 hardware (Chapter 9: PWM)
- [BCM2711 Datasheet](https://datasheets.raspberrypi.com/bcm2711/bcm2711-peripherals.pdf) - Pi 4 hardware
- [RP1 Datasheet](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf) - Pi 5 I/O controller

### Code Examples

- [lgpio-pwm-fade](../examples/lgpio-pwm-fade/) - LED fading example
- [lgpio-pwm-servo](../examples/lgpio-pwm-servo/) - Servo motor control (optional)
- [lgpio-blink](../examples/lgpio-blink/) - Basic GPIO example

### Related Documentation

- [LGPIO_SETUP.md](LGPIO_SETUP.md) - lgpio framework setup
- [FRAMEWORKS.md](FRAMEWORKS.md) - Framework comparison
- [UPLOAD.md](UPLOAD.md) - Remote deployment guide

## Support

### Getting Help

1. Check [Troubleshooting](#troubleshooting) section
2. Run diagnostics:
   ```bash
   sudo ./scripts/setup-pwm-perms.sh --verbose
   ```
3. Search existing issues: https://github.com/sfo2001/platform-linux_arm/issues
4. Create new issue with:
   - Raspberry Pi model
   - OS version (`cat /etc/os-release`)
   - Kernel version (`uname -a`)
   - Error messages (full output)
   - Output of diagnostic commands

### Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

### License

Copyright 2014-present PlatformIO <contact@platformio.org>

Licensed under the Apache License, Version 2.0. See [LICENSE](../LICENSE) file for details.
