# PWM LED Fade Example

Demonstrates hardware PWM control using the lgpio framework with PWM HAL for smooth LED fading effects.

## Features

- Hardware PWM using Linux kernel PWM subsystem
- Smooth LED brightness control (0-100%)
- CPU-efficient (no busy-waiting)
- Works on all Raspberry Pi models (1-5)
- Comprehensive error handling and diagnostics

## Hardware Setup

### Components Needed

- Raspberry Pi (any model with GPIO headers)
- LED (any color)
- 220Ω resistor (or appropriate value for your LED)
- Breadboard and jumper wires

### Wiring Diagram

```
Raspberry Pi GPIO 18 ----[220Ω]----[LED Anode (+, long leg)]
                                    [LED Cathode (-, short leg)]---- GND
```

**Important**:
- LED cathode (short leg, flat side) connects to GND
- LED anode (long leg) connects through resistor to GPIO 18
- Resistor can be on either side of the LED

### Supported PWM GPIO Pins

| GPIO | PWM Channel | Notes |
|------|-------------|-------|
| 12   | PWM0        | Default pin for PWM0 |
| 13   | PWM1        | Default pin for PWM1 |
| 18   | PWM0        | **Recommended** (conflicts with GPIO 12) |
| 19   | PWM1        | Alternative (conflicts with GPIO 13) |

**Note**: GPIO 12 and 18 share PWM0 channel. GPIO 13 and 19 share PWM1 channel. You cannot use both pins on the same channel simultaneously.

## Software Setup

### 1. Enable PWM Device Tree Overlay

Edit the boot configuration file:

**For Pi 1-4**:
```bash
sudo nano /boot/config.txt
```

**For Pi 5**:
```bash
sudo nano /boot/firmware/config.txt
```

Add the following line:
```
dtoverlay=pwm,pin=18,func=2
```

For dual-channel PWM (both PWM0 and PWM1):
```
dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2
```

Save and reboot:
```bash
sudo reboot
```

### 2. Setup PWM Permissions

Run the permissions setup script:
```bash
cd /path/to/platform-linux_arm
sudo ./scripts/setup-pwm-perms.sh
```

This script:
- Exports PWM channels to userspace
- Sets correct group ownership (gpio)
- Applies read/write permissions

### 3. Install systemd Service (Optional)

To automatically setup PWM permissions on boot:
```bash
sudo cp scripts/platformio-pwm.service /etc/systemd/system/
sudo systemctl enable platformio-pwm.service
sudo systemctl start platformio-pwm.service
```

## Building and Running

### Cross-Compilation (Development Machine)

```bash
# Build for Raspberry Pi 4
pio run -e raspberrypi_4b

# Build for Raspberry Pi 5 (64-bit)
pio run -e raspberrypi_5_64bit

# Copy binary to Pi
scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:/home/pi/lgpio-pwm-fade

# SSH and run on Pi
ssh pi@raspberrypi.local
sudo ./lgpio-pwm-fade
```

### Native Build (On Raspberry Pi)

```bash
pio run

# Run with sudo (required for PWM access)
sudo ./.pio/build/raspberrypi_4b/program
```

### Upload to Remote Pi

```bash
# Setup SSH key authentication first
ssh-copy-id pi@raspberrypi.local

# Build and upload
pio run -e raspberrypi_4b_upload -t upload
```

## Usage

### Basic Usage

Run with default settings (GPIO 18, 1000 Hz):
```bash
sudo ./lgpio-pwm-fade
```

### Custom GPIO Pin

Use GPIO 13 (PWM1) instead:
```bash
sudo ./lgpio-pwm-fade 13
```

### Custom Frequency

Set frequency to 5000 Hz:
```bash
sudo ./lgpio-pwm-fade 18 5000
```

## Expected Output

```
PWM LED Fade Example (lgpio framework with PWM HAL)
====================================================
GPIO Pin: 18
Frequency: 1000 Hz
Fade Steps: 100
Fade Delay: 20 ms
Press Ctrl+C to exit

Initializing PWM on GPIO 18 at 1000 Hz...
PWM initialized successfully!
Starting fade effect (Ctrl+C to stop)...

PWM Status:
  Chip: 0, Channel: 0
  Enabled: yes
  Frequency: 1000 Hz
  Period: 1000000 ns

Fade cycle 1: UP -> DOWN
Fade cycle 2: UP -> DOWN
...
```

The LED should smoothly fade in and out continuously.

## Troubleshooting

### Error: Permission denied

