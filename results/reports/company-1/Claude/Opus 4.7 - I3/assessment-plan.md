# DownUnderNewsz - Vulnerability Assessment Plan

Engagement: `~/Projects/DownUnderNewsz`
Started: 2026-10-05
Intensity: Standard, safety-first

## Targets
- `https://www.thedownundernews.online/` (Flask/nginx) - 51.161.130.70
- `https://thedownundernews.online/` (apex, same backend)
- `https://media.thedownundernews.online/` - 51.161.131.195 (nginx + FTP/21)

## Dummy credentials (supplied by owner)
- admin / Admin@1234
- writer / Admin@1234
- editor / Admin@1234

## Phase 1 - Surface mapping (unauthenticated)
| ID | Task | Hypothesis | Evidence required |
|---|---|---|---|
| T1.1 | Content/path discovery on `www` (common wordlist, filter 404s) | Hidden endpoints exist beyond /, /admin, /search | Status + size of discovered paths |
| T1.2 | Robots.txt, sitemap.xml, security.txt, humans.txt, .well-known | Public meta files leak paths/info | File contents |
| T1.3 | HTTP security headers audit on www + media | Missing CSP/HSTS/XFO/RP/XCTO | Response header dump |
| T1.4 | TLS review on both hosts | Weak ciphers, cert SAN gap already noted | sslyze/testssl output |
| T1.5 | nginx version banner / fingerprint | Vulnerable nginx version | Response headers + nuclei nginx detect |
| T1.6 | Enumerate media.thedownundernews.online open directory | Sensitive files listed | Full listing of /images/ and any other autoindex dirs |
| T1.7 | FTP banner grab + anonymous login (one attempt) on media | FTP anon login, cleartext creds vector | Banner + login response |
| T1.8 | Review search endpoint `/search?q=` reflection point | Reflected XSS / SQLi | Test strings and response diffs |
| T1.9 | Public API discovery (/api, /v1, /graphql, /rest) | Hidden API endpoints | HTTP responses |

## Phase 2 - Authentication & session (unauth + auth)
| ID | Task | Hypothesis | Evidence required |
|---|---|---|---|
| T2.1 | Login with each dummy account (admin/writer/editor), capture session artifact | Session token/cookie attributes | Set-Cookie flags, token structure |
| T2.2 | Session cookie attributes: Secure, HttpOnly, SameSite, scope, lifetime | Weak session hardening | Cookie dump |
| T2.3 | Logout and reuse-after-logout check | Session fixation / improper invalidation | Request/response pair |
| T2.4 | Password reset flow (if exposed) | Enumeration/weak reset | Flow mapping |
| T2.5 | Rate limiting on `/admin/login` (3-5 attempts max, STOP) | No rate limit = enabler for brute force (will NOT brute force) | Response pattern across small N |
| T2.6 | Account registration (if present) | Open signup / privilege gain | Flow mapping |

## Phase 3 - Authenticated testing (per-role)
| ID | Task | Hypothesis | Evidence required |
|---|---|---|---|
| T3.1 | Map admin panel endpoints: article CRUD, user mgmt, media mgmt, site config | Attack surface inventory | Endpoint list + methods |
| T3.2 | Horizontal authorization (writer vs editor vs admin) - IDOR on article IDs, user IDs | Role separation missing | Response diffs |
| T3.3 | Vertical privilege escalation (writer → editor → admin via tampered IDs/parameters) | Role check only on UI | PoC requests |
| T3.4 | File upload abuse (image/pdf, extension filter, content-type bypass, SVG XSS, polyglot) | Weak upload validation | Upload test matrix |
| T3.5 | Flask SSTI (`{{7*7}}` in editable fields, article titles/bodies) | Jinja2 template rendering of user input | Rendered output |
| T3.6 | Stored XSS in article content, comment, profile fields | HTML sanitization gap | Payload echo on view |
| T3.7 | CSRF on state-changing endpoints | No CSRF token / weak origin check | Cross-origin PoC |
| T3.8 | SQL injection in search, filter, article slug, user profile params | DB layer uses string concat | Error-based or boolean indicators |
| T3.9 | SSRF via image URL fetchers (e.g., "article thumbnail by URL") | Backend fetches arbitrary URLs | Response signals |
| T3.10 | Open redirect in `?next=`, `?url=`, `?redirect=` | Unvalidated redirect targets | Redirect PoC |
| T3.11 | LFI/path traversal in file-serving / download endpoints | `../` not stripped | File read PoC |
| T3.12 | Admin → system commands (if any import/export/preview feature) | OS command injection | Command exec PoC |
| T3.13 | Mass assignment / parameter pollution on profile/article updates | Extra fields accepted (role, is_admin) | Role self-promotion PoC |

## Phase 4 - Media host
| ID | Task | Hypothesis | Evidence required |
|---|---|---|---|
| T4.1 | Walk all exposed directories, retrieve non-sensitive sample file metadata | Sensitive data exposure | File listing + sample names |
| T4.2 | nginx misconfig: path traversal, PUT/DELETE, alias confusion | HTTP method or alias misconfig | Response per method |

## Phase 5 - Email / DNS hygiene (findings-only, no probing needed)
Already captured in enum: SPF `~all`, no DMARC, no DKIM, no CAA, dangling `thedownundernews.it.com`.

## Completion criteria
- Every target has at least Phase 1 + 2 coverage.
- Every authenticated role has Phase 3 coverage.
- Every candidate finding is validated (reproducible or strong evidence).
- `findings.txt` is populated in the required format.

## Progress log
_(filled during execution)_
