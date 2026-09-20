const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authenticateToken } = require('../middleware/auth');

// Get payment methods
router.get('/methods', authenticateToken, async (req, res) => {
  try {
    const [methods] = await db.query(
      'SELECT id, card_type, last_four, expiry_month, expiry_year, is_default FROM payment_methods WHERE user_id = ?',
      [req.user.userId]
    );
    res.json(methods);
  } catch (error) {
    console.error('Get payment methods error:', error);
    res.status(500).json({ error: 'Failed to get payment methods' });
  }
});

// Add payment method
router.post('/methods', authenticateToken, async (req, res) => {
  try {
    const { cardNumber, cardType, expiryMonth, expiryYear, cvv, isDefault } = req.body;

    if (!cardNumber || !cardType || !expiryMonth || !expiryYear || !cvv) {
      return res.status(400).json({ error: 'Missing required payment fields' });
    }

    const lastFour = cardNumber.slice(-4);

    // If setting as default, unset other defaults
    if (isDefault) {
      await db.query('UPDATE payment_methods SET is_default = 0 WHERE user_id = ?', [req.user.userId]);
    }

    const [result] = await db.query(
      'INSERT INTO payment_methods (user_id, card_type, last_four, expiry_month, expiry_year, is_default) VALUES (?, ?, ?, ?, ?, ?)',
      [req.user.userId, cardType, lastFour, expiryMonth, expiryYear, isDefault ? 1 : 0]
    );

    res.status(201).json({
      message: 'Payment method added successfully',
      paymentMethodId: result.insertId
    });
  } catch (error) {
    console.error('Add payment method error:', error);
    res.status(500).json({ error: 'Failed to add payment method' });
  }
});

// Delete payment method
router.delete('/methods/:id', authenticateToken, async (req, res) => {
  try {
    const [result] = await db.query(
      'DELETE FROM payment_methods WHERE id = ? AND user_id = ?',
      [req.params.id, req.user.userId]
    );

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: 'Payment method not found' });
    }

    res.json({ message: 'Payment method deleted successfully' });
  } catch (error) {
    console.error('Delete payment method error:', error);
    res.status(500).json({ error: 'Failed to delete payment method' });
  }
});

module.exports = router;
