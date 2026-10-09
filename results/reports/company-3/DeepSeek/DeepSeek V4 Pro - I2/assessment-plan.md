# Assessment Plan — Imagur (imagesharer.xyz)

Engagement: Imagur / FShare — image hosting service
Date: 2026-10-05/06
State: ASSESSING

## In-scope assets
- Web app: https://imagesharer.xyz/ (+ www)
- Origin VPS: 51.161.131.44 (nginx, PHP 8.2.34)
- CDN: resources.imagesharer.xyz → CloudFront d273uevi0662l0.cloudfront.net
- AWS account 016170038077: S3 filesharer-research, filesharer-research-testing, RDS Aurora PostgreSQL database-2, IAM console-admin/fokirohu, SG sg-0fb1d9ee18578a337, default VPC

## Leads from enumeration (to confirm/validate)
1. Hardcoded AWS credentials in /js/awsvalid.js (root) — HIGH priority
2. S3 bucket filesharer-research publicly listable — HIGH
3. SSH security group open 0.0.0.0/0 — MEDIUM
4. CloudFront default cert / no custom alias; deleted origin bucket — LOW
5. nginx + PHP 8.2 app with /login /register /dashboard /upload — primary attack surface

## Planned tasks

### Web application (primary)
| # | Hypothesis | Method | Evidence required | Completion |
|---|---|---|---|---|
| W1 | App surface map | Crawl routes, JS, HTML, robots | Route list, form params | Mapped |
| W2 | Hardcoded secrets in client code | Review /js/*.js | Presence of keys (redact) | Confirmed |
| W3 | SQL injection in login/register/search | Parameterized fuzz (safe) | Error/behavioral evidence | Confirmed/refuted |
| W4 | Auth bypass / weak auth | Login logic review | Bypass proof | Confirmed/refuted |
| W5 | File upload flaws (arbitrary upload, traversal, stored XSS) | Upload crafted files | Malicious file accepted | Confirmed/refuted |
| W6 | IDOR on images/users | Access others' objects | Unauthorized read | Confirmed/refuted |
| W7 | XSS (reflected/stored) | Inject payloads | Execution context | Confirmed/refuted |
| W8 | SSRF via image URL fetch | URL parameter abuse | Internal request | Confirmed/refuted |
| W9 | Command injection | Input → shell | RCE proof | Confirmed/refuted |
| W10 | Sensitive data exposure / info leak | Headers, error pages, source | Leaked data | Confirmed/refuted |
| W11 | CSRF / session issues | Cookie flags, tokens | Missing protections | Confirmed/refuted |

### Cloud configuration (read-only review)
| # | Hypothesis | Method | Evidence | Completion |
|---|---|---|---|---|
| C1 | S3 filesharer-research public | Anonymous GET/list | Listing + object read | Confirmed |
| C2 | Over-privileged IAM / root creds | Read-only API | Policy evidence | Confirmed |
| C3 | RDS misconfig | Config review | Exposure | Confirmed |
| C4 | Open SSH SG | SG review | 0.0.0.0/0 | Confirmed |

## Method notes
- Non-destructive only; minimal proof of concept.
- No brute force, no data exfiltration, no lateral movement.
- Redact all secrets/credentials in findings and reports.
