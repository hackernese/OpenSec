import api from './axios';

// Auth Services
export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/me'),
};

// Product Services
export const productService = {
  getAll: (params) => api.get('/products', { params }),
  search: (params) => api.get('/products/search', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};

// Category Services
export const categoryService = {
  getAll: () => api.get('/categories'),
  getById: (id) => api.get(`/categories/${id}`),
  create: (data) => api.post('/categories', data),
};

// Cart Services
export const cartService = {
  getCart: () => api.get('/cart'),
  addItem: (data) => api.post('/cart/items', data),
  updateItem: (productId, data) => api.put(`/cart/items/${productId}`, data),
  removeItem: (productId) => api.delete(`/cart/items/${productId}`),
  clearCart: () => api.delete('/cart'),
};

// Order Services
export const orderService = {
  getAll: () => api.get('/orders'),
  getById: (id) => api.get(`/orders/${id}`),
  create: (data) => api.post('/orders', data),
  updateStatus: (id, data) => api.patch(`/orders/${id}/status`, data),
};

// User Services
export const userService = {
  getAll: () => api.get('/users'),
  updateProfile: (data) => api.put('/users/profile', data),
  changePassword: (data) => api.put('/users/password', data),
};

// Review Services
export const reviewService = {
  getProductReviews: (productId) => api.get(`/reviews/product/${productId}`),
  create: (data) => api.post('/reviews', data),
  delete: (id) => api.delete(`/reviews/${id}`),
};

// Wishlist Services
export const wishlistService = {
  getAll: () => api.get('/wishlist'),
  add: (data) => api.post('/wishlist', data),
  remove: (productId) => api.delete(`/wishlist/${productId}`),
};

// Address Services
export const addressService = {
  getAll: () => api.get('/addresses'),
  create: (data) => api.post('/addresses', data),
  update: (id, data) => api.put(`/addresses/${id}`, data),
  delete: (id) => api.delete(`/addresses/${id}`),
};

// Payment Method Services
export const paymentService = {
  getAll: () => api.get('/payments/methods'),
  add: (data) => api.post('/payments/methods', data),
  delete: (id) => api.delete(`/payments/methods/${id}`),
};

// Admin Services
export const adminService = {
  // OS Command Injection endpoints
  systemInfo: (params) => api.get('/admin/system-info', { params }),
  exportLogs: (data) => api.post('/admin/export-logs', data),
  backup: (data) => api.post('/admin/backup', data),
  
  // XXE Injection endpoints
  uploadSalesReport: (data) => api.post('/reports/upload-sales', data),
  importProducts: (data) => api.post('/reports/import-products', data),
  
  // XPath Injection endpoint
  searchUsers: (params) => api.get('/search/users', { params }),
  getUsersXml: () => api.get('/search/users/xml'),
};

export default {
  auth: authService,
  products: productService,
  categories: categoryService,
  cart: cartService,
  orders: orderService,
  users: userService,
  reviews: reviewService,
  wishlist: wishlistService,
  addresses: addressService,
  payments: paymentService,
  admin: adminService,
};
