# Hardware Testing Guide

**Purpose**: Validate platform functionality on actual Raspberry Pi hardware
**Status**: Not yet executed (awaiting hardware tests)
**Last Updated**: 2025-11-09

---

## Overview

This guide provides comprehensive hardware testing procedures to validate that the platform-linux_arm platform works correctly on actual Raspberry Pi devices. Unlike cross-compilation build tests (CI), hardware tests verify **runtime functionality** including GPIO, frameworks, and board-specific features.

### Why Hardware Testing is Critical

**The Cross-Compilation Problem**:
- Development: Build on fast x86_64 machine
- Target: Run on ARM hardware
- **Gap**: Cross-compiled binaries **cannot run on build host**

**CI Testing Limitation**:
- GitHub Actions: x86_64 runners only
- CI validates: Code compiles for ARM ✅
- CI cannot validate: Code **runs** on ARM ❌

**Solutions**:
1. **Manual hardware testing** on actual Raspberry Pi devices (this guide)
2. **Automated remote test execution** via SSH (see [`REMOTE_TESTING.md`](../REMOTE_TESTING.md))

### Remote Test Execution Alternative

**New in v1.6.0**: The platform now supports **automated remote test execution** using PlatformIO's test framework. This provides an automated alternative to manual testing:

```ini
[env:raspberrypi_3b]
platform = linux_arm
board = raspberrypi_3b

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/tmp/program

; Test configuration - automatically deploys and runs tests
test_transport = ssh
test_build_src = yes
```

**When to use remote testing vs. manual testing:**
- **Remote Testing** (automated):
  - Unit tests (business logic validation)
  - Integration tests (automated GPIO, I2C, SPI tests)
  - CI/CD pipelines (automated test runs)
  - Regression testing (run tests frequently)

- **Manual Testing** (this guide):
  - Initial platform validation
  - Visual verification (LED blink, displays)
  - Exploratory testing
  - One-time board verification
  - Troubleshooting issues

**See also**: [`REMOTE_TESTING.md`](../REMOTE_TESTING.md) for comprehensive remote testing guide

---

## Test Coverage Matrix

### Hardware Coverage

| Device | Model | SoC | Arch | RAM | Priority | Status |
|--------|-------|-----|------|-----|----------|--------|
| **Pi 1** | Model B Rev 2 | BCM2835 | ARMv6 (32-bit) | 512MB | 🟡 MEDIUM | ⏳ Pending |
| **Pi 3** | Model B | BCM2837 | ARMv7 (32-bit) | 1GB | 🔴 HIGH | ⏳ Pending |
| **Pi 5** | Model B | BCM2712 | ARMv8 (64-bit) | 8GB | 🔴 HIGH | ⏳ Pending |

**Missing Hardware** (optional):
- Pi 2 Model B (BCM2836)
- Pi 4 Model B (BCM2711) - similar to Pi 3
- Pi 400, CM4, Zero 2W - lower priority

### Framework Coverage

| Framework | Pi 1 | Pi 3 | Pi 5 | Purpose |
|-----------|------|------|------|---------|
| **bare-metal** | ✅ Test | ✅ Test | ✅ Test | Generic Linux apps (no GPIO) |
| **lgpio** | ⚠️ Test + workaround | ✅ Test | ✅ Test | Modern GPIO (PRIMARY) |
| **WiringPi GC2** | ✅ Test | ✅ Test | ⚠️ Test (GCLK limitation) | Legacy GPIO compatibility |
| **pigpio** | ✅ Test | ✅ Test | ❌ Skip (incompatible) | Deprecated framework |

### Example Coverage

| Example | Frameworks | GPIO | Complexity | Priority |
|---------|-----------|------|------------|----------|
| baremetal-hello | None | No | Trivial | 🔴 HIGH |
| lgpio-blink | lgpio | Yes | Simple | 🔴 HIGH |
| wiringpi-blink | WiringPi | Yes | Simple | 🟡 MEDIUM |
| wiringpi-serial | WiringPi | Yes (UART) | Medium | 🟡 MEDIUM |
| pigpio-blink | pigpio | Yes | Simple | 🟢 LOW |

**Total**: 5 examples × 3 hardware platforms × 4 frameworks = **60 test combinations** (with exclusions: ~35 valid tests)

---

## Test Environment Setup

### Prerequisites

