# Assessment Plan — DownUnderNewsz

## Scope (approved)
- `thedownundernews.online` / `www.thedownundernews.online` → 51.161.130.70 (nginx web app, ports 22/443)
- `media.thedownundernews.online` → 51.161.131.195 (media server, ports 21/22/80/443, 502 at enum time)
- Test accounts provided: admin / writer / editor (all Admin@1234)

## Tech surface (initial)
- News web app (Jinja2 templates, nginx, Let's Encrypt) with routes:
  - `/article/<slug>`, `/category/<cat>`, `/search?q=`, `/about`, `/contact`
  - Static assets under `/static/`
  - Authentication (admin/writer/editor roles) — login mechanism TBD

## Plan / hypotheses

### Phase 1 — Web app recon
- H1.1 Identify framework/stack (response headers, cookies, error pages, debug endpoints)
- H1.2 Discover endpoints (robots.txt, sitemap, common admin/login paths)
- H1.3 Identify auth mechanism (login form, session cookie properties)

### Phase 2 — Authentication
- H2.1 Login with provided accounts; confirm role separation
- H2.2 Account enumeration / verbose login errors
- H2.3 Session cookie security (HttpOnly/Secure/SameSite), session fixation
- H2.4 Password reset/change functionality abuse

### Phase 3 — Authorization / RBAC
- H3.1 Privilege escalation: writer/editor reaching admin-only functions
- H3.2 IDOR on article/user/comment identifiers across roles

### Phase 4 — Web app vulnerabilities
- H4.1 SQL injection (search, slug, category, login)
- H4.2 XSS (reflected in search; stored in article content/comments)
- H4.3 CSRF on state-changing actions
- H4.4 File upload (media) — if upload endpoint exists
- H4.5 Command injection / SSTI (Jinja2) where user input reaches templates

### Phase 5 — Media server
- H5.1 FTP anonymous/banner (port 21)
- H5.2 HTTP(S) endpoints + version detection

### Phase 6 — Infrastructure
- H6.1 Service version detection on open ports (already partially known)
- H6.2 TLS config + security headers review

## Evidence / completion criteria
Each hypothesis: required evidence + reproducible proof. Confirm findings only with strong direct evidence, staying within approved methods (no brute force, no DoS, no destructive actions).

## Status
- [x] Enumeration (enum-001)
- [ ] Phase 1 recon
- [ ] Phase 2 auth
- [ ] Phase 3 authz
- [ ] Phase 4 web vulns
- [ ] Phase 5 media
- [ ] Phase 6 infra
