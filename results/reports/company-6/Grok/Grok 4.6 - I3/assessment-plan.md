# Assessment plan — AuSecurity

State: VALIDATING → REPORTING
Scope: `ausecurity.best` only (owner-approved)
Started: 2026-10-05
Ended testing: 2026-10-05

## Constraints
- No brute force, credential stuffing, password spraying, DDoS, social engineering, or destructive tests
- Stop at minimum proof for each finding
- Commands via execution sub-agents only
- Client emails and other PII not copied into findings

## Tasks

### T1 — TLS and HTTPS baseline — DONE
- Confirmed self-signed certificate CN=ausecurity.best

### T2 — Security headers and information disclosure — DONE
- Confirmed missing HSTS/CSP/XFO/XCTO/RP; Server nginx/1.22.1

### T3 — Surface mapping — DONE
- Pages: /, index, about, services, case-studies, contact, login, dashboard, consultation-success
- APIs: /api/auth/me, /api/auth/login, /api/auth/logout, /api/contact, /api/health
- ffuf on / and /api; FastAPI-style errors; /docs not exposed

### T4 — Unauthenticated access control — DONE
- Dashboard HTML served without session; /api/auth/me returns 401

### T5 — Authentication and session handling — DONE
- Invalid login 401; SQLi login probe 401 no error; no credential spraying
- Open redirect in login JS confirmed in source

### T6 — Injection and input handling — DONE
- DOM XSS via name→innerHTML confirmed
- Contact SQLi message not evidenced
- Combined h=localhost/127.0.0.1 caused 500; not promoted to confirmed SSRF

### T7 — Sensitive file exposure — DONE
- .git, .env, maps, package.json, phpinfo, actuator: 404
- /assets/ 403 no listing

### T8 — Cookie, CORS, and CSRF — DONE
- No cookies issued on unauthenticated requests
- CORS: ACAC true, origin not reflected — not a confirmed CORS bypass
- TRACE disabled

## Out of scope (owner did not approve)
- www / contact / blog / ticket hosts and their IPs as general targets

## Limitations
- No successful authenticated session, so cookie flags were not observed
- Dashboard record authenticity (demo vs production) not independently verified
- SSRF via contact `h` left unverified
