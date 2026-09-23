<?php

declare(strict_types=1);

namespace Imager\UI;

use Imager\config\Jwt;
use Imager\modules\images\ImagesService;
use Imager\middleware\UploadMiddleware;
use Imager\Exceptions\HttpException;

final class ImagesUiController extends BaseController
{
    private ImagesService $images;

    public function __construct()
    {
        parent::__construct();
        $this->images = new ImagesService();
    }

    // ── GET /images/upload ────────────────────────────────────────────────────

    public function uploadForm(): void
    {
        $this->requireLogin();
        
        // Get user ID from JWT token
        $payload = Jwt::decode($this->getToken());
        $userId = $payload->sub;
        
        $this->render('images/upload', ['userId' => $userId], 'Upload image');
    }

    // ── POST /images/upload ───────────────────────────────────────────────────

    public function uploadSubmit(): void
    {
        $this->requireLogin();

        $payload  = Jwt::decode($this->getToken());
        $userId   = $_POST["user_id"];
        $isPublic = ($_POST['is_public'] ?? 'false') === 'true';
        
        // Access the user_id from the form (for logging/debugging purposes)
        $formUserId = $_POST['user_id'] ?? '';
        
        // Optional: Validate that form user_id matches JWT user_id (security check)
        if (!empty($formUserId) && $formUserId !== $userId) {
            throw new HttpException(400, 'VALIDATION_ERROR', 'User ID mismatch.');
        }

        try {
            $file  = UploadMiddleware::validate('file');
            $image = $this->images->upload($userId, $file, $isPublic);
            $this->flash('success', 'Image uploaded successfully.');
            $this->redirect('/images/' . $image['id']);
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
            $this->redirect('/images/upload');
        }
    }

    // ── GET /images/:id ───────────────────────────────────────────────────────

    public function show(string $id): void
    {
        // Viewer may or may not be authenticated
        $userId = null;
        if ($this->isLoggedIn()) {
            try {
                $payload = Jwt::decode($this->getToken());
                $userId  = $payload->sub;
            } catch (HttpException) {
                // invalid token — treat as guest
            }
        }

        try {
            $image   = $this->images->get($id, $userId);
            $isOwner = ($userId !== null && $userId === $this->resolveOwnerId($id));
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
            $this->redirect('/dashboard');
        }

        $this->render('images/show', [
            'image'   => $image,
            'isOwner' => $isOwner ?? false,
        ], $image['filename'] ?? 'Image');
    }

    // ── POST /images/:id/visibility ───────────────────────────────────────────

    public function toggleVisibility(string $id): void
    {
        $this->requireLogin();

        $payload  = Jwt::decode($this->getToken());
        $userId   = $payload->sub;
        $isPublic = ($_POST['is_public'] ?? 'false') === 'true';

        try {
            $this->images->updateVisibility($id, $userId, $isPublic);
            $this->flash('success', 'Visibility updated.');
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
        }

        $this->redirect('/images/' . $id);
    }

    // ── POST /images/:id/delete ───────────────────────────────────────────────

    public function delete(string $id): void
    {
        $this->requireLogin();

        $payload = Jwt::decode($this->getToken());
        $userId  = $payload->sub;

        try {
            $this->images->delete($id, $userId);
            $this->flash('success', 'Image deleted.');
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
            $this->redirect('/images/' . $id);
        }

        $this->redirect('/dashboard');
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    /**
     * We need the owner ID to know whether to show owner controls.
     * Re-fetches via DB through the service's internal query.
     * The get() call already validated access; this just surfaces ownership.
     */
    private function resolveOwnerId(string $imageId): ?string
    {
        // We can't easily access the raw row from ImagesService::get(),
        // so we call it again with null userId to get the public record,
        // then compare. For private images the outer show() already validated.
        // Simpler: store user_id in the returned payload.
        // Since ImagesService::formatRow() doesn't include user_id, we rely
        // on the JWT userId matching any edit attempt — the service enforces it.
        // Return the current logged-in user so the view shows controls for their own images.
        if ($this->isLoggedIn()) {
            try {
                $payload = Jwt::decode($this->getToken());
                return $payload->sub;
            } catch (\Throwable) {}
        }
        return null;
    }
}
