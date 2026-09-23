import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { productService, categoryService } from '../api/services';
import { FaArrowRight } from 'react-icons/fa';

export default function Home() {
  const { data: productsData } = useQuery('featured-products', () =>
    productService.getAll({ limit: 8 })
  );

  const { data: categoriesData } = useQuery('categories', categoryService.getAll);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white rounded-2xl p-12">
        <div className="max-w-3xl">
          <h1 className="text-5xl font-bold mb-4">
            Welcome to E-Shop
          </h1>
          <p className="text-xl mb-8">
            Discover amazing products at great prices. Shop now and enjoy fast delivery!
          </p>
          <Link to="/products" className="inline-flex items-center space-x-2 bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            <span>Shop Now</span>
            <FaArrowRight />
          </Link>
        </div>
      </section>

      {/* Categories Section */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Shop by Category</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {categoriesData?.data?.map((category) => (
            <Link
              key={category.id}
              to={`/products?category=${category.id}`}
              className="card hover:shadow-lg transition-shadow text-center"
            >
              <h3 className="font-semibold text-lg">{category.name}</h3>
              <p className="text-gray-600 text-sm mt-2">{category.description}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Products */}
      <section>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold">Featured Products</h2>
          <Link to="/products" className="text-primary-600 hover:text-primary-700 font-semibold">
            View All →
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {productsData?.data?.products?.map((product) => (
            <Link
              key={product.id}
              to={`/products/${product.id}`}
              className="card hover:shadow-lg transition-shadow"
            >
              <div className="aspect-square bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <span className="text-gray-400 text-4xl">📦</span>
                )}
              </div>
              <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
              <p className="text-primary-600 font-bold text-xl">
                ${product.price}
              </p>
              <p className="text-gray-600 text-sm mt-2">
                {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8 py-12">
        <div className="text-center">
          <div className="text-4xl mb-4">🚚</div>
          <h3 className="font-bold text-lg mb-2">Fast Delivery</h3>
          <p className="text-gray-600">Get your products delivered quickly and safely</p>
        </div>
        <div className="text-center">
          <div className="text-4xl mb-4">🔒</div>
          <h3 className="font-bold text-lg mb-2">Secure Payment</h3>
          <p className="text-gray-600">Shop with confidence using our secure payment system</p>
        </div>
        <div className="text-center">
          <div className="text-4xl mb-4">💯</div>
          <h3 className="font-bold text-lg mb-2">Quality Products</h3>
          <p className="text-gray-600">We ensure the best quality for all our products</p>
        </div>
      </section>
    </div>
  );
}
