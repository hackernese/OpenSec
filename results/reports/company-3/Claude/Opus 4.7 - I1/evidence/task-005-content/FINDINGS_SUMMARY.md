# Content Discovery & Info-Disclosure Assessment - Imagur
**Company**: Imagur  
**Targets**: 
- https://imagesharer.xyz/ (nginx + PHP/8.2.33, port 443)
- http://51.161.131.44:8080/ (Apache 2.4.68 + PHP/8.2.33, port 8080)  
**Task ID**: task-005-content  
**Date**: 2026-09-18

---

## Executive Summary

Critical information disclosure vulnerability detected on both targets. An accessible JavaScript file (`/js/awsvalid.js`) contains **hardcoded AWS credentials in comments**, providing potential unauthorized access to AWS infrastructure. Both instances show identical response headers and routing behavior, confirming synchronized deployment.

---

## Detailed Findings

### 1. CRITICAL: Exposed AWS Credentials in Source Code
**Status**: 200 OK (accessible)  
**File**: `/js/awsvalid.js` (5.2 KB on both targets)  
**Severity**: CRITICAL

#### Discovery Details:
- Path returns HTTP 200 on both HTTPS (443) and HTTP (8080)
- Contains hardcoded AWS credentials in JavaScript comments:
  - **Access Key**: `AKIAQHQ6PGM62T2FFPGU`
  - **Secret Key**: `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`
  - **Region**: `ap-southeast-2`

#### Business Impact:
- Potential unauthorized access to AWS resources
- Possible lateral movement into cloud infrastructure
- Data exfiltration risks
- Credential compromise for application services

#### Recommendation:
1. **Immediate**: Revoke exposed AWS credentials in IAM console
2. Rotate all associated access keys and secret keys
3. Remove hardcoded credentials from source code
4. Implement environment-based credential management (AWS SSO, instance profiles, or AWS Secrets Manager)
5. Add `.js` files to `.gitignore` or implement credential scanning in CI/CD
6. Review CloudTrail logs for any unauthorized access using these credentials
7. Re-deploy application with fresh credentials

---

### 2. Framework & Technology Identification

#### Server Headers (Both Targets):
```
HTTPS (443):
  Server: nginx
  X-Powered-By: PHP/8.2.33
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin

HTTP (8080):
  Server: Apache/2.4.68 (Debian)
  X-Powered-By: PHP/8.2.33
  [Same security headers as above]
```

#### Framework Indicators:
- **Name**: "Imager" (identified from page titles: "Log in — Imager", "Create account — Imager")
- **Technology Stack**: PHP 8.2.33, Laravel-like structure (referenced in commented scripts)
- **Architecture**: Custom-built image sharing application

---

### 3. Authentication & Session Structure

#### Login Page (`/login`)
- Status: **200 OK**
- Form: POST `/login`
- Fields: `email`, `password`
- **Missing**: No CSRF tokens found in HTML
- **Missing**: No visible session cookie management in page

#### Register Page (`/register`)
- Status: **200 OK**
- Form: POST `/register`
- Fields: `email`, `password`, `confirm`
- Password requirement: Minimum 8 characters
- **Missing**: No CSRF tokens found
- **Missing**: No session/cookie references

#### Dashboard (`/dashboard`)
- Status: **302 Redirect** → `/login` (unauthenticated redirect)
- Access control: Confirmed (redirects to login)

#### Profile (`/profile`)
- Status: **302 Redirect** → `/login`
- Access control: Confirmed

---

### 4. HTTP Status Code Distribution

#### 200 OK Responses (Content Accessible):
1. `/login` (2,140 bytes) - Login form
2. `/register` (2,595 bytes) - Registration form
3. `/js/awsvalid.js` (5,298 bytes) - **CRITICAL - Contains AWS credentials**

#### 301/302 Redirects:
- `/` → `/dashboard` (302 redirect)
- `/dashboard` → `/login` (302 redirect, requires auth)
- `/profile` → `/login` (302 redirect, requires auth)
- `/css` → `/css/` (301 redirect)
- `/js` → `/js/` (301 redirect)
- `/uploads` → `/uploads/` (301 redirect)

#### 403 Forbidden (Directory Access Denied):
- `/.hta`, `/.htaccess`, `/.htpasswd`
- `/css/`, `/js/`, `/uploads/` (directory listings blocked)
- `/server-status` (both targets)

#### 404 Not Found (All Targets):
All probed sensitive files returned 404, including:
- `.env*` variants (development config)
- `.git/` (version control)
- `composer.json`, `package.json` (dependencies)
- `phpinfo.php`, `info.php` (server info)
- Admin paths (`/admin/`, `/administrator/`, `/phpmyadmin/`)
- API documentation (`swagger.json`, `openapi.json`)
- Backup files (`.zip`, `.tar.gz`, `.sql`)
- Database files and logs

---

### 5. Directory Structure (via ffuf)

**Discovered Paths**:
```
✓ / (302 to /dashboard)
✓ /css/ (301, directory index forbidden)
✓ /js/ (301, directory index forbidden)
✓ /uploads/ (301, directory index forbidden)
✓ /login (200)
✓ /register (200)
✓ /dashboard (302 to /login - auth required)
✓ /profile (302 to /login - auth required)
✗ /server-status (403)
✗ .hta, .htaccess, .htpasswd (403)
```

