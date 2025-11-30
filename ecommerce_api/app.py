from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import math
from decimal import Decimal

app = FastAPI(title="E-Commerce Products API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"
    CASH_ON_DELIVERY = "cash_on_delivery"

# Pydantic models
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    sku: str = Field(default_factory=lambda: f"PRD-{uuid.uuid4().hex[:8].upper()}")
    price: Decimal = Field(..., gt=0)
    compare_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    track_inventory: bool = True
    inventory_quantity: int = 0
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict[str, Decimal]] = None  # {length, width, height}
    category_id: Optional[str] = None
    brand: Optional[str] = None
    tags: List[str] = []
    images: List[str] = []
    status: ProductStatus = ProductStatus.ACTIVE
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CartItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    quantity: int = Field(..., gt=0)
    added_at: datetime = Field(default_factory=datetime.now)

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[CartItem] = []
    subtotal: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    shipping_amount: Decimal = Decimal('0.00')
    discount_amount: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class OrderItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    product_image: Optional[str] = None

class ShippingAddress(BaseModel):
    first_name: str
    last_name: str
    company: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    city: str
    province: str
    country: str
    postal_code: str
    phone: Optional[str] = None

class BillingAddress(BaseModel):
    first_name: str
    last_name: str
    company: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    city: str
    province: str
    country: str
    postal_code: str
    phone: Optional[str] = None

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str = Field(default_factory=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")
    user_id: str
    items: List[OrderItem] = []
    status: OrderStatus = OrderStatus.PENDING
    currency: str = "USD"
    subtotal: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    shipping_amount: Decimal = Decimal('0.00')
    discount_amount: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    shipping_address: Optional[ShippingAddress] = None
    billing_address: Optional[BillingAddress] = None
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    amount: Decimal
    currency: str = "USD"
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

class PaymentRequest(BaseModel):
    order_id: str
    payment_method: PaymentMethod
    card_number: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None
    cardholder_name: Optional[str] = None
    billing_address: Optional[BillingAddress] = None

class PaymentResponse(BaseModel):
    success: bool
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    message: str
    gateway_response: Optional[Dict[str, Any]] = None

# In-memory storage (for demo purposes)
# In production, replace with PostgreSQL database
class ECommerceStore:
    def __init__(self):
        self.categories: Dict[str, Category] = {}
        self.products: Dict[str, Product] = {}
        self.carts: Dict[str, Cart] = {}
        self.orders: Dict[str, Order] = {}
        self.payments: Dict[str, Payment] = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample data for testing"""
        # Create categories
        electronics = Category(
            name="Electronics",
            description="Electronic devices and accessories"
        )
        clothing = Category(
            name="Clothing",
            description="Fashion and apparel"
        )
        books = Category(
            name="Books",
            description="Books and publications"
        )
        
        self.categories[electronics.id] = electronics
        self.categories[clothing.id] = clothing
        self.categories[books.id] = books
        
        # Create sample products
        laptop = Product(
            name="Laptop Pro 15\"",
            description="High-performance laptop with 15-inch display",
            price=Decimal('1299.99'),
            compare_price=Decimal('1499.99'),
            inventory_quantity=50,
            category_id=electronics.id,
            brand="TechBrand",
            tags=["laptop", "computer", "electronics"],
            images=["https://example.com/laptop1.jpg", "https://example.com/laptop2.jpg"],
            featured=True
        )
        
        smartphone = Product(
            name="Smartphone X",
            description="Latest smartphone with advanced features",
            price=Decimal('899.99'),
            compare_price=Decimal('999.99'),
            inventory_quantity=100,
            category_id=electronics.id,
            brand="PhoneCo",
            tags=["smartphone", "mobile", "electronics"],
            images=["https://example.com/phone1.jpg"],
            featured=True
        )
        
        tshirt = Product(
            name="Cotton T-Shirt",
            description="Comfortable cotton t-shirt",
            price=Decimal('19.99'),
            inventory_quantity=200,
            category_id=clothing.id,
            brand="FashionBrand",
            tags=["clothing", "t-shirt", "casual"],
            images=["https://example.com/tshirt1.jpg"]
        )
        
        book = Product(
            name="Programming Guide",
            description="Complete guide to programming",
            price=Decimal('39.99'),
            inventory_quantity=30,
            category_id=books.id,
            brand="TechBooks",
            tags=["programming", "education", "books"],
            images=["https://example.com/book1.jpg"]
        )
        
        self.products[laptop.id] = laptop
        self.products[smartphone.id] = smartphone
        self.products[tshirt.id] = tshirt
        self.products[book.id] = book
    
    def calculate_cart_totals(self, cart: Cart) -> Cart:
        """Calculate cart totals"""
        subtotal = Decimal('0.00')
        
        for item in cart.items:
            product = self.products.get(item.product_id)
            if product:
                item_total = product.price * item.quantity
                subtotal += item_total
        
        # Calculate tax (8% for demo)
        tax_rate = Decimal('0.08')
        tax_amount = subtotal * tax_rate
        
        # Calculate shipping (flat rate for demo)
        shipping_amount = Decimal('9.99') if subtotal > Decimal('0.00') else Decimal('0.00')
        
        # Calculate discount (no discount for demo)
        discount_amount = Decimal('0.00')
        
        # Calculate total
        total_amount = subtotal + tax_amount + shipping_amount - discount_amount
        
        cart.subtotal = subtotal
        cart.tax_amount = tax_amount
        cart.shipping_amount = shipping_amount
        cart.discount_amount = discount_amount
        cart.total_amount = total_amount
        cart.updated_at = datetime.now()
        
        return cart
    
    def get_or_create_cart(self, user_id: str) -> Cart:
        """Get or create cart for user"""
        if user_id not in self.carts:
            self.carts[user_id] = Cart(user_id=user_id)
        
        return self.carts[user_id]
    
    def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """Add item to cart"""
        product = self.products.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.status != ProductStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Product not available")
        
        if product.track_inventory and product.inventory_quantity < quantity:
            raise HTTPException(status_code=400, detail="Insufficient inventory")
        
        cart = self.get_or_create_cart(user_id)
        
        # Check if item already in cart
        for item in cart.items:
            if item.product_id == product_id:
                # Update quantity
                new_quantity = item.quantity + quantity
                if product.track_inventory and product.inventory_quantity < new_quantity:
                    raise HTTPException(status_code=400, detail="Insufficient inventory")
                item.quantity = new_quantity
                return self.calculate_cart_totals(cart)
        
        # Add new item
        cart_item = CartItem(product_id=product_id, quantity=quantity)
        cart.items.append(cart_item)
        
        return self.calculate_cart_totals(cart)
    
    def remove_from_cart(self, user_id: str, item_id: str) -> Cart:
        """Remove item from cart"""
        cart = self.get_or_create_cart(user_id)
        
        cart.items = [item for item in cart.items if item.id != item_id]
        
        return self.calculate_cart_totals(cart)
    
    def update_cart_item(self, user_id: str, item_id: str, quantity: int) -> Cart:
        """Update cart item quantity"""
        cart = self.get_or_create_cart(user_id)
        
        for item in cart.items:
            if item.id == item_id:
                product = self.products.get(item.product_id)
                if product and product.track_inventory and product.inventory_quantity < quantity:
                    raise HTTPException(status_code=400, detail="Insufficient inventory")
                item.quantity = quantity
                return self.calculate_cart_totals(cart)
        
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    def clear_cart(self, user_id: str) -> Cart:
        """Clear cart"""
        cart = self.get_or_create_cart(user_id)
        cart.items = []
        return self.calculate_cart_totals(cart)
    
    def create_order(self, user_id: str, cart: Cart, shipping_address: ShippingAddress, billing_address: Optional[BillingAddress] = None) -> Order:
        """Create order from cart"""
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Check inventory
        for cart_item in cart.items:
            product = self.products.get(cart_item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
            
            if product.track_inventory and product.inventory_quantity < cart_item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient inventory for {product.name}")
        
        # Create order items
        order_items = []
        for cart_item in cart.items:
            product = self.products.get(cart_item.product_id)
            order_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                quantity=cart_item.quantity,
                unit_price=product.price,
                total_price=product.price * cart_item.quantity,
                product_image=product.images[0] if product.images else None
            )
            order_items.append(order_item)
        
        # Create order
        order = Order(
            user_id=user_id,
            items=order_items,
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            shipping_amount=cart.shipping_amount,
            discount_amount=cart.discount_amount,
            total_amount=cart.total_amount,
            shipping_address=shipping_address,
            billing_address=billing_address or shipping_address
        )
        
        # Update inventory
        for cart_item in cart.items:
            product = self.products.get(cart_item.product_id)
            if product and product.track_inventory:
                product.inventory_quantity -= cart_item.quantity
                product.updated_at = datetime.now()
        
        # Store order
        self.orders[order.id] = order
        
        # Clear cart
        self.clear_cart(user_id)
        
        return order
    
    def process_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """Process payment (mock implementation)"""
        order = self.orders.get(payment_request.order_id)
        if not order:
            return PaymentResponse(
                success=False,
                message="Order not found"
            )
        
        if order.payment_status != PaymentStatus.PENDING:
            return PaymentResponse(
                success=False,
                message="Order already processed"
            )
        
        # Mock payment processing
        payment_id = str(uuid.uuid4())
        transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        # Simulate payment processing
        success = True  # In real implementation, this would call payment gateway
        
        if success:
            # Create payment record
            payment = Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method=payment_request.payment_method,
                status=PaymentStatus.COMPLETED,
                transaction_id=transaction_id,
                processed_at=datetime.now(),
                gateway_response={"status": "approved", "auth_code": "123456"}
            )
            
            self.payments[payment.id] = payment
            
            # Update order
            order.payment_status = PaymentStatus.COMPLETED
            order.payment_method = payment_request.payment_method
            order.transaction_id = transaction_id
            order.status = OrderStatus.CONFIRMED
            order.updated_at = datetime.now()
            
            return PaymentResponse(
                success=True,
                payment_id=payment.id,
                transaction_id=transaction_id,
                message="Payment processed successfully",
                gateway_response=payment.gateway_response
            )
        else:
            return PaymentResponse(
                success=False,
                message="Payment failed"
            )

# Initialize store
store = ECommerceStore()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to E-Commerce Products API", "version": "1.0.0"}

# Categories
@app.post("/categories", response_model=Category)
async def create_category(category: Category):
    """Create a new category"""
    store.categories[category.id] = category
    return category

@app.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all categories"""
    return list(store.categories.values())

@app.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: str):
    """Get category by ID"""
    category = store.categories.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, category_update: Dict[str, Any]):
    """Update category"""
    category = store.categories.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for field, value in category_update.items():
        if hasattr(category, field):
            setattr(category, field, value)
    
    return category

