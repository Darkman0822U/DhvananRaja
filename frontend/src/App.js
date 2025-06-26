import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCart, setShowCart] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Fetch products
  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await fetch(`${BACKEND_URL}/api/products?${params}`);
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch categories
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  // Fetch cart
  const fetchCart = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/cart`);
      const data = await response.json();
      setCart(data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    }
  };

  // Add to cart
  const addToCart = async (product) => {
    try {
      const cartItem = {
        id: product.id,
        product_id: product.id,
        name: product.name,
        price: product.price,
        image: product.image,
        quantity: 1
      };

      await fetch(`${BACKEND_URL}/api/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cartItem),
      });

      fetchCart();
      // Show success message
      alert('Product added to cart!');
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  // Update cart item quantity
  const updateCartItem = async (productId, quantity) => {
    try {
      await fetch(`${BACKEND_URL}/api/cart/update/${productId}?quantity=${quantity}`, {
        method: 'PUT',
      });
      fetchCart();
    } catch (error) {
      console.error('Error updating cart:', error);
    }
  };

  // Remove from cart
  const removeFromCart = async (productId) => {
    try {
      await fetch(`${BACKEND_URL}/api/cart/remove/${productId}`, {
        method: 'DELETE',
      });
      fetchCart();
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  // Clear cart
  const clearCart = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/cart/clear`, {
        method: 'DELETE',
      });
      fetchCart();
    } catch (error) {
      console.error('Error clearing cart:', error);
    }
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    fetchProducts();
  };

  useEffect(() => {
    fetchProducts();
    fetchCategories();
    fetchCart();
  }, [selectedCategory]);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="logo">
              <h1 className="text-2xl md:text-3xl font-bold text-white">ShopHub</h1>
              <p className="text-blue-200 text-sm">Your Premium Shopping Destination</p>
            </div>
            
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="hidden md:flex items-center space-x-2">
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-4 py-2 rounded-lg border-0 focus:ring-2 focus:ring-blue-300 w-64"
              />
              <button
                type="submit"
                className="bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 font-medium"
              >
                Search
              </button>
            </form>

            {/* Cart Button */}
            <button
              onClick={() => setShowCart(!showCart)}
              className="cart-button"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l-2.5 5m0 0h12.5" />
              </svg>
              <span className="ml-2">Cart ({cart.items.length})</span>
              {cart.total > 0 && (
                <span className="ml-2 bg-yellow-400 text-blue-900 px-2 py-1 rounded-full text-sm font-bold">
                  ${cart.total.toFixed(2)}
                </span>
              )}
            </button>
          </div>

          {/* Mobile Search */}
          <form onSubmit={handleSearch} className="md:hidden mt-4 flex items-center space-x-2">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 rounded-lg border-0 focus:ring-2 focus:ring-blue-300"
            />
            <button
              type="submit"
              className="bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 font-medium"
            >
              Search
            </button>
          </form>
        </div>
      </header>

      {/* Categories Filter */}
      <div className="categories-filter">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('')}
              className={`category-chip ${selectedCategory === '' ? 'active' : ''}`}
            >
              All Products
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`category-chip ${selectedCategory === category ? 'active' : ''}`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="main-content">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Products Grid */}
            <div className="flex-1">
              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>Loading products...</p>
                </div>
              ) : (
                <>
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">
                      {selectedCategory || 'All Products'} 
                      <span className="text-gray-500 text-lg ml-2">({products.length} items)</span>
                    </h2>
                  </div>
                  
                  <div className="products-grid">
                    {products.map((product) => (
                      <div key={product.id} className="product-card">
                        <div className="product-image-container">
                          <img
                            src={product.image}
                            alt={product.name}
                            className="product-image"
                            onClick={() => setSelectedProduct(product)}
                          />
                          <div className="product-overlay">
                            <button
                              onClick={() => setSelectedProduct(product)}
                              className="overlay-button"
                            >
                              Quick View
                            </button>
                          </div>
                        </div>
                        
                        <div className="product-info">
                          <div className="product-category">{product.category}</div>
                          <h3 className="product-name">{product.name}</h3>
                          <p className="product-description">{product.description}</p>
                          
                          <div className="product-rating">
                            <div className="stars">
                              {[...Array(5)].map((_, i) => (
                                <span
                                  key={i}
                                  className={`star ${i < Math.floor(product.rating) ? 'filled' : ''}`}
                                >
                                  ★
                                </span>
                              ))}
                            </div>
                            <span className="rating-text">({product.rating})</span>
                          </div>
                          
                          <div className="product-footer">
                            <div className="product-price">${product.price}</div>
                            <button
                              onClick={() => addToCart(product)}
                              className="add-to-cart-btn"
                              disabled={product.stock === 0}
                            >
                              {product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
                            </button>
                          </div>
                          
                          <div className="stock-info">
                            {product.stock < 10 && product.stock > 0 && (
                              <span className="low-stock">Only {product.stock} left!</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

            {/* Shopping Cart Sidebar */}
            {showCart && (
              <div className="cart-sidebar">
                <div className="cart-header">
                  <h3 className="text-xl font-bold">Shopping Cart</h3>
                  <button
                    onClick={() => setShowCart(false)}
                    className="close-cart-btn"
                  >
                    ×
                  </button>
                </div>

                <div className="cart-content">
                  {cart.items.length === 0 ? (
                    <div className="empty-cart">
                      <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l-2.5 5m0 0h12.5" />
                      </svg>
                      <p className="text-gray-500">Your cart is empty</p>
                    </div>
                  ) : (
                    <>
                      <div className="cart-items">
                        {cart.items.map((item) => (
                          <div key={item.product_id} className="cart-item">
                            <img src={item.image} alt={item.name} className="cart-item-image" />
                            <div className="cart-item-details">
                              <h4 className="cart-item-name">{item.name}</h4>
                              <div className="cart-item-price">${item.price}</div>
                              <div className="quantity-controls">
                                <button
                                  onClick={() => updateCartItem(item.product_id, item.quantity - 1)}
                                  className="quantity-btn"
                                >
                                  -
                                </button>
                                <span className="quantity">{item.quantity}</span>
                                <button
                                  onClick={() => updateCartItem(item.product_id, item.quantity + 1)}
                                  className="quantity-btn"
                                >
                                  +
                                </button>
                              </div>
                            </div>
                            <button
                              onClick={() => removeFromCart(item.product_id)}
                              className="remove-item-btn"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>

                      <div className="cart-footer">
                        <div className="cart-total">
                          <div className="total-text">Total: ${cart.total.toFixed(2)}</div>
                        </div>
                        <div className="cart-actions">
                          <button onClick={clearCart} className="clear-cart-btn">
                            Clear Cart
                          </button>
                          <button className="checkout-btn">
                            Proceed to Checkout
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="modal-overlay" onClick={() => setSelectedProduct(null)}>
          <div className="product-modal" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setSelectedProduct(null)}
              className="modal-close-btn"
            >
              ×
            </button>
            
            <div className="modal-content">
              <div className="modal-image">
                <img src={selectedProduct.image} alt={selectedProduct.name} />
              </div>
              
              <div className="modal-details">
                <div className="product-category">{selectedProduct.category}</div>
                <h2 className="text-2xl font-bold mb-4">{selectedProduct.name}</h2>
                <p className="text-gray-600 mb-4">{selectedProduct.description}</p>
                
                <div className="product-rating mb-4">
                  <div className="stars">
                    {[...Array(5)].map((_, i) => (
                      <span
                        key={i}
                        className={`star ${i < Math.floor(selectedProduct.rating) ? 'filled' : ''}`}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                  <span className="rating-text">({selectedProduct.rating})</span>
                </div>
                
                <div className="price-section mb-6">
                  <div className="text-3xl font-bold text-blue-600">${selectedProduct.price}</div>
                  <div className="text-sm text-gray-500">In stock: {selectedProduct.stock} items</div>
                </div>
                
                <button
                  onClick={() => {
                    addToCart(selectedProduct);
                    setSelectedProduct(null);
                  }}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                  disabled={selectedProduct.stock === 0}
                >
                  {selectedProduct.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h3 className="text-xl font-bold text-white mb-4">ShopHub</h3>
            <p className="text-blue-200 mb-4">Your trusted e-commerce destination for quality products</p>
            <div className="flex justify-center space-x-6 text-blue-200">
              <a href="#" className="hover:text-white">About Us</a>
              <a href="#" className="hover:text-white">Contact</a>
              <a href="#" className="hover:text-white">Privacy Policy</a>
              <a href="#" className="hover:text-white">Terms of Service</a>
            </div>
            <div className="mt-6 pt-6 border-t border-blue-700">
              <p className="text-blue-300">&copy; 2025 ShopHub. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;