**Development Machine** (where you build):
- PlatformIO Core installed
- ARM cross-toolchains installed
- Platform installed: `pio pkg install --global --platform symlink://path/to/platform-linux_arm`

**Target Raspberry Pi** (where you test):
- Raspberry Pi OS (32-bit or 64-bit based on model)
- SSH enabled and accessible from dev machine
- Network connectivity
- Optional: LED on GPIO pin 17 for blink tests

### Network Configuration

```bash
# On dev machine: Verify SSH access
ssh pi@raspberrypi.local
# Or use IP address
ssh pi@192.168.1.100

# Set up SSH keys (optional but recommended)
ssh-copy-id pi@raspberrypi.local
```

### Target Setup Script

Run this on each Raspberry Pi before testing:

```bash
#!/bin/bash
# setup-target.sh - Prepare Raspberry Pi for testing

echo "=== Raspberry Pi Hardware Test Setup ==="

# Update package lists
sudo apt-get update

# Install lgpio (for lgpio framework tests)
sudo apt-get install -y lgpio

# Install WiringPi (for WiringPi framework tests)
sudo apt-get install -y wiringpi

# Install pigpio (for pigpio framework tests - deprecated)
sudo apt-get install -y pigpio

# Add current user to gpio group (for non-root GPIO access)
sudo usermod -a -G gpio $USER
echo "⚠️  You must logout/login for gpio group to take effect"

# Verify installations
echo ""
echo "=== Verification ==="
echo "lgpio version: $(lgpio --version 2>/dev/null || echo 'NOT FOUND')"
echo "WiringPi version: $(gpio -v 2>/dev/null | head -1 || echo 'NOT FOUND')"
echo "pigpio daemon: $(which pigpiod || echo 'NOT FOUND')"

echo ""
echo "=== System Information ==="
echo "Model: $(cat /proc/device-tree/model)"
echo "Architecture: $(uname -m)"
echo "Kernel: $(uname -r)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME)"

echo ""
echo "✅ Setup complete!"
echo "⚠️  Remember to logout/login for gpio group membership"
```

---

## Test Procedures

### Phase 1: Baseline Testing (Pi 3)

**Why Pi 3 First**: Most common, stable, well-documented

#### Test 1.1: Bare-Metal Hello World

**Purpose**: Validate basic cross-compilation and execution

```bash
# On dev machine
cd examples/baremetal-hello
pio run -e raspberrypi_3b

# Deploy to target
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/baremetal-test

# Execute on target
ssh pi@raspberrypi.local "/tmp/baremetal-test"
```

**Expected Output**:
```
Hello from Raspberry Pi 3 Model B!
Board: raspberrypi_3b
MCU: bcm2837
Frequency: 1200000000 Hz
```

**✅ Success Criteria**:
- Program executes without errors
- Output shows correct board name and specs
- Exit code: 0

**❌ Failure Modes**:
- "Exec format error" → Wrong architecture compiled
- "Permission denied" → chmod +x needed
- No output → Check stderr

---

#### Test 1.2: lgpio GPIO Blink

**Purpose**: Validate lgpio framework and GPIO functionality

```bash
# On dev machine
cd examples/lgpio-blink
pio run -e raspberrypi_3b

# Deploy to target
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/lgpio-test

# Execute on target (requires root for GPIO access)
ssh pi@raspberrypi.local "sudo /tmp/lgpio-test"
```

**Expected Output**:
```
lgpio blink example
Using GPIO chip 0, pin 17
Starting blink (Ctrl+C to exit)...
LED ON
LED OFF
LED ON
LED OFF
...
```

**✅ Success Criteria**:
- Program runs without errors
- Output shows GPIO operations
- LED physically blinks (if connected to GPIO 17)
- OR verify with multimeter: pin 17 toggles 3.3V ↔ 0V

**Hardware Verification** (optional):
```bash
# Connect LED:
# GPIO 17 (pin 11) → LED → 220Ω resistor → GND (pin 6)

# Or verify with multimeter on GPIO 17 (physical pin 11)
```

**❌ Failure Modes**:
- "Permission denied" → Run with sudo
- "gpiochip not found" → lgpio not installed on target
- "Cannot claim line" → Pin already in use

---

#### Test 1.3: WiringPi GPIO Blink

**Purpose**: Validate WiringPi GC2 framework

