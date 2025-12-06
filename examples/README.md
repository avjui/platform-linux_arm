# Platform Examples and Templates

This directory contains example configurations and templates for using platform-linux_arm.

## Files

### template.gdbinit
GDB configuration file for remote debugging with PlatformIO.

**Purpose:** Works around PlatformIO's limitation where it creates `.pioinit` but GDB only auto-loads `.gdbinit`.

**Usage:**
```bash
# Copy to your project root
cp examples/template.gdbinit /path/to/your/project/.gdbinit

# Configure GDB to allow auto-loading (one-time setup)
mkdir -p ~/.config/gdb
echo "add-auto-load-safe-path /path/to/your/project/.gdbinit" >> ~/.config/gdb/gdbinit
```

**Features:**
- Automatically sources PlatformIO's `.pioinit` when GDB starts
- Suppresses debuginfod prompt for cleaner output
- Provides helpful feedback if .pioinit is not found

### VS Code Tasks

#### tasks-remote.json
VS Code tasks for remote development setup (direct path to pio).

**Use when:** Working via VS Code Remote SSH extension.

**Features:**
- SSH Monitor task
- Upload and Monitor task
- Environment-specific variants

#### tasks-cli-pure.json
VS Code tasks using shell to find pio (supports both `pio` and `platformio` commands).

**Use when:** Working on local machine with pio in PATH.

**Features:**
- Automatically detects `pio` or falls back to `platformio`
- Login shell (`bash -l`) ensures proper PATH
- Works across different installation methods

## platformio.ini Configuration

### Basic Debug Configuration

```ini
[env:your_board]
platform = platform-linux_arm
board = raspberrypi_5
board_build.arch = aarch64

; Upload configuration
upload_protocol = scp
upload_port = user@hostname:/remote/path/

; Debug configuration
debug_tool = gdbserver-ssh
debug_port = user@hostname
debug_init_cmds =
    target extended-remote $DEBUG_PORT
    set remote exec-file /remote/path/program
    set sysroot /
```

### Key Points

1. **upload_port format:**
   - Directory: `user@host:/path/to/dir/` (trailing slash)
   - File: `user@host:/path/to/program` (no trailing slash)

2. **debug_init_cmds:**
   - MUST include `target extended-remote $DEBUG_PORT`
   - `$DEBUG_PORT` is automatically replaced with SSH pipe command
   - `set remote exec-file` tells gdbserver which program to run
   - `set sysroot /` prevents slow file transfers

3. **Build flags for debugging:**
   ```ini
   build_flags =
       -O0      ; No optimization
       -g3      ; Maximum debug info
       -ggdb    ; GDB-specific formats
   ```

## Debugging Workflow

1. **Setup (one-time):**
   ```bash
   cp examples/template.gdbinit .gdbinit
   echo "add-auto-load-safe-path $(pwd)/.gdbinit" >> ~/.config/gdb/gdbinit
   ```

2. **Debug:**
   ```bash
   pio debug --environment your_env --interface=gdb
   ```

3. **GDB automatically:**
   - Connects to remote target via SSH
   - Starts gdbserver on remote system
   - Breaks at main
   - Ready for debugging!

## Troubleshooting

See [DEBUGGING.md](../docs/DEBUGGING.md) for comprehensive troubleshooting guide.

### Quick Checks

```bash
# Verify .gdbinit exists
ls -la .gdbinit

# Check GDB safe-path configuration
gdb -q --batch -ex "show auto-load safe-path"

# Test SSH connection
ssh user@hostname "which gdbserver"

# Verify uploaded binary exists
ssh user@hostname "ls -la /remote/path/program"
```
