<?php

declare(strict_types=1);

namespace Imager\config;

use Aws\S3\S3Client;
use Aws\Exception\AwsException;
use Imager\Exceptions\HttpException;
use RuntimeException;

/**
 * AWS S3 client wrapper.
 *
 * Responsibilities:
 *  - Upload objects under users/{user_id}/{uuid}.{ext}
 *  - Generate presigned GET URLs (short-lived for private, long-lived for public)
 *  - Delete objects
 */
final class S3
{
    private static ?S3Client $client = null;

    private static function client(): S3Client
    {
        if (self::$client === null) {
            $key    = getenv('AWS_ACCESS_KEY_ID');
            $secret = getenv('AWS_SECRET_ACCESS_KEY');
            $region = getenv('AWS_REGION') ?: 'ap-southeast-2';

            if (!$key || !$secret) {
                throw new RuntimeException('AWS credentials are not configured.');
            }

            self::$client = new S3Client([
                'version'     => 'latest',
                'region'      => $region,
                'credentials' => [
                    'key'    => $key,
                    'secret' => $secret,
                ],
            ]);
        }

        return self::$client;
    }

    private static function bucket(): string
    {
        $bucket = getenv('S3_BUCKET_NAME');
        if (!$bucket) {
            throw new RuntimeException('S3_BUCKET_NAME is not configured.');
        }
        return $bucket;
    }

    /**
     * Upload a file to S3.
     *
     * @param  string $localPath   Absolute path of the temp file on disk.
     * @param  string $s3Key       Destination key, e.g. users/{uid}/{uuid}.jpg
     * @param  string $mimeType    MIME type for Content-Type metadata.
     * @return string              The S3 object key stored.
     * @throws HttpException 500 on S3 failure.
     */
    public static function upload(string $localPath, string $s3Key, string $mimeType): string
    {
        try {
            self::client()->putObject([
                'Bucket'      => self::bucket(),
                'Key'         => $s3Key,
                'SourceFile'  => $localPath,
                'ContentType' => $mimeType,
                // Bucket is private; ACL is omitted intentionally
            ]);
        } catch (AwsException $e) {
            throw new HttpException(500, 'INTERNAL_ERROR', 'Failed to upload image to storage.');
        }

        return $s3Key;
    }

    /**
     * Generate a presigned GET URL for the given S3 key.
     *
     * @param  string $s3Key   Object key.
     * @param  bool   $public  Use long TTL (public) or short TTL (private).
     * @return string          Presigned URL.
     */
    public static function presignedUrl(string $s3Key, bool $public): string
    {
        $ttl = $public
            ? (int) (getenv('S3_PUBLIC_URL_TTL')  ?: 604800)   // 7 days
            : (int) (getenv('S3_PRIVATE_URL_TTL') ?: 900);     // 15 minutes

        $cmd = self::client()->getCommand('GetObject', [
            'Bucket' => self::bucket(),
            'Key'    => $s3Key,
        ]);

        $request = self::client()->createPresignedRequest($cmd, "+{$ttl} seconds");

        return (string) $request->getUri();
    }

    /**
     * Delete an object from S3. Failures are swallowed with a logged warning
     * so that a storage hiccup doesn't prevent DB record deletion.
     *
     * @param  string $s3Key   Object key to delete.
     */
    public static function delete(string $s3Key): void
    {
        try {
            self::client()->deleteObject([
                'Bucket' => self::bucket(),
                'Key'    => $s3Key,
            ]);
        } catch (AwsException $e) {
            // Log but do not throw — DB deletion proceeds regardless
            error_log("[S3::delete] Failed to delete $s3Key: " . $e->getMessage());
        }
    }
}
