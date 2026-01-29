from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime, timedelta
import json
import random
import math

app = FastAPI(
    title="Currency Exchange API",
    description="Real-time currency exchange rates and conversion service with historical data",
    version="1.0.0"
)

# Enums
class CurrencyType(str, Enum):
    FIAT = "fiat"
    CRYPTO = "crypto"
    COMMODITY = "commodity"

class RateType(str, Enum):
    LIVE = "live"
    HISTORICAL = "historical"
    AVERAGE = "average"
    PREDICTED = "predicted"

class Timeframe(str, Enum):
    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"
    YEAR = "1Y"

# Data Models
class Currency(BaseModel):
    code: str
    name: str
    symbol: str
    type: CurrencyType
    country: Optional[str] = None
    is_active: bool = True
    
    @validator('code')
    def validate_currency_code(cls, v):
        if len(v) != 3:
            raise ValueError('Currency code must be 3 characters')
        return v.upper()

class ExchangeRate(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    timestamp: datetime
    source: str
    type: RateType = RateType.LIVE
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None

class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    rate_type: RateType = RateType.LIVE
    timestamp: Optional[datetime] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class ConversionResult(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    rate: float
    timestamp: datetime
    rate_type: RateType

class HistoricalRequest(BaseModel):
    base_currency: str
    target_currency: str
    start_date: datetime
    end_date: datetime
    timeframe: Timeframe = Timeframe.DAY

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

class Portfolio(BaseModel):
    id: Optional[str] = None
    name: str
    currencies: Dict[str, float]  # currency_code -> amount
    base_currency: str = "USD"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Storage (in production, use database)
currencies = {}
exchange_rates = {}
rate_alerts = {}
portfolios = {}
rate_history = {}

# Initialize with common currencies
def initialize_currencies():
    global currencies
    
    # Major fiat currencies
    fiat_currencies = [
        {"code": "USD", "name": "US Dollar", "symbol": "$", "type": CurrencyType.FIAT, "country": "United States"},
        {"code": "EUR", "name": "Euro", "symbol": "€", "type": CurrencyType.FIAT, "country": "European Union"},
        {"code": "GBP", "name": "British Pound", "symbol": "£", "type": CurrencyType.FIAT, "country": "United Kingdom"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "type": CurrencyType.FIAT, "country": "Japan"},
        {"code": "CHF", "name": "Swiss Franc", "symbol": "Fr", "type": CurrencyType.FIAT, "country": "Switzerland"},
        {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "type": CurrencyType.FIAT, "country": "Canada"},
        {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "type": CurrencyType.FIAT, "country": "Australia"},
        {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "type": CurrencyType.FIAT, "country": "China"},
        {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "type": CurrencyType.FIAT, "country": "India"},
        {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "type": CurrencyType.FIAT, "country": "Brazil"},
    ]
    
    # Major cryptocurrencies
    crypto_currencies = [
        {"code": "BTC", "name": "Bitcoin", "symbol": "₿", "type": CurrencyType.CRYPTO},
        {"code": "ETH", "name": "Ethereum", "symbol": "Ξ", "type": CurrencyType.CRYPTO},
        {"code": "USDT", "name": "Tether", "symbol": "₮", "type": CurrencyType.CRYPTO},
        {"code": "BNB", "name": "Binance Coin", "symbol": "BNB", "type": CurrencyType.CRYPTO},
        {"code": "SOL", "name": "Solana", "symbol": "SOL", "type": CurrencyType.CRYPTO},
        {"code": "ADA", "name": "Cardano", "symbol": "ADA", "type": CurrencyType.CRYPTO},
        {"code": "XRP", "name": "Ripple", "symbol": "XRP", "type": CurrencyType.CRYPTO},
        {"code": "DOGE", "name": "Dogecoin", "symbol": "Ð", "type": CurrencyType.CRYPTO},
    ]
    
    # Commodities
    commodity_currencies = [
        {"code": "XAU", "name": "Gold", "symbol": "XAU", "type": CurrencyType.COMMODITY},
        {"code": "XAG", "name": "Silver", "symbol": "XAG", "type": CurrencyType.COMMODITY},
        {"code": "XPT", "name": "Platinum", "symbol": "XPT", "type": CurrencyType.COMMODITY},
        {"code": "XPD", "name": "Palladium", "symbol": "XPD", "type": CurrencyType.COMMODITY},
    ]
    
    all_currencies = fiat_currencies + crypto_currencies + commodity_currencies
    
    for currency_data in all_currencies:
        currency = Currency(**currency_data)
        currencies[currency.code] = currency.dict()

def generate_mock_rate(base: str, target: str) -> float:
    """Generate realistic mock exchange rates"""
    # Base rates relative to USD
    base_rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.0,
        "CHF": 0.92,
        "CAD": 1.25,
        "AUD": 1.35,
        "CNY": 6.45,
        "INR": 74.0,
        "BRL": 5.2,
        "BTC": 0.000023,
        "ETH": 0.00031,
        "USDT": 1.0,
        "BNB": 0.0023,
        "SOL": 0.015,
        "ADA": 1.25,
        "XRP": 2.5,
        "DOGE": 2500,
        "XAU": 0.00052,
        "XAG": 0.017,
        "XPT": 0.000011,
        "XPD": 0.000009,
    }
    
    base_rate = base_rates.get(base, 1.0)
    target_rate = base_rates.get(target, 1.0)
    
    # Calculate rate with small random variation
    if base == "USD":
        rate = target_rate
    elif target == "USD":
        rate = 1.0 / base_rate
    else:
        rate = target_rate / base_rate
    
    # Add small random variation (±0.5%)
    variation = random.uniform(-0.005, 0.005)
    rate = rate * (1 + variation)
    
    return round(rate, 6)

def initialize_rates():
    """Initialize mock exchange rates"""
    global exchange_rates
    
    currency_codes = list(currencies.keys())
    
    for base in currency_codes:
        for target in currency_codes:
            if base != target:
                rate_key = f"{base}_{target}"
                exchange_rates[rate_key] = {
                    "rate": generate_mock_rate(base, target),
                    "timestamp": datetime.now(),
                    "source": "mock_provider",
                    "type": RateType.LIVE,
                    "volume_24h": random.uniform(1000000, 100000000),
                    "market_cap": random.uniform(100000000, 10000000000)
                }

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    initialize_currencies()
    initialize_rates()

@app.get("/")
async def root():
    return {"message": "Currency Exchange API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Currency Management
@app.get("/api/currencies")
async def list_currencies(
    type: Optional[CurrencyType] = None,
    is_active: Optional[bool] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """List available currencies"""
    try:
        filtered_currencies = list(currencies.values())
        
        # Apply filters
        if type:
            filtered_currencies = [c for c in filtered_currencies if c.get("type") == type]
        if is_active is not None:
            filtered_currencies = [c for c in filtered_currencies if c.get("is_active") == is_active]
        
        # Apply pagination
        total = len(filtered_currencies)
        paginated_currencies = filtered_currencies[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "currencies": paginated_currencies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list currencies: {str(e)}")

@app.get("/api/currencies/{code}")
async def get_currency(code: str):
    """Get currency details"""
    code = code.upper()
    if code not in currencies:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    return {
        "success": True,
        "currency": currencies[code]
    }

# Exchange Rates
@app.get("/api/rates/{base_currency}")
async def get_exchange_rates(
    base_currency: str,
    targets: Optional[str] = None,  # Comma-separated list of target currencies
    type: RateType = RateType.LIVE
):
    """Get exchange rates for a base currency"""
    try:
        base_currency = base_currency.upper()
        
        if base_currency not in currencies:
            raise HTTPException(status_code=404, detail="Base currency not found")
        
        target_currencies = targets.split(',') if targets else [c for c in currencies.keys() if c != base_currency]
        target_currencies = [c.strip().upper() for c in target_currencies]
        
        rates = {}
        for target in target_currencies:
            if target in currencies and target != base_currency:
                rate_key = f"{base_currency}_{target}"
                
                if rate_key in exchange_rates:
                    rate_data = exchange_rates[rate_key]
                    
                    # Update timestamp for live rates
                    if type == RateType.LIVE:
                        rate_data["rate"] = generate_mock_rate(base_currency, target)
                        rate_data["timestamp"] = datetime.now()
                    
                    rates[target] = rate_data
        
        return {
            "success": True,
            "base_currency": base_currency,
            "timestamp": datetime.now().isoformat(),
            "type": type,
            "rates": rates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get exchange rates: {str(e)}")

@app.post("/api/convert")
async def convert_currency(conversion: ConversionRequest):
    """Convert amount from one currency to another"""
    try:
        from_currency = conversion.from_currency.upper()
        to_currency = conversion.to_currency.upper()
        
        if from_currency not in currencies:
            raise HTTPException(status_code=404, detail="Source currency not found")
        if to_currency not in currencies:
            raise HTTPException(status_code=404, detail="Target currency not found")
        
        # Get exchange rate
        rate_key = f"{from_currency}_{to_currency}"
        
        if rate_key not in exchange_rates:
            raise HTTPException(status_code=404, detail="Exchange rate not available")
        
        rate_data = exchange_rates[rate_key]
        
        # Update rate for live conversions
        if conversion.rate_type == RateType.LIVE:
            rate_data["rate"] = generate_mock_rate(from_currency, to_currency)
            rate_data["timestamp"] = datetime.now()
        
        # Calculate conversion
        converted_amount = conversion.amount * rate_data["rate"]
        
        result = ConversionResult(
            amount=conversion.amount,
            from_currency=from_currency,
            to_currency=to_currency,
            converted_amount=round(converted_amount, 6),
            rate=rate_data["rate"],
            timestamp=rate_data["timestamp"],
            rate_type=conversion.rate_type
        )
        
        return {
            "success": True,
            "conversion": result.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/api/convert/batch")
async def convert_batch(
    conversions: List[ConversionRequest],
    background_tasks: BackgroundTasks
):
    """Convert multiple currency pairs"""
    try:
        results = []
        
        for conversion in conversions:
            try:
                from_currency = conversion.from_currency.upper()
                to_currency = conversion.to_currency.upper()
                
                if from_currency not in currencies or to_currency not in currencies:
                    results.append({
                        "success": False,
                        "error": "Currency not found",
                        "from_currency": from_currency,
                        "to_currency": to_currency
                    })
                    continue
                
                rate_key = f"{from_currency}_{to_currency}"
                if rate_key not in exchange_rates:
                    results.append({
                        "success": False,
                        "error": "Exchange rate not available",
                        "from_currency": from_currency,
                        "to_currency": to_currency
                    })
                    continue
                
                rate_data = exchange_rates[rate_key]
                
                if conversion.rate_type == RateType.LIVE:
                    rate_data["rate"] = generate_mock_rate(from_currency, to_currency)
                    rate_data["timestamp"] = datetime.now()
                
                converted_amount = conversion.amount * rate_data["rate"]
                
                result = ConversionResult(
                    amount=conversion.amount,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    converted_amount=round(converted_amount, 6),
                    rate=rate_data["rate"],
                    timestamp=rate_data["timestamp"],
                    rate_type=conversion.rate_type
                )
                
                results.append({
                    "success": True,
                    "conversion": result.dict()
                })
                
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "from_currency": conversion.from_currency,
                    "to_currency": conversion.to_currency
                })
        
        return {
            "success": True,
            "total_conversions": len(conversions),
            "successful_conversions": len([r for r in results if r["success"]]),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {str(e)}")

# Historical Data
@app.post("/api/historical")
async def get_historical_rates(request: HistoricalRequest):
    """Get historical exchange rates"""
    try:
        base_currency = request.base_currency.upper()
        target_currency = request.target_currency.upper()
        
        if base_currency not in currencies:
            raise HTTPException(status_code=404, detail="Base currency not found")
        if target_currency not in currencies:
            raise HTTPException(status_code=404, detail="Target currency not found")
        
        # Generate historical data
        historical_data = []
        current_date = request.start_date
        
        while current_date <= request.end_date:
            # Generate mock historical rate
            base_rate = generate_mock_rate(base_currency, target_currency)
            
            # Add trend and volatility
            days_diff = (current_date - request.start_date).days
            trend = math.sin(days_diff * 0.1) * 0.05  # Sinusoidal trend
            volatility = random.uniform(-0.02, 0.02)  # Random volatility
            
            historical_rate = base_rate * (1 + trend + volatility)
            
            historical_data.append({
                "date": current_date.isoformat(),
                "rate": round(historical_rate, 6),
                "volume": random.uniform(1000000, 100000000),
                "high": round(historical_rate * 1.02, 6),
                "low": round(historical_rate * 0.98, 6),
                "open": round(historical_rate * 0.99, 6),
                "close": round(historical_rate, 6)
            })
            
            # Move to next date based on timeframe
            if request.timeframe == Timeframe.MINUTE:
                current_date += timedelta(minutes=1)
            elif request.timeframe == Timeframe.HOUR:
                current_date += timedelta(hours=1)
            elif request.timeframe == Timeframe.DAY:
                current_date += timedelta(days=1)
            elif request.timeframe == Timeframe.WEEK:
                current_date += timedelta(weeks=1)
            elif request.timeframe == Timeframe.MONTH:
                current_date += timedelta(days=30)
            elif request.timeframe == Timeframe.YEAR:
                current_date += timedelta(days=365)
        
        return {
            "success": True,
            "base_currency": base_currency,
            "target_currency": target_currency,
            "timeframe": request.timeframe,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "data_points": len(historical_data),
            "data": historical_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get historical data: {str(e)}")

# Rate Alerts
@app.post("/api/alerts")
async def create_rate_alert(alert: RateAlert):
    """Create a rate alert"""
    try:
        alert_id = str(uuid.uuid4())
        
        alert_record = alert.dict()
        alert_record["id"] = alert_id
        alert_record["created_at"] = datetime.now()
        
        rate_alerts[alert_id] = alert_record
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Rate alert created successfully",
            "alert": alert_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@app.get("/api/alerts")
async def list_alerts(
    is_active: Optional[bool] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """List rate alerts"""
    try:
        filtered_alerts = list(rate_alerts.values())
        
        if is_active is not None:
            filtered_alerts = [a for a in filtered_alerts if a.get("is_active") == is_active]
        
        total = len(filtered_alerts)
        paginated_alerts = filtered_alerts[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "alerts": paginated_alerts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list alerts: {str(e)}")

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete a rate alert"""
    try:
        if alert_id not in rate_alerts:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        del rate_alerts[alert_id]
        
        return {
            "success": True,
            "message": "Alert deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")

# Portfolio Management
@app.post("/api/portfolios")
async def create_portfolio(portfolio: Portfolio):
    """Create a currency portfolio"""
    try:
        portfolio_id = str(uuid.uuid4())
        
        portfolio_record = portfolio.dict()
        portfolio_record["id"] = portfolio_id
        portfolio_record["created_at"] = datetime.now()
        portfolio_record["updated_at"] = datetime.now()
        
        # Calculate portfolio value in base currency
        portfolio_value = 0.0
        for currency_code, amount in portfolio.currencies.items():
            if currency_code.upper() != portfolio.base_currency.upper():
                rate_key = f"{currency_code.upper()}_{portfolio.base_currency.upper()}"
                if rate_key in exchange_rates:
                    rate = exchange_rates[rate_key]["rate"]
                    portfolio_value += amount * rate
                else:
                    portfolio_value += amount  # Assume 1:1 if rate not available
            else:
                portfolio_value += amount
        
        portfolio_record["total_value"] = portfolio_value
        
        portfolios[portfolio_id] = portfolio_record
        
        return {
            "success": True,
            "portfolio_id": portfolio_id,
            "message": "Portfolio created successfully",
            "portfolio": portfolio_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create portfolio: {str(e)}")

@app.get("/api/portfolios/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """Get portfolio details and current value"""
    try:
        if portfolio_id not in portfolios:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio = portfolios[portfolio_id]
        
        # Recalculate current value
        current_value = 0.0
        currency_values = {}
        
        for currency_code, amount in portfolio["currencies"].items():
            if currency_code.upper() != portfolio["base_currency"].upper():
                rate_key = f"{currency_code.upper()}_{portfolio['base_currency'].upper()}"
                if rate_key in exchange_rates:
                    rate = exchange_rates[rate_key]["rate"]
                    value_in_base = amount * rate
                    currency_values[currency_code] = {
                        "amount": amount,
                        "rate": rate,
                        "value_in_base": value_in_base
                    }
                    current_value += value_in_base
                else:
                    currency_values[currency_code] = {
                        "amount": amount,
                        "rate": 1.0,
                        "value_in_base": amount
                    }
                    current_value += amount
            else:
                currency_values[currency_code] = {
                    "amount": amount,
                    "rate": 1.0,
                    "value_in_base": amount
                }
                current_value += amount
        
        # Calculate 24h change (mock)
        change_24h = random.uniform(-5, 5)
        change_percentage = (change_24h / current_value) * 100 if current_value > 0 else 0
        
        portfolio["current_value"] = current_value
        portfolio["currency_breakdown"] = currency_values
        portfolio["change_24h"] = change_24h
        portfolio["change_percentage_24h"] = change_percentage
        portfolio["updated_at"] = datetime.now()
        
        return {
            "success": True,
            "portfolio": portfolio
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")

# Analytics and Statistics
@app.get("/api/stats/market")
async def get_market_stats():
    """Get market statistics"""
    try:
        # Calculate market stats
        total_currencies = len(currencies)
        active_rates = len(exchange_rates)
        
        # Top currencies by volume (mock data)
        top_currencies = ["BTC", "ETH", "USDT", "BNB", "SOL"]
        volume_stats = {}
        
        for currency in top_currencies:
            volume_stats[currency] = {
                "volume_24h": random.uniform(1000000000, 50000000000),
                "change_24h": random.uniform(-10, 10),
                "market_cap": random.uniform(10000000000, 1000000000000)
            }
        
        # Rate changes (mock data)
        rate_changes = {}
        sample_pairs = ["USD_EUR", "USD_GBP", "USD_JPY", "BTC_USD", "ETH_USD"]
        
        for pair in sample_pairs:
            if pair in exchange_rates:
                current_rate = exchange_rates[pair]["rate"]
                change_24h = random.uniform(-5, 5)
                rate_changes[pair] = {
                    "current_rate": current_rate,
                    "change_24h": change_24h,
                    "change_percentage_24h": (change_24h / current_rate) * 100
                }
        
        return {
            "success": True,
            "statistics": {
                "total_currencies": total_currencies,
                "active_exchange_rates": active_rates,
                "last_updated": datetime.now().isoformat(),
                "top_volumes": volume_stats,
                "rate_changes": rate_changes
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market stats: {str(e)}")

@app.get("/api/stats/currency/{currency}")
async def get_currency_stats(currency: str):
    """Get statistics for a specific currency"""
    try:
        currency = currency.upper()
        
        if currency not in currencies:
            raise HTTPException(status_code=404, detail="Currency not found")
        
        # Calculate currency stats
        currency_info = currencies[currency]
        
        # Get all rates for this currency
        rates_as_base = {}
        rates_as_target = {}
        
        for rate_key, rate_data in exchange_rates.items():
            base, target = rate_key.split('_')
            if base == currency:
                rates_as_base[target] = rate_data
            elif target == currency:
                rates_as_target[base] = rate_data
        
        # Calculate statistics
        total_pairs = len(rates_as_base) + len(rates_as_target)
        avg_rate = sum(r["rate"] for r in rates_as_base.values()) / len(rates_as_base) if rates_as_base else 0
        
        return {
            "success": True,
            "currency": currency_info,
            "statistics": {
                "total_trading_pairs": total_pairs,
                "rates_as_base": len(rates_as_base),
                "rates_as_target": len(rates_as_target),
                "average_rate_as_base": avg_rate,
                "last_updated": datetime.now().isoformat()
            },
            "rates_as_base": rates_as_base,
            "rates_as_target": rates_as_target
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get currency stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
