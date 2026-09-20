export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4">E-Shop</h3>
            <p className="text-gray-400">
              Your one-stop shop for all your needs.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Shop</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/products" className="hover:text-white">All Products</a></li>
              <li><a href="/products?category=1" className="hover:text-white">Electronics</a></li>
              <li><a href="/products?category=2" className="hover:text-white">Clothing</a></li>
              <li><a href="/products?category=3" className="hover:text-white">Books</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Customer Service</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-white">Contact Us</a></li>
              <li><a href="#" className="hover:text-white">Shipping Policy</a></li>
              <li><a href="#" className="hover:text-white">Returns</a></li>
              <li><a href="#" className="hover:text-white">FAQ</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Account</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/profile" className="hover:text-white">My Account</a></li>
              <li><a href="/orders" className="hover:text-white">Order History</a></li>
              <li><a href="/wishlist" className="hover:text-white">Wishlist</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2024 E-Shop. All rights reserved.</p>
          <p className="mt-2 text-sm text-yellow-500">
            ⚠️ This is an intentionally vulnerable application for security testing purposes only
          </p>
        </div>
      </div>
    </footer>
  );
}
