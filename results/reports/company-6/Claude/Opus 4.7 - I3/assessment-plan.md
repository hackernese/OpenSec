# Assessment Plan - AuSecurity

Start: 2026-10-05
Scope: ausecurity.best, www/blog/ticket subdomains, 3 OVH-SG VPS IPs (51.79.166.148, 51.79.166.209, 51.79.167.208), info@ausecurity.best email/DNS posture.

Methodology: PTES / OWASP WSTG / NIST SP 800-115 - adapted. Non-destructive. No credential bruteforce, DoS, phishing, or data exfiltration.

## Phase P1 - Infrastructure (parallel across 3 IPs)

| ID | Hypothesis | Task | Evidence required | Completion criteria |
|----|-----------|------|-------------------|---------------------|
| P1.1 | Hosts expose services beyond :80/:443 | Fast TCP top-ports scan via nmap `-sS -Pn -T4 --top-ports 1000 --open` on each IP | nmap output | Open-port list per IP |
| P1.2 | Open ports run outdated/vulnerable versions | nmap `-sV -sC --script vuln` targeted at open ports | nmap XML + console | Service versions + script hits |
| P1.3 | TLS misconfigs / weak ciphers on 443 | testssl.sh on each HTTPS endpoint | testssl.sh HTML/log | Grade + list of issues |

## Phase P2 - Apex & www (static marketing site)

| ID | Hypothesis | Task | Completion |
|----|-----------|------|-----------|
| P2.1 | Self-signed cert in production (already flagged) | openssl / testssl confirm | Confirmed |
| P2.2 | Missing security headers (HSTS/CSP/X-Frame/etc.) | curl -I + manual review | Header matrix |
| P2.3 | nginx/1.25.5 fallback banner = reverse proxy misconfig | Probe /robots.txt /sitemap.xml / unknown paths | Behavior documented |
| P2.4 | Hidden paths / backups / .git / .env | ffuf with common wordlist (seclists common.txt), rate-limited | Status matrix |
| P2.5 | Contact form (if present) for XSS/SSTI/injection | Manual + burp-style probes | Documented |

## Phase P3 - Email/DNS posture (ausecurity.best)

| ID | Hypothesis | Task | Completion |
|----|-----------|------|-----------|
| P3.1 | No SPF/DMARC/DKIM/MX/MTA-STS/CAA (already observed) | dig TXT/MX/CAA + mxtoolbox-style verify | Confirmed with specific records |
| P3.2 | Domain spoofable from internet | Verify absence; conclude spoof risk | Documented |

## Phase P4 - blog.ausecurity.best (WordPress 7.1.2 / Apache 2.4.68)

| ID | Hypothesis | Task | Completion |
|----|-----------|------|-----------|
| P4.1 | WordPress core version 7.1.2 has known CVEs (future major; needs CVE research) | WPScan passive (no API key needed for banner/vuln listing) + manual version mapping | List CVEs applicable |
| P4.2 | Plugins/themes with known vulns | WPScan plugin/theme enumeration (passive) | List with CVEs |
| P4.3 | User enumeration (?author=N, /wp-json/wp/v2/users) | curl probes | Confirmed admin usernames |
| P4.4 | xmlrpc.php exposure | curl -I xmlrpc.php + system.listMethods probe | Status |
| P4.5 | wp-config.* / backup files exposure | ffuf wp-specific list | Status |
| P4.6 | Apache 2.4.68 CVEs | CVE lookup | List |
| P4.7 | REST API data exposure (/wp-json) | Enumerate endpoints | Documented |

## Phase P5 - ticket.ausecurity.best (osTicket 1.18.4)

| ID | Hypothesis | Task | Completion |
|----|-----------|------|-----------|
| P5.1 | **Installer still exposed** at /setup/install.php (CRITICAL candidate - takeover possibility) | GET /setup/install.php and sibling paths; document ability to invoke installer without auth | Confirmed |
| P5.2 | osTicket 1.18.4 known CVEs | CVE research (NVD, GitHub advisories) | List |
| P5.3 | Default/exposed admin paths /scp/login.php | curl probes | Status (no credential attack) |
| P5.4 | PHP 8.2.33 info disclosure, X-Powered-By | header check | Documented |
| P5.5 | File-upload / ticket-create endpoints for XSS/SSRF (if reachable without auth) | Non-destructive probe | Documented |
| P5.6 | config.php / backup / .git exposure | ffuf | Status |

## Phase P6 - Cross-cutting web testing

| ID | Hypothesis | Task | Completion |
|----|-----------|------|-----------|
| P6.1 | Open redirect, reflected XSS, SQLi, SSRF on any identified parameterized endpoint | Manual + nuclei (with -t cves,vulnerabilities,exposures,misconfiguration,default-logins templates) across all 3 hosts | Nuclei JSON + manual confirm |
| P6.2 | HTTP method tampering (TRACE/PUT), CORS misconfig | curl -X | Documented |
| P6.3 | Information disclosure (stack traces, PHP info, server-status) | ffuf common paths | Documented |

## Priorities
1. P5.1 (osTicket installer) - potentially critical, verify first.
2. P1.1/P1.2 - port exposure baseline.
3. P4.1-P4.5 - WordPress is historically high-risk.
4. P3 - email spoofing posture (business impact: BEC).
5. Remainder.

## Safety rails
- No credential bruteforce / spraying.
- No destructive payloads: all SQLi probes = boolean/time-based proof-of-concept only, no DROP/UPDATE/DELETE.
- No automated DoS via nuclei rate (use default rate + -rl 50).
- Stop at minimum proof of each finding.
- Never follow or test the osTicket installer to completion (would alter the system state - owner impact).
