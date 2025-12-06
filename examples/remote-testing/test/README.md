# Remote Testing Example

This example demonstrates remote test execution on Linux ARM targets using SSH.

## Overview

The tests are:
1. **Built** on the host machine (macOS or Linux x86_64)
2. **Cross-compiled** for ARM architecture
3. **Uploaded** to the target device via SSH
4. **Executed** remotely on the target hardware
5. **Results** streamed back to the host in real-time

## Test Structure

```
test/
└── test_math_functions/
    └── test_main.c       # Unit tests for math functions
```

## Running Tests

### Basic Usage

```bash
# Run all tests
pio test

# Run specific test
pio test -f test_math_functions

# Verbose output
pio test -v
```

### Configuration

Tests use the configuration from `platformio.ini`:

```ini
[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/tmp/program

; Test configuration
test_transport = ssh
test_build_src = yes
```

### SSH Setup

Before running tests, ensure:

1. **SSH access is configured** to your target device:
   ```bash
   ssh pi@raspberrypi.local  # Should connect without password
   ```

2. **SSH keys are set up** (recommended):
   ```bash
   ssh-copy-id pi@raspberrypi.local
   ```

3. **Target device is accessible** on the network

## Test Output

Example output:

```
Testing remote-testing:raspberrypi_3b [PASSED]
===========================================

test/test_math_functions/test_main.c:18:test_add_positive_numbers [PASSED]
test/test_math_functions/test_main.c:24:test_add_negative_numbers [PASSED]
test/test_math_functions/test_main.c:31:test_subtract_positive_numbers [PASSED]
test/test_math_functions/test_main.c:37:test_subtract_negative_numbers [PASSED]
test/test_math_functions/test_main.c:44:test_multiply_positive_numbers [PASSED]
test/test_math_functions/test_main.c:50:test_multiply_negative_numbers [PASSED]
test/test_math_functions/test_main.c:57:test_divide_positive_numbers [PASSED]
test/test_math_functions/test_main.c:63:test_divide_by_zero [PASSED]
test/test_math_functions/test_main.c:69:test_factorial_base_cases [PASSED]
test/test_math_functions/test_main.c:74:test_factorial_positive_numbers [PASSED]
test/test_math_functions/test_main.c:81:test_factorial_negative_input [PASSED]

----------------------
11 Tests 0 Failures 0 Ignored
OK
```

## CI/CD Integration

For CI/CD pipelines (GitHub Actions, GitLab CI, etc.), use environment variables:

```ini
[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b

; Use environment variables for credentials
upload_port = ${env.REMOTE_HOST}:/tmp/program
upload_ssh_key = ${env.SSH_KEY_PATH}
test_transport = ssh
```

Example GitHub Actions workflow:

```yaml
- name: Run Remote Tests
  env:
    REMOTE_HOST: pi@192.168.1.100
    SSH_KEY_PATH: ~/.ssh/ci_deploy_key
  run: pio test
```

## Hardware-Specific Tests

For tests that require hardware (GPIO, I2C, SPI), see the hardware examples:
- `examples/wiringpi-blink/test/` - GPIO tests with WiringPi
- `examples/lgpio-blink/test/` - GPIO tests with lgpio

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection manually
ssh pi@raspberrypi.local echo "Connected successfully"

# Check SSH key permissions (should be 600)
chmod 600 ~/.ssh/id_rsa
```

### Test Timeout

If tests take too long, increase the timeout in `platformio.ini`:

```ini
test_timeout = 60  ; seconds
```

### Permission Denied on Target

Ensure the upload path is writable:

```bash
ssh pi@raspberrypi.local "mkdir -p /tmp && chmod 777 /tmp"
```

## Learn More

- [PlatformIO Unit Testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
- [SSH Configuration](https://www.ssh.com/academy/ssh/config)
