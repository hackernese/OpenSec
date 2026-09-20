# Assessment Plan — Imagur (imagesharer.xyz)

Engagement state: ASSESSING
Scope: approved by owner (all discovered assets).

## In-scope assets
- `https://imagesharer.xyz/` (and `www`) — "Imager" PHP app, nginx + PHP 8.2.33, ports 80/443
- `http://51.161.131.44:8080/` — second "Imager" instance, Apache 2.4.68 + PHP 8.2.33
- `resources.imagesharer.xyz` → `d273uevi0662l0.cloudfront.net` (CloudFront + S3 origin)
- S3 buckets: `imagesharer` (likely), `fshare` (candidate)
- Client-side AWS credentials in `/js/awsvalid.js`

## Known leads
1. **Hardcoded AWS credentials** (access key + secret + region ap-southeast-2) shipped in `/js/awsvalid.js`.
2. Two deployments of the same app (nginx 443 vs Apache 8080) — possible config drift / dev exposure.
3. Login/register endpoints; image-sharing functionality to be mapped.

## Task plan

| ID | Hypothesis / test | Method | Evidence needed | Status |
|----|-------------------|--------|-----------------|--------|
| T1 | Exposed AWS creds are valid and disclose account identity | `aws sts get-caller-identity` (minimal proof only) | ARN/account/user id | pending |
| T2 | App has hidden/undocumented endpoints & sensitive files | directory/file brute force (both 443 & 8080) | discovered paths | pending |
| T3 | Login form vulnerable to SQL injection / auth bypass | SQLi payloads on email/password | DB error or bypass | pending |
| T4 | Registration allows weak/duplicate authz and leaks info | register + inspect | response differences | pending |
| T5 | Image upload allows malicious file types / traversal | upload SVG/HTML/PHP, path traversal | stored XSS / RCE / traversal | pending |
| T6 | IDOR on images/users/objects | enumerate object IDs, access others' | unauthorized access | pending |
| T7 | Stored/reflected XSS in titles/descriptions/comments | inject payloads | execution in browser | pending |
| T8 | SSRF via image URL fetch (if present) | URL fetch to internal | internal response | pending |
| T9 | LFI/path traversal in image serving | `../` sequences | file disclosure | pending |
| T10 | Info disclosure via headers/errors/debug | inspect responses, trigger errors | version/path/stack traces | pending |
| T11 | Apache 8080 instance differences (dev/debug) | compare responses, check debug | dev-only exposure | pending |
| T12 | CloudFront / S3 misconfig (public listing, overly permissive) | bucket policy probes, listing | public object access | pending |
| T13 | Session/cookie security (flags, fixation) | inspect cookies | missing Secure/HttpOnly | pending |
| T14 | ReDoS on any regex-driven input (if applicable) | crafted long inputs | catastrophic backtracking | pending |

## Completion criteria
- Every task completed or explicitly closed with reason.
- Findings confirmed with evidence saved under `evidence/<task-id>/`.
- `findings.txt` populated in the required format.

## Results (closed)
- T1 exposed AWS creds -> CONFIRMED valid, arn:aws:iam::016170038077:root (critical).
- T2 hidden endpoints/sensitive files -> none exposed (443 & 8080).
- T3 SQLi login -> not vulnerable (error-based and time-based negative).
- T4 registration -> account enumeration confirmed (low).
- T5 file upload -> PHP/SVG/HTML rejected; stored XSS via FILENAME confirmed (high).
- T6 IDOR -> upload user_id field trusted (medium); detail-page/visibility/delete ownership enforced.
- T7 XSS -> stored XSS on detail page confirmed in-browser.
- T8 SSRF -> no URL-fetch feature present.
- T9 LFI/path traversal -> not applicable (images served from S3).
- T10 info disclosure -> Apache/PHP version disclosure (info).
- T11 Apache 8080 differences -> same app, no extra exposure.
- T12 CloudFront/S3 -> S3 bucket filesharer-research public list+read (high); write denied.
- T13 session cookies -> Secure/HttpOnly/SameSite=Lax set (good).
- T14 ReDoS -> no regex-driven input identified; not applicable.
