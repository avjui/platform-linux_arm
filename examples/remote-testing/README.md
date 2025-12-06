# Remote Testing Example

This example demonstrates **remote test execution** for Linux ARM targets using SSH. Tests are cross-compiled on your development machine and automatically deployed and executed on the target hardware.

## What This Example Demonstrates

1. **Cross-compilation** of test binaries for ARM targets
2. **Automated SSH deployment** of test executables
3. **Remote test execution** on actual hardware
4. **Real-time streaming** of test results back to the host
5. **CI/CD integration** patterns for automated testing

## Project Structure

```
remote-testing/
├── platformio.ini          # Project configuration
├── src/
│   ├── main.c             # Main application
│   └── math_functions.c   # Business logic (testable)
├── include/
│   └── math_functions.h   # Function declarations
└── test/
    └── test_math_functions/
        └── test_main.c    # Unit tests
```

## Quick Start

### 1. Prerequisites

**Hardware:**
- A Raspberry Pi or other ARM Linux device
- Network connection between host and target

**Software:**
- PlatformIO installed on your development machine
- SSH server running on target device
- SSH access configured (password or key-based)

### 2. Configure Target Device

Edit `platformio.ini` and set your target details:

```ini
[env:raspberrypi_3b]
upload_port = pi@raspberrypi.local:/tmp/program
; Or use IP address:
; upload_port = pi@192.168.1.100:/tmp/program
```

### 3. Set Up SSH Access

**Option A: SSH Keys (Recommended for CI/CD)**

```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096

# Copy key to target device
ssh-copy-id pi@raspberrypi.local

# Test connection
ssh pi@raspberrypi.local echo "Connected successfully"
```

**Option B: Password Authentication**

PlatformIO will prompt for password when needed (not suitable for CI/CD).

### 4. Build and Upload

```bash
# Build the project
pio run

# Upload to target device
pio upload

# Or build and upload in one step
pio run --target upload
```

### 5. Run Tests

```bash
# Run all tests
pio test

# Run specific test
pio test -f test_math_functions

# Verbose output
pio test -v
```

## How It Works

### Test Execution Flow

1. **Build Phase** (on host):
   - PlatformIO compiles test source files
   - Cross-compilation for ARM architecture
   - Links with Unity test framework
   - Produces test binary for target

2. **Upload Phase** (SSH):
   - Test binary uploaded via SCP to target device
   - Binary made executable (`chmod +x`)

3. **Execution Phase** (on target):
   - Test binary executed remotely via SSH
   - Test output streamed back to host in real-time

4. **Result Phase** (on host):
   - PlatformIO parses Unity test output
   - Reports pass/fail status
   - Returns appropriate exit code for CI/CD

### Configuration Options

**Basic Configuration:**

```ini
[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b

; Required: SSH target configuration
upload_protocol = scp
upload_port = user@host:/path/to/binary

; Required: Test transport
test_transport = ssh

; Optional: Include src/ files in test builds
test_build_src = yes
```

**Advanced Configuration:**

```ini
[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/tmp/program
upload_ssh_port = 22               ; Default SSH port
upload_ssh_key = ~/.ssh/id_rsa     ; Path to SSH private key

; Test configuration
test_transport = ssh
test_port = pi@raspberrypi.local:/tmp/test_program  ; Override for tests
test_build_src = yes               ; Include src/ in test builds
test_filter = test_*               ; Run tests matching pattern
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Remote Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install PlatformIO
        run: pip install platformio

      - name: Set up SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.REMOTE_HOST }} >> ~/.ssh/known_hosts

      - name: Run Remote Tests
        env:
          REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
        run: |
          cd examples/remote-testing
          pio test
```

**Required GitHub Secrets:**
- `SSH_PRIVATE_KEY`: Your SSH private key
- `REMOTE_HOST`: Target device address (e.g., `pi@192.168.1.100`)

### GitLab CI Example

Create `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.11
  before_script:
    - pip install platformio
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan -H $REMOTE_HOST >> ~/.ssh/known_hosts
  script:
    - cd examples/remote-testing
    - pio test
  variables:
    REMOTE_HOST: "pi@192.168.1.100"
```

