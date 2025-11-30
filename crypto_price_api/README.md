# Real-Time Crypto Price API

A comprehensive real-time cryptocurrency price tracking API with portfolio management, WebSocket streams, and price alerts. Built with FastAPI and WebSockets for maximum performance and real-time updates.

## 🚀 Features

- **Live Crypto Prices**: Real-time price updates from CoinGecko API
- **Portfolio Tracking**: Create and manage multiple portfolios with detailed analytics
- **WebSocket Streams**: Real-time price updates via WebSocket connections
- **Price Alerts**: Set custom price alerts with instant notifications
- **Transaction History**: Track buy/sell transactions with detailed records
- **Market Overview**: Market statistics and top cryptocurrency data
- **Search Functionality**: Search for cryptocurrencies by name or symbol
- **Price History**: Historical price data and charts
- **User Management**: Secure API key authentication

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy with SQLite
- **Real-time**: WebSockets for live updates
- **External API**: CoinGecko for price data
- **Data Validation**: Pydantic models
- **Async Processing**: aiohttp for HTTP requests

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for CoinGecko API)

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8019`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8019/docs`
- ReDoc: `http://localhost:8019/redoc`

## 📝 API Endpoints

### User Management

#### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Response Example**:
```json
{
  "id": "user_123",
  "username": "john_doe",
  "email": "john@example.com",
  "api_key": "ck_abc123def456...",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Get Current User
```http
GET /users/me?api_key=your_api_key
```

### Cryptocurrency Prices

#### Get All Crypto Prices
```http
GET /crypto/prices?limit=100&vs_currency=usd&order=market_cap_desc
```

**Response Example**:
```json
[
  {
    "id": "bitcoin",
    "symbol": "BTC",
    "name": "Bitcoin",
    "current_price": 43250.50,
    "market_cap": 845000000000,
    "volume_24h": 25000000000,
    "price_change_24h": 1250.75,
    "price_change_percentage_24h": 2.98,
    "last_updated": "2024-01-15T12:00:00"
  }
]
```

#### Get Specific Crypto Price
```http
GET /crypto/bitcoin
```

#### Get Crypto Price History
```http
GET /crypto/bitcoin/history?days=7
```

**Response Example**:
```json
[
  {
    "crypto_id": "bitcoin",
    "price": 43250.50,
    "market_cap": 845000000000,
    "volume_24h": 25000000000,
    "timestamp": "2024-01-15T12:00:00"
  }
]
```

#### Search Cryptocurrencies
```http
GET /search/crypto?query=bitcoin&limit=10
```

### Portfolio Management

#### Create Portfolio
```http
POST /portfolios?api_key=your_api_key
Content-Type: application/json

{
  "name": "My Crypto Portfolio",
  "description": "Long-term investment portfolio"
}
```

#### Get User Portfolios
```http
GET /portfolios?api_key=your_api_key
```

#### Get Portfolio Summary
```http
GET /portfolios/{portfolio_id}/summary?api_key=your_api_key
```

**Response Example**:
```json
{
  "portfolio_id": "portfolio_123",
  "portfolio_name": "My Crypto Portfolio",
  "total_value": 50000.00,
  "total_cost": 45000.00,
  "total_profit_loss": 5000.00,
  "total_profit_loss_percentage": 11.11,
  "holdings_count": 5,
  "holdings": [
    {
      "crypto_id": "bitcoin",
      "crypto_name": "Bitcoin",
      "crypto_symbol": "BTC",
      "quantity": 0.5,
      "average_buy_price": 40000.00,
      "current_price": 43250.50,
      "current_value": 21625.25,
      "cost_basis": 20000.00,
      "profit_loss": 1625.25,
      "profit_loss_percentage": 8.13,
      "price_change_24h": 1250.75,
      "price_change_percentage_24h": 2.98
    }
  ],
  "last_updated": "2024-01-15T12:00:00"
}
```

#### Add Holding to Portfolio
```http
POST /portfolios/{portfolio_id}/holdings?api_key=your_api_key
Content-Type: application/json

