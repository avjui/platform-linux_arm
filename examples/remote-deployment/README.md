# Remote Deployment Example

This example demonstrates the **automated upload/deployment functionality** of the PlatformIO Linux ARM platform. It shows how to build ARM Linux applications on your development machine and automatically deploy them to remote targets (Raspberry Pi, Orange Pi, etc.) using standard Linux tools.

## Features Demonstrated

- **SCP Upload**: Secure copy using SSH
- **Rsync Upload**: Efficient incremental transfer
- **SSH Upload**: Alternative deployment method
- **Post-Upload Execution**: Automatically run the program after upload
- **Multiple Target Configurations**: Deploy to dev/staging/production

## Quick Start

### 1. Prerequisites

**On your development machine:**
- PlatformIO Core installed
- SSH client (scp/rsync/ssh) - usually pre-installed on Linux/macOS
- SSH access to your target device

**On your target device (Raspberry Pi/Orange Pi):**
- SSH server running (usually enabled by default)
- Network connectivity
- lgpio library installed: `sudo apt install lgpio`

### 2. Setup SSH Authentication

Generate SSH key (if you don't have one):
```bash
ssh-keygen -t ed25519 -C "platformio@pi"
```

Copy your SSH key to the target:
```bash
ssh-copy-id pi@raspberrypi.local
```

Test the connection:
```bash
ssh pi@raspberrypi.local
```

### 3. Build and Upload

**Build the project:**
```bash
pio run
```

**Upload to remote target:**
```bash
pio run --target upload
```

That's it! The compiled binary is automatically copied to your Raspberry Pi.

### 4. Run the Program

The program can run automatically after upload if configured, or you can run manually:

```bash
ssh pi@raspberrypi.local
sudo /home/pi/myapp  # Run with sudo for GPIO access
```

## Configuration Examples

See `platformio.ini` for 8 different configuration examples covering:

1. **SCP Upload** (recommended) - Standard secure copy
2. **Rsync Upload** - Faster for repeated deployments
3. **SSH Upload** - Alternative method
4. **Multiple Targets** - Deploy to different devices
5. **Custom SSH Port** - Non-standard SSH configurations
6. **Auto-Run** - Execute after upload
7. **Manual Upload** - Shows instructions without uploading
8. **Simplified** - Minimal configuration for quick setup

## Upload Configuration Options

### Required Options

```ini
upload_protocol = scp          ; Upload method: scp, rsync, ssh, manual
upload_port = user@host:/path  ; Target: [user@]host[:path]
```

### Optional Options

```ini
upload_ssh_port = 22                    ; SSH port (default: 22)
upload_ssh_key = ~/.ssh/id_ed25519      ; SSH key file
upload_flags = -avz --progress          ; Custom flags (rsync/scp)
upload_run_after = true                 ; Run program after upload
upload_run_command = sudo /path/to/app  ; Custom run command
```

## Target Specification Formats

The `upload_port` option supports multiple formats:

```ini
; Format 1: Full specification
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Format 2: IP address
upload_port = pi@192.168.1.100:/home/pi/myapp

; Format 3: Hostname only (uses default path /tmp/program)
upload_port = pi@raspberrypi.local

; Format 4: With .local mDNS
upload_port = pi@raspberrypi.local:/home/pi/myapp
```

## Deployment Workflows

### Development Workflow
```bash
# Edit code
# Build and upload in one command
pio run --target upload

# Upload triggers automatic rebuild if needed
```

### Multiple Device Testing
```bash
# Deploy to dev device
pio run -e pi_dev --target upload

# Deploy to staging
pio run -e pi_staging --target upload

# Deploy to production
pio run -e pi_production --target upload
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Build and Deploy
  run: |
    pio run
    pio run --target upload
  env:
    PIO_ENV: pi_production
```

## Troubleshooting

### "Permission denied" when uploading

**Solution:** Setup SSH key authentication:
```bash
ssh-copy-id user@target
```

### "Connection refused"

**Possible causes:**
1. SSH server not running on target
2. Wrong hostname/IP address
3. Firewall blocking port 22

**Solution:**
```bash
# On target, enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Test connection
ping raspberrypi.local
ssh pi@raspberrypi.local
```

### "Upload tool not found"

**Solution:** Install required tool:
```bash
# Linux
sudo apt install openssh-client rsync

# macOS
brew install rsync  # scp/ssh are pre-installed
```

### GPIO permissions error when running

**Solution:** Run with sudo or configure GPIO permissions:
```bash
# Option 1: Run with sudo
sudo /home/pi/myapp

# Option 2: Add user to gpio group
sudo usermod -a -G gpio pi
sudo reboot
```

## Hardware Requirements

- Raspberry Pi (any model) or compatible ARM SBC
- LED connected to GPIO 17 (or modify LED_PIN in code)
- Network connection (WiFi or Ethernet)

## LED Connection

```
Raspberry Pi GPIO 17 (Pin 11)
         |
         ├── LED (+) ──[220Ω resistor]── LED (-) ──┤
         |                                          |
         └──────────────────────────────────────────┴── GND (Pin 6)
```

## Expected Output

```
PlatformIO Linux ARM - Remote Deployment Example
=================================================

GPIO chip opened successfully
GPIO 17 claimed as output
Blinking LED 10 times...

LED ON  (iteration 1/10)
LED OFF (iteration 1/10)
...
LED ON  (iteration 10/10)
LED OFF (iteration 10/10)

Blink sequence complete!
GPIO resources released

=================================================
Program finished successfully
```

## Learn More

- **Platform Documentation**: See `/docs/UPLOAD.md` for complete upload feature documentation
- **PlatformIO Upload Options**: https://docs.platformio.org/en/latest/projectconf/sections/env/options/upload/
- **lgpio Documentation**: http://abyz.me.uk/lg/index.html

## Next Steps

1. Modify the code to test your own GPIO hardware
2. Try different upload protocols (scp, rsync, ssh)
3. Configure multiple target environments
4. Integrate into your CI/CD pipeline
5. Explore post-upload execution options

## License

Apache 2.0 - See LICENSE file for details
