# GPIO Framework Decision: Dual-Framework Strategy

**Date**: 2025-11-14
**Previous Decision**: lgpio as primary framework (2025-11-09)
**Updated Decision**: Implement **libgpiod** and **lgpio** as dual primary frameworks with complementary strengths

## Executive Summary

After comprehensive research and fact-checking, we've decided to support **two primary frameworks** with different target use cases:

1. **libgpiod** → Universal Linux standard (all SBCs, system daemons, production)
2. **lgpio** → Raspberry Pi convenience (multi-protocol, rapid development)

Both frameworks work on all Raspberry Pi models including Pi 5. Legacy frameworks (pigpio, WiringPi) remain available but are deprecated.

## Research Methodology

This decision was reached through:
- Analysis of official documentation and whitepapers
- Verification of claims against primary sources
- Community feedback from forums and issue trackers
- Practical testing considerations
- Fact-checking to avoid overstated claims

## Framework Analysis

### libgpiod: The Universal Standard

#### ✅ Verified Strengths

1. **Official Linux Kernel Standard**
   - Maintained by Linux kernel developers
   - Uses character device interface (`/dev/gpiochip*`) introduced in kernel 4.8+
   - Documented in official kernel documentation
   - **Source**: https://www.kernel.org/doc/html/latest/driver-api/gpio/

2. **Kernel-Enforced GPIO Exclusivity**
   - When a GPIO line is requested, kernel prevents other processes from claiming it
   - Quote from Raspberry Pi whitepaper: "One related feature of libgpiod is that it guarantees exclusivity whilst the GPIO is claimed, which none of the other libraries do."
   - **Source**: https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/

3. **Universal SBC Support**
   - Works on any Linux SBC with GPIO chardev driver
   - Not Raspberry Pi-specific
   - Tested on: Raspberry Pi, Orange Pi, Rock Pi, Odroid, NanoPi
   - **Source**: https://hub.libre.computer/t/how-to-use-libgpiod-on-libre-computer-boards/73

4. **Future-Proof Architecture**
   - Uses kernel interface (not direct register access)
   - Will work on all future Raspberry Pi models
   - Already works on Pi 5 with RP1 I/O controller

#### ⚠️ Important Caveats

1. **GPIO State Persistence**
   - By default, GPIO lines may revert to default state on process exit
   - Raspberry Pi requires `dtparam=strict_gpiod` in `/boot/config.txt` for persistence
   - This is different from lgpio/pigpio/WiringPi behavior
   - **Source**: https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/

2. **Threading Architecture**
   - No documented "zero-thread" guarantee
   - More accurate: Uses direct `ioctl()` calls without background thread management for basic GPIO
   - Event monitoring requires application-managed polling

3. **GPIO Only**
   - libgpiod handles GPIO only (not I2C/SPI/PWM)
   - Must use separate libraries for other protocols

4. **API Version Confusion**
   - Two major versions (v1.x and v2.x) with different APIs
   - Can be confusing for newcomers
   - Platform framework detects version and defines appropriate macros

#### 🎯 Best Use Cases

- System services and daemons (predictable resource cleanup)
- Multi-SBC projects (not just Raspberry Pi)
- Production deployments requiring reliability
- Projects needing guaranteed GPIO exclusivity
- Portable code across different Linux ARM platforms

---

### lgpio: The Raspberry Pi Convenience Framework

#### ✅ Verified Strengths

1. **Multi-Protocol Support**
   - GPIO, I2C, SPI, PWM, UART in one library
   - Consistent API across all protocols
   - Convenient for prototyping and development

