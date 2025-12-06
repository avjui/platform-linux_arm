# Remote Debugging Guide

**Platform**: Linux ARM (Raspberry Pi, Orange Pi)
**Feature**: GDB Remote Debugging over SSH
**Status**: Implemented | Testing Pending (Requires Hardware)
**Related**: Issue #35, examples/remote-debugging/

> **Quick Start:** For VS Code-specific setup, IntelliSense configuration, and troubleshooting, see **[VSCODE.md](VSCODE.md)** - Complete VS Code integration guide.

---

## Security Note for Remote Debugging

**Security Considerations**:

Remote debugging uses SSH with GDB to connect to target devices. Ensure secure practices:

- **SSH Keys**: Use secure SSH keys (see [SECURITY.md](../SECURITY.md))
- **Network Security**: Use trusted networks only (avoid public WiFi)
- **User Permissions**: Debug sessions run with target user permissions
- **Environment**: Use remote debugging in development/testing only, not production

**Debug sessions expose**:
- Full process memory access
- Ability to modify program state
- Potential information disclosure

**Best Practices**:
- Only debug on development/test hardware
- Use VPN or SSH tunnels for remote debugging over untrusted networks
- Disable debug capabilities in production builds
- Verify debug target identity before connecting

For comprehensive security guidelines, see [SECURITY.md](../SECURITY.md).

---

## Overview

This platform supports IDE-integrated remote debugging of ARM Linux applications using GDB and gdbserver over SSH. This is the industry-standard approach for debugging userland Linux applications on embedded ARM devices.

### Why Remote Debugging?

Unlike microcontroller platforms that run bare-metal firmware and debug via JTAG/SWD, ARM Linux platforms run full operating systems:

- **Applications run as userland processes** (not firmware)
- **SSH access is standard** on Linux systems
- **gdbserver is the industry standard** for Linux remote debugging
- **Cross-compiled binaries cannot run on host** x86_64 development machines

The debugging workflow differs fundamentally from embedded platforms:

| Platform Type | Debug Method | Transport |
|---------------|--------------|-----------|
| Embedded (ESP32, STM32) | JTAG/SWD + OpenOCD | Hardware debug probe |
| ARM Linux (Raspberry Pi) | gdbserver | SSH tunnel |

---

## Features

### Implemented

- **SSH-tunneled debugging** - Secure connection using existing SSH authentication
- **Direct TCP debugging** - Manual gdbserver setup for advanced scenarios
- **Cross-architecture support** - Automatic GDB selection for ARMv7 (32-bit) and AArch64 (64-bit)
- **IDE integration** - Works with VS Code, CLion, and other PlatformIO-compatible IDEs (see [VSCODE.md](VSCODE.md) for complete VS Code guide)
- **Automatic setup** - Platform handles gdbserver connection and symbol loading
- **Zero target setup** - Uses system gdbserver (pre-installed on Raspberry Pi OS)
- **Configuration reuse** - Leverages existing upload configuration (SSH host, port, keys)
- **Board support** - Debug configurations for all supported boards

### Testing Status

**Validation Completed:**
- Python syntax validation
- JSON schema validation
- Code review and design verification

**Pending Testing (Requires Hardware):**
- 32-bit ARMv7 debugging (Raspberry Pi 1-4)
- 64-bit AArch64 debugging (Raspberry Pi 5, Pi 4 with 64-bit OS)
- VS Code debug session integration
- CLion debug session integration
- Breakpoint and stepping operations
- Variable inspection and watch expressions
- Call stack analysis

**Hardware Requirements for Testing:**
- Raspberry Pi (any model, preferably Pi 4 or Pi 5)
- Cross-compilation toolchain with GDB on development machine
- SSH access to target
- Network connection between host and target

---

## Quick Start

### Prerequisites

#### PlatformIO GDB Integration Setup

**Required: .gdbinit configuration**

PlatformIO creates a `.pioinit` file with debug initialization commands, but GDB only auto-loads files named `.gdbinit`. This configuration ensures GDB automatically executes PlatformIO's debug setup.

