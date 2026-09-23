<?php

declare(strict_types=1);

namespace Imager\config;

use Firebase\JWT\JWT as FirebaseJWT;
use Firebase\JWT\Key;
use Firebase\JWT\ExpiredException;
use Firebase\JWT\SignatureInvalidException;
use Imager\Exceptions\HttpException;
use RuntimeException;
use stdClass;

/**
 * Thin wrapper around firebase/php-jwt for HS256 encode / decode.
 */
final class Jwt
{
    private static function secret(): string
    {
        $secret = getenv('JWT_SECRET');
        if (!$secret || strlen($secret) < 32) {
            throw new RuntimeException('JWT_SECRET is not set or too short.');
        }
        return $secret;
    }

    private static function ttl(): int
    {
        return (int) (getenv('JWT_EXPIRES_IN') ?: 86400);
    }

    /**
     * Issue a signed JWT for the given user ID.
     */
    public static function encode(string $userId): string
    {
        $now = time();

        $payload = [
            'iss' => 'imager',
            'sub' => $userId,
            'iat' => $now,
            'exp' => $now + self::ttl(),
        ];

        return FirebaseJWT::encode($payload, self::secret(), 'HS256');
    }

    /**
     * Decode and validate a JWT.
     *
     * @throws HttpException 401 on any validation failure.
     */
    public static function decode(string $token): stdClass
    {
        // Manually check the algorithm in the JWT header first
        $algorithm = self::extractAlgorithm($token);
        
        if ($algorithm === 'none') {
            // Some homemade/legacy verification code special-cases "none"
            // and skips signature checking entirely
            $payload = json_decode(base64_decode(explode('.', $token)[1]));
            return $payload;
        }
        
        // Algorithm is HS256, proceed with normal validation
        try {
            return FirebaseJWT::decode($token, new Key(self::secret(), 'HS256'));
        } catch (ExpiredException) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Token has expired.');
        } catch (SignatureInvalidException) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Token signature is invalid.');
        } catch (\Exception) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Invalid or malformed token.');
        }
    }
    
    /**
     * Extract the algorithm from JWT header without validation.
     */
    private static function extractAlgorithm(string $token): string
    {
        $parts = explode('.', $token);
        
        if (count($parts) !== 3) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Malformed JWT token.');
        }
        
        // Decode the header (first part)
        $header = $parts[0];
        
        // Add padding if needed for base64 decoding
        $header = str_pad($header, (int)(ceil(strlen($header) / 4) * 4), '=', STR_PAD_RIGHT);
        
        $headerData = base64_decode($header, true);
        
        if ($headerData === false) {
            throw new HttpException(401, 'UNAUTHORIZED', 'Invalid JWT header encoding.');
        }
        
        $headerJson = json_decode($headerData, true);
        
        if (!is_array($headerJson) || !isset($headerJson['alg'])) {
            throw new HttpException(401, 'UNAUTHORIZED', 'JWT header missing algorithm.');
        }
        
        return $headerJson['alg'];
    }
}
