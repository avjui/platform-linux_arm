# VS Code Tasks for Linux ARM Platform

This directory contains VS Code task configurations for SSH monitoring across different development scenarios.

## Quick Start

**For most users**: Copy `tasks.json` to your project's `.vscode/` folder.

```bash
mkdir -p .vscode
cp examples/vscode/tasks.json .vscode/
```

## Available Task Files

### 1. `tasks.json` (Universal - Recommended)

Works for **all scenarios** by providing both IDE and CLI fallback tasks:

**Primary tasks** (use PlatformIO IDE extension):
- `PlatformIO: Monitor (SSH)`
- `PlatformIO: Upload and Monitor (SSH)`

**Fallback tasks** (for CLI-only or remote dev):
- `PlatformIO: Monitor (SSH) - CLI Fallback`
- `PlatformIO: Upload and Monitor (SSH) - CLI Fallback`

**Use this if:**
- Yes - Using PlatformIO IDE extension (most users)
- Yes - Using Remote Development (Windows/Mac → Linux/ARM server)
- Yes - CLI-only setup
- Yes - Any combination of the above

### 2. `tasks-local.json` (IDE Only)

Optimized for **local development** with PlatformIO IDE extension.

**Use this if:**
- Yes - VS Code + PlatformIO IDE running on same machine
- Yes - Windows, macOS, or Linux local development
- Not using Remote Development

### 3. `tasks-remote.json` (Remote Development)

Optimized for **remote development** scenarios.

**Use this if:**
- Yes - VS Code Remote SSH/WSL/Containers
- Yes - PlatformIO installed on remote server
- Not using PlatformIO IDE extension locally

## Test Matrix Coverage

These tasks are designed to work across all these scenarios:

### Cross-Compilation
1. Yes - Windows IDE (local)
2. Yes - Windows CLI (local)
3. Yes - Ubuntu/Linux IDE (local)
4. Yes - Ubuntu/Linux CLI (local)
5. Yes - Windows IDE → Remote Ubuntu
6. Yes - Windows IDE → Remote ARM
7. Yes - Ubuntu IDE → Remote ARM

### Native Compilation
8. Yes - ARM CLI (directly on Raspberry Pi, etc.)
9. Yes - ARM IDE (VS Code on Raspberry Pi, etc.)

## Usage

### Using the Primary Tasks (IDE Extension)

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select:
   - `PlatformIO: Monitor (SSH)` - Monitor only
   - `PlatformIO: Upload and Monitor (SSH)` - Upload then monitor

### Using the Fallback Tasks (CLI)

If the primary tasks don't work (e.g., remote development without IDE extension):

1. Press `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select:
   - `PlatformIO: Monitor (SSH) - CLI Fallback`
   - `PlatformIO: Upload and Monitor (SSH) - CLI Fallback`

These use login shell (`bash -l`) to ensure PlatformIO is in PATH.

## Troubleshooting

### "pio: command not found" or "platformio: command not found"

**Cause**: PlatformIO not in PATH for the shell session.

**Solutions**:

1. **Use the CLI Fallback tasks** (they use login shell)

2. **Check PlatformIO installation**:
   ```bash
   # On remote server or local terminal
   which pio
   which platformio
   ```

3. **Add to PATH** (Linux/macOS - add to `~/.bashrc` or `~/.zshrc`):
   ```bash
   export PATH="$HOME/.platformio/penv/bin:$PATH"
   ```

4. **For Remote Development**:
   - Ensure PlatformIO is installed on the remote server
   - Install via: `pip install platformio`

### Tasks show but don't execute

**Cause**: PlatformIO IDE extension not installed or disabled.

**Solution**: Install the PlatformIO IDE extension from VS Code marketplace.

### Environment variable not expanded

**Cause**: `${command:pickPlatformIOProjectEnv}` requires PlatformIO extension.

**Solution**: Either:
- Install PlatformIO IDE extension, OR
- Replace `${command:pickPlatformIOProjectEnv}` with your environment name:
  ```json
  "args": ["--environment", "raspberrypi_5"]
  ```

## Customization

### Fixed Environment (No Picker)

Replace `${command:pickPlatformIOProjectEnv}` with your environment:

```json
{
    "args": [
        "--target", "monitor",
        "--environment", "raspberrypi_5"  // Your env name
    ]
}
```

### Windows (PowerShell)

For Windows PowerShell users, replace `bash` with `powershell`:

```json
{
    "command": "powershell",
    "args": ["-Command", "pio run --target monitor"]
}
```

### Keyboard Shortcuts (Optional)

Add to `.vscode/keybindings.json`:

```json
[
    {
        "key": "ctrl+alt+m",
        "command": "workbench.action.tasks.runTask",
        "args": "PlatformIO: Monitor (SSH)"
    }
]
```

## Documentation

- [VSCode Integration Guide](../../docs/VSCODE.md)
- [Platform Documentation](../../README.md)
- [Remote Upload Guide](../../docs/UPLOAD.md)

## Support

Issues? See:
- [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)
- [GitHub Issues](https://github.com/sfo2001/platform-linux_arm/issues)