**1. Copy template .gdbinit to your project:**
```bash
cp examples/template.gdbinit /path/to/your/project/.gdbinit
```

**2. Configure GDB to allow auto-loading (one-time setup):**
```bash
mkdir -p ~/.config/gdb
echo "add-auto-load-safe-path /path/to/your/project/.gdbinit" >> ~/.config/gdb/gdbinit
```

Alternative (less secure, allows all projects):
```bash
echo "set auto-load safe-path /" >> ~/.config/gdb/gdbinit
```

**Why this is required**: PlatformIO generates `.pioinit` but GDB security settings only auto-load `.gdbinit` files. The template `.gdbinit` file sources PlatformIO's `.pioinit` automatically when GDB starts.

#### On Development Machine (Host)

**Cross-compilation toolchain with GDB:**

```bash
# Linux (Ubuntu/Debian) - 32-bit ARM
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf gdb-multiarch

# Linux - 64-bit ARM
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu gdb-multiarch

# macOS
brew tap messense/macos-cross-toolchains
brew install arm-unknown-linux-gnueabihf      # 32-bit
brew install aarch64-unknown-linux-gnu        # 64-bit
```

**SSH key authentication** (recommended):

```bash
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "platformio@yourhost"

# Copy to target device
ssh-copy-id pi@raspberrypi.local

# Test connection
ssh pi@raspberrypi.local
```

#### On Target Device (Raspberry Pi)

**gdbserver** (usually pre-installed on Raspberry Pi OS):

```bash
# Check if installed
which gdbserver

# If not installed
sudo apt install gdbserver
```

**SSH server** (enabled by default on Raspberry Pi OS)

### Configuration

Add to your `platformio.ini`:

```ini
[env:debug]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio

; Build with debug symbols
build_flags =
    -O0           ; No optimization (easier debugging)
    -g3           ; Maximum debug information
    -ggdb         ; GDB-specific debug formats

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Debug configuration
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local
```

### Usage

```bash
# 1. Build with debug symbols
pio run -e debug

# 2. Upload to target
pio run -e debug --target upload

# 3. Start debugging
pio debug -e debug
```

---

## Debug Tools

The platform provides two debug tools:

### 1. gdbserver-ssh (Recommended)

Uses SSH tunnel to connect GDB to gdbserver. **This is the default and recommended method.**

**Advantages:**
- Secure (uses SSH authentication)
- No firewall configuration needed
- Automatically starts gdbserver
- Works from anywhere with SSH access
- Zero exposed network ports

**Configuration:**

```ini
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local

; Optional: Custom SSH port
; debug_ssh_port = 2222

; Optional: SSH key file
; debug_ssh_key = ~/.ssh/id_ed25519
```

**How it works:**

```
[Host] GDB → SSH tunnel → [Target] gdbserver → your_program
```

The platform automatically executes:

```bash
ssh -T pi@raspberrypi.local gdbserver - /home/pi/myapp
```

### 2. gdb-remote (Manual Setup)

Direct TCP connection to manually-started gdbserver.

**Use when:**
- You need more control over gdbserver
- SSH tunneling doesn't work in your environment
- You're debugging an already-running process

**Setup:**

1. SSH to target and start gdbserver manually:
   ```bash
   ssh pi@raspberrypi.local
   gdbserver :2345 /home/pi/myapp
   ```

2. Configure PlatformIO:
   ```ini
   debug_tool = gdb-remote
   debug_port = raspberrypi.local:2345
   ```

3. Start debugging:
   ```bash
   pio debug
   ```

---

## Architecture Support

The platform automatically selects the correct GDB based on target architecture:

| Architecture | Board Examples | GDB Command |
|-------------|----------------|-------------|
| ARMv7 (32-bit) | Pi 1-4, Orange Pi Zero | `arm-linux-gnueabihf-gdb` |
| AArch64 (64-bit) | Pi 5, Pi 4 with 64-bit OS | `aarch64-linux-gnu-gdb` |
| Native ARM | Building on Pi itself | `gdb` (system GDB) |