2. **Raspberry Pi Support (All Models)**
   - Works on Pi 1-5
   - Created by Joan (pigpio's author) as successor
   - Well-maintained and actively developed

3. **GPIO State Persistence**
   - Maintains GPIO state after process exit by default
   - No special configuration required
   - Matches behavior users expect from pigpio/WiringPi

4. **Good Documentation**
   - Clear API documentation at http://abyz.me.uk/lg/lgpio.html
   - Examples available
   - Active community support

#### ⚠️ Important Caveats

1. **Threading Behavior**
   - Documentation mentions "start and stop new threads" for callbacks/alerts
   - Specific number of threads ("3-7") is anecdotal, not officially documented
   - Anecdotal user reports of shutdown delays in LibreELEC/Kodi contexts
   - **Sources**:
     - Ubuntu manpages: https://manpages.ubuntu.com/manpages/jammy/man3/lgpio.3.html
     - LibreELEC forum: https://forum.libreelec.tv/thread/26953-rpi5-shutdown-delay/

2. **Raspberry Pi Focused**
   - Primarily tested and documented for Raspberry Pi
   - May work on other SBCs but less documented
   - Less portable than libgpiod

3. **No Kernel-Enforced Exclusivity**
   - Multiple processes can potentially access same GPIO
   - User must manage conflicts manually

#### 🎯 Best Use Cases

- Raspberry Pi-specific projects (all models including Pi 5)
- Projects needing multiple protocols (GPIO+I2C+SPI+PWM+UART)
- Rapid prototyping and development
- Single-library convenience over maximum portability
- Projects where state persistence is important

---

### pigpio: Legacy High-Performance (DEPRECATED)

#### Status: ⚠️ DEPRECATED - Keep for Legacy Support Only

**Quote from pigpio's author (Joan)**:
> "pigpio does not work on the Pi 5, I do not think it can be made to work. lgpio will work."

**Source**: https://forums.raspberrypi.com/viewtopic.php?t=373963

#### Key Facts

1. **Raspberry Pi 5 Incompatible**
   - Pi 5's RP1 I/O controller broke direct register access
   - No Pi 5 support planned by author
   - Will NOT work on future Raspberry Pi models

2. **Unique Features** (Pi 1-4 only)
   - Microsecond timing precision via DMA
   - Hardware-timed PWM on any GPIO pin
   - Waveform generation
   - Built-in servo control

3. **Daemon Architecture**
   - Requires `pigpiod` daemon for multi-process access
   - More complex setup and management

#### 🎯 When to Keep Using

- **LEGACY PROJECTS ONLY**
- Existing code on Pi 1-4 that can't be migrated
- Projects requiring unique DMA timing features
- **NOT RECOMMENDED for new projects**

---

### WiringPi: Legacy Only (NOT RECOMMENDED)

#### Status: ❌ DEPRECATED - Avoid for New Projects

1. **Deprecated Since 2019**
   - Original author (Gordon Henderson) discontinued project
   - GC2 fork provides maintenance but incomplete Pi 5 support
   - Not in official Raspberry Pi OS repositories

2. **Pi 5 Support Incomplete**
   - GC2 fork added basic Pi 5 support
   - GCLK function broken on Pi 5
   - Quote: "GCLK functionality is not supported due to RP1 chip documentation limitations"

3. **No Cross-Compilation**
   - Must build directly on Raspberry Pi
   - Cannot cross-compile from macOS/Linux desktop

4. **Architectural Issues**
   - Bypasses kernel GPIO management
   - Can cause conflicts with modern drivers
   - Confusing pin numbering (WiringPi/BCM/Physical)

#### 🎯 When to Keep Using

- **MAINTENANCE OF LEGACY CODE ONLY**
- Projects already using WiringPi that can't be migrated immediately
- **PLAN MIGRATION to libgpiod or lgpio**

---

## Decision Rationale

### Why Dual-Framework Approach?

Different projects have different requirements:

| Requirement | Recommended Framework | Why |
|-------------|----------------------|-----|
| Universal SBC support | libgpiod | Works across all Linux ARM SBCs |
| Raspberry Pi only | lgpio or libgpiod | Both work, lgpio adds multi-protocol convenience |
| System daemon | libgpiod | Kernel-enforced cleanup, predictable behavior |
| Multi-protocol needs | lgpio | All protocols in one library |
| Maximum portability | libgpiod | Official Linux standard |
| Rapid prototyping | lgpio | Single library, less setup |
| Production deployment | libgpiod | Future-proof, official standard |

### Why Not "One Framework to Rule Them All"?

1. **libgpiod** provides maximum portability but is GPIO-only
2. **lgpio** provides convenience but is Raspberry Pi-focused
3. Users benefit from having both options with clear guidance
4. Real-world projects have different priorities (portability vs. convenience)

### Positioning Strategy

**Tier 1: Recommended for New Projects**
- **libgpiod** → Production, daemons, multi-SBC, maximum portability
- **lgpio** → Raspberry Pi convenience, multi-protocol, rapid development

**Tier 2: Legacy Support**
- **pigpio** → Pi 1-4 only, migration to lgpio recommended
- **WiringPi** → Maintenance only, migration to libgpiod recommended

## Implementation Details

### Framework Files

1. **builder/frameworks/libgpiod.py**
   - Auto-detects libgpiod installation (multiarch support)
   - Detects API version (v1.x vs v2.x)
   - Defines `LIBGPIOD_V1` or `LIBGPIOD_V2` macros
   - Prints state persistence warning

2. **builder/frameworks/lgpio.py**
   - Already implemented (existing implementation)
   - Architecture-specific path detection
   - Cross-compilation support

3. **builder/frameworks/pigpio.py**
   - Marked as DEPRECATED with warnings
   - Blocks Pi 5 usage with clear error message
   - No automated setup (manual build required)

4. **builder/frameworks/wiringpi.py**
   - Legacy support (native compilation only)
   - Clear deprecation warnings
   - Blocks cross-compilation

### Example Projects

#### libgpiod
- `examples/libgpiod-blink/` - LED blink (v1 API)
- `examples/libgpiod-blink-v2/` - LED blink (v2 API)
- `examples/libgpiod-button/` - Button input with interrupts

#### lgpio
- `examples/lgpio-blink/` - LED blink
- `examples/lgpio-pwm-fade/` - Software PWM LED fade
- `examples/lgpio-i2c-sensor/` - I2C sensor reading
- `examples/lgpio-spi-adc/` - SPI ADC reading

#### Legacy
- `examples/pigpio-blink/` - pigpio LED blink (Pi 1-4 only)
- `examples/wiringpi-blink/` - WiringPi LED blink (native only)

### Documentation

1. **docs/LIBGPIOD_SETUP.md** - Comprehensive libgpiod setup guide
2. **docs/LGPIO_SETUP.md** - lgpio cross-compilation guide
3. **docs/frameworks.md** - Evidence-based framework comparison
4. **docs/GPIO_FRAMEWORK_DECISION.md** - This document

## Fact-Checked Claims Summary

### ✅ Valid Claims

| Claim | Verification | Source |
|-------|-------------|---------|
| libgpiod is official Linux standard | Verified | Kernel docs |
| Kernel-enforced GPIO exclusivity | Verified | RPi whitepaper |
| libgpiod works on all SBCs | Verified | Community reports |
| pigpio doesn't work on Pi 5 | Verified | Author statement |
| lgpio supports all Pi models | Verified | Author docs |

### ⚠️ Nuanced Claims

| Claim | Reality | Notes |
|-------|---------|-------|
| "libgpiod has zero threads" | Not documented | More accurate: "uses direct ioctl calls" |
| "lgpio spawns 3-7 threads" | Anecdotal | Docs mention threading, specific number unverified |
| "Better for systemd daemons" | Likely true | Based on anecdotal shutdown delay reports |

### ❌ Corrected Claims

- Original: "libgpiod has zero-thread architecture"
- Corrected: "libgpiod uses direct ioctl() calls without persistent background thread management for basic GPIO operations"

## Migration Recommendations

### From WiringPi → libgpiod

**Reason**: WiringPi is deprecated, libgpiod is official standard

**Benefits**:
- Future-proof (works on all future Pi models)
- Cross-compilation support
- Official Linux standard

**Trade-offs**:
- API rewrite required
- GPIO-only (need separate libs for I2C/SPI)
- State persistence requires `dtparam=strict_gpiod`

### From pigpio → lgpio (for Pi 5 Support)

**Reason**: pigpio doesn't work on Pi 5, lgpio is successor by same author

**Benefits**:
- Pi 5 support
- Similar feature set
- Maintained by original author

**Trade-offs**:
- No DMA-timed PWM (pigpio's unique feature)
- API rewrite required
- Different threading model

### From lgpio → libgpiod (for Multi-SBC Support)

**Reason**: Need to support boards beyond Raspberry Pi

**Benefits**:
- Works on all Linux ARM SBCs
- Official kernel standard
- Kernel-enforced exclusivity

**Trade-offs**:
- GPIO only (need separate libs for I2C/SPI/PWM)
- State persistence configuration needed
- Potential threading differences

## Conclusion

The dual-framework strategy provides users with:

1. **libgpiod**: Maximum portability, official standard, production-ready
2. **lgpio**: Raspberry Pi convenience, multi-protocol, development-friendly

This approach serves different real-world use cases while being honest about trade-offs. Users can make informed decisions based on their specific requirements rather than overstated marketing claims.

## References

### Primary Sources

1. **Linux Kernel GPIO Documentation**
   https://www.kernel.org/doc/html/latest/driver-api/gpio/

2. **Raspberry Pi GPIO White Paper**
   https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-006553-WP/

3. **libgpiod Git Repository**
   https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/

4. **lgpio Documentation (Joan)**
   http://abyz.me.uk/lg/lgpio.html

5. **Raspberry Pi Forums - GPIO Library Discussion**
   https://forums.raspberrypi.com/viewtopic.php?t=373963

6. **Libre Computer Hub - libgpiod Tutorial**
   https://hub.libre.computer/t/how-to-use-libgpiod-on-libre-computer-boards/73

7. **EmbeddedPi - Migrating to libgpiod**
   https://www.embeddedpi.com/documentation/gpio-interfaces/libgpiod-guide

### Community Reports

1. **LibreELEC Forum - Shutdown Delays with lgpio**
   https://forum.libreelec.tv/thread/26953-rpi5-shutdown-delay/

2. **Ubuntu Manpages - lgpio threading mention**
   https://manpages.ubuntu.com/manpages/jammy/man3/lgpio.3.html

---

**Last Updated**: 2025-11-14
**Status**: Implementation Complete
**Frameworks Supported**: libgpiod (new), lgpio, pigpio (deprecated), wiringpi (deprecated)
