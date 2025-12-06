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
# Target: Upload program to remote target
#

def _upload_handler(target, source, env):
    """Handler for upload target - delegates to platform.on_upload()"""
    platform = env.PioPlatform()
    return platform.on_upload(target, source, env)

target_upload = env.Alias("upload", target_bin, _upload_handler)
AlwaysBuild(target_upload)

#
# Target: Upload and execute tests on remote target
#

def _test_upload_handler(target, source, env):
    """Handler for test upload target - delegates to platform.on_test_upload()"""
    platform = env.PioPlatform()
    # Check if platform has on_test_upload method
    if hasattr(platform, 'on_test_upload'):
        return platform.on_test_upload(target, source, env)
    else:
        # Fallback to regular upload if test upload not implemented
        return platform.on_upload(target, source, env)

# Register the test upload handler
env.Replace(UPLOADTESTCMD=_test_upload_handler)

#
# Target: Monitor remote program via SSH
#

def _monitor_handler(target, source, env) -> int:
    """
    Handle remote program monitoring target.

    Connects to remote target via SSH and runs the program,
    streaming output in real-time (similar to serial monitor for microcontrollers).

    Args:
        target: Build target.
        source: List of source files (binary path).
        env: SCons environment object.

    Returns:
        int: Exit code from remote program execution.

    See Also:
        - Linux_armPlatform.on_monitor: Platform monitor implementation
    """
    platform = env.PioPlatform()
    # Check if platform has on_monitor method
    if hasattr(platform, 'on_monitor'):
        return platform.on_monitor(target, source, env)
    else:
        # Fallback: show instructions if monitor not implemented
        print("\n" + "="*60)
        print("Remote monitoring is not configured.")
        print("="*60)
        print("\nTo monitor your remote program, use one of:")
        print("  1. Enable upload_run_after = true in platformio.ini")
        print("  2. Manually SSH to target: ssh user@host")
        print("="*60 + "\n")
        return 0

# Use AddCustomTarget to properly override PlatformIO's built-in monitor
env.AddCustomTarget(
    name="monitor",
    dependencies=None,
    actions=_monitor_handler,
    title="Monitor",
    description="Monitor remote program via SSH",
    always_build=True
)

# Add a custom SSH monitor target that definitely won't conflict
env.AddCustomTarget(
    name="sshmonitor",
    dependencies=None,
    actions=_monitor_handler,
    title="SSH Monitor",
    description="Monitor remote program via SSH (guaranteed to use custom handler)",
    always_build=True
)

#
# Default targets
#

Default([target_bin])
