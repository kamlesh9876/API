from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
import random
import math

app = FastAPI(title="Weather Forecasting API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    PARTLY_CLOUDY = "partly_cloudy"
    OVERCAST = "overcast"
    RAIN = "rain"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"
    LIGHT_SNOW = "light_snow"
    HEAVY_SNOW = "heavy_snow"
    THUNDERSTORM = "thunderstorm"
    FOG = "fog"
    MIST = "mist"
    HAIL = "hail"
    SLEET = "sleet"
    WINDY = "windy"

class AlertSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"

class ForecastType(str, Enum):
    CURRENT = "current"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"

# Data models
class Location(BaseModel):
    id: str
    name: str
    country: str
    state: Optional[str] = None
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    timezone: str
    created_at: datetime

class WeatherData(BaseModel):
    id: str
    location_id: str
    timestamp: datetime
    temperature: float  # Celsius
    feels_like: float  # Celsius
    humidity: int  # percentage
    pressure: float  # hPa
    visibility: float  # km
    uv_index: float
    wind_speed: float  # km/h
    wind_direction: int  # degrees
    wind_gust: Optional[float] = None  # km/h
    condition: WeatherCondition
    description: str
    cloud_cover: int  # percentage
    precipitation_probability: int  # percentage
    precipitation_amount: Optional[float] = None  # mm
    dew_point: float  # Celsius
    created_at: datetime

class Forecast(BaseModel):
    id: str
    location_id: str
    forecast_type: ForecastType
    timestamp: datetime
    valid_from: datetime
    valid_to: datetime
    temperature_min: float
    temperature_max: float
    feels_like_min: float
    feels_like_max: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    condition: WeatherCondition
    description: str
    precipitation_probability: int
    precipitation_amount: Optional[float] = None
    uv_index: Optional[float] = None
    created_at: datetime

class WeatherAlert(BaseModel):
    id: str
    location_id: str
    title: str
    description: str
    severity: AlertSeverity
    alert_type: str
    valid_from: datetime
    valid_to: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

class HistoricalWeather(BaseModel):
    id: str
    location_id: str
    date: datetime
    temperature_min: float
    temperature_max: float
    temperature_avg: float
    humidity_avg: int
    pressure_avg: float
    wind_speed_avg: float
    condition: WeatherCondition
    precipitation_total: float
    created_at: datetime

class WeatherStation(BaseModel):
    id: str
    name: str
    location_id: str
    station_type: str  # "automated", "manual", "satellite"
    latitude: float
    longitude: float
    elevation: float
    installation_date: datetime
    is_active: bool
    data_sources: List[str] = []
    created_at: datetime
    updated_at: datetime

class ClimateData(BaseModel):
    id: str
    location_id: str
    year: int
    month: Optional[int] = None
    temperature_avg: float
    temperature_min_avg: float
    temperature_max_avg: float
    precipitation_total: float
    humidity_avg: int
    pressure_avg: float
    wind_speed_avg: float
    days_with_precipitation: int
    days_with_sunshine: int
    created_at: datetime

# In-memory storage
locations: Dict[str, Location] = {}
weather_data: Dict[str, List[WeatherData]] = {}  # location_id -> list of weather data
forecasts: Dict[str, List[Forecast]] = {}  # location_id -> list of forecasts
weather_alerts: Dict[str, List[WeatherAlert]] = {}  # location_id -> list of alerts
historical_weather: Dict[str, List[HistoricalWeather]] = {}  # location_id -> list of historical data
weather_stations: Dict[str, WeatherStation] = {}
climate_data: Dict[str, List[ClimateData]] = {}  # location_id -> list of climate data
websocket_connections: Dict[str, WebSocket] = {}

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # location_id -> list of connections

    async def connect(self, websocket: WebSocket, location_id: str, client_id: str):
        await websocket.accept()
        if location_id not in self.active_connections:
            self.active_connections[location_id] = []
        self.active_connections[location_id].append(websocket)
        websocket_connections[client_id] = websocket

    def disconnect(self, location_id: str, websocket: WebSocket, client_id: str):
        if location_id in self.active_connections:
            if websocket in self.active_connections[location_id]:
                self.active_connections[location_id].remove(websocket)
        if client_id in websocket_connections:
            del websocket_connections[client_id]

    async def broadcast_to_location(self, location_id: str, message: dict):
        if location_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[location_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[location_id].remove(conn)

    async def send_to_client(self, client_id: str, message: dict):
        if client_id in websocket_connections:
            try:
                await websocket_connections[client_id].send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Utility functions
def generate_location_id() -> str:
    """Generate unique location ID"""
    return f"loc_{uuid.uuid4().hex[:8]}"

def generate_weather_data_id() -> str:
    """Generate unique weather data ID"""
    return f"weather_{uuid.uuid4().hex[:8]}"

def generate_forecast_id() -> str:
    """Generate unique forecast ID"""
    return f"forecast_{uuid.uuid4().hex[:8]}"

def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return f"alert_{uuid.uuid4().hex[:8]}"

def generate_station_id() -> str:
    """Generate unique station ID"""
    return f"station_{uuid.uuid4().hex[:8]}"

def calculate_dew_point(temperature: float, humidity: int) -> float:
    """Calculate dew point temperature"""
    a = 17.27
    b = 237.7
    alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 1)

def calculate_wind_chill(temperature: float, wind_speed: float) -> float:
    """Calculate wind chill temperature"""
    if temperature > 10 or wind_speed < 4.8:
        return temperature
    
    wind_chill = 13.12 + 0.6215 * temperature - 11.37 * (wind_speed ** 0.16) + 0.3965 * temperature * (wind_speed ** 0.16)
    return round(wind_chill, 1)

def calculate_heat_index(temperature: float, humidity: int) -> float:
    """Calculate heat index temperature"""
    if temperature < 27:
        return temperature
    
    t = temperature
    h = humidity
    
    if h < 40:
        h = 40
    elif h > 100:
        h = 100
    
    heat_index = -8.78469475556 + 1.61139411 * t + 2.33854883889 * h - 0.14611605 * t * h - 0.012308094 * t * t - 0.0164248277778 * h * h + 0.002211732 * t * t * h + 0.00072546 * t * h * h + 0.000003582 * t * t * h * h
    
    return round(heat_index, 1)

def get_wind_direction_text(degrees: int) -> str:
    """Convert wind direction degrees to compass direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / 22.5) % 16
    return directions[index]

def generate_mock_weather_data(location_id: str, timestamp: datetime) -> WeatherData:
    """Generate mock weather data for testing"""
    # Base temperature varies by time of day
    hour = timestamp.hour
    base_temp = 20 + 5 * math.sin((hour - 6) * math.pi / 12)  # Peak at 2 PM
    
    # Add random variation
    temperature = base_temp + random.uniform(-5, 5)
    humidity = random.randint(30, 90)
    pressure = random.uniform(990, 1030)
    wind_speed = random.uniform(0, 30)
    wind_direction = random.randint(0, 360)
    uv_index = max(0, 10 * math.sin((hour - 6) * math.pi / 12)) if 6 <= hour <= 18 else 0
    
    # Random weather condition
    conditions = [WeatherCondition.CLEAR, WeatherCondition.PARTLY_CLOUDY, WeatherCondition.CLOUDY, WeatherCondition.LIGHT_RAIN]
    condition = random.choice(conditions)
    
    descriptions = {
        WeatherCondition.CLEAR: "Clear sky",
        WeatherCondition.PARTLY_CLOUDY: "Partly cloudy",
        WeatherCondition.CLOUDY: "Cloudy",
        WeatherCondition.LIGHT_RAIN: "Light rain"
    }
    
    precipitation_prob = 0
    precipitation_amount = None
    
    if condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.RAIN]:
        precipitation_prob = random.randint(60, 100)
        precipitation_amount = random.uniform(0.1, 5.0)
    
    weather_id = generate_weather_data_id()
    
    return WeatherData(
        id=weather_id,
        location_id=location_id,
        timestamp=timestamp,
        temperature=round(temperature, 1),
        feels_like=round(temperature, 1),
        humidity=humidity,
        pressure=round(pressure, 1),
        visibility=random.uniform(5, 20),
        uv_index=round(uv_index, 1),
        wind_speed=round(wind_speed, 1),
        wind_direction=wind_direction,
        wind_gust=round(wind_speed * random.uniform(1.0, 1.5), 1) if wind_speed > 5 else None,
        condition=condition,
        description=descriptions[condition],
        cloud_cover=random.randint(0, 100),
        precipitation_probability=precipitation_prob,
        precipitation_amount=precipitation_amount,
        dew_point=round(calculate_dew_point(temperature, humidity), 1),
        created_at=datetime.now()
    )

def generate_mock_forecast(location_id: str, forecast_type: ForecastType, valid_from: datetime) -> Forecast:
    """Generate mock forecast data"""
    if forecast_type == ForecastType.HOURLY:
        valid_to = valid_from + timedelta(hours=1)
    elif forecast_type == ForecastType.DAILY:
        valid_to = valid_from + timedelta(days=1)
    elif forecast_type == ForecastType.WEEKLY:
        valid_to = valid_from + timedelta(weeks=1)
    else:  # CURRENT
        valid_to = valid_from + timedelta(hours=1)
    
    # Generate temperature range
    base_temp = 20 + random.uniform(-10, 15)
    temp_range = random.uniform(5, 15)
    
    conditions = [WeatherCondition.CLEAR, WeatherCondition.PARTLY_CLOUDY, WeatherCondition.CLOUDY, WeatherCondition.LIGHT_RAIN, WeatherCondition.RAIN]
    condition = random.choice(conditions)
    
    descriptions = {
        WeatherCondition.CLEAR: "Clear skies expected",
        WeatherCondition.PARTLY_CLOUDY: "Partly cloudy conditions",
        WeatherCondition.CLOUDY: "Overcast conditions",
        WeatherCondition.LIGHT_RAIN: "Light rain expected",
        WeatherCondition.RAIN: "Rain expected"
    }
    
    precipitation_prob = 0
    precipitation_amount = None
    
    if condition in [WeatherCondition.LIGHT_RAIN, WeatherCondition.RAIN]:
        precipitation_prob = random.randint(40, 90)
        precipitation_amount = random.uniform(0.5, 10.0)
    
    forecast_id = generate_forecast_id()
    
    return Forecast(
        id=forecast_id,
        location_id=location_id,
        forecast_type=forecast_type,
        timestamp=datetime.now(),
        valid_from=valid_from,
        valid_to=valid_to,
        temperature_min=round(base_temp - temp_range/2, 1),
        temperature_max=round(base_temp + temp_range/2, 1),
        feels_like_min=round(base_temp - temp_range/2, 1),
        feels_like_max=round(base_temp + temp_range/2, 1),
        humidity=random.randint(30, 90),
        pressure=round(random.uniform(990, 1030), 1),
        wind_speed=round(random.uniform(0, 25), 1),
        wind_direction=random.randint(0, 360),
        condition=condition,
        description=descriptions[condition],
        precipitation_probability=precipitation_prob,
        precipitation_amount=precipitation_amount,
        uv_index=round(random.uniform(0, 10), 1),
        created_at=datetime.now()
    )

# Background task for weather data updates
async def weather_data_updater():
    """Background task to update weather data and forecasts"""
    while True:
        current_time = datetime.now()
        
        for location_id in locations:
            # Generate current weather data
            weather = generate_mock_weather_data(location_id, current_time)
            
            if location_id not in weather_data:
                weather_data[location_id] = []
            
            weather_data[location_id].append(weather)
            
            # Keep only last 24 hours of data
            cutoff_time = current_time - timedelta(hours=24)
            weather_data[location_id] = [
                w for w in weather_data[location_id] if w.timestamp >= cutoff_time
            ]
            
            # Broadcast weather update
            await manager.broadcast_to_location(location_id, {
                "type": "weather_update",
                "weather": weather.dict(),
                "timestamp": current_time.isoformat()
            })
            
            # Generate forecasts
            if location_id not in forecasts:
                forecasts[location_id] = []
            
            # Generate hourly forecasts for next 24 hours
            for i in range(24):
                forecast_time = current_time + timedelta(hours=i)
                forecast = generate_mock_forecast(location_id, ForecastType.HOURLY, forecast_time)
                forecasts[location_id].append(forecast)
            
            # Generate daily forecasts for next 7 days
            for i in range(7):
                forecast_time = current_time + timedelta(days=i)
                forecast = generate_mock_forecast(location_id, ForecastType.DAILY, forecast_time)
                forecasts[location_id].append(forecast)
            
            # Keep only relevant forecasts
            future_cutoff = current_time + timedelta(days=7)
            forecasts[location_id] = [
                f for f in forecasts[location_id] if f.valid_to >= current_time and f.valid_from <= future_cutoff
            ]
        
        await asyncio.sleep(300)  # Update every 5 minutes

# Start background task
asyncio.create_task(weather_data_updater())

# Initialize sample data
def initialize_sample_data():
    """Initialize sample location and weather station data"""
    # Sample locations
    sample_locations = [
        {
            "name": "New York",
            "country": "United States",
            "state": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "elevation": 10.0,
            "timezone": "America/New_York"
        },
        {
            "name": "London",
            "country": "United Kingdom",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "elevation": 11.0,
            "timezone": "Europe/London"
        },
        {
            "name": "Tokyo",
            "country": "Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "elevation": 40.0,
            "timezone": "Asia/Tokyo"
        },
        {
            "name": "Sydney",
            "country": "Australia",
            "latitude": -33.8688,
            "longitude": 151.2093,
            "elevation": 3.0,
            "timezone": "Australia/Sydney"
        },
        {
            "name": "Mumbai",
            "country": "India",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "elevation": 14.0,
            "timezone": "Asia/Kolkata"
        }
    ]
    
    for loc_data in sample_locations:
        location_id = generate_location_id()
        
        location = Location(
            id=location_id,
            **loc_data,
            created_at=datetime.now()
        )
        
        locations[location_id] = location
        weather_data[location_id] = []
        forecasts[location_id] = []
        weather_alerts[location_id] = []
        historical_weather[location_id] = []
        climate_data[location_id] = []
        
        # Create weather station
        station_id = generate_station_id()
        station = WeatherStation(
            id=station_id,
            name=f"{loc_data['name']} Weather Station",
            location_id=location_id,
            station_type="automated",
            latitude=loc_data['latitude'],
            longitude=loc_data['longitude'],
            elevation=loc_data.get('elevation', 0),
            installation_date=datetime.now() - timedelta(days=365),
            is_active=True,
            data_sources=["temperature", "humidity", "pressure", "wind"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        weather_stations[station_id] = station

# Initialize sample data
initialize_sample_data()

# API Endpoints
@app.post("/api/locations", response_model=Location)
async def create_location(
    name: str,
    country: str,
    state: Optional[str] = None,
    latitude: float,
    longitude: float,
    elevation: Optional[float] = None,
    timezone: str = "UTC"
):
    """Create a new location"""
    location_id = generate_location_id()
    
    location = Location(
        id=location_id,
        name=name,
        country=country,
        state=state,
        latitude=latitude,
        longitude=longitude,
        elevation=elevation,
        timezone=timezone,
        created_at=datetime.now()
    )
    
    locations[location_id] = location
    weather_data[location_id] = []
    forecasts[location_id] = []
    weather_alerts[location_id] = []
    historical_weather[location_id] = []
    climate_data[location_id] = []
    
    return location

@app.get("/api/locations", response_model=List[Location])
async def get_locations(
    country: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 50
):
    """Get locations with optional filters"""
    filtered_locations = list(locations.values())
    
    if country:
        filtered_locations = [l for l in filtered_locations if l.country == country]
    
    if state:
        filtered_locations = [l for l in filtered_locations if l.state == state]
    
    return filtered_locations[:limit]

@app.get("/api/locations/{location_id}", response_model=Location)
async def get_location(location_id: str):
    """Get specific location"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    return locations[location_id]

@app.get("/api/locations/{location_id}/current", response_model=WeatherData)
async def get_current_weather(location_id: str):
    """Get current weather for a location"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    
    if location_id not in weather_data or not weather_data[location_id]:
        # Generate current weather if none exists
        current_weather = generate_mock_weather_data(location_id, datetime.now())
        weather_data[location_id] = [current_weather]
        return current_weather
    
    # Get most recent weather data
    current_weather = max(weather_data[location_id], key=lambda x: x.timestamp)
    return current_weather

@app.get("/api/locations/{location_id}/forecast", response_model=List[Forecast])
async def get_forecast(
    location_id: str,
    forecast_type: ForecastType = ForecastType.DAILY,
    days: int = 7
):
    """Get weather forecast for a location"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    
    if location_id not in forecasts:
        # Generate initial forecasts
        forecasts[location_id] = []
        current_time = datetime.now()
        
        for i in range(days):
            forecast_time = current_time + timedelta(days=i)
            forecast = generate_mock_forecast(location_id, forecast_type, forecast_time)
            forecasts[location_id].append(forecast)
    
    # Filter by forecast type and time range
    current_time = datetime.now()
    future_cutoff = current_time + timedelta(days=days)
    
    filtered_forecasts = [
        f for f in forecasts[location_id] 
        if f.forecast_type == forecast_type and f.valid_from >= current_time and f.valid_from <= future_cutoff
    ]
    
    return sorted(filtered_forecasts, key=lambda x: x.valid_from)

@app.get("/api/locations/{location_id}/historical", response_model=List[HistoricalWeather])
async def get_historical_weather(
    location_id: str,
    start_date: datetime,
    end_date: datetime
):
    """Get historical weather data for a location"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Generate mock historical data if none exists
    if location_id not in historical_weather:
        historical_weather[location_id] = []
        
        current_date = start_date.date()
        while current_date <= end_date.date():
            # Generate historical data for each day
            base_temp = 20 + 10 * math.sin((current_date.timetuple().tm_yday - 80) * math.pi / 182.5)  # Seasonal variation
            
            historical = HistoricalWeather(
                id=f"hist_{uuid.uuid4().hex[:8]}",
                location_id=location_id,
                date=datetime.combine(current_date, datetime.min.time()),
                temperature_min=round(base_temp - random.uniform(5, 10), 1),
                temperature_max=round(base_temp + random.uniform(5, 10), 1),
                temperature_avg=round(base_temp, 1),
                humidity_avg=random.randint(40, 80),
                pressure_avg=round(random.uniform(990, 1030), 1),
                wind_speed_avg=round(random.uniform(0, 20), 1),
                condition=random.choice(list(WeatherCondition)),
                precipitation_total=random.uniform(0, 10) if random.random() < 0.3 else 0,
                created_at=datetime.now()
            )
            
            historical_weather[location_id].append(historical)
            current_date += timedelta(days=1)
    
    # Filter by date range
    filtered_data = [
        h for h in historical_weather[location_id] 
        if start_date.date() <= h.date.date() <= end_date.date()
    ]
    
    return sorted(filtered_data, key=lambda x: x.date)

@app.post("/api/locations/{location_id}/alerts", response_model=WeatherAlert)
async def create_weather_alert(
    location_id: str,
    title: str,
    description: str,
    severity: AlertSeverity,
    alert_type: str,
    valid_hours: int = 24
):
    """Create a weather alert"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    
    alert_id = generate_alert_id()
    current_time = datetime.now()
    
    alert = WeatherAlert(
        id=alert_id,
        location_id=location_id,
        title=title,
        description=description,
        severity=severity,
        alert_type=alert_type,
        valid_from=current_time,
        valid_to=current_time + timedelta(hours=valid_hours),
        is_active=True,
        created_at=current_time,
        updated_at=current_time
    )
    
    if location_id not in weather_alerts:
        weather_alerts[location_id] = []
    
    weather_alerts[location_id].append(alert)
    
    # Broadcast alert
    await manager.broadcast_to_location(location_id, {
        "type": "weather_alert",
        "alert": alert.dict(),
        "timestamp": current_time.isoformat()
    })
    
    return alert

@app.get("/api/locations/{location_id}/alerts", response_model=List[WeatherAlert])
async def get_weather_alerts(
    location_id: str,
    active_only: bool = True,
    severity: Optional[AlertSeverity] = None
):
    """Get weather alerts for a location"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    
    filtered_alerts = weather_alerts.get(location_id, [])
    
    if active_only:
        current_time = datetime.now()
        filtered_alerts = [a for a in filtered_alerts if a.is_active and a.valid_from <= current_time <= a.valid_to]
    
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
    
    return sorted(filtered_alerts, key=lambda x: x.created_at, reverse=True)

@app.get("/api/weather-stations", response_model=List[WeatherStation])
async def get_weather_stations(
    location_id: Optional[str] = None,
    station_type: Optional[str] = None,
    active_only: bool = False
):
    """Get weather stations"""
    filtered_stations = list(weather_stations.values())
    
    if location_id:
        filtered_stations = [s for s in filtered_stations if s.location_id == location_id]
    
    if station_type:
        filtered_stations = [s for s in filtered_stations if s.station_type == station_type]
    
    if active_only:
        filtered_stations = [s for s in filtered_stations if s.is_active]
    
    return filtered_stations

@app.get("/api/locations/{location_id}/climate", response_model=List[ClimateData])
async def get_climate_data(
    location_id: str,
    year: int,
    month: Optional[int] = None
):
    """Get climate data for a location"""
    if location_id not in locations:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Generate mock climate data if none exists
    if location_id not in climate_data:
        climate_data[location_id] = []
        
        # Generate data for the requested year
        if month:
            # Generate monthly data
            base_temp = 20 + 10 * math.sin((month - 1) * math.pi / 6)  # Seasonal variation
            
            climate = ClimateData(
                id=f"climate_{uuid.uuid4().hex[:8]}",
                location_id=location_id,
                year=year,
                month=month,
                temperature_avg=round(base_temp, 1),
                temperature_min_avg=round(base_temp - 5, 1),
                temperature_max_avg=round(base_temp + 5, 1),
                precipitation_total=random.uniform(20, 100),
                humidity_avg=random.randint(50, 80),
                pressure_avg=round(random.uniform(1000, 1020), 1),
                wind_speed_avg=round(random.uniform(5, 15), 1),
                days_with_precipitation=random.randint(5, 15),
                days_with_sunshine=random.randint(10, 25),
                created_at=datetime.now()
            )
            
            climate_data[location_id].append(climate)
        else:
            # Generate yearly data by month
            for m in range(1, 13):
                base_temp = 20 + 10 * math.sin((m - 1) * math.pi / 6)
                
                climate = ClimateData(
                    id=f"climate_{uuid.uuid4().hex[:8]}",
                    location_id=location_id,
                    year=year,
                    month=m,
                    temperature_avg=round(base_temp, 1),
                    temperature_min_avg=round(base_temp - 5, 1),
                    temperature_max_avg=round(base_temp + 5, 1),
                    precipitation_total=random.uniform(20, 100),
                    humidity_avg=random.randint(50, 80),
                    pressure_avg=round(random.uniform(1000, 1020), 1),
                    wind_speed_avg=round(random.uniform(5, 15), 1),
                    days_with_precipitation=random.randint(5, 15),
                    days_with_sunshine=random.randint(10, 25),
                    created_at=datetime.now()
                )
                
                climate_data[location_id].append(climate)
    
    # Filter by year and month
    filtered_data = [
        c for c in climate_data[location_id] 
        if c.year == year and (month is None or c.month == month)
    ]
    
    return sorted(filtered_data, key=lambda x: (x.month or 1))

@app.get("/api/stats")
async def get_weather_stats():
    """Get weather platform statistics"""
    total_locations = len(locations)
    total_stations = len(weather_stations)
    total_weather_data = sum(len(data) for data in weather_data.values())
    total_forecasts = sum(len(forecasts) for forecasts in forecasts.values())
    total_alerts = sum(len(alerts) for alerts in weather_alerts.values())
    
    # Location distribution by country
    country_distribution = {}
    for location in locations.values():
        country = location.country
        country_distribution[country] = country_distribution.get(country, 0) + 1
    
    # Station type distribution
    station_type_distribution = {}
    for station in weather_stations.values():
        station_type = station.station_type
        station_type_distribution[station_type] = station_type_distribution.get(station_type, 0) + 1
    
    # Active alerts by severity
    alert_severity_distribution = {}
    current_time = datetime.now()
    for alerts in weather_alerts.values():
        for alert in alerts:
            if alert.is_active and alert.valid_from <= current_time <= alert.valid_to:
                severity = alert.severity.value
                alert_severity_distribution[severity] = alert_severity_distribution.get(severity, 0) + 1
    
    return {
        "total_locations": total_locations,
        "total_stations": total_stations,
        "total_weather_data": total_weather_data,
        "total_forecasts": total_forecasts,
        "total_alerts": total_alerts,
        "country_distribution": country_distribution,
        "station_type_distribution": station_type_distribution,
        "alert_severity_distribution": alert_severity_distribution,
        "supported_forecast_types": [t.value for t in ForecastType],
        "supported_weather_conditions": [c.value for c in WeatherCondition],
        "supported_alert_severities": [s.value for s in AlertSeverity]
    }

# WebSocket endpoint for real-time weather updates
@app.websocket("/ws/{location_id}")
async def websocket_endpoint(websocket: WebSocket, location_id: str):
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, location_id, client_id)
    
    try:
        # Send current weather on connection
        current_weather = await get_current_weather(location_id)
        await manager.send_to_client(client_id, {
            "type": "current_weather",
            "weather": current_weather.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages
            if message.get("type") == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
            
            elif message.get("type") == "subscribe_forecast":
                forecast_type = message.get("forecast_type", "daily")
                days = message.get("days", 7)
                
                forecasts = await get_forecast(location_id, ForecastType(forecast_type), days)
                await manager.send_to_client(client_id, {
                    "type": "forecast_update",
                    "forecasts": [f.dict() for f in forecasts],
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message.get("type") == "get_alerts":
                alerts = await get_weather_alerts(location_id)
                await manager.send_to_client(client_id, {
                    "type": "alerts_update",
                    "alerts": [a.dict() for a in alerts],
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(location_id, websocket, client_id)

@app.get("/")
async def root():
    return {"message": "Weather Forecasting API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