### 32-bit ARMv7 (Default)

All boards default to 32-bit for compatibility:

```ini
[env:pi4_debug]
board = raspberrypi_4b
; No arch specification needed - defaults to armv7
```

### 64-bit AArch64 (Optional)

For Pi 4/5 with 64-bit OS:

```ini
[env:pi5_debug_64bit]
board = raspberrypi_5
board_build.arch = aarch64  ; Enable 64-bit
```

**Requirements:**
- 64-bit Raspberry Pi OS on target
- 64-bit cross-toolchain on host

---

## Configuration Options

### Basic Configuration

```ini
[env:debug]
platform = linux_arm
board = raspberrypi_4b

; Debug build flags (REQUIRED)
build_flags = -O0 -g3 -ggdb

; Upload configuration (reused by debug)
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Debug tool selection
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local
```

### Advanced Configuration

#### Custom SSH Port

```ini
upload_ssh_port = 2222
debug_ssh_port = 2222
```

#### Custom SSH Key

```ini
upload_ssh_key = ~/.ssh/my_pi_key
debug_ssh_key = ~/.ssh/my_pi_key
```

#### Custom Remote Path

The remote path is extracted from `upload_port`. You can also set it explicitly:

```ini
debug_prog_path = /home/pi/myapp
```

#### Custom GDB Commands

Add initialization commands to run when GDB starts:

```ini
debug_init_cmds =
    set print pretty on
    set pagination off
    set non-stop on
```

#### Different Upload and Debug Targets

```ini
; Upload to one device
upload_port = pi@build-server.local:/tmp/myapp

; Debug on different device
debug_port = pi@test-device.local
debug_prog_path = /tmp/myapp
```

---

## IDE Integration

### VS Code

The platform automatically generates debug configurations for VS Code.

> **Note:** For comprehensive VS Code setup, IntelliSense configuration, build tasks, and detailed troubleshooting, see [VSCODE.md](VSCODE.md).

**Quick Workflow:**

1. Open project in VS Code
2. Click "Debug" icon in sidebar
3. Select environment (e.g., `debug`)
4. Click "Start Debugging" (F5)

**Debug Controls:**

- **F5**: Continue
- **F10**: Step Over
- **F11**: Step Into
- **Shift+F11**: Step Out
- **Click line gutter**: Set breakpoint

**Panels:**

- **Variables**: Inspect variable values
- **Watch**: Add expressions to monitor
- **Call Stack**: View function call hierarchy
- **Debug Console**: Execute GDB commands

### CLion

CLion supports PlatformIO debugging via the PlatformIO plugin.

**Setup:**

1. Install PlatformIO plugin
2. Open project
3. Select run configuration
4. Click debug icon

### Command-Line (GDB)

```bash
pio debug -e debug

# GDB commands:
(gdb) break main              # Set breakpoint at main
(gdb) break main.c:42         # Set breakpoint at line 42
(gdb) run                     # Start program
(gdb) next                    # Step over
(gdb) step                    # Step into
(gdb) print local_var         # Inspect variable
(gdb) backtrace               # View call stack
(gdb) continue                # Continue execution
(gdb) quit                    # Exit debugger
```

---

## Implementation Details

### Platform Components

#### platform.py

**configure_debug_session(debug_config):**
- Detects target architecture from board configuration
- Selects appropriate GDB (arm-linux-gnueabihf-gdb or aarch64-linux-gnu-gdb)
- Builds SSH command for gdbserver-ssh mode
- Configures GDB initialization commands
- Returns debug configuration dict

**get_boards(id_=None):**
- Overrides parent to inject debug configurations
- Calls `_add_debug_to_board()` for each board
- Returns boards with debug tools added

**_add_debug_to_board(board):**
- Adds debug tool configurations to board manifest
- Sets default debug tool to `gdbserver-ssh`
- Configures init commands and extra commands

#### platform.json

```json
{
  "debug": {
    "tools": {
      "gdbserver-ssh": {
        "server": {
          "package": null,
          "executable": null,
          "arguments": []
        }
      },
      "gdb-remote": {
        "server": {
          "package": null,
          "executable": null,
          "arguments": []
        }
      }
    }
  }
}
```

