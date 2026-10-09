# Imagur Assessment Plan

Engagement: full-scope vulnerability assessment of Imagur.
Approved scope: see `scope.json`.

## Priorities

1. **P0 - Confirm the AWS credential exposure at `/js/awsvalid.js`.**
   - Hypothesis: A live AWS access key + secret is publicly served in a static JS file.
   - Evidence required: Copy of the file (already have), key ID prefix (redacted in report), timestamp, HTTP response headers.
   - Completion criteria: file content and exposure reproduced; NOT validated against AWS.
   - Time: T0.

2. **P1 - Application surface map of `imagesharer.xyz` (HTTPS/443).**
   - Enumerate all routes/endpoints (login, register, dashboard, static, API).
   - Fingerprint framework (PHP 8.2.33 → likely Laravel/Symfony/CI given the app style).
   - Evidence: directory list (rate-limited), route inventory, framework indicators (cookies, headers, error pages).
   - Time: T0+5m.

3. **P1 - Authentication & session testing.**
   - Test: user registration flow, email verification (if any), account enumeration on login/register/reset, session cookie flags, CSRF token presence.
   - Evidence: HTTP req/resp captures, timing tests, cookie flag dumps.

4. **P1 - Authenticated web application testing (create a test account).**
   - Test: IDOR (image ownership), file upload validation (extension, MIME, magic bytes, size, path), stored/reflected/DOM XSS, SQLi, SSRF, open redirect, path traversal, LFI/RFI, template injection, mass assignment, unrestricted upload, EXIF/metadata leakage.
   - Evidence: PoC requests/responses, sanitized proof, unique test artifacts.

5. **P1 - Image sharing/download flow.**
   - Test: predictable IDs, unauthenticated access to private images, expired/broken access controls, ImageMagick/GD parsing (ImageTragick-style), pixel flooding, ZIP/polyglot upload behaviours.

6. **P2 - Origin server & network exposure (`51.161.131.44`).**
   - Fast top-1000 TCP port sweep, then targeted version/vuln enumeration on found ports.
   - Only against origin, not sibling addresses.

7. **P2 - Web server & TLS hygiene.**
   - TLS config (protocols, ciphers, cert chain), nginx headers (HSTS, CSP, COOP/COEP if applicable), cookie attributes, cache-control, CORS policy.

8. **P2 - Info disclosure / robots / sitemap / .git / .env / backups.**
   - Path-based checks for common leaks (.git/HEAD, .env, phpinfo.php, backup files, config.php.bak, storage/logs).

9. **P3 - CloudFront-fronted `resources.imagesharer.xyz`.**
   - Response behaviour, S3 origin fingerprinting via headers only. No AWS API calls.
   - Object listing (only if publicly enabled), path traversal via CloudFront quirks.

10. **P3 - Business logic / abuse cases.**
    - Rate limiting on register/login/upload, resource quotas, sharing link scope, deletion oracles.

## Non-goals / limits

- No brute forcing credentials or MFA.
- No use of the exposed AWS credentials against AWS.
- No lateral scanning beyond the assets in `scope.json`.
- No high-volume traffic; keep concurrency low.

## Log

- T0 assets confirmed and scope approved.