@app.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    """Delete category"""
    category = store.categories.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    del store.categories[category_id]
    return {"message": "Category deleted successfully"}

# Products
@app.post("/products", response_model=Product)
async def create_product(product: Product):
    """Create a new product"""
    store.products[product.id] = product
    return product

@app.get("/products", response_model=List[Product])
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None),
    status: Optional[ProductStatus] = Query(None),
    featured: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None)
):
    """Get products with filtering and pagination"""
    products = list(store.products.values())
    
    # Apply filters
    if category_id:
        products = [p for p in products if p.category_id == category_id]
    
    if status:
        products = [p for p in products if p.status == status]
    
    if featured is not None:
        products = [p for p in products if p.featured == featured]
    
    if search:
        search_lower = search.lower()
        products = [p for p in products if 
                   search_lower in p.name.lower() or 
                   search_lower in (p.description or "").lower() or
                   search_lower in p.brand.lower() or
                   any(search_lower in tag.lower() for tag in p.tags)]
    
    if min_price is not None:
        products = [p for p in products if float(p.price) >= min_price]
    
    if max_price is not None:
        products = [p for p in products if float(p.price) <= max_price]
    
    # Sort by created_at (newest first)
    products.sort(key=lambda x: x.created_at, reverse=True)
    
    # Pagination
    total = len(products)
    start = (page - 1) * limit
    end = start + limit
    paginated_products = products[start:end]
    
    return paginated_products

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product by ID"""
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: Dict[str, Any]):
    """Update product"""
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for field, value in product_update.items():
        if hasattr(product, field):
            setattr(product, field, value)
    
    product.updated_at = datetime.now()
    return product

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete product"""
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    del store.products[product_id]
    return {"message": "Product deleted successfully"}