{
  "crypto_id": "bitcoin",
  "quantity": 0.5,
  "price_per_unit": 40000.00
}
```

#### Get Portfolio Holdings
```http
GET /portfolios/{portfolio_id}/holdings?api_key=your_api_key
```

#### Get Portfolio Transactions
```http
GET /portfolios/{portfolio_id}/transactions?api_key=your_api_key&limit=50
```

### Price Alerts

#### Create Alert
```http
POST /alerts?api_key=your_api_key
Content-Type: application/json

{
  "crypto_id": "bitcoin",
  "alert_type": "price_above",
  "target_price": 50000.00
}
```

**Response Example**:
```json
{
  "id": "alert_123",
  "user_id": "user_123",
  "crypto_id": "bitcoin",
  "alert_type": "price_above",
  "target_price": 50000.00,
  "percentage_change": null,
  "status": "active",
  "notification_sent": false,
  "created_at": "2024-01-15T12:00:00",
  "triggered_at": null
}
```

#### Get User Alerts
```http
GET /alerts?api_key=your_api_key&status=active
```

#### Delete Alert
```http
DELETE /alerts/{alert_id}?api_key=your_api_key
```

### Market Data

#### Get Market Overview
```http
GET /market/overview
```

**Response Example**:
```json
{
  "total_market_cap": 2500000000000,
  "total_volume_24h": 125000000000,
  "top_cryptos": [
    {
      "id": "bitcoin",
      "name": "Bitcoin",
      "symbol": "BTC",
      "current_price": 43250.50,
      "market_cap": 845000000000,
      "price_change_percentage_24h": 2.98
    }
  ],
  "market_stats": {
    "gainers_count": 75,
    "losers_count": 25,
    "top_gainer": {
      "id": "ethereum",
      "name": "Ethereum",
      "symbol": "ETH",
      "price_change_percentage_24h": 5.67
    },
    "top_loser": {
      "id": "ripple",
      "name": "Ripple",
      "symbol": "XRP",
      "price_change_percentage_24h": -2.34
    }
  },
  "last_updated": "2024-01-15T12:00:00"
}
```

### WebSocket Connection

#### Connect to Real-time Stream
```javascript
const ws = new WebSocket('ws://localhost:8019/ws?api_key=your_api_key');

ws.onopen = function(event) {
    console.log('Connected to crypto price stream');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'price_update') {
        console.log('Price update:', data.data);
    } else if (data.type === 'alert_triggered') {
        console.log('Alert triggered:', data);
    }
};

// Send ping to keep connection alive
setInterval(() => {
    ws.send(JSON.stringify({type: 'ping'}));
}, 30000);
```

**WebSocket Message Types**:

1. **Connection Message**:
```json
{
  "type": "connected",
  "user_id": "user_123",
  "message": "Connected to real-time price stream",
  "timestamp": "2024-01-15T12:00:00"
}
```

2. **Price Update**:
```json
{
  "type": "price_update",
  "data": {
    "id": "bitcoin",
    "symbol": "BTC",
    "name": "Bitcoin",
    "current_price": 43250.50,
    "price_change_24h": 1250.75,
    "price_change_percentage_24h": 2.98,
    "market_cap": 845000000000,
    "volume_24h": 25000000000
  },
  "timestamp": "2024-01-15T12:00:00"
}
```

3. **Alert Triggered**:
```json
{
  "type": "alert_triggered",
  "alert_id": "alert_123",
  "crypto_id": "bitcoin",
  "crypto_name": "Bitcoin",
  "current_price": 50000.00,
  "alert_type": "price_above",
  "target_price": 50000.00,
  "percentage_change": null,
  "timestamp": "2024-01-15T12:00:00"
}
```

## 🧪 Testing Examples

### User Management
```bash
# Create user
curl -X POST "http://localhost:8019/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'

