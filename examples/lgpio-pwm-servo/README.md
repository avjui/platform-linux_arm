# PWM Servo Motor Control Example

Demonstrates precise servo motor position control using hardware PWM with the lgpio framework and PWM HAL.

## Features

- Hardware PWM at 50 Hz (standard servo frequency)
- Smooth servo movement with interpolation
- Precise angle control (0-180 degrees)
- Multiple demonstration modes
- Comprehensive safety warnings

## Hardware Setup

### Components Needed

- Raspberry Pi (any model with GPIO headers)
- Standard hobby servo motor (SG90, MG90S, or similar)
- **External 5V power supply** (1A minimum, 2A recommended)
- Breadboard and jumper wires

### CRITICAL SAFETY WARNING

**DO NOT power the servo from the Raspberry Pi's 5V pin!**

Servos draw 500mA to 2A of current during movement, which **WILL damage or destroy your Raspberry Pi**. Always use an external 5V power supply.

### Wiring Diagram

```
                   ┌─────────────────┐
                   │  Raspberry Pi   │
                   │                 │
                   │  GPIO 18 ───────┼──────── Servo Signal (orange/yellow/white)
                   │                 │
                   │  GND ────────────┼────┬── Pi Ground
                   └─────────────────┘    │
                                          │
                   ┌─────────────────┐    │
                   │ External 5V PSU │    │
                   │                 │    │
                   │  +5V ────────────┼────┼── Servo Power (red)
                   │  GND ────────────┼────┴── Servo Ground (brown/black) + PSU GND
                   └─────────────────┘
```

### Servo Wire Color Codes

Most servos use one of these color schemes:

| Signal | Standard | Futaba | JR/Spektrum |
|--------|----------|--------|-------------|
| Power  | Red      | Red    | Red         |
| Ground | Brown/Black | Black | Black    |
| Signal | Orange/Yellow | White | White/Orange |

### Connection Summary

1. **Servo Signal Wire** (orange/yellow/white) → Raspberry Pi GPIO 18
2. **Servo Power Wire** (red) → External 5V power supply (+)
3. **Servo Ground Wire** (brown/black) → Common ground with Pi and power supply
4. **Pi GND** → Power supply GND (creates common ground reference)

### Power Supply Requirements

- **Voltage**: 5V DC (4.8V - 6V acceptable)
- **Current**:
  - Small servos (SG90): 500mA - 1A
  - Standard servos (MG90S): 1A - 1.5A
  - Large servos: 2A+
- **Recommended**: Use 5V 2A power supply for safety margin

### Supported GPIO Pins

| GPIO | PWM Channel | Notes |
|------|-------------|-------|
| 18   | PWM0        | **Recommended** (default) |
| 19   | PWM1        | Alternative |
| 12   | PWM0        | Conflicts with GPIO 18 |
| 13   | PWM1        | Conflicts with GPIO 19 |

## Software Setup

### 1. Enable PWM Device Tree Overlay

Edit boot configuration:

**Pi 1-4**:
```bash
sudo nano /boot/config.txt
```

**Pi 5**:
```bash
sudo nano /boot/firmware/config.txt
```

Add:
```
dtoverlay=pwm,pin=18,func=2
```

Reboot:
```bash
sudo reboot
```

### 2. Setup PWM Permissions

```bash
cd /path/to/platform-linux_arm
sudo ./scripts/setup-pwm-perms.sh
```

### 3. Add User to GPIO Group

```bash
sudo usermod -a -G gpio $USER
# Log out and back in for changes to take effect
```

## Building and Running

### Cross-Compilation

```bash
# Build for Pi 4
pio run -e raspberrypi_4b

# Copy to Pi
scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:/home/pi/lgpio-pwm-servo

# Run on Pi
ssh pi@raspberrypi.local
sudo ./lgpio-pwm-servo
```

### Native Build

```bash
pio run
sudo ./.pio/build/raspberrypi_4b/program
```

### Upload to Remote Pi

```bash
ssh-copy-id pi@raspberrypi.local
pio run -e raspberrypi_4b_upload -t upload
```

## Usage

### Basic Usage

Run with default settings (GPIO 18):
```bash
sudo ./lgpio-pwm-servo
```

### Custom GPIO Pin

Use GPIO 13 instead:
```bash
sudo ./lgpio-pwm-servo 13
```

## Expected Output

