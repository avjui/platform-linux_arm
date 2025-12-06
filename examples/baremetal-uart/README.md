# Bare-Metal UART Serial Communication Example

A comprehensive example demonstrating asynchronous serial communication on Raspberry Pi using the standard Linux `termios` API. No GPIO library or framework required - pure POSIX serial port interface.

## Overview

This example showcases professional serial port programming techniques commonly needed for:
- **GPS modules** (NMEA data parsing)
- **Bluetooth serial** (HC-05, HC-06 modules)
- **GSM/LTE modems** (AT command interface)
- **Serial sensors** (temperature, pressure, etc.)
- **USB-to-Serial adapters**
- **Arduino/ESP32 communication**
- **Industrial serial protocols** (Modbus RTU, etc.)

### Key Features

Yes - **Proper termios configuration** following POSIX best practices
Yes - **Bidirectional communication** with echo test and interactive modes
Yes - **Non-blocking I/O** with timeout handling
Yes - **Comprehensive error handling** with helpful diagnostics
Yes - **Multiple operation modes** (echo test, interactive)
Yes - **Cross-compilation support** (build on x86_64, run on ARM)
Yes - **No framework dependency** - standard Linux APIs only

### Learning Outcomes

- Understanding Linux serial port device model (`/dev/tty*`)
- Configuring `termios` structure (baud rate, parity, data bits, stop bits)
- Non-blocking I/O with `select()` and timeouts
- Proper error handling for serial communication
- Data parsing and protocol implementation patterns

## Hardware Connections

### Option 1: Hardware UART on GPIO (Most Common)

The Raspberry Pi's hardware UART is available on GPIO pins 14 and 15:

```
Raspberry Pi                  Serial Device
┌─────────────┐              ┌──────────────┐
│             │              │              │
│  GPIO 14 TX │─────────────>│ RX           │
│  (Pin 8)    │              │              │
│             │              │              │
│  GPIO 15 RX │<─────────────│ TX           │
│  (Pin 10)   │              │              │
│             │              │              │
│  GND        │──────────────│ GND          │
│  (Pin 6)    │              │              │
└─────────────┘              └──────────────┘
```

**Pin mapping (40-pin header):**
- **Pin 8** (GPIO 14) = TX (Transmit)
- **Pin 10** (GPIO 15) = RX (Receive)
- **Pin 6** (or any GND) = Ground

**Voltage warning:** Raspberry Pi GPIO is **3.3V logic**. If connecting to 5V devices (like Arduino), use a logic level converter!

### Option 2: USB-to-Serial Adapter

Simply plug in a USB-to-Serial adapter (FTDI, CH340, CP2102, etc.):
- Device will appear as `/dev/ttyUSB0` (or `/dev/ttyACM0` for some devices)
- No GPIO wiring needed
- Automatically detected by Linux kernel

### Option 3: Loopback Test (No External Device)

For testing without external hardware, connect TX to RX:
- Connect GPIO 14 (Pin 8) to GPIO 15 (Pin 10)
- Any data sent will be immediately received (echo)

## Raspberry Pi UART Configuration

### Step 1: Enable UART Hardware

The UART may be disabled by default or used for Bluetooth. Enable it with:

```bash
sudo raspi-config
```

Navigate to: **Interface Options** → **Serial Port**
- "Login shell accessible over serial?" → **No**
- "Serial port hardware enabled?" → **Yes**

Or manually edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add or uncomment these lines:

```ini
# Enable UART
enable_uart=1

# For Pi 3/4/5: Disable Bluetooth to free up hardware UART (optional)
# dtoverlay=disable-bt
```

Reboot after changes:

```bash
sudo reboot
```

### Step 2: Verify UART Devices

Check available serial devices:

```bash
ls -l /dev/serial* /dev/tty{AMA,S,USB,ACM}*
```

Common devices:
- `/dev/serial0` → Primary UART (symlink, **recommended**)
- `/dev/ttyAMA0` → Hardware UART (Pi 1, 2, Zero)
- `/dev/ttyS0` → Mini UART or Bluetooth (Pi 3, 4, 5)
- `/dev/ttyUSB0` → USB-to-Serial adapter
- `/dev/ttyACM0` → USB CDC ACM device

**Best practice:** Use `/dev/serial0` as it always points to the primary UART regardless of Pi model.

### Step 3: Fix Permissions (if needed)

If you get "Permission denied" errors:

```bash
# Add your user to the dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for changes to take effect
```

Or run with sudo:

```bash
sudo .pio/build/raspberrypi_3b/program
```

## Building

### Prerequisites

- PlatformIO Core 6.0+
- ARM cross-compilation toolchain (automatically installed by PlatformIO)

### Build for Specific Board

