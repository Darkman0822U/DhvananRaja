import requests
import json
import unittest
import os
import sys

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"')
            break

# Ensure we have a valid backend URL
if not BACKEND_URL:
    print("Error: Could not find REACT_APP_BACKEND_URL in frontend/.env")
    sys.exit(1)

# Add /api prefix to all endpoints
API_URL = f"{BACKEND_URL}/api"
print(f"Testing backend API at: {API_URL}")

class ECommerceBackendTests(unittest.TestCase):
    
    def setUp(self):
        # Clear the cart before each test to ensure a clean state
        self.clear_cart()
    
    def tearDown(self):
        # Clean up after tests
        self.clear_cart()
    
    def clear_cart(self):
        """Helper method to clear the cart"""
        response = requests.delete(f"{API_URL}/cart/clear")
        self.assertEqual(response.status_code, 200)
    
    def test_get_products(self):
        """Test the GET /api/products endpoint"""
        print("\n--- Testing Product Catalog API ---")
        
        # Test getting all products
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200)
        
        products = response.json()
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)
        
        # Verify product structure
        product = products[0]
        required_fields = ['id', 'name', 'price', 'description', 'image', 'category', 'stock', 'rating']
        for field in required_fields:
            self.assertIn(field, product)
        
        print(f"✅ Successfully retrieved {len(products)} products with all required fields")
        
        # Test category filtering
        categories = ['Electronics', 'Fashion', 'Home & Living']
        for category in categories:
            response = requests.get(f"{API_URL}/products?category={category}")
            self.assertEqual(response.status_code, 200)
            
            filtered_products = response.json()
            self.assertIsInstance(filtered_products, list)
            
            # Verify all products are in the requested category
            for product in filtered_products:
                self.assertEqual(product['category'], category)
            
            print(f"✅ Category filter for '{category}' returned {len(filtered_products)} products")
        
        # Test search functionality
        search_terms = ['headphones', 'arduino', 'elegant']
        for term in search_terms:
            response = requests.get(f"{API_URL}/products?search={term}")
            self.assertEqual(response.status_code, 200)
            
            search_results = response.json()
            self.assertIsInstance(search_results, list)
            
            # Verify search results contain the term in name or description
            if len(search_results) > 0:
                found = False
                for product in search_results:
                    if (term.lower() in product['name'].lower() or 
                        term.lower() in product['description'].lower()):
                        found = True
                        break
                self.assertTrue(found, f"Search term '{term}' not found in results")
                
                print(f"✅ Search for '{term}' returned {len(search_results)} products")
            else:
                print(f"⚠️ Search for '{term}' returned no results")
    
    def test_get_categories(self):
        """Test the GET /api/categories endpoint"""
        print("\n--- Testing Categories API ---")
        
        response = requests.get(f"{API_URL}/categories")
        self.assertEqual(response.status_code, 200)
        
        categories = response.json()
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        
        # Verify expected categories are present
        expected_categories = ['Electronics', 'Fashion', 'Home & Living']
        for category in expected_categories:
            self.assertIn(category, categories)
        
        print(f"✅ Successfully retrieved {len(categories)} categories: {', '.join(categories)}")
    
    def test_shopping_cart(self):
        """Test all Shopping Cart API operations"""
        print("\n--- Testing Shopping Cart API ---")
        
        # First, get a product to add to cart
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200)
        
        products = response.json()
        self.assertGreater(len(products), 0)
        
        test_product = products[0]
        
        # 1. Test adding item to cart
        cart_item = {
            "id": "test_cart_item_id",
            "product_id": test_product['id'],
            "name": test_product['name'],
            "price": test_product['price'],
            "image": test_product['image'],
            "quantity": 2
        }
        
        response = requests.post(f"{API_URL}/cart/add", json=cart_item)
        self.assertEqual(response.status_code, 200)
        print("✅ Successfully added item to cart")
        
        # 2. Test getting cart
        response = requests.get(f"{API_URL}/cart")
        self.assertEqual(response.status_code, 200)
        
        cart = response.json()
        self.assertIn('items', cart)
        self.assertIn('total', cart)
        self.assertEqual(len(cart['items']), 1)
        self.assertEqual(cart['items'][0]['product_id'], test_product['id'])
        self.assertEqual(cart['items'][0]['quantity'], 2)
        self.assertEqual(cart['total'], test_product['price'] * 2)
        
        print("✅ Successfully retrieved cart with correct items and total")
        
        # 3. Test updating item quantity
        response = requests.put(f"{API_URL}/cart/update/{test_product['id']}?quantity=3")
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = requests.get(f"{API_URL}/cart")
        self.assertEqual(response.status_code, 200)
        
        cart = response.json()
        self.assertEqual(cart['items'][0]['quantity'], 3)
        self.assertEqual(cart['total'], test_product['price'] * 3)
        
        print("✅ Successfully updated item quantity in cart")
        
        # 4. Test removing specific item
        response = requests.delete(f"{API_URL}/cart/remove/{test_product['id']}")
        self.assertEqual(response.status_code, 200)
        
        # Verify removal
        response = requests.get(f"{API_URL}/cart")
        self.assertEqual(response.status_code, 200)
        
        cart = response.json()
        self.assertEqual(len(cart['items']), 0)
        self.assertEqual(cart['total'], 0)
        
        print("✅ Successfully removed item from cart")
        
        # 5. Test adding multiple items and clearing cart
        # Add first item
        response = requests.post(f"{API_URL}/cart/add", json=cart_item)
        self.assertEqual(response.status_code, 200)
        
        # Add second item (if available)
        if len(products) > 1:
            second_product = products[1]
            second_cart_item = {
                "id": "test_cart_item_id2",
                "product_id": second_product['id'],
                "name": second_product['name'],
                "price": second_product['price'],
                "image": second_product['image'],
                "quantity": 1
            }
            
            response = requests.post(f"{API_URL}/cart/add", json=second_cart_item)
            self.assertEqual(response.status_code, 200)
        
        # Verify multiple items
        response = requests.get(f"{API_URL}/cart")
        self.assertEqual(response.status_code, 200)
        
        cart = response.json()
        self.assertGreaterEqual(len(cart['items']), 1)
        
        # Test clearing cart
        response = requests.delete(f"{API_URL}/cart/clear")
        self.assertEqual(response.status_code, 200)
        
        # Verify cart is empty
        response = requests.get(f"{API_URL}/cart")
        self.assertEqual(response.status_code, 200)
        
        cart = response.json()
        self.assertEqual(len(cart['items']), 0)
        self.assertEqual(cart['total'], 0)
        
        print("✅ Successfully cleared cart")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)