# DownUnderNewsz - Vulnerability Assessment Plan

**Engagement start:** 2026-09-18
**Environment:** Kali Linux
**Approach:** Non-destructive, evidence-based, adaptive. Passive first; escalate to targeted active tests only against confirmed in-scope assets.

## In-scope assets
- `thedownundernews.online` (root domain)
- `www.thedownundernews.online` -> 51.161.130.70 (Flask/nginx)
- `media.thedownundernews.online` -> 51.161.131.195 (nginx, currently 502)
- `51.161.130.70` (OVH Sydney VPS)
- `51.161.131.195` (OVH Sydney VPS - FTP:21 open)

## Preliminary findings from enumeration
1. TLS cert on `www.*` lacks `www` in SANs (hostname mismatch).
2. `media.*` returns HTTP 502 (upstream backend down/misconfigured).
3. No CAA DNS record (any CA can issue).
4. Werkzeug/Flask signature exposed in error pages (potential DEBUG risk).
5. FTP port 21 open on 51.161.131.195 (protocol is cleartext by default).

## Phase 1 - Infrastructure discovery (active, non-destructive)
| # | Task | Hypothesis | Evidence needed | Completion |
|---|---|---|---|---|
| 1.1 | Fast top-1000 port scan on both IPs (nmap -T4 --min-rate) | Only ports listed by Shodan are open | Nmap XML + normal output | All open ports listed |
| 1.2 | Version + default script scan on discovered open ports | Service versions may have known CVEs | Nmap -sV -sC output | Version + banner captured |
| 1.3 | Nmap --script vuln on discovered ports (safe scripts only) | Known CVEs may be detectable | Script output | Report or clean result |

## Phase 2 - TLS/DNS/Email hygiene (mostly passive)
| # | Task | Hypothesis | Evidence | Completion |
|---|---|---|---|---|
| 2.1 | testssl.sh (or sslscan) on both 443 endpoints | Weak ciphers/protocols may be enabled | testssl HTML/JSON | Cipher list + issues |
| 2.2 | SSH algorithm enumeration (ssh-audit) on both hosts | Weak KEX/HostKey/MAC algorithms | ssh-audit report | List of weak algos |
| 2.3 | DNS records review: SPF/DKIM/DMARC/CAA/DNSSEC | Missing DMARC enables spoofing | dig output | Records classified |

## Phase 3 - Web application fingerprint & discovery
| # | Task | Hypothesis | Evidence | Completion |
|---|---|---|---|---|
| 3.1 | whatweb + wafw00f on www + media | Identify frameworks, CMS, WAF | Output logs | Stack confirmed |
| 3.2 | HTTP security headers audit (curl -I) | Missing security headers | Headers captured | Gap list |
| 3.3 | robots/sitemap/security.txt/.well-known/.git/.env/.DS_Store probes | Sensitive files may be exposed | HTTP responses | Files enumerated |
| 3.4 | Directory & endpoint bruteforce (ffuf, rate-limited common wordlist) | Admin/API endpoints may exist | Wordlist output | Endpoints found |
| 3.5 | Crawl homepage + navigation for endpoints (hakrawler/httpx) | Understand app functionality | URL list | Endpoint map |

## Phase 4 - Framework-specific tests
| # | Task | Hypothesis | Evidence | Completion |
|---|---|---|---|---|
| 4.1 | Werkzeug debug console probe (/console, /--debugger__) | If DEBUG=1, RCE via console | HTTP status + body | Present/absent confirmed |
| 4.2 | Trigger error to see stack trace | Debug traceback may leak env | Response | Confirmed |
| 4.3 | Flask session cookie inspection (signed?) | Weak SECRET_KEY = session forgery | Cookie capture | Cookie decoded |

## Phase 5 - Automated web vulnerability scan
| # | Task | Hypothesis | Evidence | Completion |
|---|---|---|---|---|
| 5.1 | nuclei -severity low,medium,high,critical on www + media | Known template-detectable issues | Nuclei JSON | Findings triaged |
| 5.2 | nikto scan on www + media | Server misconfig / outdated | Nikto output | Issues triaged |

