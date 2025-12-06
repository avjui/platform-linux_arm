# GPIO Framework Decision: lgpio as Primary Framework

**Date**: 2025-11-09
**Decision**: Use **lgpio** as the primary GPIO framework for all Raspberry Pi models

## Summary

After research and analysis, we've decided to prioritize **lgpio** over pigpio for this platform. This document explains the rationale.

## Key Finding: lgpio Supersedes pigpio

**From pigpio's own author (Joan)**:
> "pigpio does not work on the Pi 5, I do not think it can be made to work. **lgpio will work.**"

Joan created lgpio specifically as the modern successor to pigpio.

## Compatibility Matrix

| Framework | Pi 1 | Pi 2 | Pi 3 | Pi 4 | Pi 5 | Future Pi | Status |
|-----------|------|------|------|------|------|-----------|---------|
| **lgpio** | ✅* | ✅ | ✅ | ✅ | ✅ | ✅ | **Active** |
| pigpio    | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | Deprecated |
| WiringPi  | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | Legacy |

*Pi 1 (original models) requires `RPI_LGPIO_REVISION` environment variable

## Why lgpio?

### 1. **Universal Compatibility**
- Works on **all** Raspberry Pi models (1-5)
- Only Pi 1 (original A/B models) needs minor workaround
- Future-proof: uses kernel interface (`/dev/gpiochip`)

### 2. **Official Recommendation**
- Recommended by **Joan** (pigpio/lgpio author)
- Recommended by **Raspberry Pi Foundation**
- Modern, maintained, active development

### 3. **Simpler Cross-Compilation**
- Single framework to support
- Cleaner build process
- Less maintenance burden

### 4. **No Hardware Lock-in**
- Kernel interface (not direct register access)
- Works on Pi 5's new RP1 I/O controller
- Will work on future Pi hardware

## What About pigpio?

**pigpio is deprecated but kept for legacy support:**

### pigpio Limitations:
- ❌ Does **NOT** work on Pi 5
- ❌ Won't work on future Pi models
- ❌ Direct register access (hardware-specific)
- ❌ More complex cross-compilation setup

### When to Use pigpio:
Only if you have **specific requirements**:
- Need hardware-timed PWM (unique to pigpio)
- Legacy code that depends on pigpio
- Targeting **only** Pi 4 and earlier
- Willing to manually build from source

## Implementation

### Primary Framework: lgpio

**Location**: `builder/frameworks/lgpio.py`

**Features**:
- Auto-detects lgpio installation paths
- Clear error messages with setup instructions
- Supports user-local builds (`$HOME/.local/arm-linux-gnueabihf`)
- Works with system packages and custom builds

**Setup**:
```bash
./scripts/setup-lgpio-cross.sh
```

### Deprecated Framework: pigpio

**Location**: `builder/frameworks/pigpio.py`

**Status**:
- Marked as DEPRECATED with warning messages
- Blocks Pi 5 usage with clear error
- No automated setup (user must build manually)
- Documentation points to lgpio

## Migration Path

For users currently using pigpio:

### lgpio API is similar but cleaner:

**pigpio**:
```c
gpioInitialise();
gpioSetMode(23, PI_OUTPUT);
gpioWrite(23, 1);
gpioTerminate();
```

**lgpio**:
```c
int h = lgGpiochipOpen(0);
lgGpioClaimOutput(h, 0, 23, 0);
lgGpioWrite(h, 23, 1);
lgGpiochipClose(h);
```

See `docs/LGPIO_SETUP.md` for full migration guide.

## References

1. **Raspberry Pi Forums - GPIO library for new projects**
   https://forums.raspberrypi.com/viewtopic.php?t=373963
   Quote: *"If you stick to older Pi...it is a really good choice, but not if you plan to use it in the future"*

2. **Raspberry Pi Official GPIO White Paper**
   https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/
   Recommends gpiozero with lgpio backend

3. **lgpio GitHub Repository**
   https://github.com/joan2937/lg

4. **lgpio Documentation**
   http://abyz.me.uk/lg/lgpio.html

## Files Changed

1. `builder/frameworks/lgpio.py` - Enhanced with auto-detection and clear errors
2. `builder/frameworks/pigpio.py` - Marked deprecated, added warnings
3. `scripts/setup-lgpio-cross.sh` - Automated lgpio build script
4. `docs/LGPIO_SETUP.md` - Comprehensive setup and migration guide
5. `docs/GPIO_FRAMEWORK_DECISION.md` - This document

## Conclusion

**lgpio is the right choice for this platform:**
- ✅ Works on all Pi models (1-5)
- ✅ Future-proof
- ✅ Officially recommended
- ✅ Simpler to maintain
- ✅ Better cross-compilation support

**Result**: Simplified implementation, better user experience, future-proof platform.
