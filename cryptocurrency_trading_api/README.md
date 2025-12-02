# Cryptocurrency Trading API

A comprehensive cryptocurrency trading platform with real-time order book, trading engine, portfolio management, and automated trading bots.

## Features

- **Real-time Trading**: Live order book matching and trade execution
- **Multiple Order Types**: Market, limit, stop-loss, take-profit, and stop-limit orders
- **Portfolio Management**: Multi-currency wallet and portfolio tracking
- **Trading Bots**: Automated trading strategies and performance tracking
- **Price Alerts**: Custom price notifications and alerts
- **WebSocket Support**: Real-time market data and order updates
- **Market Data**: Cryptocurrency prices, trading pairs, and market statistics
- **Order Management**: Advanced order management with time-in-force options

## API Endpoints

### Market Data

#### Get Cryptocurrencies
```http
GET /api/cryptocurrencies?limit=50&sort_by=market_cap
```

#### Get Specific Cryptocurrency
```http
GET /api/cryptocurrencies/{crypto_id}
```

#### Get Trading Pairs
```http
GET /api/trading-pairs?limit=50
```

#### Get Order Book
```http
GET /api/trading-pairs/{pair_symbol}/orderbook?limit=20
```

### Order Management

#### Create Order
```http
POST /api/orders
Content-Type: application/json

{
  "user_id": "user_123",
  "pair_symbol": "BTC/USD",
  "order_type": "limit",
  "order_side": "buy",
  "quantity": 0.5,
  "price": 45000,
  "time_in_force": "good_til_canceled",
  "expires_hours": 24
}
```

#### Get Orders
```http
GET /api/orders?user_id=user_123&pair_symbol=BTC/USD&status=open&limit=50
```

#### Get Specific Order
```http
GET /api/orders/{order_id}
```

#### Cancel Order
```http
DELETE /api/orders/{order_id}?user_id=user_123
```

### Trading History

#### Get Trades
```http
GET /api/trades?user_id=user_123&pair_symbol=BTC/USD&limit=50&hours=24
```

### Portfolio Management

#### Get Wallets
```http
GET /api/wallets?user_id=user_123
```

#### Get Specific Wallet
```http
GET /api/wallets/{wallet_id}
```

#### Get Portfolio
```http
GET /api/portfolio?user_id=user_123
```

### Trading Bots

#### Create Trading Bot
```http
POST /api/trading-bots
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Bitcoin Scalper",
  "strategy": "scalping",
  "pair_symbol": "BTC/USD",
  "parameters": {
    "profit_target": 0.5,
    "stop_loss": 0.2,
    "max_position_size": 0.1
  }
}
```

#### Get Trading Bots
```http
GET /api/trading-bots?user_id=user_123
```

### Price Alerts

#### Create Price Alert
```http
POST /api/price-alerts
Content-Type: application/json

{
  "user_id": "user_123",
  "cryptocurrency_id": "crypto_btc",
  "alert_type": "price_above",
  "target_price": 50000
}
```

