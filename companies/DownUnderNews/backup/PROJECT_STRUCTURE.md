# Project Structure

## Directory Layout

```
test-subject-1/
├── config/
│   └── database.js              # MySQL database connection configuration
│
├── middleware/
│   └── auth.js                  # JWT authentication and authorization middleware
│
├── routes/
│   ├── addresses.js             # Shipping address management endpoints
│   ├── admin.js                 # 🔴 Admin endpoints with 3 OS command injection vulnerabilities
│   ├── auth.js                  # User registration, login, profile endpoints
│   ├── cart.js                  # Shopping cart management endpoints
│   ├── categories.js            # Product category endpoints
│   ├── orders.js                # Order creation and management endpoints
│   ├── payments.js              # Payment method management endpoints
│   ├── products.js              # 🔴 Product endpoints with SQL injection vulnerability
│   ├── reports.js               # 🔴 Report endpoints with 2 XXE injection vulnerabilities
│   ├── reviews.js               # Product review endpoints
│   ├── search.js                # 🔴 User search endpoint with XPath injection vulnerability
│   ├── users.js                 # User management endpoints
│   └── wishlist.js              # Wishlist management endpoints
│
├── data/
│   └── users.xml                # XML data for XPath injection testing (auto-generated)
│
├── .env                         # Environment configuration (generated from .env.example)
├── .env.example                 # Example environment variables
├── .dockerignore                # Docker ignore file
├── .gitignore                   # Git ignore file
├── docker-compose.yml           # Docker Compose configuration for MySQL and API
├── Dockerfile                   # Docker image configuration for Node.js application
├── init-db.js                   # Database initialization script with sample data
├── package.json                 # Node.js dependencies and scripts
├── server.js                    # Main Express application entry point
│
├── README.md                    # Main documentation (you are here)
├── ALL_VULNERABILITIES.md       # Detailed vulnerability documentation and exploitation
├── VULNERABILITIES_SUMMARY.md   # Quick reference guide for all vulnerabilities
├── VULNERABILITY_DETAILS.md     # Original SQL injection detailed documentation
├── SAMPLE_PAYLOADS.md           # Ready-to-use attack payloads for testing
├── SETUP_GUIDE.md               # Detailed setup and testing instructions
├── PROJECT_STRUCTURE.md         # This file - project organization overview
└── test-vulnerabilities.sh      # Automated testing script for all vulnerabilities
```

## File Descriptions

### Configuration Files

**config/database.js**
- MySQL connection pool configuration
- Uses environment variables for credentials
- Returns promise-based database interface

**middleware/auth.js**
- `authenticateToken()` - JWT token verification
- `isAdmin()` - Admin role check middleware
- Used to protect authenticated and admin-only endpoints

### Route Files (Endpoints)

**routes/addresses.js** ✅ Secure
- GET `/api/addresses` - List user's addresses
- POST `/api/addresses` - Add new address
- PUT `/api/addresses/:id` - Update address
- DELETE `/api/addresses/:id` - Delete address

**routes/admin.js** 🔴 **Contains 3 OS Command Injection Vulnerabilities**
- GET `/api/admin/system-info` - System information (VULNERABLE)
- POST `/api/admin/export-logs` - Export logs (VULNERABLE)
- POST `/api/admin/backup` - Create database backup (VULNERABLE)
- All require admin authentication

**routes/auth.js** ✅ Secure
- POST `/api/auth/register` - User registration
- POST `/api/auth/login` - User login (returns JWT)
- GET `/api/auth/me` - Get current user profile

**routes/cart.js** ✅ Secure
- GET `/api/cart` - Get user's cart
- POST `/api/cart/items` - Add item to cart
- PUT `/api/cart/items/:productId` - Update quantity
- DELETE `/api/cart/items/:productId` - Remove item
- DELETE `/api/cart` - Clear cart

**routes/categories.js** ✅ Secure
- GET `/api/categories` - List all categories
- GET `/api/categories/:id` - Get category by ID
- POST `/api/categories` - Create category (admin only)

**routes/orders.js** ✅ Secure
- GET `/api/orders` - List user's orders
- GET `/api/orders/:id` - Get order details with items
- POST `/api/orders` - Create order from cart (with transaction)
- PATCH `/api/orders/:id/status` - Update order status (admin only)