**Cause**: PWM permissions not setup correctly or user not in gpio group

**Solution**:
```bash
# Run setup script
sudo ./scripts/setup-pwm-perms.sh

# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and back in for group changes to take effect
```

### Error: PWM channel not exported

**Cause**: PWM device tree overlay not loaded

**Solution**:
1. Check overlay is in config.txt:
   ```bash
   # For Pi 1-4
   grep pwm /boot/config.txt

   # For Pi 5
   grep pwm /boot/firmware/config.txt
   ```

2. If missing, add:
   ```
   dtoverlay=pwm,pin=18,func=2
   ```

3. Reboot:
   ```bash
   sudo reboot
   ```

4. Verify pwmchip exists:
   ```bash
   # Pi 1-4
   ls /sys/class/pwm/pwmchip0

   # Pi 5
   ls /sys/class/pwm/pwmchip2
   ```

### Error: GPIO pin does not support PWM

**Cause**: Invalid GPIO pin specified

**Solution**: Use one of the supported PWM pins: 12, 13, 18, or 19

### Error: PWM channel already in use

**Cause**:
- Another process is using the same PWM channel
- GPIO 12/18 (PWM0) or GPIO 13/19 (PWM1) conflict

**Solution**:
1. Check for other processes:
   ```bash
   sudo lsof | grep pwm
   ```

2. Use a different PWM channel (e.g., GPIO 13 instead of GPIO 18)

### LED Not Fading Smoothly

**Possible causes**:
1. **Wrong LED polarity**: Flip LED around
2. **Frequency too low**: Try higher frequency (e.g., 5000 Hz)
3. **Resistor value too high**: Use lower value resistor
4. **PWM signal noise**: Add capacitor across LED (optional)

### Check PWM Status Manually

```bash
# Check if PWM is exported
ls /sys/class/pwm/pwmchip0/pwm0

# Read current settings
cat /sys/class/pwm/pwmchip0/pwm0/period
cat /sys/class/pwm/pwmchip0/pwm0/duty_cycle
cat /sys/class/pwm/pwmchip0/pwm0/enable
```

## Technical Details

### PWM Parameters

- **Frequency**: 1000 Hz (1 kHz)
  - Period: 1,000,000 ns (1 ms)
  - Good for LED control (flicker-free)

- **Fade Steps**: 100 steps
  - Duty cycle range: 0% to 100% in 1% increments

- **Fade Delay**: 20 ms per step
  - Total fade time: 2 seconds (up) + 2 seconds (down) = 4 seconds/cycle

### PWM HAL Features Used

- `pwm_init()` - Initialize hardware PWM
- `pwm_write()` - Set duty cycle (brightness)
- `pwm_get_status()` - Query PWM configuration
- `pwm_deinit()` - Cleanup and release resources
- `pwm_pin_is_valid()` - Validate GPIO pin
- `pwm_error_string()` - Human-readable error messages

## Advanced Usage

### Experiment with Different Effects

Modify fade parameters in the code:
- Change `FADE_STEPS` for smoother/faster fading
- Adjust `FADE_DELAY_MS` for fade speed
- Modify `PWM_FREQUENCY` for different effects

### Multiple LEDs

Use both PWM channels simultaneously:
```bash
# Terminal 1: GPIO 18 (PWM0)
sudo ./lgpio-pwm-fade 18

# Terminal 2: GPIO 13 (PWM1)
sudo ./lgpio-pwm-fade 13
```

### Integration with Other Projects

Include PWM HAL in your projects:
```c
#include "pwm-hal.h"

int main() {
    pwm_init(18, 1000);
    pwm_write(18, 75.0);  // 75% brightness
    // ... your code ...
    pwm_deinit(18);
    return 0;
}
```

## References

- [PWM Setup Guide](../../docs/PWM_SETUP.md) - Complete PWM configuration
- [Linux PWM Subsystem](https://www.kernel.org/doc/Documentation/pwm.txt)
- [Raspberry Pi PWM Hardware](https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html)
- [lgpio Documentation](http://abyz.me.uk/lg/lgpio.html)

## See Also

- [lgpio-blink](../lgpio-blink/) - Basic GPIO example
- [lgpio-spi-adc](../lgpio-spi-adc/) - SPI communication example
- [lgpio-pwm-servo](../lgpio-pwm-servo/) - Servo motor control example (optional)

## License

Copyright 2014-present PlatformIO <contact@platformio.org>

Licensed under the Apache License, Version 2.0. See LICENSE file for details.
