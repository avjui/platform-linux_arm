# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
libgpiod - Official Linux GPIO Character Device Library

libgpiod is the official userspace library for the Linux kernel GPIO subsystem.
It provides a C API for interacting with GPIO chips via the character device
interface (/dev/gpiochip*) introduced in Linux kernel 4.8.

Architecture:
- Direct ioctl() calls to kernel GPIO character device
- File descriptor-based resource management
- Kernel-enforced GPIO line exclusivity (only one consumer at a time)
- No persistent background threads for basic GPIO operations
- Clean resource cleanup on process exit

Compatibility:
- All Raspberry Pi models (1-5)
- Orange Pi, Rock Pi, Odroid, Banana Pi, NanoPi
- Any Linux SBC with kernel 4.8+ and GPIO chardev driver support
- Portable across architectures (ARM, ARM64, x86)

Key Features:
- Guaranteed exclusive access to GPIO lines (kernel-enforced)
- Request-based API (must claim lines before use)
- Support for input, output, edge detection, bias configuration
- Event monitoring for interrupt-driven applications

Important Notes:
1. GPIO State Persistence: By default, libgpiod may revert GPIO lines to their
   default state when the process exits. On Raspberry Pi, enable persistent
   state by adding to /boot/config.txt:
       dtparam=strict_gpiod

2. API Versions: libgpiod has two major API versions:
   - v1.x (legacy): Simpler API, widely deployed
   - v2.x (modern): More flexible, object-oriented design
   Both are supported; v2.x is recommended for new projects.

3. Comparison with Other Libraries:
   - vs lgpio: libgpiod is kernel-standard, lgpio is RPi-focused with multi-protocol
   - vs pigpio: libgpiod is future-proof, pigpio is Pi 1-4 only (no Pi 5)
   - vs WiringPi: libgpiod is maintained, WiringPi is deprecated

Installation for Cross-Compilation:
    See docs/LIBGPIOD_SETUP.md for detailed instructions.

    Quick start:
    # Install cross-compilation toolchain
    sudo apt install gcc-arm-linux-gnueabihf

    # Install libgpiod for target architecture
    sudo dpkg --add-architecture armhf
    sudo apt update
    sudo apt install libgpiod-dev:armhf

    # Or build from source for custom install location

For Native Compilation (on Raspberry Pi):
    sudo apt install libgpiod-dev gpiod

References:
- Official Documentation: https://libgpiod.readthedocs.io/
- Kernel GPIO Documentation: https://www.kernel.org/doc/html/latest/driver-api/gpio/
- Raspberry Pi GPIO White Paper: https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/
- Migration Guide: https://www.embeddedpi.com/documentation/gpio-interfaces/libgpiod-guide

