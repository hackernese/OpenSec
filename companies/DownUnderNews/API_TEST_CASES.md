# API Test Cases – The Down Under News

**Base URL:** `http://localhost:5000`  
**Tool:** curl, Postman, or any HTTP client.

Replace `<TOKEN>` with the JWT returned from a login call.  
Replace slugs/IDs with real values from your database.

---

## 1. Auth

### Login (get a token)
```
POST /login
Content-Type: application/json

{ "username": "admin", "password": "yourpassword" }
```
- ✅ Expect `200` with `token` and `user` fields
- ❌ Wrong password → `401`
- ❌ Missing fields → `400`

### Get current user
```
GET /api/admin/me
Authorization: Bearer <TOKEN>
```
- ✅ Expect `200` with user object
- ❌ No token → `401`

### Update profile
```
PUT /profile
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "first_name": "Jane", "last_name": "Doe" }
```
- ✅ Expect `200` with updated user

### Change password
```
POST /change-password
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "current_password": "oldpass", "new_password": "newpass123" }
```
- ✅ Expect `200` success message
- ❌ Wrong current password → `401`
- ❌ New password < 8 chars → `400`

---

## 2. Public API (no auth needed)

### List articles
```
GET /api/articles
GET /api/articles?page=1&limit=5
GET /api/articles?search=news
GET /api/articles?category=<category-slug>
```
- ✅ Expect `200` with `articles`, `total`, `page`, `totalPages`

### Featured articles
```
GET /api/articles/featured
```
- ✅ Expect `200` with list of featured articles

### Get single article
```
GET /api/articles/<slug>
```
- ✅ Expect `200` with full article and `related` list
- ❌ Unknown slug → `404`

### List categories
```
GET /api/categories
```
- ✅ Expect `200` with `categories` list

### Articles by category
```
GET /api/categories/<category-slug>/articles
```
- ✅ Expect `200` with `category`, `articles`, pagination fields
- ❌ Unknown slug → `404`

### Search
```
GET /api/search?q=australia
GET /api/search?q=sport&category=<slug>
GET /api/search?q=news&date_from=2024-01-01&date_to=2024-12-31
```
- ✅ Expect `200` with `results`, `total`, `query`
- Empty `q` → `200` with empty results (not an error)

---

## 3. Admin API (token required)

### Dashboard stats
```
GET /api/admin/dashboard
Authorization: Bearer <TOKEN>
```
- ✅ Expect `200` with `stats`, `recent_articles`, `popular_articles`

---

### Articles (admin)

**List all**
```
GET /api/admin/articles
GET /api/admin/articles?status=published
GET /api/admin/articles?search=title
Authorization: Bearer <TOKEN>
```

**Get one**
```
GET /api/admin/articles/<id>
Authorization: Bearer <TOKEN>
```

**Create**
```
POST /api/admin/articles
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "title": "Test Article",
  "content": "Body text here.",
  "status": "draft",
  "category_id": 1,
  "tags": ["tag1", "tag2"]
}
```
- ✅ Expect `201` with new article
- ❌ Missing title or content → `400`

**Update**
```
PUT /api/admin/articles/<id>
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "title": "Updated Title", "status": "published" }
```
- ✅ Expect `200` with updated article

**Publish / Unpublish**
```
PATCH /api/admin/articles/<id>/publish
PATCH /api/admin/articles/<id>/unpublish
Authorization: Bearer <TOKEN>
```
- ✅ Expect `200` with updated article

**Delete**
```
DELETE /api/admin/articles/<id>
Authorization: Bearer <TOKEN>
```
- ✅ Expect `200` success message
- ❌ Non-existent ID → `404`

---

### Categories (admin)

**List**
```
GET /api/admin/categories
Authorization: Bearer <TOKEN>
```

**Create**
```
POST /api/admin/categories
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "name": "Science", "description": "Science articles" }
```
- ✅ Expect `201`
- ❌ Missing name → `400`

**Update**
```
PUT /api/admin/categories/<id>
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "name": "Updated Name", "display_order": 2 }
```

**Delete** *(admin only)*
```
DELETE /api/admin/categories/<id>
Authorization: Bearer <TOKEN>
```

---

### Users (admin only)

**List**
```
GET /api/admin/users
Authorization: Bearer <TOKEN>
```

**Create**
```
POST /api/admin/users
Authorization: Bearer <TOKEN>
Content-Type: application/json

{
  "username": "newwriter",
  "email": "writer@example.com",
  "password": "secure123",
  "role": "writer"
}
```
- ✅ Expect `201`
- ❌ Duplicate username/email → `409`
- ❌ Password < 8 chars → `400`
- ❌ Invalid role → `400`

**Update**
```
PUT /api/admin/users/<id>
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "role": "editor", "is_active": false }
```

**Reset password**
```
POST /api/admin/users/<id>/reset-password
Authorization: Bearer <TOKEN>
Content-Type: application/json

{ "new_password": "newpass123" }
```

**Delete**
```
DELETE /api/admin/users/<id>
Authorization: Bearer <TOKEN>
```
- ❌ Deleting your own account → `400`

---

### Comments (admin/editor only)

**List**
```
GET /api/admin/comments
GET /api/admin/comments?approved=pending
GET /api/admin/comments?approved=approved
Authorization: Bearer <TOKEN>
```

**Approve**
```
PATCH /api/admin/comments/<id>/approve
Authorization: Bearer <TOKEN>
```
- ✅ Expect `200` success message

**Delete**
```
DELETE /api/admin/comments/<id>
Authorization: Bearer <TOKEN>
```

---

### Media

**List**
```
GET /api/admin/media
GET /api/admin/media?type=image
Authorization: Bearer <TOKEN>
```

**Upload**
```
POST /api/admin/media/upload
Authorization: Bearer <TOKEN>
Content-Type: multipart/form-data

file=@/path/to/image.jpg
```
- ✅ Expect `201` with `url`, `filename`, `media`
- ❌ No file → `400`

**Delete**
```
DELETE /api/admin/media/<id>
Authorization: Bearer <TOKEN>
```

---

## 4. Public HTML pages (browser / smoke test)

| URL | Expected result |
|-----|-----------------|
| `GET /` | Homepage loads |
| `GET /category/<slug>` | Category page loads |
| `GET /article/<slug>` | Article page loads, view count increments |
| `GET /search?q=test` | Search results page |
| `GET /about` | About page loads |
| `GET /contact` | Contact page loads |
| `POST /article/<slug>/comment` (form data: `author_name`, `author_email`, `content`) | Redirects back to article with success flash |

---

## 5. Role access checks

| Action | admin | editor | writer |
|--------|-------|--------|--------|
| Create article | ✅ | ✅ | ✅ (draft only) |
| Publish article | ✅ | ✅ | ❌ |
| Delete article | ✅ | ✅ | ❌ |
| Manage categories | ✅ | ✅ | ❌ |
| Manage users | ✅ | ❌ | ❌ |
| Moderate comments | ✅ | ✅ | ❌ |
| Delete category | ✅ | ❌ | ❌ |
