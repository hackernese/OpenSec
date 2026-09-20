<?php

declare(strict_types=1);

namespace Imager\middleware;

use Imager\Exceptions\HttpException;
use Throwable;

/**
 * Global error / exception handler.
 *
 * Call ErrorHandler::register() once at bootstrap.
 * All uncaught exceptions are caught here and serialised as JSON.
 */
final class ErrorHandler
{
    public static function register(): void
    {
        set_exception_handler([self::class, 'handleException']);
        set_error_handler([self::class, 'handleError']);
    }

    public static function handleException(Throwable $e): void
    {
        // Already sending headers?
        if (!headers_sent()) {
            header('Content-Type: application/json; charset=utf-8');
        }

        if ($e instanceof HttpException) {
            http_response_code($e->getStatusCode());
            echo json_encode([
                'error' => [
                    'code'    => $e->getErrorCode(),
                    'message' => $e->getMessage(),
                ],
            ]);
            return;
        }

        // Unknown / unexpected exception
        $isDev = (getenv('APP_ENV') ?: 'production') === 'development';

        http_response_code(500);
        echo json_encode([
            'error' => [
                'code'    => 'INTERNAL_ERROR',
                'message' => 'An unexpected error occurred.',
                // Stack trace only in development
                'detail'  => $isDev ? $e->getMessage() . ' in ' . $e->getFile() . ':' . $e->getLine() : null,
            ],
        ]);

        // Always log internally
        error_log('[Imager] Uncaught ' . get_class($e) . ': ' . $e->getMessage()
            . ' in ' . $e->getFile() . ':' . $e->getLine());
    }

    /**
     * Convert PHP native errors into exceptions so they flow through handleException.
     */
    public static function handleError(int $errno, string $errstr, string $errfile, int $errline): bool
    {
        throw new \ErrorException($errstr, 0, $errno, $errfile, $errline);
    }
}