# Get user info
curl -X GET "http://localhost:8019/users/me?api_key=ck_abc123def456"
```

### Crypto Prices
```bash
# Get all prices
curl -X GET "http://localhost:8019/crypto/prices?limit=10"

# Get Bitcoin price
curl -X GET "http://localhost:8019/crypto/bitcoin"

# Get Bitcoin history
curl -X GET "http://localhost:8019/crypto/bitcoin/history?days=7"

# Search crypto
curl -X GET "http://localhost:8019/search/crypto?query=ethereum"
```

### Portfolio Management
```bash
# Create portfolio
curl -X POST "http://localhost:8019/portfolios?api_key=ck_abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Portfolio",
    "description": "Test portfolio"
  }'

# Add holding
curl -X POST "http://localhost:8019/portfolios/portfolio_123/holdings?api_key=ck_abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "crypto_id": "bitcoin",
    "quantity": 0.5,
    "price_per_unit": 40000
  }'

# Get portfolio summary
curl -X GET "http://localhost:8019/portfolios/portfolio_123/summary?api_key=ck_abc123def456"
```

### Price Alerts
```bash
# Create price alert
curl -X POST "http://localhost:8019/alerts?api_key=ck_abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "crypto_id": "bitcoin",
    "alert_type": "price_above",
    "target_price": 50000
  }'

# Get alerts
curl -X GET "http://localhost:8019/alerts?api_key=ck_abc123def456"
```

### WebSocket Testing
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8019/ws?api_key=ck_abc123def456');

ws.onmessage = function(event) {
    console.log('Received:', JSON.parse(event.data));
};
```

## 📊 Database Schema

### Users Table
- **id**: Primary key (UUID)
- **username**: Unique username
- **email**: Unique email address
- **api_key**: Secure API key for authentication
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp

### Cryptocurrencies Table
- **id**: CoinGecko cryptocurrency ID
- **symbol**: Cryptocurrency symbol (e.g., BTC)
- **name**: Full cryptocurrency name
- **current_price**: Current USD price
- **market_cap**: Market capitalization
- **volume_24h**: 24-hour trading volume
- **price_change_24h**: 24-hour price change
- **price_change_percentage_24h**: 24-hour percentage change
- **last_updated**: Last price update timestamp

### Portfolios Table
- **id**: Primary key (UUID)
- **user_id**: Foreign key to Users table
- **name**: Portfolio name
- **description**: Portfolio description
- **total_value**: Total portfolio value
- **created_at**: Portfolio creation timestamp
- **updated_at**: Last update timestamp

### Portfolio Holdings Table
- **id**: Primary key (UUID)
- **portfolio_id**: Foreign key to Portfolios table
- **crypto_id**: Foreign key to Cryptocurrencies table
- **quantity**: Amount of cryptocurrency held
- **average_buy_price**: Average purchase price
- **current_value**: Current value of holding
- **created_at**: Holding creation timestamp
- **updated_at**: Last update timestamp

### Transactions Table
- **id**: Primary key (UUID)
- **portfolio_id**: Foreign key to Portfolios table
- **crypto_id**: Foreign key to Cryptocurrencies table
- **transaction_type**: Buy/Sell transaction type
- **quantity**: Amount transacted
- **price_per_unit**: Price per unit at transaction time
- **total_amount**: Total transaction amount
- **fee**: Transaction fee
- **notes**: Transaction notes
- **created_at**: Transaction timestamp

### Alerts Table
- **id**: Primary key (UUID)
- **user_id**: Foreign key to Users table
- **crypto_id**: Foreign key to Cryptocurrencies table
- **alert_type**: Type of alert (price_above, price_below, percentage_change)
- **target_price**: Target price for price alerts
- **percentage_change**: Percentage change threshold
- **status**: Alert status (active, triggered, disabled)
- **notification_sent**: Whether notification was sent
- **created_at**: Alert creation timestamp
- **triggered_at**: Alert trigger timestamp