```bash
# On dev machine
cd examples/wiringpi-blink
pio run -e raspberrypi_3b

# Deploy to target
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/wiringpi-test

# Execute on target
ssh pi@raspberrypi.local "sudo /tmp/wiringpi-test"
```

**Expected Output**:
```
WiringPi blink example
Using WiringPi pin 0 (GPIO 17, physical pin 11)
Starting blink (Ctrl+C to exit)...
LED ON
LED OFF
...
```

**✅ Success Criteria**:
- Program runs without errors
- GPIO pin toggles (verify with LED or multimeter)

**❌ Failure Modes**:
- "wiringPiSetup: Unable to open /dev/mem" → Needs root
- "This module can only be loaded on a Raspberry Pi!" → Wrong board detection

---

#### Test 1.4: WiringPi Serial

**Purpose**: Validate UART functionality

```bash
# On dev machine
cd examples/wiringpi-serial
pio run -e raspberrypi_3b

# Deploy to target
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/serial-test

# Execute on target
ssh pi@raspberrypi.local "sudo /tmp/serial-test"
```

**Expected Output**:
```
WiringPi Serial Example
Opening /dev/ttyAMA0 at 9600 baud...
Serial port opened successfully
Sending: Hello from Raspberry Pi!
```

**Hardware Verification**:
```bash
# Connect USB-to-Serial adapter to GPIO 14 (TX) and GPIO 15 (RX)
# Monitor serial output:
screen /dev/ttyUSB0 9600
```

**✅ Success Criteria**:
- Serial port opens without errors
- Data transmitted (verify with serial monitor)

---

#### Test 1.5: pigpio GPIO Blink (Deprecated)

**Purpose**: Validate legacy pigpio framework (low priority)

```bash
# On dev machine
cd examples/pigpio-blink
pio run -e raspberrypi_3b

# Deploy to target
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:/tmp/pigpio-test

# Start pigpio daemon on target (required for pigpio)
ssh pi@raspberrypi.local "sudo pigpiod"

# Execute on target
ssh pi@raspberrypi.local "/tmp/pigpio-test"
```

**Expected Output**:
```
pigpio blink example
Connected to pigpio daemon
Using GPIO 17
Starting blink...
```

**✅ Success Criteria**:
- Connects to pigpio daemon
- GPIO pin toggles

**⚠️ Note**: pigpio deprecated, lgpio is recommended

---

### Phase 2: Latest Hardware (Pi 5)

**Why Pi 5**: Test 64-bit support, RP1 I/O controller

#### Test 2.1: Bare-Metal (64-bit)

```bash
# Build for Pi 5 (64-bit by default)
cd examples/baremetal-hello
pio run -e raspberrypi_5

# Deploy
scp .pio/build/raspberrypi_5/program pi@pi5.local:/tmp/test64

# Execute
ssh pi@pi5.local "/tmp/test64"
```

**Expected Output**:
```
Hello from Raspberry Pi 5!
Board: raspberrypi_5
MCU: bcm2712
Frequency: 2400000000 Hz
```

**✅ Success Criteria**:
- Binary executes on 64-bit Pi OS
- Correct board identification

---

#### Test 2.2: lgpio on Pi 5 (RP1 Chip)

**Purpose**: Validate lgpio works with Pi 5's new RP1 I/O controller

```bash
cd examples/lgpio-blink
pio run -e raspberrypi_5

scp .pio/build/raspberrypi_5/program pi@pi5.local:/tmp/lgpio-pi5
ssh pi@pi5.local "sudo /tmp/lgpio-pi5"
```

**Expected Output**:
```
lgpio blink example
Using GPIO chip 4, pin 17  # Note: Different chip number on Pi 5
Starting blink...
LED ON
LED OFF
...
```

**✅ Success Criteria**:
- lgpio auto-detects RP1 chip (gpiochip4)
- GPIO functions correctly despite different hardware

**⚠️ Pi 5 Specific**: RP1 I/O controller uses different gpiochip number

---

#### Test 2.3: WiringPi on Pi 5 (Limited)

```bash
cd examples/wiringpi-blink
pio run -e raspberrypi_5

scp .pio/build/raspberrypi_5/program pi@pi5.local:/tmp/wiringpi-pi5
ssh pi@pi5.local "sudo /tmp/wiringpi-pi5"
```

