<?php

declare(strict_types=1);

namespace Imager\UI;

use Imager\middleware\CookieMiddleware;

/**
 * Base class for all UI (HTML) controllers.
 *
 * Provides:
 *  - Session start + JWT storage (now with optional cookie serialization)
 *  - Flash messages (one-shot notices)
 *  - Redirect helper
 *  - View renderer (renders views/ templates with extracted variables)
 *  - Auth guard
 *  - Cookie-based preferences and data storage
 */
abstract class BaseController
{
    public function __construct()
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }

    // ── Session / auth ────────────────────────────────────────────────────────

    protected function isLoggedIn(): bool
    {
        return !empty($_SESSION['jwt']);
    }

    protected function requireLogin(): void
    {
        if (!$this->isLoggedIn()) {
            $this->redirect('/login');
        }
    }

    protected function requireGuest(): void
    {
        if ($this->isLoggedIn()) {
            $this->redirect('/dashboard');
        }
    }

    protected function getToken(): string
    {
        return $_SESSION['jwt'] ?? '';
    }

    protected function login(string $token): void
    {
        session_regenerate_id(true);
        $_SESSION['jwt'] = $token;
        
        // Also store login timestamp in a cookie for analytics
        CookieMiddleware::set('last_login', [
            'timestamp' => time(),
            'session_id' => session_id(),
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
        ], [
            'expires' => time() + (30 * 24 * 60 * 60), // 30 days
            'format' => CookieMiddleware::FORMAT_JSON,
            'httponly' => true,
            'secure' => true,
        ]);
    }

    protected function logout(): void
    {
        // Store logout timestamp before clearing session
        CookieMiddleware::set('last_logout', [
            'timestamp' => time(),
            'session_duration' => $this->getSessionDuration(),
        ], [
            'expires' => time() + (7 * 24 * 60 * 60), // 7 days
            'format' => CookieMiddleware::FORMAT_JSON,
        ]);
        CookieMiddleware::set('PHPSESSID', [
            'timestamp' => time(),
            'session_duration' => $this->getSessionDuration(),
        ], [
            'expires' => 0,
            'format' => CookieMiddleware::FORMAT_JSON,
        ]);
        
        
        // $_SESSION = [];
        // session_destroy();
        
        // Clear login-related cookies
        CookieMiddleware::delete('last_login');
    }

    // ── Flash messages ────────────────────────────────────────────────────────

    protected function flash(string $type, string $message): void
    {
        $_SESSION['_flash'][$type] = $message;
    }

    protected function getFlash(): array
    {
        $flash = $_SESSION['_flash'] ?? [];
        unset($_SESSION['_flash']);
        return $flash;
    }

    // ── Redirect ──────────────────────────────────────────────────────────────

    protected function redirect(string $path): never
    {
        header('Location: ' . $path);
        exit;
    }

    // ── User Preferences (Cookie-based) ──────────────────────────────────────

    /**
     * Get user preferences from cookies.
     */
    protected function getUserPreferences(): array
    {
        return CookieMiddleware::get('user_preferences', [
            'theme' => 'light',
            'language' => 'en',
            'items_per_page' => 20,
            'notifications' => ['email' => true, 'push' => false],
            'display_settings' => ['show_thumbnails' => true],
        ]);
    }

    /**
     * Set user preferences in cookies.
     */
    protected function setUserPreferences(array $preferences): void
    {
        $preferences['last_updated'] = time();
        
        CookieMiddleware::set('user_preferences', $preferences, [
            'expires' => time() + (365 * 24 * 60 * 60), // 1 year
            'format' => CookieMiddleware::FORMAT_JSON,
        ]);
    }

    /**
     * Get a specific user preference value.
     */
    protected function getUserPreference(string $key, mixed $default = null): mixed
    {
        $preferences = $this->getUserPreferences();
        return $preferences[$key] ?? $default;
    }

    /**
     * Set a specific user preference value.
     */
    protected function setUserPreference(string $key, mixed $value): void
    {
        $preferences = $this->getUserPreferences();
        $preferences[$key] = $value;
        $this->setUserPreferences($preferences);
    }

    // ── Session Analytics ─────────────────────────────────────────────────────

    /**
     * Get session duration in seconds.
     */
    private function getSessionDuration(): int
    {
        $loginData = CookieMiddleware::get('last_login', []);
        $loginTime = $loginData['timestamp'] ?? time();
        return time() - $loginTime;
    }

    /**
     * Track page view in cookies for analytics.
     */
    protected function trackPageView(string $page): void
    {
        $pageViews = CookieMiddleware::get('page_views', [], [
            'format' => CookieMiddleware::FORMAT_JSON,
            'encrypt' => false,
        ]);

        if (!is_array($pageViews)) {
            $pageViews = [];
        }

        $pageViews[] = [
            'page' => $page,
            'timestamp' => time(),
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
            'referer' => $_SERVER['HTTP_REFERER'] ?? '',
        ];

        // Keep only the last 50 page views
        if (count($pageViews) > 50) {
            $pageViews = array_slice($pageViews, -50);
        }

        CookieMiddleware::set('page_views', $pageViews, [
            'expires' => time() + (30 * 24 * 60 * 60), // 30 days
            'format' => CookieMiddleware::FORMAT_JSON,
        ]);
    }

    // ── View renderer ─────────────────────────────────────────────────────────

    /**
     * Render a view template.
     *
     * @param string $view   Relative path inside views/ without .php, e.g. 'dashboard/index'
     * @param array  $data   Variables extracted into the template scope
     * @param string $title  Page title shown in <title> and nav
     */
    protected function render(string $view, array $data = [], string $title = 'Imager'): void
    {
        // Track this page view
        $this->trackPageView($view);
        
        $viewFile = BASE_PATH . '/views/' . $view . '.php';
        if (!file_exists($viewFile)) {
            throw new \RuntimeException("View not found: $viewFile");
        }

        // Make data available to the view
        extract($data, EXTR_SKIP);
        $flash  = $this->getFlash();
        $isAuth = $this->isLoggedIn();
        $userPrefs = $this->getUserPreferences(); // Make preferences available to all views

        // Capture view content
        ob_start();
        require $viewFile;
        $content = ob_get_clean();

        // Render into layout
        require BASE_PATH . '/views/layout.php';
    }
}
