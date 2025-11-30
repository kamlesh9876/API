from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio
import logging
import websockets
from websockets.exceptions import ConnectionClosed
import aiohttp
import time
from collections import defaultdict
import sqlite3
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
import secrets
import hashlib

app = FastAPI(
    title="Real-Time Crypto Price API",
    description="Real-time cryptocurrency price tracking with portfolio management, WebSocket streams, and price alerts",
    version="1.0.0"
)

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
DATABASE_URL = "sqlite:///crypto_price.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class AlertType(str, Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENTAGE_CHANGE = "percentage_change"
    VOLUME_ALERT = "volume_alert"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    api_key = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"
    
    id = Column(String, primary_key=True)  # CoinGecko ID
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    current_price = Column(Float)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    price_change_24h = Column(Float)
    price_change_percentage_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio_holdings = relationship("PortfolioHolding", back_populates="cryptocurrency")
    price_history = relationship("PriceHistory", back_populates="cryptocurrency")
    alerts = relationship("Alert", back_populates="cryptocurrency")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    total_value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")

class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False)
    crypto_id = Column(String, ForeignKey("cryptocurrencies.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    average_buy_price = Column(Float)
    current_value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    cryptocurrency = relationship("Cryptocurrency", back_populates="portfolio_holdings")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False)
    crypto_id = Column(String, ForeignKey("cryptocurrencies.id"), nullable=False)
    transaction_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    crypto_id = Column(String, ForeignKey("cryptocurrencies.id"), nullable=False)
    alert_type = Column(String, nullable=False)
    target_price = Column(Float)
    percentage_change = Column(Float)
    status = Column(String, default=AlertStatus.ACTIVE)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    cryptocurrency = relationship("Cryptocurrency", back_populates="alerts")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    crypto_id = Column(String, ForeignKey("cryptocurrencies.id"), nullable=False)
    price = Column(Float, nullable=False)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="price_history")

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    api_key: str
    created_at: datetime
    updated_at: datetime

class CryptoPrice(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: Optional[float]
    volume_24h: Optional[float]
    price_change_24h: Optional[float]
    price_change_percentage_24h: Optional[float]
    last_updated: datetime

class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class PortfolioResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    total_value: float
    created_at: datetime
    updated_at: datetime

class PortfolioHoldingCreate(BaseModel):
    crypto_id: str
    quantity: float = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)

class PortfolioHoldingResponse(BaseModel):
    id: str
    portfolio_id: str
    crypto_id: str
    quantity: float
    average_buy_price: Optional[float]
    current_value: Optional[float]
    created_at: datetime
    updated_at: datetime

