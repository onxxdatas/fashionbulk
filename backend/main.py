from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import hashlib
import json
import os

app = FastAPI(title="FashionBulk API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://salomyangi.netlify.app",
        "https://www.salomyangi.netlify.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ---------- In-memory DB (replace with real DB later) ----------

USERS = {
    "admin@fashionbulk.com": {
        "id": "u1",
        "name": "Admin",
        "email": "admin@fashionbulk.com",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
    }
}

PRODUCTS = [
    {"id": "p1", "name": "Classic White Tee", "category": "T-Shirts", "price": 4.50, "stock": 500, "min_order": 50, "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"},
    {"id": "p2", "name": "Slim Fit Jeans", "category": "Denim", "price": 12.00, "stock": 300, "min_order": 30, "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400"},
    {"id": "p3", "name": "Floral Summer Dress", "category": "Dresses", "price": 9.00, "stock": 200, "min_order": 20, "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400"},
    {"id": "p4", "name": "Wool Blend Jacket", "category": "Outerwear", "price": 25.00, "stock": 150, "min_order": 15, "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400"},
    {"id": "p5", "name": "Cargo Shorts", "category": "Shorts", "price": 6.50, "stock": 400, "min_order": 40, "image_url": "https://images.unsplash.com/photo-1591195853828-11db59a44f43?w=400"},
    {"id": "p6", "name": "Striped Polo Shirt", "category": "T-Shirts", "price": 5.50, "stock": 350, "min_order": 50, "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=400"},
]

ORDERS = []
TOKENS = {}  # token -> user_email

# ---------- Models ----------

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderRequest(BaseModel):
    items: List[OrderItem]
    shipping_address: str

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    min_order: int
    image_url: Optional[str] = ""

# ---------- Auth helpers ----------

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    email = TOKENS.get(token)
    if not email or email not in USERS:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return USERS[email]

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ---------- Auth routes ----------

@app.post("/auth/register", status_code=201)
def register(body: RegisterRequest):
    if body.email in USERS:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "email": body.email,
        "password_hash": hashlib.sha256(body.password.encode()).hexdigest(),
        "role": "buyer",
    }
    USERS[body.email] = user
    return {"message": "Registered successfully"}

@app.post("/auth/login")
def login(body: LoginRequest):
    user = USERS.get(body.email)
    if not user or user["password_hash"] != hashlib.sha256(body.password.encode()).hexdigest():
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = str(uuid.uuid4())
    TOKENS[token] = body.email
    return {"token": token, "name": user["name"], "role": user["role"]}

@app.post("/auth/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        TOKENS.pop(credentials.credentials, None)
    return {"message": "Logged out"}

# ---------- Product routes ----------

@app.get("/products")
def list_products(category: Optional[str] = None, search: Optional[str] = None):
    results = PRODUCTS.copy()
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if search:
        results = [p for p in results if search.lower() in p["name"].lower()]
    return results

@app.get("/products/{product_id}")
def get_product(product_id: str):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", status_code=201)
def create_product(body: ProductCreate, admin=Depends(require_admin)):
    product = {
        "id": str(uuid.uuid4()),
        **body.dict()
    }
    PRODUCTS.append(product)
    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: str, admin=Depends(require_admin)):
    global PRODUCTS
    PRODUCTS = [p for p in PRODUCTS if p["id"] != product_id]
    return {"message": "Deleted"}

@app.get("/categories")
def list_categories():
    cats = list({p["category"] for p in PRODUCTS})
    return sorted(cats)

# ---------- Order routes ----------

@app.post("/orders", status_code=201)
def place_order(body: OrderRequest, user=Depends(get_current_user)):
    order_items = []
    total = 0.0
    for item in body.items:
        product = next((p for p in PRODUCTS if p["id"] == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if item.quantity < product["min_order"]:
            raise HTTPException(status_code=400, detail=f"Minimum order for {product['name']} is {product['min_order']} units")
        if item.quantity > product["stock"]:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product['name']}")
        line_total = product["price"] * item.quantity
        total += line_total
        order_items.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity,
            "unit_price": product["price"],
            "line_total": line_total,
        })
        product["stock"] -= item.quantity

    order = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "user_email": user["email"],
        "items": order_items,
        "total": round(total, 2),
        "shipping_address": body.shipping_address,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    ORDERS.append(order)
    return order

@app.get("/orders")
def list_orders(user=Depends(get_current_user)):
    if user["role"] == "admin":
        return ORDERS
    return [o for o in ORDERS if o["user_id"] == user["id"]]

@app.get("/orders/{order_id}")
def get_order(order_id: str, user=Depends(get_current_user)):
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user["role"] != "admin" and order["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return order

@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: str, status: str, admin=Depends(require_admin)):
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    valid = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid}")
    order["status"] = status
    return order

# ---------- Stats (admin dashboard) ----------

@app.get("/admin/stats")
def admin_stats(admin=Depends(require_admin)):
    return {
        "total_products": len(PRODUCTS),
        "total_orders": len(ORDERS),
        "total_revenue": round(sum(o["total"] for o in ORDERS), 2),
        "pending_orders": len([o for o in ORDERS if o["status"] == "pending"]),
    }

# ---------- Health ----------

@app.get("/health")
def health():
    return {"status": "ok"}