#### Board Definitions

Each board JSON file includes:

```json
{
  "debug": {
    "default_tool": "gdbserver-ssh",
    "tools": {
      "gdbserver-ssh": { ... },
      "gdb-remote": { ... }
    }
  }
}
```

Updated boards:
- `boards/raspberrypi_4b.json`
- `boards/raspberrypi_5.json`
- `boards/orangepi_zero.json`

### GDB Protocol

The implementation uses GDB's remote protocol:

1. **Host GDB** connects to **target gdbserver**
2. **gdbserver** controls the target process
3. **GDB** sends commands (breakpoints, step, continue, etc.)
4. **gdbserver** responds with program state

For SSH tunneling, the connection is:

```
GDB → SSH stdin/stdout → gdbserver
```

Using the `target extended-remote | ssh ...` syntax.

---

## Troubleshooting

### Common Issues

#### "Could not connect to remote target"

**Possible causes:**
1. SSH connection failed
2. gdbserver not installed on target
3. Wrong hostname/IP

**Solutions:**

```bash
# Test SSH connection
ssh pi@raspberrypi.local

# Verify gdbserver on target
ssh pi@raspberrypi.local which gdbserver

# Try IP address instead of hostname
debug_port = pi@192.168.1.100
```

#### "No symbol table is loaded"

**Cause:** Binary was not built with debug symbols

**Solution:** Use debug build flags:

```ini
build_flags = -O0 -g3 -ggdb
```

#### "Remote communication error"

**Cause:** gdbserver crashed or connection dropped

**Solutions:**

1. Check target logs:
   ```bash
   ssh pi@raspberrypi.local dmesg | tail
   ```

2. Try manual gdbserver to see error messages:
   ```bash
   ssh pi@raspberrypi.local
   gdbserver :2345 /home/pi/myapp
   ```

3. Restart debugging session

#### "Cannot find bounds of current function"

**Cause:** Code was optimized, debug info incomplete

**Solution:** Use `-O0` (no optimization) in `build_flags`

#### "Permission denied" when starting gdbserver

**Cause:** Program file not executable

**Solution:** Upload methods should set execute permissions automatically. If not:

```bash
ssh pi@raspberrypi.local chmod +x /home/pi/myapp
```

#### GDB cannot find source files

**Cause:** Source file paths don't match

**Solution:** GDB should find sources automatically. If not, set source path:

```ini
debug_init_cmds =
    set substitute-path /old/path /new/path
    directory /path/to/src
```

#### Exec format error when running program

**Symptom:**
```
/bin/bash: cannot execute binary file: Exec format error
```

**Cause:** GDB attempting to run the ARM binary locally instead of on the remote target.

**Solution:**
1. Verify `.gdbinit` exists in project root
2. Check GDB is allowed to load it (see Quick Start Prerequisites)
3. Ensure `target extended-remote $DEBUG_PORT` is in `debug_init_cmds`

#### GDB does not stop at main automatically

**Symptom:** GDB starts but does not execute .pioinit commands.

**Cause:** .gdbinit not being auto-loaded due to GDB security settings.

**Solution:**
```bash
# Check if safe-path is configured
gdb -q --batch -ex "show auto-load safe-path"

# Add project to safe-path
echo "add-auto-load-safe-path $(pwd)/.gdbinit" >> ~/.config/gdb/gdbinit
```

#### "The program is not being run"

**Symptom:** Typing `continue` displays "The program is not being run".

**Cause:** Not connected to remote target.

**Solution:** Manually source .pioinit:
```gdb
(gdb) source ~/.platformio/.cache/.piodebug-XXXXX/.pioinit
```
Then verify .gdbinit configuration as described above.

#### AsyncIO PermissionError

**Symptom:**
```
PermissionError: [Errno 1] Operation not permitted
```

**Cause:** Python asyncio has issues with redirected or closed stdin.

**Impact:** Cosmetic only. Debugging functionality continues to work.

