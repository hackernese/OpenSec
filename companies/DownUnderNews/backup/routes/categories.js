const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authenticateToken, isAdmin } = require('../middleware/auth');

// Get all categories
router.get('/', async (req, res) => {
  try {
    const [categories] = await db.query('SELECT * FROM categories ORDER BY name');
    res.json(categories);
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({ error: 'Failed to get categories' });
  }
});

// Get category by ID
router.get('/:id', async (req, res) => {
  try {
    const [categories] = await db.query('SELECT * FROM categories WHERE id = ?', [req.params.id]);

    if (categories.length === 0) {
      return res.status(404).json({ error: 'Category not found' });
    }

    res.json(categories[0]);
  } catch (error) {
    console.error('Get category error:', error);
    res.status(500).json({ error: 'Failed to get category' });
  }
});

// Create category (admin only)
router.post('/', authenticateToken, isAdmin, async (req, res) => {
  try {
    const { name, description } = req.body;

    if (!name) {
      return res.status(400).json({ error: 'Category name required' });
    }

    const [result] = await db.query(
      'INSERT INTO categories (name, description) VALUES (?, ?)',
      [name, description || null]
    );

    res.status(201).json({
      message: 'Category created successfully',
      categoryId: result.insertId
    });
  } catch (error) {
    console.error('Create category error:', error);
    res.status(500).json({ error: 'Failed to create category' });
  }
});

module.exports = router;
