# Imagur assessment plan

Engagement directory: `/home/research/Projects/Imagur`
State: ASSESSING
Date: 2026-09-18

In-scope: `imagesharer.xyz`, `www.imagesharer.xyz`, `resources.imagesharer.xyz` (CloudFront hostname), origin IP `51.161.131.44` only as that website host.

## A. Origin and TLS

- A1. Fast open-port probe of 51.161.131.44 only.
  - Hypothesis: extra services besides HTTP/HTTPS are exposed on the rented origin.
  - Evidence: open port list.
  - Done when: all open ports recorded; no netblock expansion.
- A2. Version/service scan of open ports only.
  - Hypothesis: outdated or dangerous services.
  - Evidence: service banners/versions.
- A3. TLS and HTTP security headers on apex, www, and resources.
  - Hypothesis: weak TLS, missing headers, www certificate mismatch.
  - Evidence: handshake and header captures.

## B. Web attack surface (imagesharer.xyz)

- B1. Map unauthenticated routes (robots, sitemap, common files, directory discovery).
  - Hypothesis: hidden admin, backups, debug, API, upload, image endpoints.
  - Evidence: live URL list with status codes.
- B2. Fingerprint application (PHP/nginx, cookies, forms, JS, endpoints in HTML/JS).
  - Hypothesis: identifiable framework and client-side secrets.
  - Evidence: sanitized HTML/JS notes.
- B3. Registration/login/session testing without brute force.
  - Hypothesis: weak session flags, user enumeration, mass assignment, auth bypass.
  - Evidence: request/response behavior on one test account if self-registration is public.
- B4. Access control on images and users (IDOR).
  - Hypothesis: other users' images or profiles are reachable by ID/name.
- B5. Upload and image handling.
  - Hypothesis: unrestricted file upload, XSS in SVG/HTML, path traversal, malware-type content (do not upload malware), content-type bypass.
- B6. Injection across discovered parameters (SQLi, XSS, SSTI, command, SSRF, LFI/path traversal, open redirect).
  - Hypothesis: unsanitized input on search, login, register, image metadata, headers.
  - Stop at minimum proof.
- B7. CSRF, CORS, cookie scope, cache, HTTP method tampering.
- B8. Information disclosure (source maps, .git, .env, phpinfo, errors, stack traces).

## C. CloudFront / resources.imagesharer.xyz

- C1. Public objects and misconfiguration (listing, default root, sensitive files).
- C2. Origin exposure and host-header/cache behavior limited to this distribution hostname.

## D. www.imagesharer.xyz

- D1. Confirm same app and TLS name mismatch impact.

Adapt the plan as new endpoints appear. No brute force, no destructive tests, no third-party expansion.

## Status

- A1-A3: in progress
- B-D: pending
