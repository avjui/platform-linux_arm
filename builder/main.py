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
SCons Build Script for Linux ARM Platform.

This module configures the build environment for ARM Linux targets,
supporting both native compilation on ARM Linux and cross-compilation
from x86_64 hosts.

Features:
    - Automatic toolchain detection (native vs cross-compilation)
    - Architecture-specific toolchain selection (ARMv7 vs AArch64)
    - Build targets: program binary, size calculation, upload, test upload
    - Integration with PlatformIO platform class for uploads and testing

Build Targets:
    - Default: Build program binary
    - size: Calculate and display binary size
    - upload: Upload binary to remote target (delegates to platform.on_upload)
    - test upload: Upload and execute tests (delegates to platform.on_test_upload)

Toolchain Selection:
    - Native ARM Linux: Uses system toolchain (no prefix)
    - Cross-compilation ARMv7: Uses arm-linux-gnueabihf- prefix
    - Cross-compilation AArch64: Uses aarch64-linux-gnu- prefix

Examples:
    Build program:
        $ pio run

    Build and display size:
        $ pio run --target size

    Build and upload:
        $ pio run --target upload

Author: PlatformIO
License: Apache 2.0
"""

import sys
import os
import shutil
from platform import system as get_os_name

from SCons.Script import AlwaysBuild, Default, DefaultEnvironment

from platformio.util import get_systype

env = DefaultEnvironment()

# Add platform directory to sys.path for importing platform_constants
# Use env.PioPlatform().get_dir() instead of __file__ because __file__
# is not defined in SCons execution context (scripts are executed via exec())
platform_dir = env.PioPlatform().get_dir()
if platform_dir not in sys.path:
    sys.path.insert(0, platform_dir)

# Import platform_constants after sys.path is configured
from platform_constants import Architecture, SystemType, ToolchainPrefix


def get_toolchain_prefix(arch: str) -> str:
    """
    Get the appropriate toolchain prefix for the target architecture.
    
    Handles different naming conventions across platforms:
    - Linux (apt):     arm-linux-gnueabihf- / aarch64-linux-gnu-
    - macOS (brew):    arm-linux-gnueabihf- / aarch64-linux-gnu-
    - Windows (ARM):   arm-none-linux-gnueabihf- / aarch64-none-linux-gnu-
    
    Args:
        arch: Target architecture (Architecture.ARMV7 or Architecture.AARCH64)
    
    Returns:
        The first available toolchain prefix found in PATH, or the
        platform-appropriate default if none found.
    """
    if arch == Architecture.AARCH64:
        # AArch64/ARMv8 64-bit toolchain prefixes
        if get_os_name() == "Windows":
            candidates = [
                "aarch64-none-linux-gnu-",   # ARM official (Windows)
                "aarch64-linux-gnu-",         # Alternative
            ]
        else:
            candidates = [
                "aarch64-linux-gnu-",         # System packages (Linux/macOS)
                "aarch64-none-linux-gnu-",    # ARM official
            ]
    else:
        # ARMv7 32-bit toolchain prefixes
        if get_os_name() == "Windows":
            candidates = [
                "arm-none-linux-gnueabihf-",  # ARM official (Windows)
                "arm-linux-gnueabihf-",        # Alternative
            ]
        else:
            candidates = [
                "arm-linux-gnueabihf-",        # System packages (Linux/macOS)
                "arm-none-linux-gnueabihf-",   # ARM official
            ]
    
    # Find first available toolchain in PATH
    for prefix in candidates:
        if shutil.which(prefix + "gcc"):
            return prefix
    
    # Return platform-appropriate default (will fail with clear error if not installed)
    return candidates[0]

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
is_native = SystemType.LINUX_ARM in systype or SystemType.LINUX_AARCH64 in systype

if not is_native:
    # Detect target architecture from board configuration
    board = env.BoardConfig()
    target_arch = board.get("build.arch", Architecture.ARMV7)  # Default to 32-bit for backward compatibility

    # Check if user explicitly set architecture via board_build.arch in platformio.ini
    # This takes precedence over board definition
    if env.GetProjectOption("board_build.arch", None):
        target_arch = env.GetProjectOption("board_build.arch")

    # Pi 4/5 with 64-bit OS use aarch64 architecture
    if target_arch == Architecture.AARCH64:
        toolchain_prefix = get_toolchain_prefix(Architecture.AARCH64)
        env.Replace(_BINPREFIX=toolchain_prefix)
        print("Cross-compiling for ARM Linux (AArch64/ARMv8 64-bit)")
        print(f"Using toolchain prefix: {toolchain_prefix}")
        print("Ensure toolchain is installed:")
        print("  Linux:   sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu")
        print("  macOS:   brew tap messense/macos-cross-toolchains")
        print("           brew install aarch64-unknown-linux-gnu")
        print("  Windows: Download from https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads")
        print("           (aarch64-none-linux-gnu variant)")
    else:
        # Default: 32-bit ARMv7 (backward compatible)
        toolchain_prefix = get_toolchain_prefix(Architecture.ARMV7)
        env.Replace(_BINPREFIX=toolchain_prefix)
        print("Cross-compiling for ARM Linux (ARMv7 32-bit)")
        print(f"Using toolchain prefix: {toolchain_prefix}")
        print("Ensure toolchain is installed:")
        print("  Linux:   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf")
        print("  macOS:   brew tap messense/macos-cross-toolchains")
        print("           brew install arm-unknown-linux-gnueabihf")
        print("  Windows: Download from https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads")
        print("           (arm-none-linux-gnueabihf variant)")

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

def _upload_handler(target, source, env) -> int:
    """
    Handle upload target.

    Delegates to platform.on_upload() for protocol-specific upload logic
    (SCP, rsync, SSH, or manual).

    Args:
        target: Build target.
        source: List of source files (binary path).
        env: SCons environment object.

    Returns:
        int: Exit code from upload operation.

    See Also:
        - Linux_armPlatform.on_upload: Platform upload implementation
    """
    platform = env.PioPlatform()
    return platform.on_upload(target, source, env)

target_upload = env.Alias("upload", target_bin, _upload_handler)
AlwaysBuild(target_upload)

#
# Target: Upload and execute tests on remote target
#

def _test_upload_handler(target, source, env) -> int:
    """
    Handle test upload target.

    Delegates to platform.on_test_upload() for remote test execution
    via SSH, or falls back to regular upload if test upload is not implemented.

    Args:
        target: Build target.
        source: List of source files (test binary path).
        env: SCons environment object.

    Returns:
        int: Exit code from test execution.

    See Also:
        - Linux_armPlatform.on_test_upload: Platform test upload implementation
        - RemoteTestUploader: SSH test uploader implementation
    """
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
