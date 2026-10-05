# Assessment Plan — Imagur (imagesharer.xyz)

**Engagement window:** 2026-10-05 onward
**Target host:** 51.161.131.44 (OVH Sydney VPS)
**Approved scope:** apex + www + resources subdomain + 6 open ports on the VPS
**Approved methods:** passive OSINT, light active probing, standard web testing, light fuzzing, authenticated testing with self-created accounts, non-destructive protocol probes. **No** brute force / DoS / destructive writes.

Legend: [S]tatus = pending / in-progress / done / dropped. Each task has a hypothesis, the evidence needed to confirm, and completion criteria.

---

## Phase A — Infrastructure & non-web services

### A1. TLS configuration review (443, 8080-if-TLS)  [S:pending]
- Hypothesis: Weak TLS versions/ciphers, missing HSTS enforced in TLS layer, cert chain issues (www SAN already known missing).
- Evidence: sslscan/testssl output, cert chain, protocol/cipher matrix.
- Done when: full TLS matrix captured, any weak protocol/cipher documented.

### A2. SSH (22) hardening review  [S:pending]
- Hypothesis: Outdated algorithms, root login enabled, password auth enabled.
- Evidence: `nmap -sV --script ssh2-enum-algos,ssh-auth-methods` output and version.
- Done when: supported auth methods and algorithm list captured. No credentials attempted.

### A3. Public DNS resolver on 53/tcp  [S:pending]
- Hypothesis: Open recursive resolver (amplification risk) or zone-serving for internal names.
- Evidence: `dig @51.161.131.44 version.bind chaos txt`, test recursion with a controlled external name (`dig @IP example.com +norec` and `+rec`), check for AXFR denial.
- Done when: recursion state and version string recorded.

### A4. PostgreSQL (5432) public exposure  [S:pending]  **HIGH PRIORITY**
- Hypothesis: Public PostgreSQL instance is exploitable (no TLS required, auth-method weak, or empty creds).
- Evidence: `nmap --script pgsql-brute-ssl=NO` **omit brute** — only banner/version via `pg_isready`/`nmap -sV` and a single unauthenticated connection with a non-sensitive username to observe the auth challenge type. **No brute force.**
- Done when: PG version, auth method, and TLS-required flag captured. Finding written regardless (public DB exposure is itself a finding).

### A5. Secondary HTTP stack :8080 reconnaissance  [S:pending]
- Hypothesis: Dev/admin surface, phpinfo, server-status, or default Apache pages.
- Evidence: HEAD/GET on `/`, `/server-status`, `/server-info`, `/phpinfo.php`, `/index.php`, `/info.php`, common PHP dev endpoints; light wordlist (common.txt, ~ few hundred entries).
- Done when: all content classified; distinct hosts via `Host:` header tested (apex, www, localhost).

---

## Phase B — Web application: imagesharer.xyz

### B1. Application surface mapping  [S:pending]
- Hypothesis: Routes beyond login/register/dashboard exist (upload, image view, profile, admin, API).
- Evidence: light directory fuzzing with ffuf and a common wordlist (SecLists common.txt + api endpoints), status-code filtered.
- Done when: full route inventory saved.

### B2. Authentication: registration + login flow analysis  [S:pending]
- Create 2 test accounts. Observe:
    - Password policy, lockout, rate limit (observe only — no brute force)
    - Session cookie behavior (PHPSESSID flags, rotation on login)
    - Account enumeration via login/register/forgot-password responses & timing
    - CSRF tokens on auth forms
- Done when: all auth flows mapped; enumeration & CSRF status documented.

### B3. Authorization / IDOR / BOLA  [S:pending]
- Hypothesis: Access to other users' resources (images, profile, dashboard data) via ID manipulation.
- Evidence: capture every URL/endpoint referencing an identifier; attempt cross-account access with user A's session on user B's object; test both numeric IDs and UUIDs; test API verbs.
- Done when: every id-bearing endpoint tested with the other account.

### B4. File upload testing (image sharing core feature)  [S:pending]  **HIGH PRIORITY**
- Hypotheses: path traversal in filename, SVG with embedded JS (stored XSS), content-type bypass to upload .php, size/type validation gaps, server-side image parsing (ImageMagick/ghostscript/ImageTragick/CVE-2016-3714 class), SSRF via image URL fetch feature, EXIF-based stored XSS.
- Evidence: upload matrix — ok image / renamed-extension / double-ext / null-byte / huge filename / SVG with script / HTML disguised as JPEG / polyglot / php payload / symlink / zip-slip; also test "upload by URL" (if present) with internal IPs / 169.254.169.254.
- Done when: all vectors attempted with minimum proof.

### B5. Injection suite across all endpoints  [S:pending]
- SQLi (error, boolean, time, 2nd-order) on login/register/search/any parameter
- Command injection (image conversion params if any)
- SSTI (any templated field)
- XSS (reflected, stored, DOM) across every input and the `page_views` cookie sink
- Open redirect on login `?redirect=` and similar
- CRLF/HTTP header injection
- XXE / XML-based features if any

### B6. Session & cookie review  [S:pending]
- Verify PHPSESSID lifecycle, HttpOnly/Secure/SameSite flags, session fixation
- Validate the `page_views` cookie: does the server read it unsafely? decode->render? reflect? Could it enable server-side XSS/SQLi via that sink.
- Done when: cookie tampering matrix and server reaction documented.

### B7. CSRF across state-changing requests  [S:pending]
- Done when: tested on password-change, upload, delete, profile-update, share actions.

### B8. Security headers / cookies / clickjacking  [S:pending]
- Already know HSTS, CSP, Permissions-Policy missing — formalize as a finding; evaluate real exposure (mixed content, framing of sensitive flows).

### B9. Secrets / information disclosure  [S:pending]
- `/.env`, `/.git/HEAD`, `/vendor/`, `/composer.json`, backup files `~`, `.bak`, `.old`, phpinfo paths, swagger/openapi, debug toolbars, verbose stack traces.

### B10. Mail/email spoofing finding  [S:pending]
- Already observed: no MX / SPF / DMARC / DKIM. Document as a finding; no live spoofing performed.

### B11. ReDoS single-shot checks (per scope allowance)  [S:pending]
- Single large pathological payload per text field; observe response time; **immediately stop** if any slow-down is observed; one-shot only.

---

## Phase C — resources.imagesharer.xyz (CloudFront in front, owner-controlled DNS)

### C1. CloudFront misconfig / origin disclosure (passive + light active)  [S:pending]
- Hypothesis: Origin bucket is public-listable (`?list-type=2`), bucket name leaks, SSRF-friendly, or allows direct origin access.
- Evidence: various `Host:` header tests, `?list-type=2`, common bucket name guesses from the "imagesharer" root (passive — no brute wordlists).
- Done when: public listability yes/no proven.

---

## Phase D — Validation & reporting
- Reconfirm each candidate finding with a second narrow test.
- Write confirmed findings to `findings.txt` in the required format.
- Spawn `report` sub-agent.

---

## Coverage checklist
- [ ] All 4 confirmed assets touched
- [ ] All 6 open ports probed
- [ ] All HTML forms tested
- [ ] All id-bearing endpoints tested cross-account
- [ ] Upload surface stressed
- [ ] Secrets/dev-files checked