### Price History Table
- **id**: Primary key (UUID)
- **crypto_id**: Foreign key to Cryptocurrencies table
- **price**: Historical price
- **market_cap**: Historical market cap
- **volume_24h**: Historical 24h volume
- **timestamp**: Price timestamp

## 🔐 Alert Types

### Price Above Alert
Triggers when cryptocurrency price goes above target price.

```json
{
  "crypto_id": "bitcoin",
  "alert_type": "price_above",
  "target_price": 50000.00
}
```

### Price Below Alert
Triggers when cryptocurrency price goes below target price.

```json
{
  "crypto_id": "bitcoin",
  "alert_type": "price_below",
  "target_price": 40000.00
}
```

### Percentage Change Alert
Triggers when 24-hour price change exceeds threshold.

```json
{
  "crypto_id": "bitcoin",
  "alert_type": "percentage_change",
  "percentage_change": 5.0
}
```

## 📈 Real-time Features

### WebSocket Connection Management
- **Connection Pool**: Manages multiple WebSocket connections
- **User Authentication**: Validates API keys for WebSocket connections
- **Message Broadcasting**: Sends price updates to all connected users
- **Connection Health**: Monitors connection status and handles disconnects

### Price Update System
- **Background Task**: Runs every 30 seconds to fetch latest prices
- **Change Detection**: Only broadcasts significant price changes (>0.1%)
- **Portfolio Updates**: Automatically updates portfolio values
- **Alert Checking**: Checks and triggers price alerts
- **History Storage**: Stores price history for charts

### Alert Notification System
- **Real-time Triggers**: Instant alert notifications via WebSocket
- **Alert States**: Active, triggered, or disabled
- **Multiple Alert Types**: Price above, price below, percentage change
- **User-specific**: Only sends alerts to relevant users

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8019
DEBUG=false
RELOAD=false

# Database Configuration
DATABASE_URL=sqlite:///crypto_price.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30
DATABASE_ECHO=false

# CoinGecko API
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
API_REQUEST_TIMEOUT=10
RATE_LIMIT_DELAY=1
MAX_RETRIES=3

# WebSocket Configuration
WEBSOCKET_PING_INTERVAL=30
WEBSOCKET_CONNECTION_TIMEOUT=60
MAX_WEBSOCKET_CONNECTIONS=1000
ENABLE_WEBSOCKET_COMPRESSION=true

# Price Update Configuration
PRICE_UPDATE_INTERVAL=30
PRICE_CHANGE_THRESHOLD=0.1
MAX_CRYPTOCURRENCIES=250
ENABLE_PRICE_HISTORY=true
HISTORY_RETENTION_DAYS=365

# Alert Configuration
ENABLE_ALERTS=true
ALERT_CHECK_INTERVAL=30
MAX_ALERTS_PER_USER=50
ALERT_NOTIFICATION_RETRIES=3

# Portfolio Configuration
MAX_PORTFOLIOS_PER_USER=10
MAX_HOLDINGS_PER_PORTFOLIO=50
ENABLE_PORTFOLIO_ANALYTICS=true
PORTFOLIO_VALUE_UPDATE_INTERVAL=30

# Security Configuration
SECRET_KEY=your-secret-key-here
API_KEY_LENGTH=32
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/crypto_price.log
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_PRICE_UPDATES=true
LOG_ALERTS=true
LOG_WEBSOCKET_EVENTS=true

# Performance Configuration
ENABLE_CACHING=true
CACHE_TTL=60
CACHE_STORAGE=memory
ENABLE_COMPRESSION=true
COMPRESSION_LEVEL=6
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_REQUESTS=10

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_PORT=8020
HEALTH_CHECK_INTERVAL=30
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USAGE_ANALYTICS=true

# CORS Configuration
ENABLE_CORS=true
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Development Configuration
TEST_MODE=false
ENABLE_PROFILING=false
DEBUG_RESPONSES=false
MOCK_COINGECKO_API=false
ENABLE_SWAGGER_UI=true
ENABLE_REDOC=true
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs data

