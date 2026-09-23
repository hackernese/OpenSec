# Imager

A multi-account image hosting platform. Users can upload images, set them as
public or private, and share public images with anyone via a direct URL. Images
are stored in AWS S3; access is always via presigned URLs — the API server never
proxies binary content.

**Domain:** `imager.it.com`  
**Stack:** PHP 8.2 · Apache2 · PostgreSQL 15 · AWS S3 · Docker Compose

---

## Quick Start

### 1. Prerequisites

- Docker ≥ 24 and Docker Compose v2
- An AWS account with an S3 bucket (private ACL)
- AWS credentials with `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` on the bucket

### 2. Clone and configure

```bash
git clone <repo-url> imager
cd imager

cp .env.example .env
# Open .env and fill in all required values (see "Environment Variables" below)
```

### 3. Build and start

```bash
docker compose up --build -d
```

This starts two containers:
- `imager_app` — PHP 8.2 + Apache2, port **8080**
- `imager_db`  — PostgreSQL 15, port **5432**

### 4. Run database migrations

```bash
docker compose exec app php scripts/migrate.php
```

Expected output:
```
[migrate] Applied: 001_create_users.sql
[migrate] Applied: 002_create_images.sql
[migrate] Done — 2 migration(s) applied.
```

### 5. Verify

```bash
curl http://localhost:8080/api/v1/health
# {"status":"ok","service":"imager"}
```

---

## Environment Variables

Copy `.env.example` to `.env` and set each value:

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | `development` or `production` | `development` |
| `APP_URL` | Public base URL | `https://imager.it.com` |
| `DB_HOST` | Postgres host (Docker service name) | `db` |
| `DB_PORT` | Postgres port | `5432` |
| `DB_NAME` | Database name | `imager` |
| `DB_USER` | Database user | `imager` |
| `DB_PASSWORD` | Database password | — |
| `JWT_SECRET` | HS256 signing secret (min 64 chars) | — |
| `JWT_EXPIRES_IN` | Token TTL in seconds | `86400` (24h) |
| `AWS_ACCESS_KEY_ID` | AWS access key | — |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | — |
| `AWS_REGION` | S3 bucket region | `ap-southeast-2` |
| `S3_BUCKET_NAME` | S3 bucket name | `imager-dev` |
| `S3_PUBLIC_URL_TTL` | Presigned URL TTL for public images (s) | `604800` (7d) |
| `S3_PRIVATE_URL_TTL` | Presigned URL TTL for private images (s) | `900` (15m) |
| `CORS_ORIGIN` | Allowed CORS origin | `https://imager.it.com` |
| `MAX_UPLOAD_SIZE_MB` | Max upload size in MB | `10` |

Generate a strong JWT secret:
```bash
openssl rand -hex 64
```

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Auth

#### `POST /api/v1/auth/register`
Register a new user account.

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"strongpassword"}'
```

Response `201`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "created_at": "2026-08-05T09:00:00+00:00"
}
```

---

#### `POST /api/v1/auth/login`
Login and receive a JWT.

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"strongpassword"}'
```

Response `200`:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

#### `POST /api/v1/auth/logout`
Logout (stateless — instructs client to discard the token).

```bash
curl -X POST http://localhost:8080/api/v1/auth/logout \
  -H 'Authorization: Bearer <token>'
```

---

### Images

#### `GET /api/v1/images`
List all images owned by the authenticated user.

```bash
curl http://localhost:8080/api/v1/images \
  -H 'Authorization: Bearer <token>'
```

Response `200` — array of image objects.

---

#### `POST /api/v1/images`
Upload a new image (multipart/form-data).

Fields:
- `file` — image binary (required; JPEG, PNG, GIF, WebP; max 10 MB)
- `is_public` — `"true"` or `"false"` (default `"false"`)

```bash
curl -X POST http://localhost:8080/api/v1/images \
  -H 'Authorization: Bearer <token>' \
  -F 'file=@/path/to/photo.jpg' \
  -F 'is_public=true'
```

Response `201`:
```json
{
  "id": "uuid",
  "filename": "photo.jpg",
  "mime_type": "image/jpeg",
  "file_size": 204800,
  "is_public": true,
  "url": "https://s3.amazonaws.com/...(presigned)...",
  "uploaded_at": "2026-08-05T09:00:00+00:00"
}
```

---

#### `GET /api/v1/images/:id`
View a single image.
- Public images: no authentication required.
- Private images: must be the owner (`Authorization: Bearer <token>`).

Responds with a `302` redirect to the S3 presigned URL, plus JSON metadata in the body.

---

#### `PATCH /api/v1/images/:id`
Update image visibility.

```bash
curl -X PATCH http://localhost:8080/api/v1/images/<id> \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"is_public": false}'
```

---

#### `DELETE /api/v1/images/:id`
Delete an image (removes from S3 and database). Returns `204 No Content`.

---

### Error Responses

All errors follow this format:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token."
  }
}
```

| HTTP | Code | Cause |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Missing or invalid fields |
| 401 | `UNAUTHORIZED` | Missing/invalid/expired JWT |
| 403 | `FORBIDDEN` | Not the resource owner |
| 404 | `NOT_FOUND` | Resource does not exist |
| 413 | `FILE_TOO_LARGE` | Upload exceeds size limit |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | File type not allowed |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

---

## Project Structure

```
.
├── apache2/
│   └── imager.conf          # Apache2 VirtualHost config
├── migrations/
│   ├── 001_create_users.sql
│   └── 002_create_images.sql
├── public/
│   ├── .htaccess            # mod_rewrite front-controller routing + CORS
│   └── index.php            # Front-controller router
├── scripts/
│   └── migrate.php          # Database migration runner
├── src/
│   ├── config/
│   │   ├── Database.php     # PDO PostgreSQL singleton
│   │   ├── Jwt.php          # JWT encode/decode (HS256)
│   │   └── S3.php           # AWS S3 client + presigned URLs
│   ├── Exceptions/
│   │   └── HttpExceptions.php
│   ├── middleware/
│   │   ├── AuthMiddleware.php   # Bearer JWT extraction
│   │   ├── ErrorHandler.php     # Global JSON error responses
│   │   └── UploadMiddleware.php # MIME + size validation
│   └── modules/
│       ├── auth/
│       │   ├── AuthController.php
│       │   └── AuthService.php
│       └── images/
│           ├── ImagesController.php
│           └── ImagesService.php
├── .env.example
├── .gitignore
├── composer.json
├── docker-compose.yml
└── Dockerfile
```

---

## Development

### Viewing logs

```bash
docker compose logs -f app    # Apache + PHP errors
docker compose logs -f db     # PostgreSQL logs
```

### Running a shell inside the app container

```bash
docker compose exec app bash
```

### Re-running migrations after adding a new file

```bash
docker compose exec app php scripts/migrate.php
```

### Stopping and removing containers

```bash
docker compose down            # stop containers, keep volumes
docker compose down -v         # stop containers AND delete volumes (resets DB)
```

---

## Security Notes

- Passwords are hashed with bcrypt at cost 12.
- JWTs are signed with HS256; secret must be ≥ 64 random bytes.
- JWT expiry is 24 hours; tokens cannot be server-side revoked in v1 (stateless).
- S3 bucket is private — all access is via presigned URLs generated at the API layer.
- MIME type validation uses `finfo` (reads magic bytes), not the client-reported Content-Type.
- Ownership is validated on every mutating and private-read operation.
- `APP_ENV=development` includes stack traces in error responses — set to `production` when deploying.
- Never commit `.env` — it is in `.gitignore`.
