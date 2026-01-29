# Currency Exchange API

A comprehensive currency exchange service providing real-time exchange rates, currency conversion, historical data, and portfolio management. Built with FastAPI, this service supports both fiat and cryptocurrencies with advanced analytics and alerting features.

## 🚀 Features

### Exchange Rates
- **Real-time Rates**: Live currency exchange rates
- **Multiple Currency Types**: Support for fiat, crypto, and commodities
- **Historical Data**: Access historical exchange rate data
- **Batch Conversion**: Convert multiple currency pairs simultaneously
- **Rate Sources**: Multiple data sources with fallback support

### Currency Management
- **Currency Database**: Comprehensive currency information
- **Currency Types**: Fiat, cryptocurrency, and commodity support
- **Active/Inactive Status**: Manage currency availability
- **Currency Metadata**: Symbols, countries, and additional info

### Advanced Features
- **Rate Alerts**: Create alerts for specific rate conditions
- **Portfolio Management**: Track multi-currency portfolios
- **Market Analytics**: Comprehensive market statistics
- **Historical Analysis**: Trend analysis and predictions
- **API Integration**: RESTful API with comprehensive endpoints

### Analytics & Monitoring
- **Market Statistics**: Real-time market overview
- **Currency Statistics**: Individual currency performance
- **Volume Tracking**: 24-hour trading volumes
- **Price Changes**: Real-time price movements
- **Market Cap**: Cryptocurrency market capitalization

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Data Validation**: Pydantic models with currency validation
- **Enum Types**: Type-safe currency and rate management
- **Background Tasks**: Asyncio for rate updates
- **Mock Data**: Realistic mock exchange rates

## 📋 API Endpoints

### Currency Management

#### List Currencies
```http
GET /api/currencies?type=fiat&is_active=true&limit=50&offset=0
```

#### Get Currency Details
```http
GET /api/currencies/{code}
```

### Exchange Rates

#### Get Exchange Rates
```http
GET /api/rates/{base_currency}?targets=EUR,GBP,JPY&type=live
```

#### Convert Currency
```http
POST /api/convert
Content-Type: application/json

{
  "amount": 100.50,
  "from_currency": "USD",
  "to_currency": "EUR",
  "rate_type": "live",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### Batch Convert
```http
POST /api/convert/batch
Content-Type: application/json

[
  {
    "amount": 100,
    "from_currency": "USD",
    "to_currency": "EUR"
  },
  {
    "amount": 50,
    "from_currency": "GBP",
    "to_currency": "JPY"
  }
]
```

### Historical Data

#### Get Historical Rates
```http
POST /api/historical
Content-Type: application/json

{
  "base_currency": "USD",
  "target_currency": "EUR",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "timeframe": "1d"
}
```

### Rate Alerts

#### Create Rate Alert
```http
POST /api/alerts
Content-Type: application/json

{
  "base_currency": "BTC",
  "target_currency": "USD",
  "target_rate": 50000,
  "condition": "above",
  "is_active": true,
  "notification_email": "user@example.com",
  "notification_webhook": "https://yourapp.com/webhook"
}
```

#### List Alerts
```http
GET /api/alerts?is_active=true&limit=50&offset=0
```

#### Delete Alert
```http
DELETE /api/alerts/{alert_id}
```

### Portfolio Management

#### Create Portfolio
```http
POST /api/portfolios
Content-Type: application/json

{
  "name": "My Investment Portfolio",
  "currencies": {
    "BTC": 0.5,
    "ETH": 10,
    "USD": 5000
  },
  "base_currency": "USD"
}
```

#### Get Portfolio
```http
GET /api/portfolios/{portfolio_id}
```

### Analytics

#### Get Market Statistics
```http
GET /api/stats/market
```

#### Get Currency Statistics
```http
GET /api/stats/currency/{currency}
```

## 📊 Data Models

### Currency
```python
class Currency(BaseModel):
    code: str
    name: str
    symbol: str
    type: CurrencyType
    country: Optional[str] = None
    is_active: bool = True
