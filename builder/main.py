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
    Builder for Linux ARM
"""

from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

from platformio.util import get_systype

env = DefaultEnvironment()

env.Replace(
    _BINPREFIX="",
    AR="${_BINPREFIX}ar",
    AS="${_BINPREFIX}as",
    CC="${_BINPREFIX}gcc",
    CXX="${_BINPREFIX}g++",
    GDB="${_BINPREFIX}gdb",
    OBJCOPY="${_BINPREFIX}objcopy",
    RANLIB="${_BINPREFIX}ranlib",
    SIZETOOL="${_BINPREFIX}size",

    SIZEPRINTCMD='$SIZETOOL $SOURCES'
)

# Detect if we're cross-compiling (not native ARM Linux)
systype = get_systype()
is_native = "linux_arm" in systype or "linux_aarch64" in systype

if not is_native:
    # Detect target architecture from board configuration
    board = env.BoardConfig()
    target_arch = board.get("build.arch", "armv7")  # Default to 32-bit for backward compatibility

    # Check if user explicitly set architecture via board_build.arch in platformio.ini
    # This takes precedence over board definition
    if env.GetProjectOption("board_build.arch", None):
        target_arch = env.GetProjectOption("board_build.arch")

    # Pi 4/5 with 64-bit OS use aarch64 architecture
    if target_arch == "aarch64":
        env.Replace(_BINPREFIX="aarch64-linux-gnu-")
        print("Cross-compiling for ARM Linux (AArch64/ARMv8 64-bit)")
        print("Using toolchain prefix: aarch64-linux-gnu-")
        print("Ensure toolchain is installed:")
        print("  Linux:   sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu")
        print("  macOS:   brew tap messense/macos-cross-toolchains")
        print("           brew install aarch64-unknown-linux-gnu")
    else:
        # Default: 32-bit ARMv7 (backward compatible)
        env.Replace(_BINPREFIX="arm-linux-gnueabihf-")
        print("Cross-compiling for ARM Linux (ARMv7 32-bit)")
        print("Using toolchain prefix: arm-linux-gnueabihf-")
        print("Ensure toolchain is installed:")
        print("  Linux:   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf")
        print("  macOS:   brew tap messense/macos-cross-toolchains")
        print("           brew install arm-unknown-linux-gnueabihf")

#
# Target: Build executable program
#

target_bin = env.BuildProgram()

#
# Target: Print binary size
#

target_size = env.Alias("size", target_bin, env.VerboseAction(
    "$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Default targets
#

Default([target_bin])
