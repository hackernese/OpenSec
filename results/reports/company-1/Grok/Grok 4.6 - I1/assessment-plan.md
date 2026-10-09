# Assessment plan — DownUnderNewsz

State: ASSESSING
Started: 2026-09-18
In-scope: thedownundernews.online, www.thedownundernews.online, media.thedownundernews.online, 51.161.130.70, 51.161.131.195

## T1 — Fast full-port probe of 51.161.130.70
- Hypothesis: services besides 80/443/22 are exposed on the web VPS
- Time: 2026-09-18
- Evidence: open TCP ports
- Completion: all-port list without version scan

## T2 — Fast full-port probe of 51.161.131.195
- Hypothesis: media VPS exposes FTP/SSH/HTTP plus other ports
- Time: 2026-09-18
- Evidence: open TCP ports
- Completion: all-port list without version scan

## T3 — Version/service scan of open ports on 51.161.130.70
- Hypothesis: outdated or misconfigured services
- Evidence: product/version banners
- Completion: versions recorded; no exploit attempted beyond banner

## T4 — Version/service scan of open ports on 51.161.131.195
- Hypothesis: FTP/SSH/nginx versions identifiable
- Evidence: product/version banners
- Completion: versions recorded

## T5 — HTTP/TLS/security headers on apex
- Hypothesis: missing security headers, TLS issues, info leaks
- Evidence: response headers, TLS details
- Completion: header set documented

## T6 — Web path and API discovery on apex
- Hypothesis: unlinked admin, API, upload, backup, debug endpoints exist
- Evidence: live paths/status codes
- Completion: attack surface list for authenticated and unauthenticated tests

## T7 — Media host despite 502
- Hypothesis: alternate paths or methods bypass 502; origin misconfig
- Evidence: status codes on common paths
- Completion: media surface documented

## T8 — Authentication and role testing with owner-provided dummy accounts
- Hypothesis: weak session, privilege issues between admin/writer/editor
- Evidence: login responses, role-gated pages
- Completion: auth flows mapped; no brute force

## T9 — Input/access control testing on discovered endpoints
- Hypothesis: injection, XSS, IDOR, CSRF, file issues, info disclosure
- Evidence: safe proof of each confirmed issue
- Completion: each hypothesis validated or rejected

## Constraints
No DDoS, brute force, spraying, phishing, malware, third-party, or destructive tests.
