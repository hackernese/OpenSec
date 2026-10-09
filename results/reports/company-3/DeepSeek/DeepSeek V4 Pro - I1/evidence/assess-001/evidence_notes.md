# Assessment Evidence Summary — Imagur (imagesharer.xyz)

Task ID: assess-001
Date: 2026-09-17

## Confirmed findings and supporting evidence

1. Hardcoded AWS root credentials (/js/awsvalid.js)
   - aws sts get-caller-identity (read-only) -> arn:aws:iam::016170038077:root (VALID)
   - Source file saved at evidence/enum-001/awsvalid.js

2. S3 bucket "filesharer-research" public read + list
   - Anonymous ListObjectsV2 returned 200 with all keys (user UUIDs + filenames)
   - Anonymous GET of private object 18d612b9... returned 200 image/png (68 bytes, PNG magic)
   - Anonymous PUT returned 403 AccessDenied (write correctly denied)
   - Bucket keys: users/<uuid>/<image-uuid>.png|.jpg

3. Stored XSS via filename
   - Upload filename '<img src=x onerror=alert(document.domain)>.png' -> image c7a40a45-bb8a-4156-a4b1-3c7977c1640a
   - Detail page rendered raw: <span>xss<img src=x onerror=alert(document.domain)>.png</span>
   - Verified in browser: alert fired with "imagesharer.xyz"

4. IDOR via hidden user_id in upload
   - Upload with User A session + User B user_id (4d572b82...) -> object stored under users/4d572b82.../16de04a2...png and appeared in User B's gallery only.

5. Missing CSRF
   - No CSRF token on /logout, /images/upload, /images/<id>/visibility, /images/<id>/delete, /profile/avatar. No Origin/Referer enforcement observed.

6. Account enumeration
   - POST /register with existing email -> "An account with that email already exists."

7. Version disclosure
   - Apache/2.4.68 (Debian) in 403 error pages; X-Powered-By: PHP/8.2.33; nginx on 80/443, Apache on 8080.

## Tests that came back negative (no finding)
- Error-based and time-based SQL injection on /login: none.
- Sensitive files (.env, .git, composer.json, etc.) on 443 and 8080: none exposed.
- Cross-account access to another user's PRIVATE image detail page: correctly denied (302 -> /dashboard).
- Cross-account visibility change and delete: state did not change (ownership enforced).
- Anonymous S3 write (PUT): denied (403).
- phpinfo.php / server-status on 8080: 403/404 (not exposed).
- Avatar upload of PHP/SVG: no objects stored (rejected).