# Cart
@app.get("/cart", response_model=Cart)
async def get_cart(user_id: str = Query(...)):
    """Get user's cart"""
    cart = store.get_or_create_cart(user_id)
    return cart

@app.post("/cart/add", response_model=Cart)
async def add_to_cart(
    user_id: str = Query(...),
    product_id: str = Body(...),
    quantity: int = Body(..., gt=0)
):
    """Add item to cart"""
    return store.add_to_cart(user_id, product_id, quantity)

@app.delete("/cart/items/{item_id}", response_model=Cart)
async def remove_from_cart(item_id: str, user_id: str = Query(...)):
    """Remove item from cart"""
    return store.remove_from_cart(user_id, item_id)

@app.put("/cart/items/{item_id}", response_model=Cart)
async def update_cart_item(
    item_id: str,
    quantity: int = Body(..., gt=0),
    user_id: str = Query(...)
):
    """Update cart item quantity"""
    return store.update_cart_item(user_id, item_id, quantity)

@app.delete("/cart", response_model=Cart)
async def clear_cart(user_id: str = Query(...)):
    """Clear cart"""
    return store.clear_cart(user_id)

# Orders
@app.post("/orders", response_model=Order)
async def create_order(
    user_id: str = Query(...),
    shipping_address: ShippingAddress = Body(...),
    billing_address: Optional[BillingAddress] = Body(None)
):
    """Create order from cart"""
    cart = store.get_or_create_cart(user_id)
    return store.create_order(user_id, cart, shipping_address, billing_address)

