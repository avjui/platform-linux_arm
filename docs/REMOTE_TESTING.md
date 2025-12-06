# Remote Test Execution Guide

This guide explains how to run PlatformIO tests on remote Linux ARM targets using SSH. This feature enables:

- **Cross-compilation** of test binaries on development machines
- **Automated deployment** to target hardware via SSH
- **Remote execution** on actual ARM Linux devices
- **Real-time test results** streamed back to the host
- **CI/CD integration** for automated hardware testing

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration Reference](#configuration-reference)
- [SSH Setup](#ssh-setup)
- [Writing Tests](#writing-tests)
- [Hardware Testing](#hardware-testing)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

### Why Remote Test Execution?

For embedded Linux development, there are three levels of testing:

1. **Unit Tests** (business logic) - Can run anywhere
2. **Integration Tests** (hardware interaction) - Must run on target
3. **System Tests** (end-to-end) - Must run on target

Remote test execution enables all three levels by automatically:
- Building tests on your development machine
- Deploying to target hardware
- Running tests in the target environment
- Reporting results back

### How It Works

```
┌─────────────────┐
│  Development    │
│    Machine      │
│                 │
│  1. Cross-      │
│     compile     │
│     tests       │
└────────┬────────┘
         │ SSH/SCP
         ▼
┌─────────────────┐
│  Target Device  │
│   (ARM Linux)   │
│                 │
│  2. Execute     │
│     tests       │
│  3. Stream      │
│     output      │
└─────────────────┘
```

### Architecture

The implementation consists of:

- **`platform-test-uploader.py`**: Python script for SSH deployment and execution
- **`platform.py:on_test_upload()`**: Integration with PlatformIO test framework
- **`builder/main.py`**: SCons build configuration for test targets
- **SSH transport layer**: Uses standard SSH/SCP tools

## Quick Start

### 1. Configure platformio.ini

Add test configuration to your project:

```ini
[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b

; SSH upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/tmp/program

; Test configuration
test_transport = ssh
test_build_src = yes  ; Include src/ files in test builds
```

**Note:** You may see a warning: `Warning! Ignore unknown configuration option 'test_transport'`.
This is expected and harmless - PlatformIO's core schema doesn't include platform-specific
options, but the platform correctly handles the configuration.

### 2. Set Up SSH Access

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096

# Copy key to target device
ssh-copy-id pi@raspberrypi.local

# Verify connection
ssh pi@raspberrypi.local echo "Connected!"
```

### 3. Write Tests

Create `test/test_example/test_main.c`:

```c
#include <unity.h>

void setUp(void) {}
void tearDown(void) {}

void test_example(void) {
    TEST_ASSERT_EQUAL(42, 42);
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_example);
    return UNITY_END();
}
```

### 4. Run Tests

```bash
pio test
```

That's it! PlatformIO will:
- Cross-compile your tests for ARM
- Upload to the target via SSH
- Execute remotely
- Show results in real-time

## Configuration Reference

### Test Configuration Options

#### test_transport

**Type:** String
**Default:** `manual`
**Options:** `ssh`, `manual`

Specifies how tests are uploaded and executed.

```ini
test_transport = ssh  ; Upload and execute via SSH
```

#### test_port

**Type:** String
**Default:** Uses `upload_port` if not specified
**Format:** `user@host:/path/to/test_binary`

SSH target for test execution. Can also be just `user@host` with path in `test_path`.

```ini
test_port = pi@raspberrypi.local:/tmp/test_program
```

Alternative formats:
```ini
; Full specification
test_port = pi@192.168.1.100:/tmp/test

; Host only (uses test_path for path)
test_port = pi@raspberrypi.local
test_path = /tmp/test_program

; IP address
test_port = root@192.168.1.50:/tmp/test
```

#### test_username

**Type:** String
**Default:** `pi`

Default SSH username if not specified in `test_port`.

```ini
test_port = raspberrypi.local  ; host only
test_username = myuser
```

#### test_path

**Type:** String
**Default:** `/tmp/test_program`

Default remote path for test binary if not specified in `test_port`.

```ini
test_port = pi@raspberrypi.local
test_path = /home/pi/tests/test_program
```

#### test_ssh_port

**Type:** Integer
**Default:** `22`

SSH port number.

```ini
test_ssh_port = 2222  ; Non-standard SSH port
```

#### test_ssh_key

**Type:** String
**Default:** Uses SSH agent/default keys

Path to SSH private key for authentication.

```ini
test_ssh_key = ~/.ssh/id_rsa_deploy
```

#### test_build_src

**Type:** Boolean
**Default:** `no`

Include `src/` directory files in test builds. Useful for testing application code.

```ini
test_build_src = yes
```

#### test_filter

**Type:** String
**Default:** `*` (all tests)

Filter which tests to run.

```ini
test_filter = test_hardware_*  ; Only hardware tests
```

### Upload Configuration Options

Test execution uses upload configuration by default if test-specific options aren't provided.

#### upload_protocol

**Type:** String
**Default:** `manual`
**Options:** `scp`, `rsync`, `ssh`, `manual`

```ini
upload_protocol = scp
```

#### upload_port

**Type:** String
**Format:** `user@host:/path/to/binary`

Used as fallback for `test_port` if not specified.

```ini
upload_port = pi@raspberrypi.local:/tmp/program
```

#### upload_ssh_port

**Type:** Integer
**Default:** `22`

Used as fallback for `test_ssh_port`.

```ini
upload_ssh_port = 22
```

#### upload_ssh_key

**Type:** String

Used as fallback for `test_ssh_key`.

```ini
upload_ssh_key = ~/.ssh/id_rsa
```

### Environment Variables

Use environment variables for CI/CD or dynamic configuration:

```ini
[env:raspberrypi_3b]
upload_port = ${env.REMOTE_HOST}:/tmp/program
upload_ssh_key = ${env.SSH_KEY_PATH}
test_transport = ssh
```

Set in shell:
```bash
export REMOTE_HOST=pi@192.168.1.100
export SSH_KEY_PATH=~/.ssh/deploy_key
pio test
```

## SSH Setup

### Password Authentication

Works out of the box but not recommended for CI/CD:

```ini
test_port = pi@raspberrypi.local:/tmp/test
```

PlatformIO will prompt for password when needed.

### SSH Key Authentication (Recommended)

#### Generate SSH Key

```bash
# Generate new key
ssh-keygen -t rsa -b 4096 -C "platformio@test"

# Save to: ~/.ssh/id_rsa (or custom path)
```

#### Copy Key to Target

```bash
# Method 1: ssh-copy-id (easiest)
ssh-copy-id pi@raspberrypi.local

# Method 2: Manual
cat ~/.ssh/id_rsa.pub | ssh pi@raspberrypi.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

#### Test Connection

```bash
ssh pi@raspberrypi.local echo "Success!"
```

Should connect without password prompt.

#### Configure PlatformIO

```ini
upload_port = pi@raspberrypi.local:/tmp/program
upload_ssh_key = ~/.ssh/id_rsa  ; Optional: auto-detected
test_transport = ssh
```

### SSH Config File (Advanced)

Create `~/.ssh/config`:

```
Host mypi
    HostName raspberrypi.local
    User pi
    Port 22
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

Use in `platformio.ini`:

```ini
upload_port = mypi:/tmp/program
test_transport = ssh
```

## Security Considerations for Remote Testing

### SSH Configuration for CI/CD

**Best Practices**:
- Use dedicated SSH keys for automated testing (not personal keys)
- Restrict SSH key permissions to specific commands (if supported by target)
- Use key-based authentication exclusively (disable password auth)
- Rotate CI/CD SSH keys regularly

**Example: Generate CI/CD SSH Key**:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/ci-test-runner -C "ci-test-automation"
chmod 600 ~/.ssh/ci-test-runner
```

### Host Key Verification

Partial - **Important Security Note**: The test framework disables strict host key checking by default (lines 126-128 in platform-test-uploader.py) for automation convenience.

Default behavior (automated testing):

```python
# SSH options in test uploader
"-o", "StrictHostKeyChecking=no"
"-o", "UserKnownHostsFile=/dev/null"
```

**Security implications:**

- Yes - Enables automated testing without manual SSH setup
- No - Vulnerable to man-in-the-middle (MITM) attacks
- Partial - Only use in trusted networks

For production or sensitive environments: Consider enabling strict checking by modifying the test uploader or using SSH config overrides.

### Test Isolation

**Recommended practices:**

- Run tests in isolated environments (containers, VMs, or dedicated hardware)
- Use dedicated test users with limited permissions
- Clean up test artifacts after execution
- Monitor test execution logs for anomalies

### Timeout Configuration

```ini
[env:myboard]
# Test upload timeout in seconds (default: 300)
test_upload_timeout = 300

# Test execution timeout in seconds (default: 600)
# Tests may run longer than uploads
test_timeout = 600
```

See [SECURITY.md](SECURITY.md) for detailed security guidance.

### Troubleshooting SSH

#### Permission Denied

```bash
# Check key permissions (must be 600)
chmod 600 ~/.ssh/id_rsa

# Check authorized_keys on target (must be 600)
ssh pi@raspberrypi.local "chmod 600 ~/.ssh/authorized_keys"

# Verify public key is in authorized_keys
ssh pi@raspberrypi.local "cat ~/.ssh/authorized_keys"
```

#### Connection Refused

```bash
# Test basic connectivity
ping raspberrypi.local

# Check SSH server is running
ssh pi@raspberrypi.local "systemctl status sshd"

# Try IP address instead of hostname
test_port = pi@192.168.1.100:/tmp/test
```

#### Host Key Verification Failed

```bash
# Remove old host key
ssh-keygen -R raspberrypi.local

# Or disable strict checking (less secure)
ssh -o StrictHostKeyChecking=no pi@raspberrypi.local
```

## Writing Tests

### Test Framework

PlatformIO uses **Unity** test framework by default. Tests are written in C.

### Basic Test Structure

```c
#include <unity.h>

// Runs before each test
void setUp(void) {
    // Initialize test environment
}

// Runs after each test
void tearDown(void) {
    // Clean up
}

// Individual test
void test_example(void) {
    TEST_ASSERT_EQUAL(42, 42);
}

// Main function
int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_example);
    return UNITY_END();
}
```

### Test Directory Structure

```
project/
├── platformio.ini
├── src/
│   └── module.c
├── include/
│   └── module.h
└── test/
    ├── test_module1/
    │   └── test_main.c
    └── test_module2/
        └── test_main.c
```

### Common Assertions

```c
// Equality
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_EQUAL_INT(expected, actual)
TEST_ASSERT_EQUAL_STRING(expected, actual)

// Boolean
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)

// Null checks
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_NOT_NULL(pointer)

// Memory
TEST_ASSERT_EQUAL_MEMORY(expected, actual, length)

// Floating point
TEST_ASSERT_EQUAL_FLOAT(expected, actual)
TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual)
```

### Testing Application Code

Enable `test_build_src` to include `src/` files:

```ini
test_build_src = yes
```

Test file:
```c
#include <unity.h>
#include "module.h"  // From src/

void test_module_function(void) {
    TEST_ASSERT_EQUAL(42, module_get_value());
}
```

### Multiple Test Suites

Organize tests by feature:

```
test/
├── test_core/
│   └── test_main.c       # Core functionality
├── test_hardware/
│   └── test_main.c       # Hardware interaction
└── test_integration/
    └── test_main.c       # End-to-end tests
```

Run specific suite:
```bash
pio test -f test_hardware
```

## Hardware Testing

### GPIO Testing Example

For WiringPi framework:

```c
#include <unity.h>
#include <wiringPi.h>

#define LED_PIN 0  // GPIO17

void setUp(void) {
    wiringPiSetup();
}

void tearDown(void) {
    // Turn off LED
    digitalWrite(LED_PIN, LOW);
}

void test_gpio_output(void) {
    pinMode(LED_PIN, OUTPUT);

    digitalWrite(LED_PIN, HIGH);
    TEST_ASSERT_EQUAL(HIGH, digitalRead(LED_PIN));

    digitalWrite(LED_PIN, LOW);
    TEST_ASSERT_EQUAL(LOW, digitalRead(LED_PIN));
}

int main(int argc, char **argv) {
    UNITY_BEGIN();
    RUN_TEST(test_gpio_output);
    return UNITY_END();
}
```

Configuration:
```ini
[env:raspberrypi_3b]
platform = linux_arm
framework = wiringpi
board = raspberrypi_3b

test_transport = ssh
test_port = pi@raspberrypi.local:/tmp/test
test_build_src = yes
```

### Testing Best Practices

1. **Separate unit tests from hardware tests**:
   ```
   test/
   ├── test_unit/        # Can run anywhere
   └── test_hardware/    # Requires target hardware
   ```

2. **Use descriptive test names**:
   ```c
   void test_led_toggles_correctly(void)
   void test_i2c_read_temperature_sensor(void)
   ```

3. **Clean up after tests**:
   ```c
   void tearDown(void) {
       // Reset GPIO states
       // Close file handles
       // Free memory
   }
   ```

4. **Handle hardware failures gracefully**:
   ```c
   void test_i2c_device(void) {
       int fd = i2c_open("/dev/i2c-1");
       if (fd < 0) {
           TEST_IGNORE_MESSAGE("I2C device not available");
           return;
       }
       // ... rest of test
       close(fd);
   }
   ```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Remote Hardware Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install PlatformIO
        run: |
          pip install platformio
          pio --version

      - name: Set up SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.REMOTE_HOST_IP }} >> ~/.ssh/known_hosts

      - name: Run Tests on Remote Hardware
        env:
          REMOTE_HOST: pi@${{ secrets.REMOTE_HOST_IP }}
        run: |
          pio test --project-dir examples/remote-testing

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            examples/remote-testing/.pio/build/*/output.txt
```

**Required Secrets** (Settings → Secrets):
- `SSH_PRIVATE_KEY`: Your SSH private key content
- `REMOTE_HOST_IP`: Target device IP (e.g., `192.168.1.100`)

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test

hardware_tests:
  stage: test
  image: python:3.11
  before_script:
    - pip install platformio
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan -H $REMOTE_HOST_IP >> ~/.ssh/known_hosts
  script:
    - cd examples/remote-testing
    - pio test
  variables:
    REMOTE_HOST_IP: "192.168.1.100"
  artifacts:
    when: always
    paths:
      - examples/remote-testing/.pio/build/*/output.txt
```

**Required Variables** (Settings → CI/CD → Variables):
- `SSH_PRIVATE_KEY`: SSH private key
- `REMOTE_HOST_IP`: Target IP

### Jenkins Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any

    environment {
        REMOTE_HOST = "pi@${env.REMOTE_HOST_IP}"
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install platformio'
            }
        }

        stage('Configure SSH') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: 'pi-ssh-key',
                    keyFileVariable: 'SSH_KEY'
                )]) {
                    sh '''
                        mkdir -p ~/.ssh
                        cp $SSH_KEY ~/.ssh/id_rsa
                        chmod 600 ~/.ssh/id_rsa
                        ssh-keyscan -H $REMOTE_HOST_IP >> ~/.ssh/known_hosts
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pio test --project-dir examples/remote-testing'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/.pio/build/*/output.txt', allowEmptyArchive: true
        }
    }
}
```

### Self-Hosted Runners

For faster CI/CD, use self-hosted runners with direct network access to target hardware.

**GitHub Actions Self-Hosted:**
```yaml
jobs:
  test:
    runs-on: self-hosted  # Uses your own runner
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: pio test
```

**Benefits:**
- No SSH tunneling required
- Faster uploads (LAN speeds)
- Better hardware access
- Reduced latency

## Troubleshooting

### Common Issues

#### 1. "test_port is not configured"

**Error:**
```
ERROR: test_port or upload_port is not configured
```

**Solution:**
Add to `platformio.ini`:
```ini
upload_port = user@host:/path/to/binary
test_transport = ssh
```

#### 2. "SSH is not installed"

**Error:**
```
ERROR: SSH is not installed
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install openssh-client

# macOS (pre-installed)
# Windows
# Install Git for Windows (includes SSH)
# Or use WSL
```

#### 3. "Permission denied (publickey)"

**Error:**
```
Permission denied (publickey,password)
```

**Solution:**
```bash
# Ensure SSH key is correct
ssh -i ~/.ssh/id_rsa pi@raspberrypi.local

# Or use ssh-copy-id
ssh-copy-id pi@raspberrypi.local

# Check key permissions
chmod 600 ~/.ssh/id_rsa
```

#### 4. "Connection timed out"

**Error:**
```
ssh: connect to host raspberrypi.local port 22: Connection timed out
```

**Solution:**
```bash
# Test connectivity
ping raspberrypi.local

# Try IP address
test_port = pi@192.168.1.100:/tmp/test

# Check SSH server on target
ssh pi@raspberrypi.local "systemctl status sshd"
```

#### 5. "Warning! Ignore unknown configuration option `test_transport`"

**Warning Message:**
```
Warning! Ignore unknown configuration option `test_transport` in section [env:raspberrypi_5]
```

**Explanation:**
This warning is **normal and expected**. PlatformIO's core validator doesn't know about platform-specific configuration options like `test_transport`. The option is properly recognized and used by the `linux_arm` platform during test execution.

**Why it appears:**
- The warning appears when running non-test commands (`upload`, `build`, etc.)
- PlatformIO validates all options in the environment section
- Platform-specific options (like `test_transport`) are not in the core validation schema

**Action Required:**
None. The warning can be safely ignored. Your `test_transport` configuration is working correctly when you run `pio test`.

**To verify it's working:**
```bash
# Run tests - test_transport will be used correctly
pio test

# You should see the SSH test execution without errors
```

#### 6. Tests Pass Locally But Fail Remotely

**Possible causes:**
- Different CPU architecture (endianness, alignment)
- Missing libraries on target
- Hardware not available (GPIO, I2C devices)
- File path assumptions

**Debug:**
```bash
# Run test binary manually on target
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/test
ssh pi@raspberrypi.local "/tmp/test"
```

#### 6. "Failed to make test binary executable"

**Error:**
```
ERROR: Failed to make test binary executable
```

**Solution:**
```bash
# Verify target path is writable
ssh pi@raspberrypi.local "ls -ld /tmp"

# Use different path with write permissions
test_path = /home/pi/tests/test_program
```

### Debug Mode

Enable verbose output:

```bash
# Verbose test output
pio test -v

# Very verbose (shows all commands)
pio test -vv
```

### Manual Testing

Test the upload process manually:

```bash
# 1. Build tests
pio test --without-uploading

# 2. Find test binary
find .pio/build -name "program" -type f

# 3. Upload manually
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/test
ssh pi@raspberrypi.local "chmod +x /tmp/test"

# 4. Run manually
ssh pi@raspberrypi.local "/tmp/test"
```

## Best Practices

### 1. Use SSH Keys for Automation

Never use password authentication in CI/CD. Always use SSH keys:

```bash
# Generate dedicated CI key
ssh-keygen -t ed25519 -C "ci@platformio" -f ~/.ssh/ci_key

# Add to target
ssh-copy-id -i ~/.ssh/ci_key.pub pi@raspberrypi.local
```

### 2. Organize Tests by Type

```
test/
├── test_unit/          # Pure logic, no hardware
├── test_integration/   # Hardware interaction
└── test_system/        # End-to-end scenarios
```

Run selectively:
```bash
pio test -f test_unit        # Fast, no hardware needed
pio test -f test_integration # Hardware required
```

### 3. Use Environment-Specific Configuration

```ini
; Local development with mDNS
[env:dev]
extends = env:raspberrypi_3b
upload_port = pi@raspberrypi.local:/tmp/program

; CI/CD with static IP
[env:ci]
extends = env:raspberrypi_3b
upload_port = ${env.REMOTE_HOST}:/tmp/program
upload_ssh_key = ${env.SSH_KEY_PATH}
```

### 4. Implement Test Timeouts

```ini
test_timeout = 30  ; seconds
```

### 5. Clean Up After Tests

```c
void tearDown(void) {
    // Reset GPIO to safe state
    digitalWrite(LED_PIN, LOW);
    pinMode(LED_PIN, INPUT);

    // Close file handles
    // Free allocated memory
}
```

### 6. Use CI Artifacts

Save test outputs for debugging:

```yaml
- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: .pio/build/*/output.txt
```

### 7. Cache Build Artifacts

Speed up CI/CD:

```yaml
- name: Cache PlatformIO
  uses: actions/cache@v3
  with:
    path: ~/.platformio
    key: ${{ runner.os }}-pio
```

### 8. Parallel Testing

If you have multiple target devices:

```ini
[env:pi1]
upload_port = pi@192.168.1.100:/tmp/test
test_transport = ssh

[env:pi2]
upload_port = pi@192.168.1.101:/tmp/test
test_transport = ssh
```

Run in parallel:
```bash
pio test -e pi1 & pio test -e pi2 & wait
```

### 9. Version Control SSH Config

Don't commit SSH keys, but do commit config templates:

```
.ssh/
├── config.example      # Commit this
└── id_rsa             # DON'T commit this
```

### 10. Monitor Test Duration

Track test execution time to catch performance regressions:

```c
void test_performance_critical_function(void) {
    clock_t start = clock();

    critical_function();

    clock_t end = clock();
    double duration = ((double)(end - start)) / CLOCKS_PER_SEC;

    TEST_ASSERT_LESS_THAN(0.1, duration);  // Must complete in < 100ms
}
```

## Examples

See working examples in:
- [`examples/remote-testing/`](examples/remote-testing/) - Complete remote testing example
- [`examples/wiringpi-blink/`](examples/wiringpi-blink/) - GPIO testing with WiringPi
- [`examples/lgpio-blink/`](examples/lgpio-blink/) - GPIO testing with lgpio

## Learn More

- [PlatformIO Unit Testing](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [Unity Test Framework](https://github.com/ThrowTheSwitch/Unity)
- [SSH Configuration Guide](https://www.ssh.com/academy/ssh/config)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

- [Report Issues](https://github.com/platformio/platform-linux_arm/issues)
- [PlatformIO Community](https://community.platformio.org/)
- [Platform Documentation](README.md)
