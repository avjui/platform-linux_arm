# Remote Debugging Example

This example demonstrates remote debugging support for ARM Linux targets using GDB/gdbserver over SSH.

## Overview

Remote debugging allows you to debug ARM Linux applications running on Raspberry Pi (or other ARM SBCs) from your development machine using an IDE like VS Code or CLion. The platform automatically handles:

- SSH connection to target device
- Launching gdbserver on the remote target
- Connecting local GDB to remote gdbserver
- Symbol resolution and source mapping

## Prerequisites

### On Your Development Machine (Host)

1. **Cross-compilation toolchain with GDB**:
   ```bash
   # Linux (Ubuntu/Debian)
   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf gdb-multiarch

   # macOS
   brew tap messense/macos-cross-toolchains
   brew install arm-unknown-linux-gnueabihf

   # For 64-bit ARM (Pi 5, Pi 4 with 64-bit OS)
   # Linux:
   sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu gdb-multiarch

   # macOS:
   brew install aarch64-unknown-linux-gnu
   ```

2. **SSH key authentication** (recommended):
   ```bash
   # Generate SSH key if you don't have one
   ssh-keygen -t ed25519 -C "platformio@yourhost"

   # Copy to target device
   ssh-copy-id pi@raspberrypi.local

   # Test connection
   ssh pi@raspberrypi.local
   ```

3. **PlatformIO IDE** (VS Code extension) or PlatformIO Core

### On Your Target Device (Raspberry Pi)

1. **gdbserver** (usually pre-installed on Raspberry Pi OS):
   ```bash
   # Check if installed
   which gdbserver

   # If not installed:
   sudo apt install gdbserver
   ```

2. **SSH server** running (enabled by default on Raspberry Pi OS)

## Quick Start

### 1. Build with Debug Symbols

Debug builds require special compiler flags to include debugging information:

```bash
# Build for Raspberry Pi 4
pio run -e pi4_ssh_debug
```

The `pi4_ssh_debug` environment includes:
- `-O0`: No optimization (easier debugging)
- `-g3`: Maximum debug information
- `-ggdb`: GDB-specific debug formats

### 2. Upload to Target

Upload the debug build to your Raspberry Pi:

```bash
pio run -e pi4_ssh_debug --target upload
```

This uses the `upload_port` configuration to transfer the binary via SCP.

### 3. Start Debugging

#### Option A: VS Code Debugger (Recommended)

1. Open the project in VS Code
2. Click the "Debug" icon in the sidebar
3. Select the environment (e.g., `pi4_ssh_debug`)
4. Click "Start Debugging" (F5)

The debugger will:
- Connect to your Pi via SSH
- Launch gdbserver with your program
- Attach GDB to the remote process
- Break at `main()` by default

#### Option B: Command-Line Debugging

```bash
pio debug -e pi4_ssh_debug
```

This opens an interactive GDB session connected to your Pi.

## Configuration Options

### Basic Configuration

Add to your `platformio.ini`:

```ini
[env:my_debug_env]
platform = linux_arm
board = raspberrypi_4b

; Build flags for debugging
build_flags =
    -O0           ; No optimization
    -g3           ; Full debug info
    -ggdb         ; GDB-specific format

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Debug configuration
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

## Debug Tools

This platform supports two debug tools:

### 1. `gdbserver-ssh` (Recommended)

Uses SSH tunnel to connect to gdbserver. **This is the default and recommended method.**

**Advantages**:
- Secure (uses SSH authentication)
- No firewall configuration needed
- Automatically starts gdbserver
- Works from anywhere with SSH access

**Configuration**:
```ini
debug_tool = gdbserver-ssh
debug_port = pi@raspberrypi.local
```

**How it works**:
```
[Host] GDB → SSH tunnel → [Target] gdbserver → your_program
```

### 2. `gdb-remote` (Manual Setup)

Direct TCP connection to a manually-started gdbserver.

**Use when**:
- You need more control over gdbserver
- SSH tunneling doesn't work in your environment
- You're debugging an already-running process

**Setup**:

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

## Debugging Workflow

### Setting Breakpoints

#### In VS Code:
- Click in the left gutter next to line numbers
- Red dots appear for breakpoints

#### In GDB CLI:
```gdb
(gdb) break main                  # Break at main function
(gdb) break main.c:42             # Break at line 42
(gdb) break factorial             # Break at function
(gdb) break main.c:42 if i == 5   # Conditional breakpoint
```

### Inspecting Variables

#### In VS Code:
- Variables appear in the "Variables" panel
- Hover over variables in code to see values
- Add expressions to "Watch" panel

#### In GDB CLI:
```gdb
(gdb) print local_var             # Print variable
(gdb) print p1                    # Print struct
(gdb) print p1.x                  # Print struct member
(gdb) print *dynamic_array@5      # Print array
(gdb) x/10x dynamic_array         # Examine memory
```

### Stepping Through Code

#### In VS Code:
- F10: Step Over (next line)
- F11: Step Into (enter function)
- Shift+F11: Step Out (exit function)
- F5: Continue

#### In GDB CLI:
```gdb
(gdb) next      # Step over (don't enter functions)
(gdb) step      # Step into functions
(gdb) finish    # Run until function returns
(gdb) continue  # Continue execution
(gdb) until 50  # Run until line 50
```

### Call Stack

#### In VS Code:
- View in "Call Stack" panel

#### in GDB CLI:
```gdb
(gdb) backtrace       # Show call stack
(gdb) frame 2         # Switch to frame 2
(gdb) up              # Move up one frame
(gdb) down            # Move down one frame
```

### Watching Variables

```gdb
(gdb) watch global_counter        # Break when variable changes
(gdb) rwatch global_counter       # Break when variable is read
(gdb) awatch global_counter       # Break on read or write
```

## Example Debugging Session

Here's a typical debugging session using the provided example:

```bash
# 1. Build with debug symbols
pio run -e pi4_ssh_debug

