<?php

declare(strict_types=1);

namespace Imager\middleware;

use Imager\Exceptions\HttpException;

/**
 * Cookie middleware with serialization/deserialization capabilities.
 * 
 * Features:
 * - Set cookies with automatic serialization of complex data
 * - Get cookies with automatic deserialization
 * - Secure cookie handling with encryption support
 * - JSON and PHP serialization options
 * - Cookie validation and sanitization
 * 
 * Usage:
 *   CookieMiddleware::set('user_prefs', ['theme' => 'dark', 'lang' => 'en']);
 *   $prefs = CookieMiddleware::get('user_prefs', []);
 *   CookieMiddleware::delete('user_prefs');
 */
final class CookieMiddleware
{
    private const DEFAULT_EXPIRES = 86400; // 24 hours
    private const DEFAULT_PATH = '/';
    private const DEFAULT_DOMAIN = '';
    private const DEFAULT_SECURE = true;
    private const DEFAULT_HTTP_ONLY = true;
    private const DEFAULT_SAME_SITE = 'Lax';
    
    // Serialization formats
    public const FORMAT_JSON = 'json';
    public const FORMAT_PHP = 'php';
    
    /**
     * Set a cookie with automatic serialization of complex data.
     * 
     * @param string $name Cookie name
     * @param mixed $value Value to serialize and store
     * @param array $options Cookie options
     * @throws HttpException 500 if serialization fails
     */
    public static function set(string $name, mixed $value, array $options = []): void
    {
        $options = array_merge([
            'expires' => time() + self::DEFAULT_EXPIRES,
            'path' => self::DEFAULT_PATH,
            'domain' => self::DEFAULT_DOMAIN,
            'secure' => self::DEFAULT_SECURE,
            'httponly' => self::DEFAULT_HTTP_ONLY,
            'samesite' => self::DEFAULT_SAME_SITE,
            'format' => self::FORMAT_JSON,
            'encrypt' => false,
        ], $options);
        
        // Serialize the value
        $serializedValue = self::serialize($value, $options['format']);
        
        // Encrypt if requested
        if ($options['encrypt']) {
            $serializedValue = self::encrypt($serializedValue);
        }
        
        // Set the cookie
        $success = setcookie(
            $name,
            $serializedValue,
            [
                'expires' => $options['expires'],
                'path' => $options['path'],
                'domain' => $options['domain'],
                'secure' => $options['secure'],
                'httponly' => $options['httponly'],
                'samesite' => $options['samesite'],
            ]
        );
        
        if (!$success) {
            throw new HttpException(500, 'COOKIE_ERROR', 'Failed to set cookie.');
        }
        
        // Also set in $_COOKIE for immediate availability
        $_COOKIE[$name] = $serializedValue;
    }
    
    /**
     * Get a cookie with automatic deserialization.
     * 
     * @param string $name Cookie name
     * @param mixed $default Default value if cookie doesn't exist
     * @param array $options Deserialization options
     * @return mixed Deserialized cookie value or default
     */
    public static function get(string $name, mixed $default = null, array $options = []): mixed
    {
        if (!isset($_COOKIE[$name])) {
            return $default;
        }
        
        $options = array_merge([
            'format' => self::FORMAT_JSON,
            'encrypt' => false,
        ], $options);
        
        $value = $_COOKIE[$name];
        
        // Decrypt if needed
        if ($options['encrypt']) {
            $value = self::decrypt($value);
            if ($value === false) {
                return $default; // Decryption failed
            }
        }
        
        // Deserialize the value
        $deserializedValue = self::deserialize($value, $options['format']);
        
        return $deserializedValue !== false ? $deserializedValue : $default;
    }
    
    /**
     * Check if a cookie exists.
     */
    public static function has(string $name): bool
    {
        return isset($_COOKIE[$name]);
    }
    
    /**
     * Delete a cookie.
     */
    public static function delete(string $name, array $options = []): void
    {
        $options = array_merge([
            'path' => self::DEFAULT_PATH,
            'domain' => self::DEFAULT_DOMAIN,
            'secure' => self::DEFAULT_SECURE,
            'httponly' => self::DEFAULT_HTTP_ONLY,
            'samesite' => self::DEFAULT_SAME_SITE,
        ], $options);
        
        setcookie(
            $name,
            '',
            [
                'expires' => time() - 3600, // 1 hour ago
                'path' => $options['path'],
                'domain' => $options['domain'],
                'secure' => $options['secure'],
                'httponly' => $options['httponly'],
                'samesite' => $options['samesite'],
            ]
        );
        
        unset($_COOKIE[$name]);
    }
    
