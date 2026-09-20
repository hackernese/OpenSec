-- Migration: 002_create_images
-- Creates the images table with UUID PK, FK to users, S3 key/url, visibility flag.

CREATE TABLE IF NOT EXISTS images (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename    VARCHAR(255) NOT NULL,
    mime_type   VARCHAR(100) NOT NULL,
    file_size   BIGINT       NOT NULL,
    s3_key      VARCHAR(512) NOT NULL UNIQUE,
    is_public   BOOLEAN      NOT NULL DEFAULT FALSE,
    uploaded_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_images_user_id    ON images (user_id);
CREATE INDEX IF NOT EXISTS idx_images_is_public  ON images (is_public);
