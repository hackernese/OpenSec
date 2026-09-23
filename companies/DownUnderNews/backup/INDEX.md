# Documentation Index

Complete guide to the intentionally vulnerable e-commerce application.

## 📋 Quick Navigation

### Getting Started
1. **[README.md](README.md)** - Start here for overview and quick start
2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup and testing instructions
3. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Understanding the codebase

### Vulnerability Documentation
4. **[VULNERABILITIES_SUMMARY.md](VULNERABILITIES_SUMMARY.md)** - Quick reference (recommended first read)
5. **[ALL_VULNERABILITIES.md](ALL_VULNERABILITIES.md)** - Complete exploitation guide
6. **[SAMPLE_PAYLOADS.md](SAMPLE_PAYLOADS.md)** - Ready-to-use attack payloads

### Testing
7. **[test-vulnerabilities.sh](test-vulnerabilities.sh)** - Automated test script

---

## 📚 Document Summaries

### README.md
**Purpose**: Main entry point and overview  
**Contents**:
- Application description
- Vulnerability overview (7 types)
- Quick start with Docker
- API endpoints list (45+ routes)
- Basic testing examples
- Technology stack

**Best for**: First-time users, quick reference

---

### SETUP_GUIDE.md
**Purpose**: Comprehensive setup and testing guide  
**Contents**:
- Step-by-step Docker setup
- Admin account creation methods
- Individual vulnerability testing procedures
- Tool configuration (SQLMap, Burp Suite, ZAP)
- Troubleshooting common issues
- Security considerations

**Best for**: Detailed implementation, troubleshooting

---

### PROJECT_STRUCTURE.md
**Purpose**: Codebase organization and architecture  
**Contents**:
- Complete directory tree
- File-by-file descriptions
- Database schema details
- Technology stack breakdown
- Dependency list
- Vulnerability location mapping
- Environment variable reference

**Best for**: Understanding the code, locating vulnerabilities

---

### VULNERABILITIES_SUMMARY.md
**Purpose**: Quick reference for all vulnerabilities  
**Contents**:
- Vulnerability comparison table
- One-liner exploit examples
- Impact summary by vulnerability
- Remediation checklists
- Testing tool recommendations
- CVSS severity ratings

**Best for**: Quick lookup, teaching reference

---

### ALL_VULNERABILITIES.md
**Purpose**: Complete vulnerability documentation  
**Contents**:
- Detailed analysis of all 7 vulnerabilities
- Multiple exploitation techniques per vulnerability
- Impact assessments (CIA triad)
- Secure code examples
- Remediation best practices
- Detection methods
- OWASP references

**Best for**: In-depth learning, security training

---

### SAMPLE_PAYLOADS.md
**Purpose**: Ready-to-use attack payloads  
**Contents**:
- Categorized payload lists
- Basic to advanced techniques
- Complete cURL commands
- Encoding variations for WAF bypass
- Testing workflow recommendations
- Safety reminders

**Best for**: Hands-on testing, payload library

---

### test-vulnerabilities.sh
**Purpose**: Automated vulnerability testing  
**Contents**:
- Bash script for all 7 vulnerabilities
- Automated admin setup
- Color-coded output
- Test result validation
- Usage instructions

**Best for**: Quick validation, CI/CD integration

---

## 🎯 Recommended Reading Paths

### For Security Students
1. README.md (overview)
2. VULNERABILITIES_SUMMARY.md (quick reference)
3. ALL_VULNERABILITIES.md (deep dive)
4. SAMPLE_PAYLOADS.md (practice)
5. SETUP_GUIDE.md (hands-on testing)

### For Penetration Testers
1. VULNERABILITIES_SUMMARY.md (quick assessment)
2. SAMPLE_PAYLOADS.md (exploitation)
3. test-vulnerabilities.sh (automated testing)
4. ALL_VULNERABILITIES.md (detailed techniques)

### For Developers
1. README.md (overview)
2. PROJECT_STRUCTURE.md (codebase understanding)
3. ALL_VULNERABILITIES.md (secure coding examples)
4. SETUP_GUIDE.md (local testing)

### For Instructors
1. README.md (course overview)
2. VULNERABILITIES_SUMMARY.md (teaching reference)
3. ALL_VULNERABILITIES.md (detailed explanations)
4. SAMPLE_PAYLOADS.md (student exercises)
5. SETUP_GUIDE.md (lab setup)

