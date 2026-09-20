<?php

declare(strict_types=1);

namespace Imager\UI;

use Imager\modules\auth\AuthService;
use Imager\Exceptions\HttpException;

final class AuthUiController extends BaseController
{
    private AuthService $service;

    public function __construct()
    {
        parent::__construct();
        $this->service = new AuthService();
    }

    // ── GET /login ────────────────────────────────────────────────────────────

    public function loginForm(): void
    {
        $this->requireGuest();
        $this->render('auth/login', [], 'Log in');
    }

    // ── POST /login ───────────────────────────────────────────────────────────

    public function loginSubmit(): void
    {
        $this->requireGuest();

        $email    = trim($_POST['email']    ?? '');
        $password = trim($_POST['password'] ?? '');

        try {
            $token = $this->service->login($email, $password);
            $this->login($token);
            $this->redirect('/dashboard');
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
            $this->redirect('/login');
        }
    }

    // ── GET /register ─────────────────────────────────────────────────────────

    public function registerForm(): void
    {
        $this->requireGuest();
        $this->render('auth/register', [], 'Create account');
    }

    // ── POST /register ────────────────────────────────────────────────────────

    public function registerSubmit(): void
    {
        $this->requireGuest();

        $email    = trim($_POST['email']    ?? '');
        $password = trim($_POST['password'] ?? '');
        $confirm  = trim($_POST['confirm']  ?? '');

        if ($password !== $confirm) {
            $this->flash('error', 'Passwords do not match.');
            $this->redirect('/register');
        }

        try {
            $this->service->register($email, $password);
            // Auto-login after registration
            $token = $this->service->login($email, $password);
            $this->login($token);
            $this->flash('success', 'Welcome to Imager!');
            $this->redirect('/dashboard');
        } catch (HttpException $e) {
            $this->flash('error', $e->getMessage());
            $this->redirect('/register');
        }
    }

    // ── POST /logout ──────────────────────────────────────────────────────────

    public function logoutSubmit(): void
    {
        $this->logout();
        $this->flash('success', 'You have been logged out.');
        $this->redirect('/login');
    }
}
