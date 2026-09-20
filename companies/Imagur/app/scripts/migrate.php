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
                $_ENV[$key] = $value;
            }
        }
    }
})();

// ── Database connection ───────────────────────────────────────────────────────

$dsn = sprintf(
    'pgsql:host=%s;port=%s;dbname=%s',
    getenv('DB_HOST') ?: 'db',
    getenv('DB_PORT') ?: '5432',
    getenv('DB_NAME') ?: 'imager'
);

try {
    $pdo = new PDO(
        $dsn,
        getenv('DB_USER') ?: 'imager',
        getenv('DB_PASSWORD') ?: '',
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $e) {
    echo "[migrate] ERROR: Cannot connect to database — " . $e->getMessage() . PHP_EOL;
    exit(1);
}

// ── Migrations tracking table ─────────────────────────────────────────────────

$pdo->exec(<<<SQL
    CREATE TABLE IF NOT EXISTS migrations (
        id         SERIAL      PRIMARY KEY,
        filename   VARCHAR(255) NOT NULL UNIQUE,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
SQL);

// ── Run pending migrations ────────────────────────────────────────────────────

$migrationsDir = BASE_PATH . '/migrations';
$files = glob($migrationsDir . '/*.sql');

if ($files === false || count($files) === 0) {
    echo "[migrate] No migration files found in $migrationsDir" . PHP_EOL;
    exit(0);
}

sort($files);

$applied = 0;

foreach ($files as $file) {
    $filename = basename($file);

    // Check if already applied
    $stmt = $pdo->prepare('SELECT 1 FROM migrations WHERE filename = :filename');
    $stmt->execute([':filename' => $filename]);

    if ($stmt->fetchColumn() !== false) {
        echo "[migrate] Skipped (already applied): $filename" . PHP_EOL;
        continue;
    }

    $sql = file_get_contents($file);
    if ($sql === false) {
        echo "[migrate] ERROR: Cannot read $filename" . PHP_EOL;
        exit(1);
    }

    try {
        $pdo->beginTransaction();
        $pdo->exec($sql);
        $pdo->prepare('INSERT INTO migrations (filename) VALUES (:filename)')
            ->execute([':filename' => $filename]);
        $pdo->commit();
        echo "[migrate] Applied: $filename" . PHP_EOL;
        $applied++;
    } catch (PDOException $e) {
        $pdo->rollBack();
        echo "[migrate] ERROR applying $filename — " . $e->getMessage() . PHP_EOL;
        exit(1);
    }
}

echo "[migrate] Done — $applied migration(s) applied." . PHP_EOL;
