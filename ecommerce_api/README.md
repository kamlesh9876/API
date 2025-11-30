# E-Commerce Products API

A comprehensive e-commerce API with full CRUD operations for products, cart management, order processing, and payment handling. Built with FastAPI and designed for PostgreSQL integration.

## 🚀 Features

- **Product Management**: Full CRUD for products with categories, inventory, pricing
- **Category Management**: Hierarchical category system with images
- **Shopping Cart**: Add/remove items, update quantities, calculate totals
- **Order Management**: Create orders, track status, manage shipping/billing
- **Payment Processing**: Mock payment gateway with multiple payment methods
- **Search & Filtering**: Advanced product search with filters
- **Inventory Tracking**: Automatic inventory updates on orders
- **Analytics**: Sales analytics and reporting
- **Pagination**: Efficient data pagination for large datasets
- **Tax & Shipping**: Automatic calculation of taxes and shipping costs
- **Discount System**: Framework for discount codes and promotions
- **SEO Support**: SEO titles and descriptions for products
- **Product Variants**: Support for product variants and options
- **Customer Management**: User-based carts and order history

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Authentication**: JWT tokens (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Payment Integration**: Stripe (ready for production)
- **Data Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.7+
- PostgreSQL database (for production)
- pip package manager
- (Optional) Stripe account for payment processing

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up database** (for production):
```bash
# Create PostgreSQL database
createdb ecommerce_db

# Run migrations (when using Alembic)
alembic upgrade head
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8009`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8009/docs`
- ReDoc: `http://localhost:8009/redoc`

## 🛍️ API Endpoints

### Categories

#### Create Category
```http
POST /categories
Content-Type: application/json

{
  "name": "Electronics",
  "description": "Electronic devices and accessories",
  "parent_id": null,
  "image_url": "https://example.com/electronics.jpg",
  "is_active": true
}
```

#### Get All Categories
```http
GET /categories
```

#### Get Category
```http
GET /categories/{category_id}
```

#### Update Category
```http
PUT /categories/{category_id}
Content-Type: application/json

{
  "name": "Updated Category Name",
  "description": "Updated description"
}
```

#### Delete Category
```http
DELETE /categories/{category_id}
```

### Products

#### Create Product
```http
POST /products
Content-Type: application/json

{
  "name": "Laptop Pro 15\"",
  "description": "High-performance laptop",
  "price": 1299.99,
  "compare_price": 1499.99,
  "inventory_quantity": 50,
  "category_id": "category_id",
  "brand": "TechBrand",
  "tags": ["laptop", "computer"],
  "images": ["https://example.com/laptop.jpg"],
  "featured": true
}
```

#### Get Products (with filtering)
```http
GET /products?page=1&limit=20&category_id=cat123&status=active&featured=true&search=laptop&min_price=500&max_price=2000
```

**Response Example**:
```json
[
  {
    "id": "prod_123",
    "name": "Laptop Pro 15\"",
    "description": "High-performance laptop",
    "sku": "PRD-ABC12345",
    "price": 1299.99,
    "compare_price": 1499.99,
    "inventory_quantity": 50,
    "category_id": "cat_123",
    "brand": "TechBrand",
    "tags": ["laptop", "computer"],
    "images": ["https://example.com/laptop.jpg"],
    "status": "active",
    "featured": true,
    "created_at": "2024-01-15T10:00:00"
  }
]
```

#### Get Product
```http
GET /products/{product_id}
```

#### Update Product
```http
PUT /products/{product_id}
Content-Type: application/json

{
  "name": "Updated Product Name",
  "price": 1199.99,
  "inventory_quantity": 45
}
```

#### Delete Product
```http
DELETE /products/{product_id}
```

### Shopping Cart

#### Get Cart
```http
GET /cart?user_id=user123
```

**Response Example**:
```json
{
  "id": "cart_123",
  "user_id": "user123",
  "items": [
    {
      "id": "item_123",
      "product_id": "prod_123",
      "quantity": 2,
      "added_at": "2024-01-15T12:00:00"
    }
  ],
  "subtotal": 2599.98,
  "tax_amount": 207.99,
  "shipping_amount": 9.99,
  "discount_amount": 0.00,
  "total_amount": 2817.96,
  "currency": "USD"
}
```

#### Add to Cart
```http
POST /cart/add?user_id=user123
Content-Type: application/json

{
  "product_id": "prod_123",
  "quantity": 2
}
```

#### Remove from Cart
```http
DELETE /cart/items/{item_id}?user_id=user123
```

#### Update Cart Item
```http
PUT /cart/items/{item_id}?user_id=user123
Content-Type: application/json

{
  "quantity": 3
}
```

#### Clear Cart
```http
DELETE /cart?user_id=user123
```

### Orders

#### Create Order
```http
POST /orders?user_id=user123
Content-Type: application/json

{
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address1": "123 Main St",
    "city": "New York",
    "province": "NY",
    "country": "USA",
    "postal_code": "10001",
    "phone": "+1-555-0123"
  },
  "billing_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address1": "123 Main St",
    "city": "New York",
    "province": "NY",
    "country": "USA",
    "postal_code": "10001"
  }
}
```

**Response Example**:
```json
{
  "id": "order_123",
  "order_number": "ORD-ABC12345",
  "user_id": "user123",
  "items": [
    {
      "id": "order_item_123",
      "product_id": "prod_123",
      "product_name": "Laptop Pro 15\"",
      "product_sku": "PRD-ABC12345",
      "quantity": 2,
      "unit_price": 1299.99,
      "total_price": 2599.98
    }
  ],
  "status": "pending",
  "subtotal": 2599.98,
  "tax_amount": 207.99,
  "shipping_amount": 9.99,
  "total_amount": 2817.96,
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address1": "123 Main St",
    "city": "New York",
    "province": "NY",
    "country": "USA",
    "postal_code": "10001"
  },
  "payment_status": "pending",
  "created_at": "2024-01-15T12:00:00"
}
```

#### Get User Orders
```http
GET /orders?user_id=user123&page=1&limit=20&status=pending
```

#### Get Order
```http
GET /orders/{order_id}?user_id=user123
```

#### Update Order Status
```http
PUT /orders/{order_id}/status?user_id=user123
Content-Type: application/json

{
  "status": "shipped"
}
```

### Payments

#### Process Payment
```http
POST /payments/process
Content-Type: application/json

{
  "order_id": "order_123",
  "payment_method": "credit_card",
  "card_number": "4242424242424242",
  "card_expiry": "12/25",
  "card_cvv": "123",
  "cardholder_name": "John Doe"
}
```

**Response Example**:
```json
{
  "success": true,
  "payment_id": "pay_123",
  "transaction_id": "TXN-ABC12345",
  "message": "Payment processed successfully",
  "gateway_response": {
    "status": "approved",
    "auth_code": "123456"
  }
}
```

#### Get Payment
```http
GET /payments/{payment_id}
```

#### Get Order Payments
```http
GET /orders/{order_id}/payments
```

### Search

#### Search Products
```http
GET /search/products?q=laptop&page=1&limit=20
```

**Response Example**:
```json
{
  "products": [...],
  "total": 15,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

### Analytics

#### Get Analytics Summary
```http
GET /analytics/summary
```

**Response Example**:
```json
{
  "total_products": 150,
  "total_categories": 12,
  "total_orders": 1250,
  "total_revenue": 125000.50,
  "orders_by_status": {
    "pending": 25,
    "confirmed": 100,
    "shipped": 75,
    "delivered": 1050
  },
  "top_products": [
    {
      "product_id": "prod_123",
      "product_name": "Laptop Pro 15\"",
      "order_count": 150
    }
  ]
}
```

## 📊 Data Models

### Product
```json
{
  "id": "prod_123",
  "name": "Product Name",
  "description": "Product description",
  "sku": "PRD-ABC12345",
  "price": 99.99,
  "compare_price": 129.99,
  "cost_price": 50.00,
  "track_inventory": true,
  "inventory_quantity": 100,
  "weight": 1.5,
  "dimensions": {"length": 10.0, "width": 8.0, "height": 2.0},
  "category_id": "cat_123",
  "brand": "Brand Name",
  "tags": ["tag1", "tag2"],
  "images": ["https://example.com/image.jpg"],
  "status": "active",
  "seo_title": "SEO Title",
  "seo_description": "SEO Description",
  "featured": false,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### Order
```json
{
  "id": "order_123",
  "order_number": "ORD-ABC12345",
  "user_id": "user_123",
  "items": [...],
  "status": "pending",
  "currency": "USD",
  "subtotal": 99.99,
  "tax_amount": 8.00,
  "shipping_amount": 9.99,
  "discount_amount": 0.00,
  "total_amount": 117.98,
  "shipping_address": {...},
  "billing_address": {...},
  "payment_status": "pending",
  "payment_method": "credit_card",
  "transaction_id": "TXN-ABC12345",
  "notes": "Customer notes",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

## 🧪 Testing Examples

### Create Product
```bash
curl -X POST "http://localhost:8009/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Headphones",
    "description": "Bluetooth noise-canceling headphones",
    "price": 199.99,
    "inventory_quantity": 25,
    "category_id": "cat_123",
    "brand": "AudioBrand",
    "tags": ["headphones", "bluetooth", "wireless"]
  }'
```

### Add to Cart
```bash
curl -X POST "http://localhost:8009/cart/add?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod_123",
    "quantity": 2
  }'
