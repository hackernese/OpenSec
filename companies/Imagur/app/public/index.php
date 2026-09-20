<?php

declare(strict_types=1);

// ── Bootstrap ────────────────────────────────────────────────────────────────

define('BASE_PATH', dirname(__DIR__));

require BASE_PATH . '/vendor/autoload.php';

// Load .env
(function () {
    $envFile = BASE_PATH . '/.env';
    if (!file_exists($envFile)) {
        return;
    }
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || str_starts_with($line, '#')) {
            continue;
        }
        if (str_contains($line, '=')) {
            [$key, $value] = explode('=', $line, 2);
            $key   = trim($key);
            $value = trim($value);
            if (!array_key_exists($key, $_ENV)) {
                putenv("$key=$value");
                $_ENV[$key]    = $value;
                $_SERVER[$key] = $value;
            }
        }
    }
})();

use Imager\middleware\ErrorHandler;
use Imager\middleware\CookieMiddleware;
use Imager\middleware\AuthorizationHeaderMiddleware;
use Imager\modules\auth\AuthController;
use Imager\modules\images\ImagesController;
use Imager\UI\AuthUiController;
use Imager\UI\DashboardController;
use Imager\UI\ImagesUiController;
use Imager\UI\ProfileUiController;

// Register global error / exception handler
ErrorHandler::register();

// ── Cookie parsing ────────────────────────────────────────────────────────────

// Parse incoming cookies with automatic deserialization
CookieMiddleware::parseIncomingCookies([
    'user_preferences' => ['format' => CookieMiddleware::FORMAT_JSON],
    'cart_items' => ['format' => CookieMiddleware::FORMAT_JSON, 'encrypt' => true],
    'session_data' => ['format' => CookieMiddleware::FORMAT_PHP, 'encrypt' => true],
    'theme_settings' => ['format' => CookieMiddleware::FORMAT_JSON],
]);

// ── Authorization Header Middleware ───────────────────────────────────────────

// Handle IsAuthorized header and set AuthorizedCode response header if needed
AuthorizationHeaderMiddleware::handle();

// ── Request parsing ───────────────────────────────────────────────────────────

$method = strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');
$uri    = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
$uri    = rtrim($uri, '/') ?: '/';

// Read JSON body once; multipart is handled via $_POST / $_FILES
$rawBody = file_get_contents('php://input');
$body    = [];
$ct      = $_SERVER['CONTENT_TYPE'] ?? '';
if ($rawBody !== '' && str_contains($ct, 'application/json')) {
    $decoded = json_decode($rawBody, true);
    if (is_array($decoded)) {
        $body = $decoded;
    }
}

// ── CORS (API only) ───────────────────────────────────────────────────────────

$isApiRequest = str_starts_with($uri, '/api/');

if ($isApiRequest) {
    $allowedOrigin = getenv('CORS_ORIGIN') ?: 'https://imager.it.com';
    $origin        = $_SERVER['HTTP_ORIGIN'] ?? '';

    if ($origin === $allowedOrigin) {
        header("Access-Control-Allow-Origin: $origin");
        header('Access-Control-Allow-Credentials: true');
    }

    header('Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Authorization, Content-Type, Accept');

    if ($method === 'OPTIONS') {
        http_response_code(204);
        exit;
    }

    header('Content-Type: application/json; charset=utf-8');
}

// ── Router helper ─────────────────────────────────────────────────────────────

$params = [];
$match  = static function (string $pattern) use ($uri, &$params): bool {
    if (preg_match($pattern, $uri, $m)) {
        $params = $m;
        return true;
    }
    return false;
};

// ════════════════════════════════════════════════════════════════════════════
// UI ROUTES  (HTML, session-based)
// ════════════════════════════════════════════════════════════════════════════

// ── Root redirect ─────────────────────────────────────────────────────────────
if ($method === 'GET' && $uri === '/') {
    header('Location: /dashboard');
    exit;
}

// ── Auth UI ───────────────────────────────────────────────────────────────────
if ($method === 'GET' && $uri === '/login') {
    (new AuthUiController())->loginForm();
    exit;
}

