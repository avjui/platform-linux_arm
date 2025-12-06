# GPIO Framework Selection Guide

This guide helps you choose the right GPIO framework for your Raspberry Pi project.

## Framework Comparison

| Feature | lgpio | pigpio | WiringPi | Bare-metal |
|---------|-------|--------|----------|------------|
| **Pi 5 Support** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Pi 1-4 Support** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cross-compilation** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **GPIO Control** | ✅ | ✅ | ✅ | Manual |
| **PWM** | ✅ | ✅ Advanced | ✅ Basic | Manual |
| **I2C** | ✅ | ✅ | ✅ | Manual |
| **SPI** | ✅ | ✅ | ✅ | Manual |
| **Serial** | ✅ | ✅ | ✅ | Manual |
| **Precise Timing** | ⚠️ Standard | ✅ Microsecond | ⚠️ Standard | ⚠️ Standard |
| **Waveform Generation** | ❌ | ✅ | ❌ | ❌ |
| **Servo Control** | ⚠️ Manual | ✅ Built-in | ⚠️ Manual | ❌ |
| **Remote GPIO** | ❌ | ✅ via pigpiod | ❌ | ❌ |
| **Maintenance Status** | ✅ Active | ✅ Active | ⚠️ Deprecated | N/A |

## Recommendations

### For New Projects

**Use lgpio** - It's the modern standard, actively maintained, and works on all Raspberry Pi models including Pi 5.

```ini
[env:myproject]
platform = linux_arm
framework = lgpio
board = raspberrypi_5
```

### For Raspberry Pi 5

**Use lgpio only** - This is your only framework option. pigpio and WiringPi are not compatible with Pi 5's new RP1 I/O controller.

```ini
[env:pi5_project]
platform = linux_arm
framework = lgpio
board = raspberrypi_5
```

### For Precise Timing and Advanced PWM (Pi 1-4)

**Use pigpio** - If you need microsecond timing accuracy, complex PWM patterns, waveform generation, or servo control.

```ini
[env:robotics]
platform = linux_arm
framework = pigpio
board = raspberrypi_4b
```

### For Legacy Project Compatibility (Pi 1-4)

**Use WiringPi** - If you're maintaining an existing WiringPi project and can't migrate yet.

**Note:** WiringPi requires native compilation on a Raspberry Pi. Cross-compilation is not supported.

```ini
[env:legacy]
platform = linux_arm
framework = wiringpi
board = raspberrypi_3b
```

### For Maximum Portability

**Use bare-metal** - Direct system calls work on all boards and architectures, but require more manual coding.

```ini
[env:portable]
platform = linux_arm
board = raspberrypi_4b
; No framework specified
```

## Board-Framework Compatibility Matrix

| Board | lgpio | pigpio | WiringPi | Bare-metal |
|-------|-------|--------|----------|------------|
| Raspberry Pi 1 | ✅ | ✅ | ✅ | ✅ |
| Raspberry Pi 2 | ✅ | ✅ | ✅ | ✅ |
| Raspberry Pi 3 | ✅ | ✅ | ✅ | ✅ |
| Raspberry Pi 4 | ✅ | ✅ | ✅ | ✅ |
| **Raspberry Pi 5** | **✅** | **❌** | **❌** | **✅** |
| Raspberry Pi Zero | ✅ | ✅ | ✅ | ✅ |

## Migration Guide: WiringPi → lgpio

If you're migrating from WiringPi to lgpio, here's a quick API mapping:

### GPIO Setup and Control

```c
// WiringPi
#include <wiringPi.h>

wiringPiSetupGpio();
pinMode(23, OUTPUT);
digitalWrite(23, HIGH);
digitalWrite(23, LOW);
int value = digitalRead(24);

// lgpio equivalent
#include <lgpio.h>

int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);  // flags=0, initial value=0
lgGpioWrite(h, 23, 1);
lgGpioWrite(h, 23, 0);
int value = lgGpioRead(h, 24);
lgGpiochipClose(h);
```

### PWM

```c
// WiringPi
pinMode(18, PWM_OUTPUT);
pwmWrite(18, 512);  // 50% duty cycle (0-1024 range)

// lgpio equivalent
// lgpio requires manual PWM implementation via toggling
// OR use hardware PWM via sysfs
// For complex PWM, consider using pigpio instead
```

### I2C

