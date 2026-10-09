# Imagur — Vulnerability Assessment Plan

Engagement directory: `/home/research/Projects/Imagur`
Scope approved: 2026-10-05
Environment: Kali Linux

## In-scope assets
- A1 `imagesharer.xyz` (web app, nginx + PHP 8.2.34 + PostgreSQL)
- A2 `www.imagesharer.xyz` (alias)
- A3 `resources.imagesharer.xyz` (CloudFront)
- A4 `51.161.131.44` ports 80/443/5432
- A5 `d273uevi0662l0.cloudfront.net` (CloudFront distribution config)

## Priority queue

### P0 — Verify high-signal early findings
1. **Hard-coded AWS key in /js/awsvalid.js** — download, extract AKIA/secret; verify ownership via `sts:GetCallerIdentity` (read-only); enumerate attached policies (read-only) if the key is Imagur's. Hypothesis: credentials are live and privileged.
2. **PostgreSQL on 51.161.131.44:5432** — banner grab + version detect (nmap -sV -Pn -p 5432). Attempt no-auth / default-cred *only via a single probe* using `psql` with empty password (one probe, non-brute).
3. **resources.imagesharer.xyz CloudFront alias/cert mismatch** — verify current state; check for subdomain-takeover indicators (missing distribution alias? pointing to deleted bucket?).

### P1 — Web application: unauthenticated attack surface
4. Full content/path discovery on `https://imagesharer.xyz/`: ffuf wordlist of common paths, examine robots.txt, sitemap, .well-known.
5. Enumerate HTTP methods, security headers (missing HSTS/CSP), cookie flags on login/dashboard.
6. Pre-auth endpoint tests:
   - `/login` POST — SQLi (error+boolean+time-based), authentication bypass, user enumeration via timing/response-diff.
   - `/register` POST — mass-assignment, weak password policy, duplicate-handling, SQLi, HTML/JS injection in profile fields, email verification bypass.
   - `/dashboard` (unauth) — forced browsing / auth-gate check.
7. Verbose error / debug exposure (crash-page info disclosure).

### P2 — Web application: authenticated attack surface
8. Register a test account (and a second account for IDOR/multi-tenant tests). Record creds in evidence (not findings).
9. Walk the authenticated app, map all endpoints (profile, image upload, image view, image delete, listing, sharing, comments/likes if any, search, etc.).
10. For each discovered endpoint, test:
    - **SQLi** on every parameter (POST body, GET query, path segments, cookies, headers like X-Forwarded-For).
    - **XSS** (reflected, stored, DOM-based) — image titles, descriptions, filenames, profile fields.
    - **IDOR / BOLA** — accessing user B's images/data from user A by changing IDs.
    - **SSRF** — if the app fetches remote images by URL ("import from URL"), test with `http://169.254.169.254/`, `http://127.0.0.1/`, `file://`, DNS rebinding, redirect-based SSRF, blind SSRF (OOB via Burp Collaborator / self-hosted listener).
    - **File upload abuse** — magic-byte spoofing, double extension, SVG with JS, polyglot files, path traversal in filenames, oversized files (ReDoS-adjacent), MIME confusion, image-tragick / imagemagick CVE patterns if ImageMagick is used.
    - **Path traversal / LFI / RFI** — any file= or path= parameter.
    - **Authorization flaws** — admin-only endpoints accessible as user, mass-assignment of role.
    - **Session security** — fixation, cookie flags (Secure, HttpOnly, SameSite), logout invalidation, concurrent sessions, password reset token entropy & reuse.
    - **CSRF** — on state-changing endpoints (register, upload, delete, change-password).
    - **Open redirect** — `?url=`, `?next=`, `?redirect=`.
    - **Rate limiting** on sensitive endpoints (single-request probe, no spraying).
    - **Clickjacking** — X-Frame-Options already DENY on root; verify per-page.
    - **Business logic** — ownership transfer, hidden/shared image access, deleted-image recovery, quota bypass.
11. API discovery — look for `/api/`, GraphQL, JSON endpoints; test same vuln classes.

### P3 — Infrastructure / network
12. Nmap fast port enumeration on 51.161.131.44 (top 1000 TCP; then version/CVE scan on open ports).
13. TLS configuration test (testssl.sh) on all three HTTPS hostnames.
14. CloudFront misconfig deep-dive on resources.imagesharer.xyz — origin discovery, cache poisoning, host-header injection.

### P4 — Email / DNS hygiene
15. Confirm absence of SPF/DMARC/MX/DNSSEC CAA — document impact (spoofing).

### P5 — Nice-to-have / information
16. JavaScript inspection for secrets, API keys, hidden endpoints, source-map exposure.
17. Wayback / archive inspection for leaked historical content.

## Rules of engagement reminders
- Every command is executed by a one-shot `execution` sub-agent — never by me.
- Each finding goes to `findings.txt` ONLY after reproducibility is established.
- No destructive queries on PostgreSQL. No bulk/brute credential testing. No mass scanning across the OVH range.
- Pause and ask the owner if a scope-adjacent discovery appears.
