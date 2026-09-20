<div class="page-header">
    <h1>My Images</h1>
    <a href="/images/upload" class="btn btn-primary">+ Upload image</a>
</div>

<?php if (empty($images)): ?>
    <div class="empty-state">
        <div class="icon">🖼️</div>
        <p>You haven't uploaded any images yet.</p>
        <a href="/images/upload" class="btn btn-primary">Upload your first image</a>
    </div>
<?php else: ?>
    <p class="text-muted mb-2"><?= count($images) ?> image<?= count($images) !== 1 ? 's' : '' ?></p>

    <div class="image-grid mt-2">
        <?php foreach ($images as $image): ?>
            <div class="image-card">
                <a href="/images/<?= htmlspecialchars($image['id']) ?>">
                    <img
                        class="image-thumb"
                        src="<?= htmlspecialchars($image['url']) ?>"
                        alt="<?= htmlspecialchars($image['filename']) ?>"
                        loading="lazy"
                        onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"
                    >
                    <div class="image-thumb-placeholder" style="display:none">🖼️</div>
                </a>
                <div class="image-meta">
                    <span class="filename"><?= htmlspecialchars($image['filename']) ?></span>
                    <span class="badge <?= $image['is_public'] ? 'badge-public' : 'badge-private' ?>">
                        <?= $image['is_public'] ? '🌍 Public' : '🔒 Private' ?>
                    </span>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
<?php endif; ?>
