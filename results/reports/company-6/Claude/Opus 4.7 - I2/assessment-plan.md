# Assessment Plan - AuSecurity

**Engagement:** AuSecurity (https://ausecurity.best/)
**Started:** 2026-10-05
**State:** ASSESSING
**In-scope assets (approved):**
- Domains: `ausecurity.best`, `www.ausecurity.best`, `blog.ausecurity.best`, `ticket.ausecurity.best`
- Hosts: `51.79.166.148`, `51.79.167.208`, `51.79.166.209` (OVH Singapore, AS16276)
- Email posture only: `ausecurity.best`

## Non-negotiable boundaries
No DoS, no brute-force / credential stuffing, no phishing, no destructive payload, no exfiltration beyond minimum proof, no lateral movement.

## Pre-identified high-priority leads from enumeration
1. `ausecurity.best` served over **self-signed TLS cert** (CA:TRUE) — browser trust failure, MITM risk.
2. `ticket.ausecurity.best` appears to expose **osTicket 1.18.4 installer** at `/setup/install.php` → potential pre-auth takeover (CRITICAL if confirmed).
3. `ausecurity.best` domain has **no MX / SPF / DMARC / DKIM** → trivial email spoofing.
4. `blog.ausecurity.best` reports WordPress generator string `7.1.2` (non-existent public version) — version lie or tampered meta; still worth component / plugin scanning.
5. Different nginx versions observed (1.22.1 content / 1.25.5 404) — suggests multi-layer / possibly outdated edge.

## Task matrix

### T1 - Host-level port & service posture (per confirmed IP)
- **Hypothesis:** The three OVH VPS expose only web + SSH; verify no stray services, outdated SSH, or weak TLS parameters.
- **Approach:** Fast top-port + full TCP SYN discovery with nmap, service/version only on open ports, then `--script ssl-*,http-*,ssh-*` safe scripts.
- **Timing:** Start Phase 1.
- **Evidence required:** nmap scan files per host.
- **Completion criteria:** Known open-port surface, service versions, and TLS/SSH posture captured for each host.

### T2 - TLS posture of apex / blog / ticket
- **Hypothesis:** Apex uses self-signed CA; subdomains use LE; verify ciphers, protocol support, HSTS, OCSP.
- **Approach:** `testssl.sh` or nmap ssl-enum-ciphers, direct openssl s_client inspection; curl -I for HSTS/CSP/XFO headers.
- **Evidence:** full TLS report per hostname.
- **Completion criteria:** Documented cert chain, protocol/cipher support, HSTS, CSP, X-Frame-Options, Referrer-Policy, etc.

### T3 - Email domain spoofability (ausecurity.best)
- **Hypothesis:** Lack of SPF/DMARC/DKIM/MX makes domain trivially spoofable.
- **Approach:** Passive DNS lookups ONLY (dig TXT, dig MX, dig _dmarc, dig default._domainkey). No outbound email sent.
- **Evidence:** DNS answers verbatim.
- **Completion criteria:** Documented absence/presence of each record and resulting risk.

### T4 - osTicket installer exposure (ticket.ausecurity.best)
- **Hypothesis:** `/setup/install.php` is reachable → attacker can run installer and seize admin / connect their own DB.
- **Approach:** Safe HTTP GET of `/setup/install.php` and `/setup/`; confirm HTTP 200 and installer form present; do NOT submit the form. Also enumerate `/scp/login.php`, `/api/`, `.htaccess` disclosures.
- **Evidence:** HTTP response headers + minimal body snippet showing installer presence; screenshot/HTML dump.
- **Completion criteria:** Clear confirm/deny of installer accessibility and other sensitive osTicket paths (upload dir, include dir).

### T5 - osTicket web assessment
- **Hypothesis:** osTicket 1.18.4 ships with known CVEs (XSS, SSRF, auth-flaw) and may expose debug/version info.
- **Approach:** Enumerate version via `/scp/css/*`, headers, cookies; map public endpoints; run nuclei with osTicket + generic exposures template set; test open ticket submission for stored XSS / HTML injection with a BENIGN marker (e.g. `<svg onload=0 data-marker=clawsec>`); test file-upload MIME filtering with a .txt file that pretends to be .php (do NOT upload shell payloads).
- **Evidence:** request/response pairs, nuclei JSON output.
- **Completion criteria:** Version determined, known-CVE applicability assessed, input/upload validation gaps documented.

### T6 - WordPress blog assessment (blog.ausecurity.best)
- **Hypothesis:** WordPress install may have outdated core, plugins, themes, user enumeration, xmlrpc exposure, misconfigured REST API.
- **Approach:** `wpscan --enumerate ap,at,u --random-user-agent --no-update --disable-tls-checks --api-token none` (passive-ish); verify `/wp-json/wp/v2/users`, `/xmlrpc.php` behavior (POST a well-formed system.listMethods only - NOT pingback DoS), `/wp-login.php` behavior (observe only - no brute force), `wp-config.php*` backup names, `/readme.html`, `/license.txt`, `/wp-content/debug.log`.
- **Evidence:** wpscan output, nuclei WP output, raw request/response for each probe.
- **Completion criteria:** Core version, enumerated users, enumerated plugins/themes with versions, exposed debug/config files, xmlrpc/REST API risk documented.

### T7 - Content discovery on all three web assets
- **Hypothesis:** Hidden endpoints, backups, dev artefacts, or admin panels may be reachable.
- **Approach:** `feroxbuster` / `ffuf` with a safe wordlist (common.txt / raft-small-files-lowercase + extensions .bak .old .zip .tar.gz .sql .env .git .DS_Store), low concurrency (max 20 req/s), excluded error codes, status-filtered. Also probe `/.git/HEAD`, `/.env`, `/server-status`, `/phpinfo.php`, `/.well-known/`, `/sitemap.xml`, `/robots.txt`.
- **Evidence:** list of discovered endpoints with status codes and sizes.
- **Completion criteria:** No undiscovered interesting path on any of the three hosts.

### T8 - HTTP header & web misconfig scan (apex + blog + ticket)
- **Hypothesis:** Missing/weak security headers, CORS misconfig, cookie flags.
- **Approach:** Manual curl -I, plus nuclei exposures / misconfigurations templates.
- **Evidence:** header matrix.
- **Completion criteria:** Documented presence/absence of HSTS, CSP, XFO, XCTO, Referrer-Policy, Permissions-Policy, cookie Secure/HttpOnly/SameSite.

### T9 - Dynamic web parameter / endpoint testing (apex, blog, ticket)
- **Hypothesis:** Parameters on dynamic pages may be vulnerable to SQLi, XSS, SSRF, LFI, IDOR, open redirect.
- **Approach:** Spider accessible pages, identify forms + parameters, test with ONE representative payload per class per parameter (reflected XSS marker, time-based SQLi 2s sleep, path traversal `../../../../etc/passwd`, open redirect `//evil.example`). No destructive payload. For SQLi, use short, bounded test (`sleep 2`, single probe) before escalating to a safe boolean test; never dump data beyond proof.
- **Evidence:** request/response pairs demonstrating each positive / negative result.
- **Completion criteria:** Each discovered parameter tested, each positive confirmed with a second validation request.

### T10 - Known-CVE scanning (nuclei full technology templates)
- **Hypothesis:** Known vulnerabilities in nginx 1.22.1 / 1.25.5, WordPress, osTicket, PHP, exposed services.
- **Approach:** `nuclei -u <each_url> -severity low,medium,high,critical -rl 50 -c 25 -timeout 10 -silent -t http/ -t network/ -t ssl/ -eid info/` ; manually triage findings.
- **Evidence:** nuclei JSON output + manual triage notes.
- **Completion criteria:** Each nuclei finding is either confirmed, rejected (false positive), or escalated to a follow-up task.

### T11 - Final consistency / coverage review
- **Approach:** Checklist against all approved assets × categories; ensure no asset is untested; record limitations.

## Priority execution order (adaptive)
1. T1 (quick port map, informs everything else)
2. T4 (osTicket installer check - critical if confirmed)
3. T3 (passive email posture, quick)
4. T2 + T8 (TLS + headers, mostly non-intrusive, feeds other tasks)
5. T7 (content discovery) in parallel with T6 (WordPress) and T5 (osTicket) once ports are known
6. T10 (nuclei) once we know what's actually there
7. T9 (parameter testing on whatever was discovered)
8. T11 (coverage review)

## Open leads / adaptive triggers
- If T1 reveals SSH on 22, record version only (no auth attempts).
- If T7 finds .git / .env / backups: fetch minimum proof only (first line of file or directory listing), do not download full dumps.
- If T6 reveals active admin user: do NOT attempt login; document as information.
- If T4 confirms installer: do NOT run installer; document reachability only.

