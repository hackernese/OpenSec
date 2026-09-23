const express = require('express');
const router = express.Router();
const { authenticateToken, isAdmin } = require('../middleware/auth');
const xml2js = require('xml2js');
const libxmljs = require('libxmljs');
const fs = require('fs');
const path = require('path');

// VULNERABLE ENDPOINT 1 - XXE Injection via Sales Report Upload
// This endpoint processes XML sales reports but is vulnerable to XXE attacks
router.post('/upload-sales', authenticateToken, isAdmin, async (req, res) => {
  try {
    const { xmlData } = req.body;

    if (!xmlData) {
      return res.status(400).json({ error: 'XML data required' });
    }

    // VULNERABILITY: XML parsing with external entities enabled
    // This allows XXE attacks to read local files or perform SSRF
    const parserOptions = {
      // DANGEROUS: Explicitly enabling features that allow XXE
      noent: true,  // Enable entity expansion
      dtdload: true, // Load external DTD
      dtdvalid: true // Validate against DTD
    };

    console.log('Parsing XML sales report with XXE-vulnerable parser');

    try {
      // Using libxmljs which is vulnerable to XXE when configured improperly
      const xmlDoc = libxmljs.parseXml(xmlData, parserOptions);
      
      // Extract data from XML
      const root = xmlDoc.root();
      const salesData = {
        reportName: root.get('//reportName')?.text() || 'Unknown',
        period: root.get('//period')?.text() || 'Unknown',
        totalSales: root.get('//totalSales')?.text() || '0',
        items: []
      };

      // Get all sale items
      const items = root.find('//item');
      items.forEach(item => {
        salesData.items.push({
          product: item.get('product')?.text() || '',
          quantity: item.get('quantity')?.text() || '0',
          revenue: item.get('revenue')?.text() || '0'
        });
      });

      res.json({
        message: 'Sales report processed successfully',
        data: salesData
      });
    } catch (parseError) {
      // Even errors can leak information in XXE attacks
      res.status(400).json({ 
        error: 'XML parsing failed',
        message: parseError.message,
        details: parseError.toString()
      });
    }
  } catch (error) {
    console.error('Upload sales report error:', error);
    res.status(500).json({ error: 'Failed to process sales report', message: error.message });
  }
});

// VULNERABLE ENDPOINT 2 - XXE Injection via Product Import
// This endpoint imports products from XML but is vulnerable to XXE
router.post('/import-products', authenticateToken, isAdmin, async (req, res) => {
  try {
    const { xmlContent } = req.body;

    if (!xmlContent) {
      return res.status(400).json({ error: 'XML content required' });
    }

    // VULNERABILITY: xml2js parser with XXE-vulnerable configuration
    const parser = new xml2js.Parser({
      // DANGEROUS: These settings enable XXE attacks
      explicitChildren: true,
      preserveChildrenOrder: true,
      // Not disabling external entities (vulnerable by default in older versions)
    });

    console.log('Parsing product import XML');

    parser.parseString(xmlContent, async (err, result) => {
      if (err) {
        return res.status(400).json({ 
          error: 'XML parsing failed',
          message: err.message,
          details: err.toString()
        });
      }

      try {
        // Process the parsed XML
        const products = [];
        if (result.products && result.products.product) {
          for (const prod of result.products.product) {
            products.push({
              name: prod.name ? prod.name[0] : 'Unknown',
              description: prod.description ? prod.description[0] : '',
              price: prod.price ? prod.price[0] : '0',
              stock: prod.stock ? prod.stock[0] : '0'
            });
          }
        }

        res.json({
          message: 'Products imported successfully',
          count: products.length,
          products: products
        });
      } catch (processingError) {
        res.status(500).json({ 
          error: 'Product processing failed',
          message: processingError.message 
        });
      }
    });
  } catch (error) {
    console.error('Import products error:', error);
    res.status(500).json({ error: 'Failed to import products', message: error.message });
  }
});

module.exports = router;
