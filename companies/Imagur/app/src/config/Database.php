<?php

declare(strict_types=1);

namespace Imager\config;

use PDO;
use PDOException;
use RuntimeException;

/**
 * PDO PostgreSQL singleton.
 * Call Database::getConnection() anywhere to get the shared PDO instance.
 */
final class Database
{
    private static ?PDO $instance = null;

    private function __construct() {}

    public static function getConnection(): PDO
    {
        if (self::$instance === null) {
            $host   = getenv('DB_HOST')     ?: 'db';
            $port   = getenv('DB_PORT')     ?: '5432';
            $dbname = getenv('DB_NAME')     ?: 'imager';
            $user   = getenv('DB_USER')     ?: 'imager';
            $pass   = getenv('DB_PASSWORD') ?: '';

            $dsn = "pgsql:host=$host;port=$port;dbname=$dbname";

            try {
                self::$instance = new PDO($dsn, $user, $pass, [
                    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES   => false,
                ]);
            } catch (PDOException $e) {
                // Never expose credentials in the message
                throw new RuntimeException('Database connection failed: ' . $e->getMessage());
            }
        }

        return self::$instance;
    }
}