---

## 🔍 Finding Information

### "How do I get started?"
→ **README.md** - Quick start section

### "How do I test vulnerability X?"
→ **SETUP_GUIDE.md** - Individual vulnerability testing sections

### "What are the exploit payloads?"
→ **SAMPLE_PAYLOADS.md** - Organized by vulnerability type

### "Where is vulnerability X in the code?"
→ **PROJECT_STRUCTURE.md** - Vulnerability locations section

### "What's the impact of vulnerability X?"
→ **ALL_VULNERABILITIES.md** or **VULNERABILITIES_SUMMARY.md**

### "How do I fix vulnerability X?"
→ **ALL_VULNERABILITIES.md** - Remediation sections

### "What tools can I use?"
→ **VULNERABILITIES_SUMMARY.md** - Testing tools section

### "How do I set up the database?"
→ **SETUP_GUIDE.md** - Setup instructions section

---

## 📊 Vulnerability Quick Reference

| # | Type | File | Endpoint | Doc Section |
|---|------|------|----------|-------------|
| 1 | SQL Injection | products.js | /api/products/search | All docs |
| 2 | OS Command Injection | admin.js | /api/admin/system-info | All docs |
| 3 | OS Command Injection | admin.js | /api/admin/export-logs | All docs |
| 4 | OS Command Injection | admin.js | /api/admin/backup | All docs |
| 5 | XXE Injection | reports.js | /api/reports/upload-sales | All docs |
| 6 | XXE Injection | reports.js | /api/reports/import-products | All docs |
| 7 | XPath Injection | search.js | /api/search/users | All docs |

---

## 🛠️ Key Commands

```bash
# Start application
docker-compose up -d

# Run automated tests
./test-vulnerabilities.sh

# View API logs
docker-compose logs -f api

# Access database
docker exec -it ecommerce_mysql mysql -u ecommerce_user -pecommerce_pass ecommerce_db

# Stop application
docker-compose down

# Rebuild from scratch
docker-compose down -v && docker-compose up -d --build
```

---

## 🎓 Educational Use

### Learning Objectives
- Understand common web application vulnerabilities
- Practice exploitation techniques safely
- Learn secure coding practices
- Understand vulnerability remediation
- Develop security testing skills

### Topics Covered
- OWASP Top 10 vulnerabilities
- Injection attacks (SQL, OS Command, XXE, XPath)
- Authentication and authorization
- Input validation and sanitization
- Secure coding best practices
- Security testing methodologies

### Prerequisites
- Basic understanding of web applications
- Familiarity with HTTP/REST APIs
- Command line proficiency
- Basic SQL knowledge
- Understanding of XML and XPath (for XXE/XPath)

---

## ⚠️ Important Warnings

### DO NOT
❌ Deploy to production  
❌ Expose to the internet  
❌ Use with real user data  
❌ Use without authorization  
❌ Test on third-party systems  

### DO
✅ Use in isolated test environments  
✅ Practice ethical hacking  
✅ Learn secure coding  
✅ Obtain proper authorization  
✅ Follow responsible disclosure  

---

## 📞 Support and Resources

### Issues
If you find any issues with the documentation or setup:
1. Check SETUP_GUIDE.md troubleshooting section
2. Review docker-compose logs
3. Verify environment variables in .env

### Learning Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackTheBox](https://www.hackthebox.com/)
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)

### Security Standards
- CWE (Common Weakness Enumeration)
- CVE (Common Vulnerabilities and Exposures)
- CVSS (Common Vulnerability Scoring System)
- OWASP Testing Guide
- SANS Top 25

---

## 📈 Version Information

**Application Version**: 1.0.0  
**Last Updated**: 2024  
**Node.js Version**: 18+  
**MySQL Version**: 8.0  

---

## 🔒 Security Disclaimer

This application is intentionally vulnerable and designed exclusively for educational and security testing purposes. The creators and contributors are not responsible for any misuse or damage caused by this software. Users must ensure compliance with applicable laws and regulations, obtain proper authorization before testing, and use the application only in controlled, isolated environments.

---

**Happy (Ethical) Hacking! 🎯**
