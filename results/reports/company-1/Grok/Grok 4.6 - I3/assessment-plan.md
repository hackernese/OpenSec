# Assessment plan — DownUnderNewsz

State: ASSESSING
In-scope: thedownundernews.online, www.thedownundernews.online, 51.161.130.70
Out of scope: media host, claimed it.com domain, third-party providers

Owner-provided test roles (passwords not stored here): admin, writer, editor

## Coverage

| ID | Hypothesis | When | Required evidence | Completion |
|----|------------|------|-------------------|------------|
| T1 | Extra services listen on the web server besides 80/443 | start | nmap top-ports output | open TCP ports listed |
| T2 | Open services have identifiable versions / known issues | after T1 | nmap -sV on open ports only | service names/versions recorded |
| T3 | TLS configuration is weak or certificate mismatches apex | parallel | testssl or nmap ssl scripts / openssl | cert, protocols, ciphers noted |
| T4 | Missing security headers / cookie flags | parallel | HTTP response headers | header set documented |
| T5 | Application stack and public routes are discoverable | after T4 | homepage/about/contact HTML, JS, links | route map |
| T6 | Hidden paths exist (admin, api, backups, .git, env) | after T5 | directory brute of small wordlist | interesting status codes |
| T7 | Unauthenticated API/data leaks or injection | after T5 | /api and related endpoints | request/response evidence |
| T8 | Login, session, and role controls fail | after T5 | owner dummy accounts only | session/cookie/role evidence |
| T9 | Input sinks (search, contact, article params, APIs) are injectable | after T7/T8 | safe SQLi/XSS/SSTI/path tests | confirmed or ruled out |
| T10 | Access control / IDOR between admin, editor, writer, public | after T8 | role-specific requests | privilege findings |
| T11 | CSRF, upload, and state-changing issues on in-scope forms | after T8 | form/token/upload evidence | confirmed or ruled out |
| T12 | Info disclosure (errors, source, debug, backups) | throughout | error pages, headers, files | confirmed or ruled out |

## Limits

- No brute force, spraying, stuffing, DDoS, malware, phishing, or out-of-scope hosts.
- Stop at minimum proof. Do not persist destructive changes.
- Findings recorded only when in-scope, reproducible, and impact is concrete.
