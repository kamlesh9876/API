# Weather Forecasting API

A comprehensive weather forecasting platform with real-time data, forecasting, alerts, historical data, and climate analytics.

## Features

- **Real-time Weather**: Current weather conditions with live updates
- **Multi-day Forecasts**: Hourly, daily, and weekly weather predictions
- **Weather Alerts**: Customizable severe weather notifications
- **Historical Data**: Access to historical weather records
- **Climate Analytics**: Long-term climate trends and statistics
- **Weather Stations**: Network monitoring and station management
- **WebSocket Support**: Real-time weather updates and alerts
- **Global Coverage**: Support for multiple locations worldwide

## API Endpoints

### Location Management

#### Create Location
```http
POST /api/locations
Content-Type: application/json

{
  "name": "New York",
  "country": "United States",
  "state": "New York",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "elevation": 10.0,
  "timezone": "America/New_York"
}
```

#### Get Locations
```http
GET /api/locations?country=United%20States&state=New%20York&limit=50
```

#### Get Specific Location
```http
GET /api/locations/{location_id}
```

### Weather Data

#### Get Current Weather
```http
GET /api/locations/{location_id}/current
```

#### Get Weather Forecast
```http
GET /api/locations/{location_id}/forecast?forecast_type=daily&days=7
```

#### Get Historical Weather
```http
GET /api/locations/{location_id}/historical?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59
```

### Weather Alerts

#### Create Weather Alert
```http
POST /api/locations/{location_id}/alerts
Content-Type: application/json

{
  "title": "Severe Thunderstorm Warning",
  "description": "Severe thunderstorms expected with damaging winds and large hail",
  "severity": "severe",
  "alert_type": "thunderstorm",
  "valid_hours": 6
}
```

#### Get Weather Alerts
```http
GET /api/locations/{location_id}/alerts?active_only=true&severity=severe
```

### Weather Stations

#### Get Weather Stations
```http
GET /api/weather-stations?location_id=loc_123&station_type=automated&active_only=true
```

### Climate Data

