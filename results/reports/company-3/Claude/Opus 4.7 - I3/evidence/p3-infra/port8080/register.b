HTTP/1.1 200 OK
Date: Mon, 05 Oct 2026 05:55:17 GMT
Server: Apache/2.4.68 (Debian)
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
X-Powered-By: PHP/8.2.34
Set-Cookie: PHPSESSID=c09e30ffd73eaf8089734e1380d25fce; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Set-Cookie: page_views=%5B%7B%22page%22%3A%22auth%5C%2Fregister%22%2C%22timestamp%22%3A1791179717%2C%22user_agent%22%3A%22curl%5C%2F8.21.0%22%2C%22referer%22%3A%22%22%7D%5D; expires=Wed, 04 Nov 2026 05:55:17 GMT; Max-Age=2592000; path=/; secure; HttpOnly; SameSite=Lax
Vary: Accept-Encoding
Content-Length: 2595
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create account — Imager</title>
    <link rel="stylesheet" href="/css/app.css">

    <!-- <link rel="icon" href="https://resources.imagesharer.xyz/icon.ico" type="image/png"> -->

    <link rel="icon" href="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTlZ85k3kCmkla3sPyrD94VIVRwnfCN0BzZjLw5BGf6HQ&s=10" type="image/png">
</head>
<body>

<header class="site-header">
    <a href="/dashboard" class="logo">📷 Imager</a>
    <nav>
                    <a href="/login">Log in</a>
            <a href="/register" class="btn btn-primary btn-sm">Sign up</a>
            </nav>
</header>

<main class="container">

    
    
    <div class="auth-wrap">
    <div class="card auth-card">
        <h1>Create account</h1>

        <form method="POST" action="/register">
            <div class="form-group">
                <label for="email">Email address</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    autofocus
                    autocomplete="email"
                    placeholder="you@example.com"
                >
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    required
                    autocomplete="new-password"
                    placeholder="Min. 8 characters"
                    minlength="8"
                >
            </div>

            <div class="form-group">
                <label for="confirm">Confirm password</label>
                <input
                    type="password"
                    id="confirm"
                    name="confirm"
                    required
                    autocomplete="new-password"
                    placeholder="••••••••"
                >
            </div>

            <button type="submit" class="btn btn-primary btn-block mt-2">
                Create account
            </button>
        </form>

        <p class="form-footer">
            Already have an account? <a href="/login">Log in</a>
        </p>
    </div>
</div>

</main>

<footer class="site-footer">
    <p>Imager &mdash; your images, your control.</p>
</footer>

    <!-- <script src="/js/awsvalid.js"></script> -->


</body>
</html>
