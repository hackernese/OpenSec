# AuSecurity assessment plan

State: ASSESSING
Date: 2026-10-05
In-scope: ausecurity.best, www, contact, blog, ticket, and IPs 51.79.166.148, 51.79.167.208, 51.79.166.209

## T1 Fast port probe — 51.79.166.148
- Hypothesis: extra services besides HTTP/HTTPS are exposed on the main VPS.
- Required evidence: open TCP ports from a fast top-ports scan.
- Completion: list of open ports, no full 65535 scan unless needed.

## T2 Fast port probe — 51.79.167.208
- Hypothesis: blog VPS exposes more than HTTP/HTTPS.
- Required evidence: open TCP ports.
- Completion: open port list.

## T3 Fast port probe — 51.79.166.209
- Hypothesis: ticket VPS exposes more than HTTP/HTTPS.
- Required evidence: open TCP ports.
- Completion: open port list.

## T4 Version scan on discovered ports (per IP, after T1-T3)
- Hypothesis: outdated or vulnerable services are running.
- Required evidence: nmap service/version output for open ports only.

## T5 Main site surface mapping
- Hypothesis: admin pages, APIs, and misconfigured paths are reachable.
- Required evidence: HTTP status, titles, headers, robots, common paths.

## T6 TLS configuration on apex/www/contact
- Hypothesis: self-signed cert, hostname mismatch, and CA:TRUE increase intercept risk.
- Required evidence: certificate fields and handshake behavior.

## T7 Auth API and login/dashboard access control
- Hypothesis: authentication endpoints or dashboard are weakly protected.
- Required evidence: unauthenticated responses, session handling. No brute force.

## T8 Contact API / form
- Hypothesis: injection, missing CSRF, or information leakage on /api/contact.
- Required evidence: request/response behavior with safe payloads.

## T9 WordPress blog assessment
- Hypothesis: default/misconfigured WordPress with known issues.
- Required evidence: version, users (no brute force), plugins, xmlrpc, directory listing.

## T10 osTicket installer
- Hypothesis: public installer allows takeover of the ticket system.
- Required evidence: installer page reachable; stop after minimum proof. Do not complete install.

## T11 Security headers and cookie flags
- Hypothesis: missing security headers across sites.
- Required evidence: response header sets.

## T12 Email authentication DNS
- Hypothesis: missing SPF/DMARC enables spoofing of ausecurity.best.
- Required evidence: TXT/MX/DMARC lookup.

Adapt after each result. Confirm findings only with in-scope, reproducible, concrete impact.

## Coverage status (2026-10-05)

Completed:
- T1-T4 port/version scans on the three IPs
- T5-T8 main site paths, TLS, auth API, contact API
- T9 WordPress checks (wpscan API token unavailable; manual checks done)
- T10 osTicket installer (not submitted)
- T11 headers/cookies
- T12 email DNS

Not done (limits):
- No password guessing, spraying, or default-credential attacks
- No completion of osTicket install
- No XML-RPC pingback against third parties
- No full 65535 port sweep
- wpscan vulnerability API not available

State: VALIDATING then REPORTING