**Not Discovered** (404):
- `/admin`, `/admin/`, `/administrator/`, `/api/`, `/phpmyadmin/`
- Standard dotfiles and config files

---

### 6. Security Headers Assessment

Both targets implement good security headers:
- ✅ `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- ✅ `X-Frame-Options: DENY` - Prevents clickjacking
- ✅ `X-XSS-Protection: 1; mode=block` - XSS protection enabled
- ✅ `Referrer-Policy: strict-origin-when-cross-origin` - Referrer leakage prevention
- ⚠️ **Missing**: `Strict-Transport-Security` (HTTPS only)
- ⚠️ **Missing**: `Content-Security-Policy`
- ⚠️ **Missing**: `Permissions-Policy`

---

### 7. Cookie & Session Management

**Findings**:
- No explicit cookie flags visible in HTTP headers during GET requests
- Forms lack visible CSRF tokens in HTML source
- Session establishment would occur during POST operations (not tested per scope)

**Observations**:
- Login/Register forms lack CSRF tokens in visible HTML source (potential CSRF vulnerability)
- Session cookies likely set on POST response (not captured in current testing scope)

---

### 8. Information Disclosure Vectors

### Successfully Exploited:
| Path | Status | Size | Content Type | Disclosure |
|------|--------|------|--------------|-----------|
| `/js/awsvalid.js` | 200 | 5.3 KB | application/javascript | **AWS Access Key + Secret Key + Region** |

### Blocked (403 Forbidden):
| Path | Size | Note |
|------|------|------|
| `/.htaccess` | 320 | Apache config protection working |
| `/.htpasswd` | 320 | Password file protection working |
| `/server-status` | 320 | Apache status page blocked |

### Not Present (404):
- All `.env*` files
- All `.git*` files
- All backup/dump files
- Configuration files
- Admin panels

---

### 9. Port Comparison (443 vs 8080)

Both targets return **identical results** for all probed paths:
- Same HTTP status codes
- Same security headers (except Server version)
- Same responsive structure
- Same file accessibility
- **Same vulnerability** - AWS credentials exposed on both

| Aspect | HTTPS (443) | HTTP (8080) |
|--------|------------|-----------|
| Server | nginx | Apache 2.4.68 |
| PHP Version | 8.2.33 | 8.2.33 |
| Security Headers | Identical | Identical |
| `/js/awsvalid.js` | 200 ✓ | 200 ✓ |
| AWS Credentials | Present | Present |

**Conclusion**: Both targets run the **same application instance** with different reverse proxies/web servers.

---

### 10. Missing Security Controls

1. **CSRF Protection**: No visible tokens in forms
2. **HTTPS Enforcement**: HTTP (8080) accepts unencrypted traffic with credentials
3. **API Documentation**: No public API spec discoverable
4. **Version Control Exposure**: `.git/` is blocked (good)
5. **Configuration Files**: Not publicly accessible (good)
6. **Source Code Comments**: Contain hardcoded secrets (critical issue)

---

## Artifact Files Generated

```
/home/research/Projects/Imagur/evidence/task-005-content/
├── 443-awsvalid.txt .......................... [CRITICAL - AWS credentials]
├── 443-headers-root.txt ..................... Security headers (HTTPS)
├── 443-headers-login.txt .................... Login page headers
├── 443-login.html ........................... Login form (2.1 KB)
├── 443-register.html ........................ Registration form (2.6 KB)
├── 443-css-app.txt .......................... Application CSS (14 KB)
├── 443-root.html ............................ Root redirect (0 bytes)
├── 443-dashboard.html ....................... Dashboard access denied (0 bytes)
├── 443-password_reset.html .................. Password reset (434 bytes - 404)
├── 443-forgot.html .......................... Forgot password (434 bytes - 404)
├── 443-server_status.txt .................... Apache status (320 bytes - 403)
├── 443-htaccess.txt ......................... .htaccess blocked (320 bytes - 403)
├── 443-htpasswd.txt ......................... .htpasswd blocked (320 bytes - 403)
├── [... 60+ additional probed paths ...]
├── 8080-* .................................... Parallel tests on port 8080
├── ffuf-443.json ............................ ffuf directory brute force results
└── FINDINGS_SUMMARY.md ...................... This report

Total evidence files: 140+
```

---

## Remediation Priority

### CRITICAL (Immediate Action Required):
1. **Revoke AWS credentials** - AKIAQHQ6PGM62T2FFPGU / c7njNpv1oT3rhBhUHue2e2d+oIFnw7QDgCmTtPCG
2. Remove hardcoded credentials from `/js/awsvalid.js`
3. Re-deploy with environment-based credential management

### HIGH:
1. Add CSRF tokens to login/register forms
2. Implement `Strict-Transport-Security` header (enforce HTTPS)
3. Add `Content-Security-Policy` header
4. Review AWS CloudTrail for unauthorized access

### MEDIUM:
1. Remove commented-out script references in HTML
2. Implement additional security headers (Permissions-Policy)
3. Review CORS policy if APIs are exposed
4. Add rate limiting on authentication endpoints

---

## Summary Statistics

- **Paths Tested**: 60+ unique paths
- **Successful Discoveries**: 3 (login, register, AWS credentials)
- **Critical Vulnerabilities**: 1
- **High Risk Issues**: 2
- **Info-Disclosure Vectors**: 1 exploited
- **False Positives**: 0

