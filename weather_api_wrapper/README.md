# Weather API Wrapper

A comprehensive weather API that aggregates data from multiple weather services (OpenWeatherMap, WeatherBit, Visual Crossing) to provide accurate forecasts, air quality data, and weather alerts.

## 🚀 Features

- **Multi-Source Aggregation**: Combines data from OpenWeatherMap, WeatherBit, and Visual Crossing
- **Accurate Forecasts**: Merges multiple data sources for improved accuracy
- **Comprehensive Data**: Temperature, humidity, pressure, visibility, UV index, AQI
- **Air Quality Monitoring**: PM2.5, PM10, O3, NO2, SO2, CO measurements
- **Weather Alerts**: Severe weather warnings and notifications
- **Flexible Units**: Support for Celsius/Fahrenheit, km/h/mph, etc.
- **Real-time Data**: Current conditions with up-to-date information
- **Extended Forecasts**: Hourly (48h) and daily (16-day) forecasts
- **Historical Data**: Access to past weather conditions
- **Error Handling**: Graceful fallback when sources are unavailable

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **HTTP Client**: httpx for async API calls
- **Data Aggregation**: Custom normalization and merging algorithms
- **Error Handling**: Comprehensive exception management
- **Rate Limiting**: Built-in throttling for external APIs

## 📋 Prerequisites

- Python 3.7+
- API keys from weather services:
  - OpenWeatherMap API key
  - WeatherBit API key
  - Visual Crossing API key

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set API keys** (update in `app.py` or use environment variables):
```python
API_KEYS = {
    "openweather": "your-openweather-api-key",
    "weatherbit": "your-weatherbit-api-key",
    "visualcrossing": "your-visualcrossing-api-key"
}
```

3. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8006`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8006/docs`
- ReDoc: `http://localhost:8006/redoc`

## 🌤️ API Endpoints

### Comprehensive Weather Data

#### Get Full Weather Data
```http
GET /weather?lat=40.7128&lon=-74.0060&units=celsius&wind_units=km/h&sources=openweather,weatherbit,visualcrossing
```

**Response Example**:
```json
{
  "location": {
    "name": "New York",
    "country": "US",
    "coordinates": {"lat": 40.7128, "lon": -74.0060}
  },
  "current": {
    "temperature": 22.5,
    "feels_like": 24.1,
    "humidity": 65,
    "pressure": 1013.25,
    "visibility": 10.0,
    "uv_index": 6.2,
    "aqi": 2,
    "wind_speed": 15.3,
    "wind_direction": 180,
    "condition": "clear",
    "description": "clear sky",
    "timestamp": "2024-01-15T12:00:00"
  },
  "hourly": [
    {
      "time": "2024-01-15T13:00:00",
      "temperature": 23.1,
      "humidity": 62,
      "precipitation_probability": 10,
      "condition": "clear"
    }
  ],
  "daily": [
    {
      "date": "2024-01-15",
      "temperature_min": 18.2,
      "temperature_max": 25.8,
      "humidity": 68,
      "precipitation_probability": 20,
      "condition": "partly_cloudy",
      "sunrise": "2024-01-15T07:15:00",
      "sunset": "2024-01-15T17:30:00"
    }
  ],
  "air_quality": {
    "aqi": 2,
    "pm25": 12.5,
    "pm10": 18.2,
    "o3": 45.1,
    "no2": 22.3,
    "so2": 8.7,
    "co": 0.4,
    "category": "Fair"
  },
  "data_sources": ["openweather", "weatherbit"],
  "last_updated": "2024-01-15T12:00:00"
}
```

### Specialized Endpoints

#### Current Weather Only
```http
GET /weather/current?lat=40.7128&lon=-74.0060
```

#### Weather Forecast
```http
GET /weather/forecast?lat=40.7128&lon=-74.0060&days=7&sources=weatherbit,visualcrossing
```

#### Air Quality Data
```http
GET /weather/air-quality?lat=40.7128&lon=-74.0060
```

#### Weather Alerts
```http
GET /weather/alerts?lat=40.7128&lon=-74.0060
```

### System Endpoints

#### Health Check
```http
GET /health
```

#### Available Sources
```http
GET /sources
```

