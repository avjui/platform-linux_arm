# GPIO Framework Selection Guide

This guide helps you choose the right GPIO framework for your Raspberry Pi or ARM SBC project.

## Quick Decision Tree

```
START: What are you building?
│
├─ System daemon/service?
│  ├─ Yes → libgpiod (kernel-enforced cleanup)
│  └─ No → Continue
│
├─ Need to support non-RPi SBCs (Orange Pi, Rock Pi, etc.)?
│  ├─ Yes → libgpiod (universal Linux standard)
│  └─ No → Continue
│
├─ Need I2C/SPI/PWM in same library?
│  ├─ Yes → lgpio (or use separate libs with libgpiod)
│  └─ No → Continue
│
├─ Raspberry Pi 5?
│  ├─ Yes → libgpiod or lgpio (NOT pigpio/WiringPi)
│  └─ No → Continue
│
├─ Legacy project with pigpio/WiringPi?
│  ├─ Yes → Keep existing (migration = work)
│  └─ No → libgpiod (portable) or lgpio (convenient)
```

## Framework Comparison Matrix

| Feature | libgpiod | lgpio | pigpio | WiringPi |
|---------|----------|-------|--------|----------|
| **Linux Standard** | Yes (Official kernel API) | Partial (RPi-focused) | No (RPi-only) | No (RPi-only) |
| **Pi 5 Support** | Yes | Yes | No | Partial (GCLK broken) |
| **Pi 1-4 Support** | Yes | Yes | Yes | Yes |
| **Cross-compilation** | Yes | Yes | Yes | No |
| **GPIO Control** | Yes (Full) | Yes (Full) | Yes (Full) | Yes (Full) |
| **PWM** | No (Use /sys/class/pwm | Yes (Software + HW | Yes (Hardware DMA | Yes (Basic) |
| **I2C** | No (Use smbus2 | Yes (Built-in) | Yes (Built-in) | Yes (Built-in) |
| **SPI** | No (Use spidev | Yes (Built-in) | Yes (Built-in) | Yes (Built-in) |
| **Serial** | No (Use pyserial | Yes (Built-in) | Yes (Built-in) | Yes (Built-in) |
| **Threading** | Yes (Direct ioctl calls) | Partial (Spawns threads) | Partial (Daemon process) | Partial (Variable) |
| **Resource Cleanup** | Yes (Kernel-enforced) | Partial (Manual cleanup) | Partial (Daemon mgmt) | Partial (Variable) |
| **Exclusivity** | Yes (Kernel-enforced) | No (Not guaranteed) | No (Not guaranteed) | No (Not guaranteed) |
| **State Persistence** | Partial (Requires dtparam) | Yes (Maintains) | Yes (Maintains) | Yes (Maintains) |
| **Universal SBC** | Yes (Any with chardev) | Partial (Primarily RPi) | No (RPi only) | No (RPi only) |
| **Systemd-Friendly** | Yes (Clean shutdown) | Partial (Reported delays)* | Partial (Daemon mgmt) | Partial (Mixed) |
| **Timing Precision** | Partial (Standard) | Partial (Standard) | Yes (Microsecond (DMA) | Partial (Standard) |
| **Waveform Generation** | No | No | Yes | No |
| **Servo Control** | No (Manual) | Partial (Manual) | Yes (Built-in) | Partial (Manual) |
| **Remote GPIO** | No | No | Yes (Via pigpiod) | No |
| **Maintenance Status** | Yes (Active, kernel) | Yes (Active) | Yes (Active) | Partial (Deprecated) |

\* *Anecdotal reports from LibreELEC/Kodi users; not comprehensively tested*

## Framework Recommendations

### libgpiod: The Universal Standard

**Best for:**
- System services and daemons
- Multi-SBC projects (Raspberry Pi, Orange Pi, Rock Pi, etc.)
- Production deployments requiring reliability
- Projects needing guaranteed GPIO exclusivity
- Portable code across different Linux ARM platforms

**Configuration:**

```ini
[env:universal]
platform = linux_arm
framework = libgpiod
board = raspberrypi_5  ; Works on any board
```

**Pros:**
- Official Linux kernel standard
- Works across all Linux ARM SBCs
- Yes (Kernel-enforced) GPIO exclusivity (only one process can claim a line)
- Predictable resource cleanup on process exit
- No persistent background threads for basic GPIO
- Future-proof (kernel interface)

**Cons:**
- GPIO only (use separate libraries for I2C/SPI/PWM)
- Requires `dtparam=strict_gpiod` for state persistence on Raspberry Pi
- Two API versions (v1.x and v2.x) can be confusing

**Setup:** See [docs/LIBGPIOD_SETUP.md](LIBGPIOD_SETUP.md)

**Example:** See `examples/libgpiod-blink/`

---

### lgpio: The Raspberry Pi Convenience Framework

**Best for:**
- Raspberry Pi-specific projects (all models including Pi 5)
- Projects needing multiple protocols (GPIO+I2C+SPI+PWM+UART)
- Rapid prototyping and development
- Single-library convenience

**Configuration:**

```ini
[env:raspberry_pi]
platform = linux_arm
framework = lgpio
board = raspberrypi_5
```

**Pros:**
- All protocols in one library (GPIO, I2C, SPI, PWM, UART)
- Works on all Raspberry Pi models (1-5)
- Good documentation and examples
- Yes (Maintains) GPIO state after process exit
- Cross-compilation support

**Cons:**
- Partial (Spawns threads) for callback/alert handling
- Anecdotal reports of shutdown delays in systemd contexts
- Raspberry Pi focused (less portable to other SBCs)
- No kernel-enforced GPIO exclusivity

**Setup:** See [docs/LGPIO_SETUP.md](LGPIO_SETUP.md)

**Examples:** See `examples/lgpio-blink/`, `examples/lgpio-pwm-fade/`, etc.

---

### pigpio: Legacy High-Performance (Pi 1-4 Only)

**Best for:**
- **LEGACY PROJECTS ONLY**
- Pi 1-4 projects requiring hardware-timed PWM
- Microsecond timing precision (DMA-based)
- Waveform generation
- Existing pigpio code that can't be migrated

**Configuration:**

```ini
[env:legacy_pi4]
platform = linux_arm
framework = pigpio
board = raspberrypi_4b  ; Pi 5 NOT supported
```

**Pros:**
- Yes (Microsecond timing precision (DMA-based)
- Yes (Hardware-timed PWM on any GPIO pin
- Yes (Built-in) servo control
- Waveform generation
- Remote GPIO via network (pigpiod daemon)

**Cons:**
- **Does NOT work on Raspberry Pi 5**
- **Will NOT work on future Raspberry Pi models**
- Direct register access (hardware-specific)
- Requires pigpiod daemon for multi-process access
- More complex setup

**Status:** Partial - **DEPRECATED** - pigpio's author (Joan) recommends lgpio for new projects

**Quote from pigpio author:**
> "pigpio does not work on the Pi 5, I do not think it can be made to work. lgpio will work."

**Setup:** Manual build from source required (no automated script)

**Example:** See `examples/pigpio-blink/`

---

### WiringPi: Legacy Only (Not Recommended)

**Best for:**
- **LEGACY PROJECTS ONLY**
- Maintaining existing WiringPi code
- **NOT RECOMMENDED FOR NEW PROJECTS**

**Configuration:**

```ini
[env:legacy_wiringpi]
platform = linux_arm
framework = wiringpi
board = raspberrypi_3b  ; Native compilation only
```

**Pros:**
- Arduino-like API (familiar for Arduino users)
- Command-line tools (gpio command)
- GC2 fork adds partial Pi 5 support

**Cons:**
- **Deprecated** (original author discontinued in 2019)
- **NO cross-compilation support** (must build on Raspberry Pi)
- Pi 5 support incomplete (GCLK broken in GC2 fork)
- Confusing pin numbering (WiringPi/BCM/Physical)
- Bypasses kernel GPIO management (causes conflicts)
- Not in official Raspberry Pi OS repos

**Status:** Partial - **DEPRECATED** - Raspberry Pi Foundation recommends gpiozero (Python) or libgpiod (C)

**Migration:** Migrate to libgpiod for portable, maintained code

---

### Bare-metal: Manual Control

**Best for:**
- Maximum portability (no library dependencies)
- Educational purposes
- Custom hardware requiring specific timing

**Configuration:**

```ini
[env:baremetal]
platform = linux_arm
board = raspberrypi_4b
; No framework specified
```

**Pros:**
- No library dependencies
- Maximum control
- Works on any board

**Cons:**
- Requires manual implementation of all GPIO operations
- More code to write and maintain
- Harder to debug

**Examples:** See `examples/baremetal-hello/`, `examples/baremetal-uart/`

## Board-Framework Compatibility Matrix

| Board | libgpiod | lgpio | pigpio | WiringPi | Bare-metal |
|-------|----------|-------|--------|----------|------------|
| Raspberry Pi 1 | Yes | Yes | Yes | Yes | Yes |
| Raspberry Pi 2 | Yes | Yes | Yes | Yes | Yes |
| Raspberry Pi 3 | Yes | Yes | Yes | Yes | Yes |
| Raspberry Pi 4 | Yes | Yes | Yes | Yes | Yes |
| **Raspberry Pi 5** | Yes | Yes | No | Partial | Yes |
| Raspberry Pi Zero | Yes | Yes | Yes | Yes | Yes |
| Raspberry Pi Zero 2W | Yes | Yes | Yes | Yes | Yes |
| Orange Pi Zero | Yes | Partial (Untested) | No | No | Yes |
| Rock Pi 4 | Yes | Partial (Untested) | No | No | Yes |
| Odroid N2 | Yes | Partial (Untested) | No | No | Yes |

## Multi-Protocol Development Strategies

### Strategy 1: libgpiod + Separate Libraries (Recommended for Portability)

Use the official kernel interfaces for each protocol:

- **GPIO**: libgpiod
- **PWM**: `/sys/class/pwm/` (kernel PWM subsystem)
- **I2C**: `smbus2` or `i2c-dev`
- **SPI**: `spidev`
- **Serial**: `pyserial` or termios

**Pros:**
- Maximum portability
- Official kernel interfaces
- Each protocol uses best-practice library

**Cons:**
- Multiple libraries to learn
- More setup complexity

**Example platformio.ini:**

```ini
[env:multi_protocol_portable]
platform = linux_arm
framework = libgpiod
board = raspberrypi_5
lib_deps =
    ; Add Python libraries via pip if using Python
```

### Strategy 2: lgpio All-in-One (Raspberry Pi Convenience)

Use lgpio for all protocols in one library:

**Pros:**
- Single library for everything
- Consistent API across protocols
- Simpler setup

**Cons:**
- Raspberry Pi specific
- Threading considerations for daemons
- Less portable to other SBCs

**Example platformio.ini:**

```ini
[env:multi_protocol_rpi]
platform = linux_arm
framework = lgpio
board = raspberrypi_5
```

## Migration Guides

### From WiringPi to libgpiod

#### GPIO Setup and Control

**WiringPi:**
```c
#include <wiringPi.h>

wiringPiSetupGpio();  // Use BCM numbering
pinMode(23, OUTPUT);
digitalWrite(23, HIGH);
digitalWrite(23, LOW);
int value = digitalRead(24);
```

**libgpiod (v1.x API):**
```c
#include <gpiod.h>

struct gpiod_chip *chip = gpiod_chip_open_by_name("gpiochip0");
struct gpiod_line *line_out = gpiod_chip_get_line(chip, 23);
gpiod_line_request_output(line_out, "example", 0);

gpiod_line_set_value(line_out, 1);
gpiod_line_set_value(line_out, 0);

struct gpiod_line *line_in = gpiod_chip_get_line(chip, 24);
gpiod_line_request_input(line_in, "example");
int value = gpiod_line_get_value(line_in);
```

#### Pin Numbering

Both use **BCM GPIO numbering** on Raspberry Pi (same numbers).

### From pigpio to lgpio (for Pi 5 Compatibility)

#### GPIO Setup and Control

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

#### PWM and Servo Control

For advanced PWM and servo control on Pi 5, you'll need to implement manual PWM or use hardware PWM via `/sys/class/pwm/`, as lgpio doesn't provide the same high-level PWM API as pigpio.

See [docs/PWM_SETUP.md](PWM_SETUP.md) for details.

## Code Examples

See the `examples/` directory for complete working projects:

### libgpiod Examples
- `libgpiod-blink/` - Basic LED blink (v1 API)
- `libgpiod-blink-v2/` - LED blink using v2 API
- `libgpiod-button/` - Button input with interrupts

### lgpio Examples
- `lgpio-blink/` - Basic LED blink
- `lgpio-pwm-fade/` - Software PWM LED fade
- `lgpio-i2c-sensor/` - I2C sensor reading
- `lgpio-spi-adc/` - SPI ADC reading

### Legacy Examples
- `pigpio-blink/` - pigpio LED blink (Pi 1-4 only)
- `wiringpi-blink/` - WiringPi LED blink (native only)

## System Dependencies

### libgpiod

**On target (Raspberry Pi):**
```bash
sudo apt install libgpiod-dev gpiod
```

**For cross-compilation:**
```bash
sudo dpkg --add-architecture armhf
sudo apt update
sudo apt install libgpiod-dev:armhf
```

See [docs/LIBGPIOD_SETUP.md](LIBGPIOD_SETUP.md) for detailed instructions.

### lgpio

**On target (Raspberry Pi):**
```bash
sudo apt install liblgpio-dev liblgpio1
```

**For cross-compilation:**
See [docs/LGPIO_SETUP.md](LGPIO_SETUP.md) for build-from-source instructions.

### pigpio

**On target (Raspberry Pi, Pi 1-4 only):**
```bash
sudo apt install libpigpio-dev pigpio
```

Not recommended for new projects. Use lgpio instead.

### WiringPi

Not in official repos. GC2 fork requires manual build. Not recommended for new projects.

## Additional Resources

### libgpiod
- **Documentation**: https://libgpiod.readthedocs.io/
- **Git Repository**: https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/
- **Setup Guide**: [docs/LIBGPIOD_SETUP.md](LIBGPIOD_SETUP.md)

### lgpio
- **Documentation**: http://abyz.me.uk/lg/lgpio.html
- **Git Repository**: https://github.com/joan2937/lg
- **Setup Guide**: [docs/LGPIO_SETUP.md](LGPIO_SETUP.md)

### pigpio (Legacy)
- **Documentation**: http://abyz.me.uk/rpi/pigpio/
- **Git Repository**: https://github.com/joan2937/pigpio

### Raspberry Pi Official
- **GPIO White Paper**: https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/
- **Forums**: https://forums.raspberrypi.com/

## Summary

**For most projects, choose:**

1. **libgpiod** - Universal Linux standard, works everywhere, best for production
2. **lgpio** - Raspberry Pi convenience framework, all protocols in one library

**Avoid for new projects:**

- **pigpio** - Pi 5 incompatible, use lgpio instead
- **WiringPi** - Deprecated, use libgpiod or lgpio instead

**Decision factors:**

- Multi-SBC support? → **libgpiod**
- Raspberry Pi only + need I2C/SPI/PWM? → **lgpio**
- System daemon? → **libgpiod**
- Pi 5? → **libgpiod** or **lgpio** (NOT pigpio/WiringPi)
- Legacy code? → Keep existing, but plan migration