```bash
# Build for Raspberry Pi 3
pio run -e raspberrypi_3b

# Build for Raspberry Pi 4
pio run -e raspberrypi_4b

# Build for Raspberry Pi 5
pio run -e raspberrypi_5

# Build for Raspberry Pi Zero 2W
pio run -e raspberrypi_zero2w

# Clean build artifacts
pio run --target clean
```

### Cross-Compilation

This example can be cross-compiled from:
- **Linux x86_64** (Ubuntu, Debian, etc.)
- **macOS** (Intel or Apple Silicon)
- **Windows x86_64** (WSL or native)

PlatformIO will automatically download and configure the ARM toolchain.

## Running

After building, transfer the executable to your Raspberry Pi and run it:

```bash
# Transfer (from your dev machine)
scp .pio/build/raspberrypi_3b/program pi@raspberrypi.local:~/uart-test

# Run on Raspberry Pi
ssh pi@raspberrypi.local
./uart-test
```

Or if compiling directly on the Pi:

```bash
.pio/build/raspberrypi_3b/program
```

## Usage

### Mode 1: Echo Test (Default)

Sends predefined test messages and waits for echo responses. Ideal for loopback testing or devices that echo data back.

```bash
# Using default device (/dev/serial0)
./program

# Using specific device
./program /dev/ttyUSB0
```

**Expected output:**
```
╔════════════════════════════════════════════════════╗
║  Bare-Metal UART Serial Communication Example     ║
║  Platform: Linux ARM (Raspberry Pi)               ║
║  API: POSIX termios (no framework required)        ║
╚════════════════════════════════════════════════════╝

Configuration:
  Device: /dev/serial0
  Baud rate: 9600
  Mode: Echo Test

Opening serial port...
✓ Serial port opened successfully
Configuring serial parameters...
✓ Serial port configured

╔════════════════════════════════════════════════════╗
║  Echo Test Mode                                    ║
╚════════════════════════════════════════════════════╝

TX: Hello from Raspberry Pi!
RX: Waiting for response -> Hello from Raspberry Pi! ✓ Match

TX: Testing UART communication
RX: Waiting for response -> Testing UART communication ✓ Match

✓ Echo test completed
```

### Mode 2: Interactive Mode

Interactive bidirectional communication. Type messages to send, received data displayed automatically.

```bash
# Interactive mode with default device
./program --interactive

# Interactive mode with specific device
./program --interactive /dev/ttyAMA0
```

**Example session:**
```
╔════════════════════════════════════════════════════╗
║  Interactive Mode                                  ║
╚════════════════════════════════════════════════════╝

Type messages to send. Press Ctrl+C to exit.
Received data will be displayed automatically.

>> TX: AT
<< RX: OK

>> TX: Hello Arduino!
<< RX: Received: Hello Arduino!
```

### Command-Line Options

```bash
# Show help
./program --help

# Echo test (default)
./program [device]

# Interactive mode
./program --interactive [device]
```

## Testing Without Hardware

### Software Loopback Test

1. **Physical loopback**: Connect GPIO 14 to GPIO 15
2. **Run echo test**:
   ```bash
   ./program /dev/serial0
   ```
3. All sent messages should be received back immediately

### Using Virtual Serial Ports (socat)

For testing without hardware or GPIO connections:

```bash
# Install socat
sudo apt install socat

# Create virtual serial port pair
socat -d -d pty,raw,echo=0 pty,raw,echo=0
# Note the devices created, e.g., /dev/pts/2 and /dev/pts/3

# In terminal 1: Run program
./program /dev/pts/2

# In terminal 2: Communicate with it
cat /dev/pts/3          # Receive
echo "Hello" > /dev/pts/3  # Send
```

## Code Structure

### Key Functions

| Function | Purpose |
|----------|---------|
| `configure_serial_port()` | Sets up termios structure with proper POSIX flags |
| `serial_write()` | Sends data and ensures transmission completes |
| `serial_read_timeout()` | Reads data with timeout using `select()` |
| `run_echo_test()` | Automated test sequence for validation |
| `run_interactive_mode()` | User-interactive bidirectional communication |

### termios Configuration Details

The example demonstrates **proper POSIX termios configuration**:

```c
// Input flags: raw input, no processing
c_iflag &= ~(IGNBRK | BRKINT | ICRNL | INLCR | PARMRK | INPCK | ISTRIP | IXON);

// Output flags: raw output, no processing
c_oflag &= ~(OCRNL | ONLCR | ONLRET | ONOCR | OFILL | OPOST);

// Line flags: no canonical mode, no echo
c_lflag &= ~(ECHO | ECHONL | ICANON | IEXTEN | ISIG);

// Control flags: 8N1 (8 data bits, no parity, 1 stop bit)
c_cflag &= ~(CSIZE | PARENB | CSTOPB);
c_cflag |= CS8 | CREAD | CLOCAL;

// Timeouts: non-blocking with timeout
c_cc[VMIN] = 0;   // Return immediately
c_cc[VTIME] = 5;  // 0.5 second timeout
```