```
PWM Servo Motor Control Example
================================
GPIO Pin: 18
Frequency: 50 Hz (standard servo frequency)
Pulse Width Range: 1.0 - 2.0 ms
Angle Range: 0° - 180°
Press Ctrl+C to exit

Initializing PWM on GPIO 18 at 50 Hz...
PWM initialized successfully!

PWM Status:
  Chip: 0, Channel: 0
  Frequency: 50 Hz
  Period: 20000000 ns (20.0 ms)

Centering servo (90°)...

Starting servo demonstration...

Demo 1: Basic positions (0°, 90°, 180°)
----------------------------------------
Moving to 0° (full left)...
Moving to 90° (center)...
Moving to 180° (full right)...
Moving back to 90° (center)...

Demo 2: Smooth sweep (0° to 180° and back)
-------------------------------------------
Sweeping from 0° to 180°...
Sweeping from 180° to 0°...

Demo 3: Precise angles
----------------------
Setting position to 0°...
Setting position to 30°...
Setting position to 60°...
Setting position to 90°...
Setting position to 120°...
Setting position to 150°...
Setting position to 180°...

Demo 4: Continuous sweep (Ctrl+C to stop)
-----------------------------------------
Sweep cycle 1: 0° -> 180° -> 0°
Sweep cycle 2: 0° -> 180° -> 0°
...
```

The servo should move through various positions smoothly.

## Demonstration Modes

The example runs four demonstration modes:

1. **Basic Positions**: Tests three key positions (0°, 90°, 180°)
2. **Smooth Sweep**: Continuous smooth movement between extremes
3. **Precise Angles**: Steps through specific angles (0°, 30°, 60°, etc.)
4. **Continuous Sweep**: Repeats smooth sweep indefinitely (press Ctrl+C to stop)

## Servo Specifications

### Standard Hobby Servo

- **Frequency**: 50 Hz (20 ms period)
- **Pulse Width Range**:
  - 1.0 ms = 0° (full left)
  - 1.5 ms = 90° (center)
  - 2.0 ms = 180° (full right)
- **Rotation**: 180° (most common)
- **Voltage**: 4.8V - 6V
- **Current**: 100mA idle, 500mA - 2A under load

### Common Servo Models

| Model | Torque | Speed | Current | Notes |
|-------|--------|-------|---------|-------|
| SG90 | 1.8 kg·cm | 0.1 s/60° | 500mA | Micro, plastic gears |
| MG90S | 2.2 kg·cm | 0.08 s/60° | 1A | Micro, metal gears |
| MG996R | 11 kg·cm | 0.17 s/60° | 2A | Standard, metal gears |
| DS3218 | 20 kg·cm | 0.16 s/60° | 2A | Digital, high torque |

## Calibration

Different servo models may have slightly different pulse width ranges. If your servo doesn't reach full range or jitters at extremes, adjust these values in the code:

```c
// Default values
#define SERVO_MIN_PULSE_MS   1.0    // 1 ms = 0 degrees
#define SERVO_MAX_PULSE_MS   2.0    // 2 ms = 180 degrees

// Some servos may need:
#define SERVO_MIN_PULSE_MS   0.5    // Extended range
#define SERVO_MAX_PULSE_MS   2.5    // Extended range

// Or:
#define SERVO_MIN_PULSE_MS   1.1    // Narrower range
#define SERVO_MAX_PULSE_MS   1.9    // Narrower range
```

Test by running the example and observing:
- Does servo reach full 0° position without jittering?
- Does servo reach full 180° position without jittering?
- Adjust MIN and MAX values as needed

## Troubleshooting

### Servo Jittering or Vibrating

**Causes**:
1. Insufficient power supply current
2. Poor power supply regulation
3. Pulse width outside servo's range
4. Loose connections

