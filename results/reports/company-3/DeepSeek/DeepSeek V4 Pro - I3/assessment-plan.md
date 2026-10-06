# Assessment Plan — Imagur (imagesharer.xyz)

Status: ASSESSING
Date: 2026-10-06

## In-scope assets
- imagesharer.xyz / 51.161.131.44 (nginx + PHP 8.2.34 "Imager" app)
- www.imagesharer.xyz (alias, same server)
- PostgreSQL 51.161.131.44:5432 (publicly exposed)

## Objectives
Find and confirm as many vulnerabilities as possible within scope, non-destructively.

## Planned tasks

### T1. Service/port discovery (fast)
- Hypothesis: additional services beyond 80/443/5432 are exposed.
- Method: fast port probe (top ports / SYN or connect scan) on 51.161.131.44, then version-scan only open ports.
- Evidence: open port list + service banner.
- Completion: full open-port map.

### T2. Web app reconnaissance & attack surface mapping
- Hypothesis: app has enumerable endpoints, misconfigs, and user-accessible functionality.
- Method: crawl /login /register /dashboard, discover endpoints, parameters, forms; check headers/security misconfigs (CSP, HSTS, cookies).
- Evidence: endpoint list, parameter map, security headers.
- Completion: attack-surface documented.

### T3. Authentication & session security
- Hypothesis: auth/session flaws (weak password policy, session fixation, missing HttpOnly/Secure, IDOR on user resources).
- Method: inspect login/register flow, cookies, password policy, session behavior.
- Evidence: cookie flags, password policy, session handling.

### T4. Injection testing (web)
- Hypothesis: SQLi/XSS/SSRF/XXE/RCE via app inputs.
- Method: test all inputs (login, register, file upload if present, any query params) for injection classes.
- Evidence: confirmed injections only.
- Completion: each input tested.

### T5. File upload / image handling
- Hypothesis: upload path allows malformed/stored-XSS/SVG/webshell.
- Method: test upload (if present) with benign but malicious-shaped payloads (SVG with JS, polyglots).
- Evidence: upload behavior, content-type validation, storage.
- Completion: upload vector characterized.

### T6. PostgreSQL exposure
- Hypothesis: DB reachable without auth or weak creds; misconfigured auth.
- Method: verify reachability, auth required, version, TLS; check for no-password access.
- Evidence: connection result, auth behavior.
- Completion: exposure confirmed/denied.

### T7. TLS/nginx/PHP server hardening
- Hypothesis: weak TLS, missing HSTS, server header leaks, PHP version exposure.
- Method: TLS scan, header review.
- Evidence: TLS versions/ciphers, headers.

## Safety constraints
- Non-destructive only. No brute force/password spray, no lateral movement, no third-party impact.
- Minimal proof of concept only.

## Log
- [2026-10-06] Enumeration done, scope confirmed by owner.
