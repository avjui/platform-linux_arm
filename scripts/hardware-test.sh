#!/bin/bash
# hardware-test.sh - Automated hardware testing script
#
# Usage: ./scripts/hardware-test.sh <target-host> <board>
# Example: ./scripts/hardware-test.sh pi@raspberrypi.local raspberrypi_3b
#
# Prerequisites:
#   - PlatformIO Core installed on dev machine
#   - Platform installed (symlink or global)
#   - SSH access to target configured
#   - Target prepared with scripts/setup-target.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TARGET_HOST="$1"
BOARD="$2"

if [ -z "$TARGET_HOST" ] || [ -z "$BOARD" ]; then
    echo "Usage: $0 <target-host> <board>"
    echo ""
    echo "Example:"
    echo "  $0 pi@raspberrypi.local raspberrypi_3b"
    echo "  $0 pi@192.168.1.100 raspberrypi_5"
    echo ""
    echo "Supported boards:"
    echo "  raspberrypi_1b, raspberrypi_2b, raspberrypi_3b,"
    echo "  raspberrypi_4b, raspberrypi_5, raspberrypi_400,"
    echo "  raspberrypi_cm4, raspberrypi_zero, raspberrypi_zero2w"
    exit 1
fi

echo "=== Hardware Testing: $BOARD on $TARGET_HOST ==="
echo ""

# Verify SSH connectivity
echo "Checking SSH connectivity..."
if ! ssh -o ConnectTimeout=5 "$TARGET_HOST" "echo OK" > /dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to $TARGET_HOST${NC}"
    echo "Please check:"
    echo "  - Target is powered on and connected to network"
    echo "  - SSH is enabled on target"
    echo "  - Hostname/IP is correct"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection OK${NC}"
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
    local timeout_sec="${5:-10}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    # Build
    echo "Building $example_dir for $BOARD..."
    if ! pio run -d "$example_dir" -e "$BOARD" 2>&1 | grep -v "^Processing"; then
        echo -e "${RED}❌ BUILD FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo ""
        return 1
    fi
    echo -e "${GREEN}✅ Build successful${NC}"

    # Deploy
    echo "Deploying to $TARGET_HOST:$target_path..."
    if ! scp -q "$example_dir/.pio/build/$BOARD/program" "$TARGET_HOST:$target_path"; then
        echo -e "${RED}❌ DEPLOY FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo ""
        return 1
    fi
    echo -e "${GREEN}✅ Deploy successful${NC}"

    # Execute
    echo "Executing on target (timeout: ${timeout_sec}s)..."
    if ! ssh "$TARGET_HOST" "timeout $timeout_sec $run_cmd" 2>&1; then
        # Check if timeout was expected (Ctrl+C needed for blink examples)
        if [ $? -eq 124 ]; then
            echo -e "${YELLOW}⚠️  Program timed out (expected for blink examples)${NC}"
            echo -e "${GREEN}✅ Test PASSED: $test_name (GPIO blink running)${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ EXECUTION FAILED${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            echo ""
            return 1
        fi
    else
        echo -e "${GREEN}✅ Test PASSED: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi

    echo ""
    return 0
}

# Detect board family for special handling
IS_PI5=false
IS_PI1=false
if [[ "$BOARD" == "raspberrypi_5" ]]; then
    IS_PI5=true
    echo "Detected Pi 5 - will skip pigpio tests (incompatible)"
fi
if [[ "$BOARD" == "raspberrypi_1b" ]]; then
    IS_PI1=true
    echo "Detected Pi 1 - will set RPI_LGPIO_REVISION for lgpio"
fi
echo ""

# Test 1: Bare-metal Hello World
run_test \
    "Bare-metal Hello World" \
    "examples/baremetal-hello" \
    "/tmp/baremetal-test" \
    "/tmp/baremetal-test" \
    5

# Test 2: lgpio GPIO Blink
if [ "$IS_PI1" = true ]; then
    # Pi 1 requires RPI_LGPIO_REVISION workaround
    run_test \
        "lgpio GPIO Blink (with Pi 1 workaround)" \
        "examples/lgpio-blink" \
        "/tmp/lgpio-test" \
        "export RPI_LGPIO_REVISION=800012 && sudo /tmp/lgpio-test" \
        10
else
    run_test \
        "lgpio GPIO Blink" \
        "examples/lgpio-blink" \
        "/tmp/lgpio-test" \
        "sudo /tmp/lgpio-test" \
        10
fi

# Test 3: WiringPi GPIO Blink
run_test \
    "WiringPi GPIO Blink" \
    "examples/wiringpi-blink" \
    "/tmp/wiringpi-test" \
    "sudo /tmp/wiringpi-test" \
    10

# Test 4: pigpio GPIO Blink (skip on Pi 5)
if [ "$IS_PI5" = false ]; then
    # Start pigpio daemon first
    echo "Starting pigpio daemon on target..."
    ssh "$TARGET_HOST" "sudo killall pigpiod 2>/dev/null || true; sudo pigpiod" || true

    run_test \
        "pigpio GPIO Blink" \
        "examples/pigpio-blink" \
        "/tmp/pigpio-test" \
        "/tmp/pigpio-test" \
        10

    # Stop pigpio daemon
    ssh "$TARGET_HOST" "sudo killall pigpiod 2>/dev/null || true"
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: pigpio GPIO Blink"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${YELLOW}⏭️  SKIPPED: pigpio incompatible with Pi 5${NC}"
    echo ""
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Board:  $BOARD"
echo "Target: $TARGET_HOST"
echo ""
echo "Total:  $TESTS_TOTAL"
echo -e "Passed: ${GREEN}$TESTS_PASSED ✅${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED ❌${NC}"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Document results in docs/HARDWARE_TEST_RESULTS.md"
    echo "  2. Verify GPIO functionality with LED or multimeter (optional)"
    echo "  3. Test on other Pi models if available"
    exit 0
else
    echo -e "${RED}❌ Some tests failed - review output above${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check target has required libraries installed (run scripts/setup-target.sh)"
    echo "  - Verify user is in gpio group (groups | grep gpio)"
    echo "  - Check target logs: ssh $TARGET_HOST dmesg | tail"
    exit 1
fi
