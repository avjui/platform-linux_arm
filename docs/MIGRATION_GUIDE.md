# GPIO Framework Migration Guide

This guide helps you migrate between different GPIO frameworks on Raspberry Pi and ARM SBCs.

## Table of Contents

- [WiringPi → libgpiod](#wiringpi--libgpiod)
- [WiringPi → lgpio](#wiringpi--lgpio)
- [pigpio → lgpio](#pigpio--lgpio)
- [pigpio → libgpiod](#pigpio--libgpiod)
- [lgpio → libgpiod](#lgpio--libgpiod)
- [RPi.GPIO → libgpiod](#rpigpio--libgpiod)
- [State Persistence Comparison](#state-persistence-comparison)
- [Common Pitfalls](#common-pitfalls)

---

## WiringPi → libgpiod

**Why migrate**: WiringPi is deprecated (discontinued 2019), no official cross-compilation support, incomplete Pi 5 support.

**Target**: libgpiod is the official Linux kernel GPIO library, works on all SBCs.

### API Comparison

#### Basic GPIO Output

**WiringPi:**
```c
#include <wiringPi.h>

wiringPiSetupGpio();  // Use BCM numbering
pinMode(23, OUTPUT);
digitalWrite(23, HIGH);
digitalWrite(23, LOW);
```

**libgpiod v1:**
```c
#include <gpiod.h>

struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");
struct gpiod_line *line = gpiod_chip_get_line(chip, 23);
gpiod_line_request_output(line, "my-app", 0);

gpiod_line_set_value(line, 1);
gpiod_line_set_value(line, 0);

gpiod_line_release(line);
gpiod_chip_close(chip);
```

**libgpiod v2:**
```c
#include <gpiod.h>

struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");
struct gpiod_request_config *req_cfg = gpiod_request_config_new();
gpiod_request_config_set_consumer(req_cfg, "my-app");

struct gpiod_line_config *line_cfg = gpiod_line_config_new();
gpiod_line_config_set_direction_default(line_cfg, GPIOD_LINE_DIRECTION_OUTPUT);

struct gpiod_line_request *request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

gpiod_line_request_set_value(request, 23, 1);
gpiod_line_request_set_value(request, 23, 0);

gpiod_line_request_release(request);
gpiod_line_config_free(line_cfg);
gpiod_request_config_free(req_cfg);
gpiod_chip_close(chip);
```

#### GPIO Input with Pull-up

**WiringPi:**
```c
wiringPiSetupGpio();
pinMode(24, INPUT);
pullUpDnControl(24, PUD_UP);
int value = digitalRead(24);
```

**libgpiod v1:**
```c
struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");
struct gpiod_line *line = gpiod_chip_get_line(chip, 24);
gpiod_line_request_input_flags(line, "my-app", GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP);

int value = gpiod_line_get_value(line);
```

#### Pin Numbering

Both WiringPi (BCM mode) and libgpiod use **BCM GPIO numbers**:
- Physical pin 16 = GPIO 23
- Physical pin 18 = GPIO 24

### Key Differences

| Aspect | WiringPi | libgpiod |
|--------|----------|----------|
| **Pin Numbering** | WiringPi/BCM/Physical | BCM only (simpler) |
| **Initialization** | `wiringPiSetupGpio()` | Open chip explicitly |
| **State Persistence** | Maintains state | Requires `dtparam=strict_gpiod` on RPi |
| **Cross-compilation** | No | Yes |
| **Multi-SBC Support** | No - RPi only | Yes - All Linux SBCs |

### Migration Checklist

- [ ] Replace `wiringPiSetupGpio()` with `gpiod_chip_open_by_name("gpiochip0")`
- [ ] Replace `pinMode()` with `gpiod_line_request_*()`
- [ ] Replace `digitalWrite()` with `gpiod_line_set_value()`
- [ ] Replace `digitalRead()` with `gpiod_line_get_value()`
- [ ] Add cleanup code (`gpiod_line_release()`, `gpiod_chip_close()`)
- [ ] Enable `dtparam=strict_gpiod` in `/boot/config.txt` if you need state persistence
- [ ] Update `platformio.ini`: `framework = libgpiod`

---

## WiringPi → lgpio

**Why migrate**: WiringPi is deprecated, lgpio is actively maintained for Raspberry Pi.

**Target**: lgpio works on all Raspberry Pi models (1-5) with multi-protocol support.

### API Comparison

#### Basic GPIO Output

**WiringPi:**
```c
#include <wiringPi.h>

wiringPiSetupGpio();
pinMode(23, OUTPUT);
digitalWrite(23, HIGH);
```

**lgpio:**
```c
#include <lgpio.h>

int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);
lgGpioWrite(h, 23, 1);

lgGpiochipClose(h);
```

### Key Differences

| Aspect | WiringPi | lgpio |
|--------|----------|-------|
| **Pin Numbering** | WiringPi/BCM/Physical | BCM only |
| **State Persistence** | Yes - Maintains | Yes - Maintains |
| **Multi-Protocol** | GPIO/I2C/SPI/PWM | GPIO/I2C/SPI/PWM/UART |
| **Pi 5 Support** | Partial - Partial (GCLK broken) | Yes - Full |

### Migration Checklist

- [ ] Replace `wiringPiSetupGpio()` with `lgGpiochipOpen(0)`
- [ ] Replace `pinMode()` with `lgGpioClaimOutput()` or `lgGpioClaimInput()`
- [ ] Replace `digitalWrite()` with `lgGpioWrite()`
- [ ] Replace `digitalRead()` with `lgGpioRead()`
- [ ] Add cleanup code (`lgGpiochipClose()`)
- [ ] Update `platformio.ini`: `framework = lgpio`

---

## pigpio → lgpio

**Why migrate**: pigpio doesn't work on Raspberry Pi 5. lgpio is the successor by the same author (Joan).

**Target**: lgpio works on all Raspberry Pi models (1-5).

### API Comparison

#### Basic GPIO

**pigpio:**
```c
#include <pigpio.h>

gpioInitialise();
gpioSetMode(23, PI_OUTPUT);
gpioWrite(23, 1);
gpioWrite(23, 0);
int value = gpioRead(24);
gpioTerminate();
```

**lgpio:**
```c
#include <lgpio.h>

int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);
lgGpioWrite(h, 23, 1);
lgGpioWrite(h, 23, 0);

lgGpioClaimInput(h, 0, 24);
int value = lgGpioRead(h, 24);

lgGpiochipClose(h);
```

#### PWM

**pigpio (hardware PWM):**
```c
gpioHardwarePWM(18, 1000, 500000);  // 1kHz, 50% duty
```

**lgpio (software PWM):**
```c
// lgpio requires manual PWM implementation or use kernel PWM subsystem
// For software PWM, use lgGpioWrite in a timed loop
// For hardware PWM, use /sys/class/pwm/ interface
```

Partial - **Important**: pigpio's hardware-timed PWM via DMA is a unique feature. lgpio uses software PWM or kernel PWM subsystem. If you need precise hardware PWM, consider staying on pigpio (Pi 1-4 only) or migrate to kernel PWM.

### Key Differences

| Aspect | pigpio | lgpio |
|--------|--------|-------|
| **Pi 5 Support** | No | Yes |
| **Daemon** | Required (pigpiod) | Not required |
| **PWM** | Hardware-timed (DMA) | Software or kernel PWM |
| **Timing Precision** | Microsecond (DMA) | Standard |
| **State Persistence** | Yes - Maintains | Yes - Maintains |

### Migration Checklist

- [ ] Replace `gpioInitialise()` with `lgGpiochipOpen(0)`
- [ ] Replace `gpioSetMode()` with `lgGpioClaimOutput()` or `lgGpioClaimInput()`
- [ ] Replace `gpioWrite()` with `lgGpioWrite()`
- [ ] Replace `gpioRead()` with `lgGpioRead()`
- [ ] Replace `gpioTerminate()` with `lgGpiochipClose()`
- [ ] Reimplement PWM using software PWM or `/sys/class/pwm/`
- [ ] Remove pigpiod daemon dependency
- [ ] Update `platformio.ini`: `framework = lgpio`

---

## pigpio → libgpiod

**Why migrate**: pigpio doesn't work on Raspberry Pi 5, need multi-SBC support.

**Target**: libgpiod is the official Linux kernel standard, works on all SBCs.

### API Comparison

**pigpio:**
```c
#include <pigpio.h>

gpioInitialise();
gpioSetMode(23, PI_OUTPUT);
gpioWrite(23, 1);
gpioTerminate();
```

**libgpiod v1:**
```c
#include <gpiod.h>

struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");
struct gpiod_line *line = gpiod_chip_get_line(chip, 23);
gpiod_line_request_output(line, "my-app", 0);
gpiod_line_set_value(line, 1);

gpiod_line_release(line);
gpiod_chip_close(chip);
```

### Key Differences

| Aspect | pigpio | libgpiod |
|--------|--------|----------|
| **Pi 5 Support** | No | Yes |
| **Multi-SBC** | No - RPi only | Yes - All Linux SBCs |
| **Daemon** | Required | Not required |
| **PWM** | Hardware DMA | Use separate libraries |
| **State Persistence** | Yes - Maintains | Requires `dtparam=strict_gpiod` |

### Migration Checklist

- [ ] Replace `gpioInitialise()` with `gpiod_chip_open_by_name("gpiochip0")`
- [ ] Replace `gpioSetMode()` with `gpiod_line_request_*()`
- [ ] Replace `gpioWrite()` with `gpiod_line_set_value()`
- [ ] Replace `gpioRead()` with `gpiod_line_get_value()`
- [ ] Replace `gpioTerminate()` with cleanup code
- [ ] Reimplement PWM using `/sys/class/pwm/` or separate library
- [ ] Enable `dtparam=strict_gpiod` if needed
- [ ] Update `platformio.ini`: `framework = libgpiod`

---

## lgpio → libgpiod

**Why migrate**: Need multi-SBC support, want official kernel standard.

**Target**: libgpiod works across all Linux ARM SBCs.

### API Comparison

**lgpio:**
```c
#include <lgpio.h>

int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);
lgGpioWrite(h, 23, 1);
lgGpiochipClose(h);
```

**libgpiod v1:**
```c
#include <gpiod.h>

struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");
struct gpiod_line *line = gpiod_chip_get_line(chip, 23);
gpiod_line_request_output(line, "my-app", 0);
gpiod_line_set_value(line, 1);

gpiod_line_release(line);
gpiod_chip_close(chip);
```

### Key Differences

| Aspect | lgpio | libgpiod |
|--------|-------|----------|
| **Multi-SBC** | Partial - RPi-focused | Yes - All Linux SBCs |
| **Multi-Protocol** | Yes - GPIO/I2C/SPI/PWM/UART | No - GPIO only |
| **Exclusivity** | Not guaranteed | Yes - Kernel-enforced |
| **State Persistence** | Yes - Maintains | Requires `dtparam=strict_gpiod` |
| **Threading** | May spawn threads | Direct ioctl calls |

### Migration Checklist

- [ ] Replace `lgGpiochipOpen(0)` with `gpiod_chip_open_by_name("gpiochip0")`
- [ ] Replace `lgGpioClaimOutput()` with `gpiod_line_request_output()`
- [ ] Replace `lgGpioWrite()` with `gpiod_line_set_value()`
- [ ] Replace `lgGpioRead()` with `gpiod_line_get_value()`
- [ ] Replace `lgGpiochipClose()` with cleanup code
- [ ] Migrate I2C/SPI/PWM to separate libraries if needed
- [ ] Enable `dtparam=strict_gpiod` if needed
- [ ] Update `platformio.ini`: `framework = libgpiod`

---

## RPi.GPIO → libgpiod

**Why migrate**: RPi.GPIO doesn't work on Raspberry Pi 5, Python-only.

**Target**: libgpiod is the official Linux kernel standard with C/Python bindings.

### API Comparison (Python)

**RPi.GPIO:**
```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.HIGH)
GPIO.cleanup()
```

**Python libgpiod (gpiod):**
```python
import gpiod

chip = gpiod.Chip('gpiochip0')
line = chip.get_line(23)
line.request(consumer='my-app', type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
line.set_value(1)
line.release()
```

### Migration Notes (Python)

- Install: `sudo apt install python3-libgpiod` (v1) or `pip install gpiod` (v2)
- RPi.GPIO uses BCM or BOARD numbering; libgpiod uses BCM (line offset)
- libgpiod requires explicit line request before use
- State persistence: Enable `dtparam=strict_gpiod` on Raspberry Pi

---

## State Persistence Comparison

### What is State Persistence?

State persistence refers to whether GPIO pin states (HIGH/LOW, INPUT/OUTPUT) are maintained after your program exits.

### Behavior by Framework

| Framework | State Persistence | Configuration Needed |
|-----------|-------------------|----------------------|
| **libgpiod** | Partial - No (by default) | Raspberry Pi: Add `dtparam=strict_gpiod` to `/boot/config.txt` |
| **lgpio** | Yes | None |
| **pigpio** | Yes | None |
| **WiringPi** | Yes | None |
| **RPi.GPIO** | Yes | None |

### Enabling State Persistence for libgpiod

#### Raspberry Pi

Edit `/boot/firmware/config.txt` (or `/boot/config.txt` on older systems):

```bash
sudo nano /boot/firmware/config.txt
```

Add this line:

```
dtparam=strict_gpiod
```

Reboot:

```bash
sudo reboot
```

#### Other SBCs

Check your SBC's documentation for equivalent device tree parameters.

### When State Persistence Matters

**Scenarios where you NEED state persistence:**
- LED indicators that should stay on after program exits
- Relay control (keep relay active between program restarts)
- System status LEDs
- Persistent GPIO configuration

**Scenarios where you DON'T need state persistence:**
- Temporary GPIO operations during program execution
- GPIO reset to default state is desired on exit
- Security: want GPIOs to revert to safe state

### Example: State Persistence Impact

Without `strict_gpiod`:
```bash
# Program sets GPIO 23 HIGH and exits
./my_program  # Sets GPIO 23 HIGH
# After exit: GPIO 23 reverts to INPUT (usually LOW)
```

With `strict_gpiod`:
```bash
# Program sets GPIO 23 HIGH and exits
./my_program  # Sets GPIO 23 HIGH
# After exit: GPIO 23 remains HIGH
```

---

## Common Pitfalls

### 1. Forgetting to Enable `strict_gpiod` for libgpiod

**Problem**: GPIO reverts to default state after program exits.

**Solution**: Add `dtparam=strict_gpiod` to `/boot/config.txt` and reboot.

### 2. Wrong Pin Numbering

**Problem**: Using wrong GPIO numbers (physical pin vs BCM vs WiringPi).

**Solution**: libgpiod and lgpio use **BCM GPIO numbers**. Use `gpioinfo` to verify:

```bash
gpioinfo
```

### 3. Not Closing Resources

**Problem**: GPIO lines remain claimed, preventing other programs from accessing them.

**Solution**: Always call cleanup functions:
- libgpiod: `gpiod_line_release()`, `gpiod_chip_close()`
- lgpio: `lgGpiochipClose()`

### 4. Missing Cross-Compilation Dependencies

**Problem**: Build fails with "libgpiod not found" during cross-compilation.

**Solution**: Install architecture-specific packages:

```bash
sudo dpkg --add-architecture armhf
sudo apt update
sudo apt install libgpiod-dev:armhf
```

### 5. Expecting Hardware PWM with lgpio

**Problem**: lgpio doesn't provide pigpio's DMA-based hardware PWM.

**Solution**: Use software PWM (toggle GPIO in loop) or kernel PWM subsystem (`/sys/class/pwm/`).

### 6. Multi-Process GPIO Access

**Problem**: Multiple programs trying to access same GPIO.

**libgpiod**: Kernel enforces exclusivity - second program will fail with "Device busy" (this is correct behavior).

**lgpio/pigpio/WiringPi**: No exclusivity enforcement - may cause conflicts.

**Solution**: Design your application to use a single process for GPIO, or use libgpiod's exclusivity as a feature.

### 7. Threading Considerations for Daemons

**Problem**: lgpio may spawn threads for callbacks, potentially causing shutdown delays.

**Solution**:
- For system daemons: Prefer libgpiod (direct ioctl calls, no background threads)
- For applications: lgpio is fine, but test shutdown behavior in your specific context

---

## Quick Reference: GPIO Output Example

### libgpiod v1
```c
struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");
struct gpiod_line *line = gpiod_chip_get_line(chip, 23);
gpiod_line_request_output(line, "app", 0);
gpiod_line_set_value(line, 1);
gpiod_line_release(line);
gpiod_chip_close(chip);
```

### libgpiod v2
```c
struct gpiod_chip *chip = gpiod_chip_open("/dev/gpiochip0");
struct gpiod_request_config *req = gpiod_request_config_new();
struct gpiod_line_config *cfg = gpiod_line_config_new();
gpiod_line_config_set_direction_default(cfg, GPIOD_LINE_DIRECTION_OUTPUT);
struct gpiod_line_request *request = gpiod_chip_request_lines(chip, req, cfg);
gpiod_line_request_set_value(request, 23, 1);
gpiod_line_request_release(request);
gpiod_line_config_free(cfg);
gpiod_request_config_free(req);
gpiod_chip_close(chip);
```

### lgpio
```c
int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);
lgGpioWrite(h, 23, 1);
lgGpiochipClose(h);
```

### pigpio
```c
gpioInitialise();
gpioSetMode(23, PI_OUTPUT);
gpioWrite(23, 1);
gpioTerminate();
```

### WiringPi
```c
wiringPiSetupGpio();
pinMode(23, OUTPUT);
digitalWrite(23, HIGH);
```

---

## Additional Resources

- **libgpiod Setup**: [docs/LIBGPIOD_SETUP.md](LIBGPIOD_SETUP.md)
- **lgpio Setup**: [docs/LGPIO_SETUP.md](LGPIO_SETUP.md)
- **Framework Comparison**: [docs/FRAMEWORKS.md](FRAMEWORKS.md)

---

**Last Updated**: 2025-11-14
