# AuSecurity — Vulnerability Assessment Plan

Engagement: AUTHORIZED full-scope assessment
Scope: ausecurity.best + www/contact/blog/ticket subdomains, admin login/dashboard, API backend, on IPs 51.79.166.148, 51.79.167.208, 51.79.166.209.

## Infrastructure

| Asset | IP | Stack |
|---|---|---|
| Main site + API | 51.79.166.148 | nginx 1.22.1 + FastAPI-style backend |
| WordPress blog | 51.79.167.208 | WordPress 7.1, Apache/nginx, OpenSSH |
| osTicket | 51.79.166.209 | osTicket v1.18.4 (installer exposed), PHP 8.2.33 |

## Task plan

### T1 — Network/port discovery (all 3 IPs)
Hypothesis: exposed services beyond 80/443.
Method: fast SYN scan of top ports, then version detection on open ports.
Evidence: open ports + service banners.

### T2 — Main site & API (51.79.166.148)
- T2a: TLS/self-signed cert + security headers audit (info findings).
- T2b: API auth endpoints — auth bypass on /api/auth/me, SQLi/NoSQLi on login, JWT tampering, IDOR.
- T2c: /api/contact — SSRF, command injection, header injection.
- T2d: /login + /dashboard — access control, default creds, info disclosure.
- T2e: Server-side misconfig — path traversal, method tampering, error leakage.

### T3 — WordPress blog (51.79.167.208)
- T3a: User enumeration (wp-json/wp/v2/users, author sitemaps).
- T3b: xmlrpc.php abuse + custom methods (demo.addTwoNumbers, demo.sayHello).
- T3c: Known plugin/theme/version vulns; wp-config leak; directory listing; debug log.

### T4 — osTicket (51.79.166.209)
- T4a: Exposed installer (uninstalled state) — takeover risk.
- T4b: osTicket v1.18.4 known CVEs / default creds / file disclosure.

## Rules
- One execution sub-agent per command; review outputs critically.
- No brute force, no DDoS, no destructive ops. Stop at minimum proof.
- Record confirmed findings to findings.txt only.
