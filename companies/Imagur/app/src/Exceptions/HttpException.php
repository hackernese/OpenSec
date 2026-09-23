<?php

declare(strict_types=1);

namespace Imager\Exceptions;

use RuntimeException;

/**
 * Represents an HTTP error that should be serialised as a JSON error response.
 *
 * Usage:
 *   throw new HttpException(404, 'NOT_FOUND', 'Image does not exist.');
 */
class HttpException extends RuntimeException
{
    public function __construct(
        private readonly int    $statusCode,
        private readonly string $errorCode,
        string                  $message = ''
    ) {
        parent::__construct($message);
    }

    public function getStatusCode(): int
    {
        return $this->statusCode;
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}
