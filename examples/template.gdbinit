# GDB Configuration for PlatformIO Remote Debugging
# Copy this file to your project root as .gdbinit
#
# IMPORTANT: Add this line to ~/.config/gdb/gdbinit to allow auto-loading:
#   add-auto-load-safe-path /path/to/your/project/.gdbinit
#
# Or to allow all project .gdbinit files (less secure):
#   set auto-load safe-path /

# Suppress informational messages
set debuginfod enabled off

# Auto-source PlatformIO's .pioinit file
# PlatformIO creates .pioinit with debug commands but doesn't tell GDB to execute it
# This workaround automatically loads it when GDB starts
python
import os
import glob
import sys

def find_latest_pioinit():
    """Return path to the latest .pioinit file, checking common PlatformIO cache locations."""
    home = os.path.expanduser("~")
    candidates = []

    # 1. Standard POSIX (Linux/macOS/WSL)
    candidates.append(os.path.join(home, ".platformio", ".cache"))
    candidates.append(os.path.join(home, ".platformio", ".cache", "tmp"))  # PIO Core 6.x occasionally uses tmp/

    # 2. Windows-native: LOCALAPPDATA is authoritative
    if sys.platform.startswith('win'):
        local_appdata = os.getenv('LOCALAPPDATA')
        roaming_appdata = os.getenv('APPDATA')
        if local_appdata:
            candidates.append(os.path.join(local_appdata, "PlatformIO", ".cache"))
        if roaming_appdata:  # Less common but seen in some installations
            candidates.append(os.path.join(roaming_appdata, "PlatformIO", ".cache"))

    # 3. PlatformIO portable mode (if user set PLATFORMIO_HOME_DIR)
    pio_home = os.getenv("PLATFORMIO_HOME_DIR")
    if pio_home:
        candidates.append(os.path.join(pio_home, ".cache"))

    # Resolve all candidate dirs
    debug_dirs = []
    for base in candidates:
        base = os.path.abspath(os.path.expanduser(base))
        if os.path.isdir(base):
            matches = glob.glob(os.path.join(base, ".piodebug-*"))
            if matches:
                debug_dirs.extend(matches)

    if not debug_dirs:
        return None

    # Select the newest by modification timestamp
    try:
        latest_dir = max(debug_dirs, key=os.path.getmtime)
    except Exception:
        latest_dir = debug_dirs[-1]  # fallback—unlikely but safe

    pioinit = os.path.join(latest_dir, ".pioinit")
    return pioinit if os.path.isfile(pioinit) and os.path.getsize(pioinit) > 0 else None


try:
    pioinit = find_latest_pioinit()

    if pioinit:
        # Ensure POSIX-style separators, required even on Windows GDB
        normalized = pioinit.replace(os.path.sep, "/")
        gdb.execute(f"source {normalized}")
        print(f"[PIO] Loaded PlatformIO .pioinit from: {pioinit}")
    else:
        print("[PIO] Warning: .pioinit not found. Run `pio debug` once to generate it.")

except Exception as e:
    # Avoid showing Python tracebacks to GDB user — keep clean output
    print(f"[PIO] Error loading PlatformIO .pioinit: {str(e)}")

end
