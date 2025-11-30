# Expense Tracker API

A comprehensive expense tracking API with income/expense management, categorization, monthly summaries, and graph-ready analytics endpoints. Built with FastAPI and PostgreSQL for robust financial data management.

## 🚀 Features

- **Transaction Management**: Add, edit, delete income and expense transactions
- **Smart Categories**: Pre-defined categories (Food, Rent, Travel, etc.) with custom categories
- **Monthly Summaries**: Comprehensive monthly financial reports
- **Graph Analytics**: Ready-to-use data for charts and visualizations
- **Budget Tracking**: Set and monitor budgets by category
- **Account Management**: Multiple payment methods (cash, bank, credit cards)
- **Recurring Transactions**: Automated recurring income/expenses
- **Tag System**: Organize transactions with custom tags
- **Receipt Management**: Store receipt URLs and documents
- **Trend Analysis**: Track spending patterns over time
- **Budget Alerts**: Monitor budget usage with warnings
- **Multi-currency Support**: Handle different currencies
- **Advanced Filtering**: Filter by date, category, type, tags

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Migrations**: Alembic for database schema management

## 📋 Prerequisites

- Python 3.7+
- pip package manager
- PostgreSQL 12+ (or use SQLite for development)
- PostgreSQL user with database creation privileges

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up database**:
```bash
# PostgreSQL
createdb expense_tracker

# Or use SQLite (no setup required)
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your database configuration
```

4. **Run database migrations**:
```bash
# For PostgreSQL
alembic upgrade head

# For SQLite (automatic)
python app.py  # Database created automatically
```

5. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8012`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8012/docs`
- ReDoc: `http://localhost:8012/redoc`

## 💰 API Endpoints

### User Management

#### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "currency": "USD"
}
```

#### Get User
```http
GET /users/{user_id}
```

### Categories

#### Create Category
```http
POST /categories
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Groceries",
  "description": "Food and grocery items",
  "color": "#ef4444",
  "icon": "🛒",
  "type": "expense"
}
```

#### Get Categories
```http
GET /categories?user_id=user_123&type=expense
```

**Response Example**:
```json
[
  {
    "id": "cat_123",
    "user_id": "user_123",
    "name": "Food & Dining",
    "description": "Restaurants and food delivery",
    "color": "#ef4444",
    "icon": "🍔",
    "type": "expense",
    "is_default": true,
    "created_at": "2024-01-15T10:00:00"
  },
  {
    "id": "cat_456",
    "user_id": "user_123",
    "name": "Salary",
    "description": "Monthly salary",
    "color": "#22c55e",
    "icon": "💰",
    "type": "income",
    "is_default": true,
    "created_at": "2024-01-15T10:00:00"
  }
]
```

### Transactions

#### Create Transaction
```http
POST /transactions
Content-Type: application/json

{
  "user_id": "user_123",
  "category_id": "cat_123",
  "amount": 45.99,
  "description": "Lunch at restaurant",
  "type": "expense",
  "date": "2024-01-15",
  "location": "Downtown Cafe",
  "tags": ["dining", "restaurant"],
  "receipt_url": "https://example.com/receipt.jpg",
  "is_recurring": false
}
```

#### Get Transactions
```http
GET /transactions?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31&category_id=cat_123&type=expense&limit=50&offset=0
```

**Response Example**:
```json
[
  {
    "id": "txn_123",
    "user_id": "user_123",
    "category_id": "cat_123",
    "amount": 45.99,
    "description": "Lunch at restaurant",
    "type": "expense",
    "date": "2024-01-15",
    "location": "Downtown Cafe",
    "tags": ["dining", "restaurant"],
    "receipt_url": "https://example.com/receipt.jpg",
    "is_recurring": false,
    "recurring_pattern": null,
    "recurring_end_date": null,
    "created_at": "2024-01-15T12:30:00",
    "updated_at": "2024-01-15T12:30:00"
  }
]
```

#### Update Transaction
```http
PUT /transactions/{transaction_id}
Content-Type: application/json

