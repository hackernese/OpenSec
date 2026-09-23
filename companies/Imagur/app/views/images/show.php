<div class="page-header">
    <h1><?= htmlspecialchars($image['filename']) ?></h1>
    <?php if ($isOwner): ?>
        <a href="/dashboard" class="btn btn-ghost btn-sm">← My images</a>
    <?php endif; ?>
</div>

<div class="detail-grid">

    <!-- ── Image preview ──────────────────────────────────────────────────── -->
    <div>
        <img
            class="detail-image"
            src="<?= htmlspecialchars($image['url']) ?>"
            alt="<?= htmlspecialchars($image['filename']) ?>"
            onerror="this.style.background='#e5e7eb';this.alt='Image unavailable';"
        >
    </div>

    <!-- ── Metadata + actions ─────────────────────────────────────────────── -->
    <div class="detail-panel">

        <!-- Metadata -->
        <div class="card" style="padding:1.25rem">
            <h2>Details</h2>
            <div class="meta-row">
                <span>Filename</span>
                <span><?= $image['filename'] ?></span>
            </div>
            <div class="meta-row">
                <span>Type</span>
                <span><?= htmlspecialchars($image['mime_type']) ?></span>
            </div>
            <div class="meta-row">
                <span>Size</span>
                <span><?= number_format($image['file_size'] / 1024, 1) ?> KB</span>
            </div>
            <div class="meta-row">
                <span>Uploaded</span>
                <span><?= htmlspecialchars(date('d M Y, H:i', strtotime($image['uploaded_at']))) ?></span>
            </div>
            <div class="meta-row">
                <span>Visibility</span>
                <span>
                    <span class="badge <?= $image['is_public'] ? 'badge-public' : 'badge-private' ?>">
                        <?= $image['is_public'] ? '🌍 Public' : '🔒 Private' ?>
                    </span>
                </span>
            </div>
        </div>

        <?php if ($isOwner): ?>

            <!-- Direct link -->
            <div class="card" style="padding:1.25rem">
                <h2>Direct link</h2>
                <input
                    type="text"
                    readonly
                    value="<?= htmlspecialchars($image['url']) ?>"
                    onclick="this.select()"
                    style="width:100%;font-size:.8rem;padding:.4rem .6rem;border:1px solid var(--color-border);border-radius:var(--radius);background:var(--color-bg);"
                    title="Click to select"
                >
            </div>

            <!-- Toggle visibility -->
            <div class="card" style="padding:1.25rem">
                <h2>Visibility</h2>
                <form method="POST" action="/images/<?= htmlspecialchars($image['id']) ?>/visibility">
                    <input type="hidden" name="is_public" value="<?= $image['is_public'] ? 'false' : 'true' ?>">
                    <button type="submit" class="btn btn-ghost btn-sm" style="width:100%;justify-content:center;">
                        <?php if ($image['is_public']): ?>
                            🔒 Make private
                        <?php else: ?>
                            🌍 Make public
                        <?php endif; ?>
                    </button>
                </form>
            </div>

            <!-- Danger zone -->
            <div class="danger-zone">
                <h2>⚠ Danger zone</h2>
                <p>Deleting this image is permanent and cannot be undone.</p>
                <form method="POST" action="/images/<?= htmlspecialchars($image['id']) ?>/delete"
                      onsubmit="return confirm('Delete this image permanently?')">
                    <button type="submit" class="btn btn-danger btn-sm" style="width:100%;justify-content:center;">
                        Delete image
                    </button>
                </form>
            </div>

        <?php endif; ?>

    </div><!-- /.detail-panel -->
</div><!-- /.detail-grid -->
