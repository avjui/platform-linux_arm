#!/bin/bash
#
# Setup PWM Permissions Script
#
# Configures Linux PWM subsystem permissions for userspace access.
# Exports PWM channels, sets group ownership, and applies read/write permissions.
#
# Usage:
#   sudo ./scripts/setup-pwm-perms.sh [OPTIONS]
#
# Options:
#   --chip CHIP     PWM chip number (default: auto-detect)
#   --channels N    Number of channels to export (default: 2)
#   --group GROUP   Group name for permissions (default: gpio)
#   --help          Display this help message
#
# Examples:
#   sudo ./scripts/setup-pwm-perms.sh              # Auto-detect and setup
#   sudo ./scripts/setup-pwm-perms.sh --chip 0     # Force pwmchip0 (Pi 1-4)
#   sudo ./scripts/setup-pwm-perms.sh --chip 2     # Force pwmchip2 (Pi 5)
#
# Requirements:
#   - Must run as root (sudo)
#   - PWM device tree overlay loaded (dtoverlay=pwm or pwm-2chan)
#   - gpio group exists
#
# See docs/PWM_SETUP.md for complete documentation
#
# Copyright 2014-present PlatformIO <contact@platformio.org>
# Licensed under the Apache License, Version 2.0

set -e  # Exit on error

# Default values
PWM_CHIP=""
PWM_CHANNELS=2
GPIO_GROUP="gpio"
VERBOSE=0

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Usage information
usage() {
    cat << EOF
PWM Permissions Setup Script

Usage:
  sudo $0 [OPTIONS]

Options:
  --chip CHIP       PWM chip number (default: auto-detect)
  --channels N      Number of channels to export (default: 2)
  --group GROUP     Group name for permissions (default: gpio)
  --verbose         Enable verbose output
  --help            Display this help message

Examples:
  sudo $0                              # Auto-detect and setup
  sudo $0 --chip 0                     # Force pwmchip0 (Pi 1-4)
  sudo $0 --chip 2                     # Force pwmchip2 (Pi 5)
  sudo $0 --channels 1 --group users   # Custom configuration

Requirements:
  - Root privileges (run with sudo)
  - PWM device tree overlay loaded
  - Target group must exist

For complete documentation, see docs/PWM_SETUP.md
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --chip)
            PWM_CHIP="$2"
            shift 2
            ;;
        --channels)
            PWM_CHANNELS="$2"
            shift 2
            ;;
        --group)
            GPIO_GROUP="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=1
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    echo ""
    echo "Example:"
    echo "  sudo $0"
    exit 1
fi

print_info "PWM Permissions Setup"
echo "======================================"

# Auto-detect PWM chip if not specified
if [ -z "$PWM_CHIP" ]; then
    print_info "Auto-detecting PWM chip..."

    # Check for Pi 5 (pwmchip2/3)
    if [ -d "/sys/class/pwm/pwmchip2" ]; then
        PWM_CHIP=2
        print_info "Detected Raspberry Pi 5 (pwmchip2)"
    # Check for Pi 1-4 (pwmchip0)
    elif [ -d "/sys/class/pwm/pwmchip0" ]; then
        PWM_CHIP=0
        print_info "Detected Raspberry Pi 1-4 (pwmchip0)"
    else
        print_error "No PWM chip found!"
        echo ""
        echo "Possible causes:"
        echo "  1. PWM device tree overlay not loaded"
        echo "  2. Raspberry Pi model not supported"
        echo ""
        echo "Solution:"
        echo "  1. Edit /boot/config.txt (Pi 1-4) or /boot/firmware/config.txt (Pi 5)"
        echo "  2. Add: dtoverlay=pwm,pin=18,func=2"
        echo "  3. Reboot"
        echo ""
        echo "See docs/PWM_SETUP.md for detailed instructions"
        exit 1
    fi
fi

# Validate PWM chip exists
PWM_CHIP_PATH="/sys/class/pwm/pwmchip${PWM_CHIP}"
if [ ! -d "$PWM_CHIP_PATH" ]; then
    print_error "PWM chip not found: $PWM_CHIP_PATH"
    echo ""
    echo "Available PWM chips:"
    ls -1d /sys/class/pwm/pwmchip* 2>/dev/null || echo "  (none found)"
    exit 1
fi

print_success "Using PWM chip: pwmchip${PWM_CHIP}"

# Validate group exists
if ! getent group "$GPIO_GROUP" >/dev/null; then
    print_error "Group '$GPIO_GROUP' does not exist"
    echo ""
    echo "Available groups:"
    getent group | cut -d: -f1 | grep -E "(gpio|users|plugdev)" || true
    echo ""
    echo "Create the group with:"
    echo "  sudo groupadd $GPIO_GROUP"
    exit 1
