from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from enum import Enum
import uuid
import sqlite3
from sqlite3 import Connection
from decimal import Decimal
import json
from collections import defaultdict

app = FastAPI(title="Expense Tracker API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "expense_tracker.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            currency TEXT DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#6366f1',
            icon TEXT,
            type TEXT CHECK(type IN ('expense', 'income')) DEFAULT 'expense',
            is_default BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            category_id TEXT,
            amount DECIMAL(15,2) NOT NULL,
            description TEXT,
            type TEXT CHECK(type IN ('expense', 'income')) NOT NULL,
            date DATE NOT NULL,
            location TEXT,
            tags TEXT,  -- JSON array
            receipt_url TEXT,
            is_recurring BOOLEAN DEFAULT 0,
            recurring_pattern TEXT,  -- daily, weekly, monthly, yearly
            recurring_end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            category_id TEXT,
            amount DECIMAL(15,2) NOT NULL,
            period TEXT CHECK(period IN ('weekly', 'monthly', 'yearly')) DEFAULT 'monthly',
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Accounts table (for multiple payment methods)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('cash', 'bank', 'credit_card', 'digital_wallet', 'investment')) DEFAULT 'bank',
            balance DECIMAL(15,2) DEFAULT 0,
            currency TEXT DEFAULT 'USD',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Enums
class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"

class CategoryType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"

class BudgetPeriod(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class AccountType(str, Enum):
    CASH = "cash"
    BANK = "bank"
    CREDIT_CARD = "credit_card"
    DIGITAL_WALLET = "digital_wallet"
    INVESTMENT = "investment"

class RecurringPattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# Pydantic models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: Optional[str] = None
    color: str = "#6366f1"
    icon: Optional[str] = None
    type: CategoryType = CategoryType.EXPENSE
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    category_id: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    type: TransactionType
    date: date
    location: Optional[str] = None
    tags: List[str] = []
    receipt_url: Optional[str] = None
    is_recurring: bool = False
    recurring_pattern: Optional[RecurringPattern] = None
    recurring_end_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Budget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    category_id: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    start_date: date
    end_date: date
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class Account(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    type: AccountType = AccountType.BANK
    balance: Decimal = Decimal('0.00')
    currency: str = "USD"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class MonthlySummary(BaseModel):
    month: str  # YYYY-MM format
    year: int
    month_number: int
    total_income: Decimal
    total_expenses: Decimal
    net_amount: Decimal
    transaction_count: int
    average_daily_spending: Decimal
    top_categories: List[Dict[str, Any]]
    budget_comparison: List[Dict[str, Any]]

class CategoryAnalytics(BaseModel):
    category_id: str
    category_name: str
    total_amount: Decimal
    transaction_count: int
    average_amount: Decimal
    percentage_of_total: float
    trend: str  # increasing, decreasing, stable

class DailySpending(BaseModel):
    date: date
    amount: Decimal
    transaction_count: int
    categories: List[Dict[str, Any]]

class TrendData(BaseModel):
    period: str
    income: List[Dict[str, Any]]
    expenses: List[Dict[str, Any]]
    net: List[Dict[str, Any]]
    categories: List[CategoryAnalytics]

class BudgetStatus(BaseModel):
    budget_id: str
    category_name: str
    budget_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: float
    status: str  # under, warning, over
    days_remaining: int

# Helper functions
def create_default_categories(user_id: str, cursor: Connection):
    """Create default categories for new user"""
    default_expense_categories = [
        {"name": "Food & Dining", "icon": "🍔", "color": "#ef4444"},
        {"name": "Transportation", "icon": "🚗", "color": "#f59e0b"},
        {"name": "Shopping", "icon": "🛍️", "color": "#8b5cf6"},
        {"name": "Entertainment", "icon": "🎬", "color": "#ec4899"},
        {"name": "Bills & Utilities", "icon": "💡", "color": "#3b82f6"},
        {"name": "Healthcare", "icon": "🏥", "color": "#10b981"},
        {"name": "Education", "icon": "📚", "color": "#06b6d4"},
        {"name": "Travel", "icon": "✈️", "color": "#f97316"},
        {"name": "Rent & Housing", "icon": "🏠", "color": "#84cc16"},
        {"name": "Other", "icon": "📌", "color": "#6b7280"}
    ]
    
    default_income_categories = [
        {"name": "Salary", "icon": "💰", "color": "#22c55e"},
        {"name": "Freelance", "icon": "💻", "color": "#14b8a6"},
        {"name": "Investments", "icon": "📈", "color": "#a855f7"},
        {"name": "Business", "icon": "💼", "color": "#0ea5e9"},
        {"name": "Other Income", "icon": "💵", "color": "#84cc16"}
    ]
    
    # Insert expense categories
    for cat in default_expense_categories:
        cursor.execute('''
            INSERT INTO categories (id, user_id, name, icon, color, type, is_default)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (str(uuid.uuid4()), user_id, cat["name"], cat["icon"], cat["color"], "expense"))
    
    # Insert income categories
    for cat in default_income_categories:
        cursor.execute('''
            INSERT INTO categories (id, user_id, name, icon, color, type, is_default)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (str(uuid.uuid4()), user_id, cat["name"], cat["icon"], cat["color"], "income"))

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Expense Tracker API", "version": "1.0.0"}

# Users
@app.post("/users", response_model=User)
async def create_user(user: User, db: Connection = Depends(get_db)):
    """Create a new user"""
    cursor = db.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (id, username, email, first_name, last_name, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.email, user.first_name, user.last_name, user.currency))
        
        # Create default categories for the user
        create_default_categories(user.id, cursor)
        
        db.commit()
        return user
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, db: Connection = Depends(get_db)):
    """Get user by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        currency=row["currency"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

# Categories
@app.post("/categories", response_model=Category)
async def create_category(category: Category, db: Connection = Depends(get_db)):
    """Create a new category"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO categories (id, user_id, name, description, color, icon, type, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category.id, category.user_id, category.name, category.description,
          category.color, category.icon, category.type.value, category.is_default))
    
    db.commit()
    return category

