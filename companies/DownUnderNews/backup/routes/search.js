const express = require('express');
const router = express.Router();
const xpath = require('xpath');
const dom = require('xmldom').DOMParser;
const fs = require('fs');
const path = require('path');
const { authenticateToken } = require('../middleware/auth');

// Initialize XML user database (in-memory for demo)
const userXmlPath = path.join(__dirname, '..', 'data', 'users.xml');

// Create sample XML data if it doesn't exist
function ensureXmlData() {
  const dataDir = path.join(__dirname, '..', 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  if (!fs.existsSync(userXmlPath)) {
    const sampleXml = `<?xml version="1.0" encoding="UTF-8"?>
<users>
  <user id="1">
    <username>admin</username>
    <email>admin@example.com</email>
    <role>administrator</role>
    <firstName>Admin</firstName>
    <lastName>User</lastName>
    <phone>555-0001</phone>
    <apiKey>sk_live_admin_key_12345</apiKey>
  </user>
  <user id="2">
    <username>john_doe</username>
    <email>john@example.com</email>
    <role>customer</role>
    <firstName>John</firstName>
    <lastName>Doe</lastName>
    <phone>555-0002</phone>
    <apiKey>sk_live_user_key_67890</apiKey>
  </user>
  <user id="3">
    <username>jane_smith</username>
    <email>jane@example.com</email>
    <role>customer</role>
    <firstName>Jane</firstName>
    <lastName>Smith</lastName>
    <phone>555-0003</phone>
    <apiKey>sk_live_user_key_abcdef</apiKey>
  </user>
  <user id="4">
    <username>bob_wilson</username>
    <email>bob@example.com</email>
    <role>customer</role>
    <firstName>Bob</firstName>
    <lastName>Wilson</lastName>
    <phone>555-0004</phone>
    <apiKey>sk_live_user_key_ghijkl</apiKey>
  </user>
  <user id="5">
    <username>alice_brown</username>
    <email>alice@example.com</email>
    <role>premium</role>
    <firstName>Alice</firstName>
    <lastName>Brown</lastName>
    <phone>555-0005</phone>
    <apiKey>sk_live_premium_key_mnopqr</apiKey>
  </user>
</users>`;
    fs.writeFileSync(userXmlPath, sampleXml);
  }
}

// VULNERABLE ENDPOINT - XPath Injection
// This endpoint searches users in XML database but is vulnerable to XPath injection
router.get('/users', authenticateToken, async (req, res) => {
  try {
    const { username, role } = req.query;

    if (!username && !role) {
      return res.status(400).json({ 
        error: 'Search parameter required',
        hint: 'Use ?username=john or ?role=customer'
      });
    }

    ensureXmlData();

    // Read XML file
    const xmlContent = fs.readFileSync(userXmlPath, 'utf8');
    const doc = new dom().parseFromString(xmlContent);

    // VULNERABILITY: Direct concatenation of user input into XPath query
    // This allows XPath injection attacks to bypass authentication or extract data
    let xpathQuery;
    
    if (username) {
      // VULNERABLE: No sanitization of username parameter
      xpathQuery = `//user[username='${username}']`;
    } else if (role) {
      // VULNERABLE: No sanitization of role parameter
      xpathQuery = `//user[role='${role}']`;
    }

    console.log('Executing XPath query:', xpathQuery);

    try {
      // Execute the vulnerable XPath query
      const nodes = xpath.select(xpathQuery, doc);

      if (!nodes || nodes.length === 0) {
        return res.json({
          message: 'No users found',
          query: xpathQuery,
          results: []
        });
      }

      // Extract user data from XML nodes
      const users = [];
      for (const node of nodes) {
        const user = {};
        if (node.childNodes) {
          for (const child of node.childNodes) {
            if (child.nodeName && child.textContent) {
              user[child.nodeName] = child.textContent;
            }
          }
        }
        // Also get the id attribute
        if (node.getAttribute) {
          user.id = node.getAttribute('id');
        }
        users.push(user);
      }

      res.json({
        message: 'Users found',
        query: xpathQuery,
        count: users.length,
        results: users
      });
    } catch (xpathError) {
      // Error messages can leak information about the XML structure
      res.status(400).json({
        error: 'XPath query failed',
        query: xpathQuery,
        message: xpathError.message,
        details: xpathError.toString()
      });
    }
  } catch (error) {
    console.error('User search error:', error);
    res.status(500).json({ 
      error: 'Search failed',
      message: error.message 
    });
  }
});

// Additional endpoint to view raw XML (for testing)
router.get('/users/xml', authenticateToken, async (req, res) => {
  try {
    ensureXmlData();
    const xmlContent = fs.readFileSync(userXmlPath, 'utf8');
    res.type('application/xml');
    res.send(xmlContent);
  } catch (error) {
    res.status(500).json({ error: 'Failed to read XML data' });
  }
});

module.exports = router;
