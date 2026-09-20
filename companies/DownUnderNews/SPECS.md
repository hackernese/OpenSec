# The Down Under News - Technical Specification Document

## Project Overview
**Domain:** thedownundernews.it.com  
**Type:** Online Newspaper/News Publication Website  
**Primary Function:** Display news articles with an admin panel for content management

---

## 1. System Architecture

### 1.1 Multi-Server Architecture
The application uses a **distributed architecture** with content separation:

- **Main Application Server**: Hosts the web application, database, and business logic
- **Media/Asset Server**: Hosts all static assets (images, PDFs, downloadable documents)
  - All media files are referenced via external URLs pointing to a different IP address
  - The main server does NOT store or serve media files locally

### 1.2 Technology Stack Recommendations

#### Backend
- **Runtime**: Node.js (Express.js) or Python (Flask/Django) or PHP (Laravel)
- **Database**: PostgreSQL or MySQL
- **Authentication**: JWT-based or session-based authentication
- **API Architecture**: RESTful API

#### Frontend
- **Framework**: React, Vue.js, or vanilla JavaScript
- **Styling**: Tailwind CSS, Bootstrap, or custom CSS
- **Build Tool**: Vite or Webpack

#### Media Server
- **Web Server**: Nginx or Apache (serving static files)
- **Storage**: File system or S3-compatible object storage
- **CORS Configuration**: Must allow requests from main application domain

---

## 2. Core Features & Functional Requirements

### 2.1 Public-Facing Website (Reader Interface)

#### Homepage
- Display latest news articles (grid or list layout)
- Featured/breaking news section at the top
- Category navigation (e.g., Politics, Sports, Business, Technology, Entertainment)
- Search functionality
- Pagination for article listings

#### Article Page
- Display full article content
- Article metadata: author, publication date, category, tags
- Featured image (hosted on external media server)
- Related articles section
- Social media share buttons
- Comments section (optional)

#### Category Pages
- Display articles filtered by category
- Same layout as homepage but filtered

#### Search Functionality
- Full-text search across article titles and content
- Display search results with article snippets
- Filters: by date, category, author

#### Navigation
- Header with logo, main navigation menu, search bar
- Footer with links (About Us, Contact, Privacy Policy, Terms of Service)
- Responsive mobile navigation

---

### 2.2 Admin Panel (Content Management System)

#### Authentication & Authorization
- Secure login page for administrators
- Role-based access control:
  - **Admin**: Full access (create, edit, delete articles, manage users)
  - **Editor**: Create and edit articles, publish/unpublish
  - **Writer**: Create articles (requires approval before publishing)
- Session management with secure logout
- Password reset functionality

#### Dashboard
- Overview statistics:
  - Total articles published
  - Articles pending approval (if multi-role system)
  - Recent activity log
  - Page views (if analytics integrated)

#### Article Management
**Create New Article:**
- Rich text editor (WYSIWYG) for article content
- Fields:
  - Title (required)
  - Subtitle/excerpt (optional)
  - Author name
  - Category selection (dropdown)
  - Tags (multi-select or comma-separated)
  - Featured image upload
  - Additional images for article body
  - Attachments (PDF documents, downloadable files)
  - Publication date/time (schedule for future publishing)
  - Status (Draft, Published, Archived)
- Image/document upload:
  - Files must be uploaded TO the external media server
  - System stores only the URL reference in the database
  - Support for drag-and-drop uploads
  - Image preview before saving

**Edit Article:**
- Load existing article data
- Modify any field
- Update media references
- Save as draft or publish immediately

**Delete Article:**
- Soft delete (mark as deleted but keep in database) or hard delete
- Confirmation dialog before deletion
- Optionally delete associated media files from media server

**Article List View:**
- Table/grid showing all articles
- Columns: Title, Author, Category, Status, Published Date, Actions
- Filters: by status, category, date range, author
- Search within articles
- Bulk actions (publish, unpublish, delete)

#### Category Management
- Create, edit, delete categories
- Category name and slug
- Category description (optional)
- Display order/priority

#### User Management (Admin Only)
- Create new admin users
- Edit user details (name, email, role)
- Deactivate/delete users
- Change passwords (admin can reset user passwords)

#### Media Library
- View all uploaded images and documents
- Display thumbnails for images
- Media details: file name, size, upload date, URL
- Search and filter media files
- Delete media files (if integration with media server allows)

---

## 3. Database Schema

