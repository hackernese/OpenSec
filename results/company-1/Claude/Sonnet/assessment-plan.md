# Assessment Plan - DownUnderNewsz

Engagement dir: ~/Projects/DownUnderNewsz
State: ASSESSING

## In-scope assets
- thedownundernews.online (root domain)
- www.thedownundernews.online
- media.thedownundernews.online (currently 502 - verify status before intrusive testing)
- 51.161.130.70 (main server)
- 51.161.131.195 (media server)

## Phase 1 - Network & Service Recon
| Task ID | Hypothesis | Target | Method | Evidence | Completion Criteria |
|---|---|---|---|---|---|
| net-001 | Unnecessary/risky ports may be exposed on main server | 51.161.130.70 | Fast top-1000 port scan (nmap -T4 --top-ports 1000) | Open port list | Port list captured |
| net-002 | Unnecessary/risky ports may be exposed on media server | 51.161.131.195 | Fast top-1000 port scan | Open port list | Port list captured |
| net-003 | Open services may run vulnerable versions | Both IPs (open ports from net-001/002) | nmap -sV -sC --script vuln on discovered open ports | Service versions, vuln script output | Findings triaged |

## Phase 2 - Web Application Recon
| Task ID | Hypothesis | Target | Method | Evidence | Completion Criteria |
|---|---|---|---|---|---|
| web-001 | Fingerprint tech stack (CMS/framework/server) | www.thedownundernews.online | whatweb | Tech stack list | Stack identified |
| web-002 | Missing/weak security headers (CSP, HSTS, X-Frame-Options, etc.) | main site | curl -I headers check | Header dump | Headers evaluated |
| web-003 | Weak TLS/SSL configuration, cert issues | thedownundernews.online + www | nmap ssl-enum-ciphers / testssl | Cipher list, cert details | Config graded |
| web-004 | Sensitive files/dirs exposed (.git, .env, backups, admin panels) | main site | Targeted content discovery (curated small wordlist, ffuf/gobuster) | Discovered paths | Exposure confirmed/ruled out |
| web-005 | robots.txt/sitemap reveal hidden paths | main site | curl robots.txt & sitemap.xml | File contents | Reviewed |
| web-006 | media subdomain currently unavailable - confirm status, avoid hammering a broken service | media.thedownundernews.online | curl status check only | HTTP status | Status confirmed, decide go/no-go for further testing |

## Phase 3 - Application-Layer Vulnerability Testing (scope depends on Phase 2 findings)
| Task ID | Hypothesis | Target | Method | Evidence | Completion Criteria |
|---|---|---|---|---|---|
| app-001 | Input fields (search/contact/comments) vulnerable to XSS/SQLi | Discovered forms/endpoints | Manual + targeted payloads (non-destructive) | Request/response pairs | Confirmed or ruled out |
| app-002 | CORS misconfiguration allows cross-origin data theft | API/dynamic endpoints if found | curl Origin header tests | Response ACAO headers | Confirmed or ruled out |
| app-003 | Clickjacking possible (missing X-Frame-Options/CSP frame-ancestors) | main site | Header review (from web-002) | N/A | Confirmed or ruled out |

## Phase 4 - DNS/Email Hygiene (domain-owned records only)
| Task ID | Hypothesis | Target | Method | Evidence | Completion Criteria |
|---|---|---|---|---|---|
| dns-001 | Missing DMARC weakens anti-spoofing posture | thedownundernews.online DNS zone | dig TXT _dmarc | TXT record (or absence) | Confirmed (already flagged in enum, verify directly) |

## Constraints
- No brute force, DDoS, credential stuffing, MFA bypass, social engineering.
- No testing of third-party infra (registrar DNS, mail relay, CDNs).
- media.thedownundernews.online: check status only first; do not intrusively test a possibly-broken service without re-confirming it's actually up.
- Every command run by a fresh, single-purpose execution sub-agent.

## Status Log
- Phase 1: complete (net-001, net-002, net-003)
- Phase 2: complete (web-001 through web-006)
- Phase 3: complete (app-001, app-002, app-003)
- Phase 4: complete (dns-001)
- FTP write-access validation: attempted with explicit owner approval, declined twice by execution agent's own safety controls (treats remote write/delete as destructive-adjacent regardless of scope). Not forced through. Recorded as untested limitation in findings.

## Limitations / Untested Areas
- Anonymous FTP write/delete capability on media server: could not be safely validated; only read access confirmed.
- media.thedownundernews.online backend currently returns 502 (appears down/misconfigured); could not perform deeper web app testing on this subdomain beyond confirming reachability of nginx layer.
- amass (additional passive subdomain enumeration tool) was unavailable in the enumeration sandbox; coverage was cross-validated via subfinder, assetfinder, crt.sh, and Shodan instead.
- No credential/brute-force testing performed against /admin login, per engagement rules.
- General web search for additional business aliases was blocked by a search engine interstitial during enumeration.

## State: VALIDATING -> complete, moving to REPORTING
