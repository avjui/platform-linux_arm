# Upload and Deployment

This document describes the **automated upload and deployment functionality** for the PlatformIO Linux ARM platform. This feature enables seamless deployment of compiled ARM Linux applications to remote targets (Raspberry Pi, Orange Pi, and other ARM-based SBCs) directly from your development machine.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Upload Protocols](#upload-protocols)
  - [SCP (Secure Copy)](#scp-secure-copy)
  - [Rsync (Incremental Sync)](#rsync-incremental-sync)
  - [SSH (Piped Transfer)](#ssh-piped-transfer)
  - [Manual (Instructions Only)](#manual-instructions-only)
- [Configuration Reference](#configuration-reference)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Overview

### Why Upload Functionality?

After cross-compiling an ARM Linux application on your development machine (macOS, Linux x86_64), you need to transfer the compiled binary to the target device for testing and deployment. Without automated upload, this requires manual steps:

1. Build: `pio run`
2. Copy: `scp .pio/build/raspberrypi_4b/program pi@raspberrypi.local:/home/pi/app`
3. Execute: `ssh pi@raspberrypi.local /home/pi/app`

The upload functionality automates this entire workflow into a single command: `pio run --target upload`

### How It Differs from Embedded Platforms

For microcontroller platforms (ESP32, Arduino), "upload" means flashing firmware to non-volatile memory using specialized tools (esptool, avrdude). For Linux ARM platforms:

- **"Upload"** = Deploy executable to target filesystem
- **Uses standard tools**: SCP, rsync, SSH (not custom flashers)
- **Requires network**: SSH connection to target device
- **Executable runs in userland**: Not burned to flash memory

This is conceptually similar but technically different from traditional firmware upload.

## Quick Start

### 1. Basic Setup

**Minimal configuration** (`platformio.ini`):

```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b
framework = lgpio

; Upload configuration
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp
```

### 2. SSH Key Setup

**Generate SSH key** (skip if you already have one):
```bash
ssh-keygen -t ed25519 -C "platformio@pi"
```

**Copy key to target**:
```bash
ssh-copy-id pi@raspberrypi.local
```

**Test connection**:
```bash
ssh pi@raspberrypi.local
```

### 3. Build and Upload

```bash
# Build and upload in one command
pio run --target upload

# Or separate steps
pio run              # Build
pio run -t upload    # Upload only
```

## Upload Protocols

### SCP (Secure Copy)

**Recommended for most users.** Uses the standard `scp` command to securely copy files over SSH.

#### Configuration

```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b

upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Optional settings
upload_ssh_port = 22                    ; Default SSH port
upload_ssh_key = ~/.ssh/id_ed25519      ; Specific SSH key
upload_flags = -v                       ; Verbose output
```

#### When to Use
- Yes - First-time setup (simple and reliable)
- Yes - Production deployment (secure and standard)
- Yes - Small to medium binaries (< 50MB)
- Yes - One-time or infrequent uploads

#### Pros & Cons
- Yes - **Pros**: Simple, secure, widely available, works everywhere
- No - **Cons**: Slower for large/repeated uploads (transfers entire file)

---

### Rsync (Incremental Sync)

**Best for development workflow.** Uses `rsync` to transfer only changed portions of the file.

#### Configuration

```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b

upload_protocol = rsync
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Optional settings
upload_flags = -avz --progress          ; Archive, verbose, compress, progress
upload_ssh_port = 22
upload_ssh_key = ~/.ssh/id_ed25519
```

#### When to Use
- Yes - Rapid development (frequent uploads)
- Yes - Large binaries (only changed parts transfer)
- Yes - Continuous integration workflows
- Yes - Multiple targets (sync to many devices)

#### Pros & Cons
- Yes - **Pros**: Fast incremental updates, efficient bandwidth usage
- No - **Cons**: Requires rsync on both sides (usually pre-installed)

---

### SSH (Piped Transfer)

**Alternative method.** Transfers file content via SSH stdin using `cat`.

#### Configuration

```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b

upload_protocol = ssh
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Optional settings
upload_ssh_port = 22
upload_ssh_key = ~/.ssh/id_ed25519
```

#### When to Use
- Yes - Restricted environments (scp/rsync disabled)
- Yes - Custom SSH configurations
- Yes - Debugging transfer issues

#### Pros & Cons
- Yes - **Pros**: Works with SSH only (minimal dependencies)
- No - **Cons**: Slower than scp/rsync, less common

---

### Manual (Instructions Only)

**No automatic upload.** Shows instructions for manual deployment.

#### Configuration

```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b

; upload_protocol = manual  ; Default if not specified
```

#### Output

```
============================================================
MANUAL UPLOAD REQUIRED
============================================================

Compiled binary location:
  .pio/build/raspberrypi_4b/program

To deploy to your target device, use one of:
  scp .pio/build/raspberrypi_4b/program user@host:/path/to/destination
  rsync -avz .pio/build/raspberrypi_4b/program user@host:/path/to/destination

To configure automatic upload, add to platformio.ini:
  upload_protocol = scp
  upload_port = user@hostname:/path/to/destination

See documentation for more upload options.
============================================================
```

#### When to Use
- Yes - Custom deployment workflows (scripts, CI/CD)
- Yes - Non-network deployment (USB, NFS, shared filesystem)
- Yes - Learning/testing (see what commands would run)

---

## Configuration Reference

### Required Options

| Option | Description | Example |
|--------|-------------|---------|
| `upload_protocol` | Upload method | `scp`, `rsync`, `ssh`, `manual` |
| `upload_port` | Target destination | `pi@host:/path` |

### Optional Options

| Option | Description | Default | Protocols |
|--------|-------------|---------|-----------|
| `upload_ssh_port` | SSH port number | `22` | All |
| `upload_ssh_key` | SSH private key file | (ssh-agent) | All |
| `upload_flags` | Custom flags for upload tool | (protocol-specific) | scp, rsync |
| `upload_run_after` | Run program after upload | `false` | All |
| `upload_run_command` | Custom command to run | (uploaded binary path) | All |

### Upload Port Format

The `upload_port` option accepts multiple formats:

```ini
; Format 1: Full specification (user@host:path)
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Format 2: IP address
upload_port = pi@192.168.1.100:/home/pi/myapp

; Format 3: Hostname only (path defaults to /tmp/program)
upload_port = raspberrypi.local

; Format 4: User inferred from upload_user
upload_port = raspberrypi.local:/home/pi/myapp
upload_user = pi

; Format 5: Custom path via upload_path
upload_port = raspberrypi.local
upload_path = /opt/myapp/bin/program
upload_user = pi
```

**Parsing Rules:**
1. User extracted from `user@` prefix (fallback: `upload_user`, default: `pi`)
2. Host extracted from `@host` or entire string if no `@`
3. Path extracted from `:path` suffix (fallback: `upload_path`, default: `/tmp/program`)

## Advanced Usage

### Post-Upload Execution

Run the program automatically after upload:

```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b

upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Run after upload
upload_run_after = true

; Optional: Run with sudo (for GPIO access)
upload_run_command = sudo /home/pi/myapp
```

**Output:**
```
============================================================
UPLOAD SUCCESSFUL
============================================================

============================================================
RUNNING REMOTE PROGRAM
============================================================
Target: pi@raspberrypi.local
Command: sudo /home/pi/myapp
============================================================

[Program output appears here...]
```

### Remote Program Monitoring

Monitor the remote program's output in real-time via SSH (similar to serial monitor for microcontrollers):

```bash
# Upload and then monitor
pio run --target upload --target monitor

# Or monitor separately (runs the already-uploaded program)
pio run --target monitor
```

**Configuration:**
```ini
[env:mypi]
platform = linux_arm
board = raspberrypi_4b

upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/myapp

; Optional: Custom run command for monitoring
; upload_run_command = sudo /home/pi/myapp
; upload_run_timeout = 60  ; Timeout in seconds
```

**Notes:**
- The `monitor` target runs the program at `upload_port` location via SSH
- Output is streamed in real-time from the remote target
- Press Ctrl+C to stop monitoring
- Unlike serial monitors, this requires a network connection to the target
- The platform automatically configures a dummy `monitor_port` to prevent PlatformIO's
  default serial monitor from interfering with SSH-based monitoring

**Comparison with upload_run_after:**
- `upload_run_after = true`: Runs once after each upload
- `--target monitor`: Can be run independently, useful for repeated testing without re-uploading

### Multiple Target Environments

Deploy to different devices by environment:

```ini
[env:dev]
platform = linux_arm
board = raspberrypi_4b
upload_protocol = scp
upload_port = pi@pi-dev.local:/home/pi/myapp

[env:staging]
platform = linux_arm
board = raspberrypi_4b
upload_protocol = scp
upload_port = pi@pi-staging.local:/home/pi/myapp

[env:production]
platform = linux_arm
board = raspberrypi_5
upload_protocol = rsync
upload_port = admin@pi-prod.example.com:/opt/myapp/bin/program
upload_ssh_port = 2222
upload_ssh_key = ~/.ssh/production_key
```

**Usage:**
```bash
pio run -e dev -t upload        # Upload to dev
pio run -e staging -t upload    # Upload to staging
pio run -e production -t upload # Upload to production
```

### Custom SSH Configuration

Non-standard SSH setups:

```ini
[env:secure]
platform = linux_arm
board = raspberrypi_4b

upload_protocol = scp
upload_port = admin@prod-server.example.com:/opt/myapp/program

; Custom SSH port
upload_ssh_port = 2222

; Specific SSH key (not default)
upload_ssh_key = ~/.ssh/production_deploy_key

; Extra SCP flags (e.g., compression, bandwidth limit)
upload_flags = -C -l 8192
```

### CI/CD Integration

#### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup PlatformIO
        run: |
          pip install platformio

      - name: Setup SSH Key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.PI_SSH_KEY }}" > ~/.ssh/pi_key
          chmod 600 ~/.ssh/pi_key

      - name: Build and Deploy
        run: |
          pio run -e production --target upload
        env:
          PLATFORMIO_UPLOAD_SSH_KEY: ~/.ssh/pi_key
```

#### GitLab CI Example

```yaml
deploy:
  stage: deploy
  script:
    - pip install platformio
    - eval $(ssh-agent -s)
    - echo "$PI_SSH_KEY" | ssh-add -
    - pio run -e production --target upload
  only:
    - main
```

### Custom Upload Flags

#### SCP Examples

```ini
; Verbose output for debugging
upload_flags = -v

; Compression (useful for large binaries on slow networks)
upload_flags = -C

; Limit bandwidth to 1MB/s
upload_flags = -l 8192

; Multiple flags
upload_flags = -v -C
```

#### Rsync Examples

```ini
; Default: archive, verbose, compress
upload_flags = -avz

; Add progress bar
upload_flags = -avz --progress

; Preserve permissions and times
upload_flags = -rlptgoDvz

; Dry run (test without uploading)
upload_flags = -avz --dry-run

; Delete extraneous files on destination
upload_flags = -avz --delete
```

## Security Considerations

### SSH Key Security

Generate dedicated SSH keys for PlatformIO deployments:

```bash
# Generate dedicated key
ssh-keygen -t ed25519 -f ~/.ssh/pio-deploy -C "platformio-deploy"

# Set proper permissions
chmod 600 ~/.ssh/pio-deploy
chmod 644 ~/.ssh/pio-deploy.pub
```

Configure in platformio.ini:

```ini
[env:myboard]
upload_ssh_key = ~/.ssh/pio-deploy
```

**Best Practices:**

- Use separate keys for different environments (dev/staging/prod)
- Use passphrase protection for keys
- Never commit private keys to version control
- Restrict key permissions (600 for private, 644 for public)

### Host Key Verification

By default, upload operations respect your SSH configuration. For strict host key checking:

```ini
[env:production]
upload_flags = -o StrictHostKeyChecking=yes
```

### Timeout Protection

Configure timeouts to prevent hung SSH connections:

```ini
[env:myboard]
# Upload timeout in seconds (default: 300)
upload_timeout = 300

# Remote command execution timeout (default: 300)
upload_run_timeout = 300
```

If uploads frequently timeout on slow networks, increase these values accordingly.

See [SECURITY.md](../SECURITY.md) for comprehensive security guidelines.

## Troubleshooting

### Permission Denied (SSH Authentication)

**Problem:** Upload fails with "Permission denied (publickey)"

**Solution:**
```bash
# 1. Generate SSH key if needed
ssh-keygen -t ed25519 -C "platformio@pi"

# 2. Copy key to target
ssh-copy-id pi@raspberrypi.local

# 3. Test connection
ssh pi@raspberrypi.local

# 4. Verify SSH key in platformio.ini
upload_ssh_key = ~/.ssh/id_ed25519  # Explicit path if needed
```

### Connection Refused

**Problem:** "Connection refused" or "No route to host"

**Possible Causes:**
1. SSH server not running
2. Wrong hostname/IP
3. Firewall blocking port 22
4. Network connectivity issue

**Solution:**
```bash
# On target device, enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh

# Test connectivity
ping raspberrypi.local  # Or IP address
nmap -p 22 raspberrypi.local

# Check firewall (if applicable)
sudo ufw allow ssh
```

### Upload Tool Not Found

**Problem:** "Upload tool 'scp' is not installed"

**Solution:**
```bash
# Linux
sudo apt update
sudo apt install openssh-client rsync

# macOS (rsync only, scp/ssh pre-installed)
brew install rsync

# Verify installation
which scp rsync ssh
```

### Hostname Not Resolved

**Problem:** "Could not resolve hostname raspberrypi.local"

**Solution:**
```bash
# 1. Use IP address instead
upload_port = pi@192.168.1.100:/home/pi/myapp

# 2. Or find IP on network
# On Raspberry Pi:
hostname -I

# 3. Add to /etc/hosts (macOS/Linux)
echo "192.168.1.100 raspberrypi.local" | sudo tee -a /etc/hosts

# 4. Enable mDNS/Bonjour (Linux)
sudo apt install avahi-daemon
```

### Destination Path Not Writable

**Problem:** Upload succeeds but "Permission denied" writing to destination

**Solution:**
```bash
# Option 1: Use writable directory
upload_port = pi@raspberrypi.local:/home/pi/myapp

# Option 2: Create directory and set permissions
ssh pi@raspberrypi.local
mkdir -p /home/pi/myapp
chmod 755 /home/pi/myapp

# Option 3: Use /tmp (world-writable)
upload_port = pi@raspberrypi.local:/tmp/program
```

### Binary Won't Execute (Permission Denied)

**Problem:** Upload succeeds but running gives "Permission denied"

**Solution:**
```bash
# SSH uploads automatically chmod +x
# For scp/rsync, do manually:
ssh pi@raspberrypi.local chmod +x /home/pi/myapp

# Or use upload_run_after to test immediately
upload_run_after = true
```

### Stale Fingerprint (Host Key Verification Failed)

**Problem:** "Host key verification failed" after re-imaging SD card

**Solution:**
```bash
# Remove old fingerprint
ssh-keygen -R raspberrypi.local

# Or by IP
ssh-keygen -R 192.168.1.100

# Reconnect to add new fingerprint
ssh pi@raspberrypi.local
```

### Slow Upload on Fast Network

**Problem:** Upload takes longer than expected

**Solution:**
```bash
# 1. Use rsync for incremental (much faster for re-uploads)
upload_protocol = rsync

# 2. Enable compression (helps on slow networks, may slow fast ones)
upload_flags = -C  # SCP
upload_flags = -avz  # Rsync (default)

# 3. Test network speed
iperf3 -s  # On target
iperf3 -c raspberrypi.local  # On dev machine
```

## Security Best Practices

### 1. Use SSH Key Authentication (Not Passwords)

**Why:** Password authentication is vulnerable to brute-force attacks.

```bash
# Generate strong key
ssh-keygen -t ed25519 -C "platformio@$(hostname)"

# Use passphrase to protect key
# (ssh-agent caches passphrase)

# Disable password auth on target (optional)
sudo vi /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart ssh
```

### 2. Restrict SSH Key Usage

**Why:** Limit what a compromised key can do.

```bash
# On target: ~/.ssh/authorized_keys
# Restrict key to specific command
command="/home/pi/myapp",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAA...
```

### 3. Use Non-Standard SSH Port

**Why:** Reduces automated SSH brute-force attempts.

```ini
; Change SSH port on target
; /etc/ssh/sshd_config: Port 2222

[env:secure]
upload_ssh_port = 2222
upload_port = pi@raspberrypi.local:/home/pi/myapp
```

### 4. Separate Deploy Keys per Environment

**Why:** Limit blast radius of key compromise.

```ini
[env:dev]
upload_ssh_key = ~/.ssh/dev_deploy_key

[env:staging]
upload_ssh_key = ~/.ssh/staging_deploy_key

[env:production]
upload_ssh_key = ~/.ssh/production_deploy_key
```

### 5. Use Firewall Rules

**Why:** Limit SSH access to known IPs.

```bash
# On target: Allow SSH only from dev machine
sudo ufw allow from 192.168.1.50 to any port 22
sudo ufw enable
```

### 6. Monitor Upload Activity

**Why:** Detect unauthorized deployments.

```bash
# On target: Watch auth logs
sudo tail -f /var/log/auth.log

# Set up fail2ban (optional)
sudo apt install fail2ban
```

### 7. Validate Binary Integrity (Advanced)

**Why:** Ensure binary wasn't tampered with in transit.

```bash
# Before upload: generate checksum
sha256sum .pio/build/raspberrypi_4b/program > program.sha256

# After upload: verify
ssh pi@raspberrypi.local sha256sum -c program.sha256
```

## Examples

See `examples/remote-deployment/` for a complete working example with:
- All upload protocols demonstrated
- Multiple environment configurations
- Post-upload execution examples
- Detailed README with troubleshooting

## See Also

- [PlatformIO Upload Options](https://docs.platformio.org/en/latest/projectconf/sections/env/options/upload/)
- [SCP Manual](https://man.openbsd.org/scp)
- [Rsync Manual](https://linux.die.net/man/1/rsync)
- [SSH Configuration](https://linux.die.net/man/5/ssh_config)
- [Issue #36](https://github.com/sfo2001/platform-linux_arm/issues/36) - Feature discussion

## Contributing

Found a bug or have a feature request? Please [open an issue](https://github.com/sfo2001/platform-linux_arm/issues).

## License

Apache 2.0 - See LICENSE file for details
