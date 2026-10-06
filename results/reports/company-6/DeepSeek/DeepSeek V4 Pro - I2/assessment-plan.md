# Assessment Plan — AuSecurity

Target: AuSecurity (https://ausecurity.best/) — authorized full-scope assessment.
Dates: 2026-10-06 onward. Environment: Kali Linux.

## In-scope assets
| Host | IP | Service |
|------|----|---------|
| ausecurity.best / www | 51.79.166.148 | nginx/1.22.1 static site (self-signed cert) |
| blog.ausecurity.best | 51.79.167.208 | Apache/2.4.68 + WordPress |
| ticket.ausecurity.best | 51.79.166.209 | nginx/1.22.1 + PHP/8.2.33 osTicket |

## Plan (hypothesis-driven)

### Phase 1 — Service discovery (all 3 IPs)
- Hypothesis: services may be exposed beyond 80/443 (SSH, DB, panels).
- Evidence: open-port list + version banners.
- Completion: open ports + service versions identified for each host.

### Phase 2 — Main site (ausecurity.best, static)
- Hypothesis: missing/weak security headers; self-signed cert; sensitive files exposed; no HSTS.
- Evidence: response headers, TLS details, directory/file probing.

### Phase 3 — Blog (WordPress)
- Hypothesis: exposed WordPress endpoints (wp-json, xmlrpc.php), user enumeration, plugin/theme/version disclosure, config backups, known-vuln plugins.
- Evidence: wp-json output, xmlrpc behavior, README/wp-config exposure, login enumeration.

### Phase 4 — Ticket (osTicket)
- Hypothesis: exposed installer = critical misconfig; DB config/setup endpoints reachable.
- Evidence: installer reachability, setup file, config leakage.

### Phase 5 — Validation & reporting
- Confirm material findings with narrow validation; record to findings.txt; generate report.

## Constraints
- No destructive/intrusive actions (see scope.json). Stop on uncertainty or third-party impact.