**routes/payments.js** ✅ Secure
- GET `/api/payments/methods` - List payment methods
- POST `/api/payments/methods` - Add payment method
- DELETE `/api/payments/methods/:id` - Delete payment method

**routes/products.js** 🔴 **Contains SQL Injection Vulnerability**
- GET `/api/products` - List products (paginated, secure)
- GET `/api/products/search` - Search products (VULNERABLE - SQL injection)
- GET `/api/products/:id` - Get product by ID (secure)
- POST `/api/products` - Create product (admin only, secure)
- PUT `/api/products/:id` - Update product (admin only, secure)
- DELETE `/api/products/:id` - Delete product (admin only, secure)

**routes/reports.js** 🔴 **Contains 2 XXE Injection Vulnerabilities**
- POST `/api/reports/upload-sales` - Upload sales report XML (VULNERABLE)
- POST `/api/reports/import-products` - Import products from XML (VULNERABLE)
- Both require admin authentication

**routes/reviews.js** ✅ Secure
- GET `/api/reviews/product/:productId` - Get product reviews
- POST `/api/reviews` - Create review
- DELETE `/api/reviews/:id` - Delete review

**routes/search.js** 🔴 **Contains XPath Injection Vulnerability**
- GET `/api/search/users` - Search users in XML (VULNERABLE)
- GET `/api/search/users/xml` - View raw XML data
- Uses XML file at `data/users.xml`

**routes/users.js** ✅ Secure
- GET `/api/users` - List all users (admin only)
- PUT `/api/users/profile` - Update profile
- PUT `/api/users/password` - Change password

**routes/wishlist.js** ✅ Secure
- GET `/api/wishlist` - Get user's wishlist
- POST `/api/wishlist` - Add to wishlist
- DELETE `/api/wishlist/:productId` - Remove from wishlist

### Application Files

**server.js**
- Main Express application setup
- Middleware configuration (CORS, body-parser, logging)
- Route registration
- Error handling
- Health check endpoint at `/health`

**init-db.js**
- Creates database and all tables
- Inserts sample categories and products
- Run automatically by Docker Compose on startup
- Can be run manually with `npm run init-db`

### Docker Files

**docker-compose.yml**
- MySQL 8.0 service with health checks
- Node.js API service with auto database initialization
- Volume for MySQL data persistence
- Port mappings: 3000 (API), 3306 (MySQL)

**Dockerfile**
- Based on Node.js 18 Alpine
- Installs dependencies
- Copies application code
- Exposes port 3000

### Documentation Files

**README.md**
- Overview of the application
- Quick start guide
- API endpoint listing
- Basic vulnerability testing examples

**ALL_VULNERABILITIES.md**
- Complete documentation of all 7 vulnerabilities
- Detailed exploitation examples for each
- Impact assessment
- Remediation recommendations
- References to security standards

**VULNERABILITIES_SUMMARY.md**
- Quick reference table of all vulnerabilities
- One-liner exploit examples
- Impact summary
- Remediation checklist
- Testing tools recommendations

**VULNERABILITY_DETAILS.md**
- In-depth SQL injection documentation
- Multiple attack scenarios
- Complete secure code examples
- Prevention best practices

**SAMPLE_PAYLOADS.md**
- Ready-to-use attack payloads
- Organized by vulnerability type
- Complete cURL command examples
- Encoded payload variations
- Testing workflow guide

**SETUP_GUIDE.md**
- Step-by-step setup instructions
- Admin account creation
- Individual vulnerability testing
- Troubleshooting section
- Tool recommendations

**PROJECT_STRUCTURE.md** (This file)
- Complete project organization
- File and directory descriptions
- Technology stack overview
- Endpoint vulnerability status

### Testing Files

**test-vulnerabilities.sh**
- Bash script for automated testing
- Tests all 7 vulnerabilities
- Color-coded output
- Usage: `./test-vulnerabilities.sh http://localhost:3000`

## Technology Stack

### Backend
- **Runtime**: Node.js 18
- **Framework**: Express.js 4.18
- **Language**: JavaScript (ES6+)

### Database
- **RDBMS**: MySQL 8.0
- **Driver**: mysql2 (promise-based)
- **ORM**: None (raw SQL queries)

### Security (Intentionally Misconfigured)
- **Authentication**: JWT (jsonwebtoken)
- **Password Hashing**: bcrypt
- **XML Parsing**: libxmljs, xml2js (with XXE enabled)
- **XPath**: xpath + xmldom