### 3.1 Tables

#### `users`
```
id (PRIMARY KEY, AUTO_INCREMENT)
username (VARCHAR, UNIQUE, NOT NULL)
email (VARCHAR, UNIQUE, NOT NULL)
password_hash (VARCHAR, NOT NULL)
role (ENUM: 'admin', 'editor', 'writer', DEFAULT 'writer')
first_name (VARCHAR)
last_name (VARCHAR)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
is_active (BOOLEAN, DEFAULT TRUE)
```

#### `categories`
```
id (PRIMARY KEY, AUTO_INCREMENT)
name (VARCHAR, UNIQUE, NOT NULL)
slug (VARCHAR, UNIQUE, NOT NULL)
description (TEXT)
display_order (INT, DEFAULT 0)
created_at (TIMESTAMP)
```

#### `articles`
```
id (PRIMARY KEY, AUTO_INCREMENT)
title (VARCHAR, NOT NULL)
slug (VARCHAR, UNIQUE, NOT NULL)
subtitle (VARCHAR)
content (TEXT, NOT NULL)
excerpt (TEXT)
author_id (FOREIGN KEY -> users.id)
category_id (FOREIGN KEY -> categories.id)
featured_image_url (VARCHAR) -- URL to external media server
status (ENUM: 'draft', 'published', 'archived', DEFAULT 'draft')
published_at (TIMESTAMP)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
views_count (INT, DEFAULT 0)
is_featured (BOOLEAN, DEFAULT FALSE)
```

#### `article_media`
```
id (PRIMARY KEY, AUTO_INCREMENT)
article_id (FOREIGN KEY -> articles.id)
media_url (VARCHAR, NOT NULL) -- URL to external media server
media_type (ENUM: 'image', 'document', 'pdf')
file_name (VARCHAR)
file_size (INT) -- in bytes
display_order (INT)
caption (TEXT)
uploaded_at (TIMESTAMP)
```

#### `tags`
```
id (PRIMARY KEY, AUTO_INCREMENT)
name (VARCHAR, UNIQUE, NOT NULL)
slug (VARCHAR, UNIQUE, NOT NULL)
```

#### `article_tags` (Junction table)
```
article_id (FOREIGN KEY -> articles.id)
tag_id (FOREIGN KEY -> tags.id)
PRIMARY KEY (article_id, tag_id)
```

#### `comments` (Optional)
```
id (PRIMARY KEY, AUTO_INCREMENT)
article_id (FOREIGN KEY -> articles.id)
author_name (VARCHAR, NOT NULL)
author_email (VARCHAR, NOT NULL)
content (TEXT, NOT NULL)
is_approved (BOOLEAN, DEFAULT FALSE)
created_at (TIMESTAMP)
```

---

## 4. API Endpoints

### 4.1 Public API (No authentication required)

#### Articles
```
GET /api/articles
  Query params: ?page=1&limit=10&category=<category_slug>&search=<query>
  Response: { articles: [...], total: <count>, page: <num>, totalPages: <num> }

GET /api/articles/:slug
  Response: { article: {...}, related: [...] }

GET /api/articles/featured
  Response: { articles: [...] }

GET /api/categories
  Response: { categories: [...] }

GET /api/categories/:slug/articles
  Query params: ?page=1&limit=10
  Response: { articles: [...], category: {...}, total: <count> }

GET /api/search
  Query params: ?q=<query>&page=1&limit=10
  Response: { results: [...], total: <count> }
```

### 4.2 Admin API (Authentication required)

#### Authentication
```
POST /api/admin/login
  Body: { username/email, password }
  Response: { token/session, user: {...} }

POST /api/admin/logout
  Response: { success: true }

POST /api/admin/forgot-password
  Body: { email }

POST /api/admin/reset-password
  Body: { token, newPassword }
```

#### Article Management
```
GET /api/admin/articles
  Query params: ?status=<status>&category=<id>&page=1&limit=20
  Response: { articles: [...], total: <count> }

POST /api/admin/articles
  Body: { title, content, subtitle, category_id, featured_image_url, tags: [], status, published_at }
  Response: { article: {...} }

PUT /api/admin/articles/:id
  Body: { ...article fields }
  Response: { article: {...} }

DELETE /api/admin/articles/:id
  Response: { success: true }

PATCH /api/admin/articles/:id/publish
  Response: { article: {...} }

PATCH /api/admin/articles/:id/unpublish
  Response: { article: {...} }
```

