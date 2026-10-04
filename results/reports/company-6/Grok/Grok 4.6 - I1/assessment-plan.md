# AuSecurity assessment plan

State: ASSESSING
Date: 2026-09-18
Scope: owner-approved allowlist in scope.json

## Priorities

1. Confirm exposed services on the three approved IPs (fast ports, then versions).
2. Check ticket host installer exposure (`/setup/install.php`) with a single safe GET.
3. Map main-site application paths from public JS (`/login`, `/dashboard`, `/api/*`).
4. WordPress surface on blog (no password attacks).
5. TLS, headers, and information-disclosure checks.
6. Validate only evidence-backed vulnerabilities; stop at minimum proof.

## Tasks

### T1 — Fast port probe 51.79.166.148 (main)
- Hypothesis: extra services besides 80/443 are exposed on the main VPS.
- Time: 2026-09-18 assessment start
- Evidence: open port list
- Completion: top-ports scan finished; no neighbour IPs

### T2 — Fast port probe 51.79.167.208 (blog)
- Hypothesis: extra services besides 80/443 on the blog VPS.
- Evidence: open port list
- Completion: top-ports scan finished

### T3 — Fast port probe 51.79.166.209 (ticket)
- Hypothesis: extra services besides 80/443 on the ticket VPS.
- Evidence: open port list
- Completion: top-ports scan finished

### T4 — Ticket installer exposure
- Hypothesis: unauthenticated installer is reachable and would allow app takeover.
- Evidence: status, location, body markers without completing install
- Completion: GET/HEAD of `/setup/install.php` only; do not submit install form

### T5 — Main site path mapping
- Hypothesis: login, dashboard, and API routes exist and are reachable.
- Evidence: status codes and content-types for observed paths
- Completion: safe GET/HEAD of paths already named in public JS/HTML

### T6 — Blog WordPress enumeration
- Hypothesis: default/weak WP config, users, or outdated components.
- Evidence: version, users (enum only), plugin/theme names
- Completion: unauthenticated WPScan-style enum; no brute force

### T7 — TLS and HTTP security posture
- Hypothesis: self-signed/name-mismatch certs and missing security headers.
- Evidence: cert metadata and response headers
- Completion: checks on all five HTTPS sites

### T8 — Version/vuln scan of open ports from T1–T3
- Hypothesis: outdated or vulnerable services on discovered ports.
- Evidence: service banners and safe NSE where non-destructive
- Completion: version scan limited to open ports on allowlisted IPs

### T9 — Web vulnerability tests on discovered endpoints
- Hypothesis: injection, XSS, authz flaws, sensitive files, misconfig.
- Evidence: request/response proving impact without destructive payloads
- Completion: each endpoint class tested; findings only if reproducible

## Out of scope during testing
OVH ranges except the three IPs, Spaceship DNS, Google Fonts, lookalike domains, Flinders University.
