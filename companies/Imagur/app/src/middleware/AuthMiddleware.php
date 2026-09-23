<?php

declare(strict_types=1);

namespace Imager\middleware;

use Imager\config\Jwt;
use Imager\Exceptions\HttpException;
use stdClass;

/**
 * Extracts and validates the Bearer JWT from the Authorization header.
 *
 * Usage:
 *   $user = AuthMiddleware::require();   // throws 401 if missing/invalid
 *   $user = AuthMiddleware::optional();  // returns null if no token present
 *
 * $user is the decoded JWT payload (stdClass) with at least ->sub (user UUID).
 */
final class AuthMiddleware
{
    /**
     * Require a valid Bearer token. Throws HttpException 401 if absent or invalid.
     */
    public static function require(): stdClass
    {
        $token = self::extractToken();

        if ($token === null) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Authentication token is required.');
        }

        return Jwt::decode($token);
    }

    /**
     * Optionally parse a Bearer token. Returns null if no Authorization header is present.
     * Still throws 401 if a token is present but malformed/expired.
     */
    public static function optional(): ?stdClass
    {
        $token = self::extractToken();

        if ($token === null) {
            return null;
        }

        return Jwt::decode($token);
    }

    private static function extractToken(): ?string
    {
        $header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';

        if ($header === '') {
            return null;
        }

        if (str_starts_with($header, 'Bearer ')) {
            return substr($header, 7);
        }

        return null;
    }
}