#### Media Management
```
POST /api/admin/media/upload
  Body: FormData with file
  Action: Upload file to external media server
  Response: { url: <external_media_url>, filename, size }

GET /api/admin/media
  Query params: ?type=<image|document>&page=1&limit=20
  Response: { media: [...], total: <count> }

DELETE /api/admin/media/:id
  Action: Delete from external media server (if possible)
  Response: { success: true }
```

#### Category Management
```
GET /api/admin/categories
POST /api/admin/categories
  Body: { name, slug, description }
PUT /api/admin/categories/:id
DELETE /api/admin/categories/:id
```

#### User Management
```
GET /api/admin/users
POST /api/admin/users
  Body: { username, email, password, role, first_name, last_name }
PUT /api/admin/users/:id
DELETE /api/admin/users/:id
POST /api/admin/users/:id/reset-password
```

---

## 5. External Media Server Integration

### 5.1 Media Server Requirements
- Must be accessible via HTTP/HTTPS
- Must serve static files with proper MIME types
- Must have CORS headers configured to allow requests from main application domain
- Example URL structure: `http://MEDIA_SERVER_IP/uploads/images/article-image-123.jpg`

### 5.2 Upload Process Flow
1. User uploads file through admin panel
2. Backend receives file
3. Backend sends file to external media server via:
   - HTTP POST/PUT request to media server upload endpoint
   - OR SFTP/FTP transfer
   - OR S3-compatible API
4. Media server stores file and returns accessible URL
5. Backend stores only the URL in database
6. Frontend displays images/documents by fetching from external URL

### 5.3 Media Server API (To be implemented on media server)
```
POST /upload
  Body: multipart/form-data with file
  Response: { url: <public_url>, filename, size }

DELETE /files/:filename (Optional)
  Response: { success: true }

GET /files/:filename
  Response: File content with appropriate headers
```

### 5.4 Configuration
Store media server details in environment variables:
```
MEDIA_SERVER_URL=http://MEDIA_SERVER_IP
MEDIA_SERVER_API_KEY=<optional_authentication_key>
MEDIA_UPLOAD_ENDPOINT=/upload
```

---

## 6. Security Requirements

### 6.1 Authentication & Authorization
- Passwords must be hashed using bcrypt or Argon2
- JWT tokens or secure session cookies with httpOnly flag
- CSRF protection for state-changing operations
- Rate limiting on login endpoint to prevent brute force attacks
- Admin panel accessible only to authenticated users
- Role-based access control enforcement on all admin endpoints

### 6.2 Input Validation & Sanitization
- Validate all user inputs on both client and server side
- Sanitize HTML content in articles to prevent XSS
- Use parameterized queries/ORM to prevent SQL injection
- Validate file uploads (file type, size limits)
- Sanitize file names before storage

### 6.3 HTTPS & Transport Security
- Use HTTPS in production
- Set secure headers (CSP, X-Frame-Options, X-Content-Type-Options)
- CORS configuration to allow only trusted domains

### 6.4 Media Server Security
- Validate uploaded files (check magic bytes, not just extension)
- Limit file sizes (e.g., max 10MB for images, 50MB for documents)
- Restrict allowed file types
- Generate unique file names to prevent overwriting
- Optional: Implement authentication for media upload endpoint

---

## 7. Frontend Requirements

### 7.1 Public Website Pages
```
/                          - Homepage (latest articles)
/category/:slug            - Category page
/article/:slug             - Article detail page
/search?q=query            - Search results page
/about                     - About page (static)
/contact                   - Contact page (static)
```

### 7.2 Admin Panel Pages
```
/admin/login               - Login page
/admin/dashboard           - Dashboard overview
/admin/articles            - Article list
/admin/articles/new        - Create new article
/admin/articles/:id/edit   - Edit article
/admin/categories          - Category management
/admin/media               - Media library
/admin/users               - User management (admin only)
/admin/profile             - User profile/settings
```

### 7.3 Responsive Design
- Mobile-first approach
- Breakpoints: mobile (<768px), tablet (768px-1024px), desktop (>1024px)
- Touch-friendly navigation on mobile
- Optimized images for different screen sizes (responsive images)

### 7.4 Accessibility
- Semantic HTML
- ARIA labels where appropriate
- Keyboard navigation support
- Alt text for all images
- Sufficient color contrast

---

## 8. Content Editor Specifications