**Solution:** Run `pio debug` from an interactive terminal rather than from scripts with stdin redirection.

### Debug Logging

Enable verbose debug output:

```bash
# Set environment variable
export PLATFORMIO_DEBUG=1

# Run debug session
pio debug -e debug
```

---

## Common Warnings

The following warnings may appear during debugging sessions. These are typically harmless and do not prevent debugging functionality.

### Build ID Mismatch

**Warning message:**
```
Warning: Build ID mismatch between current exec-file ... and automatically determined exec-file ...
```

**Cause**: Local and remote binaries differ slightly due to timestamps or build IDs.

**Impact**: Cosmetic only. Debugging functionality remains intact.

**Solution**: Upload a fresh binary before debugging to eliminate this warning.

### File Not Found

**Warning message:**
```
Warning: ../sysdeps/aarch64/dl-start.S:22: Datei oder Verzeichnis nicht gefunden
```

**Cause**: GDB attempting to display source code for C library internals on the remote system.

**Impact**: None. Application source code debugging functions normally.

**Solution**: This is expected behavior when debugging without remote system source packages. The warning can be safely ignored.

### File Transfer Performance

**Warning message:**
```
Warning: File transfers from remote targets can be slow. Use "set sysroot" to access files locally instead.
```

**Cause**: GDB downloading library debug symbols from the remote target.

**Impact**: Initial connection may be slower (one-time per session).

**Solution**: Add `set sysroot /` to `debug_init_cmds` (already included in platform examples).

### Debuginfod Prompt

**Warning message:**
```
Enable debuginfod for this session? (y or [n])
```

**Cause**: GDB requesting permission to auto-download debug symbols.

**Impact**: None when using the template .gdbinit file (disables this prompt).

**Solution**: The template .gdbinit includes `set debuginfod enabled off` to suppress this prompt.

### Exit Warning

**Warning message:**
```
(gdb) quit
Warning! Undefined pio_reset_run_target command
Unknown monitor command.
```

**Cause**: GDB cleanup attempting to execute PlatformIO reset command.

**Impact**: Cosmetic only. Session exits cleanly after this message.

**Solution**: This warning is harmless and can be ignored.

---

## Testing Guide

### For Contributors Testing This Feature

**Test Environment:**

```bash
# Development machine (Ubuntu 22.04)
sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf gdb-multiarch

# Target device (Raspberry Pi OS)
- Raspberry Pi 4 Model B (4GB RAM)
- Raspberry Pi OS (32-bit or 64-bit)
- gdbserver installed
- SSH enabled
```

**Test Scenarios:**

1. **32-bit ARMv7 Debugging:**
   ```bash
   cd examples/remote-debugging
   pio run -e pi4_ssh_debug
   pio run -e pi4_ssh_debug --target upload
   pio debug -e pi4_ssh_debug
   ```
   - Verify GDB connects successfully
   - Set breakpoint at `main`
   - Run program, verify breakpoint hit
   - Inspect variables, step through code
   - Exit cleanly

2. **64-bit AArch64 Debugging (Pi 5):**
   ```bash
   pio run -e pi5_debug
   pio run -e pi5_debug --target upload
   pio debug -e pi5_debug
   ```
   - Verify `aarch64-linux-gnu-gdb` is used
   - Test same workflow as 32-bit

3. **VS Code Integration:**
   - Open project in VS Code
   - Select debug environment
   - Click "Start Debugging" (F5)
   - Verify debug session starts
   - Test breakpoints, stepping, variable inspection

4. **Manual gdbserver Mode:**
   ```bash
   # On target
   ssh pi@raspberrypi.local
   gdbserver :2345 /home/pi/program

   # On host (update platformio.ini to use gdb-remote)
   pio debug
   ```

**Expected Results:**
- GDB connects to target
- Breakpoints work
- Stepping through code works
- Variable inspection works
- Call stack displayed correctly
- Debug session exits cleanly

**Report Issues:**
- Python errors or exceptions
- Connection failures
- GDB protocol errors
- IDE integration problems

