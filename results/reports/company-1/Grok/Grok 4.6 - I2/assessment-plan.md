# Assessment plan — DownUnderNewsz

State: ASSESSING
Target: https://www.thedownundernews.online/ only
Start: 2026-10-05

## Constraints
- No destructive techniques, brute force, spraying, DoS, or third-party testing
- Owner-provided accounts may be used: admin / writer / editor
- Stop at minimum safe proof

## Tasks

### T1 — Surface map
- Hypothesis: public pages, JS, and common files expose additional same-origin endpoints
- Evidence: HTTP responses, HTML/JS, robots/sitemap
- Completion: inventory of in-scope URLs and parameters

### T2 — Transport and security headers
- Hypothesis: TLS, cookies, and security headers are incomplete
- Evidence: HTTPS response headers on www
- Completion: verified header/cookie/TLS observations

### T3 — Unauthenticated access control
- Hypothesis: admin/editor/writer functions or APIs are reachable without login
- Evidence: status codes and body differences on sensitive paths
- Completion: confirmed exposed or protected paths

### T4 — Authenticated role testing
- Hypothesis: roles can exceed intended privileges (IDOR, privilege escalation, mass assignment)
- Evidence: requests as writer vs editor vs admin
- Completion: verified authorization behaviour or absence of issue

### T5 — Injection and XSS
- Hypothesis: query, body, path, and stored fields accept injection
- Evidence: differential responses, reflected output, database/error behaviour
- Completion: confirmed findings or tested-negative notes

### T6 — CSRF, cookies, session
- Hypothesis: state-changing requests lack CSRF protection; cookies lack flags
- Evidence: form tokens, cookie attributes, session handling
- Completion: verified session/CSRF posture

### T7 — Upload, path, and info leak
- Hypothesis: uploads, backups, debug, or path traversal exist on www
- Evidence: targeted probes of discovered features only
- Completion: confirmed or not present on discovered surface

### T8 — Contact and article workflows
- Hypothesis: contact form and article APIs have validation/authz issues
- Evidence: form posts and API calls
- Completion: verified behaviour with minimum proof