@app.get("/orders", response_model=List[Order])
async def get_orders(
    user_id: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None)
):
    """Get user's orders"""
    orders = [order for order in store.orders.values() if order.user_id == user_id]
    
    if status:
        orders = [order for order in orders if order.status == status]
    
    # Sort by created_at (newest first)
    orders.sort(key=lambda x: x.created_at, reverse=True)
    
    # Pagination
    total = len(orders)
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = orders[start:end]
    
    return paginated_orders

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, user_id: str = Query(...)):
    """Get order by ID"""
    order = store.orders.get(order_id)
    if not order or order.user_id != user_id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: OrderStatus = Body(...),
    user_id: str = Query(...)
):
    """Update order status"""
    order = store.orders.get(order_id)
    if not order or order.user_id != user_id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    order.updated_at = datetime.now()
    
    if status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.now()
    elif status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.now()
    
    return {"message": "Order status updated successfully", "status": status.value}

# Payments
@app.post("/payments/process", response_model=PaymentResponse)
async def process_payment(payment_request: PaymentRequest):
    """Process payment"""
    return store.process_payment(payment_request)

@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    """Get payment by ID"""
    payment = store.payments.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.get("/orders/{order_id}/payments", response_model=List[Payment])
async def get_order_payments(order_id: str):
    """Get payments for order"""
    order = store.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payments = [payment for payment in store.payments.values() if payment.order_id == order_id]
    return payments

# Search
@app.get("/search/products")
async def search_products(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Search products"""
    products = list(store.products.values())
    search_lower = q.lower()
    
    # Search in name, description, brand, tags
    results = []
    for product in products:
        if (search_lower in product.name.lower() or
            search_lower in (product.description or "").lower() or
            search_lower in (product.brand or "").lower() or
            any(search_lower in tag.lower() for tag in product.tags)):
            results.append(product)
    
    # Sort by relevance (name matches first)
    results.sort(key=lambda x: (
        search_lower in x.name.lower(),
        x.name.lower().startswith(search_lower),
        x.created_at
    ), reverse=True)
    
    # Pagination
    total = len(results)
    start = (page - 1) * limit
    end = start + limit
    paginated_results = results[start:end]
    
    return {
        "products": paginated_results,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit)
    }

# Analytics
@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    total_products = len(store.products)
    total_categories = len(store.categories)
    total_orders = len(store.orders)
    total_revenue = sum(order.total_amount for order in store.orders.values() if order.payment_status == PaymentStatus.COMPLETED)
    
    # Orders by status
    orders_by_status = {}
    for status in OrderStatus:
        orders_by_status[status.value] = len([order for order in store.orders.values() if order.status == status])
    
    # Top products by orders
    product_order_counts = {}
    for order in store.orders.values():
        for item in order.items:
            product_order_counts[item.product_id] = product_order_counts.get(item.product_id, 0) + item.quantity
    
    top_products = sorted(product_order_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "orders_by_status": orders_by_status,
        "top_products": [
            {
                "product_id": product_id,
                "product_name": store.products[product_id].name,
                "order_count": count
            }
            for product_id, count in top_products
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "store_stats": {
            "products": len(store.products),
            "categories": len(store.categories),
            "orders": len(store.orders),
            "payments": len(store.payments)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
