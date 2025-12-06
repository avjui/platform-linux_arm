# Security Policy

## Supported Versions

Security updates are provided for the following versions:

| Version | Supported |
| ------- | --------- |
| 1.7.x   | Yes       |
| 1.6.x   | Yes       |
| < 1.6   | No        |

## Security Features

The platform-linux_arm PlatformIO platform implements several security features to protect against common vulnerabilities:

### 1. Command Injection Protection

All user-provided input that is passed to shell commands is properly escaped using Python's `shlex.quote()` function. This prevents command injection attacks through:
- File paths in upload/test operations
- SSH configuration parameters
- Remote execution commands
- Debug session paths

**Affected areas:**
- `platform.py`: All upload methods (`_upload_scp`, `_upload_rsync`, `_upload_ssh`)
- `platform.py`: Remote command execution (`_run_remote_command`)
- `platform.py`: Debug session configuration (`configure_debug_session`)
- `platform-test-uploader.py`: Test binary upload and execution

### 2. Timeout Protection

All subprocess calls include configurable timeouts to prevent denial-of-service attacks through hung SSH connections or long-running processes.

**Default timeouts:**
- Upload operations: 300 seconds (5 minutes)
- Remote command execution: 300 seconds (5 minutes)
- Test upload: 300 seconds (5 minutes)
- Test execution: 600 seconds (10 minutes)

**Configuration options** (add to `platformio.ini`):
```ini
[env:myboard]
# Upload timeout in seconds
upload_timeout = 300

# Remote command execution timeout in seconds
upload_run_timeout = 300

# Test upload timeout in seconds
test_upload_timeout = 300

# Test execution timeout in seconds
test_timeout = 600
```

### 3. SSH Host Key Verification

**For upload and debugging operations:**
By default, SSH host key checking is enabled and follows your system's SSH configuration (`~/.ssh/known_hosts`).

**For automated testing:**
The test framework (`platform-test-uploader.py`) disables strict host key checking by default to enable automated CI/CD workflows. This is documented and intentional, but introduces a potential man-in-the-middle (MITM) attack risk.

**To enable strict host key checking for tests**, you can override this behavior by configuring custom SSH options:
```ini
[env:myboard]
test_ssh_flags = -o StrictHostKeyChecking=yes
```

## Security Best Practices

### 1. SSH Key Management

**Recommended:**
- Use SSH key-based authentication instead of passwords
- Store SSH private keys with restrictive permissions (chmod 600)
- Use different SSH keys for different environments (dev, staging, production)
- Consider using SSH agent for key management

**Example configuration:**
```ini
[env:raspberrypi_4b]
upload_protocol = scp
upload_port = pi@raspberrypi.local:/home/pi/program
upload_ssh_key = ~/.ssh/id_rsa_raspberry
```

### 2. Path Validation

Always use absolute paths or carefully validated relative paths for:
- Upload destinations (`upload_port`)
- Test binary locations (`test_port`)
- Debug session paths (`debug_port`)

**Avoid:**
- User input in path construction without validation
- Paths containing shell metacharacters (`;`, `|`, `&`, etc.)
- Relative paths that could be manipulated (e.g., `../../etc/passwd`)

### 3. Network Security

**Recommendations:**
- Use SSH tunnels or VPNs for remote access to development boards
- Restrict SSH access to trusted IP addresses/networks using firewall rules
- Keep SSH server software up-to-date on target devices
- Disable password authentication on SSH servers (use keys only)
- Use non-standard SSH ports to reduce automated attack surface

### 4. CI/CD Security

For automated testing in CI/CD pipelines:
- Use ephemeral test environments when possible
- Rotate SSH keys regularly
- Limit SSH key permissions (use dedicated test-only users)
- Monitor logs for suspicious activity
- Consider using container-based testing instead of physical hardware

### 5. Timeout Configuration

Adjust timeouts based on your specific use case:
- **Slow networks**: Increase `upload_timeout` and `test_upload_timeout`
- **Long-running tests**: Increase `test_timeout`
- **Security-critical environments**: Decrease timeouts to minimize exposure time

## Reporting a Vulnerability

If you discover a security vulnerability in platform-linux_arm, please report it by:

1. **DO NOT** open a public GitHub issue
2. Email the maintainer at: [maintainer contact - update this]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

**Response timeline:**
- Initial response: Within 48 hours
- Vulnerability assessment: Within 7 days
- Fix implementation: Within 30 days (critical), 90 days (high/medium)

## Security Audit History

### Version 1.7.0 (2025-11-14)

**Critical fixes:**
- Fixed command injection vulnerabilities in SSH upload methods (CVSS 9.0)
- Fixed command injection in rsync SSH options (CVSS 8.0)
- Fixed command injection in debug session configuration (CVSS 8.0)
- Fixed command injection in test execution (CVSS 8.5)
- Added timeout protection to all subprocess calls (DoS mitigation)

**Files modified:**
- `platform.py`: Command injection fixes and timeout protection
- `platform-test-uploader.py`: Command injection fixes and timeout protection

**Testing:**
- Verified with malicious path inputs (e.g., `/tmp/program; rm -rf /`)
- Verified with paths containing spaces and special characters
- Verified timeout behavior with artificially delayed connections

## Known Security Considerations

### 1. Disabled Host Key Checking (Test Framework)

**Risk:** Man-in-the-middle attacks during automated testing
**Severity:** Low (4.0 CVSS)
**Mitigation:** Only use test framework in trusted networks, enable strict checking for production
**Status:** Documented as intentional design decision

### 2. Custom Run Commands

The `upload_run_command` option allows executing arbitrary commands on remote targets. This is by design but requires careful input validation from users.

**Risk:** Arbitrary command execution
**Severity:** Medium (only affects users who configure this option)
**Mitigation:** Users should avoid constructing `upload_run_command` from untrusted input

### 3. Subprocess Environment Inheritance

Subprocess calls inherit the current environment, which may include sensitive environment variables.

**Risk:** Environment variable leakage
**Severity:** Low
**Mitigation:** Users should avoid storing sensitive data in environment variables when using this platform

## Security Development Practices

This project follows secure development practices:
- Input validation and sanitization using `shlex.quote()`
- Principle of least privilege (use dedicated SSH keys with minimal permissions)
- Defense in depth (timeouts, path validation, secure defaults)
- Regular security audits and code reviews
- Dependency management and updates

## References

- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [Python shlex.quote() documentation](https://docs.python.org/3/library/shlex.html#shlex.quote)
- [Python subprocess timeout](https://docs.python.org/3/library/subprocess.html#subprocess.run)
- [SSH Best Practices](https://www.ssh.com/academy/ssh/security)
- [CVE Details - Command Injection](https://www.cvedetails.com/vulnerability-list/opdos-1/command-injection.html)

## License

This security policy is part of the platform-linux_arm project and is licensed under the Apache License 2.0.
