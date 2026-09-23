import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import { productService, cartService, reviewService, wishlistService } from '../api/services';
import { useAuthStore } from '../store/authStore';
import { useCartStore } from '../store/cartStore';
import { FaHeart, FaRegHeart, FaStar } from 'react-icons/fa';

export default function ProductDetail() {
  const { id } = useParams();
  const { isAuthenticated } = useAuthStore();
  const { incrementCart } = useCartStore();
  const queryClient = useQueryClient();
  const [quantity, setQuantity] = useState(1);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');

  const { data: productData, isLoading } = useQuery(
    ['product', id],
    () => productService.getById(id)
  );

  const { data: reviewsData } = useQuery(
    ['reviews', id],
    () => reviewService.getProductReviews(id)
  );

  const addToCartMutation = useMutation(
    (data) => cartService.addItem(data),
    {
      onSuccess: () => {
        toast.success('Added to cart!');
        incrementCart();
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to add to cart');
      },
    }
  );

  const addToWishlistMutation = useMutation(
    (data) => wishlistService.add(data),
    {
      onSuccess: () => {
        toast.success('Added to wishlist!');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to add to wishlist');
      },
    }
  );

  const createReviewMutation = useMutation(
    (data) => reviewService.create(data),
    {
      onSuccess: () => {
        toast.success('Review submitted!');
        setReviewComment('');
        setReviewRating(5);
        queryClient.invalidateQueries(['reviews', id]);
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to submit review');
      },
    }
  );

  const handleAddToCart = () => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart');
      return;
    }
    addToCartMutation.mutate({ productId: id, quantity });
  };

  const handleAddToWishlist = () => {
    if (!isAuthenticated) {
      toast.error('Please login to add items to wishlist');
      return;
    }
    addToWishlistMutation.mutate({ productId: id });
  };

  const handleSubmitReview = (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      toast.error('Please login to submit a review');
      return;
    }
    createReviewMutation.mutate({
      productId: id,
      rating: reviewRating,
      comment: reviewComment,
    });
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  const product = productData?.data;

  return (
    <div className="max-w-7xl mx-auto space-y-12">
      {/* Product Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Product Image */}
        <div className="bg-gray-200 rounded-lg aspect-square flex items-center justify-center">
          {product?.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover rounded-lg"
            />
          ) : (
            <span className="text-gray-400 text-9xl">📦</span>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <h1 className="text-4xl font-bold mb-2">{product?.name}</h1>
            <p className="text-gray-600">{product?.category_name}</p>
          </div>

          <div className="flex items-baseline space-x-4">
            <p className="text-4xl font-bold text-primary-600">
              ${product?.price}
            </p>
            <p className={`text-lg ${product?.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {product?.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
            </p>
          </div>

          <p className="text-gray-700 leading-relaxed">{product?.description}</p>

          {/* Quantity Selector */}
          <div className="flex items-center space-x-4">
            <label className="font-semibold">Quantity:</label>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
              >
                -
              </button>
              <span className="px-4 py-1 border rounded">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(product?.stock || 1, quantity + 1))}
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
              >
                +
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleAddToCart}
              disabled={product?.stock === 0 || addToCartMutation.isLoading}
              className="flex-1 btn-primary disabled:opacity-50"
            >
              {addToCartMutation.isLoading ? 'Adding...' : 'Add to Cart'}
            </button>
            <button
              onClick={handleAddToWishlist}
              disabled={addToWishlistMutation.isLoading}
              className="btn-secondary"
            >
              <FaHeart className="text-xl" />
            </button>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="space-y-6">
        <h2 className="text-3xl font-bold">Customer Reviews</h2>

        {/* Submit Review Form */}
        {isAuthenticated && (
          <form onSubmit={handleSubmitReview} className="card space-y-4">
            <h3 className="text-xl font-semibold">Write a Review</h3>
            <div>
              <label className="block mb-2">Rating</label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setReviewRating(star)}
                    className="text-2xl"
                  >
                    <FaStar
                      className={star <= reviewRating ? 'text-yellow-400' : 'text-gray-300'}
                    />
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block mb-2">Comment</label>
              <textarea
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                className="input-field"
                rows="4"
                placeholder="Share your thoughts about this product..."
              />
            </div>
            <button
              type="submit"
              disabled={createReviewMutation.isLoading}
              className="btn-primary"
            >
              {createReviewMutation.isLoading ? 'Submitting...' : 'Submit Review'}
            </button>
          </form>
        )}

        {/* Reviews List */}
        <div className="space-y-4">
          {reviewsData?.data?.map((review) => (
            <div key={review.id} className="card">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold">
                    {review.first_name} {review.last_name}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    {[...Array(5)].map((_, i) => (
                      <FaStar
                        key={i}
                        className={i < review.rating ? 'text-yellow-400' : 'text-gray-300'}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-sm text-gray-500">
                  {new Date(review.created_at).toLocaleDateString()}
                </p>
              </div>
              {review.comment && (
                <p className="text-gray-700">{review.comment}</p>
              )}
            </div>
          ))}
          {reviewsData?.data?.length === 0 && (
            <p className="text-gray-600 text-center py-8">No reviews yet. Be the first to review!</p>
          )}
        </div>
      </div>
    </div>
  );
}
