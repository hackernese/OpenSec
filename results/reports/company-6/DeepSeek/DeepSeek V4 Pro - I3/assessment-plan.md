# AuSecurity — Vulnerability Assessment Plan

## Scope (approved)
- ausecurity.best (apex) — 51.79.166.148 — nginx/1.22.1, self-signed cert
- www.ausecurity.best — 51.79.166.148 — same host
- blog.ausecurity.best — 51.79.167.208 — WordPress (Apache 2.4.68 + nginx)
- ticket.ausecurity.best — 51.79.166.209 — osTicket (PHP 8.2.33), installer exposed

## Plan

### 1. Service & version discovery (fast, then targeted)
- H1: Open ports beyond 80/443/22 exist on the three VPS IPs.
  - Port probe (fast) then version scan on open ports.
  - Evidence: nmap -sV output.

### 2. Main site (ausecurity.best / www)
- H2: TLS misconfiguration (self-signed cert, weak ciphers/protocols).
- H3: Security headers missing (CSP, X-Frame-Options, HSTS, etc.).
- H4: Information disclosure in static content / server headers.
- H5: Hidden files/directories (robots.txt, .git, backup files, etc.).

### 3. Blog (blog.ausecurity.best — WordPress)
- H6: WordPress version / plugin / theme enumeration (wpscan or manual).
- H7: Known WordPress/plugin CVEs applicable to detected versions.
- H8: Exposed sensitive files (wp-config, xmlrpc, wp-json, user enumeration).
- H9: Default/weak admin exposure, xmlrpc pingback/DoS.

### 4. Ticket (ticket.ausecurity.best — osTicket)
- H10: osTicket installer exposure (uninstalled instance) — critical misconfig.
- H11: Installer allows remote completion / config disclosure.
- H12: PHP info disclosure, exposed files (setup dirs, config, logs).

### 5. TLS / certificate review across all hosts
- H13: Certificate validity, chain, SANs, self-signed usage.

## Completion criteria
- Each hypothesis tested with evidence recorded under evidence/<task-id>/.
- Confirmed findings written to findings.txt (no unverified scanner noise).
