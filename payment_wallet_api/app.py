from fastapi import FastAPI, HTTPException, Depends, Query, Body, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import sqlite3
from sqlite3 import Connection
import json
import hashlib
import secrets
from decimal import Decimal, InvalidOperation
import logging
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
import re

app = FastAPI(title="Payment Wallet API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///payment_wallet.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()

# Enums
class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WalletStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"
    SUSPENDED = "suspended"

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallets = relationship("Wallet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    wallet_number = Column(String, unique=True, nullable=False, index=True)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    pin_hash = Column(String, nullable=False)
    pin_salt = Column(String, nullable=False)
    status = Column(String, default=WalletStatus.ACTIVE)
    daily_limit = Column(Float, default=1000.0)
    monthly_limit = Column(Float, default=10000.0)
    daily_spent = Column(Float, default=0.0)
    monthly_spent = Column(Float, default=0.0)
    last_daily_reset = Column(DateTime, default=datetime.utcnow)
    last_monthly_reset = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions_sent = relationship("Transaction", foreign_keys="Transaction.sender_wallet_id", back_populates="sender_wallet")
    transactions_received = relationship("Transaction", foreign_keys="Transaction.receiver_wallet_id", back_populates="receiver_wallet")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    sender_wallet_id = Column(String, ForeignKey("wallets.id"), nullable=True)
    receiver_wallet_id = Column(String, ForeignKey("wallets.id"), nullable=True)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    description = Column(Text)
    status = Column(String, default=TransactionStatus.PENDING)
    reference_id = Column(String, unique=True, nullable=False, index=True)
    fee = Column(Float, default=0.0)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    sender_wallet = relationship("Wallet", foreign_keys=[sender_wallet_id], back_populates="transactions_sent")
    receiver_wallet = relationship("Wallet", foreign_keys=[receiver_wallet_id], back_populates="transactions_received")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime

class WalletCreate(BaseModel):
    user_id: str
    currency: str = Field("USD", regex=r'^[A-Z]{3}$')
    pin: str = Field(..., min_length=4, max_length=6, regex=r'^\d+$')
    daily_limit: Optional[float] = Field(1000.0, ge=0)
    monthly_limit: Optional[float] = Field(10000.0, ge=0)

class WalletResponse(BaseModel):
    id: str
    user_id: str
    wallet_number: str
    balance: float
    currency: str
    status: str
    daily_limit: float
    monthly_limit: float
    daily_spent: float
    monthly_spent: float
    created_at: datetime
    updated_at: datetime

class TransactionCreate(BaseModel):
    wallet_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    pin: str = Field(..., min_length=4, max_length=6, regex=r'^\d+$')

class TransferCreate(BaseModel):
    sender_wallet_id: str
    receiver_wallet_number: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)
    pin: str = Field(..., min_length=4, max_length=6, regex=r'^\d+$')

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    sender_wallet_id: Optional[str]
    receiver_wallet_id: Optional[str]
    transaction_type: str
    amount: float
    currency: str
    description: Optional[str]
    status: str
    reference_id: str
    fee: float
    created_at: datetime
    completed_at: Optional[datetime]

class WalletAuth(BaseModel):
    wallet_id: str
    pin: str = Field(..., min_length=4, max_length=6, regex=r'^\d+$')

class AddMoneyRequest(BaseModel):
    wallet_id: str
    amount: float = Field(..., gt=0, le=10000)
    description: Optional[str] = Field(None, max_length=500)
    payment_method: str = Field("card", regex=r'^(card|bank|paypal|crypto)$')

# Utility functions
def generate_wallet_number() -> str:
    """Generate unique wallet number"""
    while True:
        wallet_number = f"WA{secrets.randbelow(10**12):012d}"
        return wallet_number

def generate_reference_id() -> str:
    """Generate unique transaction reference ID"""
    return f"TXN{datetime.utcnow().strftime('%Y%m%d')}{secrets.randbelow(10**6):06d}"

def hash_pin(pin: str, salt: str) -> str:
    """Hash PIN with salt"""
    return hashlib.pbkdf2_hex(pin.encode(), salt.encode(), 100000)

def verify_pin(pin: str, pin_hash: str, salt: str) -> bool:
    """Verify PIN against hash"""
    return hash_pin(pin, salt) == pin_hash

def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def validate_wallet_limits(db: Session, wallet: Wallet, amount: float) -> Dict[str, Any]:
    """Validate wallet spending limits"""
    now = datetime.utcnow()
    
    # Reset daily limit if needed
    if (now - wallet.last_daily_reset).days >= 1:
        wallet.daily_spent = 0.0
        wallet.last_daily_reset = now
    
    # Reset monthly limit if needed
    if (now - wallet.last_monthly_reset).days >= 30:
        wallet.monthly_spent = 0.0
        wallet.last_monthly_reset = now
    
    # Check limits
    daily_available = wallet.daily_limit - wallet.daily_spent
    monthly_available = wallet.monthly_limit - wallet.monthly_spent
    
    if amount > daily_available:
        return {
            "valid": False,
            "reason": "daily_limit_exceeded",
            "available": daily_available,
            "limit": wallet.daily_limit
        }
    
    if amount > monthly_available:
        return {
            "valid": False,
            "reason": "monthly_limit_exceeded",
            "available": monthly_available,
            "limit": wallet.monthly_limit
        }
    
    return {"valid": True}

def calculate_transaction_fee(amount: float, transaction_type: str) -> float:
    """Calculate transaction fee"""
    if transaction_type == TransactionType.TRANSFER_OUT:
        return max(0.5, amount * 0.002)  # 0.2% minimum $0.5
    elif transaction_type == TransactionType.CREDIT:
        return 0.0  # No fee for adding money
    else:
        return 0.0

# Authentication
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    session = db.query(Session).filter(
        Session.token == token,
        Session.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def authenticate_wallet(wallet_id: str, pin: str, db: Session) -> Wallet:
    """Authenticate wallet with PIN"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.status != WalletStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Wallet is {wallet.status}"
        )
    
    if not verify_pin(pin, wallet.pin_hash, wallet.pin_salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN"
        )
    
    return wallet

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Payment Wallet API", "version": "1.0.0"}

# User Management
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user details"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@app.post("/auth/login")
async def login(username: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    """User login (simplified - in production, use proper password hashing)"""
    # This is a simplified login - in production, implement proper authentication
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create session
    token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    session = Session(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
        "user": UserResponse.from_orm(user)
    }

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """User logout"""
    # Delete user sessions
    db.query(Session).filter(Session.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Logged out successfully"}

# Wallet Management
@app.post("/wallets", response_model=WalletResponse)
async def create_wallet(wallet: WalletCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new wallet"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == wallet.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user already has wallet for this currency
        existing_wallet = db.query(Wallet).filter(
            Wallet.user_id == wallet.user_id,
            Wallet.currency == wallet.currency
        ).first()
        
        if existing_wallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already has a {wallet.currency} wallet"
            )
        
        # Generate wallet number and salt
        wallet_number = generate_wallet_number()
        pin_salt = secrets.token_hex(16)
        
        # Create wallet
        db_wallet = Wallet(
            user_id=wallet.user_id,
            wallet_number=wallet_number,
            pin_hash=hash_pin(wallet.pin, pin_salt),
            pin_salt=pin_salt,
            currency=wallet.currency,
            daily_limit=wallet.daily_limit,
            monthly_limit=wallet.monthly_limit
        )
        
        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)
        
        return db_wallet
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wallet creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Wallet creation failed"
        )

@app.get("/wallets/{wallet_id}", response_model=WalletResponse)
async def get_wallet(wallet_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get wallet details"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Verify ownership
    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return wallet

@app.get("/users/{user_id}/wallets", response_model=List[WalletResponse])
async def get_user_wallets(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all user wallets"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    return wallets

@app.put("/wallets/{wallet_id}/pin")
async def update_wallet_pin(
    wallet_id: str,
    old_pin: str = Body(..., min_length=4, max_length=6, regex=r'^\d+$'),
    new_pin: str = Body(..., min_length=4, max_length=6, regex=r'^\d+$'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update wallet PIN"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Verify ownership
    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Verify old PIN
    if not verify_pin(old_pin, wallet.pin_hash, wallet.pin_salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid old PIN"
        )
    
    # Update PIN
    new_pin_salt = secrets.token_hex(16)
    wallet.pin_hash = hash_pin(new_pin, new_pin_salt)
    wallet.pin_salt = new_pin_salt
    wallet.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "PIN updated successfully"}

# Transaction Management
@app.post("/wallets/add-money", response_model=TransactionResponse)
async def add_money(
    request: AddMoneyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add money to wallet"""
    try:
        # Get wallet
        wallet = db.query(Wallet).filter(Wallet.id == request.wallet_id).first()
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        
        # Verify ownership
        if wallet.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            receiver_wallet_id=request.wallet_id,
            transaction_type=TransactionType.CREDIT,
            amount=request.amount,
            currency=wallet.currency,
            description=request.description or f"Added money via {request.payment_method}",
            reference_id=generate_reference_id(),
            fee=0.0,
            status=TransactionStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
        
        # Update wallet balance
        wallet.balance += request.amount
        wallet.updated_at = datetime.utcnow()
        
        # Save transaction
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add money failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Add money failed"
        )

@app.post("/wallets/transfer", response_model=TransactionResponse)
async def transfer_money(
    transfer: TransferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer money to another wallet"""
    try:
        # Get sender wallet
        sender_wallet = db.query(Wallet).filter(Wallet.id == transfer.sender_wallet_id).first()
        if not sender_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender wallet not found"
            )
        
        # Verify ownership
        if sender_wallet.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Authenticate sender
        authenticate_wallet(transfer.sender_wallet_id, transfer.pin, db)
        
        # Get receiver wallet
        receiver_wallet = db.query(Wallet).filter(
            Wallet.wallet_number == transfer.receiver_wallet_number
        ).first()
        
        if not receiver_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver wallet not found"
            )
        
        # Check self-transfer
        if sender_wallet.id == receiver_wallet.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to same wallet"
            )
        
        # Check currency compatibility
        if sender_wallet.currency != receiver_wallet.currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currency mismatch"
            )
        
        # Calculate fee
        fee = calculate_transaction_fee(transfer.amount, TransactionType.TRANSFER_OUT)
        total_amount = transfer.amount + fee
        
        # Check balance
        if sender_wallet.balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        # Validate limits
        limit_validation = validate_wallet_limits(db, sender_wallet, transfer.amount)
        if not limit_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer limit exceeded: {limit_validation['reason']}"
            )
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            sender_wallet_id=sender_wallet.id,
            receiver_wallet_id=receiver_wallet.id,
            transaction_type=TransactionType.TRANSFER_OUT,
            amount=transfer.amount,
            currency=sender_wallet.currency,
            description=transfer.description,
            reference_id=generate_reference_id(),
            fee=fee,
            status=TransactionStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
        
        # Create receiver transaction
        receiver_transaction = Transaction(
            user_id=receiver_wallet.user_id,
            sender_wallet_id=sender_wallet.id,
            receiver_wallet_id=receiver_wallet.id,
            transaction_type=TransactionType.TRANSFER_IN,
            amount=transfer.amount,
            currency=receiver_wallet.currency,
            description=transfer.description,
            reference_id=transaction.reference_id,
            fee=0.0,
            status=TransactionStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )
        
        # Update balances
        sender_wallet.balance -= total_amount
        sender_wallet.daily_spent += transfer.amount
        sender_wallet.monthly_spent += transfer.amount
        sender_wallet.updated_at = datetime.utcnow()
        
        receiver_wallet.balance += transfer.amount
        receiver_wallet.updated_at = datetime.utcnow()
        
        # Save transactions
        db.add(transaction)
        db.add(receiver_transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer failed"
        )

@app.get("/wallets/{wallet_id}/transactions", response_model=List[TransactionResponse])
async def get_wallet_transactions(
    wallet_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    transaction_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wallet transaction history"""
    # Get wallet
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Verify ownership
    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Build query
    query = db.query(Transaction).filter(
        (Transaction.sender_wallet_id == wallet_id) | 
        (Transaction.receiver_wallet_id == wallet_id)
    )
    
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    # Get transactions
    transactions = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    
    return transactions

@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction details"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Verify ownership
    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return transaction

@app.get("/users/{user_id}/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    transaction_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user transactions"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Build query
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    # Get transactions
    transactions = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()
    
    return transactions

# Wallet Authentication
@app.post("/wallets/authenticate")
async def authenticate_wallet_endpoint(
    wallet_auth: WalletAuth,
    db: Session = Depends(get_db)
):
    """Authenticate wallet with PIN"""
    wallet = authenticate_wallet(wallet_auth.wallet_id, wallet_auth.pin, db)
    
    return {
        "authenticated": True,
        "wallet_id": wallet.id,
        "wallet_number": wallet.wallet_number,
        "balance": wallet.balance,
        "currency": wallet.currency
    }

# Analytics and Reporting
@app.get("/wallets/{wallet_id}/balance")
async def get_wallet_balance(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wallet balance"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    # Verify ownership
    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "wallet_id": wallet.id,
        "wallet_number": wallet.wallet_number,
        "balance": wallet.balance,
        "currency": wallet.currency,
        "daily_limit": wallet.daily_limit,
        "monthly_limit": wallet.monthly_limit,
        "daily_spent": wallet.daily_spent,
        "monthly_spent": wallet.monthly_spent,
        "status": wallet.status
    }

@app.get("/users/{user_id}/summary")
async def get_user_summary(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user financial summary"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get user wallets
    wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    
    # Calculate totals
    total_balance = sum(wallet.balance for wallet in wallets)
    
    # Get recent transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Get monthly stats
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.created_at >= current_month_start
    ).all()
    
    monthly_credits = sum(t.amount for t in monthly_transactions if t.transaction_type == TransactionType.CREDIT)
    monthly_debits = sum(t.amount for t in monthly_transactions if t.transaction_type in [TransactionType.DEBIT, TransactionType.TRANSFER_OUT])
    
    return {
        "user_id": user_id,
        "total_balance": total_balance,
        "wallet_count": len(wallets),
        "wallets": [
            {
                "id": w.id,
                "wallet_number": w.wallet_number,
                "balance": w.balance,
                "currency": w.currency,
                "status": w.status
            }
            for w in wallets
        ],
        "monthly_summary": {
            "credits": monthly_credits,
            "debits": monthly_debits,
            "net": monthly_credits - monthly_debits,
            "transaction_count": len(monthly_transactions)
        },
        "recent_transactions": [
            {
                "id": t.id,
                "type": t.transaction_type,
                "amount": t.amount,
                "description": t.description,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in recent_transactions
        ]
    }

# Utility Endpoints
@app.get("/currencies")
async def get_supported_currencies():
    """Get supported currencies"""
    return {
        "currencies": [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "GBP", "name": "British Pound", "symbol": "£"},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
            {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF"},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"}
        ]
    }

@app.get("/transaction-types")
async def get_transaction_types():
    """Get transaction types"""
    return {
        "transaction_types": [
            {"type": "credit", "name": "Credit", "description": "Money added to wallet"},
            {"type": "debit", "name": "Debit", "description": "Money withdrawn from wallet"},
            {"type": "transfer_out", "name": "Transfer Out", "description": "Money sent to another wallet"},
            {"type": "transfer_in", "name": "Transfer In", "description": "Money received from another wallet"}
        ]
    }

@app.get("/wallet-statuses")
async def get_wallet_statuses():
    """Get wallet statuses"""
    return {
        "statuses": [
            {"status": "active", "name": "Active", "description": "Wallet is fully functional"},
            {"status": "frozen", "name": "Frozen", "description": "Wallet is temporarily frozen"},
            {"status": "suspended", "name": "Suspended", "description": "Wallet is suspended"},
            {"status": "closed", "name": "Closed", "description": "Wallet is permanently closed"}
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database_connected": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8016)