#### Get Price Alerts
```http
GET /api/price-alerts?user_id=user_123&active_only=true
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Cryptocurrency
```json
{
  "id": "crypto_btc",
  "symbol": "BTC",
  "name": "Bitcoin",
  "current_price": 45000.0,
  "market_cap": 850000000000,
  "volume_24h": 25000000000,
  "change_24h": 2.5,
  "change_7d": 5.2,
  "circulating_supply": 19000000,
  "max_supply": 21000000,
  "last_updated": "2024-01-01T12:00:00"
}
```

### Trading Pair
```json
{
  "id": "pair_btc_usd",
  "base_symbol": "BTC",
  "quote_symbol": "USD",
  "symbol": "BTC/USD",
  "current_price": 45000.0,
  "bid_price": 44990.0,
  "ask_price": 45010.0,
  "volume_24h": 25000000000,
  "high_24h": 46000.0,
  "low_24h": 44000.0,
  "change_24h": 2.5,
  "last_updated": "2024-01-01T12:00:00"
}
```

### Order
```json
{
  "id": "order_123",
  "user_id": "user_123",
  "pair_symbol": "BTC/USD",
  "order_type": "limit",
  "order_side": "buy",
  "quantity": 0.5,
  "price": 45000,
  "stop_price": null,
  "time_in_force": "good_til_canceled",
  "status": "open",
  "filled_quantity": 0.0,
  "remaining_quantity": 0.5,
  "average_fill_price": 0.0,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "expires_at": "2024-01-02T12:00:00"
}
```

### Trade
```json
{
  "id": "trade_123",
  "order_id": "order_123",
  "user_id": "user_123",
  "pair_symbol": "BTC/USD",
  "side": "buy",
  "quantity": 0.5,
  "price": 45000,
  "fee": 22.5,
  "fee_currency": "USD",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Wallet
```json
{
  "id": "user_123_BTC",
  "user_id": "user_123",
  "currency": "BTC",
  "balance": 1.5,
  "available_balance": 1.0,
  "locked_balance": 0.5,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### Portfolio
```json
{
  "id": "portfolio_user_123",
  "user_id": "user_123",
  "total_value_usd": 67500.0,
  "total_value_change_24h": 1250.0,
  "total_value_change_7d": 3500.0,
  "allocations": {
    "BTC": 66.7,
    "ETH": 23.7,
    "USD": 9.6
  },
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

## Order Types

### 1. Market Orders
- **Description**: Execute immediately at current market price
- **Use Cases**: Quick entry/exit, urgent trades
- **Execution**: Filled against available orders in order book

### 2. Limit Orders
- **Description**: Execute only at specified price or better
- **Use Cases**: Price control, range trading
- **Execution**: Placed in order book until matched

### 3. Stop-Loss Orders
- **Description**: Market order triggered when price reaches stop price
- **Use Cases**: Risk management, loss limiting
- **Execution**: Converts to market order at stop price

### 4. Take-Profit Orders
- **Description**: Market order triggered when profit target reached
- **Use Cases**: Profit taking, target achievement
- **Execution**: Converts to market order at target price

### 5. Stop-Limit Orders
- **Description**: Limit order triggered when price reaches stop price
- **Use Cases**: Precise entry/exit points
- **Execution**: Converts to limit order at stop price

## Time in Force Options

### GTC (Good 'til Canceled)
- **Description**: Order remains active until cancelled
- **Use Cases**: Long-term strategies, patient trading

### IOC (Immediate or Cancel)
- **Description**: Fill as much as possible immediately, cancel remainder
- **Use Cases**: Large orders requiring immediate execution

### FOK (Fill or Kill)
- **Description**: Must fill entire order immediately or cancel
- **Use Cases**: Precise position sizing requirements

### DAY (Day Order)
- **Description**: Order expires at end of trading day
- **Use Cases**: Intraday trading strategies

## Trading Bot Strategies

### 1. Scalping
- **Description**: Small, frequent profits from price fluctuations
- **Parameters**: profit_target, stop_loss, max_position_size
- **Risk**: High frequency, low individual risk

### 2. Grid Trading
- **Description**: Place buy/sell orders at regular intervals
- **Parameters**: grid_size, grid_levels, investment_amount
- **Risk**: Range-bound markets, accumulation

### 3. Mean Reversion
- **Description**: Trade based on price returning to mean
- **Parameters**: lookback_period, deviation_threshold, position_size
- **Risk**: Statistical arbitrage, contrarian trading

### 4. Momentum Trading
- **Description**: Follow price trends and momentum
- **Parameters**: trend_period, momentum_threshold, stop_loss
- **Risk**: Trend following, breakout trading

### 5. Arbitrage
- **Description**: Exploit price differences across markets
- **Parameters**: price_threshold, min_profit, execution_speed
- **Risk**: Market making, cross-exchange trading

## Price Alert Types

### 1. Price Above
- **Trigger**: When price rises above target price
- **Use Cases**: Profit taking, breakout alerts

### 2. Price Below
- **Trigger**: When price falls below target price
- **Use Cases**: Buy opportunities, stop-loss alerts

### 3. Percentage Change
- **Trigger**: When price changes by target percentage
- **Use Cases**: Volatility alerts, significant moves

## WebSocket Events

### Order Book Updates
```javascript
{
  "type": "orderbook_update",
  "pair_symbol": "BTC/USD",
  "bids": [
    {"order_id": "order_123", "price": 44990, "quantity": 0.5, "timestamp": "2024-01-01T12:00:00"}
  ],
  "asks": [
    {"order_id": "order_456", "price": 45010, "quantity": 0.3, "timestamp": "2024-01-01T12:00:00"}
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

### Trade Executions
```javascript
{
  "type": "trade",
  "pair_symbol": "BTC/USD",
  "price": 45000,
  "quantity": 0.5,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Price Alerts
```javascript
{
  "type": "price_alert_triggered",
  "alert": {
    "id": "alert_123",
    "cryptocurrency_id": "crypto_btc",
    "alert_type": "price_above",
    "target_price": 50000
  },
  "current_price": 50100,
  "timestamp": "2024-01-01T12:00:00"
}
```

## Installation

```bash
pip install fastapi uvicorn websockets
```

## Usage

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Example Usage

### Python Client
```python
import requests
import asyncio
import websockets
import json

# Get market data
response = requests.get("http://localhost:8000/api/cryptocurrencies")
cryptocurrencies = response.json()

print("Available cryptocurrencies:")
for crypto in cryptocurrencies[:5]:
    print(f"  {crypto['symbol']}: ${crypto['current_price']:,.2f} ({crypto['change_24h']:+.1f}%)")

# Get trading pairs
response = requests.get("http://localhost:8000/api/trading-pairs")
pairs = response.json()

print("\nTrading pairs:")
for pair in pairs[:3]:
    print(f"  {pair['symbol']}: ${pair['current_price']:,.2f} Volume: ${pair['volume_24h']:,.0f}")

# Create limit order
order_data = {
    "user_id": "user_123",
    "pair_symbol": "BTC/USD",
    "order_type": "limit",
    "order_side": "buy",
    "quantity": 0.01,
    "price": 44000,
    "time_in_force": "good_til_canceled"
}

response = requests.post("http://localhost:8000/api/orders", json=order_data)
order = response.json()
print(f"\nCreated order: {order['id']} - {order['status']}")

# Get order book
response = requests.get("http://localhost:8000/api/trading-pairs/BTC/USD/orderbook")
order_book = response.json()

print(f"\nOrder Book for BTC/USD:")
print(f"  Best Bid: ${order_book['bids'][0]['price']:,.2f}")
print(f"  Best Ask: ${order_book['asks'][0]['price']:,.2f}")

# Create trading bot
bot_data = {
    "user_id": "user_123",
    "name": "Bitcoin Scalper",
    "strategy": "scalping",
    "pair_symbol": "BTC/USD",
    "parameters": {
        "profit_target": 0.5,
        "stop_loss": 0.2,
        "max_position_size": 0.01
    }
}

response = requests.post("http://localhost:8000/api/trading-bots", json=bot_data)
bot = response.json()
print(f"\nCreated trading bot: {bot['id']} - {bot['strategy']}")

# Create price alert
alert_data = {
    "user_id": "user_123",
    "cryptocurrency_id": "crypto_btc",
    "alert_type": "price_above",
    "target_price": 50000
}

response = requests.post("http://localhost:8000/api/price-alerts", json=alert_data)
alert = response.json()
print(f"\nCreated price alert: {alert['id']} - {alert['alert_type']} at ${alert['target_price']}")

# Get portfolio
response = requests.get("http://localhost:8000/api/portfolio?user_id=user_123")
portfolio = response.json()

print(f"\nPortfolio Value: ${portfolio['total_value_usd']:,.2f}")
print("Allocations:")
for currency, percentage in portfolio['allocations'].items():
    print(f"  {currency}: {percentage:.1f}%")

# WebSocket client for real-time updates
async def websocket_client():
    uri = "ws://localhost:8000/ws/python_client"
    async with websockets.connect(uri) as websocket:
        # Subscribe to order book updates
        await websocket.send(json.dumps({
            "type": "subscribe",
            "subscription_type": "orderbook",
            "pair_symbol": "BTC/USD"
        }))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            if data['type'] == 'orderbook_update':
                print(f"Order book updated for {data['pair_symbol']}")
                print(f"  Bids: {len(data['bids'])}, Asks: {len(data['asks'])}")
            elif data['type'] == 'trade':
                print(f"Trade executed: {data['quantity']} {data['pair_symbol']} at ${data['price']}")
            elif data['type'] == 'price_alert_triggered':
                print(f"Price alert: {data['alert']['alert_type']} - Current: ${data['current_price']}")

# Run WebSocket client
asyncio.run(websocket_client())
```

### JavaScript Client
```javascript
// WebSocket client for real-time trading
class TradingClient {
  constructor() {
    this.ws = new WebSocket('ws://localhost:8000/ws/javascript_client');
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }
  
  handleMessage(message) {
    switch (message.type) {
      case 'orderbook_update':
        this.updateOrderBook(message);
        break;
      case 'trade':
        this.updateRecentTrades(message);
        break;
      case 'price_alert_triggered':
        this.showAlert(message);
        break;
    }
  }
  
  async createOrder(orderData) {
    const response = await fetch('http://localhost:8000/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    });
    
    return response.json();
  }
  
  async cancelOrder(orderId, userId) {
    const response = await fetch(`http://localhost:8000/api/orders/${orderId}?user_id=${userId}`, {
      method: 'DELETE'
    });
    
    return response.json();
  }
  
  async getPortfolio(userId) {
    const response = await fetch(`http://localhost:8000/api/portfolio?user_id=${userId}`);
    return response.json();
  }
  
  async createTradingBot(botData) {
    const response = await fetch('http://localhost:8000/api/trading-bots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(botData)
    });
    
    return response.json();
  }
  
  updateOrderBook(data) {
    // Update order book UI
    const orderBookElement = document.getElementById('orderbook');
    if (orderBookElement) {
      const bidsHtml = data.bids.slice(0, 5).map(bid => 
        `<tr><td>${bid.price}</td><td>${bid.quantity}</td></tr>`
      ).join('');
      
      const asksHtml = data.asks.slice(0, 5).map(ask => 
        `<tr><td>${ask.price}</td><td>${ask.quantity}</td></tr>`
      ).join('');
      
      orderBookElement.innerHTML = `
        <h3>Bids</h3><table>${bidsHtml}</table>
        <h3>Asks</h3><table>${asksHtml}</table>
      `;
    }
  }
  
  updateRecentTrades(data) {
    // Update recent trades UI
    const tradesElement = document.getElementById('recent-trades');
    if (tradesElement) {
      const tradeRow = document.createElement('tr');
      tradeRow.innerHTML = `
        <td>${data.timestamp}</td>
        <td>${data.pair_symbol}</td>
        <td>${data.price}</td>
        <td>${data.quantity}</td>
      `;
      tradesElement.insertBefore(tradeRow, tradesElement.firstChild);
      
      // Keep only last 10 trades
      while (tradesElement.children.length > 10) {
        tradesElement.removeChild(tradesElement.lastChild);
      }
    }
  }
  
  showAlert(data) {
    // Show price alert notification
    const alertElement = document.createElement('div');
    alertElement.className = 'alert alert-info';
    alertElement.innerHTML = `
      <h4>Price Alert Triggered!</h4>
      <p>${data.alert.alert_type}: ${data.current_price}</p>
    `;
    
    document.getElementById('alerts').appendChild(alertElement);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      alertElement.remove();
    }, 10000);
  }
}

