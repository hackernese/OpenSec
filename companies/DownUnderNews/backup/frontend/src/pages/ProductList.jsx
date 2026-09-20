import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { productService, categoryService } from '../api/services';
import { FaFilter } from 'react-icons/fa';

export default function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    query: searchParams.get('query') || '',
    category: searchParams.get('category') || '',
    minPrice: searchParams.get('minPrice') || '',
    maxPrice: searchParams.get('maxPrice') || '',
    page: parseInt(searchParams.get('page')) || 1,
  });

  const { data: productsData, isLoading } = useQuery(
    ['products', filters],
    () => filters.query 
      ? productService.search(filters)
      : productService.getAll({ ...filters, limit: 20 })
  );

  const { data: categoriesData } = useQuery('categories', categoryService.getAll);

  useEffect(() => {
    const params = {};
    Object.keys(filters).forEach(key => {
      if (filters[key]) params[key] = filters[key];
    });
    setSearchParams(params);
  }, [filters, setSearchParams]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
      {/* Filters Sidebar */}
      <div className="col-span-1">
        <div className="card sticky top-20">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <FaFilter className="mr-2" /> Filters
          </h3>

          {/* Category Filter */}
          <div className="mb-6">
            <h4 className="font-semibold mb-2">Category</h4>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="input-field"
            >
              <option value="">All Categories</option>
              {categoriesData?.data?.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Price Range */}
          <div className="mb-6">
            <h4 className="font-semibold mb-2">Price Range</h4>
            <div className="space-y-2">
              <input
                type="number"
                placeholder="Min Price"
                value={filters.minPrice}
                onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                className="input-field"
              />
              <input
                type="number"
                placeholder="Max Price"
                value={filters.maxPrice}
                onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                className="input-field"
              />
            </div>
          </div>

          <button
            onClick={() => setFilters({
              query: '', category: '', minPrice: '', maxPrice: '', page: 1
            })}
            className="btn-secondary w-full"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Products Grid */}
      <div className="col-span-3">
        {isLoading ? (
          <div className="text-center py-12">Loading products...</div>
        ) : productsData?.data?.products?.length > 0 || productsData?.data?.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {(productsData?.data?.products || productsData?.data)?.map((product) => (
                <Link
                  key={product.id}
                  to={`/products/${product.id}`}
                  className="card hover:shadow-lg transition-shadow"
                >
                  <div className="aspect-square bg-gray-200 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
                    {product.image_url ? (
                      <img
                        src={product.image_url}
                        alt={product.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-gray-400 text-5xl">📦</span>
                    )}
                  </div>
                  <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                    {product.name}
                  </h3>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {product.description}
                  </p>
                  <div className="flex justify-between items-center">
                    <p className="text-primary-600 font-bold text-xl">
                      ${product.price}
                    </p>
                    <p className={`text-sm ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                    </p>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {productsData?.data?.pagination && (
              <div className="flex justify-center mt-8 space-x-2">
                {Array.from({ length: productsData.data.pagination.totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => handleFilterChange('page', page)}
                    className={`px-4 py-2 rounded-lg ${
                      filters.page === page
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12 card">
            <p className="text-gray-600 text-lg">No products found</p>
          </div>
        )}
      </div>
    </div>
  );
}
