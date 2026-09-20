const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const db = require('../config/database');
const { authenticateToken, isAdmin } = require('../middleware/auth');

// Get all users (admin only)
router.get('/', authenticateToken, isAdmin, async (req, res) => {
  try {
    const [users] = await db.query(
      'SELECT id, email, first_name, last_name, phone, role, created_at FROM users ORDER BY created_at DESC'
    );
    res.json(users);
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Failed to get users' });
  }
});

// Update user profile
router.put('/profile', authenticateToken, async (req, res) => {
  try {
    const { firstName, lastName, phone } = req.body;

    await db.query(
      'UPDATE users SET first_name = ?, last_name = ?, phone = ? WHERE id = ?',
      [firstName, lastName, phone || null, req.user.userId]
    );

    res.json({ message: 'Profile updated successfully' });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({ error: 'Failed to update profile' });
  }
});

// Change password
router.put('/password', authenticateToken, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({ error: 'Both passwords required' });
    }

    // Verify current password
    const [users] = await db.query('SELECT password FROM users WHERE id = ?', [req.user.userId]);
    const validPassword = await bcrypt.compare(currentPassword, users[0].password);

    if (!validPassword) {
      return res.status(401).json({ error: 'Current password incorrect' });
    }

    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    await db.query('UPDATE users SET password = ? WHERE id = ?', [hashedPassword, req.user.userId]);

    res.json({ message: 'Password changed successfully' });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({ error: 'Failed to change password' });
  }
});

module.exports = router;
