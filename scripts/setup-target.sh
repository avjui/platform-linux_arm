#!/bin/bash
# setup-target.sh - Prepare Raspberry Pi for hardware testing
#
# Usage:
#   1. Copy this script to your Raspberry Pi
#   2. Run: bash setup-target.sh
#   3. Logout/login for gpio group membership to take effect

set -e

echo "=== Raspberry Pi Hardware Test Setup ==="
echo ""

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install lgpio (for lgpio framework tests)
echo "Installing lgpio..."
sudo apt-get install -y lgpio

# Install WiringPi (for WiringPi framework tests)
echo "Installing WiringPi..."
sudo apt-get install -y wiringpi

# Install pigpio (for pigpio framework tests - deprecated)
echo "Installing pigpio..."
sudo apt-get install -y pigpio

# Add current user to gpio group (for non-root GPIO access)
echo "Adding $USER to gpio group..."
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
echo "Model: $(cat /proc/device-tree/model 2>/dev/null || cat /sys/firmware/devicetree/base/model 2>/dev/null || echo 'Unknown')"
echo "Architecture: $(uname -m)"
echo "Kernel: $(uname -r)"
if [ -f /etc/os-release ]; then
    echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  IMPORTANT: Logout and login again for gpio group membership to take effect"
echo "    Then you can run GPIO programs without sudo (for lgpio/pigpio)"
echo ""
echo "Next steps:"
echo "  1. Logout/login: exit"
echo "  2. Test GPIO access: groups | grep gpio"
echo "  3. Ready for hardware testing!"
