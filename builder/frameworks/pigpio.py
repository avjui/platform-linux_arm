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
pigpio [DEPRECATED - Use lgpio instead]

DEPRECATED: pigpio is superseded by lgpio (by same author Joan).

Joan (pigpio author): "pigpio does not work on the Pi 5, I do not think it can
be made to work. lgpio will work."

Why use lgpio instead:
- Works on ALL Pi models (1-5) including Pi 5
- Future-proof (kernel interface)
- Recommended by Raspberry Pi Foundation
- Easier cross-compilation setup

This framework is kept for LEGACY support only. For new projects, use:
    framework = lgpio

If you absolutely need pigpio features (hardware-timed PWM) on Pi ≤4:
    1. Install ARM toolchain: sudo apt install gcc-arm-linux-gnueabihf
    2. Build from source: https://github.com/joan2937/pigpio
    3. Manual setup required (no automated script provided)

IMPORTANT: pigpio is NOT compatible with Raspberry Pi 5 due to the new RP1 I/O
controller.

Supported boards: Raspberry Pi 1, 2, 3, 4, Zero (NOT Pi 5)

http://abyz.me.uk/rpi/pigpio/
"""

from SCons.Script import DefaultEnvironment
import sys

env = DefaultEnvironment()

# Check board compatibility
board = env.BoardConfig()
mcu = board.get("build.mcu", "").lower()

if "bcm2712" in mcu or "5" in board.get("name", ""):
    sys.stderr.write(
        "\n"
        "ERROR: pigpio does not work on Raspberry Pi 5!\n"
        "\n"
        "Please use the lgpio framework instead:\n"
        "  [env:your_environment]\n"
        "  framework = lgpio\n"
        "\n"
        "lgpio is recommended by pigpio's author (Joan) for all Pi models.\n"
        "See docs/LGPIO_SETUP.md for installation instructions.\n"
        "\n"
    )
    env.Exit(1)

# Warn about deprecation
sys.stderr.write(
    "\n"
    "WARNING: pigpio framework is DEPRECATED.\n"
    "Please consider migrating to lgpio (recommended by pigpio's author).\n"
    "lgpio works on all Pi models (1-5) and is future-proof.\n"
    "\n"
)

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

    LIBS=["pigpio", "pthread"]
)

# Note: pigpio installation is not automated due to deprecation.
# Users must build from source manually if they really need it.