#### Get Climate Data
```http
GET /api/locations/{location_id}/climate?year=2024&month=6
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Location
```json
{
  "id": "loc_123",
  "name": "New York",
  "country": "United States",
  "state": "New York",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "elevation": 10.0,
  "timezone": "America/New_York",
  "created_at": "2024-01-01T10:00:00"
}
```

### Weather Data
```json
{
  "id": "weather_123",
  "location_id": "loc_123",
  "timestamp": "2024-01-01T12:00:00",
  "temperature": 22.5,
  "feels_like": 24.1,
  "humidity": 65,
  "pressure": 1013.2,
  "visibility": 10.0,
  "uv_index": 6.5,
  "wind_speed": 15.2,
  "wind_direction": 180,
  "wind_gust": 25.5,
  "condition": "partly_cloudy",
  "description": "Partly cloudy skies",
  "cloud_cover": 45,
  "precipitation_probability": 20,
  "precipitation_amount": null,
  "dew_point": 15.8,
  "created_at": "2024-01-01T12:00:00"
}
```

### Forecast
```json
{
  "id": "forecast_123",
  "location_id": "loc_123",
  "forecast_type": "daily",
  "timestamp": "2024-01-01T12:00:00",
  "valid_from": "2024-01-02T00:00:00",
  "valid_to": "2024-01-03T00:00:00",
  "temperature_min": 18.5,
  "temperature_max": 28.2,
  "feels_like_min": 17.8,
  "feels_like_max": 29.1,
  "humidity": 60,
  "pressure": 1015.0,
  "wind_speed": 12.5,
  "wind_direction": 225,
  "condition": "clear",
  "description": "Clear skies expected",
  "precipitation_probability": 10,
  "precipitation_amount": null,
  "uv_index": 8.0,
  "created_at": "2024-01-01T12:00:00"
}
```

### Weather Alert
```json
{
  "id": "alert_123",
  "location_id": "loc_123",
  "title": "Heat Advisory",
  "description": "High temperatures expected, stay hydrated",
  "severity": "moderate",
  "alert_type": "heat",
  "valid_from": "2024-01-01T12:00:00",
  "valid_to": "2024-01-01T20:00:00",
  "is_active": true,
  "created_at": "2024-01-01T11:30:00",
  "updated_at": "2024-01-01T11:30:00"
}
```

### Weather Station
```json
{
  "id": "station_123",
  "name": "Central Park Weather Station",
  "location_id": "loc_123",
  "station_type": "automated",
  "latitude": 40.7829,
  "longitude": -73.9654,
  "elevation": 15.0,
  "installation_date": "2020-01-01T00:00:00",
  "is_active": true,
  "data_sources": ["temperature", "humidity", "pressure", "wind"],
  "created_at": "2020-01-01T00:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### Climate Data
```json
{
  "id": "climate_123",
  "location_id": "loc_123",
  "year": 2024,
  "month": 6,
  "temperature_avg": 24.5,
  "temperature_min_avg": 19.2,
  "temperature_max_avg": 29.8,
  "precipitation_total": 85.5,
  "humidity_avg": 68,
  "pressure_avg": 1012.5,
  "wind_speed_avg": 11.2,
  "days_with_precipitation": 8,
  "days_with_sunshine": 18,
  "created_at": "2024-07-01T00:00:00"
}
```

## Weather Conditions

### Clear Conditions
- **Clear**: Clear skies, minimal clouds
- **Partly Cloudy**: Some clouds, mostly clear
- **Cloudy**: Overcast with cloud coverage

### Precipitation
- **Light Rain**: Light precipitation, drizzle
- **Rain**: Moderate to heavy rainfall
- **Heavy Rain**: Intense rainfall, potential flooding
- **Light Snow**: Light snowfall, flurries
- **Snow**: Moderate snow accumulation
- **Heavy Snow**: Heavy snowfall, significant accumulation
- **Sleet**: Mixed precipitation, ice pellets
- **Hail**: Ice pellets, storm conditions

### Atmospheric Conditions
- **Thunderstorm**: Severe weather with lightning
- **Fog**: Low visibility conditions
- **Mist**: Light fog, reduced visibility
- **Windy**: High wind conditions

## Forecast Types

### Current
- **Duration**: Current conditions
- **Update Frequency**: Real-time
- **Use Cases**: Immediate weather needs

### Hourly
- **Duration**: Next 24 hours
- **Update Frequency**: Every hour
- **Use Cases**: Daily planning, activities

### Daily
- **Duration**: Next 7 days
- **Update Frequency**: Every 6 hours
- **Use Cases**: Week planning, travel

### Weekly
- **Duration**: Next 4 weeks
- **Update Frequency**: Daily
- **Use Cases**: Long-term planning

## Alert Severities

### Low
- **Description**: Minor weather impacts
- **Examples**: Light rain, wind advisory
- **Action**: Awareness recommended

### Moderate
- **Description**: Noticeable weather impacts
- **Examples**: Heat advisory, small craft advisory
- **Action**: Take precautions

### Severe
- **Description**: Significant weather impacts
- **Examples**: Severe thunderstorm, flood warning
- **Action**: Take protective action

### Extreme
- **Description**: Dangerous weather conditions
- **Examples**: Hurricane, tornado, blizzard
- **Action**: Immediate action required

## WebSocket Events

### Weather Updates
```javascript
{
  "type": "weather_update",
  "weather": {
    "id": "weather_123",
    "temperature": 22.5,
    "condition": "partly_cloudy",
    "timestamp": "2024-01-01T12:00:00"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Weather Alerts
```javascript
{
  "type": "weather_alert",
  "alert": {
    "id": "alert_123",
    "title": "Severe Thunderstorm Warning",
    "severity": "severe",
    "valid_from": "2024-01-01T12:00:00",
    "valid_to": "2024-01-01T18:00:00"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Forecast Updates
```javascript
{
  "type": "forecast_update",
  "forecasts": [
    {
      "id": "forecast_123",
      "forecast_type": "daily",
      "temperature_max": 28.2,
      "condition": "clear",
      "valid_from": "2024-01-02T00:00:00"
    }
  ],
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

# Create a location
location_data = {
    "name": "San Francisco",
    "country": "United States",
    "state": "California",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "elevation": 16.0,
    "timezone": "America/Los_Angeles"
}

response = requests.post("http://localhost:8000/api/locations", json=location_data)
location = response.json()
print(f"Created location: {location['id']}")

# Get current weather
response = requests.get(f"http://localhost:8000/api/locations/{location['id']}/current")
current_weather = response.json()

print(f"Current weather in {location['name']}:")
print(f"  Temperature: {current_weather['temperature']}°C")
print(f"  Condition: {current_weather['condition']}")
print(f"  Humidity: {current_weather['humidity']}%")
print(f"  Wind: {current_weather['wind_speed']} km/h from {current_weather['wind_direction']}°")

# Get 7-day forecast
response = requests.get(f"http://localhost:8000/api/locations/{location['id']}/forecast?forecast_type=daily&days=7")
forecast = response.json()

print(f"\n7-day forecast for {location['name']}:")
for day in forecast:
    date = day['valid_from'].split('T')[0]
    print(f"  {date}: {day['temperature_min']}°C to {day['temperature_max']}°C - {day['condition']}")

# Create weather alert
alert_data = {
    "title": "High Wind Advisory",
    "description": "Strong winds expected this afternoon",
    "severity": "moderate",
    "alert_type": "wind",
    "valid_hours": 12
}

response = requests.post(f"http://localhost:8000/api/locations/{location['id']}/alerts", json=alert_data)
alert = response.json()
print(f"\nCreated alert: {alert['title']} ({alert['severity']})")

# Get historical weather for last month
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

response = requests.get(f"http://localhost:8000/api/locations/{location['id']}/historical", params={
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat()
})

historical = response.json()
print(f"\nHistorical weather data for last {len(historical)} days")

# Get climate data
response = requests.get(f"http://localhost:8000/api/locations/{location['id']}/climate", params={
    "year": 2024
})

climate = response.json()
print(f"\nClimate data for 2024:")
for month_data in climate:
    month_name = datetime(2024, month_data['month'], 1).strftime('%B')
    print(f"  {month_name}: Avg {month_data['temperature_avg']}°C, {month_data['precipitation_total']}mm precipitation")

# WebSocket client for real-time updates
async def weather_client():
    uri = f"ws://localhost:8000/ws/{location['id']}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to weather updates for {location['name']}")
        
        # Request forecast updates
        await websocket.send(json.dumps({
            "type": "subscribe_forecast",
            "forecast_type": "daily",
            "days": 3
        }))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'current_weather':
                weather = data['weather']
                print(f"Current weather update: {weather['temperature']}°C, {weather['condition']}")
            elif data['type'] == 'weather_update':
                weather = data['weather']
                print(f"Live update: {weather['temperature']}°C, {weather['condition']}")
            elif data['type'] == 'weather_alert':
                alert = data['alert']
                print(f"WEATHER ALERT: {alert['title']} - {alert['severity']}")
            elif data['type'] == 'forecast_update':
                forecasts = data['forecasts']
                print(f"Forecast update: {len(forecasts)} days available")

# Run WebSocket client
asyncio.run(weather_client())
```

### JavaScript Client
```javascript
// Weather API client
class WeatherClient {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }

  async createLocation(locationData) {
    const response = await fetch(`${this.baseURL}/api/locations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locationData)
    });
    return response.json();
  }

  async getCurrentWeather(locationId) {
    const response = await fetch(`${this.baseURL}/api/locations/${locationId}/current`);
    return response.json();
  }

  async getForecast(locationId, forecastType = 'daily', days = 7) {
    const response = await fetch(`${this.baseURL}/api/locations/${locationId}/forecast?forecast_type=${forecastType}&days=${days}`);
    return response.json();
  }

  async getHistoricalWeather(locationId, startDate, endDate) {
    const response = await fetch(`${this.baseURL}/api/locations/${locationId}/historical?start_date=${startDate}&end_date=${endDate}`);
    return response.json();
  }

  async createWeatherAlert(locationId, alertData) {
    const response = await fetch(`${this.baseURL}/api/locations/${locationId}/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(alertData)
    });
    return response.json();
  }

  async getWeatherAlerts(locationId, activeOnly = true) {
    const response = await fetch(`${this.baseURL}/api/locations/${locationId}/alerts?active_only=${activeOnly}`);
    return response.json();
  }
}

// WebSocket weather updates
class WeatherUpdates {
  constructor(locationId) {
    this.locationId = locationId;
    this.ws = new WebSocket(`ws://localhost:8000/ws/${locationId}`);
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('Connected to weather updates');
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from weather updates');
      clearInterval(this.pingInterval);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'current_weather':
        this.updateCurrentWeather(message.weather);
        break;
      case 'weather_update':
        this.updateWeatherDisplay(message.weather);
        break;
      case 'weather_alert':
        this.showWeatherAlert(message.alert);
        break;
      case 'forecast_update':
        this.updateForecastDisplay(message.forecasts);
        break;
      case 'alerts_update':
        this.updateAlertsDisplay(message.alerts);
        break;
      case 'pong':
        console.log('Connection healthy');
        break;
    }
  }

  startPingInterval() {
    this.pingInterval = setInterval(() => {
      this.ws.send(JSON.stringify({ type: 'ping' }));
    }, 30000);
  }

  subscribeToForecast(forecastType = 'daily', days = 7) {
    this.ws.send(JSON.stringify({
      type: 'subscribe_forecast',
      forecast_type: forecastType,
      days: days
    }));
  }

  getAlerts() {
    this.ws.send(JSON.stringify({ type: 'get_alerts' }));
  }

  // UI update methods
  updateCurrentWeather(weather) {
    document.getElementById('temperature').textContent = `${weather.temperature}°C`;
    document.getElementById('condition').textContent = weather.condition;
    document.getElementById('humidity').textContent = `${weather.humidity}%`;
    document.getElementById('wind').textContent = `${weather.wind_speed} km/h`;
    document.getElementById('last-updated').textContent = new Date(weather.timestamp).toLocaleTimeString();
  }

  updateWeatherDisplay(weather) {
    // Update live weather display
    const tempElement = document.getElementById('live-temperature');
    if (tempElement) {
      tempElement.textContent = `${weather.temperature}°C`;
      tempElement.style.color = weather.temperature > 25 ? 'red' : 'blue';
    }
  }

  showWeatherAlert(alert) {
    const alertContainer = document.getElementById('weather-alerts');
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alert.severity}`;
    alertElement.innerHTML = `
      <h4>${alert.title}</h4>
      <p>${alert.description}</p>
      <small>Valid until ${new Date(alert.valid_to).toLocaleString()}</small>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after alert expires
    setTimeout(() => {
      alertElement.remove();
    }, new Date(alert.valid_to) - new Date());
  }

  updateForecastDisplay(forecasts) {
    const forecastContainer = document.getElementById('forecast');
    forecastContainer.innerHTML = '';
    
    forecasts.forEach(forecast => {
      const date = new Date(forecast.valid_from).toLocaleDateString();
      const forecastElement = document.createElement('div');
      forecastElement.className = 'forecast-day';
      forecastElement.innerHTML = `
        <h4>${date}</h4>
        <div class="temperature">${forecast.temperature_min}°C - ${forecast.temperature_max}°C</div>
        <div class="condition">${forecast.condition}</div>
        <div class="precipitation">${forecast.precipitation_probability}% chance of rain</div>
      `;
      
      forecastContainer.appendChild(forecastElement);
    });
  }

  updateAlertsDisplay(alerts) {
    const alertsContainer = document.getElementById('active-alerts');
    alertsContainer.innerHTML = '';
    
    alerts.forEach(alert => {
      const alertElement = document.createElement('div');
      alertElement.className = `alert-item ${alert.severity}`;
      alertElement.innerHTML = `
        <h5>${alert.title}</h5>
        <p>${alert.description}</p>
        <span class="severity">${alert.severity.toUpperCase()}</span>
      `;
      
      alertsContainer.appendChild(alertElement);
    });
  }
}

