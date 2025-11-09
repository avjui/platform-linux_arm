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
WiringPi (GC2 Fork)

WiringPi is a GPIO access library written in C for the BCM2835+ used in the
Raspberry Pi. It's designed to be familiar to people who have used the Arduino
"wiring" system.

Originally created by Gordon Henderson (deprecated 2019), now maintained by
the GC2 (Grazer Computer Club) community with Raspberry Pi 5 support.

NOTE: On Pi 5, GCLK functionality is not supported due to RP1 chip documentation
      limitations. For full Pi 5 support, consider using the lgpio framework.

Installation:
    sudo apt install wiringpi

GC2 Fork: https://github.com/WiringPi/WiringPi
Original: http://wiringpi.com (deprecated)
"""

from SCons.Script import DefaultEnvironment
from os.path import isfile, join, isdir
import sys

env = DefaultEnvironment()

# Detect WiringPi installation paths
# Priority: 1) System package, 2) User local build
wiringpi_search_paths = [
    "/usr",                           # System package (apt install wiringpi)
    "/usr/local",                     # Manual installation
]

wiringpi_include = None
wiringpi_lib = None

for base_path in wiringpi_search_paths:
    inc_path = join(base_path, "include")
    lib_path = join(base_path, "lib")

    # Check for wiringPi.h header and library
    if isfile(join(inc_path, "wiringPi.h")) and \
       (isfile(join(lib_path, "libwiringPi.so")) or isfile(join(lib_path, "libwiringPi.a"))):
        wiringpi_include = inc_path
        wiringpi_lib = lib_path
        print("Found WiringPi at: %s" % base_path)
        break

if not wiringpi_include or not wiringpi_lib:
    sys.stderr.write(
        "ERROR: WiringPi library not found!\n"
        "\n"
        "Please install WiringPi (GC2 fork for Pi 5 support):\n"
        "  sudo apt install wiringpi\n"
        "\n"
        "Or build from source:\n"
        "  git clone https://github.com/WiringPi/WiringPi.git\n"
        "  cd WiringPi\n"
        "  ./build debian\n"
        "  sudo apt install ./wiringpi-*.deb\n"
        "\n"
        "NOTE: WiringPi currently requires building directly on a Raspberry Pi.\n"
        "      Cross-compilation is not supported.\n"
        "      For cross-compilation, use the lgpio framework instead.\n"
        "\n"
        "See README.md for details.\n"
    )
    env.Exit(1)

env.Replace(
    CPPFLAGS=[
        "-O2",
        "-Wformat=2",
        "-Wall",
        "-Winline",
        "-pipe",
        "-fPIC"
    ],

    LIBS=["pthread", "wiringPi"]
)

env.Append(
    CPPDEFINES=[
        "_GNU_SOURCE"
    ],

    CPPPATH=[
        wiringpi_include
    ],

    LIBPATH=[
        wiringpi_lib
    ]
)
