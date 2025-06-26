from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pymongo import MongoClient
import uuid
from datetime import datetime

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.ecommerce_db

# Collections
products_collection = db.products
cart_collection = db.cart
orders_collection = db.orders

# Pydantic models
class Product(BaseModel):
    id: str
    name: str
    price: float
    description: str
    image: str
    category: str
    stock: int
    rating: float

class CartItem(BaseModel):
    id: str
    product_id: str
    name: str
    price: float
    image: str
    quantity: int

class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int

class Order(BaseModel):
    id: str
    items: List[OrderItem]
    total: float
    customer_email: str
    status: str
    created_at: datetime

# Initialize sample products
def init_sample_products():
    if products_collection.count_documents({}) == 0:
        sample_products = [
            {
                "id": str(uuid.uuid4()),
                "name": "Premium Wireless Headphones",
                "price": 299.99,
                "description": "High-quality wireless headphones with noise cancellation and premium sound quality.",
                "image": "https://images.unsplash.com/photo-1498049794561-7780e7231661",
                "category": "Electronics",
                "stock": 50,
                "rating": 4.8
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Smart Arduino Development Kit",
                "price": 89.99,
                "description": "Complete Arduino development kit perfect for beginners and professionals.",
                "image": "https://images.unsplash.com/photo-1603732551658-5fabbafa84eb",
                "category": "Electronics",
                "stock": 30,
                "rating": 4.6
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Circuit Board Components Set",
                "price": 149.99,
                "description": "Professional circuit board components set for electronics enthusiasts.",
                "image": "https://images.pexels.com/photos/163100/circuit-circuit-board-resistor-computer-163100.jpeg",
                "category": "Electronics",
                "stock": 25,
                "rating": 4.5
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Designer Handbag Collection",
                "price": 199.99,
                "description": "Elegant designer handbag perfect for shopping and daily use.",
                "image": "https://images.unsplash.com/photo-1483985988355-763728e1935b",
                "category": "Fashion",
                "stock": 40,
                "rating": 4.7
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Premium Yellow Tracksuit",
                "price": 129.99,
                "description": "Comfortable and stylish tracksuit perfect for sports and casual wear.",
                "image": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f",
                "category": "Fashion",
                "stock": 35,
                "rating": 4.4
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Stylish Urban Outfit",
                "price": 179.99,
                "description": "Modern urban outfit perfect for everyday style and comfort.",
                "image": "https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg",
                "category": "Fashion",
                "stock": 28,
                "rating": 4.6
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Luxury Green Armchair",
                "price": 899.99,
                "description": "Elegant green armchair with premium cushioning for your living room.",
                "image": "https://images.unsplash.com/photo-1579656592043-a20e25a4aa4b",
                "category": "Home & Living",
                "stock": 15,
                "rating": 4.9
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Modern Home Organization Set",
                "price": 79.99,
                "description": "Complete home organization solution with modern design elements.",
                "image": "https://images.pexels.com/photos/5531747/pexels-photo-5531747.jpeg",
                "category": "Home & Living",
                "stock": 20,
                "rating": 4.3
            }
        ]
        products_collection.insert_many(sample_products)

# Initialize sample products on startup
init_sample_products()

# API Routes
@app.get("/api/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    products = list(products_collection.find(query, {"_id": 0}))
    return products

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = products_collection.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/categories")
async def get_categories():
    categories = products_collection.distinct("category")
    return categories

@app.post("/api/cart/add")
async def add_to_cart(cart_item: CartItem):
    # Check if item already exists in cart
    existing_item = cart_collection.find_one({"product_id": cart_item.product_id})
    
    if existing_item:
        # Update quantity
        new_quantity = existing_item["quantity"] + cart_item.quantity
        cart_collection.update_one(
            {"product_id": cart_item.product_id},
            {"$set": {"quantity": new_quantity}}
        )
    else:
        # Add new item
        cart_collection.insert_one(cart_item.dict())
    
    return {"message": "Item added to cart successfully"}

@app.get("/api/cart")
async def get_cart():
    cart_items = list(cart_collection.find({}, {"_id": 0}))
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    return {"items": cart_items, "total": total}

@app.put("/api/cart/update/{product_id}")
async def update_cart_item(product_id: str, quantity: int):
    if quantity <= 0:
        cart_collection.delete_one({"product_id": product_id})
        return {"message": "Item removed from cart"}
    else:
        cart_collection.update_one(
            {"product_id": product_id},
            {"$set": {"quantity": quantity}}
        )
        return {"message": "Cart updated successfully"}

@app.delete("/api/cart/remove/{product_id}")
async def remove_from_cart(product_id: str):
    cart_collection.delete_one({"product_id": product_id})
    return {"message": "Item removed from cart"}

@app.delete("/api/cart/clear")
async def clear_cart():
    cart_collection.delete_many({})
    return {"message": "Cart cleared successfully"}

@app.post("/api/orders")
async def create_order(order: Order):
    order_dict = order.dict()
    order_dict["id"] = str(uuid.uuid4())
    order_dict["created_at"] = datetime.now()
    order_dict["status"] = "pending"
    
    orders_collection.insert_one(order_dict)
    
    # Clear cart after order
    cart_collection.delete_many({})
    
    return {"message": "Order created successfully", "order_id": order_dict["id"]}

@app.get("/api/orders")
async def get_orders():
    orders = list(orders_collection.find({}, {"_id": 0}))
    return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)