**Expected Behavior**:
- ✅ Basic GPIO should work
- ⚠️ GCLK function unavailable (RP1 limitation documented)

---

#### Test 2.4: pigpio on Pi 5 (Expected Failure)

**Purpose**: Confirm pigpio incompatibility with Pi 5

```bash
cd examples/pigpio-blink
# Should fail to build or refuse to run on Pi 5
```

**Expected**: Platform should warn/block pigpio on Pi 5 (see platform.py)

---

### Phase 3: Legacy Hardware (Pi 1)

**Why Pi 1**: Test oldest hardware, ARMv6 edge cases

#### Test 3.1: Bare-Metal

```bash
cd examples/baremetal-hello
pio run -e raspberrypi_1b

scp .pio/build/raspberrypi_1b/program pi@pi1.local:/tmp/test-pi1
ssh pi@pi1.local "/tmp/test-pi1"
```

**Expected Output**:
```
Hello from Raspberry Pi 1 Model B!
Board: raspberrypi_1b
MCU: bcm2835
Frequency: 700000000 Hz
```

---

#### Test 3.2: lgpio on Pi 1 (With Workaround)

**Purpose**: Validate Pi 1 compatibility with RPI_LGPIO_REVISION workaround

```bash
cd examples/lgpio-blink
pio run -e raspberrypi_1b

scp .pio/build/raspberrypi_1b/program pi@pi1.local:/tmp/lgpio-pi1

# Pi 1 requires RPI_LGPIO_REVISION environment variable
ssh pi@pi1.local "export RPI_LGPIO_REVISION=800012 && sudo /tmp/lgpio-pi1"
```

**Expected Output**:
```
lgpio blink example
Using GPIO chip 0, pin 17
Starting blink...
```

**✅ Success Criteria**:
- Works with RPI_LGPIO_REVISION set
- GPIO operations successful

**⚠️ Pi 1 Limitation**: Documented in docs/LGPIO_SETUP.md

---

## Automated Test Script

Create `scripts/hardware-test.sh` for automated testing:

```bash
#!/bin/bash
# hardware-test.sh - Automated hardware testing script
# Usage: ./scripts/hardware-test.sh <target-host> <board>
# Example: ./scripts/hardware-test.sh pi@raspberrypi.local raspberrypi_3b

set -e

TARGET_HOST="$1"
BOARD="$2"

if [ -z "$TARGET_HOST" ] || [ -z "$BOARD" ]; then
    echo "Usage: $0 <target-host> <board>"
    echo "Example: $0 pi@raspberrypi.local raspberrypi_3b"
    exit 1
fi

echo "=== Hardware Testing: $BOARD on $TARGET_HOST ==="
echo ""

# Test counter
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local example_dir="$2"
    local target_path="$3"
    local run_cmd="$4"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    # Build
    echo "Building $example_dir for $BOARD..."
    if ! pio run -d "$example_dir" -e "$BOARD"; then
        echo "❌ BUILD FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    echo "✅ Build successful"

    # Deploy
    echo "Deploying to $TARGET_HOST:$target_path..."
    if ! scp "$example_dir/.pio/build/$BOARD/program" "$TARGET_HOST:$target_path"; then
        echo "❌ DEPLOY FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    echo "✅ Deploy successful"

    # Execute
    echo "Executing on target..."
    if ! ssh "$TARGET_HOST" "$run_cmd"; then
        echo "❌ EXECUTION FAILED"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    echo "✅ Test PASSED: $test_name"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo ""

    return 0
}

# Test 1: Bare-metal
run_test \
    "Bare-metal Hello World" \
    "examples/baremetal-hello" \
    "/tmp/baremetal-test" \
    "timeout 5 /tmp/baremetal-test"

# Test 2: lgpio
run_test \
    "lgpio GPIO Blink" \
    "examples/lgpio-blink" \
    "/tmp/lgpio-test" \
    "timeout 10 sudo /tmp/lgpio-test"

# Test 3: WiringPi
run_test \
    "WiringPi GPIO Blink" \
    "examples/wiringpi-blink" \
    "/tmp/wiringpi-test" \
    "timeout 10 sudo /tmp/wiringpi-test"

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total:  $TESTS_TOTAL"
echo "Passed: $TESTS_PASSED ✅"
echo "Failed: $TESTS_FAILED ❌"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
```