This is the **recommended approach** instead of zeroing the entire structure, as it preserves system-specific fields.

## Common Use Cases

### 1. GPS Module (NMEA Data)

Connect GPS module TX to Pi RX:

```bash
./program --interactive /dev/serial0
```

You'll see NMEA sentences like:
```
<< RX: $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
<< RX: $GPGLL,4916.45,N,12311.12,W,225444,A,*1D
```

### 2. Bluetooth Serial Module (HC-05)

1. Wire: HC-05 TX → Pi RX, HC-05 RX → Pi TX (via level shifter!)
2. Default baud: 9600 (HC-05 default)
3. Run interactive mode:
   ```bash
   ./program --interactive /dev/serial0
   ```
4. Send AT commands:
   ```
   >> TX: AT
   << RX: OK
   ```

### 3. Arduino Communication

**Arduino sketch:**
```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readString();
    Serial.print("Arduino received: ");
    Serial.println(data);
  }
}
```

**Raspberry Pi:**
```bash
./program --interactive /dev/serial0
>> TX: Hello Arduino!
<< RX: Arduino received: Hello Arduino!
```

### 4. USB-to-Serial Adapter

Plug in adapter, find device name:

```bash
dmesg | tail
# Look for: "FTDI USB Serial Device converter now attached to ttyUSB0"

./program /dev/ttyUSB0
```

## Troubleshooting

### Issue: "Permission denied"

**Solution:**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

Or run with sudo:
```bash
sudo ./program
```

### Issue: "No such file or directory" (`/dev/serial0`)

**Solution:**
1. Check if UART is enabled:
   ```bash
   ls -l /dev/serial* /dev/tty{AMA,S}*
   ```
2. Enable UART in `raspi-config`
3. Reboot

### Issue: "Input/output error" or garbage data

**Possible causes:**
- Wrong baud rate (both devices must match)
- Incorrect wiring (TX/RX swapped)
- Voltage mismatch (use level shifter for 5V devices)
- UART disabled in config

**Solutions:**
- Verify connections (TX → RX, RX → TX)
- Check baud rate on both devices
- Test with loopback (TX to RX on same device)

### Issue: Timeout, no data received

**Solutions:**
- Verify other device is transmitting
- Check wiring (especially TX/RX swap)
- Test with loopback
- Check device exists: `ls -l /dev/serial0`

### Issue: Works with sudo but not without

**Solution:**
```bash
# Check current permissions
ls -l /dev/serial0

# Add user to dialout group
sudo usermod -a -G dialout $USER

# Verify group membership after re-login
groups
```

## Comparison with WiringPi Serial Example

| Feature | Bare-Metal (termios) | WiringPi |
|---------|---------------------|----------|
| **API** | POSIX termios | WiringPi serialOpen/serialGetchar |
| **Framework** | None (bare-metal) | WiringPi required |
| **Portability** | Any Linux system | Raspberry Pi only |
| **Learning value** | High (standard Linux API) | Lower (abstraction layer) |
| **Cross-compile** | Yes | Limited (WiringPi dependency) |
| **Configuration** | Full control (baud, parity, etc.) | Limited options |
| **Dependencies** | None (libc only) | WiringPi library |
| **Use cases** | Production, embedded Linux | Quick prototyping |

**When to use bare-metal termios:**
- Production applications
- Learning Linux serial programming
- Cross-platform Linux projects (not Pi-specific)
- Full control over serial parameters
- No external dependencies desired

**When to use WiringPi:**
- Quick prototypes
- Already using WiringPi for GPIO
- Simple serial needs

## Further Reading

### Official Documentation
- [Linux Serial HOWTO](https://tldp.org/HOWTO/Serial-HOWTO.html)
- [POSIX termios reference](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/termios.h.html)
- [Raspberry Pi UART documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts)

### Serial Protocols
- NMEA 0183 (GPS): [NMEA Protocol Specification](https://www.nmea.org/)
- Modbus RTU: [Modbus Protocol Guide](https://modbus.org/)
- AT Commands: [AT Command Set](https://en.wikipedia.org/wiki/Hayes_command_set)

### Raspberry Pi Resources
- [Raspberry Pi Pinout](https://pinout.xyz/)
- [UART Configuration Guide](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts)

## License

This example is provided as educational material for the PlatformIO Linux ARM platform. Feel free to use and modify for your projects.

## Related Examples

- **baremetal-hello** - Simple bare-metal "Hello World"
- **wiringpi-serial** - Serial communication using WiringPi framework (simpler but less flexible)
- **lgpio-blink** - GPIO control with modern lgpio library
- **pigpio-blink** - GPIO control with pigpio library

## Contributing

Found a bug or have an improvement? Contributions welcome!

1. Test on your Raspberry Pi
2. Document hardware setup and results
3. Submit pull request with clear description

---

**Built with PlatformIO** | **Platform: Linux ARM** | **Framework: None (bare-metal)**