    /**
     * Get all cookies with optional deserialization.
     * 
     * @param array $options Deserialization options
     * @return array All cookies
     */
    public static function all(array $options = []): array
    {
        $options = array_merge([
            'deserialize' => false,
            'format' => self::FORMAT_JSON,
            'encrypt' => false,
        ], $options);
        
        if (!$options['deserialize']) {
            return $_COOKIE;
        }
        
        $cookies = [];
        foreach ($_COOKIE as $name => $value) {
            $cookies[$name] = self::get($name, $value, $options);
        }
        
        return $cookies;
    }
    
    /**
     * Serialize a value based on the specified format.
     */
    private static function serialize(mixed $value, string $format): string
    {
        switch ($format) {
            case self::FORMAT_JSON:
                $result = json_encode($value, JSON_THROW_ON_ERROR);
                if ($result === false) {
                    throw new HttpException(500, 'SERIALIZATION_ERROR', 'Failed to JSON encode cookie value.');
                }
                return $result;
                
            case self::FORMAT_PHP:
                return serialize($value);
                
            default:
                throw new HttpException(500, 'INVALID_FORMAT', "Unsupported serialization format: {$format}");
        }
    }
    
    /**
     * Deserialize a value based on the specified format.
     */
    private static function deserialize(string $value, string $format): mixed
    {
        try {
            switch ($format) {
                case self::FORMAT_JSON:
                    return json_decode($value, true, 512, JSON_THROW_ON_ERROR);
                    
                case self::FORMAT_PHP:
                    return unserialize($value);
                    
                default:
                    return false;
            }
        } catch (\Exception) {
            return false; // Deserialization failed
        }
    }
    
    /**
     * Encrypt a string value.
     * Uses AES-256-GCM for authenticated encryption.
     */
    private static function encrypt(string $value): string
    {
        $key = self::getEncryptionKey();
        $iv = random_bytes(12); // 96-bit IV for GCM
        $tag = '';
        
        $encrypted = openssl_encrypt($value, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag);
        
        if ($encrypted === false) {
            throw new HttpException(500, 'ENCRYPTION_ERROR', 'Failed to encrypt cookie value.');
        }
        
        // Combine IV + tag + encrypted data and base64 encode
        return base64_encode($iv . $tag . $encrypted);
    }
    
    /**
     * Decrypt a string value.
     */
    private static function decrypt(string $value): string|false
    {
        $key = self::getEncryptionKey();
        $data = base64_decode($value);
        
        if ($data === false || strlen($data) < 28) { // 12 (IV) + 16 (tag) minimum
            return false;
        }
        
        $iv = substr($data, 0, 12);
        $tag = substr($data, 12, 16);
        $encrypted = substr($data, 28);
        
        return openssl_decrypt($encrypted, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag);
    }
    
    /**
     * Get or generate encryption key.
     */
    private static function getEncryptionKey(): string
    {
        $key = getenv('COOKIE_ENCRYPTION_KEY');
        
        if (!$key) {
            // Generate a key based on app secret or use a default (not recommended for production)
            $appSecret = getenv('APP_SECRET') ?: 'default-secret-change-me';
            $key = hash('sha256', $appSecret . 'cookie-encryption', true);
        } else {
            $key = base64_decode($key);
        }
        
        if (strlen($key) !== 32) {
            throw new HttpException(500, 'INVALID_KEY', 'Cookie encryption key must be 32 bytes (256 bits).');
        }
        
        return $key;
    }
    
    /**
     * Parse all incoming cookies and deserialize them based on a configuration.
     * Call this early in your application bootstrap.
     * 
     * @param array $cookieConfig Configuration for automatic deserialization
     * Example: ['user_prefs' => ['format' => 'json'], 'cart' => ['format' => 'php', 'encrypt' => true]]
     */
    public static function parseIncomingCookies(array $cookieConfig = []): void
    {
        foreach ($cookieConfig as $cookieName => $options) {
            if (isset($_COOKIE[$cookieName])) {
                // Store the deserialized value in a special global for easy access
                $GLOBALS['_PARSED_COOKIES'][$cookieName] = self::get($cookieName, null, $options);
            }
        }
    }
    
    /**
     * Get a parsed cookie value (after parseIncomingCookies has been called).
     */
    public static function getParsed(string $name, mixed $default = null): mixed
    {
        return $GLOBALS['_PARSED_COOKIES'][$name] ?? $default;
    }
    
    /**
     * Validate cookie name according to RFC 6265.
     */
    private static function isValidCookieName(string $name): bool
    {
        // Cookie name should not contain special characters
        return preg_match('/^[a-zA-Z0-9_-]+$/', $name) === 1;
    }
    
    /**
     * Sanitize cookie name.
     */
    public static function sanitizeName(string $name): string
    {
        return preg_replace('/[^a-zA-Z0-9_-]/', '_', $name);
    }
}