@app.get("/categories", response_model=List[Category])
async def get_categories(
    user_id: str = Query(...),
    type: Optional[CategoryType] = Query(None),
    db: Connection = Depends(get_db)
):
    """Get user's categories"""
    cursor = db.cursor()
    
    query = "SELECT * FROM categories WHERE user_id = ?"
    params = [user_id]
    
    if type:
        query += " AND type = ?"
        params.append(type.value)
    
    query += " ORDER BY name"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    categories = []
    for row in rows:
        categories.append(Category(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row["description"],
            color=row["color"],
            icon=row["icon"],
            type=row["type"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"]
        ))
    
    return categories

@app.put("/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, category_update: Dict[str, Any], db: Connection = Depends(get_db)):
    """Update category"""
    cursor = db.cursor()
    
    # Check if category exists
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in category_update.items():
        if field in ["name", "description", "color", "icon"]:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    if update_fields:
        update_values.append(category_id)
        query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        db.commit()
    
    # Return updated category
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    row = cursor.fetchone()
    
    return Category(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        description=row["description"],
        color=row["color"],
        icon=row["icon"],
        type=row["type"],
        is_default=bool(row["is_default"]),
        created_at=row["created_at"]
    )

@app.delete("/categories/{category_id}")
async def delete_category(category_id: str, db: Connection = Depends(get_db)):
    """Delete category"""
    cursor = db.cursor()
    
    # Check if category is being used by transactions
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
    transaction_count = cursor.fetchone()[0]
    
    if transaction_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with existing transactions")
    
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.commit()
    return {"message": "Category deleted successfully"}

# Transactions
@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: Transaction, db: Connection = Depends(get_db)):
    """Create a new transaction"""
    cursor = db.cursor()
    
    # Convert tags to JSON
    tags_json = json.dumps(transaction.tags) if transaction.tags else None
    
    cursor.execute('''
        INSERT INTO transactions (id, user_id, category_id, amount, description, type, 
                                 date, location, tags, receipt_url, is_recurring, 
                                 recurring_pattern, recurring_end_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (transaction.id, transaction.user_id, transaction.category_id, transaction.amount,
          transaction.description, transaction.type.value, transaction.date, transaction.location,
          tags_json, transaction.receipt_url, transaction.is_recurring,
          transaction.recurring_pattern.value if transaction.recurring_pattern else None,
          transaction.recurring_end_date))
    
    db.commit()
    return transaction

@app.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    user_id: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[str] = Query(None),
    type: Optional[TransactionType] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Connection = Depends(get_db)
):
    """Get user's transactions with filtering"""
    cursor = db.cursor()
    
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    
    if type:
        query += " AND type = ?"
        params.append(type.value)
    
    query += " ORDER BY date DESC, created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    transactions = []
    for row in rows:
        transactions.append(Transaction(
            id=row["id"],
            user_id=row["user_id"],
            category_id=row["category_id"],
            amount=row["amount"],
            description=row["description"],
            type=row["type"],
            date=row["date"],
            location=row["location"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            receipt_url=row["receipt_url"],
            is_recurring=bool(row["is_recurring"]),
            recurring_pattern=row["recurring_pattern"],
            recurring_end_date=row["recurring_end_date"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        ))
    
    return transactions

@app.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str, db: Connection = Depends(get_db)):
    """Get transaction by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return Transaction(
        id=row["id"],
        user_id=row["user_id"],
        category_id=row["category_id"],
        amount=row["amount"],
        description=row["description"],
        type=row["type"],
        date=row["date"],
        location=row["location"],
        tags=json.loads(row["tags"]) if row["tags"] else [],
        receipt_url=row["receipt_url"],
        is_recurring=bool(row["is_recurring"]),
        recurring_pattern=row["recurring_pattern"],
        recurring_end_date=row["recurring_end_date"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

@app.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: str, 
    transaction_update: Dict[str, Any], 
    db: Connection = Depends(get_db)
):
    """Update transaction"""
    cursor = db.cursor()
    
    # Check if transaction exists
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Build update query
    update_fields = []
    update_values = []
    
    for field, value in transaction_update.items():
        if field in ["category_id", "amount", "description", "date", "location", "receipt_url"]:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
        elif field == "tags":
            update_fields.append("tags = ?")
            update_values.append(json.dumps(value))
    
    if update_fields:
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now())
        update_values.append(transaction_id)
        
        query = f"UPDATE transactions SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        db.commit()
    
    # Return updated transaction
    return await get_transaction(transaction_id, db)

@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, db: Connection = Depends(get_db)):
    """Delete transaction"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.commit()
    return {"message": "Transaction deleted successfully"}

# Analytics endpoints
@app.get("/analytics/monthly-summary", response_model=MonthlySummary)
async def get_monthly_summary(
    user_id: str = Query(...),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Connection = Depends(get_db)
):
    """Get monthly summary for analytics"""
    cursor = db.cursor()
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Get total income and expenses
    cursor.execute('''
        SELECT 
            type,
            SUM(amount) as total,
            COUNT(*) as count
        FROM transactions 
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY type
    ''', (user_id, start_date, end_date))
    
    results = cursor.fetchall()
    
    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')
    transaction_count = 0
    
    for row in results:
        if row["type"] == "income":
            total_income = row["total"]
        elif row["type"] == "expense":
            total_expenses = row["total"]
        transaction_count += row["count"]
    
    net_amount = total_income - total_expenses
    
    # Calculate average daily spending
    days_in_month = (end_date - start_date).days + 1
    average_daily_spending = total_expenses / days_in_month if days_in_month > 0 else Decimal('0.00')
    
    # Get top categories
    cursor.execute('''
        SELECT 
            c.name as category_name,
            c.color,
            t.type,
            SUM(t.amount) as total_amount,
            COUNT(*) as transaction_count
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
        GROUP BY c.id, c.name, c.color, t.type
        ORDER BY total_amount DESC
        LIMIT 10
    ''', (user_id, start_date, end_date))
    
    top_categories = []
    for row in cursor.fetchall():
        top_categories.append({
            "category_name": row["category_name"],
            "color": row["color"],
            "type": row["type"],
            "total_amount": float(row["total_amount"]),
            "transaction_count": row["transaction_count"]
        })
    
    # Get budget comparison
    cursor.execute('''
        SELECT 
            b.id,
            c.name as category_name,
            b.amount as budget_amount,
            COALESCE(SUM(t.amount), 0) as spent_amount
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN transactions t ON b.category_id = t.category_id 
            AND t.user_id = b.user_id 
            AND t.date BETWEEN b.start_date AND b.end_date
            AND t.type = 'expense'
        WHERE b.user_id = ? AND b.is_active = 1
            AND ((b.start_date <= ? AND b.end_date >= ?) OR
                 (b.start_date <= ? AND b.end_date >= ?))
    ''', (user_id, start_date, end_date, start_date, end_date))
    
    budget_comparison = []
    for row in cursor.fetchall():
        budget_amount = row["budget_amount"]
        spent_amount = row["spent_amount"] or Decimal('0.00')
        remaining = budget_amount - spent_amount
        percentage_used = float(spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        
        status = "under"
        if percentage_used >= 100:
            status = "over"
        elif percentage_used >= 80:
            status = "warning"
        
        budget_comparison.append({
            "budget_id": row["id"],
            "category_name": row["category_name"],
            "budget_amount": float(budget_amount),
            "spent_amount": float(spent_amount),
            "remaining_amount": float(remaining),
            "percentage_used": percentage_used,
            "status": status
        })
    
    return MonthlySummary(
        month=f"{year}-{month:02d}",
        year=year,
        month_number=month,
        total_income=total_income,
        total_expenses=total_expenses,
        net_amount=net_amount,
        transaction_count=transaction_count,
        average_daily_spending=average_daily_spending,
        top_categories=top_categories,
        budget_comparison=budget_comparison
    )

@app.get("/analytics/category-analytics", response_model=List[CategoryAnalytics])
async def get_category_analytics(
    user_id: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    transaction_type: Optional[TransactionType] = Query(None),
    db: Connection = Depends(get_db)
):
    """Get category-wise analytics"""
    cursor = db.cursor()
    
    # Default to last 30 days if no date range provided
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    query = '''
        SELECT 
            c.id as category_id,
            c.name as category_name,
            COALESCE(SUM(t.amount), 0) as total_amount,
            COUNT(t.id) as transaction_count,
            AVG(t.amount) as average_amount
        FROM categories c
        LEFT JOIN transactions t ON c.id = t.category_id 
            AND t.user_id = c.user_id
            AND t.date BETWEEN ? AND ?
    '''
    
    params = [user_id, start_date, end_date]
    
    if transaction_type:
        query += " AND t.type = ?"
        params.append(transaction_type.value)
    
    query += '''
        WHERE c.user_id = ?
        GROUP BY c.id, c.name
        HAVING total_amount > 0
        ORDER BY total_amount DESC
    '''
    params.append(user_id)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Calculate total for percentage calculation
    total_amount = sum(row["total_amount"] for row in rows)
    
    category_analytics = []
    for row in rows:
        percentage = float(row["total_amount"] / total_amount * 100) if total_amount > 0 else 0
        
        # Simple trend calculation (compare with previous period)
        prev_start = start_date - timedelta(days=(end_date - start_date).days)
        prev_end = start_date - timedelta(days=1)
        
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as prev_amount
            FROM transactions
            WHERE user_id = ? AND category_id = ? 
                AND date BETWEEN ? AND ?
        ''', (user_id, row["category_id"], prev_start, prev_end))
        
        prev_result = cursor.fetchone()
        prev_amount = prev_result["prev_amount"] if prev_result else Decimal('0.00')
        
        trend = "stable"
        if prev_amount > 0:
            change_percent = float((row["total_amount"] - prev_amount) / prev_amount * 100)
            if change_percent > 10:
                trend = "increasing"
            elif change_percent < -10:
                trend = "decreasing"
        
        category_analytics.append(CategoryAnalytics(
            category_id=row["category_id"],
            category_name=row["category_name"],
            total_amount=row["total_amount"],
            transaction_count=row["transaction_count"],
            average_amount=row["average_amount"] or Decimal('0.00'),
            percentage_of_total=percentage,
            trend=trend
        ))
    
    return category_analytics

@app.get("/analytics/daily-spending", response_model=List[DailySpending])
async def get_daily_spending(
    user_id: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Connection = Depends(get_db)
):
    """Get daily spending data for graphs"""
    cursor = db.cursor()
    
    # Default to last 30 days
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    cursor.execute('''
        SELECT 
            date,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense_amount,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income_amount,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
    ''', (user_id, start_date, end_date))
    
    daily_data = []
    for row in cursor.fetchall():
        # Get categories for this date
        cursor.execute('''
            SELECT 
                c.name as category_name,
                c.color,
                SUM(t.amount) as amount
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.date = ? AND t.type = 'expense'
            GROUP BY c.id, c.name, c.color
            ORDER BY amount DESC
            LIMIT 5
        ''', (user_id, row["date"]))
        
        categories = []
        for cat_row in cursor.fetchall():
            categories.append({
                "category_name": cat_row["category_name"],
                "color": cat_row["color"],
                "amount": float(cat_row["amount"])
            })
        
        daily_data.append(DailySpending(
            date=row["date"],
            amount=row["expense_amount"] or Decimal('0.00'),
            transaction_count=row["transaction_count"],
            categories=categories
        ))
    
    return daily_data

@app.get("/analytics/trends", response_model=TrendData)
async def get_trends(
    user_id: str = Query(...),
    period: str = Query("monthly", regex="^(weekly|monthly|yearly)$"),
    months: int = Query(12, ge=1, le=24),
    db: Connection = Depends(get_db)
):
    """Get trend data for graphs"""
    cursor = db.cursor()
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 30)
    
    # Group by period
    if period == "weekly":
        date_format = "%Y-W%W"
        group_by = "strftime('%Y-W%W', date)"
    elif period == "monthly":
        date_format = "%Y-%m"
        group_by = "strftime('%Y-%m', date)"
    else:  # yearly
        date_format = "%Y"
        group_by = "strftime('%Y', date)"
    
    cursor.execute(f'''
        SELECT 
            {group_by} as period,
            type,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE user_id = ? AND date BETWEEN ? AND ?
        GROUP BY period, type
        ORDER BY period
    ''', (user_id, start_date, end_date))
    
    # Process results
    periods = {}
    for row in cursor.fetchall():
        period_key = row["period"]
        if period_key not in periods:
            periods[period_key] = {"income": 0, "expenses": 0, "transaction_count": 0}
        
        if row["type"] == "income":
            periods[period_key]["income"] = float(row["total_amount"])
        else:
            periods[period_key]["expenses"] = float(row["total_amount"])
        
        periods[period_key]["transaction_count"] += row["transaction_count"]
    
    # Create trend data
    income_data = []
    expense_data = []
    net_data = []
    
    for period_key in sorted(periods.keys()):
        income = periods[period_key]["income"]
        expenses = periods[period_key]["expenses"]
        net = income - expenses
        
        income_data.append({"period": period_key, "amount": income})
        expense_data.append({"period": period_key, "amount": expenses})
        net_data.append({"period": period_key, "amount": net})
    
    # Get category trends (top 5 categories)
    cursor.execute('''
        SELECT 
            c.name as category_name,
            c.color,
            SUM(t.amount) as total_amount
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
            AND t.type = 'expense'
        GROUP BY c.id, c.name, c.color
        ORDER BY total_amount DESC
        LIMIT 5
    ''', (user_id, start_date, end_date))
    
    category_trends = []
    for row in cursor.fetchall():
        category_trends.append(CategoryAnalytics(
            category_id="",  # Not needed for trends
            category_name=row["category_name"],
            total_amount=row["total_amount"],
            transaction_count=0,
            average_amount=Decimal('0.00'),
            percentage_of_total=0,  # Calculated separately
            trend="stable"
        ))
    
    return TrendData(
        period=period,
        income=income_data,
        expenses=expense_data,
        net=net_data,
        categories=category_trends
    )

