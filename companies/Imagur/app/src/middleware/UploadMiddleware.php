<?php

declare(strict_types=1);

namespace Imager\middleware;

use Imager\Exceptions\HttpException;

/**
 * Validates an uploaded image file from $_FILES.
 *
 * Checks:
 *  - File was actually uploaded (no PHP upload error)
 *  - File size within MAX_UPLOAD_SIZE_MB (default 10 MB)
 *  - MIME type is in the allowed set, verified via finfo (magic bytes — not
 *    the client-reported Content-Type)
 *
 * Returns a normalised array on success:
 * [
 *   'tmp_path'  => string,   // path to temp file
 *   'filename'  => string,   // original filename (sanitised)
 *   'mime_type' => string,   // verified MIME type
 *   'file_size' => int,      // bytes
 * ]
 */
final class UploadMiddleware
{
    private const ALLOWED_MIME_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
    ];

    /**
     * @param  string $field  The $_FILES field name (default: 'file').
     * @return array{tmp_path: string, filename: string, mime_type: string, file_size: int}
     * @throws HttpException 400 / 413 / 415
     */
    public static function validate(string $field = 'file'): array
    {
        if (empty($_FILES[$field])) {
            throw new HttpException(400, 'VALIDATION_ERROR', 'No file was uploaded.');
        }

        $file = $_FILES[$field];

        // Check for PHP-level upload errors
        if ($file['error'] !== UPLOAD_ERR_OK) {
            $message = match ($file['error']) {
                UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE => 'The uploaded file exceeds the allowed size limit.',
                UPLOAD_ERR_PARTIAL                        => 'The file was only partially uploaded.',
                UPLOAD_ERR_NO_FILE                        => 'No file was sent.',
                default                                   => 'File upload failed.',
            };

            $code = in_array($file['error'], [UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE], true)
                ? 413
                : 400;

            throw new HttpException($code, $code === 413 ? 'FILE_TOO_LARGE' : 'VALIDATION_ERROR', $message);
        }

        // Size check
        $maxBytes = (int) (getenv('MAX_UPLOAD_SIZE_MB') ?: 10) * 1024 * 1024;
        if ($file['size'] > $maxBytes) {
            throw new HttpException(413, 'FILE_TOO_LARGE', sprintf(
                'File size %d bytes exceeds the maximum allowed %d bytes.',
                $file['size'],
                $maxBytes
            ));
        }

        // MIME check via magic bytes (finfo)
        $finfo    = new \finfo(FILEINFO_MIME_TYPE);
        $mimeType = $finfo->file($file['tmp_name']);

        if ($mimeType === false || !in_array($mimeType, self::ALLOWED_MIME_TYPES, true)) {
            throw new HttpException(415, 'UNSUPPORTED_MEDIA_TYPE', sprintf(
                'File type "%s" is not allowed. Accepted types: %s.',
                $mimeType ?: 'unknown',
                implode(', ', self::ALLOWED_MIME_TYPES)
            ));
        }

        // Sanitise original filename — strip directory traversal, keep extension
        $originalName = basename($file['name']);

        return [
            'tmp_path'  => $file['tmp_name'],
            'filename'  => $originalName,
            'mime_type' => $mimeType,
            'file_size' => (int) $file['size'],
        ];
    }
}