# 2. Upload to Pi
pio run -e pi4_ssh_debug --target upload

# 3. Start debugger
pio debug -e pi4_ssh_debug
```

In the GDB session:

```gdb
# Set breakpoint at main
(gdb) break main
Breakpoint 1 at 0x1234: file src/main.c, line 89.

# Run the program
(gdb) run
Starting program: /home/pi/debug_example
Breakpoint 1, main (argc=1, argv=0x7efff894) at src/main.c:89

# Inspect variables
(gdb) print local_var
$1 = 42

# Step through code
(gdb) next
94          printf("local_var = %d\n", local_var);

# Continue until next breakpoint
(gdb) continue
Continuing.
...
```

## Architecture-Specific Notes

### 32-bit ARM (Raspberry Pi 1-4 with 32-bit OS)

Uses `arm-linux-gnueabihf-gdb`:

```ini
board = raspberrypi_4b
; No need to specify arch (defaults to armv7)
```

### 64-bit ARM (Raspberry Pi 4/5 with 64-bit OS)

Uses `aarch64-linux-gnu-gdb`:

```ini
board = raspberrypi_5
board_build.arch = aarch64
```

Make sure you have the 64-bit cross-toolchain installed:
```bash
# Linux
sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu gdb-multiarch

# macOS
brew install aarch64-unknown-linux-gnu
```

## Troubleshooting

### "Could not connect to remote target"

**Possible causes**:
1. SSH connection failed
2. gdbserver not installed on target
3. Wrong hostname/IP

**Solutions**:
```bash
# Test SSH connection
ssh pi@raspberrypi.local

# Verify gdbserver on target
ssh pi@raspberrypi.local which gdbserver

# Try IP address instead of hostname
debug_port = pi@192.168.1.100
```

### "No symbol table is loaded"

**Cause**: Binary was not built with debug symbols

**Solution**: Make sure you use debug build flags:
```ini
build_flags = -O0 -g3 -ggdb
```

### "Remote communication error"

**Cause**: gdbserver crashed or connection dropped

**Solutions**:
1. Check target logs: `ssh pi@raspberrypi.local dmesg | tail`
2. Try manual gdbserver to see error messages
3. Restart debugging session

### "Cannot find bounds of current function"

**Cause**: Code was optimized, debug info incomplete

**Solution**: Use `-O0` (no optimization) in `build_flags`

### "Permission denied" when starting gdbserver

**Cause**: Program file not executable

**Solution**: The upload methods should set execute permissions automatically. If not:
```bash
ssh pi@raspberrypi.local chmod +x /home/pi/myapp
```

### GDB cannot find source files

**Cause**: Source file paths don't match

**Solution**: GDB should find sources automatically. If not, set source path:
```ini
debug_init_cmds =
    set substitute-path /old/path /new/path
    directory /path/to/src
```

## Performance Notes

### Debug vs Release Builds

Debug builds (`-O0 -g3`) are:
- **Larger**: 2-5x larger due to debug symbols
- **Slower**: No compiler optimizations
- **Accurate**: Variable values match source code

Release builds (`-O2 -O3`) are:
- **Smaller**: Minimal/no debug information
- **Faster**: Optimized code
- **Harder to debug**: Variables optimized out, code reordered

### Debugging Over Slow Networks

If SSH connection is slow:
1. Use wired Ethernet instead of Wi-Fi
2. Reduce debug info: use `-g` instead of `-g3`
3. Consider building on the target directly (native compilation)

## VS Code Launch Configuration

The platform automatically generates debug configurations, but you can customize `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "platformio-debug",
            "request": "launch",
            "name": "PIO Debug (pi4_ssh_debug)",
            "executable": ".pio/build/pi4_ssh_debug/program",
            "projectEnvName": "pi4_ssh_debug",
            "toolchainBinDir": "",
            "preLaunchTask": {
                "type": "PlatformIO",
                "task": "Pre-Debug"
            },
            "internalConsoleOptions": "openOnSessionStart"
        }
    ]
}
```

## Integration with Other Tools

### Valgrind (Memory Debugging)

Run your program under Valgrind on the target:

```bash
ssh pi@raspberrypi.local
valgrind --leak-check=full /home/pi/myapp
```

### GDB Server for Persistent Debugging

Keep gdbserver running between sessions:

```bash
# On target
gdbserver --multi :2345

# Then attach from host multiple times
```

## Next Steps

- Try different breakpoints in the example code
- Experiment with conditional breakpoints
- Inspect complex data structures
- Debug multi-threaded programs
- Learn advanced GDB commands

## References

- [GDB Documentation](https://sourceware.org/gdb/documentation/)
- [PlatformIO Debugging Guide](https://docs.platformio.org/en/latest/plus/debugging.html)
- [Remote Debugging with GDB](https://developers.redhat.com/blog/2015/04/28/remote-debugging-with-gdb)
- [Raspberry Pi Remote Development](https://www.raspberrypi.com/documentation/computers/remote-access.html)

## Related Examples

- `examples/remote-deployment/` - Upload configurations without debugging
- `examples/wiringpi-blink/` - GPIO example for Pi
- `examples/lgpio-blink/` - Modern GPIO library example
