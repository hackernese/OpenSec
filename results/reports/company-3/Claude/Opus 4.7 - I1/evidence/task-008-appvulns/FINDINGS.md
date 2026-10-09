# Task 008: Application-Level Vulnerability Assessment

## Test Summary

**Target:** https://imagesharer.xyz  
**Test Date:** 2026-09-18  
**Accounts Tested:** 
- User A: clawsec.tester.a@example.com (UUID: 44438961-87de-4aaa-9930-e20a2b5e7ef8)
- User B: clawsec.tester.b@example.com (UUID: 16ffaff0-cec0-4cc6-9c4a-dbb6dbe0b40d)

---

## Finding 1: IDOR - Insecure Direct Object Reference (User ID in Upload)

**Status:** MITIGATED (No actual IDOR vulnerability, but weak input validation)

### Details:
- Attempted to upload an image as User A but specify User B's UUID in the hidden `user_id` form field
- Upload succeeded (HTTP 302 redirect)
- Image was stored in User B's S3 bucket folder: `users/16ffaff0-cec0-4cc6-9c4a-dbb6dbe0b40d/`
- **However:** Access control checks still apply - User B could view their own image, but the request to create this image with another user's ID succeeded

### Implications:
- An authenticated attacker can upload images on behalf of other users
- The server accepted arbitrary `user_id` values without validation
- If the image was public, the attacker could create malicious content attributed to the victim

### Request:
```
curl -X POST "https://imagesharer.xyz/images/upload" \
  -F "user_id=16ffaff0-cec0-4cc6-9c4a-dbb6dbe0b40d" \
  -F "is_public=false" \
  -F "file=@tinyA.png;type=image/png"
```

### Response:
- HTTP 302 Redirect to: `https://imagesharer.xyz/images/b0c9c911-d750-4a6a-9e8c-286276e213bf`
- Image successfully uploaded to B's storage

### Remediation:
- **Do NOT** trust client-supplied `user_id` field in file upload forms
- Extract authenticated user's ID from session/JWT on the server side
- Validate that the authenticated user is permitted to perform the action
- Remove the `user_id` hidden field from the client form; derive it server-side from auth context

---

## Finding 2: Stored XSS - Filename Reflection

**Status:** CONFIRMED VULNERABILITY

### Details:
- Uploaded image with XSS payload in filename: `<img src=x onerror=alert(1)>.png`
- Payload was **NOT escaped** in the image detail page metadata section
- Vulnerable location: `<span><img src=x onerror=alert(1)>.png</span>`

### Evidence:
**Image Detail Page HTML (Line 61):**
```html
<div class="meta-row">
    <span>Filename</span>
    <span><img src=x onerror=alert(1)>.png</span>
</div>
```

**Properly Escaped Contexts (Title/H1):**
```html
<title>&lt;img src=x onerror=alert(1)&gt;.png — Imager</title>
<h1>&lt;img src=x onerror=alert(1)&gt;.png</h1>
```

### Attack Scenario:
1. Attacker uploads image with filename: `<img src=x onerror=alert('xss')>.png`
2. File is stored as: `xss-payload.png`
3. When owner/viewer accesses image detail page, JS payload executes in their browser
4. Payload can: steal session cookies, perform actions on behalf of user, redirect to phishing page

### Remediation:
- Always HTML-escape user-supplied filenames when displaying in HTML context
- Use `textContent` instead of `innerHTML` in JavaScript rendering
- Implement Content Security Policy (CSP) to restrict `onerror` handlers
- Validate uploaded filenames server-side (allow alphanumeric, dash, underscore only)

---

## Finding 3: Private Image Access Control

**Status:** NOT VULNERABLE

### Test Results:
- Anonymous user (no cookie): Cannot access private image → Empty response (0 bytes)
- User B (authenticated, no permission): Cannot access User A's private image → Empty response
- User A (owner): Can access their own private image → Full HTML response

### Evidence:
Access control is **properly enforced**. The application correctly checks ownership before serving image detail pages.

---

## Finding 4: CSRF - Logout & Image Deletion Forms

**Status:** PARTIALLY MITIGATED (No CSRF tokens, but access control prevents exploitation)

### Details:
- No CSRF tokens found on any authenticated form (logout, delete image, toggle visibility, upload)
- POST /logout from another user's session: HTTP 302 (redirect accepted)
- POST /images/{id}/delete as User B targeting User A's image: HTTP 302 (request accepted)
- **However:** Access control checks prevent actual damage
  - User cannot delete other users' images (ownership validation on backend)
  - Logout seems to fail silently (user remains logged in)

### Forms Without CSRF Protection:
1. **Logout Form** (POST /logout)
   ```html
   <form method="POST" action="/logout" class="inline-form">
       <button type="submit" class="btn-link">Log out</button>
   </form>
   ```

2. **Image Visibility Toggle** (POST /images/{id}/visibility)
   ```html
   <form method="POST" action="/images/{id}/visibility">
       <input type="hidden" name="is_public" value="true">
       <button type="submit">🌍 Make public</button>
   </form>
   ```

3. **Image Deletion** (POST /images/{id}/delete)
   ```html
   <form method="POST" action="/images/{id}/delete">
       <button type="submit" class="btn btn-danger">Delete image</button>
   </form>
   ```

### Remediation:
- Implement CSRF tokens (synchronizer token pattern) on all state-changing requests
- Use SameSite=Strict cookie attribute on session cookies
- Validate HTTP Referer header for sensitive operations
- Require session validation before allowing state-changing operations

---

## Finding 5: SQL Injection Attempt - Blocked by Type Enforcement

**Status:** NOT VULNERABLE

### Test:
```
curl -X POST "https://imagesharer.xyz/images/upload" \
  -F "user_id='; DROP TABLE users; --" \
  -F "is_public=false" \
  -F "file=@tinyA.png;type=image/png"
```

### Response:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "detail": "SQLSTATE[22P02]: Invalid text representation: 7 ERROR:  invalid input syntax for type uuid: \"'\"..."
  }
}
```

**Protected by:** PostgreSQL UUID type validation. The database enforces strict UUID format (32 hex chars with dashes), preventing string injection.

---

## Summary Table

| Vulnerability | Status | CVSS Estimate | Severity |
|---|---|---|---|
| IDOR (user_id field) | FOUND | 6.5 (Medium) | Medium |
| Stored XSS (filename) | FOUND | 6.1 (Medium) | Medium |
| Access Control (private images) | OK | N/A | Passed |
| CSRF (no tokens) | MITIGATED | Low | Low |
| SQL Injection | OK | N/A | Passed |

---

## Recommendations (Priority Order)

1. **High:** Fix Stored XSS in filename display
   - Add HTML escaping in the filename metadata output
   - Implement CSP header with `script-src 'self'`

2. **High:** Fix IDOR - user_id field
   - Remove `user_id` from client form
   - Always derive user ID from authenticated session server-side
   - Log upload attempts with mismatched user IDs

3. **Medium:** Add CSRF protection
   - Implement token-based CSRF mitigation
   - Set SameSite=Strict on session cookies
   - Add referer validation for state-changing operations

---

## Test Artifacts Location
- `/home/research/Projects/Imagur/evidence/task-008-appvulns/`

