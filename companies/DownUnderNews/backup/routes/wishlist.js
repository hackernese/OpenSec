const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authenticateToken } = require('../middleware/auth');

// Get user's wishlist
router.get('/', authenticateToken, async (req, res) => {
  try {
    const [items] = await db.query(
      `SELECT w.*, p.name, p.price, p.image_url, p.stock 
       FROM wishlist w 
       JOIN products p ON w.product_id = p.id 
       WHERE w.user_id = ?`,
      [req.user.userId]
    );

    res.json(items);
  } catch (error) {
    console.error('Get wishlist error:', error);
    res.status(500).json({ error: 'Failed to get wishlist' });
  }
});

// Add to wishlist
router.post('/', authenticateToken, async (req, res) => {
  try {
    const { productId } = req.body;

    if (!productId) {
      return res.status(400).json({ error: 'Product ID required' });
    }

    // Check if already in wishlist
    const [existing] = await db.query(
      'SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?',
      [req.user.userId, productId]
    );

    if (existing.length > 0) {
      return res.status(400).json({ error: 'Product already in wishlist' });
    }

    await db.query(
      'INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)',
      [req.user.userId, productId]
    );

    res.status(201).json({ message: 'Added to wishlist' });
  } catch (error) {
    console.error('Add to wishlist error:', error);
    res.status(500).json({ error: 'Failed to add to wishlist' });
  }
});

// Remove from wishlist
router.delete('/:productId', authenticateToken, async (req, res) => {
  try {
    await db.query(
      'DELETE FROM wishlist WHERE user_id = ? AND product_id = ?',
      [req.user.userId, req.params.productId]
    );

    res.json({ message: 'Removed from wishlist' });
  } catch (error) {
    console.error('Remove from wishlist error:', error);
    res.status(500).json({ error: 'Failed to remove from wishlist' });
  }
});

module.exports = router;