https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/
"""

from SCons.Script import DefaultEnvironment
from os.path import isfile, join, expanduser
from os import environ
import sys

env = DefaultEnvironment()

# Detect target architecture (same logic as builder/main.py)
board = env.BoardConfig()
target_arch = board.get("build.arch", "armv7")
if env.GetProjectOption("board_build.arch", None):
    target_arch = env.GetProjectOption("board_build.arch")

is_aarch64 = (target_arch == "aarch64")

# Detect libgpiod installation paths
# Priority: 1) CI workspace (for Windows CI), 2) User local build, 3) System multiarch, 4) System package
home = expanduser("~")
workspace = environ.get("GITHUB_WORKSPACE", "")  # CI workspace (Windows CI builds use this)

# Build architecture-specific search path list
# Put the target architecture's paths FIRST to avoid finding wrong architecture
if is_aarch64:
    # 64-bit build: prioritize aarch64 paths
    libgpiod_search_paths = [
        join(workspace, ".local", "aarch64-linux-gnu") if workspace else "",  # CI workspace (Windows)
        join(home, ".local", "aarch64-linux-gnu"),    # User-built 64-bit (recommended)
        "/usr/local/aarch64-linux-gnu",               # System-wide build 64-bit
        "/usr/aarch64-linux-gnu",                     # Multiarch package location 64-bit
        join(home, ".local", "arm-linux-gnueabihf"),  # User-built 32-bit (fallback)
        "/usr/local/arm-linux-gnueabihf",             # System-wide build 32-bit
        "/usr/arm-linux-gnueabihf",                   # Multiarch package location 32-bit
        "/usr",                                        # Native package fallback
    ]
else:
    # 32-bit build: prioritize armhf paths
    libgpiod_search_paths = [
        join(workspace, ".local", "arm-linux-gnueabihf") if workspace else "",  # CI workspace (Windows)
        join(home, ".local", "arm-linux-gnueabihf"),  # User-built 32-bit (recommended)
        "/usr/local/arm-linux-gnueabihf",             # System-wide build 32-bit
        "/usr/arm-linux-gnueabihf",                   # Multiarch package location 32-bit
        join(home, ".local", "aarch64-linux-gnu"),    # User-built 64-bit (fallback)
        "/usr/local/aarch64-linux-gnu",               # System-wide build 64-bit
        "/usr/aarch64-linux-gnu",                     # Multiarch package location 64-bit
        "/usr",                                        # Native package fallback
    ]

libgpiod_include = None
libgpiod_lib = None
libgpiod_version = None  # Try to detect v1.x vs v2.x

# Filter out empty strings from search paths
libgpiod_search_paths = [p for p in libgpiod_search_paths if p]

for base_path in libgpiod_search_paths:
    inc_path = join(base_path, "include")
    lib_path = join(base_path, "lib")
    lib_path_multiarch_armhf = join(base_path, "lib", "arm-linux-gnueabihf")
    lib_path_multiarch_aarch64 = join(base_path, "lib", "aarch64-linux-gnu")

    # Check for gpiod.h header
    if isfile(join(inc_path, "gpiod.h")):
        # Check correct architecture's path first
        if is_aarch64:
            # Building for 64-bit, check aarch64 first
            if isfile(join(lib_path_multiarch_aarch64, "libgpiod.so")) or \
               isfile(join(lib_path_multiarch_aarch64, "libgpiod.so.2")) or \
               isfile(join(lib_path_multiarch_aarch64, "libgpiod.so.1")) or \
               isfile(join(lib_path_multiarch_aarch64, "libgpiod.a")):
                libgpiod_include = inc_path
                libgpiod_lib = lib_path_multiarch_aarch64
                print("Found libgpiod at: %s (multiarch aarch64)" % base_path)
                break
        else:
            # Building for 32-bit, check armhf first
            if isfile(join(lib_path_multiarch_armhf, "libgpiod.so")) or \
               isfile(join(lib_path_multiarch_armhf, "libgpiod.so.2")) or \
               isfile(join(lib_path_multiarch_armhf, "libgpiod.so.1")) or \
               isfile(join(lib_path_multiarch_armhf, "libgpiod.a")):
                libgpiod_include = inc_path
                libgpiod_lib = lib_path_multiarch_armhf
                print("Found libgpiod at: %s (multiarch armhf)" % base_path)
                break

        # Check standard lib path as fallback
        # Architecture-specific base paths (e.g., ~/.local/arm-linux-gnueabihf/)
        # provide architecture isolation, so it's safe to check lib/ subdirectory
        if isfile(join(lib_path, "libgpiod.so")) or \
           isfile(join(lib_path, "libgpiod.so.2")) or \
           isfile(join(lib_path, "libgpiod.so.1")) or \
           isfile(join(lib_path, "libgpiod.a")):
            libgpiod_include = inc_path
            libgpiod_lib = lib_path
            print("Found libgpiod at: %s" % base_path)
            break

# Detect libgpiod API version (v1.x vs v2.x) by checking for v2-specific symbols
if libgpiod_include:
    # Try to detect version from header file
    # v2.x has gpiod_line_request struct and gpiod_request_config
    # v1.x has gpiod_chip_open and gpiod_line_request_output
    try:
        with open(join(libgpiod_include, "gpiod.h"), "r") as f:
            header_content = f.read()
            if "gpiod_request_config" in header_content or "gpiod_line_request_output_flags" in header_content:
                libgpiod_version = "v2"
                print("Detected libgpiod API version: v2.x")
            else:
                libgpiod_version = "v1"
                print("Detected libgpiod API version: v1.x")
    except (OSError, UnicodeDecodeError) as e:
        # If we can't detect, assume v1 for backward compatibility
        libgpiod_version = "v1"
        print(f"Could not detect libgpiod API version ({e.__class__.__name__}), assuming v1.x")

if not libgpiod_include or not libgpiod_lib:
    arch_name = "aarch64 (64-bit)" if is_aarch64 else "armhf (32-bit)"
    bits = "64-bit" if is_aarch64 else "32-bit"
    toolchain = "aarch64-linux-gnu" if is_aarch64 else "arm-linux-gnueabihf"
    dpkg_arch = "arm64" if is_aarch64 else "armhf"

    sys.stderr.write(
        f"ERROR: libgpiod library not found for {arch_name} architecture!\n"
        "\n"
        f"Building for: {arch_name}\n"
        "\n"
        "libgpiod is the official Linux kernel GPIO library that works across\n"
        "all Linux ARM SBCs (Raspberry Pi, Orange Pi, Rock Pi, etc.)\n"
        "\n"
        f"For {bits} ARM:\n"
        f"  1. Install cross-compilation toolchain:\n"
        f"       sudo apt install gcc-{toolchain} g++-{toolchain}\n"
        "\n"
        f"  2. Install libgpiod for target architecture (multiarch method):\n"
        f"       sudo dpkg --add-architecture {dpkg_arch}\n"
        f"       sudo apt update\n"
        f"       sudo apt install libgpiod-dev:{dpkg_arch}\n"
        "\n"
        "  3. OR build libgpiod from source:\n"
        "       git clone https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git\n"
        "       cd libgpiod\n"
        "       ./autogen.sh --enable-tools=yes --enable-bindings-cxx \\\\\n"
        f"         --prefix=$HOME/.local/{toolchain} \\\\\n"
        f"         --host={toolchain} CC={toolchain}-gcc CXX={toolchain}-g++\n"
        "       make && make install\n"
        "\n"
        "For native compilation (on Raspberry Pi):\n"
        "  sudo apt install libgpiod-dev gpiod\n"
        "\n"
        "See docs/LIBGPIOD_SETUP.md for complete instructions.\n"
    )
    env.Exit(1)

env.Replace(
    CPPFLAGS=[
        "-O2",
        "-Wall",
        "-Winline",
        "-pipe",
        "-fPIC"
    ]
)

env.Append(
    CPPDEFINES=[
        "_GNU_SOURCE"
    ],

    CPPPATH=[
        libgpiod_include
    ],

    LIBPATH=[
        libgpiod_lib
    ],

    LIBS=["gpiod"]
)

# Add version-specific defines for conditional compilation in user code
if libgpiod_version == "v2":
    env.Append(CPPDEFINES=["LIBGPIOD_V2"])
else:
    env.Append(CPPDEFINES=["LIBGPIOD_V1"])

# Print information about GPIO state persistence
print("")
print("=" * 70)
print("IMPORTANT: GPIO State Persistence")
print("=" * 70)
print("By default, libgpiod may revert GPIO lines to their default state")
print("when your program exits.")
print("")
print("On Raspberry Pi, to enable persistent GPIO state across restarts,")
print("add this line to /boot/config.txt (or /boot/firmware/config.txt):")
print("")
print("    dtparam=strict_gpiod")
print("")
print("Then reboot. See docs/LIBGPIOD_SETUP.md for details.")
print("=" * 70)
print("")