```

### ExchangeRate
```python
class ExchangeRate(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    timestamp: datetime
    source: str
    type: RateType = RateType.LIVE
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
```

### ConversionRequest
```python
class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    rate_type: RateType = RateType.LIVE
    timestamp: Optional[datetime] = None
```

### RateAlert
```python
class RateAlert(BaseModel):
    id: Optional[str] = None
    base_currency: str
    target_currency: str
    target_rate: float
    condition: str  # "above", "below", "equal"
    is_active: bool = True
    created_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    notification_email: Optional[str] = None
    notification_webhook: Optional[str] = None
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
RATE_UPDATE_INTERVAL=60
MAX_CONVERSION_AMOUNT=1000000
ALERT_CHECK_INTERVAL=30
HISTORICAL_DATA_DAYS=365
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Get exchange rates
response = requests.get("http://localhost:8000/api/rates/USD?targets=EUR,GBP,JPY")
rates_data = response.json()
print(f"Exchange rates: {rates_data['rates']}")

# Convert currency
conversion_data = {
    "amount": 100.50,
    "from_currency": "USD",
    "to_currency": "EUR",
    "rate_type": "live"
}

convert_response = requests.post(
    "http://localhost:8000/api/convert",
    json=conversion_data
)

conversion_result = convert_response.json()
print(f"Conversion result: {conversion_result['conversion']}")

# Create rate alert
alert_data = {
    "base_currency": "BTC",
    "target_currency": "USD",
    "target_rate": 50000,
    "condition": "above",
    "notification_email": "user@example.com"
}

alert_response = requests.post(
    "http://localhost:8000/api/alerts",
    json=alert_data
)

print(f"Alert created: {alert_response.json()}")

# Create portfolio
portfolio_data = {
    "name": "My Crypto Portfolio",
    "currencies": {
        "BTC": 0.5,
        "ETH": 10,
        "USDT": 1000
    },
    "base_currency": "USD"
}

portfolio_response = requests.post(
    "http://localhost:8000/api/portfolios",
    json=portfolio_data
)

portfolio_result = portfolio_response.json()
portfolio_id = portfolio_result['portfolio_id']
print(f"Portfolio created with ID: {portfolio_id}")

# Get portfolio value
portfolio_value_response = requests.get(f"http://localhost:8000/api/portfolios/{portfolio_id}")
portfolio_info = portfolio_value_response.json()
print(f"Portfolio value: ${portfolio_info['portfolio']['current_value']:.2f}")

# Get historical data
historical_data = {
    "base_currency": "BTC",
    "target_currency": "USD",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z",
    "timeframe": "1d"
}

historical_response = requests.post(
    "http://localhost:8000/api/historical",
    json=historical_data
)

historical_result = historical_response.json()
print(f"Historical data points: {historical_result['data_points']}")
```

### JavaScript Client
```javascript
// Get exchange rates
fetch('http://localhost:8000/api/rates/USD?targets=EUR,GBP,JPY')
.then(response => response.json())
.then(data => {
    console.log('Exchange rates:', data.rates);
    
    // Display rates
    Object.entries(data.rates).forEach(([currency, rateInfo]) => {
        console.log(`1 USD = ${rateInfo.rate} ${currency}`);
    });
})
.catch(error => console.error('Error:', error));

// Convert currency
const conversionData = {
    amount: 100.50,
    from_currency: "USD",
    to_currency: "EUR",
    rate_type: "live"
};

fetch('http://localhost:8000/api/convert', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(conversionData)
})
.then(response => response.json())
.then(data => {
    console.log('Conversion result:', data.conversion);
    console.log(`${data.conversion.amount} ${data.conversion.from_currency} = ${data.conversion.converted_amount} ${data.conversion.to_currency}`);
})
.catch(error => console.error('Error:', error));

// Create portfolio
const portfolioData = {
    name: "My Investment Portfolio",
    currencies: {
        "BTC": 0.5,
        "ETH": 10,
        "USD": 5000
    },
    base_currency: "USD"
};

fetch('http://localhost:8000/api/portfolios', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(portfolioData)
})
.then(response => response.json())
.then(data => {
    console.log('Portfolio created:', data);
    
    // Get portfolio details
    return fetch(`http://localhost:8000/api/portfolios/${data.portfolio_id}`);
})
.then(response => response.json())
.then(portfolio => {
    console.log('Portfolio value:', portfolio.portfolio.current_value);
    console.log('24h change:', portfolio.portfolio.change_percentage_24h.toFixed(2) + '%');
})
.catch(error => console.error('Error:', error));
```

## 🔧 Configuration

### Environment Variables
```bash
# Rate Updates
RATE_UPDATE_INTERVAL=60
RATE_SOURCE_API_KEY=your_api_key
RATE_SOURCE_URL=https://api.exchangerate.com
MAX_RATE_AGE=300

