<?php

declare(strict_types=1);

namespace Imager\UI;

use Imager\config\Jwt;
use Imager\modules\profile\ProfileService;
use Imager\Exceptions\HttpException;

final class ProfileUiController extends BaseController
{
    private ProfileService $service;

    public function __construct()
    {
        parent::__construct();
        $this->service = new ProfileService();
    }

    // ── GET /profile ──────────────────────────────────────────────────────────

    public function show(): void
    {
        $this->requireLogin();

        $userId  = Jwt::decode($this->getToken())->sub;
        $user    = $this->service->getProfile($userId);
        $total   = $this->service->countImages($userId);

        $this->render('profile/show', [
            'user'  => $user,
            'total' => $total,
        ], 'My Profile');
    }

    // ── POST /profile/avatar ──────────────────────────────────────────────────

    public function uploadAvatar(): void
    {
        $this->requireLogin();

        $userId = Jwt::decode($this->getToken())->sub;

        // Validate file (reuse the existing middleware — finfo magic-byte check)
        if (empty($_FILES['avatar']) || $_FILES['avatar']['error'] === UPLOAD_ERR_NO_FILE) {
            $this->flash('error', 'Please choose an image file to upload.');
            $this->redirect('/profile');
        }

        try {
            $file = $this->validateAvatarFile();
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
            $this->redirect('/profile');
        }

        // Build destination path
        $ext     = $this->extFromMime($file['mime_type']);
        $name    = $userId . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
        $destDir = BASE_PATH . '/public/uploads/avatars';
        $destAbs = $destDir . '/' . $name;
        $webPath = '/uploads/avatars/' . $name;

        if (!is_dir($destDir)) {
            mkdir($destDir, 0755, true);
        }

        if (!move_uploaded_file($file['tmp_path'], $destAbs)) {
            $this->flash('error', 'Failed to save the image. Please try again.');
            $this->redirect('/profile');
        }

        // Fetch old avatar so we can clean it up after the DB update
        try {
            $profile   = $this->service->getProfile($userId);
            $oldAvatar = $profile['avatar_path'];
        } catch (HttpException) {
            $oldAvatar = null;
        }

        $this->service->updateAvatar($userId, $webPath, $oldAvatar);

        $this->flash('success', 'Profile picture updated.');
        $this->redirect('/profile');
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private const ALLOWED_MIME = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
    ];

    /**
     * Validate the uploaded avatar file without using UploadMiddleware's
     * hardcoded field name, keeping this self-contained.
     *
     * @throws HttpException
     */
    private function validateAvatarFile(): array
    {
        $file = $_FILES['avatar'];

        if ($file['error'] !== UPLOAD_ERR_OK) {
            $msg = match ($file['error']) {
                UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE => 'The file exceeds the allowed size limit.',
                UPLOAD_ERR_PARTIAL                        => 'The file was only partially uploaded.',
                default                                   => 'Upload failed.',
            };
            throw new HttpException(400, 'VALIDATION_ERROR', $msg);
        }

        $maxBytes = (int) (getenv('MAX_UPLOAD_SIZE_MB') ?: 10) * 1024 * 1024;
        if ($file['size'] > $maxBytes) {
            throw new HttpException(413, 'FILE_TOO_LARGE', 'File exceeds the 10 MB limit.');
        }

        $finfo    = new \finfo(FILEINFO_MIME_TYPE);
        $mimeType = $finfo->file($file['tmp_name']);

        if (!$mimeType || !in_array($mimeType, self::ALLOWED_MIME, true)) {
            throw new HttpException(415, 'UNSUPPORTED_MEDIA_TYPE',
                'Only JPEG, PNG, GIF and WebP images are allowed.');
        }

        return [
            'tmp_path'  => $file['tmp_name'],
            'mime_type' => $mimeType,
        ];
    }

    private function extFromMime(string $mime): string
    {
        return match ($mime) {
            'image/jpeg' => 'jpg',
            'image/png'  => 'png',
            'image/gif'  => 'gif',
            'image/webp' => 'webp',
            default      => 'jpg',
        };
    }
}