{
  "amount": 49.99,
  "description": "Lunch and drinks at restaurant"
}
```

#### Delete Transaction
```http
DELETE /transactions/{transaction_id}
```

### Analytics

#### Get Monthly Summary
```http
GET /analytics/monthly-summary?user_id=user_123&year=2024&month=1
```

**Response Example**:
```json
{
  "month": "2024-01",
  "year": 2024,
  "month_number": 1,
  "total_income": 5000.00,
  "total_expenses": 3250.50,
  "net_amount": 1749.50,
  "transaction_count": 45,
  "average_daily_spending": 104.85,
  "top_categories": [
    {
      "category_name": "Rent & Housing",
      "color": "#84cc16",
      "type": "expense",
      "total_amount": 1200.00,
      "transaction_count": 1
    },
    {
      "category_name": "Food & Dining",
      "color": "#ef4444",
      "type": "expense",
      "total_amount": 650.50,
      "transaction_count": 15
    }
  ],
  "budget_comparison": [
    {
      "budget_id": "budget_123",
      "category_name": "Food & Dining",
      "budget_amount": 800.00,
      "spent_amount": 650.50,
      "remaining_amount": 149.50,
      "percentage_used": 81.3,
      "status": "warning"
    }
  ]
}
```

#### Get Category Analytics
```http
GET /analytics/category-analytics?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31&transaction_type=expense
```

**Response Example**:
```json
[
  {
    "category_id": "cat_123",
    "category_name": "Food & Dining",
    "total_amount": 650.50,
    "transaction_count": 15,
    "average_amount": 43.37,
    "percentage_of_total": 20.0,
    "trend": "increasing"
  },
  {
    "category_id": "cat_456",
    "category_name": "Transportation",
    "total_amount": 450.00,
    "transaction_count": 8,
    "average_amount": 56.25,
    "percentage_of_total": 13.8,
    "trend": "stable"
  }
]
```

#### Get Daily Spending (Graph Ready)
```http
GET /analytics/daily-spending?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31
```

**Response Example**:
```json
[
  {
    "date": "2024-01-01",
    "amount": 125.50,
    "transaction_count": 3,
    "categories": [
      {
        "category_name": "Groceries",
        "color": "#ef4444",
        "amount": 85.50
      },
      {
        "category_name": "Transportation",
        "color": "#f59e0b",
        "amount": 40.00
      }
    ]
  },
  {
    "date": "2024-01-02",
    "amount": 45.00,
    "transaction_count": 1,
    "categories": [
      {
        "category_name": "Food & Dining",
        "color": "#ef4444",
        "amount": 45.00
      }
    ]
  }
]
```

#### Get Trends (Graph Ready)
```http
GET /analytics/trends?user_id=user_123&period=monthly&months=12
```

**Response Example**:
```json
{
  "period": "monthly",
  "income": [
    {"period": "2023-02", "amount": 5200.00},
    {"period": "2023-03", "amount": 5100.00},
    {"period": "2023-04", "amount": 5300.00}
  ],
  "expenses": [
    {"period": "2023-02", "amount": 3100.00},
    {"period": "2023-03", "amount": 2950.00},
    {"period": "2023-04", "amount": 3250.00}
  ],
  "net": [
    {"period": "2023-02", "amount": 2100.00},
    {"period": "2023-03", "amount": 2150.00},
    {"period": "2023-04", "amount": 2050.00}
  ],
  "categories": [
    {
      "category_id": "",
      "category_name": "Food & Dining",
      "total_amount": 9300.00,
      "transaction_count": 45,
      "average_amount": 206.67,
      "percentage_of_total": 0,
      "trend": "stable"
    }
  ]
}
```

#### Get Budget Status
```http
GET /analytics/budget-status?user_id=user_123
```

**Response Example**:
```json
[
  {
    "budget_id": "budget_123",
    "category_name": "Food & Dining",
    "budget_amount": 800.00,
    "spent_amount": 650.50,
    "remaining_amount": 149.50,
    "percentage_used": 81.3,
    "status": "warning",
    "days_remaining": 15
  },
  {
    "budget_id": "budget_456",
    "category_name": "Transportation",
    "budget_amount": 200.00,
    "spent_amount": 225.00,
    "remaining_amount": -25.00,
    "percentage_used": 112.5,
    "status": "over",
    "days_remaining": 8
  }
]
```

### Budgets

#### Create Budget
```http
POST /budgets
Content-Type: application/json

