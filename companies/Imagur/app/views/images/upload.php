<div class="page-header">
    <h1>Upload image</h1>
    <a href="/dashboard" class="btn btn-ghost btn-sm">← Back</a>
</div>

<div class="card upload-card">
    <form method="POST" action="/images/upload" enctype="multipart/form-data">

        <!-- Hidden user ID field -->
        <input type="hidden" name="user_id" value="<?= htmlspecialchars($userId) ?>">

        <div class="form-group">
            <label for="file">Image file</label>
            <p class="text-muted mt-1" style="margin-bottom:.5rem">
                JPEG, PNG, GIF or WebP — max 10 MB
            </p>
            <input
                type="file"
                id="file"
                name="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                required
                style="width:100%;padding:.45rem 0;"
            >
        </div>

        <div class="form-group">
            <label>Visibility</label>
            <div class="visibility-toggle mt-1">
                <label>
                    <input type="radio" name="is_public" value="false" checked>
                    🔒 Private (only you)
                </label>
                <label>
                    <input type="radio" name="is_public" value="true">
                    🌍 Public (anyone with the link)
                </label>
            </div>
        </div>

        <button type="submit" class="btn btn-primary btn-block mt-2">
            Upload
        </button>
    </form>
</div>
