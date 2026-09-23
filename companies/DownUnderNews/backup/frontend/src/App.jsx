import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Layout
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';

// Public Pages
import Home from './pages/Home';
import ProductList from './pages/ProductList';
import ProductDetail from './pages/ProductDetail';
import Login from './pages/Login';
import Register from './pages/Register';

// User Pages
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import OrderDetail from './pages/OrderDetail';
import Profile from './pages/Profile';
import Wishlist from './pages/Wishlist';
import Addresses from './pages/Addresses';
import PaymentMethods from './pages/PaymentMethods';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';
import AdminProducts from './pages/admin/Products';
import AdminCategories from './pages/admin/Categories';
import AdminOrders from './pages/admin/Orders';
import AdminUsers from './pages/admin/Users';
import AdminSystemInfo from './pages/admin/SystemInfo';
import AdminLogs from './pages/admin/Logs';
import AdminBackup from './pages/admin/Backup';
import AdminReports from './pages/admin/Reports';
import AdminUserSearch from './pages/admin/UserSearch';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Public Routes */}
        <Route index element={<Home />} />
        <Route path="products" element={<ProductList />} />
        <Route path="products/:id" element={<ProductDetail />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />

        {/* Protected User Routes */}
        <Route path="cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
        <Route path="checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
        <Route path="orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
        <Route path="orders/:id" element={<ProtectedRoute><OrderDetail /></ProtectedRoute>} />
        <Route path="profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="wishlist" element={<ProtectedRoute><Wishlist /></ProtectedRoute>} />
        <Route path="addresses" element={<ProtectedRoute><Addresses /></ProtectedRoute>} />
        <Route path="payment-methods" element={<ProtectedRoute><PaymentMethods /></ProtectedRoute>} />

        {/* Admin Routes */}
        <Route path="admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
        <Route path="admin/products" element={<AdminRoute><AdminProducts /></AdminRoute>} />
        <Route path="admin/categories" element={<AdminRoute><AdminCategories /></AdminRoute>} />
        <Route path="admin/orders" element={<AdminRoute><AdminOrders /></AdminRoute>} />
        <Route path="admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
        <Route path="admin/system-info" element={<AdminRoute><AdminSystemInfo /></AdminRoute>} />
        <Route path="admin/logs" element={<AdminRoute><AdminLogs /></AdminRoute>} />
        <Route path="admin/backup" element={<AdminRoute><AdminBackup /></AdminRoute>} />
        <Route path="admin/reports" element={<AdminRoute><AdminReports /></AdminRoute>} />
        <Route path="admin/user-search" element={<AdminRoute><AdminUserSearch /></AdminRoute>} />

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;
