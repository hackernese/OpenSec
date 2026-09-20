const express = require('express');
const router = express.Router();
const db = require('../config/database');
const { authenticateToken } = require('../middleware/auth');

// Get user's cart
router.get('/', authenticateToken, async (req, res) => {
  try {
    const [cartItems] = await db.query(
      `SELECT ci.*, p.name, p.price, p.image_url, p.stock 
       FROM cart_items ci 
       JOIN products p ON ci.product_id = p.id 
       WHERE ci.user_id = ?`,
      [req.user.userId]
    );

    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    res.json({
      items: cartItems,
      total,
      itemCount: cartItems.length
    });
  } catch (error) {
    console.error('Get cart error:', error);
    res.status(500).json({ error: 'Failed to get cart' });
  }
});

// Add item to cart
router.post('/items', authenticateToken, async (req, res) => {
  try {
    const { productId, quantity } = req.body;

    if (!productId || !quantity || quantity < 1) {
      return res.status(400).json({ error: 'Invalid product or quantity' });
    }

    // Check if product exists and has stock
    const [products] = await db.query('SELECT stock FROM products WHERE id = ?', [productId]);
    if (products.length === 0) {
      return res.status(404).json({ error: 'Product not found' });
    }

    if (products[0].stock < quantity) {
      return res.status(400).json({ error: 'Insufficient stock' });
    }

    // Check if item already in cart
    const [existing] = await db.query(
      'SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?',
      [req.user.userId, productId]
    );

    if (existing.length > 0) {
      // Update quantity
      await db.query(
        'UPDATE cart_items SET quantity = quantity + ? WHERE user_id = ? AND product_id = ?',
        [quantity, req.user.userId, productId]
      );
    } else {
      // Insert new item
      await db.query(
        'INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)',
        [req.user.userId, productId, quantity]
      );
    }

    res.status(201).json({ message: 'Item added to cart' });
  } catch (error) {
    console.error('Add to cart error:', error);
    res.status(500).json({ error: 'Failed to add item to cart' });
  }
});

// Update cart item quantity
router.put('/items/:productId', authenticateToken, async (req, res) => {
  try {
    const { quantity } = req.body;

    if (!quantity || quantity < 0) {
      return res.status(400).json({ error: 'Invalid quantity' });
    }

    if (quantity === 0) {
      // Remove item if quantity is 0
      await db.query(
        'DELETE FROM cart_items WHERE user_id = ? AND product_id = ?',
        [req.user.userId, req.params.productId]
      );
    } else {
      await db.query(
        'UPDATE cart_items SET quantity = ? WHERE user_id = ? AND product_id = ?',
        [quantity, req.user.userId, req.params.productId]
      );
    }

    res.json({ message: 'Cart updated' });
  } catch (error) {
    console.error('Update cart error:', error);
    res.status(500).json({ error: 'Failed to update cart' });
  }
});

// Remove item from cart
router.delete('/items/:productId', authenticateToken, async (req, res) => {
  try {
    await db.query(
      'DELETE FROM cart_items WHERE user_id = ? AND product_id = ?',
      [req.user.userId, req.params.productId]
    );

    res.json({ message: 'Item removed from cart' });
  } catch (error) {
    console.error('Remove from cart error:', error);
    res.status(500).json({ error: 'Failed to remove item' });
  }
});

// Clear cart
router.delete('/', authenticateToken, async (req, res) => {
  try {
    await db.query('DELETE FROM cart_items WHERE user_id = ?', [req.user.userId]);
    res.json({ message: 'Cart cleared' });
  } catch (error) {
    console.error('Clear cart error:', error);
    res.status(500).json({ error: 'Failed to clear cart' });
  }
});

module.exports = router;