# Conversion Limits
MAX_CONVERSION_AMOUNT=1000000
MAX_BATCH_SIZE=100
CONVERSION_TIMEOUT=30

# Historical Data
HISTORICAL_DATA_DAYS=365
MAX_HISTORICAL_REQUESTS=10
HISTORICAL_CACHE_TTL=3600

# Alerts
ALERT_CHECK_INTERVAL=30
MAX_ALERTS_PER_USER=100
ALERT_NOTIFICATION_RETRIES=3

# Portfolio Management
MAX_PORTFOLIOS_PER_USER=10
MAX_CURRENCIES_PER_PORTFOLIO=20
PORTFOLIO_UPDATE_INTERVAL=60

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=300
ENABLE_CACHING=true

# Security
API_KEY_REQUIRED=false
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/currency_exchange.log
AUDIT_LOG_ENABLED=true
```

### Currency Types
- **fiat**: Traditional government-issued currencies (USD, EUR, GBP, etc.)
- **crypto**: Cryptocurrencies (BTC, ETH, USDT, etc.)
- **commodity**: Commodities (Gold XAU, Silver XAG, etc.)

### Rate Types
- **live**: Real-time current rates
- **historical**: Historical rates at specific timestamps
- **average**: Average rates over a period
- **predicted**: AI-predicted future rates

### Timeframes
- **1m**: 1 minute intervals
- **1h**: 1 hour intervals
- **1d**: 1 day intervals
- **1w**: 1 week intervals
- **1M**: 1 month intervals
- **1Y**: 1 year intervals

## 📈 Use Cases

### Financial Applications
- **Currency Converters**: Real-time currency conversion tools
- **Investment Portfolios**: Multi-currency portfolio tracking
- **Trading Platforms**: Cryptocurrency and forex trading
- **Financial Analytics**: Market analysis and reporting
- **Risk Management**: Currency risk assessment

### Business Applications
- **E-commerce**: Multi-currency pricing and payments
- **International Business**: Cross-border transactions
- **Accounting Software**: Multi-currency bookkeeping
- **ERP Systems**: Enterprise resource planning
- **Travel Applications**: Currency conversion for travelers

### Data Applications
- **Market Research**: Currency market analysis
- **Economic Indicators**: Economic data tracking
- **Price Comparison**: International price comparisons
- **Inflation Tracking**: Currency value monitoring
- **Forecasting**: Currency trend prediction

## 🛡️ Security Features

### API Security
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Comprehensive input validation
- **CORS Support**: Cross-origin request handling
- **Authentication**: Optional API key protection
- **Audit Logging**: Track all API activities

### Data Security
- **Data Encryption**: Encrypt sensitive data
- **Secure Storage**: Secure database connections
- **Access Control**: Role-based access control
- **Data Validation**: Validate all input data
- **Error Handling**: Secure error responses

## 📊 Monitoring

### Rate Monitoring
- **Update Frequency**: Monitor rate update intervals
- **Data Quality**: Validate rate accuracy
- **Source Health**: Monitor data source availability
- **Latency**: Track API response times
- **Error Rates**: Monitor API error rates

### Performance Metrics
- **Response Time**: API response time tracking
- **Throughput**: Requests per second
- **Cache Hit Rate**: Caching effectiveness
- **Database Performance**: Query optimization
- **Memory Usage**: Resource consumption

## 🔗 Related APIs

- **Payment Gateway API**: For processing currency payments
- **Banking API**: For traditional banking integration
- **Crypto Wallet API**: For cryptocurrency management
- **Analytics API**: For advanced financial analytics
- **Notification API**: For alert notifications

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API with mock data. In production, integrate with real exchange rate providers like:
- **ExchangeRate-API**: Real-time exchange rates
- **Fixer.io**: Currency conversion API
- **CoinGecko**: Cryptocurrency rates
- **CoinMarketCap**: Crypto market data
- **Alpha Vantage**: Forex and crypto data
- **Yahoo Finance**: Financial market data
