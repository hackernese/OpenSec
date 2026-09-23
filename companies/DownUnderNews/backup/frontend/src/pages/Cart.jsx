import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { toast } from 'react-toastify';
import { cartService } from '../api/services';
import { useCartStore } from '../store/cartStore';
import { FaTrash } from 'react-icons/fa';

export default function Cart() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setCartCount } = useCartStore();

  const { data: cartData, isLoading } = useQuery('cart', cartService.getCart, {
    onSuccess: (data) => {
      setCartCount(data.data.itemCount || 0);
    },
  });

  const updateItemMutation = useMutation(
    ({ productId, quantity }) => cartService.updateItem(productId, { quantity }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('cart');
        toast.success('Cart updated');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to update cart');
      },
    }
  );

  const removeItemMutation = useMutation(
    (productId) => cartService.removeItem(productId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('cart');
        toast.success('Item removed from cart');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to remove item');
      },
    }
  );

  const clearCartMutation = useMutation(
    () => cartService.clearCart(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('cart');
        setCartCount(0);
        toast.success('Cart cleared');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to clear cart');
      },
    }
  );

  const handleUpdateQuantity = (productId, newQuantity) => {
    if (newQuantity < 1) return;
    updateItemMutation.mutate({ productId, quantity: newQuantity });
  };

  const handleRemoveItem = (productId) => {
    removeItemMutation.mutate(productId);
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading cart...</div>;
  }

  const cart = cartData?.data;
  const items = cart?.items || [];
  const total = cart?.total || 0;

  if (items.length === 0) {
    return (
      <div className="max-w-2xl mx-auto card text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Your Cart is Empty</h2>
        <p className="text-gray-600 mb-6">Add some products to get started!</p>
        <Link to="/products" className="btn-primary inline-block">
          Shop Now
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Shopping Cart</h1>
        <button
          onClick={() => clearCartMutation.mutate()}
          disabled={clearCartMutation.isLoading}
          className="btn-danger"
        >
          Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {items.map((item) => (
            <div key={item.product_id} className="card flex items-center space-x-4">
              <div className="w-24 h-24 bg-gray-200 rounded flex-shrink-0 flex items-center justify-center">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-full h-full object-cover rounded"
                  />
                ) : (
                  <span className="text-gray-400 text-3xl">📦</span>
                )}
              </div>

              <div className="flex-grow">
                <Link
                  to={`/products/${item.product_id}`}
                  className="font-semibold text-lg hover:text-primary-600"
                >
                  {item.name}
                </Link>
                <p className="text-primary-600 font-bold mt-1">${item.price}</p>
                <p className="text-sm text-gray-600">
                  Available: {item.stock}
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleUpdateQuantity(item.product_id, item.quantity - 1)}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                  disabled={updateItemMutation.isLoading}
                >
                  -
                </button>
                <span className="px-4 py-1 border rounded">{item.quantity}</span>
                <button
                  onClick={() => handleUpdateQuantity(item.product_id, item.quantity + 1)}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
                  disabled={item.quantity >= item.stock || updateItemMutation.isLoading}
                >
                  +
                </button>
              </div>

              <div className="text-right">
                <p className="font-bold text-lg">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>
                <button
                  onClick={() => handleRemoveItem(item.product_id)}
                  disabled={removeItemMutation.isLoading}
                  className="text-red-600 hover:text-red-700 mt-2"
                >
                  <FaTrash />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="card sticky top-20">
            <h2 className="text-2xl font-bold mb-6">Order Summary</h2>

            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-semibold">${total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Shipping</span>
                <span className="font-semibold">Free</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tax</span>
                <span className="font-semibold">${(total * 0.1).toFixed(2)}</span>
              </div>
              <hr />
              <div className="flex justify-between text-xl">
                <span className="font-bold">Total</span>
                <span className="font-bold text-primary-600">
                  ${(total * 1.1).toFixed(2)}
                </span>
              </div>
            </div>

            <button
              onClick={() => navigate('/checkout')}
              className="w-full btn-primary text-lg"
            >
              Proceed to Checkout
            </button>

            <Link to="/products" className="block text-center mt-4 text-primary-600 hover:text-primary-700">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