**Solutions**:
1. Use larger power supply (2A minimum)
2. Add 100-1000 µF capacitor across power supply
3. Calibrate pulse width range (see [Calibration](#calibration))
4. Check all connections are secure

---

### Servo Not Moving

**Causes**:
1. No power to servo
2. Signal wire disconnected
3. Servo damaged
4. PWM not working

**Solutions**:
1. Check power supply voltage (should be 5V)
2. Verify signal wire connected to GPIO 18
3. Test servo with different power source
4. Run lgpio-pwm-fade example to verify PWM works

---

### Servo Moving to Wrong Positions

**Causes**:
1. Pulse width calibration incorrect
2. Servo has different specs (270° range, etc.)
3. Servo type mismatch (analog vs digital)

**Solutions**:
1. Adjust MIN/MAX pulse width values
2. Consult servo datasheet for specifications
3. Test with known working values (1.0 - 2.0 ms)

---

### Servo Moving Erratically

**Causes**:
1. Power supply noise
2. Ground loop issues
3. Voltage drop during movement
4. Signal interference

**Solutions**:
1. Add decoupling capacitor (100-1000 µF) near servo power pins
2. Ensure common ground between Pi and power supply
3. Use thicker gauge wire for power (20-22 AWG)
4. Keep signal wire away from power wires
5. Use shielded cable for long runs

---

### Raspberry Pi Rebooting

**Cause**: Servo powered from Pi's 5V pin (TOO MUCH CURRENT)

**Solution**:
- **NEVER power servo from Pi!**
- Use external 5V power supply
- Only connect signal wire to Pi GPIO

---

### Permission Denied Error

See [PWM_SETUP.md](../../docs/PWM_SETUP.md) for detailed troubleshooting.

Quick fix:
```bash
sudo ./scripts/setup-pwm-perms.sh
sudo usermod -a -G gpio $USER
# Log out and back in
```

## Advanced Usage

### Multiple Servos

Control two servos independently using both PWM channels:

```c
// Initialize both servos
pwm_init(18, 50);  // Servo 1 on PWM0 (GPIO 18)
pwm_init(13, 50);  // Servo 2 on PWM1 (GPIO 13)

// Control independently
servo_set_position(18, 45.0);   // Servo 1 to 45°
servo_set_position(13, 135.0);  // Servo 2 to 135°

// Cleanup
pwm_deinit(18);
pwm_deinit(13);
```

**Note**: Pi has only 2 hardware PWM channels. For more servos, use software PWM or PWM expansion board.

---

### Continuous Rotation Servo

Some servos are modified for continuous rotation (360°):
- 1.5 ms (center) = stopped
- 1.0 ms = full speed one direction
- 2.0 ms = full speed other direction

```c
// Stop
pwm_write(18, PULSE_TO_DUTY(1.5));

// Rotate clockwise
pwm_write(18, PULSE_TO_DUTY(2.0));

// Rotate counter-clockwise
pwm_write(18, PULSE_TO_DUTY(1.0));
```

---

### Custom Movement Profiles

Create custom movement patterns:

```c
// Sinusoidal wave pattern
for (int t = 0; t < 360; t++) {
    float angle = 90.0 + 90.0 * sin(t * M_PI / 180.0);
    servo_set_position(18, angle);
    usleep(10000);  // 10 ms delay
}

// Triangular wave pattern
for (int angle = 0; angle <= 180; angle += 5) {
    servo_set_position(18, angle);
    usleep(50000);
}
for (int angle = 180; angle >= 0; angle -= 5) {
    servo_set_position(18, angle);
    usleep(50000);
}
```

---

### Integration with Sensors

Combine servo control with sensor input:

```c
// Example: Pan servo based on sensor reading
float sensor_value = read_sensor();  // 0.0 to 1.0
float angle = sensor_value * 180.0;  // Map to 0-180°
servo_set_position(18, angle);
```

## Technical Details

### PWM Timing

- **Frequency**: 50 Hz (period = 20 ms = 20,000,000 ns)
- **Pulse Width**: 1.0 - 2.0 ms (1,000,000 - 2,000,000 ns)
- **Duty Cycle**: 5% - 10%
- **Resolution**: ~0.1° (depends on servo quality)

### Angle to Pulse Width Calculation

```
pulse_ms = MIN_PULSE + (angle / 180°) × (MAX_PULSE - MIN_PULSE)
duty_cycle% = (pulse_ms / 20 ms) × 100%
```

Example:
- 0° → 1.0 ms → 5% duty cycle
- 90° → 1.5 ms → 7.5% duty cycle
- 180° → 2.0 ms → 10% duty cycle

### Servo Response Time

Typical servo response:
- SG90: 0.1 s/60° (0.3° per ms)
- MG90S: 0.08 s/60° (0.4° per ms)

For 180° movement:
- SG90: ~300 ms
- MG90S: ~240 ms

## Safety Guidelines

1. **Never power servo from Pi's 5V pin** - Use external supply
2. **Always connect grounds** - Pi GND ↔ Power supply GND
3. **Check polarity** - Red to +5V, Brown/Black to GND
4. **Don't overload servo** - Respect torque and speed limits
5. **Don't stall servo** - Prolonged stalling damages motor
6. **Use proper gauge wire** - 20-22 AWG for power, any for signal
7. **Add capacitor** - 100-1000 µF across power supply reduces noise

## References

### Documentation

- [PWM Setup Guide](../../docs/PWM_SETUP.md) - Complete PWM configuration
- [PWM HAL API Reference](../../docs/PWM_SETUP.md#api-reference)
- [lgpio Documentation](http://abyz.me.uk/lg/lgpio.html)

### Hardware

- [Servo Motor Basics](https://learn.sparkfun.com/tutorials/hobby-servo-tutorial) - Sparkfun guide
- [PWM for Servos](https://www.pololu.com/docs/0J40) - Technical details

### Code Examples

- [lgpio-pwm-fade](../lgpio-pwm-fade/) - LED fading with PWM
- [lgpio-blink](../lgpio-blink/) - Basic GPIO control
- [lgpio-spi-adc](../lgpio-spi-adc/) - SPI communication

## See Also

- Pan-Tilt servo bracket control (combine 2 servos)
- Robot arm control (combine 4-6 servos)
- Camera gimbal stabilization

## License

Copyright 2014-present PlatformIO <contact@platformio.org>

Licensed under the Apache License, Version 2.0. See LICENSE file for details.
