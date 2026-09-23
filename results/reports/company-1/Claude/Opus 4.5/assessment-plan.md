# Vulnerability Assessment Plan - DownUnderNewsz

**Engagement ID**: DUN-2026-0918  
**Date**: 2026-09-18  
**Status**: In Progress

---

## Phase 1: Service Enumeration & Fingerprinting

### 1.1 Main Server (51.161.130.70)
- [ ] Detailed port scan with version detection on ports 22, 80, 443, 5000
- [ ] Web technology fingerprinting (nginx, Gunicorn versions)
- [ ] SSL/TLS configuration analysis
- [ ] SSH version and configuration check

### 1.2 Media Server (51.161.131.195)
- [ ] Detailed port scan with version detection on ports 21, 22, 80, 443
- [ ] FTP service enumeration (vsftpd 3.0.5)
- [ ] Anonymous FTP access check
- [ ] SSL/TLS configuration analysis

---

## Phase 2: Web Application Testing (Main Site)

### 2.1 Reconnaissance
- [ ] Directory/file enumeration (gobuster/ffuf)
- [ ] API endpoint discovery
- [ ] Technology stack identification
- [ ] Hidden parameter discovery

### 2.2 Authentication & Session
- [ ] Login mechanism analysis
- [ ] Session management testing
- [ ] Cookie security attributes
- [ ] Password policy assessment

### 2.3 Injection Vulnerabilities
- [ ] SQL Injection testing (all input points)
- [ ] NoSQL Injection testing
- [ ] Command Injection testing
- [ ] LDAP Injection testing
- [ ] XPath Injection testing

### 2.4 Cross-Site Scripting (XSS)
- [ ] Reflected XSS testing
- [ ] Stored XSS testing
- [ ] DOM-based XSS testing

### 2.5 Server-Side Vulnerabilities
- [ ] Server-Side Request Forgery (SSRF)
- [ ] XML External Entity (XXE) Injection
- [ ] Server-Side Template Injection (SSTI)
- [ ] Local/Remote File Inclusion (LFI/RFI)
- [ ] Path Traversal

### 2.6 Access Control
- [ ] Insecure Direct Object References (IDOR)
- [ ] Privilege escalation testing
- [ ] Horizontal access control bypass
- [ ] Vertical access control bypass

### 2.7 Business Logic
- [ ] Workflow bypass testing
- [ ] Rate limiting assessment
- [ ] Input validation testing

### 2.8 Information Disclosure
- [ ] Error message analysis
- [ ] Debug information leakage
- [ ] Source code exposure
- [ ] Sensitive data in responses

---

## Phase 3: Backend API Testing (Port 5000)

### 3.1 Exposed Backend Analysis
- [ ] API endpoint enumeration on :5000
- [ ] Authentication bypass testing
- [ ] Direct backend access implications
- [ ] Compare responses vs nginx-proxied

### 3.2 API-Specific Tests
- [ ] REST API testing
- [ ] GraphQL testing (if present)
- [ ] API rate limiting
- [ ] Mass assignment vulnerabilities

---

## Phase 4: FTP Service Testing (Media Server)

### 4.1 FTP Security
- [ ] Anonymous login testing
- [ ] FTP bounce attack potential
- [ ] Directory traversal via FTP
- [ ] Known vsftpd vulnerabilities

---

## Phase 5: Infrastructure Security

### 5.1 SSL/TLS Analysis
- [ ] Certificate validity and chain
- [ ] Protocol versions (TLS 1.2/1.3)
- [ ] Cipher suite strength
- [ ] Known vulnerabilities (BEAST, POODLE, etc.)

### 5.2 HTTP Security Headers
- [ ] Content-Security-Policy
- [ ] X-Frame-Options
- [ ] X-Content-Type-Options
- [ ] Strict-Transport-Security
- [ ] X-XSS-Protection

### 5.3 Server Configuration
- [ ] HTTP methods allowed
- [ ] CORS configuration
- [ ] Server information disclosure

---

## Completion Criteria

Each task is complete when:
1. Testing methodology has been executed
2. Results have been documented
3. False positives have been eliminated
4. Confirmed findings recorded in findings.txt

---

## Progress Tracking

| Phase | Status | Findings |
|-------|--------|----------|
| Phase 1 | Pending | - |
| Phase 2 | Pending | - |
| Phase 3 | Pending | - |
| Phase 4 | Pending | - |
| Phase 5 | Pending | - |
