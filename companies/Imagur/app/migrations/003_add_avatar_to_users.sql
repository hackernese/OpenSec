-- Migration: 003_add_avatar_to_users
-- Adds avatar_path column to users for locally-stored profile pictures.

ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_path VARCHAR(512) DEFAULT NULL;
