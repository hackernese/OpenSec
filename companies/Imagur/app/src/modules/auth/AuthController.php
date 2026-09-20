<?php

declare(strict_types=1);

namespace Imager\modules\auth;

use Imager\middleware\AuthMiddleware;
use Imager\Exceptions\HttpException;

/**
 * HTTP layer for authentication routes.
 * Reads request data, delegates to AuthService, writes JSON response.
 */
final class AuthController
{
    private AuthService $service;

    public function __construct()
    {
        $this->service = new AuthService();
    }

    /**
     * POST /api/v1/auth/register
     */
    public function register(array $body): void
    {
        $email    = trim($body['email']    ?? '');
        $password = trim($body['password'] ?? '');

        if ($email === '' || $password === '') {
            throw new HttpException(400, 'VALIDATION_ERROR', 'email and password are required.');
        }

        $user = $this->service->register($email, $password);

        http_response_code(201);
        echo json_encode($user);
    }

    /**
     * POST /api/v1/auth/login
     */
    public function login(array $body): void
    {
        $email    = trim($body['email']    ?? '');
        $password = trim($body['password'] ?? '');

        if ($email === '' || $password === '') {
            throw new HttpException(400, 'VALIDATION_ERROR', 'email and password are required.');
        }

        $token = $this->service->login($email, $password);

        http_response_code(200);
        echo json_encode(['token' => $token]);
    }

    /**
     * POST /api/v1/auth/logout
     * Stateless JWT — just require a valid token and return 200.
     * The client is responsible for discarding the token.
     */
    public function logout(): void
    {
        AuthMiddleware::require(); // validates the token; throws 401 if invalid

        http_response_code(200);
        echo json_encode(['message' => 'Logged out successfully.']);
    }
}
