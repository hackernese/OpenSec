# DownUnderNewsz — Assessment Plan

Status: ASSESSING
Started: 2026-10-05
Scope: see `scope.json` and `assets.json`
Credentials: admin / writer / editor (all `Admin@1234`)

## Priorities (highest first)
1. Authenticated web app testing on the main site (role separation, IDOR/BOLA, broken access control, XSS, SQLi, file upload, SSRF, SSTI). This is where business impact is highest for a CMS-style news site with 3 roles.
2. Media VPS surface: FTP (21/tcp) banner + anonymous + encryption posture; what nginx is actually fronting (even in 502 state), accessible paths, directory listings.
3. Main site unauthenticated surface: endpoint discovery, tech fingerprint, auth flow, rate limiting, info disclosure (robots, sitemap, .env, .git, /admin, /debug).
4. Network-level checks on both IPs (targeted Nmap on in-scope ports only).
5. TLS configuration, DNS/email posture (DMARC, CAA, SPF soft-fail) — mostly already documented from enum phase.

## Task log

### T1 — Main site fingerprint & endpoint discovery (unauth)
- Hypothesis: Identify framework (looks Flask-ish from 404 page), routes, auth endpoints, admin panel path, static vs dynamic surface.
- Evidence required: HTTP responses, headers, HTML, robots.txt, sitemap.xml, security.txt, 404 behavior, server/framework banner.
- Completion: have a route inventory + confirmed tech stack.
- Status: pending

### T2 — Authentication flow analysis
- Hypothesis: Session cookie or JWT; may have weak session handling, no CSRF, verbose errors, user enumeration.
- Evidence: login request/response for each role, cookie attributes (Secure, HttpOnly, SameSite), logout behavior, password reset flow if any.
- Completion: documented auth model + any weaknesses.
- Status: pending

### T3 — Role separation / BOLA / vertical & horizontal access control
- Hypothesis: Writer or editor can access admin-only functionality (user management, settings, delete, publish-override).
- Evidence: side-by-side request comparison across the three roles for every discovered admin action.
- Completion: at least one proven access control violation OR confident negative.
- Status: pending

### T4 — Injection: XSS (stored/reflected/DOM) in article/content fields
- Hypothesis: Writer/editor can inject stored XSS via article body, title, image alt, comments, etc. that fires in a reader's browser (or admin's).
- Evidence: payload persisted + rendered unescaped.
- Completion: PoC alert() or benign DOM marker in the rendered article.
- Status: pending

### T5 — Injection: SQLi / NoSQLi on search, article listings, filters, login
- Hypothesis: Query parameters are concatenated into DB queries.
- Evidence: error-based, boolean-based, or time-based differential (bounded 5–10s delays only).
- Completion: proven injection point OR confident negative on tested endpoints.
- Status: pending

### T6 — File upload abuse (very likely attack surface on a news CMS)
- Hypothesis: Image/media upload accepts dangerous types, no server-side MIME/extension validation, path traversal, SVG XSS, or files served from app origin.
- Evidence: upload artifact URL and its rendered/served behavior.
- Completion: proven file-type bypass OR path traversal OR server-side execution OR confident negative.
- Status: pending

### T7 — SSRF / URL fetchers
- Hypothesis: If articles can fetch remote images or embed URLs, an attacker can hit internal metadata (169.254.169.254), localhost admin, or other internal services.
- Evidence: internal response reflected OR DNS/HTTP callback to a controlled canary.
- Completion: proven internal fetch OR confident negative.
- Status: pending

### T8 — Server-side template injection (SSTI)
- Hypothesis: If Jinja2 (Flask), unsanitized reflected input in a template can allow {{7*7}} evaluation.
- Evidence: evaluated expression in response.
- Completion: proven template evaluation OR confident negative.
- Status: pending

### T9 — Business logic & workflow abuse
- Hypothesis: Writer can publish without editor approval; editor can delete admin-created content; comment moderation bypass; draft disclosure.
- Evidence: workflow walkthrough across roles.
- Completion: documented logic flaw(s) OR confident negative.
- Status: pending

### T10 — Media VPS surface
- T10a — Nmap of 51.161.131.195 ports 21,80,443 (service/version)
- T10b — FTP banner + anonymous login + cleartext/encryption posture check
- T10c — HTTP(S) on media host: what paths work past the 502? directory listing? static assets?
- Status: pending

### T11 — Main site network surface
- T11a — Nmap of 51.161.130.70 ports 80,443 (service/version + default scripts, no vuln scripts that are destructive)
- T11b — TLS posture (versions, ciphers, cert chain, HSTS)
- Status: pending

### T12 — Information disclosure sweep
- Hypothesis: Exposed .git, .env, backup files, debug endpoints, verbose stack traces, API docs (/swagger, /openapi.json), admin consoles.
- Evidence: direct responses.
- Completion: list of exposed sensitive endpoints OR confident negative.
- Status: pending

### T13 — HTTP security headers / cookie flags / CSRF
- Status: pending

### T14 — Rate limiting / account enumeration / password reset abuse
- Status: pending

## Validation / Reporting
- Each confirmed issue -> write to `findings.txt` using the standard format.
- Only confirmed, reproducible, in-scope issues are "findings". Candidates/leads live in this plan.