// Usage
const client = new TradingClient();

// Create order form
document.getElementById('order-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const orderData = {
    user_id: document.getElementById('user-id').value,
    pair_symbol: document.getElementById('pair-symbol').value,
    order_type: document.getElementById('order-type').value,
    order_side: document.getElementById('order-side').value,
    quantity: parseFloat(document.getElementById('quantity').value),
    price: parseFloat(document.getElementById('price').value),
    time_in_force: document.getElementById('time-in-force').value
  };
  
  try {
    const order = await client.createOrder(orderData);
    console.log('Order created:', order);
    
    // Subscribe to order book updates
    client.ws.send(JSON.stringify({
      type: 'subscribe',
      subscription_type: 'orderbook',
      pair_symbol: orderData.pair_symbol
    }));
    
  } catch (error) {
    console.error('Error creating order:', error);
  }
});

// Load portfolio
client.getPortfolio('user_123').then(portfolio => {
  console.log('Portfolio:', portfolio);
  
  // Update portfolio UI
  document.getElementById('portfolio-value').textContent = `$${portfolio.total_value_usd.toLocaleString()}`;
  
  const allocationsHtml = Object.entries(portfolio.allocations)
    .map(([currency, percentage]) => 
      `<div>${currency}: ${percentage.toFixed(1)}%</div>`
    ).join('');
  
  document.getElementById('portfolio-allocations').innerHTML = allocationsHtml;
});
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Environment
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=*