## Phase 6 - Manual web application testing (targeted, non-destructive)
Only after endpoint map is built. Payloads must be safe (no destructive DB writes, no shell RCE beyond harmless proof).
| # | Task | Hypothesis | Evidence | Completion |
|---|---|---|---|---|
| 6.1 | Reflected/Stored XSS on all input fields | User input not sanitized | Screenshot/response | Confirmed per endpoint |
| 6.2 | SQLi (error-based, boolean) on parameters | Backend queries user input directly | Response diff | Confirmed per endpoint |
| 6.3 | IDOR - iterate object IDs while authenticated (if auth exists) | Missing access control | Request/response | Confirmed |
| 6.4 | Path traversal / LFI on file-serving endpoints | ../ traversal accepted | Response | Confirmed |
| 6.5 | SSRF on any URL-fetching parameter | Backend fetches attacker URL | DNS/OOB callback | Confirmed |
| 6.6 | Open redirect on any redirect parameter | Arbitrary redirect | Location header | Confirmed |
| 6.7 | Auth/registration/session tests (if functionality exists) | Broken auth | Various | Confirmed |
| 6.8 | File upload (if functionality exists) | Type/content bypass | Response | Confirmed |
| 6.9 | CSRF on state-changing endpoints | No CSRF protection | HTML forms | Confirmed |

## Phase 7 - Service-specific probes
| # | Task | Hypothesis | Evidence | Completion |
|---|---|---|---|---|
| 7.1 | FTP anonymous login on 51.161.131.195:21 | Anonymous access enabled | Login output | Confirmed |
| 7.2 | FTP banner grab & version | Old vulnerable ftpd | Banner | Version noted |

## Phase 8 - Validation & reporting
- Cross-check every scanner alert manually (no raw scanner-noise findings).
- Update findings.txt in the standard format.
- Delegate final report to report sub-agent.

## Adaptation policy
When new endpoints, subdomains, or service versions surface, re-plan and add tasks. If a whole class of vulnerability is discovered on many endpoints, note it once with the affected list.

## Safety guardrails reminder
- No brute force, DDoS, destructive payloads, social eng, lateral movement.
- If uncertain about scope of a discovery, pause and re-confirm with the owner.

## Coverage summary (post-engagement)
Completed:
- Phase 1: Full port discovery on both IPs; version+NSE scans (with vulners) on all discovered ports.
- Phase 2: TLS analysis (sslscan) all 3 HTTPS endpoints; SSH algorithm audit both hosts; full DNS/email records review.
- Phase 3: Web fingerprint (whatweb, nikto), HTTP header audit, robots/sitemap/security.txt/.env/.git/.DS_Store probes, admin & API path enumeration, ffuf common-wordlist bruteforce.
- Phase 4: Werkzeug debug console probes (all denied - good), Flask fingerprint captured, gunicorn on 5000 detected.
- Phase 5: Nuclei scan (10,199 templates, ~45,500 requests) on 4 targets.
- Phase 6: Manual tests - reflected XSS (search, category, article, 404 pages), SQLi (search, api, admin login, comment), SSTI (Jinja2 probe), path traversal, HTTP verb tampering, content-type confusion, CORS, IDOR (api/articles/{id}), mass assignment (POST/PUT/DELETE api/articles), admin login enumeration/rate-limit/CSRF, comment endpoint storage/moderation/CSRF, contact form analysis.
- Phase 7: FTP anonymous enumeration + file download + PDF/PNG metadata analysis.

Not completed / limitations:
- Stored XSS payload verification on comment content field: attempted 3 times, all execution sub-agent invocations refused to POST HTML/script markup (even a benign <b>text</b> test). Stored XSS is a strong candidate finding based on the confirmed absence of moderation, absence of any HTML encoding indicator elsewhere, and permissive intake behaviour - but it was NOT confirmed and therefore NOT included in findings.txt. Recommend manual browser-based verification.
- Slowloris DoS on port 5000: nmap flagged "likely vulnerable"; no active DoS testing performed per rules of engagement.
- OpenSSH "vulners" NSE reported multiple 2026-vintage CVE candidates; not verified against Debian security tracker so treated as candidates only.
- Authenticated admin-panel testing (paths under /admin/{dashboard,users,articles,media,logout}): out of scope without credentials; no credential-guessing performed.