```c
// WiringPi
#include <wiringPiI2C.h>

int fd = wiringPiI2CSetup(0x48);
int data = wiringPiI2CReadReg8(fd, 0x00);
wiringPiI2CWriteReg8(fd, 0x01, 0xFF);

// lgpio equivalent
#include <lgpio.h>

int h = lgI2cOpen(1, 0x48, 0);  // I2C bus 1, address 0x48
int data = lgI2cReadByteData(h, 0x00);
lgI2cWriteByteData(h, 0x01, 0xFF);
lgI2cClose(h);
```

## Migration Guide: pigpio → lgpio (for Pi 5)

If you need to migrate from pigpio to lgpio for Pi 5 compatibility:

### GPIO Setup and Control

```c
// pigpio
#include <pigpio.h>

gpioInitialise();
gpioSetMode(23, PI_OUTPUT);
gpioWrite(23, 1);
gpioWrite(23, 0);
int value = gpioRead(24);
gpioTerminate();

// lgpio equivalent
#include <lgpio.h>

int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);
lgGpioWrite(h, 23, 1);
lgGpioWrite(h, 23, 0);
int value = lgGpioRead(h, 24);
lgGpiochipClose(h);
```

### PWM and Servo Control

For advanced PWM and servo control on Pi 5, you'll need to implement manual PWM or use hardware PWM via sysfs, as lgpio doesn't provide the same high-level PWM API as pigpio.

## Code Examples

### LED Blink Comparison

#### lgpio (Recommended for all boards)
```c
#include <stdio.h>
#include <lgpio.h>
#include <unistd.h>

#define GPIO_PIN 23

int main() {
    int h = lgGpiochipOpen(0);
    if (h < 0) {
        printf("Failed to open gpiochip0\n");
        return 1;
    }

    lgGpioClaimOutput(h, 0, GPIO_PIN, 0);

    for (int i = 0; i < 10; i++) {
        lgGpioWrite(h, GPIO_PIN, 1);  // HIGH
        sleep(1);
        lgGpioWrite(h, GPIO_PIN, 0);  // LOW
        sleep(1);
    }

    lgGpiochipClose(h);
    return 0;
}
```

#### pigpio (Pi 1-4 only)
```c
#include <stdio.h>
#include <pigpio.h>
#include <unistd.h>

#define GPIO_PIN 23

int main() {
    if (gpioInitialise() < 0) {
        printf("Failed to initialize pigpio\n");
        return 1;
    }

    gpioSetMode(GPIO_PIN, PI_OUTPUT);

    for (int i = 0; i < 10; i++) {
        gpioWrite(GPIO_PIN, 1);  // HIGH
        sleep(1);
        gpioWrite(GPIO_PIN, 0);  // LOW
        sleep(1);
    }

    gpioTerminate();
    return 0;
}
```

#### WiringPi (Legacy, Pi 1-4 only)
```c
#include <stdio.h>
#include <wiringPi.h>
#include <unistd.h>

#define GPIO_PIN 23

int main() {
    if (wiringPiSetupGpio() < 0) {
        printf("Failed to setup WiringPi\n");
        return 1;
    }

    pinMode(GPIO_PIN, OUTPUT);

    for (int i = 0; i < 10; i++) {
        digitalWrite(GPIO_PIN, HIGH);
        sleep(1);
        digitalWrite(GPIO_PIN, LOW);
        sleep(1);
    }

    return 0;
}
```

## System Dependencies

### lgpio
```bash
sudo apt update
sudo apt install liblgpio-dev liblgpio1
```

### pigpio
```bash
sudo apt update
sudo apt install libpigpio-dev pigpio
```

### WiringPi
WiringPi is deprecated and no longer receiving updates. It may be pre-installed on some Raspberry Pi OS versions, but is not recommended for new projects.

## Additional Resources

- **lgpio Documentation**: http://abyz.me.uk/lg/lgpio.html
- **pigpio Documentation**: http://abyz.me.uk/rpi/pigpio/
- **WiringPi Documentation**: http://wiringpi.com/ (archived)
- **GPIO Character Device**: https://www.kernel.org/doc/html/latest/driver-api/gpio/consumer.html

## Summary

**For most projects**: Use **lgpio**. It's modern, actively maintained, and works on all Raspberry Pi models.

**For Pi 5**: Use **lgpio** (your only option for GPIO frameworks).

**For advanced timing/PWM on Pi 1-4**: Use **pigpio** if you need microsecond precision or built-in servo control.

**For legacy projects**: Use **WiringPi** only if absolutely necessary for compatibility with existing code.