## Writing Tests

Tests use the **Unity** test framework (PlatformIO's default). Basic structure:

```c
#include <unity.h>
#include "your_module.h"

void setUp(void) {
    // Runs before each test
}

void tearDown(void) {
    // Runs after each test
}

void test_example(void) {
    TEST_ASSERT_EQUAL(42, your_function());
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_example);
    return UNITY_END();
}
```

### Test Assertions

Common Unity assertions:

```c
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_NOT_NULL(pointer)
TEST_ASSERT_EQUAL_STRING(expected, actual)
TEST_ASSERT_EQUAL_MEMORY(expected, actual, length)
```

See [Unity documentation](https://github.com/ThrowTheSwitch/Unity) for complete list.

## Hardware Testing

For tests that interact with GPIO, I2C, SPI, or other hardware:

1. **Use the appropriate framework** in `platformio.ini`:
   ```ini
   framework = wiringpi  ; or lgpio, pigpio
   ```

2. **Mock hardware when possible** for unit tests

3. **Create integration tests** for hardware interaction:
   ```c
   void test_gpio_output(void) {
       pinMode(LED_PIN, OUTPUT);
       digitalWrite(LED_PIN, HIGH);
       TEST_ASSERT_EQUAL(HIGH, digitalRead(LED_PIN));
   }
   ```

4. **Run hardware tests on target only**:
   ```ini
   test_filter = test_hardware_*  ; Only hardware tests
   test_transport = ssh           ; Must run on device
   ```

## Troubleshooting

### "Connection refused" Error

**Problem:** Can't connect to target device

**Solutions:**
- Verify target is powered on and connected to network
- Test SSH manually: `ssh pi@raspberrypi.local`
- Check firewall settings on target device
- Try using IP address instead of hostname

### "Permission denied" Error

**Problem:** Can't authenticate with target

**Solutions:**
- Verify SSH key is correct: `ssh -i ~/.ssh/id_rsa pi@raspberrypi.local`
- Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
- Ensure public key is in target's `~/.ssh/authorized_keys`
- Try password authentication first to verify credentials

### "No such file or directory" on Target

**Problem:** Upload path doesn't exist

**Solutions:**
- Create the directory: `ssh pi@raspberrypi.local "mkdir -p /tmp"`
- Verify path in `upload_port` is writable
- Use `/tmp` which exists on all Linux systems

### Tests Timeout

**Problem:** Tests don't complete in time

**Solutions:**
- Increase timeout in `platformio.ini`:
  ```ini
  test_timeout = 120  ; seconds
  ```
- Optimize tests to run faster
- Check target isn't overloaded

### Cross-Compilation Errors

**Problem:** Build fails with toolchain errors

**Solutions:**
- Install required toolchain:
  ```bash
  # Ubuntu/Debian
  sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

  # macOS
  brew tap messense/macos-cross-toolchains
  brew install arm-unknown-linux-gnueabihf
  ```
- Verify board architecture matches toolchain

## Performance Tips

1. **Use rsync for faster uploads** (incremental transfers):
   ```ini
   upload_protocol = rsync
   ```

2. **Keep test binaries small**:
   - Only include necessary source files
   - Use `test_build_src = yes` to share code

3. **Run tests in parallel** (if you have multiple targets):
   ```bash
   pio test -e raspberrypi_3b -e orangepi_zero
   ```

4. **Cache build artifacts** in CI/CD pipelines

## Learn More

- [PlatformIO Unit Testing Guide](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
- [SSH Best Practices](https://www.ssh.com/academy/ssh/config)
- [Platform Linux ARM Documentation](../../README.md)

## Related Examples

- `examples/wiringpi-blink/` - GPIO with WiringPi
- `examples/lgpio-blink/` - GPIO with lgpio
- `examples/baremetal-hello/` - Minimal bare-metal example

## Support

For issues or questions:
- [Platform Issues](https://github.com/sfo2001/platform-linux_arm/issues)
- [PlatformIO Community](https://community.platformio.org/)
