# AuSecurity - Vulnerability Assessment Plan

Engagement dir: `~/Projects/AuSecurity`
Approved in-scope assets: see `assets.json`.

## Priorities (rationale)

1. **ticket.ausecurity.best** - unauthenticated osTicket installer wizard is publicly reachable. Highest risk of full-application takeover if a re-install can be triggered. **HIGH**
2. **blog.ausecurity.best** - WordPress with user enumeration confirmed; plus cleartext HTTP served alongside HTTPS. **HIGH**
3. **ausecurity.best (apex + www + contact)** - Self-signed TLS despite valid LE cert; :8080 origin exposed cleartext; static marketing. **MEDIUM**
4. **Direct :8080 origin backends** - both `51.79.166.148:8080` and `51.79.166.209:8080` bypass the reverse proxy and reveal backend headers. **MEDIUM**
5. **DNS / email hygiene of `ausecurity.best`** - missing MX/SPF/DMARC/DKIM/MTA-STS -> spoofing risk. **MEDIUM**
6. **Network exposure** - SSH (22) on all three VPS. Check version and auth exposure only via banner. No brute force. **LOW/INFO**

## Planned tasks

### T-01  Baseline nuclei sweep across all approved web endpoints
- Hypothesis: There are publicly-known CVEs / misconfigurations detectable by nuclei's default+cves+misconfigurations templates on the 8 web endpoints.
- Evidence required: nuclei JSON output; any HIGH/CRITICAL matches verified manually.
- Completion criteria: All 8 URLs scanned at safe concurrency; false-positive review done.

### T-02  osTicket installer analysis (ticket.ausecurity.best)
- Hypothesis: The installer accepts unauthenticated POSTs allowing (a) reinstallation over the existing DB, or (b) enumeration of DB creds / server internals.
- Evidence required: HTML of `/setup/install.php`, `/setup/setup.inc.php`, form fields, hidden tokens, `/upload/` directory listing, response to a benign OPTIONS + a benign GET of `/scp/login.php` to confirm live app coexists with installer.
- Completion criteria: Determine whether reinstall is possible (or blocked) and whether the running app is v1.18.4 vulnerable to known CVEs (CVE-2024-51377 / CVE-2023-32799 / etc.). NO destructive POST to install action. Only enumeration.

### T-03  WordPress assessment (blog.ausecurity.best)
- Hypothesis: WordPress core/plugin/theme has known vulnerabilities; user enumeration confirmed; possible weak auth surface; XML-RPC exposed.
- Evidence required: `wpscan --enumerate ap,at,cb,dbe,u1-5,m --stealthy` (no password brute force); `/xmlrpc.php` reachability + methods; `/wp-json/wp/v2/users`; theme/plugin versions.
- Completion criteria: All identified plugins/themes checked against WPVulnDB; write-ups where a known CVE applies to the deployed version.

### T-04  Apache / Nginx / PHP version CVE mapping
- Hypothesis: Apache/2.4.68, nginx/1.22.1, nginx/1.25.5, PHP/8.2.33, OpenSSH 9.2p1 may expose known CVEs.
- Evidence required: CVE list per version (searchsploit + local CVE DB); server-status/server-info reachability.
- Completion criteria: Mapped versions and known CVEs; a triaged relevance judgement per CVE.

### T-05  TLS configuration review (all HTTPS endpoints)
- Hypothesis: Weak protocols/ciphers, self-signed cert on apex, mismatched cert/hostname, cert-vs-LE-inconsistency.
- Evidence required: `sslscan` or `testssl.sh` output for each of the 3 IPs; cert chain per hostname.
- Completion criteria: Ordered list of TLS issues with severity.

### T-06  HTTP security-header review (all HTTP/HTTPS endpoints)
- Hypothesis: Missing CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
- Evidence required: `curl -skI` per endpoint; comparison table.
- Completion criteria: Per-endpoint header matrix produced.

### T-07  Web content / directory enumeration (light)
- Hypothesis: Backup files, admin panels, .git exposure, /server-status, /phpinfo.php, wp backup, config leaks.
- Evidence required: feroxbuster / ffuf against each web root with a small, high-signal wordlist (raft-small-words, common backups). No API abuse.
- Completion criteria: List of interesting paths with status/size; manual verification of anything sensitive.

### T-08  Cleartext-origin cross-check
- Hypothesis: `:8080` origins reveal internal information (X-Powered-By, hostnames, upstream/backend errors) or accept requests the fronting proxy would filter.
- Evidence required: Compare responses for same paths between 443 vhost and :8080 origin; look for host-header confusion (SSRF-lite), cache-poisoning-friendly headers.
- Completion criteria: Documented differential and any exploitable divergence.

### T-09  Email / spoofing risk documentation
- Hypothesis: Absence of MX/SPF/DMARC/DKIM allows arbitrary spoofing of `@ausecurity.best`.
- Evidence required: `dig` results (already collected); documented impact statement. NO actual spoofed email will be sent.
- Completion criteria: Finding drafted with recommended records.

### T-10  Contact / apex functional review
- Hypothesis: `contact.ausecurity.best` may host a forgotten/staging app; apex may have contact forms with server-side handling.
- Evidence required: Manual HTML/JS inspection of each; look for endpoints, hidden forms, JS-embedded API keys or third-party integrations.
- Completion criteria: Documented client-side attack surface.

### T-11  SSH exposure noting
- Hypothesis: SSH is publicly reachable on all three VPS.
- Evidence required: Banner already captured. No brute force. Recommend restriction via firewall / bastion / key-only.
- Completion criteria: Info-level finding documented.

## Constraints applied across all tasks
- Safe rate. Stop-on-block. No credential brute force. No destructive POSTs.
- Every command executed via a dedicated `execution` sub-agent.
- Raw output stored under `evidence/T-XX/`. Only verified issues written to `findings.txt`.
