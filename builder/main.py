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
    # Cross-compilation to ARMv7 (32-bit ARM with hard-float)
    env.Replace(_BINPREFIX="arm-linux-gnueabihf-")
    print("Cross-compiling for ARM Linux (ARMv7)")
    print("Using toolchain prefix: arm-linux-gnueabihf-")
    print("Ensure toolchain is installed:")
    print("  Linux:   sudo apt install gcc-arm-linux-gnueabihf")
    print("  macOS:   brew install arm-linux-gnueabihf-binutils")
    print("  Windows: Install ARM GNU Toolchain from ARM Developer site")

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
