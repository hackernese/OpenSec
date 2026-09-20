<div class="page-header">
    <h1>My Profile</h1>
</div>

<div class="profile-grid">

    <!-- ── Avatar card ────────────────────────────────────────────────────── -->
    <div class="card profile-avatar-card">

        <div class="avatar-wrap">
            <?php if (!empty($user['avatar_path'])): ?>
                <img
                    src="<?= htmlspecialchars($user['avatar_path']) ?>"
                    alt="Profile picture"
                    class="avatar-img"
                >
            <?php else: ?>
                <div class="avatar-placeholder">
                    <?= strtoupper(substr($user['email'], 0, 1)) ?>
                </div>
            <?php endif; ?>
        </div>

        <h2 class="profile-email"><?= htmlspecialchars($user['email']) ?></h2>
        <p class="text-muted profile-since">
            Member since <?= date('F Y', strtotime($user['created_at'])) ?>
        </p>

        <div class="profile-stats">
            <div class="stat">
                <span class="stat-value"><?= (int) $total ?></span>
                <span class="stat-label">Image<?= $total !== 1 ? 's' : '' ?></span>
            </div>
        </div>

        <!-- Upload / change avatar -->
        <form
            method="POST"
            action="/profile/avatar"
            enctype="multipart/form-data"
            class="avatar-form"
        >
            <label class="btn btn-ghost btn-sm btn-block" for="avatar" style="cursor:pointer;justify-content:center;">
                📷 <?= empty($user['avatar_path']) ? 'Upload profile picture' : 'Change picture' ?>
            </label>
            <input
                type="file"
                id="avatar"
                name="avatar"
                accept="image/jpeg,image/png,image/gif,image/webp"
                style="display:none"
                onchange="this.form.submit()"
            >
        </form>

        <?php if (!empty($user['avatar_path'])): ?>
            <p class="text-muted" style="font-size:.78rem;text-align:center;margin-top:.5rem">
                Click the button above to replace your picture.
            </p>
        <?php endif; ?>

    </div>

    <!-- ── Info card ──────────────────────────────────────────────────────── -->
    <div>
        <div class="card" style="padding:1.5rem">
            <h2 style="font-size:.75rem;font-weight:600;color:var(--color-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:1rem">
                Account details
            </h2>

            <div class="meta-row">
                <span>Email</span>
                <span><?= htmlspecialchars($user['email']) ?></span>
            </div>
            <div class="meta-row">
                <span>User ID</span>
                <span style="font-family:monospace;font-size:.8rem"><?= htmlspecialchars($user['id']) ?></span>
            </div>
            <div class="meta-row">
                <span>Joined</span>
                <span><?= date('d M Y', strtotime($user['created_at'])) ?></span>
            </div>
            <div class="meta-row">
                <span>Images uploaded</span>
                <span><?= (int) $total ?></span>
            </div>
        </div>

        <div class="card mt-2" style="padding:1.5rem">
            <h2 style="font-size:.75rem;font-weight:600;color:var(--color-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem">
                Quick links
            </h2>
            <div style="display:flex;flex-direction:column;gap:.5rem">
                <a href="/dashboard" class="btn btn-ghost btn-sm">🖼️ My images</a>
                <a href="/images/upload" class="btn btn-ghost btn-sm">⬆️ Upload image</a>
            </div>
        </div>
    </div>

</div>
