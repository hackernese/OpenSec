# E-Commerce Frontend

Modern React-based frontend for the intentionally vulnerable e-commerce application.

## Features

- 🛍️ Full e-commerce functionality (browse, cart, checkout, orders)
- 🔐 User authentication and authorization
- 👤 User profile and account management
- ❤️ Wishlist functionality
- 📦 Order tracking
- 💳 Payment method management
- 📍 Address book
- ⭐ Product reviews and ratings
- 🔧 Admin dashboard with all vulnerable endpoints
- 📱 Responsive design with Tailwind CSS

## Technology Stack

- React 18
- React Router v6 (routing)
- React Query (data fetching/caching)
- Zustand (state management)
- Axios (HTTP client)
- React Hook Form (form validation)
- React Toastify (notifications)
- Tailwind CSS (styling)
- Vite (build tool)

## Setup

### With Docker
```bash
# Already included in main docker-compose.yml
docker-compose up -d
```

Frontend will be available at http://localhost:5173

### Manual Setup
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── axios.js          # Axios configuration
│   │   └── services.js       # API service functions
│   ├── components/
│   │   ├── Layout.jsx        # Main layout component
│   │   ├── Navbar.jsx        # Navigation bar
│   │   ├── Footer.jsx        # Footer component
│   │   ├── ProtectedRoute.jsx # Auth guard
│   │   └── AdminRoute.jsx    # Admin guard
│   ├── pages/
│   │   ├── Home.jsx          # Homepage
│   │   ├── Login.jsx         # Login page
│   │   ├── Register.jsx      # Registration page
│   │   ├── ProductList.jsx   # Product listing with filters
│   │   ├── ProductDetail.jsx # Product details with reviews
│   │   ├── Cart.jsx          # Shopping cart
│   │   ├── Checkout.jsx      # Checkout process
│   │   ├── Orders.jsx        # Order history
│   │   ├── OrderDetail.jsx   # Single order details
│   │   ├── Profile.jsx       # User profile
│   │   ├── Wishlist.jsx      # Wishlist page
│   │   ├── Addresses.jsx     # Address management
│   │   ├── PaymentMethods.jsx # Payment methods
│   │   └── admin/
│   │       ├── Dashboard.jsx         # Admin dashboard
│   │       ├── Products.jsx          # Product management
│   │       ├── Categories.jsx        # Category management
│   │       ├── Orders.jsx            # Order management
│   │       ├── Users.jsx             # User management
│   │       ├── SystemInfo.jsx        # OS Command Injection UI
│   │       ├── Logs.jsx              # Log export UI
│   │       ├── Backup.jsx            # Backup UI
│   │       ├── Reports.jsx           # XXE Injection UI
│   │       └── UserSearch.jsx        # XPath Injection UI
│   ├── store/
│   │   ├── authStore.js      # Authentication state
│   │   └── cartStore.js      # Cart state
│   ├── App.jsx               # Main app component with routes
│   ├── main.jsx              # Entry point
│   └── index.css             # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── Dockerfile
```

## Pages & Features

### Public Pages
- **Home** - Hero section, featured products, categories
- **Products** - Product listing with search, filters, pagination
- **Product Detail** - Full product info, reviews, add to cart/wishlist
- **Login** - User authentication
- **Register** - New user registration

### User Pages (Protected)
- **Cart** - View/modify cart, proceed to checkout
- **Checkout** - Select address, create order
- **Orders** - Order history list
- **Order Detail** - View order details and status
- **Profile** - Update user information, change password
- **Wishlist** - Manage wishlist items
- **Addresses** - CRUD operations for addresses
- **Payment Methods** - Manage payment methods

### Admin Pages (Admin Only)
- **Dashboard** - Overview with statistics
- **Products** - Create/update/delete products
- **Categories** - Manage categories
- **Orders** - View and update order status
- **Users** - View all users
- **System Info** - 🔴 OS Command Injection interface
- **Logs** - 🔴 Log export with command injection
- **Backup** - 🔴 Database backup with command injection
- **Reports** - 🔴 XXE injection interface
- **User Search** - 🔴 XPath injection interface

## API Integration

All API endpoints are integrated through the `services.js` file:

```javascript
import api from './services';

// Example usage
const products = await api.products.getAll();
const cart = await api.cart.getCart();
const order = await api.orders.create(orderData);
```

## State Management

### Authentication (Zustand + Persist)
```javascript
const { token, user, isAuthenticated, isAdmin, setAuth, logout } = useAuthStore();
```

### Cart (Zustand)
```javascript
const { cartCount, setCartCount, incrementCart } = useCartStore();
```

### Data Fetching (React Query)
```javascript
const { data, isLoading, error } = useQuery('products', fetchProducts);
const mutation = useMutation(createProduct);
```

## Styling

Tailwind CSS with custom configuration:
- Primary color scheme (blue)
- Custom component classes (.btn-primary, .card, .input-field)
- Responsive design
- Custom scrollbars
- Hover effects

## Environment Variables

Create `.env` file (optional):
```
VITE_API_URL=http://localhost:3000
```

## Build & Deploy

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## Vulnerability Testing UI

The admin panel includes user-friendly interfaces for testing all vulnerabilities:

1. **SQL Injection** - Product search with query builder
2. **OS Command Injection** - System info, log export, backup forms
3. **XXE Injection** - XML upload forms for sales reports and product import
4. **XPath Injection** - User search with query builder

## Security Notes

⚠️ This frontend is designed to interact with an intentionally vulnerable API. It includes:
- No client-side input sanitization (to demonstrate server-side vulnerabilities)
- Direct passthrough of user input to vulnerable endpoints
- Admin interfaces specifically designed to exploit vulnerabilities

Never use this in production or with real user data!

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

This is an educational project. Contributions should maintain the intentionally vulnerable nature while improving the user experience for security testing.
