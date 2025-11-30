#!/bin/bash
# Setup script for libgpiod cross-compilation
# This script builds libgpiod from source for ARM and installs it locally

set -e

echo "=================================================="
echo "libgpiod Cross-Compilation Setup"
echo "=================================================="
echo ""

# Set paths and defaults
# Resolve script and repo directories BEFORE any cd commands
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CROSS_PREFIX="${CROSS_PREFIX:-arm-linux-gnueabihf-}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/arm-linux-gnueabihf}"

# Detect architecture from cross-compiler prefix and set arch-specific build dir
if [[ "$CROSS_PREFIX" == "aarch64-"* ]]; then
    ARCH_NAME="ARM 64-bit (AArch64)"
    HOST_TRIPLE="aarch64-linux-gnu"
    BUILD_DIR="${BUILD_DIR:-/tmp/libgpiod-build-aarch64}"
else
    ARCH_NAME="ARM 32-bit (ARMv7)"
    HOST_TRIPLE="arm-linux-gnueabihf"
    BUILD_DIR="${BUILD_DIR:-/tmp/libgpiod-build-armhf}"
fi

# Check if cross-compiler is installed
CROSS_GCC="${CROSS_PREFIX}gcc"
if ! command -v "$CROSS_GCC" &> /dev/null; then
    echo "ERROR: Cross-compiler not found: $CROSS_GCC"
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

echo "Cross-compiler found: $($CROSS_GCC --version | head -1)"
echo "  Architecture: $ARCH_NAME"
echo ""

# Check for required build tools (libtool removed - autogen.sh will check)
MISSING_TOOLS=()
for tool in autoconf automake pkg-config; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "ERROR: Missing required build tools: ${MISSING_TOOLS[*]}"
    echo ""
    echo "Please install them first:"
    echo "  sudo apt install autoconf autoconf-archive automake libtool pkg-config"
    echo ""
    exit 1
fi

echo "Build tools found: autoconf, automake, pkg-config"
echo ""

echo "Build directory: $BUILD_DIR"
echo "Install directory: $INSTALL_DIR"
echo "Cross-compiler prefix: $CROSS_PREFIX"
echo "Host triple: $HOST_TRIPLE"
echo ""

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Clone or update libgpiod repository
if [ -d "libgpiod/.git" ]; then
    echo "Updating existing libgpiod repository..."
    cd libgpiod

    # Clean aggressively to avoid contamination between armhf/aarch64 builds
    echo "Cleaning previous build artifacts..."
    git clean -fdx  # Remove all untracked files and build artifacts
    git reset --hard  # Reset any modifications
    git fetch

    # Check if we're on a detached HEAD (tag checkout)
    if git symbolic-ref -q HEAD > /dev/null; then
        git pull
    else
        echo "  (on detached HEAD, skipping pull)"
    fi
else
    echo "Cloning libgpiod repository..."
    git clone https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git
    cd libgpiod

    # Check out latest stable version (v1.x)
    # Note: Using v1.x because most examples use v1 API
    # (libgpiod-blink and libgpiod-button use v1, only libgpiod-blink-v2 uses v2)
    echo "Checking out latest stable version..."
    LATEST_TAG=$(git tag -l 'v1.*' | sort -V | tail -1)
    if [ -n "$LATEST_TAG" ]; then
        echo "  Using: $LATEST_TAG (v1.x API)"
        git checkout "$LATEST_TAG"
    else
        echo "  Warning: No v1.x tags found, trying v2.x..."
        LATEST_TAG=$(git tag -l 'v2.*' | sort -V | tail -1)
        if [ -n "$LATEST_TAG" ]; then
            echo "  Using: $LATEST_TAG (v2.x API)"
            git checkout "$LATEST_TAG"
        else
            echo "  Warning: No stable tags found, using master branch"
        fi
    fi
fi

echo ""
echo "Configuring libgpiod for ARM cross-compilation..."
echo "  This may take a few minutes..."
echo ""

# Run autogen.sh to generate configure script
# Note: autogen.sh will check for libtool and fail with clear error if missing
# --enable-tools=yes: Build command-line tools (gpiodetect, gpioinfo, etc.)
# --enable-bindings-cxx: Build C++ bindings (optional, but often useful)
# --prefix: Installation directory
# --host: Target architecture for cross-compilation
# CC/CXX: Explicitly set cross-compiler
./autogen.sh \
    --enable-tools=yes \
    --enable-bindings-cxx \
    --prefix="$INSTALL_DIR" \
    --host="$HOST_TRIPLE" \
    CC="${CROSS_PREFIX}gcc" \
    CXX="${CROSS_PREFIX}g++"

echo ""
echo "Building libgpiod library for ARM..."
echo "  Using $(nproc) parallel jobs..."
make -j$(nproc)

echo ""
echo "Installing to $INSTALL_DIR..."
make install

echo ""
echo "=================================================="
echo "libgpiod cross-compilation setup complete!"
echo "=================================================="
echo ""
echo "Installation summary:"
echo "  Headers: $INSTALL_DIR/include/"
echo "  Libraries: $INSTALL_DIR/lib/"
echo "  Binaries: $INSTALL_DIR/bin/"
echo "  pkg-config: $INSTALL_DIR/lib/pkgconfig/"
echo ""

# Display installed version
if [ -f "$INSTALL_DIR/lib/pkgconfig/libgpiod.pc" ]; then
    VERSION=$(pkg-config --modversion "$INSTALL_DIR/lib/pkgconfig/libgpiod.pc" 2>/dev/null || echo "unknown")
    echo "  Version: $VERSION"
    echo ""
fi

echo "You can now build libgpiod examples with PlatformIO:"
echo "  cd $REPO_ROOT"
echo "  pio run -d examples/libgpiod-blink"
echo "  pio run -d examples/libgpiod-blink-v2"
echo "  pio run -d examples/libgpiod-button"
echo ""
