from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import hashlib
import time

app = FastAPI(title="Blockchain Transaction Monitoring API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Transaction(BaseModel):
    hash: str
    block_number: int
    from_address: str
    to_address: str
    value: str
    gas_used: str
    gas_price: str
    timestamp: datetime
    status: str  # "pending", "confirmed", "failed"
    confirmations: int = 0

class Wallet(BaseModel):
    address: str
    label: Optional[str] = None
    balance: str = "0"
    is_monitored: bool = True
    alert_threshold: Optional[float] = None

class Alert(BaseModel):
    id: str
    wallet_address: str
    transaction_hash: str
    alert_type: str  # "large_transaction", "suspicious_activity", "failed_transaction"
    message: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    is_resolved: bool = False

class MonitoringConfig(BaseModel):
    wallet_addresses: List[str]
    alert_thresholds: Dict[str, float]
    monitoring_interval: int = 60  # seconds
    supported_chains: List[str] = ["ethereum", "bitcoin", "polygon"]

# In-memory storage
monitored_wallets: Dict[str, Wallet] = {}
transactions: Dict[str, Transaction] = {}
alerts: Dict[str, Alert] = {}
monitoring_active: bool = False

# Blockchain API endpoints (mock implementations)
BLOCKCHAIN_APIS = {
    "ethereum": "https://api.etherscan.io/api",
    "bitcoin": "https://blockchain.info/rawaddr/",
    "polygon": "https://api.polygonscan.com/api"
}

# Utility functions
def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return hashlib.md5(f"{time.time()}_{len(alerts)}".encode()).hexdigest()

def format_wei_to_eth(wei_value: str) -> float:
    """Convert Wei to ETH"""
    try:
        return float(wei_value) / 1e18
    except:
        return 0.0

def detect_suspicious_activity(transaction: Transaction) -> List[str]:
    """Detect suspicious transaction patterns"""
    suspicious_indicators = []
    
    # Large transaction amount
    eth_value = format_wei_to_eth(transaction.value)
    if eth_value > 100:  # Large transaction threshold
        suspicious_indicators.append("large_amount")
    
    # Multiple transactions to same address in short time
    recent_txs = [tx for tx in transactions.values() 
                  if tx.to_address == transaction.to_address and 
                  tx.timestamp > datetime.now() - timedelta(hours=1)]
    if len(recent_txs) > 5:
        suspicious_indicators.append("high_frequency")
    
    # Failed transaction
    if transaction.status == "failed":
        suspicious_indicators.append("failed_transaction")
    
    return suspicious_indicators

# Blockchain API calls
async def get_ethereum_transactions(address: str) -> List[Dict]:
    """Mock Ethereum transaction fetch"""
    # In production, this would call actual Etherscan API
    await asyncio.sleep(0.1)  # Simulate API delay
    
    # Mock transaction data
    return [
        {
            "hash": f"0x{hashlib.md5(f'{address}_{i}'.encode()).hexdigest()}",
            "blockNumber": str(18000000 + i),
            "from": address,
            "to": f"0x{'1234567890abcdef' * 2}",
            "value": str(i * 1000000000000000000),  # i ETH in wei
            "gasUsed": "21000",
            "gasPrice": "20000000000",
            "timeStamp": str(int(time.time()) - i * 3600),
            "isError": "0"
        }
        for i in range(5)
    ]

async def get_bitcoin_transactions(address: str) -> List[Dict]:
    """Mock Bitcoin transaction fetch"""
    await asyncio.sleep(0.1)
    return []  # Mock empty for now

async def get_polygon_transactions(address: str) -> List[Dict]:
    """Mock Polygon transaction fetch"""
    return await get_ethereum_transactions(address)  # Similar structure

async def fetch_transactions_for_wallet(wallet: Wallet, chain: str) -> List[Transaction]:
    """Fetch transactions for a specific wallet on a specific chain"""
    try:
        if chain == "ethereum":
            raw_txs = await get_ethereum_transactions(wallet.address)
        elif chain == "bitcoin":
            raw_txs = await get_bitcoin_transactions(wallet.address)
        elif chain == "polygon":
            raw_txs = await get_polygon_transactions(wallet.address)
        else:
            return []
        
        transactions_list = []
        for tx_data in raw_txs:
            transaction = Transaction(
                hash=tx_data["hash"],
                block_number=int(tx_data["blockNumber"]),
                from_address=tx_data["from"],
                to_address=tx_data["to"],
                value=tx_data["value"],
                gas_used=tx_data["gasUsed"],
                gas_price=tx_data["gasPrice"],
                timestamp=datetime.fromtimestamp(int(tx_data["timeStamp"])),
                status="confirmed" if tx_data.get("isError") == "0" else "failed",
                confirmations=6  # Mock confirmations
            )
            transactions_list.append(transaction)
        
        return transactions_list
    
    except Exception as e:
        print(f"Error fetching transactions for {wallet.address} on {chain}: {e}")
        return []

async def create_alert(wallet_address: str, transaction: Transaction, alert_type: str, message: str, severity: str):
    """Create a new alert"""
    alert_id = generate_alert_id()
    alert = Alert(
        id=alert_id,
        wallet_address=wallet_address,
        transaction_hash=transaction.hash,
        alert_type=alert_type,
        message=message,
        severity=severity,
        timestamp=datetime.now()
    )
    alerts[alert_id] = alert
    return alert

async def monitor_wallets():
    """Background task to monitor all wallets"""
    global monitoring_active
    
    while monitoring_active:
        try:
            for wallet_address, wallet in monitored_wallets.items():
                if not wallet.is_monitored:
                    continue
                
                # Fetch transactions from all supported chains
                for chain in ["ethereum", "bitcoin", "polygon"]:
                    new_transactions = await fetch_transactions_for_wallet(wallet, chain)
                    
                    for tx in new_transactions:
                        # Check if transaction is new
                        if tx.hash not in transactions:
                            transactions[tx.hash] = tx
                            
                            # Check for alerts
                            suspicious = detect_suspicious_activity(tx)
                            
                            # Large transaction alert
                            eth_value = format_wei_to_eth(tx.value)
                            if wallet.alert_threshold and eth_value > wallet.alert_threshold:
                                await create_alert(
                                    wallet_address,
                                    tx,
                                    "large_transaction",
                                    f"Large transaction detected: {eth_value:.4f} ETH",
                                    "high"
                                )
                            
                            # Suspicious activity alert
                            if suspicious:
                                await create_alert(
                                    wallet_address,
                                    tx,
                                    "suspicious_activity",
                                    f"Suspicious activity detected: {', '.join(suspicious)}",
                                    "medium"
                                )
                            
                            # Failed transaction alert
                            if tx.status == "failed":
                                await create_alert(
                                    wallet_address,
                                    tx,
                                    "failed_transaction",
                                    "Transaction failed",
                                    "low"
                                )
            
            await asyncio.sleep(60)  # Wait before next check
        
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            await asyncio.sleep(30)  # Wait before retrying

# API Endpoints
@app.post("/api/wallets", response_model=Wallet)
async def add_wallet(wallet: Wallet):
    """Add a wallet to monitoring"""
    monitored_wallets[wallet.address] = wallet
    return wallet

@app.get("/api/wallets", response_model=List[Wallet])
async def get_wallets():
    """Get all monitored wallets"""
    return list(monitored_wallets.values())

@app.get("/api/wallets/{address}", response_model=Wallet)
async def get_wallet(address: str):
    """Get specific wallet information"""
    if address not in monitored_wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return monitored_wallets[address]

@app.delete("/api/wallets/{address}")
async def delete_wallet(address: str):
    """Remove wallet from monitoring"""
    if address not in monitored_wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    del monitored_wallets[address]
    return {"message": "Wallet removed successfully"}

@app.get("/api/wallets/{address}/transactions", response_model=List[Transaction])
async def get_wallet_transactions(address: str, limit: int = 50):
    """Get transactions for a specific wallet"""
    wallet_txs = [tx for tx in transactions.values() 
                  if tx.from_address == address or tx.to_address == address]
    return sorted(wallet_txs, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.get("/api/alerts", response_model=List[Alert])
async def get_alerts(resolved: Optional[bool] = None, severity: Optional[str] = None):
    """Get all alerts with optional filters"""
    filtered_alerts = list(alerts.values())
    
    if resolved is not None:
        filtered_alerts = [alert for alert in filtered_alerts if alert.is_resolved == resolved]
    
    if severity:
        filtered_alerts = [alert for alert in filtered_alerts if alert.severity == severity]
    
    return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    if alert_id not in alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alerts[alert_id].is_resolved = True
    return {"message": "Alert resolved successfully"}

@app.post("/api/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start blockchain monitoring"""
    global monitoring_active
    
    if monitoring_active:
        return {"message": "Monitoring already active"}
    
    monitoring_active = True
    background_tasks.add_task(monitor_wallets)
    return {"message": "Monitoring started"}

@app.post("/api/monitoring/stop")
async def stop_monitoring():
    """Stop blockchain monitoring"""
    global monitoring_active
    monitoring_active = False
    return {"message": "Monitoring stopped"}

@app.get("/api/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    return {
        "active": monitoring_active,
        "monitored_wallets": len(monitored_wallets),
        "total_transactions": len(transactions),
        "unresolved_alerts": len([a for a in alerts.values() if not a.is_resolved])
    }

@app.get("/api/stats")
async def get_stats():
    """Get monitoring statistics"""
    total_value = sum(format_wei_to_eth(tx.value) for tx in transactions.values())
    
    return {
        "total_wallets": len(monitored_wallets),
        "total_transactions": len(transactions),
        "total_alerts": len(alerts),
        "unresolved_alerts": len([a for a in alerts.values() if not a.is_resolved]),
        "total_value_eth": total_value,
        "failed_transactions": len([tx for tx in transactions.values() if tx.status == "failed"]),
        "alert_distribution": {
            severity: len([a for a in alerts.values() if a.severity == severity])
            for severity in ["low", "medium", "high", "critical"]
        }
    }

@app.post("/api/wallets/{address}/sync")
async def sync_wallet_transactions(address: str):
    """Manually sync transactions for a specific wallet"""
    if address not in monitored_wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    wallet = monitored_wallets[address]
    synced_count = 0
    
    for chain in ["ethereum", "bitcoin", "polygon"]:
        new_txs = await fetch_transactions_for_wallet(wallet, chain)
        for tx in new_txs:
            if tx.hash not in transactions:
                transactions[tx.hash] = tx
                synced_count += 1
    
    return {"message": f"Synced {synced_count} new transactions"}

@app.get("/")
async def root():
    return {"message": "Blockchain Transaction Monitoring API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