## 🧪 Testing Examples

### Get Weather for New York
```bash
curl "http://localhost:8006/weather?lat=40.7128&lon=-74.0060&units=celsius"
```

### Get Current Weather Only
```bash
curl "http://localhost:8006/weather/current?lat=51.5074&lon=-0.1278"
```

### Get Air Quality for London
```bash
curl "http://localhost:8006/weather/air-quality?lat=51.5074&lon=-0.1278"
```

### Get 3-Day Forecast
```bash
curl "http://localhost:8006/weather/forecast?lat=35.6762&lon=139.6503&days=3"
```

### Use Specific Data Sources
```bash
curl "http://localhost:8006/weather?lat=48.8566&lon=2.3522&sources=openweather,weatherbit"
```

## 📊 Data Sources

### OpenWeatherMap
- **Features**: Current weather, 5-day forecast, air pollution
- **Rate Limit**: 1000 calls/day (free tier)
- **Coverage**: Global
- **Data Points**: Temperature, humidity, pressure, wind, clouds, precipitation

### WeatherBit
- **Features**: Current weather, 16-day forecast, hourly data, air quality
- **Rate Limit**: 500 calls/day (free tier)
- **Coverage**: Global
- **Data Points**: Detailed weather metrics, UV index, air quality

### Visual Crossing
- **Features**: Current weather, historical data, forecasts, weather alerts
- **Rate Limit**: 1000 calls/day (free tier)
- **Coverage**: Global
- **Data Points**: Comprehensive weather data with severe weather alerts

## 🔄 Data Aggregation Algorithm

### Normalization Process
1. **Fetch Data**: Concurrent API calls to all specified sources
2. **Standardize**: Convert all data to common format
3. **Quality Check**: Validate data completeness and accuracy
4. **Aggregate**: Merge data using weighted averaging
5. **Enhance**: Fill gaps with data from alternative sources

### Confidence Scoring
```python
# Source confidence weights
source_weights = {
    "openweather": 0.8,
    "weatherbit": 0.9,
    "visualcrossing": 0.85
}

# Data quality indicators
quality_factors = {
    "recency": 0.3,
    "completeness": 0.4,
    "accuracy": 0.3
}
```

### Fallback Strategy
1. **Primary Source**: Use highest confidence source
2. **Secondary Sources**: Fill gaps with alternative data
3. **Last Resort**: Use cached or interpolated data
4. **Error Handling**: Graceful degradation when sources fail

## 🌡️ Unit Conversions

### Temperature
- **Celsius**: Standard metric unit
- **Fahrenheit**: Imperial unit (US)
- **Kelvin**: Scientific unit

### Wind Speed
- **km/h**: Kilometers per hour
- **mph**: Miles per hour
- **m/s**: Meters per second

### Pressure
- **hPa**: Hectopascals (standard)
- **inHg**: Inches of mercury
- **mmHg**: Millimeters of mercury

### Air Quality
- **PM2.5**: Fine particulate matter (μg/m³)
- **PM10**: Coarse particulate matter (μg/m³)
- **AQI**: Air Quality Index (1-5 scale)

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Keys
OPENWEATHER_API_KEY=your-openweather-api-key
WEATHERBIT_API_KEY=your-weatherbit-api-key
VISUALCROSSING_API_KEY=your-visualcrossing-api-key

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Caching
CACHE_TTL=300  # 5 minutes
REDIS_URL=redis://localhost:6379

# Default Settings
DEFAULT_UNITS=celsius
DEFAULT_WIND_UNITS=km/h
DEFAULT_SOURCES=openweather,weatherbit

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/weather_api.log
```

### Advanced Configuration
```python
# Custom aggregation weights
aggregation_weights = {
    "temperature": {"openweather": 0.4, "weatherbit": 0.35, "visualcrossing": 0.25},
    "humidity": {"openweather": 0.3, "weatherbit": 0.4, "visualcrossing": 0.3},
    "wind_speed": {"openweather": 0.35, "weatherbit": 0.3, "visualcrossing": 0.35}
}

