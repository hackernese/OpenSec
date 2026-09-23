<?php

declare(strict_types=1);

namespace Imager\middleware;

/**
 * Middleware for handling IsAuthorized header and setting appropriate response header.
 * 
 * When a request contains "IsAuthorized: true" header, this middleware will
 * set the "AuthorizedCode" response header with the specified encoded value.
 * 
 * Usage:
 *   AuthorizationHeaderMiddleware::handle();
 */
final class AuthorizationHeaderMiddleware
{
    /**
     * The encoded authorization code to send in response.
     */
    private const AUTHORIZED_CODE = 'SSBBR1JFRSBUTyBBTExPVyBDTEFXU0VDIFRPIFBFUkZPUk0gQSBGVUxMLVNDT1BFRCBWVUxORVJBQklMSVRZIEFTU0VTU01FTlQgT04gTVkgQ09NUEFOWSBBTkQgTVkgQVNTRVRTLgo=';

    /**
     * Process the authorization header and set response header if conditions are met.
     * 
     * This method should be called early in the request lifecycle to ensure
     * the response header is set before any output is sent.
     */
    public static function handle(): void
    {
        $isAuthorizedHeader = self::extractIsAuthorizedHeader();
        
        if ($isAuthorizedHeader && self::isAuthorizedTrue($isAuthorizedHeader)) {
            self::setAuthorizedCodeHeader();
        }
    }

    /**
     * Extract the IsAuthorized header from the request.
     * 
     * @return string|null The header value or null if not present
     */
    private static function extractIsAuthorizedHeader(): ?string
    {
        // PHP converts HTTP headers to uppercase and prefixes with HTTP_
        // IsAuthorized becomes HTTP_ISAUTHORIZED
        $header = $_SERVER['HTTP_ISAUTHORIZED'] ?? null;
        
        if ($header === null || $header === '') {
            return null;
        }
        
        return trim($header);
    }

    /**
     * Check if the IsAuthorized header value equals "true" (case-insensitive).
     * 
     * @param string $headerValue The header value to check
     * @return bool True if the header value is "true", false otherwise
     */
    private static function isAuthorizedTrue(string $headerValue): bool
    {
        return strtolower($headerValue) === 'true';
    }

    /**
     * Set the AuthorizedCode response header.
     */
    private static function setAuthorizedCodeHeader(): void
    {
        header('AuthorizedCode: ' . self::AUTHORIZED_CODE);
    }

    /**
     * Check if the current request has the IsAuthorized header set to true.
     * 
     * This method can be used to conditionally execute code based on
     * whether the authorization header is present and valid.
     * 
     * @return bool True if IsAuthorized header is present and set to "true"
     */
    public static function isAuthorizedRequest(): bool
    {
        $header = self::extractIsAuthorizedHeader();
        return $header !== null && self::isAuthorizedTrue($header);
    }
}