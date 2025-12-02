from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import hashlib
import time
from datetime import datetime, timedelta
from enum import Enum
import random

app = FastAPI(title="Cryptocurrency Trading API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class TimeInForce(str, Enum):
    GTC = "good_til_canceled"
    IOC = "immediate_or_cancel"
    FOK = "fill_or_kill"
    DAY = "day"

# Data models
class Cryptocurrency(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    volume_24h: float
    change_24h: float
    change_7d: float
    circulating_supply: float
    max_supply: Optional[float] = None
    last_updated: datetime

class TradingPair(BaseModel):
    id: str
    base_symbol: str
    quote_symbol: str
    symbol: str  # e.g., "BTC/USD"
    current_price: float
    bid_price: float
    ask_price: float
    volume_24h: float
    high_24h: float
    low_24h: float
    change_24h: float
    last_updated: datetime

class Order(BaseModel):
    id: str
    user_id: str
    pair_symbol: str
    order_type: OrderType
    order_side: OrderSide
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    average_fill_price: float = 0.0
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

class Trade(BaseModel):
    id: str
    order_id: str
    user_id: str
    pair_symbol: str
    side: OrderSide
    quantity: float
    price: float
    fee: float
    fee_currency: str
    timestamp: datetime

class Wallet(BaseModel):
    id: str
    user_id: str
    currency: str
    balance: float
    available_balance: float
    locked_balance: float
    created_at: datetime
    updated_at: datetime

class Portfolio(BaseModel):
    id: str
    user_id: str
    total_value_usd: float
    total_value_change_24h: float
    total_value_change_7d: float
    allocations: Dict[str, float]  # currency -> percentage
    created_at: datetime
    updated_at: datetime

class TradingBot(BaseModel):
    id: str
    user_id: str
    name: str
    strategy: str
    pair_symbol: str
    enabled: bool
    parameters: Dict[str, Any]
    performance: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    last_run: Optional[datetime] = None

class PriceAlert(BaseModel):
    id: str
    user_id: str
    cryptocurrency_id: str
    alert_type: str  # "price_above", "price_below", "percentage_change"
    target_price: Optional[float] = None
    target_percentage: Optional[float] = None
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

# In-memory storage
cryptocurrencies: Dict[str, Cryptocurrency] = {}
trading_pairs: Dict[str, TradingPair] = {}
orders: Dict[str, Order] = {}
trades: Dict[str, Trade] = {}
wallets: Dict[str, Wallet] = {}
portfolios: Dict[str, Portfolio] = {}
trading_bots: Dict[str, TradingBot] = {}
price_alerts: Dict[str, PriceAlert] = {}
order_books: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}  # bids and asks
websocket_connections: Dict[str, WebSocket] = {}

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

    async def send_to_client(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Utility functions
def generate_order_id() -> str:
    """Generate unique order ID"""
    return f"order_{uuid.uuid4().hex[:8]}"

def generate_trade_id() -> str:
    """Generate unique trade ID"""
    return f"trade_{uuid.uuid4().hex[:8]}"

def generate_wallet_id() -> str:
    """Generate unique wallet ID"""
    return f"wallet_{uuid.uuid4().hex[:8]}"

def generate_bot_id() -> str:
    """Generate unique bot ID"""
    return f"bot_{uuid.uuid4().hex[:8]}"

def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return f"alert_{uuid.uuid4().hex[:8]}"

def calculate_fee(amount: float, fee_rate: float = 0.001) -> float:
    """Calculate trading fee"""
    return amount * fee_rate

def update_order_book(pair_symbol: str, order: Order):
    """Update order book with new order"""
    if pair_symbol not in order_books:
        order_books[pair_symbol] = {"bids": [], "asks": []}
    
    order_book = order_books[pair_symbol]
    
    if order.status == OrderStatus.OPEN:
        order_data = {
            "order_id": order.id,
            "price": order.price,
            "quantity": order.remaining_quantity,
            "timestamp": order.created_at.isoformat()
        }
        
        if order.order_side == OrderSide.BUY:
            order_book["bids"].append(order_data)
            order_book["bids"].sort(key=lambda x: (-x["price"], x["timestamp"]))
        else:
            order_book["asks"].append(order_data)
            order_book["asks"].sort(key=lambda x: (x["price"], x["timestamp"]))
    
    # Remove filled or cancelled orders
    for side in ["bids", "asks"]:
        order_book[side] = [
            o for o in order_book[side] 
            if orders.get(o["order_id"], Order()).status == OrderStatus.OPEN
        ]

async def match_orders(pair_symbol: str):
    """Match orders in the order book"""
    if pair_symbol not in order_books:
        return
    
    order_book = order_books[pair_symbol]
    bids = order_book["bids"]
    asks = order_book["asks"]
    
    while bids and asks:
        best_bid = bids[0]
        best_ask = asks[0]
        
        if best_bid["price"] >= best_ask["price"]:
            # Match found
            bid_order = orders[best_bid["order_id"]]
            ask_order = orders[best_ask["order_id"]]
            
            trade_quantity = min(bid_order.remaining_quantity, ask_order.remaining_quantity)
            trade_price = best_ask["price"]  # Use ask price for taker
            
            # Create trades for both orders
            await create_trade(bid_order.id, bid_order.user_id, pair_symbol, OrderSide.BUY, trade_quantity, trade_price)
            await create_trade(ask_order.id, ask_order.user_id, pair_symbol, OrderSide.SELL, trade_quantity, trade_price)
            
            # Update orders
            bid_order.filled_quantity += trade_quantity
            bid_order.remaining_quantity -= trade_quantity
            bid_order.updated_at = datetime.now()
            
            ask_order.filled_quantity += trade_quantity
            ask_order.remaining_quantity -= trade_quantity
            ask_order.updated_at = datetime.now()
            
            # Calculate average fill price
            if bid_order.filled_quantity > 0:
                bid_order.average_fill_price = (
                    (bid_order.average_fill_price * (bid_order.filled_quantity - trade_quantity) + trade_price * trade_quantity) /
                    bid_order.filled_quantity
                )
            
            if ask_order.filled_quantity > 0:
                ask_order.average_fill_price = (
                    (ask_order.average_fill_price * (ask_order.filled_quantity - trade_quantity) + trade_price * trade_quantity) /
                    ask_order.filled_quantity
                )
            
            # Update order status if fully filled
            if bid_order.remaining_quantity <= 0.00000001:  # Account for floating point precision
                bid_order.status = OrderStatus.FILLED
                bids.pop(0)
            
            if ask_order.remaining_quantity <= 0.00000001:
                ask_order.status = OrderStatus.FILLED
                asks.pop(0)
            
            # Update order book
            update_order_book(pair_symbol, bid_order)
            update_order_book(pair_symbol, ask_order)
            
            # Broadcast trade
            trade_message = {
                "type": "trade",
                "pair_symbol": pair_symbol,
                "price": trade_price,
                "quantity": trade_quantity,
                "timestamp": datetime.now().isoformat()
            }
            await manager.broadcast(trade_message)
            
        else:
            break  # No more matches possible

async def create_trade(order_id: str, user_id: str, pair_symbol: str, side: OrderSide, quantity: float, price: float):
    """Create a trade record"""
    trade_id = generate_trade_id()
    fee = calculate_fee(quantity * price)
    
    trade = Trade(
        id=trade_id,
        order_id=order_id,
        user_id=user_id,
        pair_symbol=pair_symbol,
        side=side,
        quantity=quantity,
        price=price,
        fee=fee,
        fee_currency="USD",
        timestamp=datetime.now()
    )
    
    trades[trade_id] = trade
    
    # Update wallet balances
    await update_wallet_balance(user_id, pair_symbol, side, quantity, price, fee)

async def update_wallet_balance(user_id: str, pair_symbol: str, side: OrderSide, quantity: float, price: float, fee: float):
    """Update wallet balances after trade"""
    base_currency, quote_currency = pair_symbol.split("/")
    
    # Get or create wallets
    base_wallet = get_or_create_wallet(user_id, base_currency)
    quote_wallet = get_or_create_wallet(user_id, quote_currency)
    
    if side == OrderSide.BUY:
        # Buying: subtract quote currency, add base currency
        total_cost = quantity * price + fee
        quote_wallet.balance -= total_cost
        quote_wallet.available_balance -= total_cost
        base_wallet.balance += quantity
        base_wallet.available_balance += quantity
    else:
        # Selling: subtract base currency, add quote currency
        total_received = quantity * price - fee
        base_wallet.balance -= quantity
        base_wallet.available_balance -= quantity
        quote_wallet.balance += total_received
        quote_wallet.available_balance += total_received
    
    base_wallet.updated_at = datetime.now()
    quote_wallet.updated_at = datetime.now()

def get_or_create_wallet(user_id: str, currency: str) -> Wallet:
    """Get or create wallet for user and currency"""
    wallet_id = f"{user_id}_{currency}"
    
    if wallet_id not in wallets:
        wallet = Wallet(
            id=wallet_id,
            user_id=user_id,
            currency=currency,
            balance=0.0,
            available_balance=0.0,
            locked_balance=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        wallets[wallet_id] = wallet
    
    return wallets[wallet_id]

# Initialize sample data
def initialize_sample_data():
    """Initialize sample cryptocurrency and trading pair data"""
    # Sample cryptocurrencies
    crypto_data = [
        {"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.0, "market_cap": 850000000000, "volume_24h": 25000000000, "change_24h": 2.5, "change_7d": 5.2, "circulating_supply": 19000000, "max_supply": 21000000},
        {"symbol": "ETH", "name": "Ethereum", "current_price": 3200.0, "market_cap": 380000000000, "volume_24h": 15000000000, "change_24h": 3.1, "change_7d": 8.7, "circulating_supply": 118000000},
        {"symbol": "BNB", "name": "Binance Coin", "current_price": 420.0, "market_cap": 65000000000, "volume_24h": 1200000000, "change_24h": -1.2, "change_7d": 3.4, "circulating_supply": 155000000},
        {"symbol": "ADA", "name": "Cardano", "current_price": 1.25, "market_cap": 40000000000, "volume_24h": 800000000, "change_24h": 4.5, "change_7d": 12.3, "circulating_supply": 32000000000},
        {"symbol": "SOL", "name": "Solana", "current_price": 125.0, "market_cap": 35000000000, "volume_24h": 2000000000, "change_24h": -0.8, "change_7d": 6.1, "circulating_supply": 280000000}
    ]
    
    for crypto in crypto_data:
        crypto_id = f"crypto_{crypto['symbol'].lower()}"
        cryptocurrency = Cryptocurrency(
            id=crypto_id,
            **crypto,
            last_updated=datetime.now()
        )
        cryptocurrencies[crypto_id] = cryptocurrency
    
    # Sample trading pairs
    pairs = [
        {"base_symbol": "BTC", "quote_symbol": "USD", "symbol": "BTC/USD", "current_price": 45000.0, "bid_price": 44990.0, "ask_price": 45010.0, "volume_24h": 25000000000, "high_24h": 46000.0, "low_24h": 44000.0, "change_24h": 2.5},
        {"base_symbol": "ETH", "quote_symbol": "USD", "symbol": "ETH/USD", "current_price": 3200.0, "bid_price": 3195.0, "ask_price": 3205.0, "volume_24h": 15000000000, "high_24h": 3300.0, "low_24h": 3100.0, "change_24h": 3.1},
        {"base_symbol": "BTC", "quote_symbol": "ETH", "symbol": "BTC/ETH", "current_price": 14.06, "bid_price": 14.05, "ask_price": 14.07, "volume_24h": 500000000, "high_24h": 14.5, "low_24h": 13.8, "change_24h": 1.2}
    ]
    
    for pair in pairs:
        pair_id = f"pair_{pair['symbol'].replace('/', '_').lower()}"
        trading_pair = TradingPair(
            id=pair_id,
            **pair,
            last_updated=datetime.now()
        )
        trading_pairs[pair_id] = trading_pair
        order_books[pair["symbol"]] = {"bids": [], "asks": []}

# Initialize sample data
initialize_sample_data()

# Background task for price updates and order matching
async def market_data_updater():
    """Background task to update market data and match orders"""
    while True:
        # Update prices (mock data)
        for crypto in cryptocurrencies.values():
            # Random price movement
            change_percent = random.uniform(-0.5, 0.5)
            crypto.current_price *= (1 + change_percent / 100)
            crypto.change_24h += change_percent / 10
            crypto.last_updated = datetime.now()
        
        # Update trading pairs
        for pair in trading_pairs.values():
            crypto = next((c for c in cryptocurrencies.values() if c.symbol == pair.base_symbol), None)
            if crypto:
                pair.current_price = crypto.current_price
                pair.bid_price = pair.current_price * 0.9995
                pair.ask_price = pair.current_price * 1.0005
                pair.last_updated = datetime.now()
        
        # Match orders
        for pair_symbol in order_books:
            await match_orders(pair_symbol)
        
        # Check price alerts
        await check_price_alerts()
        
        await asyncio.sleep(5)  # Update every 5 seconds

async def check_price_alerts():
    """Check and trigger price alerts"""
    for alert in price_alerts.values():
        if not alert.is_active:
            continue
        
        crypto = cryptocurrencies.get(alert.cryptocurrency_id)
        if not crypto:
            continue
        
        triggered = False
        
        if alert.alert_type == "price_above" and alert.target_price:
            if crypto.current_price >= alert.target_price:
                triggered = True
        elif alert.alert_type == "price_below" and alert.target_price:
            if crypto.current_price <= alert.target_price:
                triggered = True
        elif alert.alert_type == "percentage_change" and alert.target_percentage:
            if abs(crypto.change_24h) >= alert.target_percentage:
                triggered = True
        
        if triggered:
            alert.triggered_at = datetime.now()
            alert.is_active = False
            
            # Send notification
            message = {
                "type": "price_alert_triggered",
                "alert": alert.dict(),
                "current_price": crypto.current_price,
                "timestamp": datetime.now().isoformat()
            }
            await manager.broadcast(message)

# Start background task
asyncio.create_task(market_data_updater())

# API Endpoints
@app.get("/api/cryptocurrencies", response_model=List[Cryptocurrency])
async def get_cryptocurrencies(limit: int = 50, sort_by: str = "market_cap"):
    """Get all cryptocurrencies"""
    crypto_list = list(cryptocurrencies.values())
    
    # Sort
    if sort_by == "market_cap":
        crypto_list.sort(key=lambda x: x.market_cap, reverse=True)
    elif sort_by == "price":
        crypto_list.sort(key=lambda x: x.current_price, reverse=True)
    elif sort_by == "volume":
        crypto_list.sort(key=lambda x: x.volume_24h, reverse=True)
    elif sort_by == "change_24h":
        crypto_list.sort(key=lambda x: x.change_24h, reverse=True)
    
    return crypto_list[:limit]

@app.get("/api/cryptocurrencies/{crypto_id}", response_model=Cryptocurrency)
async def get_cryptocurrency(crypto_id: str):
    """Get specific cryptocurrency"""
    if crypto_id not in cryptocurrencies:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    return cryptocurrencies[crypto_id]

@app.get("/api/trading-pairs", response_model=List[TradingPair])
async def get_trading_pairs(limit: int = 50):
    """Get all trading pairs"""
    pairs = list(trading_pairs.values())
    pairs.sort(key=lambda x: x.volume_24h, reverse=True)
    return pairs[:limit]

@app.get("/api/trading-pairs/{pair_symbol}/orderbook")
async def get_order_book(pair_symbol: str, limit: int = 20):
    """Get order book for trading pair"""
    if pair_symbol not in order_books:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    order_book = order_books[pair_symbol]
    
    return {
        "pair_symbol": pair_symbol,
        "bids": order_book["bids"][:limit],
        "asks": order_book["asks"][:limit],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/orders", response_model=Order)
async def create_order(
    user_id: str,
    pair_symbol: str,
    order_type: OrderType,
    order_side: OrderSide,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
    time_in_force: TimeInForce = TimeInForce.GTC,
    expires_hours: Optional[int] = None
):
    """Create a new order"""
    if pair_symbol not in order_books:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    
    # Validate order
    if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.TAKE_PROFIT] and price is None:
        raise HTTPException(status_code=400, detail="Price is required for limit orders")
    
    if order_type in [OrderType.STOP_LOSS, OrderType.STOP_LIMIT] and stop_price is None:
        raise HTTPException(status_code=400, detail="Stop price is required for stop orders")
    
    # Check wallet balance
    base_currency, quote_currency = pair_symbol.split("/")
    
    if order_side == OrderSide.BUY:
        required_balance = quantity * (price or 0) if order_type != OrderType.MARKET else quantity * trading_pairs[f"pair_{pair_symbol.replace('/', '_').lower()}"].current_price
        wallet = get_or_create_wallet(user_id, quote_currency)
        if wallet.available_balance < required_balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Lock balance
        wallet.available_balance -= required_balance
        wallet.locked_balance += required_balance
    else:
        wallet = get_or_create_wallet(user_id, base_currency)
        if wallet.available_balance < quantity:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Lock balance
        wallet.available_balance -= quantity
        wallet.locked_balance += quantity
    
    order_id = generate_order_id()
    expires_at = None
    if expires_hours:
        expires_at = datetime.now() + timedelta(hours=expires_hours)
    
    order = Order(
        id=order_id,
        user_id=user_id,
        pair_symbol=pair_symbol,
        order_type=order_type,
        order_side=order_side,
        quantity=quantity,
        remaining_quantity=quantity,
        price=price,
        stop_price=stop_price,
        time_in_force=time_in_force,
        status=OrderStatus.OPEN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=expires_at
    )
    
    orders[order_id] = order
    update_order_book(pair_symbol, order)
    
    # Match orders immediately
    await match_orders(pair_symbol)
    
    return order

@app.get("/api/orders", response_model=List[Order])
async def get_orders(
    user_id: str,
    pair_symbol: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    limit: int = 50
):
    """Get user's orders"""
    filtered_orders = [o for o in orders.values() if o.user_id == user_id]
    
    if pair_symbol:
        filtered_orders = [o for o in filtered_orders if o.pair_symbol == pair_symbol]
    
    if status:
        filtered_orders = [o for o in filtered_orders if o.status == status]
    
    return sorted(filtered_orders, key=lambda x: x.created_at, reverse=True)[:limit]

@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get specific order"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders[order_id]

@app.delete("/api/orders/{order_id}")
async def cancel_order(order_id: str, user_id: str):
    """Cancel an order"""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders[order_id]
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Order does not belong to user")
    
    if order.status not in [OrderStatus.OPEN, OrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="Cannot cancel filled or cancelled order")
    
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.now()
    
    # Unlock balance
    base_currency, quote_currency = order.pair_symbol.split("/")
    
    if order.order_side == OrderSide.BUY:
        wallet = get_or_create_wallet(user_id, quote_currency)
        locked_amount = order.remaining_quantity * (order.price or 0)
        wallet.locked_balance -= locked_amount
        wallet.available_balance += locked_amount
    else:
        wallet = get_or_create_wallet(user_id, base_currency)
        wallet.locked_balance -= order.remaining_quantity
        wallet.available_balance += order.remaining_quantity
    
    # Update order book
    update_order_book(order.pair_symbol, order)
    
    return {"message": "Order cancelled successfully"}

@app.get("/api/trades", response_model=List[Trade])
async def get_trades(
    user_id: str,
    pair_symbol: Optional[str] = None,
    limit: int = 50,
    hours: int = 24
):
    """Get user's trades"""
    since_time = datetime.now() - timedelta(hours=hours)
    filtered_trades = [
        t for t in trades.values() 
        if t.user_id == user_id and t.timestamp >= since_time
    ]
    
    if pair_symbol:
        filtered_trades = [t for t in filtered_trades if t.pair_symbol == pair_symbol]
    
    return sorted(filtered_trades, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.get("/api/wallets", response_model=List[Wallet])
async def get_wallets(user_id: str):
    """Get user's wallets"""
    return [w for w in wallets.values() if w.user_id == user_id]

@app.get("/api/wallets/{wallet_id}", response_model=Wallet)
async def get_wallet(wallet_id: str):
    """Get specific wallet"""
    if wallet_id not in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallets[wallet_id]

@app.get("/api/portfolio", response_model=Portfolio)
async def get_portfolio(user_id: str):
    """Get user's portfolio"""
    user_wallets = [w for w in wallets.values() if w.user_id == user_id]
    
    total_value = 0.0
    allocations = {}
    
    for wallet in user_wallets:
        if wallet.currency == "USD":
            value = wallet.balance
        else:
            crypto = next((c for c in cryptocurrencies.values() if c.symbol == wallet.currency), None)
            value = wallet.balance * (crypto.current_price if crypto else 0)
        
        total_value += value
        if value > 0:
            allocations[wallet.currency] = (value / total_value) * 100
    
    portfolio_id = f"portfolio_{user_id}"
    
    portfolio = Portfolio(
        id=portfolio_id,
        user_id=user_id,
        total_value_usd=total_value,
        total_value_change_24h=0.0,  # Would calculate from historical data
        total_value_change_7d=0.0,
        allocations=allocations,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    return portfolio

@app.post("/api/trading-bots", response_model=TradingBot)
async def create_trading_bot(
    user_id: str,
    name: str,
    strategy: str,
    pair_symbol: str,
    parameters: Dict[str, Any]
):
    """Create a trading bot"""
    bot_id = generate_bot_id()
    
    bot = TradingBot(
        id=bot_id,
        user_id=user_id,
        name=name,
        strategy=strategy,
        pair_symbol=pair_symbol,
        enabled=True,
        parameters=parameters,
        performance={"win_rate": 0.0, "total_profit": 0.0, "total_trades": 0},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    trading_bots[bot_id] = bot
    return bot

@app.get("/api/trading-bots", response_model=List[TradingBot])
async def get_trading_bots(user_id: str):
    """Get user's trading bots"""
    return [b for b in trading_bots.values() if b.user_id == user_id]

@app.post("/api/price-alerts", response_model=PriceAlert)
async def create_price_alert(
    user_id: str,
    cryptocurrency_id: str,
    alert_type: str,
    target_price: Optional[float] = None,
    target_percentage: Optional[float] = None
):
    """Create a price alert"""
    alert_id = generate_alert_id()
    
    alert = PriceAlert(
        id=alert_id,
        user_id=user_id,
        cryptocurrency_id=cryptocurrency_id,
        alert_type=alert_type,
        target_price=target_price,
        target_percentage=target_percentage,
        is_active=True,
        created_at=datetime.now()
    )
    
    price_alerts[alert_id] = alert
    return alert

@app.get("/api/price-alerts", response_model=List[PriceAlert])
async def get_price_alerts(user_id: str, active_only: bool = False):
    """Get user's price alerts"""
    filtered_alerts = [a for a in price_alerts.values() if a.user_id == user_id]
    
    if active_only:
        filtered_alerts = [a for a in filtered_alerts if a.is_active]
    
    return sorted(filtered_alerts, key=lambda x: x.created_at, reverse=True)

@app.get("/api/stats")
async def get_trading_stats():
    """Get trading platform statistics"""
    total_cryptocurrencies = len(cryptocurrencies)
    total_trading_pairs = len(trading_pairs)
    total_orders = len(orders)
    total_trades = len(trades)
    total_wallets = len(wallets)
    total_bots = len(trading_bots)
    total_alerts = len(price_alerts)
    
    # Order status distribution
    status_distribution = {}
    for order in orders.values():
        status = order.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # 24h trading volume
    total_volume_24h = sum(pair.volume_24h for pair in trading_pairs.values())
    
    # Market cap
    total_market_cap = sum(crypto.market_cap for crypto in cryptocurrencies.values())
    
    return {
        "total_cryptocurrencies": total_cryptocurrencies,
        "total_trading_pairs": total_trading_pairs,
        "total_orders": total_orders,
        "total_trades": total_trades,
        "total_wallets": total_wallets,
        "total_bots": total_bots,
        "total_alerts": total_alerts,
        "status_distribution": status_distribution,
        "total_volume_24h": total_volume_24h,
        "total_market_cap": total_market_cap,
        "supported_order_types": [t.value for t in OrderType],
        "supported_time_in_force": [t.value for t in TimeInForce]
    }

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages
            if message.get("type") == "subscribe":
                subscription_type = message.get("subscription_type")
                if subscription_type == "orderbook":
                    pair_symbol = message.get("pair_symbol")
                    # Send current order book
                    if pair_symbol in order_books:
                        order_book = order_books[pair_symbol]
                        await manager.send_to_client(client_id, {
                            "type": "orderbook_update",
                            "pair_symbol": pair_symbol,
                            "bids": order_book["bids"],
                            "asks": order_book["asks"],
                            "timestamp": datetime.now().isoformat()
                        })
            
            elif message.get("type") == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.get("/")
async def root():
    return {"message": "Cryptocurrency Trading API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