# Trading Engine
ORDER_BOOK_DEPTH=1000
ORDER_MATCHING_INTERVAL=1
MAX_ORDER_SIZE=1000000
MIN_ORDER_SIZE=0.0001

# Fee Structure
MAKER_FEE_RATE=0.001
TAKER_FEE_RATE=0.002
MIN_FEE=0.0001

# Market Data
PRICE_UPDATE_INTERVAL=5
MARKET_DATA_RETENTION_HOURS=24
EXTERNAL_DATA_PROVIDERS=coinbase,binance,kraken

# Risk Management
MAX_POSITION_SIZE=100000
MAX_DAILY_TRADES=1000
MAX_LEVERAGE=10
LIQUIDATION_THRESHOLD=0.8

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=10000

# Database (for persistence)
DATABASE_URL=sqlite:///./crypto_trading.db
ENABLE_TRADE_HISTORY=true
ORDER_HISTORY_RETENTION_DAYS=365

# Security
API_KEY_REQUIRED=false
RATE_LIMIT_PER_MINUTE=100
ENABLE_ORDER_SIGNATURE_VALIDATION=false

# Logging
LOG_LEVEL=info
ENABLE_TRADE_LOGGING=true
ORDER_LOG_RETENTION_DAYS=30
SECURITY_LOG_RETENTION_DAYS=90
```

## Use Cases

- **Cryptocurrency Exchange**: Full-featured trading platform for digital assets
- **Algorithmic Trading**: Automated trading strategies and backtesting
- **Portfolio Management**: Multi-currency portfolio tracking and rebalancing
- **Market Making**: Provide liquidity and capture spreads
- **Arbitrage Trading**: Exploit price differences across exchanges
- **Risk Management**: Automated stop-loss and position sizing
- **Market Analysis**: Real-time market data and analytics

## Advanced Features

### Advanced Order Types
```python
# Iceberg orders (hidden large orders)
class IcebergOrder(Order):
    def __init__(self, total_quantity, visible_quantity, **kwargs):
        self.total_quantity = total_quantity
        self.visible_quantity = visible_quantity
        self.remaining_quantity = total_quantity
        super().__init__(**kwargs)