fi

print_success "Using group: $GPIO_GROUP"

# Setup each PWM channel
echo ""
print_info "Setting up $PWM_CHANNELS PWM channel(s)..."

for ((channel=0; channel<PWM_CHANNELS; channel++)); do
    echo ""
    print_info "Channel $channel:"

    PWM_CHANNEL_PATH="${PWM_CHIP_PATH}/pwm${channel}"
    PWM_EXPORT="${PWM_CHIP_PATH}/export"
    PWM_UNEXPORT="${PWM_CHIP_PATH}/unexport"

    # Check if already exported
    if [ -d "$PWM_CHANNEL_PATH" ]; then
        print_warning "Channel already exported, re-configuring..."

        # Disable before reconfiguring
        if [ -f "${PWM_CHANNEL_PATH}/enable" ]; then
            echo 0 > "${PWM_CHANNEL_PATH}/enable" 2>/dev/null || true
            [ $VERBOSE -eq 1 ] && print_info "  Disabled PWM output"
        fi
    else
        # Export channel
        print_info "  Exporting channel..."
        if echo "$channel" > "$PWM_EXPORT" 2>/dev/null; then
            print_success "  Channel exported"

            # Wait for sysfs to create the directory
            for i in {1..10}; do
                [ -d "$PWM_CHANNEL_PATH" ] && break
                sleep 0.1
            done

            if [ ! -d "$PWM_CHANNEL_PATH" ]; then
                print_error "  Failed to export channel (timeout)"
                continue
            fi
        else
            print_error "  Failed to export channel"
            print_warning "  Channel may already be in use"
            continue
        fi
    fi

    # Set group ownership for all PWM files
    print_info "  Setting group ownership to '$GPIO_GROUP'..."
    chown -R root:${GPIO_GROUP} "$PWM_CHANNEL_PATH" 2>/dev/null || {
        print_error "  Failed to set group ownership"
        continue
    }

    # Set permissions: owner=rw, group=rw, other=r
    print_info "  Setting permissions..."
    chmod -R ug+rw,o+r "$PWM_CHANNEL_PATH" 2>/dev/null || {
        print_error "  Failed to set permissions"
        continue
    }

    # Verify permissions
    if [ $VERBOSE -eq 1 ]; then
        print_info "  Permissions:"
        ls -la "$PWM_CHANNEL_PATH" | tail -n +2 | sed 's/^/    /'
    fi

    print_success "  Channel $channel configured successfully"
done

# Setup export/unexport permissions (optional, for advanced users)
echo ""
print_info "Setting up export/unexport permissions..."
chown root:${GPIO_GROUP} "${PWM_CHIP_PATH}/export" 2>/dev/null || true
chown root:${GPIO_GROUP} "${PWM_CHIP_PATH}/unexport" 2>/dev/null || true
chmod ug+rw,o+r "${PWM_CHIP_PATH}/export" 2>/dev/null || true
chmod ug+rw,o+r "${PWM_CHIP_PATH}/unexport" 2>/dev/null || true

# Print summary
echo ""
echo "======================================"
print_success "PWM permissions setup complete!"
echo ""
echo "Configuration:"
echo "  PWM Chip: pwmchip${PWM_CHIP}"
echo "  Channels: ${PWM_CHANNELS}"
echo "  Group: ${GPIO_GROUP}"
echo ""

# Check if current user is in gpio group
if [ -n "$SUDO_USER" ]; then
    if groups "$SUDO_USER" | grep -q "\b${GPIO_GROUP}\b"; then
        print_success "User '$SUDO_USER' is in '$GPIO_GROUP' group"
    else
        print_warning "User '$SUDO_USER' is NOT in '$GPIO_GROUP' group"
        echo ""
        echo "Add user to group with:"
        echo "  sudo usermod -a -G ${GPIO_GROUP} $SUDO_USER"
        echo ""
        echo "Then log out and back in for changes to take effect"
    fi
fi

# Print usage instructions
echo ""
echo "Test PWM with:"
echo "  cd examples/lgpio-pwm-fade"
echo "  pio run"
echo "  sudo ./.pio/build/raspberrypi_4b/program"
echo ""
echo "For automatic setup on boot, install systemd service:"
echo "  sudo cp scripts/platformio-pwm.service /etc/systemd/system/"
echo "  sudo systemctl enable platformio-pwm.service"
echo "  sudo systemctl start platformio-pwm.service"
echo ""
echo "See docs/PWM_SETUP.md for complete documentation"
echo "======================================"

exit 0
