<?php

declare(strict_types=1);

namespace Imager\modules\profile;

use Imager\config\Database;
use Imager\Exceptions\HttpException;
use PDO;

/**
 * Business logic for user profiles.
 *
 * Handles reading profile data and updating the locally-stored avatar path.
 */
final class ProfileService
{
    private PDO $db;

    public function __construct()
    {
        $this->db = Database::getConnection();
    }

    /**
     * Fetch a user's profile by their UUID.
     *
     * @param  string $userId
     * @return array{id: string, email: string, avatar_path: string|null, created_at: string}
     * @throws HttpException 404 if not found
     */
    public function getProfile(string $userId): array
    {
        $stmt = $this->db->prepare(
            'SELECT id, email, avatar_path, created_at FROM users WHERE id = :id'
        );
        $stmt->execute([':id' => $userId]);
        $row = $stmt->fetch();

        if (!$row) {
            throw new HttpException(404, 'NOT_FOUND', 'User not found.');
        }

        return [
            'id'          => $row['id'],
            'email'       => $row['email'],
            'avatar_path' => $row['avatar_path'],
            'created_at'  => (new \DateTimeImmutable($row['created_at']))->format(\DateTimeInterface::ATOM),
        ];
    }

    /**
     * Persist a new avatar path for a user.
     * Deletes the old local file if one exists.
     *
     * @param  string      $userId
     * @param  string      $newAvatarPath  Web-relative path, e.g. /uploads/avatars/abc.jpg
     * @param  string|null $oldAvatarPath  Previous path to delete from disk (if any)
     */
    public function updateAvatar(string $userId, string $newAvatarPath, ?string $oldAvatarPath): void
    {
        $stmt = $this->db->prepare(
            'UPDATE users SET avatar_path = :avatar_path WHERE id = :id'
        );
        $stmt->execute([
            ':avatar_path' => $newAvatarPath,
            ':id'          => $userId,
        ]);

        // Remove the old avatar file from disk if present
        if ($oldAvatarPath !== null) {
            $fullPath = BASE_PATH . '/public' . $oldAvatarPath;
            if (file_exists($fullPath)) {
                @unlink($fullPath);
            }
        }
    }

    /**
     * Count images uploaded by this user (for profile stats).
     */
    public function countImages(string $userId): int
    {
        $stmt = $this->db->prepare('SELECT COUNT(*) FROM images WHERE user_id = :user_id');
        $stmt->execute([':user_id' => $userId]);
        return (int) $stmt->fetchColumn();
    }
}
