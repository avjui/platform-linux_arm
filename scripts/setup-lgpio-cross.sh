#!/bin/bash
# Setup script for lgpio cross-compilation
# This script builds lgpio from source for ARM and installs it locally

set -e

echo "=================================================="
echo "lgpio Cross-Compilation Setup"
echo "=================================================="
echo ""

# Set paths and defaults
# Resolve script and repo directories BEFORE any cd commands
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CROSS_PREFIX="${CROSS_PREFIX:-arm-linux-gnueabihf-}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/arm-linux-gnueabihf}"

# Detect architecture from cross-compiler prefix and set arch-specific build dir
# This prevents build contamination when switching between 32-bit and 64-bit builds
# (make's timestamp-based dependency tracking doesn't detect compiler changes)
if [[ "$CROSS_PREFIX" == "aarch64-"* ]]; then
    ARCH_NAME="ARM 64-bit (AArch64)"
    BUILD_DIR="${BUILD_DIR:-/tmp/lg-build-aarch64}"
else
    ARCH_NAME="ARM 32-bit (ARMv7)"
    BUILD_DIR="${BUILD_DIR:-/tmp/lg-build-armhf}"
fi

# Check if cross-compiler is installed
CROSS_GCC="${CROSS_PREFIX}gcc"
if ! command -v "$CROSS_GCC" &> /dev/null; then
    echo "❌ ERROR: Cross-compiler not found: $CROSS_GCC"
    echo ""
    echo "Please install it first:"
    if [[ "$CROSS_PREFIX" == "aarch64-"* ]]; then
        echo "  sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu"
    else
        echo "  sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf"
    fi
    echo ""
    exit 1
fi

echo "✓ Cross-compiler found: $($CROSS_GCC --version | head -1)"
echo "  Architecture: $ARCH_NAME"
echo ""

echo "Build directory: $BUILD_DIR"
echo "Install directory: $INSTALL_DIR"
echo "Cross-compiler prefix: $CROSS_PREFIX"
echo ""

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Clone or update lgpio repository
if [ -d "lg/.git" ]; then
    echo "Updating existing lg repository..."
    cd lg
    git pull
    echo "Cleaning previous build artifacts..."
    make clean
else
    echo "Cloning lg repository..."
    git clone https://github.com/joan2937/lg.git
    cd lg
fi

echo ""
echo "Building lgpio library for ARM..."
make CROSS_PREFIX="$CROSS_PREFIX" lib

echo ""
echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR/include"
mkdir -p "$INSTALL_DIR/lib"

# Install headers
cp -v lgpio.h rgpio.h "$INSTALL_DIR/include/"

# Install libraries
cp -v liblgpio.so* "$INSTALL_DIR/lib/" 2>/dev/null || true
cp -v librgpio.so* "$INSTALL_DIR/lib/" 2>/dev/null || true

# Create symlinks if needed
cd "$INSTALL_DIR/lib"
[ -f liblgpio.so.1 ] && ln -sf liblgpio.so.1 liblgpio.so
[ -f librgpio.so.1 ] && ln -sf librgpio.so.1 librgpio.so

echo ""
echo "=================================================="
echo "✓ lgpio cross-compilation setup complete!"
echo "=================================================="
echo ""
echo "Headers installed to: $INSTALL_DIR/include/"
echo "Libraries installed to: $INSTALL_DIR/lib/"
echo ""
echo "You can now build lgpio examples with PlatformIO:"
# Get the repository root directory safely
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${BUILD_DIR:-/tmp/lg-build}"
echo "  cd $REPO_ROOT"
echo "  source venv/bin/activate"
echo "  pio run -d examples/lgpio-blink"
echo ""
