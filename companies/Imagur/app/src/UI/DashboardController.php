<?php

declare(strict_types=1);

namespace Imager\UI;

use Imager\config\Jwt;
use Imager\modules\images\ImagesService;
use Imager\Exceptions\HttpException;

final class DashboardController extends BaseController
{
    private ImagesService $images;

    public function __construct()
    {
        parent::__construct();
        $this->images = new ImagesService();
    }

    // ── GET /dashboard ────────────────────────────────────────────────────────

    public function index(): void
    {
        $this->requireLogin();

        $payload = Jwt::decode($this->getToken());
        $userId  = $payload->sub;

        try {
            $images = $this->images->listForUser($userId);
        } catch (HttpException $e) {
            $images = [];
            $this->flash('error', 'Could not load images: ' . $e->getMessage());
        }

        $this->render('dashboard/index', ['images' => $images], 'My Images');
    }
}
