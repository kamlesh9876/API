# Blockchain Transaction Monitoring API

A comprehensive API for monitoring blockchain transactions across multiple chains with real-time alerts and suspicious activity detection.

## Features

- **Multi-Chain Support**: Ethereum, Bitcoin, Polygon monitoring
- **Real-time Monitoring**: Background task for continuous transaction tracking
- **Smart Alerts**: Configurable alerts for large transactions, suspicious activity, and failed transactions
- **Wallet Management**: Add, remove, and configure multiple wallet addresses
- **Transaction History**: Complete transaction records with detailed information
- **Suspicious Activity Detection**: AI-powered pattern recognition for unusual behavior
- **Alert Management**: Create, resolve, and filter alerts by severity
- **Analytics Dashboard**: Comprehensive statistics and monitoring insights

## API Endpoints

### Wallet Management

#### Add Wallet
```http
POST /api/wallets
Content-Type: application/json

{
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "label": "Main Wallet",
  "is_monitored": true,
  "alert_threshold": 10.0
}
```

#### Get All Wallets
```http
GET /api/wallets
```

#### Get Specific Wallet
```http
GET /api/wallets/{address}
```

#### Delete Wallet
```http
DELETE /api/wallets/{address}
```

#### Sync Wallet Transactions
```http
POST /api/wallets/{address}/sync
```

### Transaction Management

#### Get Wallet Transactions
```http
GET /api/wallets/{address}/transactions?limit=50
```

### Alert Management

#### Get All Alerts
```http
GET /api/alerts?resolved=false&severity=high
```

#### Resolve Alert
```http
POST /api/alerts/{alert_id}/resolve
```

### Monitoring Control

#### Start Monitoring
```http
POST /api/monitoring/start
```

#### Stop Monitoring
```http
POST /api/monitoring/stop
```

#### Get Monitoring Status
```http
GET /api/monitoring/status
```

### Statistics

#### Get Statistics
```http
GET /api/stats
```

## Data Models

### Transaction
```json
{
  "hash": "0x...",
  "block_number": 18000001,
  "from_address": "0x...",
  "to_address": "0x...",
  "value": "1000000000000000000",
  "gas_used": "21000",
  "gas_price": "20000000000",
  "timestamp": "2024-01-01T12:00:00",
  "status": "confirmed",
  "confirmations": 6
}
```

### Wallet
```json
{
  "address": "0x...",
  "label": "Main Wallet",
  "balance": "10.5",
  "is_monitored": true,
  "alert_threshold": 5.0
}
```

### Alert
```json
{
  "id": "alert_123",
  "wallet_address": "0x...",
  "transaction_hash": "0x...",
  "alert_type": "large_transaction",
  "message": "Large transaction detected: 15.7500 ETH",
  "severity": "high",
  "timestamp": "2024-01-01T12:00:00",
  "is_resolved": false
}
```

## Alert Types

### 1. Large Transaction
- **Trigger**: Transaction exceeds wallet's alert threshold
- **Severity**: High
- **Action**: Immediate notification

### 2. Suspicious Activity
- **Trigger**: Unusual transaction patterns detected
- **Examples**: High frequency, large amounts, failed transactions
- **Severity**: Medium to Critical
- **Action**: Review recommended

### 3. Failed Transaction
- **Trigger**: Transaction execution failure
- **Severity**: Low
- **Action**: Log for analysis

## Suspicious Activity Detection

The API uses pattern recognition to identify:

- **High Frequency Transactions**: Multiple transactions to same address within short time
- **Large Amount Transfers**: Unusually high transaction amounts
- **Failed Transaction Patterns**: Repeated failed attempts
- **Timing Anomalies**: Unusual transaction timing patterns

## Installation

```bash
pip install fastapi uvicorn aiohttp
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
import time

# Add wallet to monitor
response = requests.post("http://localhost:8000/api/wallets", json={
    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "label": "Main Wallet",
    "alert_threshold": 5.0
})

# Start monitoring
requests.post("http://localhost:8000/api/monitoring/start")

# Check alerts after some time
time.sleep(60)
alerts = requests.get("http://localhost:8000/api/alerts").json()
for alert in alerts:
    print(f"Alert: {alert['message']} - {alert['severity']}")
```

### JavaScript Client
```javascript
// Add wallet
await fetch('http://localhost:8000/api/wallets', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    address: '0x1234567890abcdef1234567890abcdef12345678',
    label: 'Main Wallet',
    alert_threshold: 5.0
  })
});

// Start monitoring
await fetch('http://localhost:8000/api/monitoring/start', {method: 'POST'});

// Get alerts
const alerts = await fetch('http://localhost:8000/api/alerts').json();
console.log(alerts);
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Blockchain API Keys
ETHERSCAN_API_KEY=your-etherscan-key
BLOCKCHAIN_API_KEY=your-blockchain-info-key
POLYGONSCAN_API_KEY=your-polygonscan-key

# Monitoring Settings
MONITORING_INTERVAL=60
MAX_TRANSACTIONS_PER_QUERY=1000

# Database (for persistence)
DATABASE_URL=sqlite:///./blockchain_monitor.db
```

## Supported Blockchains

### Ethereum
- **API**: Etherscan
- **Features**: Full transaction history, gas tracking
- **Updates**: Real-time block monitoring

### Bitcoin
- **API**: Blockchain.info
- **Features**: UTXO tracking, address monitoring
- **Updates**: Block confirmation tracking

### Polygon
- **API**: Polygonscan
- **Features**: Low-cost transaction tracking
- **Updates**: Bridge transaction monitoring

## Use Cases

- **DeFi Protocols**: Monitor user transactions and detect unusual activity
- **Exchanges**: Compliance and AML monitoring
- **Investment Funds**: Portfolio transaction tracking
- **Smart Contract Audits**: Monitor contract interactions
- **Personal Finance**: Track personal wallet activity
- **Security Teams**: Detect potential security breaches

## Advanced Features

### Custom Alert Thresholds
Set different thresholds for different wallets:
- High-value wallets: Lower thresholds
- Active wallets: Frequency-based alerts
- Cold storage: Movement-only alerts

### Multi-Chain Correlation
Track related addresses across different chains:
- Identify cross-chain arbitrage
- Detect wash trading patterns
- Monitor bridge transactions

### Historical Analysis
- Transaction pattern analysis
- Volume trend identification
- Risk scoring based on history

## Production Considerations

- **Database Integration**: PostgreSQL for transaction storage
- **Rate Limiting**: Respect blockchain API limits
- **Caching**: Redis for frequently accessed data
- **WebSockets**: Real-time alert delivery
- **Authentication**: API key-based access control
- **Monitoring**: Health checks and performance metrics

## Security Features

- **API Key Management**: Secure blockchain API key storage
- **Data Encryption**: Sensitive wallet data encryption
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete action audit trail
- **Rate Limiting**: Prevent abuse and API exhaustion
