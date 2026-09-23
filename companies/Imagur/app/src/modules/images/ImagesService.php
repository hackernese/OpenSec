<?php

declare(strict_types=1);

namespace Imager\modules\images;

use Imager\config\Database;
use Imager\config\S3;
use Imager\Exceptions\HttpException;
use PDO;

/**
 * Business logic for image management.
 *
 * All operations are scoped to the authenticated user. Ownership is
 * validated on every private read, update, and delete.
 */
final class ImagesService
{
    private PDO $db;

    public function __construct()
    {
        $this->db = Database::getConnection();
    }

    /**
     * List all images owned by $userId.
     *
     * @return array<int, array>
     */
    public function listForUser(string $userId): array
    {
        $stmt = $this->db->prepare(
            'SELECT id, filename, mime_type, file_size, s3_key, is_public, uploaded_at
             FROM images
             WHERE user_id = :user_id
             ORDER BY uploaded_at DESC'
        );
        $stmt->execute([':user_id' => $userId]);
        $rows = $stmt->fetchAll();

        return array_map(fn($row) => $this->formatRow($row), $rows);
    }

    /**
     * Upload a new image for $userId.
     *
     * @param  string $userId
     * @param  array{tmp_path: string, filename: string, mime_type: string, file_size: int} $file
     * @param  bool   $isPublic
     * @return array
     */
    public function upload(string $userId, array $file, bool $isPublic): array
    {
        // Derive extension from MIME type
        $ext = $this->extensionFromMime($file['mime_type']);

        $imageId = $this->generateUuid();
        $s3Key   = "users/{$userId}/{$imageId}.{$ext}";

        // Upload to S3
        S3::upload($file['tmp_path'], $s3Key, $file['mime_type']);

        // Persist metadata
        $stmt = $this->db->prepare(
            'INSERT INTO images (id, user_id, filename, mime_type, file_size, s3_key, is_public)
             VALUES (:id, :user_id, :filename, :mime_type, :file_size, :s3_key, :is_public)
             RETURNING id, filename, mime_type, file_size, s3_key, is_public, uploaded_at'
        );
        $stmt->execute([
            ':id'        => $imageId,
            ':user_id'   => $userId,
            ':filename'  => $file['filename'],
            ':mime_type' => $file['mime_type'],
            ':file_size' => $file['file_size'],
            ':s3_key'    => $s3Key,
            ':is_public' => $isPublic ? 'true' : 'false',
        ]);

        $row = $stmt->fetch();

        return $this->formatRow($row);
    }

    /**
     * Get a single image.
     *
     * Public images are accessible to anyone.
     * Private images require the requesting user to be the owner.
     *
     * @param  string      $imageId
     * @param  string|null $requestingUserId  Null for unauthenticated requests.
     * @return array
     * @throws HttpException 404 / 403
     */
    public function get(string $imageId, ?string $requestingUserId): array
    {
        $stmt = $this->db->prepare(
            'SELECT id, user_id, filename, mime_type, file_size, s3_key, is_public, uploaded_at
             FROM images WHERE id = :id'
        );
        $stmt->execute([':id' => $imageId]);
        $row = $stmt->fetch();

        if (!$row) {
            throw new HttpException(404, 'NOT_FOUND', 'Image not found.');
        }

        if (!$row['is_public']) {
            if ($requestingUserId === null || $requestingUserId !== $row['user_id']) {
                throw new HttpException(403, 'FORBIDDEN', 'You do not have access to this image.');
            }
        }

        return $this->formatRow($row);
    }

    /**
     * Update the visibility of an image.
     *
     * @param  string $imageId
     * @param  string $userId   Must be the owner.
     * @param  bool   $isPublic
     * @return array
     * @throws HttpException 404 / 403
     */
    public function updateVisibility(string $imageId, string $userId, bool $isPublic): array
    {
        $row = $this->requireOwned($imageId, $userId);

        $stmt = $this->db->prepare(
            'UPDATE images SET is_public = :is_public WHERE id = :id
             RETURNING id, filename, mime_type, file_size, s3_key, is_public, uploaded_at'
        );
        $stmt->execute([
            ':is_public' => $isPublic ? 'true' : 'false',
            ':id'        => $imageId,
        ]);

        return $this->formatRow($stmt->fetch());
    }

    /**
     * Delete an image — removes from S3 then from the database.
     *
     * @param  string $imageId
     * @param  string $userId   Must be the owner.
     * @throws HttpException 404 / 403
     */
    public function delete(string $imageId, string $userId): void
    {
        $row = $this->requireOwned($imageId, $userId);

        // Delete from S3 first; failure is logged but does not abort DB deletion
        S3::delete($row['s3_key']);

        $stmt = $this->db->prepare('DELETE FROM images WHERE id = :id');
        $stmt->execute([':id' => $imageId]);
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    /**
     * Fetch an image row and assert it belongs to $userId.
     *
     * @throws HttpException 404 / 403
     */
    private function requireOwned(string $imageId, string $userId): array
    {
        $stmt = $this->db->prepare(
            'SELECT id, user_id, filename, mime_type, file_size, s3_key, is_public, uploaded_at
             FROM images WHERE id = :id'
        );
        $stmt->execute([':id' => $imageId]);
        $row = $stmt->fetch();

        if (!$row) {
            throw new HttpException(404, 'NOT_FOUND', 'Image not found.');
        }

        if ($row['user_id'] !== $userId) {
            throw new HttpException(403, 'FORBIDDEN', 'You do not own this image.');
        }

        return $row;
    }

    /**
     * Format a raw DB row into the API response shape, including a presigned URL.
     */
    private function formatRow(array $row): array
    {
        $isPublic = (bool) $row['is_public'];

        return [
            'id'          => $row['id'],
            'filename'    => $row['filename'],
            'mime_type'   => $row['mime_type'],
            'file_size'   => (int) $row['file_size'],
            'is_public'   => $isPublic,
            'url'         => S3::presignedUrl($row['s3_key'], $isPublic),
            'uploaded_at' => (new \DateTimeImmutable($row['uploaded_at']))->format(\DateTimeInterface::ATOM),
        ];
    }

    private function extensionFromMime(string $mime): string
    {
        return match ($mime) {
            'image/jpeg' => 'jpg',
            'image/png'  => 'png',
            'image/gif'  => 'gif',
            'image/webp' => 'webp',
            default      => 'bin',
        };
    }

    private function generateUuid(): string
    {
        // RFC 4122 v4 UUID
        $data    = random_bytes(16);
        $data[6] = chr(ord($data[6]) & 0x0f | 0x40);
        $data[8] = chr(ord($data[8]) & 0x3f | 0x80);

        return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
    }
}
