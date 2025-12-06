# Visual Studio Code Integration

This guide covers using the Linux ARM platform with Visual Studio Code and the PlatformIO IDE extension.

## SSH Monitoring Setup

### Important Note

Partial - **The PlatformIO GUI's built-in "Monitor" button does NOT work with this platform.**

The standard "Monitor" button uses `pio device monitor`, which only supports serial ports. Since this platform uses SSH for remote monitoring, you need custom tasks.

### Quick Setup

1. **Copy tasks to your project**:
   ```bash
   mkdir -p .vscode
   cp ~/.platformio/platforms/linux_arm/examples/vscode/tasks.json .vscode/
   ```

2. **Reload VSCode**

3. **Use the tasks**:
   - Press `Ctrl+Shift+P` → "Tasks: Run Task"
   - Select "PlatformIO: Monitor (SSH)" or "PlatformIO: Upload and Monitor (SSH)"

See the full documentation at: https://github.com/sfo2001/platform-linux_arm/blob/develop/docs/VSCODE.md