### Development Tools
- **Container**: Docker + Docker Compose
- **Process Manager**: PM2 (optional)
- **Code Style**: Standard JavaScript

### Dependencies
```json
{
  "express": "^4.18.2",
  "mysql2": "^3.6.0",
  "bcrypt": "^5.1.1",
  "jsonwebtoken": "^9.0.2",
  "dotenv": "^16.3.1",
  "cors": "^2.8.5",
  "body-parser": "^1.20.2",
  "express-validator": "^7.0.1",
  "xml2js": "^0.4.23",
  "libxmljs": "^0.19.10",
  "xpath": "^0.0.32",
  "xmldom": "^0.6.0"
}
```

## Database Schema

### Tables

1. **users** - User accounts
   - Columns: id, email, password, first_name, last_name, phone, role, created_at, updated_at

2. **categories** - Product categories
   - Columns: id, name, description, created_at

3. **products** - Product catalog
   - Columns: id, name, description, price, stock, category_id, image_url, created_at, updated_at

4. **cart_items** - Shopping cart items
   - Columns: id, user_id, product_id, quantity, created_at

5. **orders** - Customer orders
   - Columns: id, user_id, total_amount, status, shipping_address_id, payment_method, created_at, updated_at

6. **order_items** - Order line items
   - Columns: id, order_id, product_id, quantity, price

7. **reviews** - Product reviews
   - Columns: id, user_id, product_id, rating, comment, created_at

8. **wishlist** - User wishlists
   - Columns: id, user_id, product_id, created_at

9. **addresses** - Shipping addresses
   - Columns: id, user_id, label, street, city, state, zip_code, country, is_default, created_at

10. **payment_methods** - Saved payment methods
    - Columns: id, user_id, card_type, last_four, expiry_month, expiry_year, is_default, created_at

## Vulnerability Locations

### 🔴 Critical Vulnerabilities (CVSS 9.0+)

1. **SQL Injection**
   - File: `routes/products.js`
   - Line: ~11-31
   - Function: `router.get('/search', ...)`
   - Parameter: `query`, `category`, `minPrice`, `maxPrice`

2. **OS Command Injection #1**
   - File: `routes/admin.js`
   - Line: ~8-32
   - Function: `router.get('/system-info', ...)`
   - Parameter: `command`

3. **OS Command Injection #2**
   - File: `routes/admin.js`
   - Line: ~34-60
   - Function: `router.post('/export-logs', ...)`
   - Parameter: `filename`

4. **OS Command Injection #3**
   - File: `routes/admin.js`
   - Line: ~62-95
   - Function: `router.post('/backup', ...)`
   - Parameter: `email`, `backupName`

### 🟡 High Vulnerabilities (CVSS 7.0-8.9)

5. **XXE Injection #1**
   - File: `routes/reports.js`
   - Line: ~7-50
   - Function: `router.post('/upload-sales', ...)`
   - Parameter: `xmlData`

6. **XXE Injection #2**
   - File: `routes/reports.js`
   - Line: ~52-90
   - Function: `router.post('/import-products', ...)`
   - Parameter: `xmlContent`

7. **XPath Injection**
   - File: `routes/search.js`
   - Line: ~45-95
   - Function: `router.get('/users', ...)`
   - Parameter: `username`, `role`

## Environment Variables

See `.env.example` for all required configuration:

```env
# Database
DB_HOST=mysql
DB_USER=ecommerce_user
DB_PASSWORD=ecommerce_pass
DB_NAME=ecommerce_db
DB_PORT=3306

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=24h

# Server
PORT=3000
NODE_ENV=development
```

## Quick Start Commands

```bash
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Run tests
./test-vulnerabilities.sh

# Initialize database manually
docker-compose exec api npm run init-db

# Access MySQL
docker exec -it ecommerce_mysql mysql -u ecommerce_user -pecommerce_pass ecommerce_db
```

## Security Notes

⚠️ **This is intentionally vulnerable software**
- Contains 7 exploitable vulnerabilities
- Never deploy to production
- Only use in isolated test environments
- Designed for security training and testing

✅ **Appropriate Use Cases**
- Security education and training
- Penetration testing practice
- Vulnerability scanner testing
- Secure code review exercises
- Security tool development
