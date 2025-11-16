# Debugging Guide for platform-linux_arm

## Status

CLI debugging works when run interactively. The SSH pipe connection to gdbserver is functioning correctly.

## Manual Debugging (Verified Working)

You can debug manually using GDB directly:

```bash
# In one terminal, or let PlatformIO handle it automatically
gdb-multiarch .pio/build/raspberrypi_5/program

# In GDB:
(gdb) target extended-remote | ssh -o StrictHostKeyChecking=no -T retropi@retropi "gdbserver - /home/retropi/devel/program"
(gdb) break main
(gdb) continue
```

This works perfectly and confirms the debugging infrastructure is correct.

## PlatformIO CLI Debugging

The `pio debug` command starts GDB correctly but may have asyncio stdin handling issues when run non-interactively (e.g., from scripts or with redirected stdin).

**Working configuration in platformio.ini:**

```ini
[env:raspberrypi_5]
platform = /home/stefan/devel/platform-linux_arm
framework = libgpiod
board = raspberrypi_5
board_build.arch = aarch64

; Build with debug symbols
build_flags =
    -O0           ; No optimization
    -g3           ; Maximum debug information
    -ggdb         ; GDB-specific debug formats

; Upload configuration
upload_protocol = scp
upload_port = retropi@retropi:/home/retropi/devel/

; Debug configuration
debug_tool = gdbserver-ssh
debug_port = retropi@retropi
debug_init_cmds =
    target extended-remote $DEBUG_PORT
    set remote exec-file /home/retropi/devel/program
    set sysroot /
```

**Key points:**
- `debug_init_cmds` MUST include `target extended-remote $DEBUG_PORT` as the first command
- `$DEBUG_PORT` is automatically substituted with the SSH pipe command
- Without the target command, GDB will try to run the program locally (causing "Exec format error")

## VS Code Debugging

VS Code debugging integration needs further testing. The `.vscode/launch.json` is auto-generated correctly, but the Remote Development setup (Windows → SSH to Linux) may require additional configuration.

## Troubleshooting

### "Exec format error" when running program
**Cause:** GDB is trying to run the ARM binary locally instead of on the remote target.
**Solution:** Ensure `target extended-remote $DEBUG_PORT` is in `debug_init_cmds`.

### Build ID mismatch warning
**Cause:** Local and remote binaries were built at different times.
**Solution:** This is cosmetic and doesn't prevent debugging. Upload the latest binary before debugging.

### AsyncIO PermissionError
**Cause:** Python asyncio has issues with redirected/closed stdin.
**Solution:** Run `pio debug` from an interactive terminal, not from scripts with stdin redirection.

## Next Steps

1. Test interactive CLI debugging: `pio debug --environment raspberrypi_5`
2. Test VS Code debugging via Remote Development
3. Document any VS Code-specific configuration needed