**Usage**:
```bash
# Test on Pi 3
./scripts/hardware-test.sh pi@raspberrypi.local raspberrypi_3b

# Test on Pi 5
./scripts/hardware-test.sh pi@pi5.local raspberrypi_5

# Test on Pi 1
./scripts/hardware-test.sh pi@pi1.local raspberrypi_1b
```

---

## Test Results Template

Create `docs/HARDWARE_TEST_RESULTS.md` to document findings:

```markdown
# Hardware Test Results

**Test Date**: YYYY-MM-DD
**Tester**: Your Name
**Platform Version**: 1.x.x

## Test Environment

**Development Machine**:
- OS: Ubuntu 22.04 / macOS 14 / Windows 11
- PlatformIO Core: 6.1.18
- Toolchain: gcc-arm-linux-gnueabihf 11.4.0

**Target Devices**:
- Pi 1 Model B Rev 2: IP 192.168.1.101, OS: Raspberry Pi OS Lite (32-bit)
- Pi 3 Model B: IP 192.168.1.103, OS: Raspberry Pi OS (32-bit)
- Pi 5 Model B: IP 192.168.1.105, OS: Raspberry Pi OS (64-bit)

## Test Results

| Example | Framework | Pi 1 | Pi 3 | Pi 5 | Notes |
|---------|-----------|------|------|------|-------|
| baremetal-hello | None | ✅ | ✅ | ✅ | All pass |
| lgpio-blink | lgpio | ⚠️ | ✅ | ✅ | Pi 1: needs RPI_LGPIO_REVISION |
| wiringpi-blink | WiringPi | ✅ | ✅ | ⚠️ | Pi 5: GCLK unavailable |
| wiringpi-serial | WiringPi | ⏭️ | ⏭️ | ⏭️ | Not tested (no serial adapter) |
| pigpio-blink | pigpio | ⏭️ | ⏭️ | ❌ | Pi 5: Incompatible (expected) |

**Legend**:
- ✅ Pass
- ❌ Fail
- ⚠️ Pass with caveats
- ⏭️ Skipped

## Issues Discovered

### Issue 1: lgpio on Pi 1 requires environment variable
**Severity**: Low
**Workaround**: Set `RPI_LGPIO_REVISION=800012` before running
**Status**: Documented in docs/LGPIO_SETUP.md

### Issue 2: Example
...

## Recommendations

1. All critical tests passed
2. Documentation accurate
3. Ready for release
```

---

## Success Criteria

### Minimum Required (Before 1.0 Release)

- ✅ Bare-metal works on **at least one device** (any Pi)
- ✅ lgpio works on **Pi 3 or Pi 5**
- ✅ WiringPi works on **any Pi except Pi 5** (or with known limitations)
- ✅ All discovered issues **documented**

### Ideal Coverage

- ✅ All frameworks tested on Pi 3 (stable baseline)
- ✅ lgpio tested on Pi 5 (latest hardware)
- ✅ Pi 1 tested with workaround (legacy support)
- ✅ GPIO functionality verified (LED blink or multimeter)

---

## Troubleshooting

### "Exec format error"

**Cause**: Wrong architecture
**Fix**: Verify you're using correct board (raspberrypi_3b, not raspberrypi_zero for Pi 3)

### "Permission denied" (GPIO)

**Cause**: Insufficient permissions
**Fix**: Run with `sudo` or add user to `gpio` group

### lgpio: "gpiochip not found"

**Cause**: lgpio not installed on target
**Fix**: `sudo apt-get install lgpio`

### WiringPi: "Unable to open /dev/mem"

**Cause**: Needs root access
**Fix**: Run with `sudo`

### pigpio: "Can't connect to pigpio daemon"

**Cause**: pigpiod not running
**Fix**: `sudo pigpiod` before running program

---

## Next Steps After Testing

1. **Document Results**: Fill in `docs/HARDWARE_TEST_RESULTS.md`
2. **Update README**: Add "Tested On" section with confirmed devices
3. **Report Issues**: Create GitHub issues for any failures
4. **Update CI**: Add hardware test status badge (if using self-hosted runner)
5. **Release**: Ready for v1.0 if all critical tests pass

---

**Estimated Testing Time**: 2-3 hours for full coverage (all devices + all examples)

**Quick Validation** (30 minutes): Test bare-metal + lgpio on Pi 3 only