# Set permissions
RUN chmod +x logs data

EXPOSE 8019

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8019"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  crypto-api:
    build: .
    ports:
      - "8019:8019"
    environment:
      - DATABASE_URL=sqlite:///data/crypto_price.db
      - LOG_LEVEL=INFO
      - SECRET_KEY=your-production-secret-key
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8019/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

volumes:
  data_data:
  logs_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crypto-price-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: crypto-price-api
  template:
    metadata:
      labels:
        app: crypto-price-api
    spec:
      containers:
      - name: api
        image: crypto-price-api:latest
        ports:
        - containerPort: 8019
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: crypto-secrets
              key: secret-key
        - name: DATABASE_URL
          value: sqlite:///data/crypto_price.db
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8019
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8019
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: crypto-price-service
spec:
  selector:
    app: crypto-price-api
  ports:
  - port: 8019
    targetPort: 8019
  type: LoadBalancer
```

## 📈 Advanced Features

### Portfolio Analytics
```python
# Portfolio performance metrics
def calculate_portfolio_performance(portfolio_id: str, db: Session):
    """Calculate detailed portfolio performance"""
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.portfolio_id == portfolio_id
    ).all()
    
    total_value = 0.0
    total_cost = 0.0
    best_performer = None
    worst_performer = None
    
    for holding in holdings:
        crypto = db.query(Cryptocurrency).filter(
            Cryptocurrency.id == holding.crypto_id
        ).first()
        
        if crypto and crypto.current_price:
            current_value = holding.quantity * crypto.current_price
            cost = holding.quantity * holding.average_buy_price
            profit_loss = current_value - cost
            profit_loss_percentage = (profit_loss / cost * 100) if cost > 0 else 0
            
            total_value += current_value
            total_cost += cost
            
            # Track best/worst performers
            if best_performer is None or profit_loss_percentage > best_performer['profit_loss_percentage']:
                best_performer = {
                    'crypto_name': crypto.name,
                    'profit_loss_percentage': profit_loss_percentage
                }
            
            if worst_performer is None or profit_loss_percentage < worst_performer['profit_loss_percentage']:
                worst_performer = {
                    'crypto_name': crypto.name,
                    'profit_loss_percentage': profit_loss_percentage
                }
    
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_profit_loss': total_value - total_cost,
        'total_profit_loss_percentage': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
        'best_performer': best_performer,
        'worst_performer': worst_performer
    }
```

### Advanced Alert System
```python
# Custom alert conditions
async def check_custom_alerts(db: Session):
    """Check custom alert conditions"""
    alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.ACTIVE,
        Alert.notification_sent == False
    ).all()
    
    for alert in alerts:
        crypto = db.query(Cryptocurrency).filter(
            Cryptocurrency.id == alert.crypto_id
        ).first()
        
        if not crypto:
            continue
        
        # Volume spike detection
        if alert.alert_type == AlertType.VOLUME_ALERT:
            avg_volume = calculate_average_volume(alert.crypto_id, db)
            if crypto.volume_24h and avg_volume:
                volume_increase = (crypto.volume_24h - avg_volume) / avg_volume * 100
                if volume_increase >= alert.percentage_change:
                    await trigger_alert(alert, crypto, f"Volume increased by {volume_increase:.2f}%")
        
        # Price momentum detection
        elif alert.alert_type == "price_momentum":
            momentum = calculate_price_momentum(alert.crypto_id, db)
            if abs(momentum) >= alert.percentage_change:
                direction = "up" if momentum > 0 else "down"
                await trigger_alert(alert, crypto, f"Price momentum {direction} {abs(momentum):.2f}%")