class TransactionCreate(BaseModel):
    crypto_id: str
    transaction_type: TransactionType
    quantity: float = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)
    fee: float = Field(0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class TransactionResponse(BaseModel):
    id: str
    portfolio_id: str
    crypto_id: str
    transaction_type: str
    quantity: float
    price_per_unit: float
    total_amount: float
    fee: float
    notes: Optional[str]
    created_at: datetime

class AlertCreate(BaseModel):
    crypto_id: str
    alert_type: AlertType
    target_price: Optional[float] = Field(None, gt=0)
    percentage_change: Optional[float] = Field(None)

class AlertResponse(BaseModel):
    id: str
    user_id: str
    crypto_id: str
    alert_type: str
    target_price: Optional[float]
    percentage_change: Optional[float]
    status: str
    notification_sent: bool
    created_at: datetime
    triggered_at: Optional[datetime]

class PriceHistoryResponse(BaseModel):
    crypto_id: str
    price: float
    market_cap: Optional[float]
    volume_24h: Optional[float]
    timestamp: datetime

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        self.user_connections[id(websocket)] = user_id

    def disconnect(self, websocket: WebSocket):
        user_id = self.user_connections.pop(id(websocket), None)
        if user_id and websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_user(self, message: str, user_id: str):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            for connection in disconnected:
                self.disconnect(connection)

    async def broadcast_price_update(self, crypto_data: Dict[str, Any]):
        message = json.dumps({
            "type": "price_update",
            "data": crypto_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Send to all connected users
        for user_id in self.active_connections:
            await self.broadcast_to_user(message, user_id)

manager = ConnectionManager()

# Utility Functions
def generate_api_key():
    """Generate secure API key"""
    return f"ck_{secrets.token_urlsafe(32)}"

async def fetch_crypto_data(crypto_ids: List[str] = None) -> Dict[str, Any]:
    """Fetch cryptocurrency data from CoinGecko API"""
    try:
        async with aiohttp.ClientSession() as session:
            if crypto_ids:
                # Fetch specific cryptocurrencies
                ids = ",".join(crypto_ids)
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
            else:
                # Fetch top 100 cryptocurrencies
                url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"CoinGecko API error: {response.status}")
                    return {}
    except Exception as e:
        logger.error(f"Error fetching crypto data: {e}")
        return {}

async def fetch_crypto_details(crypto_id: str) -> Dict[str, Any]:
    """Fetch detailed cryptocurrency information"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "id": data.get("id"),
                        "symbol": data.get("symbol", "").upper(),
                        "name": data.get("name"),
                        "description": data.get("description", {}).get("en", ""),
                        "market_cap_rank": data.get("market_cap_rank"),
                        "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                        "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                        "volume_24h": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                        "price_change_24h": data.get("market_data", {}).get("price_change_24h_in_currency", {}).get("usd"),
                        "price_change_percentage_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                        "circulating_supply": data.get("market_data", {}).get("circulating_supply"),
                        "total_supply": data.get("market_data", {}).get("total_supply"),
                        "max_supply": data.get("market_data", {}).get("max_supply"),
                        "ath": data.get("market_data", {}).get("ath", {}).get("usd"),
                        "ath_change_percentage": data.get("market_data", {}).get("ath_change_percentage", {}).get("usd"),
                        "ath_date": data.get("market_data", {}).get("ath_date", {}).get("usd"),
                        "atl": data.get("market_data", {}).get("atl", {}).get("usd"),
                        "atl_change_percentage": data.get("market_data", {}).get("atl_change_percentage", {}).get("usd"),
                        "atl_date": data.get("market_data", {}).get("atl_date", {}).get("usd"),
                        "last_updated": data.get("last_updated")
                    }
                else:
                    return {}
    except Exception as e:
        logger.error(f"Error fetching crypto details: {e}")
        return {}

def calculate_portfolio_value(portfolio_id: str, db: Session) -> float:
    """Calculate total portfolio value"""
    holdings = db.query(PortfolioHolding).filter(PortfolioHolding.portfolio_id == portfolio_id).all()
    total_value = 0.0
    
    for holding in holdings:
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == holding.crypto_id).first()
        if crypto and crypto.current_price:
            holding_value = holding.quantity * crypto.current_price
            total_value += holding_value
            # Update holding current value
            holding.current_value = holding_value
    
    db.commit()
    return total_value

async def check_price_alerts(db: Session):
    """Check and trigger price alerts"""
    alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.ACTIVE,
        Alert.notification_sent == False
    ).all()
    
    for alert in alerts:
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == alert.crypto_id).first()
        if not crypto or not crypto.current_price:
            continue
        
        triggered = False
        
        if alert.alert_type == AlertType.PRICE_ABOVE and alert.target_price:
            if crypto.current_price >= alert.target_price:
                triggered = True
        
        elif alert.alert_type == AlertType.PRICE_BELOW and alert.target_price:
            if crypto.current_price <= alert.target_price:
                triggered = True
        
        elif alert.alert_type == AlertType.PERCENTAGE_CHANGE and alert.percentage_change:
            if crypto.price_change_percentage_24h:
                if abs(crypto.price_change_percentage_24h) >= abs(alert.percentage_change):
                    triggered = True
        
        if triggered:
            alert.status = AlertStatus.TRIGGERED
            alert.triggered_at = datetime.utcnow()
            alert.notification_sent = True
            
            # Send notification via WebSocket
            notification = {
                "type": "alert_triggered",
                "alert_id": alert.id,
                "crypto_id": alert.crypto_id,
                "crypto_name": crypto.name,
                "current_price": crypto.current_price,
                "alert_type": alert.alert_type,
                "target_price": alert.target_price,
                "percentage_change": alert.percentage_change,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await manager.broadcast_to_user(json.dumps(notification), alert.user_id)
    
    db.commit()

# Background task for price updates
async def price_update_task():
    """Background task to update crypto prices"""
    while True:
        try:
            # Fetch top 100 cryptocurrencies
            crypto_data = await fetch_crypto_data()
            
            if crypto_data:
                db = SessionLocal()
                try:
                    for crypto_info in crypto_data:
                        crypto_id = crypto_info.get("id")
                        if not crypto_id:
                            continue
                        
                        # Update or create cryptocurrency record
                        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == crypto_id).first()
                        
                        if crypto:
                            old_price = crypto.current_price
                            crypto.current_price = crypto_info.get("current_price", {}).get("usd")
                            crypto.market_cap = crypto_info.get("market_cap", {}).get("usd")
                            crypto.volume_24h = crypto_info.get("total_volume", {}).get("usd")
                            crypto.price_change_24h = crypto_info.get("price_change_24h_in_currency", {}).get("usd")
                            crypto.price_change_percentage_24h = crypto_info.get("price_change_percentage_24h")
                            crypto.last_updated = datetime.utcnow()
                        else:
                            crypto = Cryptocurrency(
                                id=crypto_id,
                                symbol=crypto_info.get("symbol", "").upper(),
                                name=crypto_info.get("name"),
                                current_price=crypto_info.get("current_price", {}).get("usd"),
                                market_cap=crypto_info.get("market_cap", {}).get("usd"),
                                volume_24h=crypto_info.get("total_volume", {}).get("usd"),
                                price_change_24h=crypto_info.get("price_change_24h_in_currency", {}).get("usd"),
                                price_change_percentage_24h=crypto_info.get("price_change_percentage_24h"),
                                last_updated=datetime.utcnow()
                            )
                            db.add(crypto)
                            old_price = crypto.current_price
                        
                        # Add to price history
                        price_history = PriceHistory(
                            crypto_id=crypto_id,
                            price=crypto.current_price,
                            market_cap=crypto.market_cap,
                            volume_24h=crypto.volume_24h
                        )
                        db.add(price_history)
                        
                        # Broadcast price update if price changed significantly
                        if old_price and crypto.current_price:
                            price_change_percent = abs((crypto.current_price - old_price) / old_price) * 100
                            if price_change_percent > 0.1:  # 0.1% change threshold
                                await manager.broadcast_price_update({
                                    "id": crypto.id,
                                    "symbol": crypto.symbol,
                                    "name": crypto.name,
                                    "current_price": crypto.current_price,
                                    "price_change_24h": crypto.price_change_24h,
                                    "price_change_percentage_24h": crypto.price_change_percentage_24h,
                                    "market_cap": crypto.market_cap,
                                    "volume_24h": crypto.volume_24h
                                })
                    
                    # Update portfolio values
                    portfolios = db.query(Portfolio).all()
                    for portfolio in portfolios:
                        portfolio.total_value = calculate_portfolio_value(portfolio.id, db)
                    
                    # Check alerts
                    await check_price_alerts(db)
                    
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Database error in price update: {e}")
                    db.rollback()
                finally:
                    db.close()
            
            # Wait for next update (every 30 seconds)
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in price update task: {e}")
            await asyncio.sleep(60)  # Wait longer if error

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to Real-Time Crypto Price API",
        "version": "1.0.0",
        "features": [
            "Live crypto prices",
            "Portfolio tracking",
            "WebSocket price streams",
            "Price alerts"
        ]
    }

# User Management
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )
        
        # Create user
        db_user = User(
            username=user.username,
            email=user.email,
            api_key=generate_api_key()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(status_code=500, detail="User creation failed")

@app.get("/users/me", response_model=UserResponse)
async def get_current_user(api_key: str = Query(...), db: Session = Depends(get_db)):
    """Get current user by API key"""
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

# Cryptocurrency Prices
@app.get("/crypto/prices", response_model=List[CryptoPrice])
async def get_crypto_prices(
    limit: int = Query(100, ge=1, le=250),
    vs_currency: str = Query("usd", regex=r'^(usd|eur|gbp|jpy)$'),
    order: str = Query("market_cap_desc", regex=r'^(market_cap_desc|market_cap_asc|gecko_desc|gecko_asc|id_asc|id_desc)$'),
    db: Session = Depends(get_db)
):
    """Get cryptocurrency prices"""
    try:
        # Fetch fresh data from CoinGecko
        crypto_data = await fetch_crypto_data()
        
        if not crypto_data:
            # Fallback to database
            cryptos = db.query(Cryptocurrency).order_by(Cryptocurrency.market_cap.desc().nullslast()).limit(limit).all()
            return cryptos
        
        # Process and return fresh data
        result = []
        for crypto_info in crypto_data[:limit]:
            result.append(CryptoPrice(
                id=crypto_info.get("id"),
                symbol=crypto_info.get("symbol", "").upper(),
                name=crypto_info.get("name"),
                current_price=crypto_info.get("current_price", {}).get(vs_currency, 0),
                market_cap=crypto_info.get("market_cap", {}).get(vs_currency),
                volume_24h=crypto_info.get("total_volume", {}).get(vs_currency),
                price_change_24h=crypto_info.get("price_change_24h_in_currency", {}).get(vs_currency),
                price_change_percentage_24h=crypto_info.get("price_change_percentage_24h"),
                last_updated=datetime.utcnow()
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crypto prices")

@app.get("/crypto/{crypto_id}", response_model=CryptoPrice)
async def get_crypto_price(crypto_id: str, db: Session = Depends(get_db)):
    """Get specific cryptocurrency price"""
    try:
        # Fetch fresh data
        crypto_data = await fetch_crypto_details(crypto_id)
        
        if not crypto_data:
            # Fallback to database
            crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == crypto_id).first()
            if not crypto:
                raise HTTPException(status_code=404, detail="Cryptocurrency not found")
            return crypto
        
        return CryptoPrice(**crypto_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto price: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crypto price")

@app.get("/crypto/{crypto_id}/history", response_model=List[PriceHistoryResponse])
async def get_crypto_history(
    crypto_id: str,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get cryptocurrency price history"""
    try:
        # Get price history from database
        start_date = datetime.utcnow() - timedelta(days=days)
        history = db.query(PriceHistory).filter(
            PriceHistory.crypto_id == crypto_id,
            PriceHistory.timestamp >= start_date
        ).order_by(PriceHistory.timestamp.desc()).all()
        
        if not history:
            # Fetch from external API if no data
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        prices = data.get("prices", [])
                        
                        for price_point in prices:
                            timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                            price = price_point[1]
                            
                            history_item = PriceHistory(
                                crypto_id=crypto_id,
                                price=price,
                                timestamp=timestamp
                            )
                            db.add(history_item)
                        
                        db.commit()
                        history = db.query(PriceHistory).filter(
                            PriceHistory.crypto_id == crypto_id,
                            PriceHistory.timestamp >= start_date
                        ).order_by(PriceHistory.timestamp.desc()).all()
        
        return history
        
    except Exception as e:
        logger.error(f"Error fetching crypto history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch crypto history")

# Portfolio Management
@app.post("/portfolios", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio: PortfolioCreate,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    try:
        # Get user
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Create portfolio
        db_portfolio = Portfolio(
            user_id=user.id,
            name=portfolio.name,
            description=portfolio.description
        )
        
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        
        return db_portfolio
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio creation failed: {e}")
        raise HTTPException(status_code=500, detail="Portfolio creation failed")

@app.get("/portfolios", response_model=List[PortfolioResponse])
async def get_portfolios(api_key: str = Query(...), db: Session = Depends(get_db)):
    """Get user portfolios"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        return portfolios
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolios")

@app.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get specific portfolio"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return portfolio
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio")

@app.post("/portfolios/{portfolio_id}/holdings", response_model=PortfolioHoldingResponse)
async def add_holding(
    portfolio_id: str,
    holding: PortfolioHoldingCreate,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Add holding to portfolio"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Check if cryptocurrency exists
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == holding.crypto_id).first()
        if not crypto:
            # Fetch crypto data
            crypto_data = await fetch_crypto_details(holding.crypto_id)
            if not crypto_data:
                raise HTTPException(status_code=400, detail="Invalid cryptocurrency")
            
            crypto = Cryptocurrency(
                id=holding.crypto_id,
                symbol=crypto_data.get("symbol", "").upper(),
                name=crypto_data.get("name"),
                current_price=crypto_data.get("current_price"),
                last_updated=datetime.utcnow()
            )
            db.add(crypto)
            db.commit()
        
        # Check if holding already exists
        existing_holding = db.query(PortfolioHolding).filter(
            PortfolioHolding.portfolio_id == portfolio_id,
            PortfolioHolding.crypto_id == holding.crypto_id
        ).first()
        
        if existing_holding:
            # Update existing holding
            total_quantity = existing_holding.quantity + holding.quantity
            total_cost = (existing_holding.quantity * existing_holding.average_buy_price) + (holding.quantity * holding.price_per_unit)
            existing_holding.quantity = total_quantity
            existing_holding.average_buy_price = total_cost / total_quantity
            existing_holding.updated_at = datetime.utcnow()
            
            # Create transaction record
            transaction = Transaction(
                portfolio_id=portfolio_id,
                crypto_id=holding.crypto_id,
                transaction_type=TransactionType.BUY,
                quantity=holding.quantity,
                price_per_unit=holding.price_per_unit,
                total_amount=holding.quantity * holding.price_per_unit
            )
            db.add(transaction)
            
            db.commit()
            db.refresh(existing_holding)
            return existing_holding
        else:
            # Create new holding
            db_holding = PortfolioHolding(
                portfolio_id=portfolio_id,
                crypto_id=holding.crypto_id,
                quantity=holding.quantity,
                average_buy_price=holding.price_per_unit
            )
            
            db.add(db_holding)
            
            # Create transaction record
            transaction = Transaction(
                portfolio_id=portfolio_id,
                crypto_id=holding.crypto_id,
                transaction_type=TransactionType.BUY,
                quantity=holding.quantity,
                price_per_unit=holding.price_per_unit,
                total_amount=holding.quantity * holding.price_per_unit
            )
            db.add(transaction)
            
            db.commit()
            db.refresh(db_holding)
            return db_holding
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding holding: {e}")
        raise HTTPException(status_code=500, detail="Failed to add holding")

@app.get("/portfolios/{portfolio_id}/holdings", response_model=List[PortfolioHoldingResponse])
async def get_portfolio_holdings(
    portfolio_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get portfolio holdings"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = db.query(PortfolioHolding).filter(PortfolioHolding.portfolio_id == portfolio_id).all()
        
        # Update current values
        for holding in holdings:
            crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == holding.crypto_id).first()
            if crypto and crypto.current_price:
                holding.current_value = holding.quantity * crypto.current_price
        
        db.commit()
        
        return holdings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching holdings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch holdings")

@app.get("/portfolios/{portfolio_id}/summary")
async def get_portfolio_summary(
    portfolio_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get portfolio summary with detailed analytics"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get holdings
        holdings = db.query(PortfolioHolding).filter(PortfolioHolding.portfolio_id == portfolio_id).all()
        
        total_value = 0.0
        total_cost = 0.0
        holdings_summary = []
        
        for holding in holdings:
            crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == holding.crypto_id).first()
            if crypto and crypto.current_price:
                current_value = holding.quantity * crypto.current_price
                cost = holding.quantity * holding.average_buy_price if holding.average_buy_price else 0
                profit_loss = current_value - cost
                profit_loss_percentage = (profit_loss / cost * 100) if cost > 0 else 0
                
                holdings_summary.append({
                    "crypto_id": holding.crypto_id,
                    "crypto_name": crypto.name,
                    "crypto_symbol": crypto.symbol,
                    "quantity": holding.quantity,
                    "average_buy_price": holding.average_buy_price,
                    "current_price": crypto.current_price,
                    "current_value": current_value,
                    "cost_basis": cost,
                    "profit_loss": profit_loss,
                    "profit_loss_percentage": profit_loss_percentage,
                    "price_change_24h": crypto.price_change_24h,
                    "price_change_percentage_24h": crypto.price_change_percentage_24h
                })
                
                total_value += current_value
                total_cost += cost
        
        portfolio.total_value = total_value
        db.commit()
        
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "total_value": total_value,
            "total_cost": total_cost,
            "total_profit_loss": total_value - total_cost,
            "total_profit_loss_percentage": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            "holdings_count": len(holdings),
            "holdings": holdings_summary,
            "last_updated": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio summary")

# Transactions
@app.get("/portfolios/{portfolio_id}/transactions", response_model=List[TransactionResponse])
async def get_portfolio_transactions(
    portfolio_id: str,
    api_key: str = Query(...),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get portfolio transactions"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        transactions = db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id
        ).order_by(Transaction.created_at.desc()).limit(limit).all()
        
        return transactions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")

# Alerts
@app.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Create price alert"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Validate alert parameters
        if alert.alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW] and not alert.target_price:
            raise HTTPException(status_code=400, detail="Target price is required for price alerts")
        
        if alert.alert_type == AlertType.PERCENTAGE_CHANGE and not alert.percentage_change:
            raise HTTPException(status_code=400, detail="Percentage change is required for percentage alerts")
        
        # Check if cryptocurrency exists
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == alert.crypto_id).first()
        if not crypto:
            # Fetch crypto data
            crypto_data = await fetch_crypto_details(alert.crypto_id)
            if not crypto_data:
                raise HTTPException(status_code=400, detail="Invalid cryptocurrency")
            
            crypto = Cryptocurrency(
                id=alert.crypto_id,
                symbol=crypto_data.get("symbol", "").upper(),
                name=crypto_data.get("name"),
                current_price=crypto_data.get("current_price"),
                last_updated=datetime.utcnow()
            )
            db.add(crypto)
            db.commit()
        
        # Create alert
        db_alert = Alert(
            user_id=user.id,
            crypto_id=alert.crypto_id,
            alert_type=alert.alert_type,
            target_price=alert.target_price,
            percentage_change=alert.percentage_change
        )
        
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        return db_alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert")

@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    api_key: str = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get user alerts"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        query = db.query(Alert).filter(Alert.user_id == user.id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        alerts = query.order_by(Alert.created_at.desc()).all()
        return alerts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@app.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    api_key: str = Query(...),
    db: Session = Depends(get_db)
):
    """Delete alert"""
    try:
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        alert = db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == user.id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        db.delete(alert)
        db.commit()
        
        return {"message": "Alert deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete alert")

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, api_key: str = Query(...)):
    """WebSocket endpoint for real-time price updates"""
    try:
        # Validate API key
        db = SessionLocal()
        user = db.query(User).filter(User.api_key == api_key).first()
        db.close()
        
        if not user:
            await websocket.close(code=4001, reason="Invalid API key")
            return
        
        await manager.connect(websocket, user.id)
        
        # Send initial data
        initial_data = {
            "type": "connected",
            "user_id": user.id,
            "message": "Connected to real-time price stream",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(json.dumps(initial_data), websocket)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    response = {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(response), websocket)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Utility Endpoints
@app.get("/search/crypto")
async def search_crypto(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search cryptocurrencies"""
    try:
        # Search in database first
        cryptos = db.query(Cryptocurrency).filter(
            Cryptocurrency.name.ilike(f"%{query}%") |
            Cryptocurrency.symbol.ilike(f"%{query}%")
        ).limit(limit).all()
        
        if cryptos:
            return cryptos
        
        # Search via CoinGecko API
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/search?query={query}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    coins = data.get("coins", [])[:limit]
                    
                    result = []
                    for coin in coins:
                        result.append({
                            "id": coin.get("id"),
                            "name": coin.get("name"),
                            "symbol": coin.get("symbol", "").upper(),
                            "market_cap_rank": coin.get("market_cap_rank")
                        })
                    
                    return result
        
        return []
        
    except Exception as e:
        logger.error(f"Error searching crypto: {e}")
        raise HTTPException(status_code=500, detail="Failed to search cryptocurrencies")

@app.get("/market/overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """Get market overview statistics"""
    try:
        # Get top cryptocurrencies
        top_cryptos = db.query(Cryptocurrency).order_by(Cryptocurrency.market_cap.desc().nullslast()).limit(10).all()
        
        # Calculate market statistics
        total_market_cap = sum(crypto.market_cap for crypto in top_cryptos if crypto.market_cap)
        total_volume = sum(crypto.volume_24h for crypto in top_cryptos if crypto.volume_24h)
        
        # Count gainers and losers
        gainers = [crypto for crypto in top_cryptos if crypto.price_change_percentage_24h and crypto.price_change_percentage_24h > 0]
        losers = [crypto for crypto in top_cryptos if crypto.price_change_percentage_24h and crypto.price_change_percentage_24h < 0]
        
        return {
            "total_market_cap": total_market_cap,
            "total_volume_24h": total_volume,
            "top_cryptos": [
                {
                    "id": crypto.id,
                    "name": crypto.name,
                    "symbol": crypto.symbol,
                    "current_price": crypto.current_price,
                    "market_cap": crypto.market_cap,
                    "price_change_percentage_24h": crypto.price_change_percentage_24h
                }
                for crypto in top_cryptos
            ],
            "market_stats": {
                "gainers_count": len(gainers),
                "losers_count": len(losers),
                "top_gainer": max(gainers, key=lambda x: x.price_change_percentage_24h) if gainers else None,
                "top_loser": min(losers, key=lambda x: x.price_change_percentage_24h) if losers else None
            },
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market overview")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "websocket_connections": len(manager.active_connections),
        "active_users": len(manager.active_connections)
    }

# Start background task
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    # Start price update task
    asyncio.create_task(price_update_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