---

## Examples

### Complete Working Example

See `examples/remote-debugging/` for a comprehensive example with:

- 8 debugging scenarios (variable inspection, structs, arrays, recursion, loops, etc.)
- 7 platformio.ini configurations
- Comprehensive README with setup guide
- 200+ lines of educational C code

### Configuration Examples

#### Basic SSH Debugging

```ini
[env:basic]
platform = linux_arm
board = raspberrypi_4b
build_flags = -O0 -g3 -ggdb
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local
```

#### Custom SSH Port and Key

```ini
[env:custom_ssh]
platform = linux_arm
board = raspberrypi_4b
build_flags = -O0 -g3 -ggdb
upload_protocol = scp
upload_port = pi@192.168.1.100:/home/pi/myapp
upload_ssh_port = 2222
upload_ssh_key = ~/.ssh/pi_key
debug_tool = gdbserver-ssh
debug_port = pi@192.168.1.100
debug_ssh_port = 2222
debug_ssh_key = ~/.ssh/pi_key
```

#### Manual gdbserver

```ini
[env:manual]
platform = linux_arm
board = raspberrypi_4b
build_flags = -O0 -g3 -ggdb
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp
debug_tool = gdb-remote
debug_port = raspberrypi.local:2345
```

#### 64-bit Debugging (Pi 5)

```ini
[env:pi5_64bit]
platform = linux_arm
board = raspberrypi_5
board_build.arch = aarch64
build_flags = -O0 -g3 -ggdb
upload_protocol = scp
upload_port = pi@raspberrypi5.local:/home/pi/myapp
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi5.local
```

---

## Performance Notes

### Debug vs Release Builds

| Build Type | Optimization | Size | Speed | Debuggability |
|-----------|-------------|------|-------|---------------|
| Debug (`-O0 -g3`) | None | Large | Slow | Full |
| Release (`-O2`) | Medium | Medium | Fast | Limited |
| Release (`-O3`) | High | Small | Fastest | Minimal |

**Recommendations:**
- **Development**: Use debug builds for accurate debugging
- **Production**: Use release builds for performance
- **Profiling**: Use `-O2 -g` for optimized code with symbols

### Network Performance

Debugging over slow networks:
1. Use wired Ethernet instead of Wi-Fi
2. Reduce debug info: use `-g` instead of `-g3`
3. Consider building on the target directly (native compilation)

---

## Related Documentation

- **Issue**: [#35 - Remote Debugging Support](https://github.com/sfo2001/platform-linux_arm/issues/35)
- **Example**: `examples/remote-debugging/README.md`
- **Upload**: `docs/UPLOAD.md`
- **PlatformIO Debug**: https://docs.platformio.org/en/latest/plus/debugging.html
- **GDB Documentation**: https://sourceware.org/gdb/documentation/
- **Red Hat GDB Guide**: https://developers.redhat.com/blog/2015/04/28/remote-debugging-with-gdb

---

## Future Enhancements

Potential improvements for future development:

1. **Automatic deployment before debug** - Upload binary if out of date
2. **Multi-threaded debugging** - Better support for pthread programs
3. **Core dump analysis** - Load and analyze core dumps from crashes
4. **Python script integration** - GDB Python API for custom commands
5. **Valgrind integration** - Memory debugging with Valgrind
6. **perf integration** - Performance profiling integration

---

## See Also

- **[General Troubleshooting](TROUBLESHOOTING.md)** - Platform-wide issues and FAQs
- **[Upload Guide](UPLOAD.md)** - Deployment and transfer troubleshooting
- **[Remote Testing](REMOTE_TESTING.md)** - Test execution on target hardware
- **[VS Code Setup](VSCODE.md)** - IDE integration and IntelliSense configuration
- **[Testing Guide](TESTING.md)** - Test framework integration

---

**Status**: Implemented | Functional Testing Pending
**Last Updated**: 2025-11-16
**Maintainer**: Platform Linux ARM Team
**Feedback**: https://github.com/sfo2001/platform-linux_arm/issues/35
