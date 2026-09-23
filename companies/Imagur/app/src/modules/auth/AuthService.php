<?php

declare(strict_types=1);

namespace Imager\modules\auth;

use Imager\config\Database;
use Imager\config\Jwt;
use Imager\Exceptions\HttpException;
use PDO;

/**
 * Business logic for authentication.
 */
final class AuthService
{
    private PDO $db;

    public function __construct()
    {
        $this->db = Database::getConnection();
    }

    /**
     * Register a new user.
     *
     * @param  string $email
     * @param  string $password  Plain-text password (will be hashed here).
     * @return array{id: string, email: string, created_at: string}
     * @throws HttpException 400 on validation, 409 on duplicate email.
     */
    public function register(string $email, string $password): array
    {
        // Basic validation
        $email = strtolower(trim($email));

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new HttpException(400, 'VALIDATION_ERROR', 'A valid email address is required.');
        }

        if (strlen($password) < 8) {
            throw new HttpException(400, 'VALIDATION_ERROR', 'Password must be at least 8 characters.');
        }

        // Uniqueness check
        $stmt = $this->db->prepare('SELECT id FROM users WHERE email = :email');
        $stmt->execute([':email' => $email]);
        if ($stmt->fetch()) {
            throw new HttpException(409, 'VALIDATION_ERROR', 'An account with that email already exists.');
        }

        // Hash password — bcrypt cost 12
        $hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);

        // Insert
        $stmt = $this->db->prepare(
            'INSERT INTO users (email, password) VALUES (:email, :password)
             RETURNING id, email, created_at'
        );
        $stmt->execute([':email' => $email, ':password' => $hash]);
        $row = $stmt->fetch();

        return [
            'id'         => $row['id'],
            'email'      => $row['email'],
            'created_at' => (new \DateTimeImmutable($row['created_at']))->format(\DateTimeInterface::ATOM),
        ];
    }

    /**
     * Authenticate a user and return a signed JWT.
     *
     * @param  string $email
     * @param  string $password  Plain-text password.
     * @return string            Signed JWT.
     * @throws HttpException 400 on missing fields, 401 on bad credentials.
     */
    public function login(string $email, string $password): string
    {
        $email = strtolower(trim($email));

        if ($email === '' || $password === '') {
            throw new HttpException(400, 'VALIDATION_ERROR', 'Email and password are required.');
        }

        $stmt = $this->db->prepare('SELECT id, password FROM users WHERE email = :email');
        $stmt->execute([':email' => $email]);
        $user = $stmt->fetch();

        // Constant-time comparison — always verify even when user not found
        $hash = $user['password'] ?? '$2y$12$invalidhashpaddingtoensureconstanttimexxx';
        if (!$user || !password_verify($password, $hash)) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Invalid email or password.');
        }

        return Jwt::encode($user['id']);
    }
}