if ($method === 'POST' && $uri === '/login') {
    (new AuthUiController())->loginSubmit();
    exit;
}

if ($method === 'GET' && $uri === '/register') {
    (new AuthUiController())->registerForm();
    exit;
}

if ($method === 'POST' && $uri === '/register') {
    (new AuthUiController())->registerSubmit();
    exit;
}

if ($method === 'POST' && $uri === '/logout') {
    (new AuthUiController())->logoutSubmit();
    exit;
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
if ($method === 'GET' && $uri === '/dashboard') {
    (new DashboardController())->index();
    exit;
}

// ── Profile ───────────────────────────────────────────────────────────────────
if ($method === 'GET' && $uri === '/profile') {
    (new ProfileUiController())->show();
    exit;
}

if ($method === 'POST' && $uri === '/profile/avatar') {
    (new ProfileUiController())->uploadAvatar();
    exit;
}

// ── Image UI ──────────────────────────────────────────────────────────────────
if ($method === 'GET' && $uri === '/images/upload') {
    (new ImagesUiController())->uploadForm();
    exit;
}

if ($method === 'POST' && $uri === '/images/upload') {
    (new ImagesUiController())->uploadSubmit();
    exit;
}

if ($method === 'GET' && $match('#^/images/(?P<id>[0-9a-f\-]{36})$#')) {
    (new ImagesUiController())->show($params['id']);
    exit;
}

if ($method === 'POST' && $match('#^/images/(?P<id>[0-9a-f\-]{36})/visibility$#')) {
    (new ImagesUiController())->toggleVisibility($params['id']);
    exit;
}

if ($method === 'POST' && $match('#^/images/(?P<id>[0-9a-f\-]{36})/delete$#')) {
    (new ImagesUiController())->delete($params['id']);
    exit;
}


// ════════════════════════════════════════════════════════════════════════════
// API ROUTES  (JSON, Bearer JWT)
// ════════════════════════════════════════════════════════════════════════════

if ($method === 'GET' && $uri === '/api/v1/health') {
    echo json_encode(['status' => 'ok', 'service' => 'imager']);
    exit;
}

if ($method === 'POST' && $uri === '/api/v1/auth/register') {
    (new AuthController())->register($body);
    exit;
}

if ($method === 'POST' && $uri === '/api/v1/auth/login') {
    (new AuthController())->login($body);
    exit;
}

if ($method === 'POST' && $uri === '/api/v1/auth/logout') {
    (new AuthController())->logout();
    exit;
}

if ($method === 'GET' && $uri === '/api/v1/images') {
    (new ImagesController())->index();
    exit;
}

if ($method === 'POST' && $uri === '/api/v1/images') {
    (new ImagesController())->store($body);
    exit;
}

if ($method === 'GET' && $match('#^/api/v1/images/(?P<id>[0-9a-f\-]{36})$#')) {
    (new ImagesController())->show($params['id']);
    exit;
}

if ($method === 'PATCH' && $match('#^/api/v1/images/(?P<id>[0-9a-f\-]{36})$#')) {
    (new ImagesController())->update($params['id'], $body);
    exit;
}

if ($method === 'DELETE' && $match('#^/api/v1/images/(?P<id>[0-9a-f\-]{36})$#')) {
    (new ImagesController())->destroy($params['id']);
    exit;
}


// ── 404 fallback ──────────────────────────────────────────────────────────────
if ($isApiRequest) {
    http_response_code(404);
    echo json_encode([
        'error' => ['code' => 'NOT_FOUND', 'message' => 'The requested endpoint does not exist.'],
    ]);
} else {
    http_response_code(404);
    // Minimal HTML 404 for browser requests
    echo '<!DOCTYPE html><html><head><title>404 — Imager</title>
    <link rel="stylesheet" href="/css/app.css"></head><body>
    <header class="site-header"><a href="/" class="logo">📷 Imager</a></header>
    <main class="container"><div class="empty-state" style="padding-top:5rem">
    <div class="icon">🔍</div><p>Page not found.</p>
    <a href="/dashboard" class="btn btn-primary">Go to dashboard</a>
    </div></main></body></html>';
}