# Quality thresholds
quality_thresholds = {
    "min_data_sources": 1,
    "max_age_minutes": 60,
    "min_confidence": 0.6
}
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8006

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8006"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  weather-api:
    build: .
    ports:
      - "8006:8006"
    environment:
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - WEATHERBIT_API_KEY=${WEATHERBIT_API_KEY}
      - VISUALCROSSING_API_KEY=${VISUALCROSSING_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: weather-api
  template:
    metadata:
      labels:
        app: weather-api
    spec:
      containers:
      - name: weather-api
        image: weather-api:latest
        ports:
        - containerPort: 8006
        env:
        - name: OPENWEATHER_API_KEY
          valueFrom:
            secretKeyRef:
              name: weather-secrets
              key: openweather-key
```

## 📈 Performance Optimization

### Caching Strategy
```python
# Redis caching for frequent requests
cache_config = {
    "current_weather": 300,  # 5 minutes
    "hourly_forecast": 900,  # 15 minutes
    "daily_forecast": 3600,  # 1 hour
    "air_quality": 1800      # 30 minutes
}
```

### Rate Limiting
```python
# Per-client rate limiting
rate_limits = {
    "free_tier": {"requests": 100, "window": 3600},
    "premium": {"requests": 1000, "window": 3600},
    "enterprise": {"requests": 10000, "window": 3600}
}
```

### Connection Pooling
```python
# HTTP client configuration
client_config = {
    "timeout": 30.0,
    "limits": httpx.Limits(max_keepalive_connections=20),
    "retries": 3
}
```

## 🔍 Monitoring & Analytics

### Metrics Collection
```python
# Prometheus metrics
metrics = {
    "api_requests_total": Counter("weather_api_requests_total"),
    "api_response_time": Histogram("weather_api_response_time_seconds"),
    "source_errors": Counter("weather_source_errors_total"),
    "cache_hits": Counter("weather_cache_hits_total")
}
```

### Health Monitoring
```python
# Health check endpoints
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "sources": {
            "openweather": await check_openweather_health(),
            "weatherbit": await check_weatherbit_health(),
            "visualcrossing": await check_visualcrossing_health()
        },
        "cache": await check_cache_health(),
        "performance": get_performance_metrics()
    }
```

## 🛡️ Error Handling

### Source Failures
- **Graceful Degradation**: Continue with available sources
- **Circuit Breaker**: Temporarily disable failing sources
- **Retry Logic**: Exponential backoff for failed requests
- **Fallback Data**: Use cached data when sources are unavailable

### Data Validation
- **Schema Validation**: Ensure API responses match expected format
- **Range Checking**: Validate temperature, humidity, pressure ranges
- **Cross-Validation**: Compare data between sources for consistency

## 📱 Client Integration

### JavaScript Example
```javascript
async function getWeather(lat, lon) {
    const response = await fetch(
        `http://localhost:8006/weather?lat=${lat}&lon=${lon}`
    );
    const data = await response.json();
    return data;
}

// Usage
const weather = await getWeather(40.7128, -74.0060);
console.log(`Temperature: ${weather.current.temperature}°C`);
```

### Python Example
```python
import httpx

async def get_weather(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8006/weather",
            params={"lat": lat, "lon": lon}
        )
        return response.json()

# Usage
weather = await get_weather(51.5074, -0.1278)
print(f"Temperature: {weather['current']['temperature']}°C")
```

## 🔮 Future Enhancements

### Planned Features
- **Historical Data**: Access to past weather conditions
- **Weather Maps**: Radar and satellite imagery
- **Marine Weather**: Ocean conditions, tides, waves
- **Agricultural Data**: Soil moisture, growing conditions
- **Aviation Weather**: Flight conditions, visibility
- **Sports Weather**: Event-specific forecasts

### AI Integration
- **Forecast Accuracy**: Machine learning for improved predictions
- **Anomaly Detection**: Identify unusual weather patterns
- **Personalized Forecasts**: User preference learning
- **Alert Optimization**: Smart notification systems

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review weather service documentation:
  - [OpenWeatherMap Docs](https://openweathermap.org/api)
  - [WeatherBit Docs](https://www.weatherbit.io/api)
  - [Visual Crossing Docs](https://www.visualcrossing.com/weather-api)

---

**Built with ❤️ using FastAPI**
