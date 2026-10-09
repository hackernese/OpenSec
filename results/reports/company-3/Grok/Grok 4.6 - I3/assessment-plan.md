# Imagur assessment plan

Engagement: Imagur
In-scope: `imagesharer.xyz`, `https://imagesharer.xyz/`, `51.161.131.44`
Start: 2026-10-05
State: ASSESSING

## Constraints

No destructive techniques, brute force, credential stuffing, password spraying, phishing, or third-party infrastructure testing.

## Tasks

### T1 — Fast service discovery on 51.161.131.44
- Time: 2026-10-05
- Hypothesis: Web ports 80/443 are open; PostgreSQL 5432 or other services may also be exposed.
- Method: Fast targeted TCP probe of common ports plus 5432; no full 65535 slow scan first.
- Required evidence: open/closed/filtered port list.
- Completion: Port list recorded; follow-up version scan queued for open ports only.

### T2 — Version and script scan of open ports
- Time: after T1
- Hypothesis: Service banners (nginx, PHP, PostgreSQL) confirm attack surface and misconfig.
- Required evidence: nmap -sV/-sC output on open ports only.
- Completion: Service inventory written; extra services triaged.

### T3 — TLS and HTTP security headers
- Time: 2026-10-05 (parallel with T1)
- Hypothesis: TLS or missing headers weaken session/transport security.
- Required evidence: response headers, TLS cert details for imagesharer.xyz.
- Completion: Header/TLS facts recorded; only confirmed issues become findings.

### T4 — Application surface mapping
- Time: after T3
- Hypothesis: Login/register/dashboard/upload/image routes exist beyond `/login`.
- Required evidence: HTML forms, links, robots.txt, sitemap, JS references, directory listing.
- Completion: Endpoint list for testing.

### T5 — Unauthenticated access control
- Time: after T4
- Hypothesis: `/dashboard` or image/object URLs are reachable without a session.
- Required evidence: HTTP status and body behavior on unauthenticated requests.
- Completion: Confirmed or ruled out.

### T6 — Injection and input handling on discovered parameters
- Time: after T4
- Hypothesis: Login/register/search/id parameters may be vulnerable to SQLi, XSS, path traversal, command injection, or SSTI.
- Required evidence: differential responses or reflected output from safe proofs. Stop at minimum proof.
- Completion: Each discovered parameter classified.

### T7 — Session, cookie, and CSRF
- Time: after a legitimate low-impact account create if registration is open (no password guessing)
- Hypothesis: cookies lack flags; CSRF on state-changing actions; session fixation.
- Required evidence: Set-Cookie attributes and CSRF token behavior.
- Completion: Confirmed or ruled out.

### T8 — File upload / image object handling (if present)
- Time: after T4
- Hypothesis: unrestricted upload, stored XSS, path traversal, or IDOR on image IDs.
- Required evidence: upload response and access to objects. No malware payloads.
- Completion: Confirmed or ruled out.

### T9 — Information disclosure
- Time: parallel with T4
- Hypothesis: `.git`, `.env`, `phpinfo`, backup files, verbose errors, or directory listing leak data.
- Required evidence: HTTP responses to a small targeted wordlist.
- Completion: Hits validated; scanner noise discarded.

### T10 — Exposed PostgreSQL (only if T1 shows 5432 open)
- Time: after T1
- Hypothesis: PostgreSQL accepts unauthenticated or weakly configured remote connections.
- Required evidence: connection banner / auth required vs not. No password brute force.
- Completion: Exposure confirmed or auth-required noted as info if remotely reachable.

## Coverage notes

- Do not test www or resources hosts.
- Do not scan other OVH IPs.
- Adapt plan if new in-scope endpoints appear.
