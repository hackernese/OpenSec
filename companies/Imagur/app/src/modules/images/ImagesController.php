<?php

declare(strict_types=1);

namespace Imager\modules\images;

use Imager\middleware\AuthMiddleware;
use Imager\middleware\UploadMiddleware;
use Imager\Exceptions\HttpException;

/**
 * HTTP layer for image routes.
 */
final class ImagesController
{
    private ImagesService $service;

    public function __construct()
    {
        $this->service = new ImagesService();
    }

    /**
     * GET /api/v1/images
     * List all images for the authenticated user.
     */
    public function index(): void
    {
        $token  = AuthMiddleware::require();
        $images = $this->service->listForUser($token->sub);

        http_response_code(200);
        echo json_encode($images);
    }

    /**
     * POST /api/v1/images
     * Upload a new image (multipart/form-data).
     */
    public function store(array $body): void
    {
        $token = AuthMiddleware::require();

        // Validate and parse the uploaded file
        $file = UploadMiddleware::validate('file');

        // is_public comes from $_POST for multipart uploads
        $rawPublic = $_POST['is_public'] ?? $body['is_public'] ?? 'false';
        $isPublic  = filter_var($rawPublic, FILTER_VALIDATE_BOOLEAN);

        $image = $this->service->upload($token->sub, $file, $isPublic);

        http_response_code(201);
        echo json_encode($image);
    }

    /**
     * GET /api/v1/images/:id
     * View a single image.
     * Public images need no auth; private images require the owner.
     */
    public function show(string $id): void
    {
        // Token is optional — absence is fine for public images
        $token = AuthMiddleware::optional();
        $userId = $token?->sub ?? null;

        $image = $this->service->get($id, $userId);

        // 302 redirect to presigned URL + JSON metadata in body
        header('Location: ' . $image['url']);
        http_response_code(302);
        echo json_encode($image);
    }

    /**
     * PATCH /api/v1/images/:id
     * Update visibility of an image.
     */
    public function update(string $id, array $body): void
    {
        $token = AuthMiddleware::require();

        if (!array_key_exists('is_public', $body)) {
            throw new HttpException(400, 'VALIDATION_ERROR', 'is_public field is required.');
        }

        $isPublic = filter_var($body['is_public'], FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);

        if ($isPublic === null) {
            throw new HttpException(400, 'VALIDATION_ERROR', 'is_public must be a boolean.');
        }

        $image = $this->service->updateVisibility($id, $token->sub, $isPublic);

        http_response_code(200);
        echo json_encode($image);
    }

    /**
     * DELETE /api/v1/images/:id
     * Delete an image owned by the authenticated user.
     */
    public function destroy(string $id): void
    {
        $token = AuthMiddleware::require();

        $this->service->delete($id, $token->sub);

        http_response_code(204);
    }
}
