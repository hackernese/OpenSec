# SPECS.md — Imager Platform Specification

---

## 1. Company Vision & Story

**Imager** was founded on the belief that visual content should be effortless to store, share, and control. In a world drowning in screenshots, design assets, travel photos, and creative work, most hosting tools either force everything to be public or lock everything behind corporate complexity.

Imager fills that gap: a clean, fast, multi-account image hosting platform where individuals and teams can share what they want, keep private what they don't, and never worry about where or how their images are stored.

The name reflects the mission — you are the imager. You decide what the world sees.

**Domain:** `imager.it.com`

---

## 2. Goals & Non-Goals

### Goals
- Allow users to register and manage individual accounts
- Each user can upload, view, and delete their own images
- Each image can be marked **public** (accessible by anyone with the link) or **private** (accessible only to the owner)
- Images are stored in AWS S3 with access controlled at the API layer
- The platform is secure by default: authenticated routes, scoped permissions, no cross-user data leaks

### Non-Goals (v1)
- No social features (likes, comments, follows)
- No payment or subscription tiers
- No image editing or transformation
- No mobile native app (web only in v1)

---

## 3. User Stories

### Authentication
- As a new visitor, I can register an account with an email and password.
- As a returning user, I can log in and receive a session token (JWT).
- As a logged-in user, I can log out and invalidate my session.
- As a user, my password is stored hashed and never returned in any response.

### Image Management
- As a logged-in user, I can upload an image file (JPEG, PNG, GIF, WebP).
- As a logged-in user, I can set an image as **public** or **private** at upload time.
- As a logged-in user, I can update the visibility of an existing image (public ↔ private).
- As a logged-in user, I can delete any of my own images.
- As a logged-in user, I can view a list of all my images (both public and private).
- As a logged-in user, I can view any individual image I own.

### Public Access
- As an anonymous visitor, I can view any image that has been marked **public** using its direct URL.
- As an anonymous visitor, I cannot access any image marked **private** — the server returns 403.
- As an anonymous visitor, I cannot list or discover any user's images.

---

## 4. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Node.js with Express (TypeScript) |
| Authentication | JWT (JSON Web Tokens), bcrypt for passwords |
| Database | PostgreSQL (users, image metadata) |
| File Storage | AWS S3 (image binaries) |
| File Upload | Multipart form-data via `multer` |
| Infrastructure | Docker + Docker Compose for local dev |
| Environment Config | `.env` files, never committed |

> The stack is chosen for simplicity, wide ecosystem support, and straightforward AWS SDK integration.

---

## 5. Data Models

### User
```
id          UUID          Primary key
email       VARCHAR(255)  Unique, not null
password    VARCHAR(255)  Bcrypt hash, not null
created_at  TIMESTAMP     Default now()
```

### Image
```
id           UUID          Primary key
user_id      UUID          Foreign key → User.id, not null
filename     VARCHAR(255)  Original filename, not null
s3_key       VARCHAR(512)  S3 object key, not null, unique
s3_url       TEXT          Full public/presigned URL or CDN path
is_public    BOOLEAN       Default false
uploaded_at  TIMESTAMP     Default now()
```

---

## 6. API Specification

All endpoints are prefixed with `/api/v1`.

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Register a new user |
| POST | `/auth/login` | None | Login, returns JWT |
| POST | `/auth/logout` | Bearer JWT | Invalidate session |

#### POST `/auth/register`
Request body:
```json
{
  "email": "user@example.com",
  "password": "strongpassword"
}
```
Response `201`:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2026-08-04T00:00:00Z"
}
```

#### POST `/auth/login`
Request body:
```json
{
  "email": "user@example.com",
  "password": "strongpassword"
}
```
Response `200`:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR..."
}
```

---