```

### Create Order
```bash
curl -X POST "http://localhost:8009/orders?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "first_name": "John",
      "last_name": "Doe",
      "address1": "123 Main St",
      "city": "New York",
      "province": "NY",
      "country": "USA",
      "postal_code": "10001"
    }
  }'
```

### Process Payment
```bash
curl -X POST "http://localhost:8009/payments/process" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_123",
    "payment_method": "credit_card",
    "card_number": "4242424242424242",
    "card_expiry": "12/25",
    "card_cvv": "123",
    "cardholder_name": "John Doe"
  }'
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/ecommerce_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ecommerce_db
DATABASE_USER=user
DATABASE_PASSWORD=password

# JWT Configuration
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payment Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Tax Configuration
TAX_RATE=0.08
SHIPPING_RATE=9.99

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ecommerce_api.log
```

### Database Schema (PostgreSQL)
```sql
-- Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    compare_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    track_inventory BOOLEAN DEFAULT true,
    inventory_quantity INTEGER DEFAULT 0,
    weight DECIMAL(8,2),
    dimensions JSONB,
    category_id UUID REFERENCES categories(id),
    brand VARCHAR(255),
    tags TEXT[],
    images TEXT[],
    status VARCHAR(20) DEFAULT 'active',
    seo_title VARCHAR(255),
    seo_description TEXT,
    featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address JSONB,
    billing_address JSONB,
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP
);