{
  "user_id": "user_123",
  "category_id": "cat_123",
  "amount": 800.00,
  "period": "monthly",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "is_active": true
}
```

#### Get Budgets
```http
GET /budgets?user_id=user_123&active_only=true
```

### Accounts

#### Create Account
```http
POST /accounts
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Main Checking Account",
  "type": "bank",
  "balance": 5250.75,
  "currency": "USD",
  "is_active": true
}
```

#### Get Accounts
```http
GET /accounts?user_id=user_123&active_only=true
```

## 📊 Data Models

### Transaction
```json
{
  "id": "txn_123",
  "user_id": "user_123",
  "category_id": "cat_123",
  "amount": 45.99,
  "description": "Lunch at restaurant",
  "type": "expense",
  "date": "2024-01-15",
  "location": "Downtown Cafe",
  "tags": ["dining", "restaurant"],
  "receipt_url": "https://example.com/receipt.jpg",
  "is_recurring": false,
  "recurring_pattern": null,
  "recurring_end_date": null,
  "created_at": "2024-01-15T12:30:00",
  "updated_at": "2024-01-15T12:30:00"
}
```

### Category
```json
{
  "id": "cat_123",
  "user_id": "user_123",
  "name": "Food & Dining",
  "description": "Restaurants and food delivery",
  "color": "#ef4444",
  "icon": "🍔",
  "type": "expense",
  "is_default": true,
  "created_at": "2024-01-15T10:00:00"
}
```

### Budget
```json
{
  "id": "budget_123",
  "user_id": "user_123",
  "category_id": "cat_123",
  "amount": 800.00,
  "period": "monthly",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

## 🧪 Testing Examples

### Complete Workflow
```bash
# Create user
curl -X POST "http://localhost:8012/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "expense_user",
    "email": "user@example.com",
    "first_name": "Alex",
    "last_name": "Smith",
    "currency": "USD"
  }'

# Add expense transaction
curl -X POST "http://localhost:8012/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "category_id": "cat_123",
    "amount": 25.50,
    "description": "Coffee and pastry",
    "type": "expense",
    "date": "2024-01-15",
    "location": "Coffee Shop"
  }'

# Add income transaction
curl -X POST "http://localhost:8012/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "category_id": "cat_456",
    "amount": 3000.00,
    "description": "Monthly salary",
    "type": "income",
    "date": "2024-01-15"
  }'

# Get monthly summary
curl "http://localhost:8012/analytics/monthly-summary?user_id=user_123&year=2024&month=1"

# Get category analytics
curl "http://localhost:8012/analytics/category-analytics?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31"

# Get daily spending for graphs
curl "http://localhost:8012/analytics/daily-spending?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31"

# Get trends for graphs
curl "http://localhost:8012/analytics/trends?user_id=user_123&period=monthly&months=6"
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/expense_tracker
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=expense_tracker
DATABASE_USER=user
DATABASE_PASSWORD=password

# API Configuration
HOST=0.0.0.0
PORT=8012
DEBUG=false

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/expense_api.log
LOG_ROTATION=daily

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Currency
DEFAULT_CURRENCY=USD
SUPPORTED_CURRENCIES=USD,EUR,GBP,CAD,JPY
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/pdf

# Notifications
EMAIL_NOTIFICATIONS=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Analytics
ENABLE_ANALYTICS=true
DATA_RETENTION_DAYS=365
BACKUP_ENABLED=true
BACKUP_INTERVAL=86400
```

### Database Schema (PostgreSQL)
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6366f1',
    icon VARCHAR(50),
    type VARCHAR(10) CHECK (type IN ('expense', 'income')) DEFAULT 'expense',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT,
    type VARCHAR(10) CHECK (type IN ('expense', 'income')) NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(200),
    tags JSONB DEFAULT '[]',
    receipt_url TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern VARCHAR(20),
    recurring_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_tags ON transactions USING GIN(tags);
```

### Alembic Migrations
```python
# alembic/versions/001_initial_migration.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create other tables...
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs uploads

EXPOSE 8012

# Run migrations and start app
CMD ["bash", "-c", "alembic upgrade head && uvicorn app:app --host 0.0.0.0 --port 8012"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  expense-api:
    build: .
    ports:
      - "8012:8012"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/expense_tracker
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: expense_tracker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: expense-tracker-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: expense-tracker-api
  template:
    metadata:
      labels:
        app: expense-tracker-api
    spec:
      containers:
      - name: api
        image: expense-tracker-api:latest
        ports:
        - containerPort: 8012
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8012
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: expense-tracker-service
spec:
  selector:
    app: expense-tracker-api
  ports:
  - port: 8012
    targetPort: 8012
  type: LoadBalancer
```

## 📈 Advanced Features

### Recurring Transactions
```python
@app.post("/transactions/recurring")
async def create_recurring_transaction(
    transaction: Transaction,
    pattern: RecurringPattern,
    end_date: date
):
    """Create recurring transactions"""
    # Generate recurring transactions based on pattern
    pass

@app.get("/transactions/recurring")
async def get_recurring_transactions(user_id: str):
    """Get all recurring transactions"""
    pass
```

### Receipt Management
```python
@app.post("/transactions/{transaction_id}/receipt")
async def upload_receipt(
    transaction_id: str,
    file: UploadFile = File(...)
):
    """Upload receipt for transaction"""
    # Store receipt and update transaction
    pass

@app.get("/transactions/{transaction_id}/receipt")
async def get_receipt(transaction_id: str):
    """Get receipt image"""
    # Serve receipt file
    pass
```

### Currency Exchange
```python
@app.get("/exchange-rates")
async def get_exchange_rates(base_currency: str = "USD"):
    """Get current exchange rates"""
    # Fetch from external API
    pass

@app.post("/transactions/convert")
async def convert_transaction_currency(
    transaction_id: str,
    target_currency: str
):
    """Convert transaction to different currency"""
    # Convert amount using exchange rate
    pass
```

### Export/Import
```python
@app.get("/export/csv")
async def export_transactions_csv(
    user_id: str,
    start_date: date,
    end_date: date
):
    """Export transactions as CSV"""
    # Generate CSV file
    pass

@app.post("/import/csv")
async def import_transactions_csv(
    user_id: str,
    file: UploadFile = File(...)
):
    """Import transactions from CSV"""
    # Parse and import CSV
    pass
```

## 📊 Graph Data Examples

### Pie Chart Data (Category Breakdown)
```javascript
// From /analytics/category-analytics
const pieChartData = [
  { name: "Food & Dining", value: 650.50, color: "#ef4444" },
  { name: "Transportation", value: 450.00, color: "#f59e0b" },
  { name: "Shopping", value: 320.00, color: "#8b5cf6" },
  { name: "Bills", value: 1200.00, color: "#3b82f6" }
];
```

### Line Chart Data (Trends)
```javascript
// From /analytics/trends
const lineChartData = {
  income: [
    { period: "2023-01", amount: 5000 },
    { period: "2023-02", amount: 5200 },
    { period: "2023-03", amount: 5100 }
  ],
  expenses: [
    { period: "2023-01", amount: 3200 },
    { period: "2023-02", amount: 3100 },
    { period: "2023-03", amount: 3250 }
  ]
};
```

### Bar Chart Data (Daily Spending)
```javascript
// From /analytics/daily-spending
const barChartData = [
  { date: "2024-01-01", amount: 125.50 },
  { date: "2024-01-02", amount: 45.00 },
  { date: "2024-01-03", amount: 89.25 }
];
```

### Budget Gauge Data
```javascript
// From /analytics/budget-status
const gaugeData = [
  { category: "Food", used: 81.3, budget: 100, status: "warning" },
  { category: "Transport", used: 112.5, budget: 100, status: "over" }
];
```

## 🛡️ Security Features

### Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(credentials: str = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Data Validation
```python
from pydantic import validator

class Transaction(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    
    @validator('date')
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError('Date cannot be in the future')
        return v
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/transactions")
@limiter.limit("10/minute")
async def create_transaction(request: Request, transaction: Transaction):
    """Rate-limited transaction creation"""
    pass
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
transactions_created = Counter('expense_transactions_created_total', 'Total transactions created')
analytics_requests = Counter('expense_analytics_requests_total', 'Analytics requests')
api_response_time = Histogram('expense_api_response_seconds', 'API response time')
active_users = Gauge('expense_active_users', 'Active users')
```

### Health Monitoring
```python
@app.get("/health/detailed")
async def detailed_health():
    """Comprehensive health check"""
    try:
        # Test database connection
        db_status = await check_database_health()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": db_status,
            "metrics": {
                "total_transactions": transactions_created._value._value,
                "active_users": active_users._value._value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
```

## 🔮 Future Enhancements

### Planned Features
- **Multi-currency Support**: Real-time exchange rate conversion
- **Investment Tracking**: Portfolio management and returns
- **Bill Reminders**: Automated bill payment reminders
- **Goal Setting**: Financial goals and progress tracking
- **Receipt OCR**: Automatic text extraction from receipts
- **Bank Integration**: Direct bank account synchronization
- **Mobile App**: Native mobile applications
- **Collaborative Budgets**: Shared budgets for families/roommates
- **Advanced Reporting**: PDF reports and export options
- **AI Insights**: Spending pattern analysis and recommendations

### Analytics Enhancements
- **Predictive Analytics**: Forecast future spending
- **Anomaly Detection**: Unusual spending alerts
- **Budget Optimization**: AI-powered budget recommendations
- **Financial Health Score**: Overall financial wellness scoring
- **Comparison Analytics**: Compare spending with similar users
- **Seasonal Trends**: Year-over-year seasonal analysis

### Integration Opportunities
- **Plaid Integration**: Bank account linking
- **QuickBooks/Sage**: Accounting software integration
- **Tax Software**: Tax preparation integration
- **Payment Processors**: Direct payment processing
- **Calendar Integration**: Bill due date reminders
- **Notification Services**: SMS/email/push notifications

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review PostgreSQL documentation for database management
- Consult Alembic documentation for migrations
- Check financial data best practices for security

---

**Built with ❤️ using FastAPI and PostgreSQL**
