# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in platform-linux_arm, please report it by:

1. **GitHub Security**: Use GitHub's private vulnerability reporting (preferred)
   - Navigate to the repository's Security tab
   - Click "Report a vulnerability"
   - Fill out the security advisory form

2. **Email**: Contact the maintainer with subject "Security: platform-linux_arm"

**Do NOT** open public issues for security vulnerabilities.

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Critical issues patched within 30 days

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.7.x   | Yes       |
| 1.6.x   | Yes       |
| < 1.6   | No        |

## Security Features

See [SECURITY.md](SECURITY.md) for security documentation, including:

- Command injection protection
- Timeout protection against DoS attacks
- SSH host key verification
- Security best practices for remote operations
- Configuration guidelines

## Recent Security Improvements

**Version 1.7.1 (November 2025)**:
- Fixed command injection vulnerabilities (CVSS 8.0-9.0)
- Added timeout protection to all subprocess calls
- Added security documentation
- Enhanced SSH security features

For detailed security audit history, see [SECURITY.md](SECURITY.md#security-audit-history).

## Security Best Practices

When using this platform:

- Use SSH key-based authentication (not passwords)
- Configure appropriate timeouts for network operations
- Enable host key verification in production environments
- Use dedicated SSH keys for different environments
- Never commit credentials or private keys to version control

For complete security guidelines, see [SECURITY.md](SECURITY.md).

## License

This security policy is part of the platform-linux_arm project and is licensed under the Apache License 2.0.