```

### Market Sentiment Analysis
```python
# Basic sentiment analysis from price movements
def calculate_market_sentiment(db: Session):
    """Calculate overall market sentiment"""
    top_cryptos = db.query(Cryptocurrency).order_by(
        Cryptocurrency.market_cap.desc().nullslast()
    ).limit(50).all()
    
    positive_count = 0
    negative_count = 0
    total_change = 0
    
    for crypto in top_cryptos:
        if crypto.price_change_percentage_24h:
            if crypto.price_change_percentage_24h > 0:
                positive_count += 1
            else:
                negative_count += 1
            total_change += crypto.price_change_percentage_24h
    
    total_count = positive_count + negative_count
    if total_count == 0:
        return "neutral"
    
    positive_ratio = positive_count / total_count
    avg_change = total_change / total_count
    
    if positive_ratio > 0.7 and avg_change > 2:
        return "bullish"
    elif positive_ratio < 0.3 and avg_change < -2:
        return "bearish"
    else:
        return "neutral"
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
price_updates = Counter('price_updates_total', 'Total price updates')
websocket_connections = Gauge('websocket_connections_current', 'Current WebSocket connections')
portfolio_value_updates = Counter('portfolio_value_updates_total', 'Total portfolio value updates')
alerts_triggered = Counter('alerts_triggered_total', 'Total alerts triggered')
api_requests = Counter('api_requests_total', 'Total API requests', method='GET', endpoint='/crypto/prices')

# Response times
price_update_duration = Histogram('price_update_duration_seconds', 'Price update duration')
websocket_message_duration = Histogram('websocket_message_duration_seconds', 'WebSocket message duration')
```

### Usage Analytics
```python
@app.get("/analytics/usage")
async def get_usage_analytics(api_key: str = Query(...), db: Session = Depends(get_db)):
    """Get API usage analytics"""
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Get user statistics
    portfolio_count = db.query(Portfolio).filter(Portfolio.user_id == user.id).count()
    holding_count = db.query(PortfolioHolding).join(Portfolio).filter(
        Portfolio.user_id == user.id
    ).count()
    alert_count = db.query(Alert).filter(Alert.user_id == user.id).count()
    transaction_count = db.query(Transaction).join(Portfolio).filter(
        Portfolio.user_id == user.id
    ).count()
    
    return {
        "user_id": user.id,
        "portfolio_count": portfolio_count,
        "holding_count": holding_count,
        "alert_count": alert_count,
        "transaction_count": transaction_count,
        "total_portfolio_value": calculate_total_portfolio_value(user.id, db),
        "most_traded_crypto": get_most_traded_crypto(user.id, db),
        "best_performing_portfolio": get_best_performing_portfolio(user.id, db)
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Chart Data**: OHLCV data for candlestick charts
- **Social Sentiment**: Twitter sentiment analysis integration
- **News Integration**: Crypto news aggregation and sentiment analysis
- **Exchange Integration**: Direct exchange API integration for real trading
- **Mobile App**: React Native mobile application
- **Push Notifications**: Mobile push notifications for alerts
- **Advanced Analytics**: Portfolio correlation analysis, risk metrics
- **Social Features**: Portfolio sharing, leaderboards
- **Educational Content**: Crypto tutorials and market analysis

### Advanced Trading Features
- **Limit Orders**: Automated buy/sell orders
- **Stop Loss**: Automatic sell orders to limit losses
- **Dollar Cost Averaging**: Automated investment strategies
- **Rebalancing**: Automatic portfolio rebalancing
- **Tax Reporting**: Capital gains and tax calculations
- **Multi-exchange Support**: Connect to multiple exchanges

### AI/ML Features
- **Price Prediction**: Machine learning price prediction models
- **Risk Assessment**: AI-powered risk analysis
- **Portfolio Optimization**: ML-based portfolio optimization
- **Anomaly Detection**: Detect unusual trading patterns
- **Sentiment Analysis**: Advanced sentiment analysis from multiple sources

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review CoinGecko API documentation for cryptocurrency data
- Consult FastAPI documentation for API development
- Check WebSocket documentation for real-time features

---

**Built with ❤️ using FastAPI for real-time cryptocurrency tracking**