// Usage example
const weatherClient = new WeatherClient();

// Add location
document.getElementById('add-location-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const locationData = {
    name: document.getElementById('location-name').value,
    country: document.getElementById('location-country').value,
    state: document.getElementById('location-state').value,
    latitude: parseFloat(document.getElementById('location-lat').value),
    longitude: parseFloat(document.getElementById('location-lon').value),
    elevation: parseFloat(document.getElementById('location-elev').value) || null,
    timezone: document.getElementById('location-timezone').value
  };

  try {
    const location = await weatherClient.createLocation(locationData);
    console.log('Location created:', location);
    
    // Load weather data
    await loadWeatherData(location.id);
    
    // Connect to real-time updates
    const weatherUpdates = new WeatherUpdates(location.id);
    
    // Subscribe to forecast updates
    weatherUpdates.subscribeToForecast('daily', 5);
    
    // Get current alerts
    weatherUpdates.getAlerts();
    
  } catch (error) {
    console.error('Error creating location:', error);
    alert('Error creating location');
  }
});

// Load weather data for a location
async function loadWeatherData(locationId) {
  try {
    // Get current weather
    const currentWeather = await weatherClient.getCurrentWeather(locationId);
    console.log('Current weather:', currentWeather);
    
    // Get forecast
    const forecast = await weatherClient.getForecast(locationId, 'daily', 7);
    console.log('7-day forecast:', forecast);
    
    // Get historical data
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000); // 30 days ago
    
    const historical = await weatherClient.getHistoricalWeather(
      locationId,
      startDate.toISOString(),
      endDate.toISOString()
    );
    console.log('Historical weather:', historical);
    
  } catch (error) {
    console.error('Error loading weather data:', error);
  }
}

