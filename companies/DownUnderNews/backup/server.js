require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/auth');
const productRoutes = require('./routes/products');
const categoryRoutes = require('./routes/categories');
const cartRoutes = require('./routes/cart');
const orderRoutes = require('./routes/orders');
const userRoutes = require('./routes/users');
const reviewRoutes = require('./routes/reviews');
const wishlistRoutes = require('./routes/wishlist');
const addressRoutes = require('./routes/addresses');
const paymentRoutes = require('./routes/payments');
const adminRoutes = require('./routes/admin');
const reportRoutes = require('./routes/reports');
const searchRoutes = require('./routes/search');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/products', productRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/cart', cartRoutes);
app.use('/api/orders', orderRoutes);
app.use('/api/users', userRoutes);
app.use('/api/reviews', reviewRoutes);
app.use('/api/wishlist', wishlistRoutes);
app.use('/api/addresses', addressRoutes);
app.use('/api/payments', paymentRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/reports', reportRoutes);
app.use('/api/search', searchRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'E-commerce API',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      products: '/api/products',
      categories: '/api/categories',
      cart: '/api/cart',
      orders: '/api/orders',
      users: '/api/users',
      reviews: '/api/reviews',
      wishlist: '/api/wishlist',
      addresses: '/api/addresses',
      payments: '/api/payments',
      admin: '/api/admin',
      reports: '/api/reports',
      search: '/api/search'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`E-commerce API running on port ${PORT}`);
});
