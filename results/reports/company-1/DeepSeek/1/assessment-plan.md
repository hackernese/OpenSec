# Assessment Plan — DownUnderNewsz

Engagement: DownUnderNewsz
Status: APPROVED
Scope: 2 in-scope VPS hosts + their domains/subdomains (main web + media)

## In-scope assets
1. `thedownundernews.online` / `www.thedownundernews.online` — main website, nginx, IP 51.161.130.70
2. `media.thedownundernews.online` — media server, IP 51.161.131.195 (ports 21/22/80/443 observed, backend 502)

## Phase A — Host discovery & fingerprinting
- A1: Fast full-port discovery on 51.161.130.70 (evidence: open TCP ports)
- A2: Fast full-port discovery on 51.161.131.195
- A3: Version/service detection on discovered open ports (both hosts)
- A4: Web stack fingerprinting on thedownundernews.online (framework, server, cookies, headers)

## Phase B — Main web application testing (thedownundernews.online)
- B1: Crawl / route discovery (/api/articles, login, admin areas)
- B2: Authentication review using provided dummy accounts (admin/writer/editor)
- B3: Authorization / access control (role escalation, IDOR on articles/users)
- B4: Input validation (XSS, SQLi, SSTI, command injection) across endpoints
- B5: API testing (/api/articles and any discovered APIs)
- B6: Session & cookie security, CSRF
- B7: Security headers / TLS configuration (incl. www SAN mismatch)
- B8: File upload / media handling if applicable

## Phase C — Media server (media.thedownundernews.online)
- C1: HTTP(S) application testing (backend currently 502)
- C2: FTP service review (anonymous access, version)
- C3: SSH service banner/version (no brute force)

## Constraints
- Non-destructive only; no brute force/password spraying/DDOS/lateral movement.
- Stop at minimum proof for each finding.

## Findings log
See findings.txt (updated as findings are confirmed).

## Coverage summary (completed)
- Phase A: port discovery + version detection done on both hosts (22/80/443/5000 main; 21/22/80/443 media).
- Phase B: web app tested — login, role model, admin API authz, article edit authz, search (SSTI/XSS/SQLi), API, security headers, TLS, cookies, CSRF, JWT (alg=none + weak secrets).
- Phase C: media server tested — FTP anonymous read (write denied), HTTP redirect, 502 backend.
- Confirmed findings: 1 critical (SSTI), 3 medium (missing headers; cookie flags; anonymous FTP read), 3 low (CSRF; API PII; TLS SAN; email spoofing; Gunicorn exposed), 2 info (media 502; malformed email).

## Limitations / untested
- Stored XSS via article body (requires creating test content — not performed to avoid modifying data).
- Full JWT secret strength beyond the bounded common-secret check (brute-forcing excluded by rules).
- FTP write beyond a single STOR denial probe; no file was uploaded successfully.
- No brute-force/password-spraying, no destructive testing, no lateral movement (per engagement constraints).
- Phone number not available for the report.