// Create weather alert
document.getElementById('create-alert-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const locationId = document.getElementById('alert-location-id').value;
  const alertData = {
    title: document.getElementById('alert-title').value,
    description: document.getElementById('alert-description').value,
    severity: document.getElementById('alert-severity').value,
    alert_type: document.getElementById('alert-type').value,
    valid_hours: parseInt(document.getElementById('alert-duration').value) || 24
  };

  try {
    const alert = await weatherClient.createWeatherAlert(locationId, alertData);
    console.log('Alert created:', alert);
    alert('Weather alert created successfully!');
    
    // Reset form
    document.getElementById('create-alert-form').reset();
    
  } catch (error) {
    console.error('Error creating alert:', error);
    alert('Error creating weather alert');
  }
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

# Weather Data Sources
PRIMARY_WEATHER_API=openweathermap
SECONDARY_WEATHER_API=weatherapi
WEATHER_API_KEY=your_weather_api_key
WEATHER_UPDATE_INTERVAL=300  # seconds

# Data Sources
ENABLE_SATELLITE_DATA=true
ENABLE_RADAR_DATA=true
ENABLE_FORECAST_MODELS=true
DATA_RETENTION_HOURS=720  # 30 days

# Alert System
ENABLE_ALERTS=true
ALERT_CHECK_INTERVAL=300  # seconds
SEVERE_WEATHER_THRESHOLDS=wind:50,precipitation:25,temperature:40
ALERT_NOTIFICATION_CHANNELS=email,sms,push

# Forecast Models
ENABLE_ML_FORECASTS=false
FORECAST_ACCURACY_THRESHOLD=0.8
ENSEMBLE_FORECAST_COUNT=10
FORECAST_HORIZON_DAYS=14

# Historical Data
HISTORICAL_DATA_RETENTION_YEARS=10
CLIMATE_DATA_RETENTION_YEARS=50
DATA_AGGREGATION_INTERVAL=3600  # seconds

# Station Network
MAX_STATIONS_PER_LOCATION=10
STATION_DATA_VALIDATION=true
STATION_OFFLINE_THRESHOLD=300  # seconds
ENABLE_STATION_HEALTH_MONITORING=true

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=10000
WEBSOCKET_PING_TIMEOUT=10

# Database (for persistence)
DATABASE_URL=sqlite:///./weather_forecasting.db
ENABLE_DATA_BACKUP=true
BACKUP_INTERVAL_HOURS=24
DATA_COMPRESSION=true

# External Services
NOTIFICATION_SERVICE_URL=https://api.example.com/notifications
MAP_SERVICE_URL=https://api.mapbox.com
SATELLITE_DATA_PROVIDER=your_satellite_provider

# Logging
LOG_LEVEL=info
ENABLE_WEATHER_LOGGING=true
ALERT_LOG_RETENTION_DAYS=90
DATA_QUALITY_LOG_RETENTION_DAYS=30
LOG_FILE_PATH=./logs/weather.log
```

## Use Cases

- **Weather Applications**: Mobile and web weather apps
- **Agriculture**: Crop planning and irrigation management
- **Transportation**: Route planning and weather-related delays
- **Energy**: Power grid management and renewable energy forecasting
- **Insurance**: Risk assessment and claims processing
- **Events**: Outdoor event planning and safety
- **Aviation**: Flight planning and weather monitoring
- **Maritime**: Shipping and marine operations

## Advanced Features

### Machine Learning Forecasts
```python
# ML-based weather prediction
def generate_ml_forecast(location_id, forecast_hours=48):
    """Generate ML-enhanced weather forecasts"""
    # Get historical data for training
    historical_data = get_historical_weather(location_id, days=365)
    
    # Extract features (temperature, humidity, pressure trends)
    features = extract_weather_features(historical_data)
    
    # Train or load ML model
    model = load_weather_prediction_model()
    
    # Generate predictions
    predictions = model.predict(features, forecast_hours)
    
    return format_forecast_predictions(predictions)

def extract_weather_features(historical_data):
    """Extract features for ML model"""
    features = []
    
    for i in range(len(historical_data) - 24):
        window = historical_data[i:i+24]
        
        feature_vector = {
            'temp_trend': calculate_trend([w.temperature for w in window]),
            'humidity_avg': sum(w.humidity for w in window) / 24,
            'pressure_trend': calculate_trend([w.pressure for w in window]),
            'wind_pattern': analyze_wind_pattern([w.wind_speed for w in window]),
            'seasonal_factor': get_seasonal_factor(window[0].timestamp)
        }
        
        features.append(feature_vector)
    
    return features
```

### Weather Pattern Analysis
```python
# Analyze weather patterns and anomalies
def analyze_weather_patterns(location_id, analysis_period_months=12):
    """Analyze weather patterns for a location"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=analysis_period_months * 30)
    
    historical_data = get_historical_weather(location_id, start_date, end_date)
    
    analysis = {
        'temperature_patterns': analyze_temperature_patterns(historical_data),
        'precipitation_patterns': analyze_precipitation_patterns(historical_data),
        'seasonal_variations': analyze_seasonal_variations(historical_data),
        'extreme_events': identify_extreme_weather_events(historical_data),
        'climate_trends': analyze_climate_trends(historical_data)
    }
    
    return analysis

def identify_extreme_weather_events(historical_data):
    """Identify extreme weather events"""
    extreme_events = []
    
    for day in historical_data:
        if day.temperature_max > 35:  # Extreme heat
            extreme_events.append({
                'type': 'extreme_heat',
                'date': day.date,
                'value': day.temperature_max,
                'severity': 'high'
            })
        
        if day.precipitation_total > 50:  # Heavy rain
            extreme_events.append({
                'type': 'heavy_rain',
                'date': day.date,
                'value': day.precipitation_total,
                'severity': 'moderate'
            })
    
    return extreme_events
```

### Climate Change Analysis
```python
# Long-term climate trend analysis
def analyze_climate_trends(location_id, years=30):
    """Analyze long-term climate trends"""
    climate_data = get_climate_data(location_id, years)
    
    trends = {
        'temperature_trend': calculate_temperature_trend(climate_data),
        'precipitation_trend': calculate_precipitation_trend(climate_data),
        'extreme_weather_frequency': analyze_extreme_weather_frequency(climate_data),
        'seasonal_shifts': analyze_seasonal_shifts(climate_data)
    }
    
    return trends

def calculate_temperature_trend(climate_data):
    """Calculate temperature trend over time"""
    years = [data.year for data in climate_data]
    temperatures = [data.temperature_avg for data in climate_data]
    
    # Linear regression to find trend
    trend_coefficient = linear_regression(years, temperatures)
    
    return {
        'trend_per_decade': trend_coefficient * 10,
        'confidence_interval': calculate_confidence_interval(years, temperatures),
        'statistical_significance': test_significance(trend_coefficient)
    }
```

## Production Considerations

- **Data Quality**: Validation and cleaning of weather data
- **Redundancy**: Multiple data sources for reliability
- **Scalability**: Handle high-volume weather data requests
- **Real-time Processing**: Low-latency weather updates
- **Data Privacy**: Location data protection and anonymization
- **Compliance**: Weather data licensing and regulations
- **Monitoring**: System health and data quality monitoring
- **Backup**: Regular backups of historical weather data
