const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authenticateToken } = require('../middleware/auth');

// Get user's addresses
router.get('/', authenticateToken, async (req, res) => {
  try {
    const [addresses] = await db.query(
      'SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC, created_at DESC',
      [req.user.userId]
    );
    res.json(addresses);
  } catch (error) {
    console.error('Get addresses error:', error);
    res.status(500).json({ error: 'Failed to get addresses' });
  }
});

// Add address
router.post('/', authenticateToken, async (req, res) => {
  try {
    const { label, street, city, state, zipCode, country, isDefault } = req.body;

    if (!street || !city || !state || !zipCode || !country) {
      return res.status(400).json({ error: 'Missing required address fields' });
    }

    // If setting as default, unset other defaults
    if (isDefault) {
      await db.query('UPDATE addresses SET is_default = 0 WHERE user_id = ?', [req.user.userId]);
    }

    const [result] = await db.query(
      'INSERT INTO addresses (user_id, label, street, city, state, zip_code, country, is_default) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
      [req.user.userId, label || 'Home', street, city, state, zipCode, country, isDefault ? 1 : 0]
    );

    res.status(201).json({
      message: 'Address added successfully',
      addressId: result.insertId
    });
  } catch (error) {
    console.error('Add address error:', error);
    res.status(500).json({ error: 'Failed to add address' });
  }
});

// Update address
router.put('/:id', authenticateToken, async (req, res) => {
  try {
    const { label, street, city, state, zipCode, country, isDefault } = req.body;

    // If setting as default, unset other defaults
    if (isDefault) {
      await db.query('UPDATE addresses SET is_default = 0 WHERE user_id = ?', [req.user.userId]);
    }

    const [result] = await db.query(
      'UPDATE addresses SET label = ?, street = ?, city = ?, state = ?, zip_code = ?, country = ?, is_default = ? WHERE id = ? AND user_id = ?',
      [label, street, city, state, zipCode, country, isDefault ? 1 : 0, req.params.id, req.user.userId]
    );

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Address not found' });
    }

    res.json({ message: 'Address updated successfully' });
  } catch (error) {
    console.error('Update address error:', error);
    res.status(500).json({ error: 'Failed to update address' });
  }
});

// Delete address
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const [result] = await db.query(
      'DELETE FROM addresses WHERE id = ? AND user_id = ?',
      [req.params.id, req.user.userId]
    );

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Address not found' });
    }

    res.json({ message: 'Address deleted successfully' });
  } catch (error) {
    console.error('Delete address error:', error);
    res.status(500).json({ error: 'Failed to delete address' });
  }
});

module.exports = router;
