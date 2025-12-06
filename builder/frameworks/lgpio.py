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
lgpio

lgpio is a modern C library for Linux GPIO access, designed as a successor to
deprecated sysfs GPIO and the pigpio library. It uses the GPIO character device
(/dev/gpiochip*) introduced in Linux kernel 4.8.

lgpio works on ALL Raspberry Pi models (1-5) including Pi 5, which removed
support for older GPIO interfaces.

Supersedes pigpio (by same author Joan) - recommended for all new projects.

Installation for cross-compilation:
    Run: ./scripts/setup-lgpio-cross.sh

    This builds lgpio from source for ARM and installs to:
    $HOME/.local/arm-linux-gnueabihf/

For Raspberry Pi 1 (original models), set environment variable:
    export RPI_LGPIO_REVISION=800012

http://abyz.me.uk/lg/lgpio.html
"""

from SCons.Script import DefaultEnvironment
from os.path import isfile, join, expanduser
import sys

env = DefaultEnvironment()

# Detect target architecture (same logic as builder/main.py)
board = env.BoardConfig()
target_arch = board.get("build.arch", "armv7")
if env.GetProjectOption("board_build.arch", None):
    target_arch = env.GetProjectOption("board_build.arch")

is_aarch64 = (target_arch == "aarch64")

# Detect lgpio installation paths
# Priority: 1) User local build, 2) System-wide build, 3) System package
# For correct cross-compilation, prioritize architecture-specific paths first
home = expanduser("~")

# Build architecture-specific search path list
# Put the target architecture's paths FIRST to avoid finding wrong architecture
if is_aarch64:
    # 64-bit build: prioritize aarch64 paths
    lgpio_search_paths = [
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
    lgpio_search_paths = [
        join(home, ".local", "arm-linux-gnueabihf"),  # User-built 32-bit (recommended)
        "/usr/local/arm-linux-gnueabihf",             # System-wide build 32-bit
        "/usr/arm-linux-gnueabihf",                   # Multiarch package location 32-bit
        join(home, ".local", "aarch64-linux-gnu"),    # User-built 64-bit (fallback)
        "/usr/local/aarch64-linux-gnu",               # System-wide build 64-bit
        "/usr/aarch64-linux-gnu",                     # Multiarch package location 64-bit
        "/usr",                                        # Native package fallback
    ]

lgpio_include = None
lgpio_lib = None

for base_path in lgpio_search_paths:
    inc_path = join(base_path, "include")
    lib_path = join(base_path, "lib")
    lib_path_multiarch_armhf = join(base_path, "lib", "arm-linux-gnueabihf")
    lib_path_multiarch_aarch64 = join(base_path, "lib", "aarch64-linux-gnu")

    if isfile(join(inc_path, "lgpio.h")):
        # Check correct architecture's path first
        if is_aarch64:
            # Building for 64-bit, check aarch64 first
            if isfile(join(lib_path_multiarch_aarch64, "liblgpio.so")) or isfile(join(lib_path_multiarch_aarch64, "liblgpio.so.1")):
                lgpio_include = inc_path
                lgpio_lib = lib_path_multiarch_aarch64
                print("Found lgpio at: %s (multiarch aarch64)" % base_path)
                break
        else:
            # Building for 32-bit, check armhf first
            if isfile(join(lib_path_multiarch_armhf, "liblgpio.so")) or isfile(join(lib_path_multiarch_armhf, "liblgpio.so.1")):
                lgpio_include = inc_path
                lgpio_lib = lib_path_multiarch_armhf
                print("Found lgpio at: %s (multiarch armhf)" % base_path)
                break

        # Check standard lib path (native package or architecture-neutral paths only)
        # Skip this fallback for architecture-specific base paths to avoid wrong-arch libraries
        is_arch_specific_path = ("arm-linux-gnueabihf" in base_path or "aarch64-linux-gnu" in base_path)

        if not is_arch_specific_path:
            if isfile(join(lib_path, "liblgpio.so")) or isfile(join(lib_path, "liblgpio.so.1")):
                lgpio_include = inc_path
                lgpio_lib = lib_path
                print("Found lgpio at: %s" % base_path)
                break

if not lgpio_include or not lgpio_lib:
    arch_name = "aarch64 (64-bit)" if is_aarch64 else "armhf (32-bit)"
    bits = "64-bit" if is_aarch64 else "32-bit"
    toolchain = "aarch64-linux-gnu" if is_aarch64 else "arm-linux-gnueabihf"
    dpkg_arch = "arm64" if is_aarch64 else "armhf"

    sys.stderr.write(
        f"ERROR: lgpio library not found for {arch_name} architecture!\n"
        "\n"
        f"Building for: {arch_name}\n"
        "\n"
        f"For {bits} ARM:\n"
        f"  1. Install toolchain: sudo apt install gcc-{toolchain}\n"
        f"  2. Build lgpio for {toolchain}: See docs/LGPIO_SETUP.md\n"
        "\n"
        "Or install system package (requires multiarch setup):\n"
        f"  sudo dpkg --add-architecture {dpkg_arch}\n"
        f"  sudo apt update\n"
        f"  sudo apt install liblgpio-dev:{dpkg_arch}\n"
        "\n"
        "See docs/LGPIO_SETUP.md for complete instructions.\n"
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
        lgpio_include,
        join(env.PioPlatform().get_dir(), "framework-lgpio")
    ],

    LIBPATH=[
        lgpio_lib
    ],

    LIBS=["lgpio"]
)

# Build PWM HAL library
pwm_hal_src = join(env.PioPlatform().get_dir(), "framework-lgpio", "pwm-hal.c")
env.BuildSources(
    join("$BUILD_DIR", "FrameworkLgpioPwmHAL"),
    pwm_hal_src
)