### Images

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/images` | Bearer JWT | List all images for the authenticated user |
| POST | `/images` | Bearer JWT | Upload a new image |
| GET | `/images/:id` | Optional JWT | View an image (public: no auth, private: must own it) |
| PATCH | `/images/:id` | Bearer JWT | Update visibility of an image |
| DELETE | `/images/:id` | Bearer JWT | Delete an image |

#### POST `/images` — Multipart form
Fields:
- `file` — the image binary (required)
- `is_public` — `"true"` or `"false"` (default: `"false"`)

Response `201`:
```json
{
  "id": "uuid",
  "filename": "photo.jpg",
  "is_public": false,
  "url": "https://imager.it.com/api/v1/images/uuid",
  "uploaded_at": "2026-08-04T00:00:00Z"
}
```

#### GET `/images/:id`
- If image is **public**: returns image data (or redirect to S3 presigned URL), no auth required.
- If image is **private**: requires valid JWT belonging to the image owner. Returns `403` otherwise.

#### PATCH `/images/:id`
Request body:
```json
{
  "is_public": true
}
```
Response `200`:
```json
{
  "id": "uuid",
  "is_public": true
}
```

---

## 7. S3 Storage Design

- One S3 bucket per environment (e.g., `imager-prod`, `imager-dev`).
- S3 bucket is **private by default** — no public bucket policy.
- Object key format: `users/{user_id}/{uuid}.{ext}` (e.g., `users/abc-123/img-456.jpg`).
- For **public** images: generate an S3 presigned GET URL (configurable TTL, e.g., 7 days) or store a cached CDN URL.
- For **private** images: generate a short-lived presigned URL (e.g., 15 minutes) only when the authenticated owner requests it.
- Images are never served directly from the API server binary payload — the API redirects to the presigned URL.
- On image deletion: the S3 object is deleted along with the database record (atomic as possible; handle S3 failures gracefully).

---

## 8. Security Requirements

- All passwords hashed with `bcrypt` (min 12 rounds).
- JWT tokens signed with `HS256`, secret stored in environment variable, never in code.
- JWT expiry: 24 hours for access tokens.
- All private routes protected by `authMiddleware` that validates the JWT and attaches `req.user`.
- Image ownership validated on every mutating or private read operation — a user cannot access, modify, or delete another user's image.
- File upload validation: MIME type check + file size limit (e.g., max 10 MB per image).
- Allowed file types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`.
- S3 credentials (Access Key ID, Secret Access Key, bucket name, region) stored in `.env`, never hardcoded.
- CORS configured to allow only `https://imager.it.com`.
- HTTP security headers via `helmet`.
- Rate limiting on auth endpoints to prevent brute-force attacks.
- No sensitive data (passwords, tokens, S3 secrets) returned in any API response or logged to stdout.

---

## 9. Project Structure

```
imager/
├── src/
│   ├── config/
│   │   ├── db.ts           # PostgreSQL connection pool
│   │   └── s3.ts           # AWS S3 client initialization
│   ├── middleware/
│   │   ├── auth.ts         # JWT verification middleware
│   │   ├── upload.ts       # multer config + file validation
│   │   └── errorHandler.ts # Global error handler
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── auth.routes.ts
│   │   │   ├── auth.controller.ts
│   │   │   └── auth.service.ts
│   │   └── images/
│   │       ├── images.routes.ts
│   │       ├── images.controller.ts
│   │       └── images.service.ts
│   ├── models/
│   │   ├── user.model.ts
│   │   └── image.model.ts
│   └── app.ts              # Express app setup
├── migrations/             # SQL migration files
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── package.json
└── tsconfig.json
```

---

## 10. Environment Variables

```env
# App
PORT=3000
NODE_ENV=development

# Database
DATABASE_URL=postgres://user:password@localhost:5432/imager

# JWT
JWT_SECRET=replace_with_a_long_random_secret
JWT_EXPIRES_IN=24h

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-southeast-2
S3_BUCKET_NAME=imager-dev

# CORS
CORS_ORIGIN=https://imager.it.com
```

---

## 11. Error Handling

All error responses follow a consistent format:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token."
  }
}
```

Standard error codes:
| HTTP | Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Missing or invalid request fields |
| 401 | `UNAUTHORIZED` | Missing or invalid JWT |
| 403 | `FORBIDDEN` | Valid JWT but not the resource owner |
| 404 | `NOT_FOUND` | Image or user does not exist |
| 413 | `FILE_TOO_LARGE` | Upload exceeds size limit |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | File type not allowed |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

---

## 12. Database Migrations

Migrations live in the `/migrations` folder as numbered SQL files:
```
001_create_users.sql
002_create_images.sql
```

They are run manually or via a migration script on startup in development.

---

## 13. Docker Setup

`docker-compose.yml` brings up:
- `app` — the Express server
- `db` — PostgreSQL 15

The app container waits for the database to be healthy before starting.

---

## 14. Out-of-Scope for v1 (Future Considerations)

- Email verification on registration
- Password reset flow
- Image albums / collections
- Sharing private images with specific users via token link
- Usage quotas per user
- CDN integration (CloudFront) for public image delivery
- Admin dashboard
- Frontend UI (v1 is API-only)