-- Order Items
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    product_image VARCHAR(500)
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    gateway_response JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_featured ON products(featured);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8009

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8009"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  ecommerce-api:
    build: .
    ports:
      - "8009:8009"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ecommerce_db
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - postgres
    volumes:
      - ./uploads:/app/uploads

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: api
        image: ecommerce-api:latest
        ports:
        - containerPort: 8009
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## 📈 Advanced Features

### Discount System
```python
class DiscountCode(BaseModel):
    id: str
    code: str
    discount_type: str  # percentage, fixed_amount
    discount_value: Decimal
    minimum_amount: Optional[Decimal] = None
    usage_limit: Optional[int] = None
    used_count: int = 0
    expires_at: Optional[datetime] = None
    is_active: bool = True

@app.post("/discounts/apply")
async def apply_discount_code(
    cart_id: str,
    discount_code: str
):
    """Apply discount code to cart"""
    pass
```

### Product Variants
```python
class ProductVariant(BaseModel):
    id: str
    product_id: str
    title: str
    sku: str
    price: Decimal
    inventory_quantity: int
    option1: Optional[str] = None  # e.g., "Small"
    option2: Optional[str] = None  # e.g., "Red"
    option3: Optional[str] = None  # e.g., "Cotton"

@app.get("/products/{product_id}/variants")
async def get_product_variants(product_id: str):
    """Get product variants"""
    pass
```

### Inventory Management
```python
class InventoryTransaction(BaseModel):
    id: str
    product_id: str
    transaction_type: str  # sale, purchase, adjustment, return
    quantity: int
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

@app.post("/inventory/adjust")
async def adjust_inventory(
    product_id: str,
    quantity: int,
    transaction_type: str,
    notes: Optional[str] = None
):
    """Adjust product inventory"""
    pass
```

## 🛡️ Security Features

### Authentication
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(credentials: str = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/orders")
@limiter.limit("10/minute")
async def create_order(request: Request, ...):
    """Rate limited order creation"""
    pass
```

## 🔍 Monitoring & Analytics

### Sales Analytics
```python
@app.get("/analytics/sales")
async def get_sales_analytics(
    start_date: datetime,
    end_date: datetime,
    group_by: str = "day"  # day, week, month
):
    """Get sales analytics for date range"""
    pass

@app.get("/analytics/products")
async def get_product_analytics():
    """Get product performance analytics"""
    pass

@app.get("/analytics/customers")
async def get_customer_analytics():
    """Get customer analytics and insights"""
    pass
```

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
orders_created = Counter('ecommerce_orders_created_total', 'Total orders created')
payments_processed = Counter('ecommerce_payments_processed_total', 'Total payments processed')
revenue_total = Gauge('ecommerce_revenue_total', 'Total revenue')
cart_value = Histogram('ecommerce_cart_value', 'Cart value distribution')
```

## 🔮 Future Enhancements

### Planned Features
- **Customer Reviews**: Product rating and review system
- **Wishlist Management**: Customer wishlist functionality
- **Product Recommendations**: AI-powered product recommendations
- **Multi-currency Support**: International pricing and payments
- **Shipping Integration**: Real-time shipping rates and tracking
- **Tax Calculation**: Automated tax calculation by region
- **Inventory Alerts**: Low stock and reorder notifications
- **Email Notifications**: Order status and shipping notifications
- **Product Bundles**: Create product bundles and deals
- **Gift Cards**: Digital gift card system
- **Refund Management**: Automated refund processing

### AI Integration
- **Smart Search**: AI-powered product search with relevance ranking
- **Price Optimization**: Dynamic pricing based on demand
- **Fraud Detection**: AI-powered fraud detection for orders
- **Customer Segmentation**: AI-driven customer analytics
- **Demand Forecasting**: Predict inventory needs based on trends

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review PostgreSQL documentation for database setup
- Consult Stripe documentation for payment integration

---

**Built with ❤️ using FastAPI and PostgreSQL**