### 8.1 Rich Text Editor Features
- Bold, italic, underline, strikethrough
- Headings (H2, H3, H4)
- Ordered and unordered lists
- Block quotes
- Code blocks
- Hyperlinks
- Image insertion (upload or paste URL from media server)
- Embed videos (YouTube, Vimeo)
- Text alignment
- Undo/redo

### 8.2 Recommended Editors
- TinyMCE
- CKEditor
- Quill
- Tiptap

---

## 9. Deployment Considerations

### 9.1 Environment Variables
```
# Application
NODE_ENV=production
PORT=3000
APP_URL=https://thedownundernews.it.com

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=newspaper_db
DB_USER=db_user
DB_PASSWORD=secure_password

# Authentication
JWT_SECRET=random_secure_string
SESSION_SECRET=random_secure_string

# Media Server
MEDIA_SERVER_URL=http://MEDIA_SERVER_IP
MEDIA_SERVER_API_KEY=optional_key
MEDIA_UPLOAD_ENDPOINT=/upload

# Email (for password reset)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@thedownundernews.it.com
SMTP_PASSWORD=email_password
```

### 9.2 Server Requirements
**Main Application Server:**
- OS: Linux (Ubuntu 20.04+ recommended)
- RAM: 2GB minimum, 4GB recommended
- Storage: 20GB minimum
- Node.js 18+ (if using Node.js)
- PostgreSQL or MySQL
- Nginx (reverse proxy)

**Media Server:**
- OS: Linux
- Storage: Depends on media volume (start with 50GB+)
- Nginx or Apache for static file serving

### 9.3 Docker Deployment (Optional)
- Create Dockerfile for main application
- Create docker-compose.yml with services: app, database
- Media server can be separate or included as service

---

## 10. Testing Requirements

### 10.1 Backend Testing
- Unit tests for business logic
- Integration tests for API endpoints
- Test authentication and authorization
- Test media upload functionality
- Test database operations

### 10.2 Frontend Testing
- Component tests
- E2E tests for critical flows (login, create article, publish)
- Responsive design testing across devices

### 10.3 Security Testing
- SQL injection testing
- XSS vulnerability testing
- CSRF protection verification
- Authentication bypass attempts
- Rate limiting verification

---

## 11. Future Enhancements (Optional)

- Newsletter subscription system
- Article comments with moderation
- Social media auto-posting
- Analytics dashboard
- Article versioning/revision history
- Multi-language support
- RSS feed
- Push notifications
- Advanced SEO optimization (meta tags, structured data)
- Article scheduling for automated publishing
- Draft auto-save functionality

---

## 12. Success Criteria

The application will be considered complete when:

1. ✅ Public website displays articles with proper layout and navigation
2. ✅ Admin panel allows authenticated users to create, edit, and delete articles
3. ✅ All images and documents are hosted on external media server
4. ✅ Media URLs are correctly stored and referenced in database
5. ✅ Role-based access control is functional
6. ✅ Search functionality works correctly
7. ✅ Application is responsive on mobile, tablet, and desktop
8. ✅ Security measures are implemented (password hashing, CSRF protection, input validation)
9. ✅ Application is deployed and accessible at thedownundernews.it.com
10. ✅ Media server is configured and serving files correctly

---

## 13. Development Notes

- The backup folder contains old/reference code - ignore it completely
- Focus on clean, maintainable code structure
- Use modern JavaScript/TypeScript features
- Follow REST API conventions
- Implement proper error handling and logging
- Use environment variables for all configuration
- Document API endpoints (consider Swagger/OpenAPI)
- Use version control (Git) with meaningful commit messages

---

## Implementation Priority

### Phase 1 (MVP - Minimum Viable Product)
1. Database setup with core tables
2. Basic authentication system
3. Article CRUD operations (admin panel)
4. Media upload to external server
5. Public article listing and detail pages
6. Basic responsive layout

### Phase 2 (Enhanced Features)
1. Category management
2. Rich text editor integration
3. Search functionality
4. User management
5. Improved UI/UX
6. Image optimization

### Phase 3 (Polish & Production)
1. Security hardening
2. Performance optimization
3. SEO optimization
4. Testing (unit, integration, E2E)
5. Documentation
6. Deployment automation
7. Monitoring and logging

---

**Document Version:** 1.0  
**Last Updated:** Tuesday, 2026-08-04  
**Target Domain:** thedownundernews.it.com