# Trailing stop orders
class TrailingStopOrder(Order):
    def __init__(self, trail_percentage, **kwargs):
        self.trail_percentage = trail_percentage
        self.highest_price = 0
        super().__init__(**kwargs)
```

### Market Making Strategy
```python
async def market_making_strategy(pair_symbol, spread_percentage, order_size):
    """Implement market making strategy"""
    current_price = get_current_price(pair_symbol)
    spread = current_price * (spread_percentage / 100)
    
    # Place buy order below current price
    buy_price = current_price - spread / 2
    await create_limit_order(pair_symbol, "buy", order_size, buy_price)
    
    # Place sell order above current price
    sell_price = current_price + spread / 2
    await create_limit_order(pair_symbol, "sell", order_size, sell_price)
```

### Risk Management Engine
```python
def calculate_position_size(user_id, pair_symbol, risk_percentage):
    """Calculate position size based on risk management rules"""
    portfolio = get_portfolio(user_id)
    max_risk = portfolio.total_value_usd * (risk_percentage / 100)
    
    current_price = get_current_price(pair_symbol)
    max_shares = max_risk / current_price
    
    return min(max_shares, MAX_POSITION_SIZE / current_price)

def check_margin_requirements(user_id, new_order):
    """Check if user meets margin requirements"""
    portfolio = get_portfolio(user_id)
    total_position_value = calculate_total_position_value(user_id)
    
    margin_ratio = total_position_value / portfolio.total_value_usd
    
    if margin_ratio > MAX_LEVERAGE:
        raise HTTPException(status_code=400, detail="Insufficient margin")
```

## Production Considerations

- **High Availability**: Redundant systems and failover mechanisms
- **Low Latency**: Optimized order matching and data processing
- **Security**: Multi-signature wallets, cold storage, encryption
- **Compliance**: KYC/AML procedures, regulatory reporting
- **Scalability**: Horizontal scaling for high-volume trading
- **Monitoring**: Real-time system health and performance metrics
- **Backup**: Regular backups of trading data and configurations
- **Audit Trails**: Complete audit logs for all trading activities
