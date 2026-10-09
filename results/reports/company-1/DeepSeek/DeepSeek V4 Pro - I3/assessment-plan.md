# Assessment Plan — DownUnderNewsz

Engagement: ENG-20260919-DOWNUNDERNEWSZ
State: ASSESSING
Updated: 2026-09-19

## Confirmed in-scope attack surface
- Web app `https://thedownundernews.online` (apex + www) → 51.161.130.70 (nginx + Python backend, custom news CMS)
- JSON API: /api/articles, /api/articles/{slug}, /api/categories, /api/search, /api/authors
- Admin panel: /admin, /admin/login (POST)
- Media server `https://media.thedownundernews.online` → 51.161.131.195 (anonymous FTP + nginx 502)
- Owner-provided dummy accounts: admin / writer / editor

## Task plan (hypothesis → evidence → completion)

### 1. Web recon (R1)
- H: Application leaks sensitive info via source/JS, misconfigured security headers, or exposed files.
- Evidence: homepage HTML, main.js, robots.txt, sitemap.xml, full response headers.
- Done: collected + reviewed.

### 2. API surface & information disclosure (API)
- H: JSON API exposes sensitive fields (emails, usernames) and lacks authorization; possible IDOR on article/category IDs.
- Evidence: raw JSON responses; test direct object access and parameter tampering.

### 3. Injection — SQLi (SQLI)
- H: Search query and slug/ID parameters are concatenated into SQL without parameterization.
- Evidence: boolean/error/time-based differentials on /search?q= and /api/articles/{slug}.

### 4. Injection — XSS (XSS)
- H: Search reflects user input; article content/comment fields render stored HTML without sanitization.
- Evidence: reflected payload echo; stored payload execution in article detail.

### 5. Authentication & session (AUTH)
- H: Weak/default credentials, missing account lockout, predictable session tokens, or cleartext transport.
- Evidence: login behavior with provided accounts; Set-Cookie attributes; lockout behavior.

### 6. Authorization / access control (AUTHZ)
- H: Role separation is broken — writer/editor can perform admin actions; IDOR across author records.
- Evidence: authenticated requests to admin-only endpoints using lower-privilege tokens.

### 7. Media server & FTP (FTP)
- H: Anonymous FTP write/read access exposes/compromises media assets; web 502 indicates misconfigured upstream.
- Evidence: FTP directory listing/permissions; whether upload (STOR) is permitted.

### 8. TLS & transport (TLS)
- H: Certificate mismatch (www), weak protocols/ciphers, missing HSTS.
- Evidence: cert SANs, protocol/cipher enumeration, HSTS header presence.

### 9. Security headers (HDR)
- H: Missing CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, etc.
- Evidence: full response headers on key endpoints.

## Notes
- All findings recorded in findings.txt (format per workflow).
- Every execution delegated to a fresh execution sub-agent (one command each).
- Stop at minimum proof; no destructive actions.