@app.get("/analytics/budget-status", response_model=List[BudgetStatus])
async def get_budget_status(user_id: str = Query(...), db: Connection = Depends(get_db)):
    """Get current budget status"""
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT 
            b.id as budget_id,
            c.name as category_name,
            b.amount as budget_amount,
            b.start_date,
            b.end_date,
            COALESCE(SUM(t.amount), 0) as spent_amount
        FROM budgets b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN transactions t ON b.category_id = t.category_id 
            AND t.user_id = b.user_id 
            AND t.date BETWEEN b.start_date AND b.end_date
            AND t.type = 'expense'
        WHERE b.user_id = ? AND b.is_active = 1
            AND b.end_date >= ?
        GROUP BY b.id, c.name, b.amount, b.start_date, b.end_date
        ORDER BY b.end_date
    ''', (user_id, date.today()))
    
    budget_status = []
    for row in cursor.fetchall():
        budget_amount = row["budget_amount"]
        spent_amount = row["spent_amount"] or Decimal('0.00')
        remaining = budget_amount - spent_amount
        percentage_used = float(spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        
        # Determine status
        status = "under"
        if percentage_used >= 100:
            status = "over"
        elif percentage_used >= 80:
            status = "warning"
        
        # Calculate days remaining
        days_remaining = (row["end_date"] - date.today()).days
        
        budget_status.append(BudgetStatus(
            budget_id=row["budget_id"],
            category_name=row["category_name"] or "Uncategorized",
            budget_amount=budget_amount,
            spent_amount=spent_amount,
            remaining_amount=remaining,
            percentage_used=percentage_used,
            status=status,
            days_remaining=days_remaining
        ))
    
    return budget_status

# Budgets
@app.post("/budgets", response_model=Budget)
async def create_budget(budget: Budget, db: Connection = Depends(get_db)):
    """Create a new budget"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO budgets (id, user_id, category_id, amount, period, start_date, end_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (budget.id, budget.user_id, budget.category_id, budget.amount,
          budget.period.value, budget.start_date, budget.end_date, budget.is_active))
    
    db.commit()
    return budget

@app.get("/budgets", response_model=List[Budget])
async def get_budgets(
    user_id: str = Query(...),
    active_only: bool = Query(True),
    db: Connection = Depends(get_db)
):
    """Get user's budgets"""
    cursor = db.cursor()
    
    query = "SELECT * FROM budgets WHERE user_id = ?"
    params = [user_id]
    
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY end_date"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    budgets = []
    for row in rows:
        budgets.append(Budget(
            id=row["id"],
            user_id=row["user_id"],
            category_id=row["category_id"],
            amount=row["amount"],
            period=row["period"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"]
        ))
    
    return budgets

# Accounts
@app.post("/accounts", response_model=Account)
async def create_account(account: Account, db: Connection = Depends(get_db)):
    """Create a new account"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO accounts (id, user_id, name, type, balance, currency, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (account.id, account.user_id, account.name, account.type.value,
          account.balance, account.currency, account.is_active))
    
    db.commit()
    return account

@app.get("/accounts", response_model=List[Account])
async def get_accounts(
    user_id: str = Query(...),
    active_only: bool = Query(True),
    db: Connection = Depends(get_db)
):
    """Get user's accounts"""
    cursor = db.cursor()
    
    query = "SELECT * FROM accounts WHERE user_id = ?"
    params = [user_id]
    
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY name"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    accounts = []
    for row in rows:
        accounts.append(Account(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            type=row["type"],
            balance=row["balance"],
            currency=row["currency"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"]
        ))
    
    return accounts

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": "SQLite"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8012)
