from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import httpx
import asyncio
from collections import defaultdict
import math

app = FastAPI(title="Weather API Wrapper", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration (in production, use environment variables)
API_KEYS = {
    "openweather": "your-openweather-api-key",
    "weatherbit": "your-weatherbit-api-key",
    "visualcrossing": "your-visualcrossing-api-key"
}

BASE_URLS = {
    "openweather": "https://api.openweathermap.org/data/2.5",
    "weatherbit": "https://api.weatherbit.io/v2.0",
    "visualcrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
}

# Enums
class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    MIST = "mist"
    FOG = "fog"

class WindSpeedUnit(str, Enum):
    MPS = "m/s"
    KMH = "km/h"
    MPH = "mph"

class TemperatureUnit(str, Enum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    KELVIN = "kelvin"

# Pydantic models
class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")

class Location(BaseModel):
    name: str
    country: str
    state: Optional[str] = None
    coordinates: Coordinates

class CurrentWeather(BaseModel):
    temperature: float
    feels_like: float
    humidity: int  # 0-100
    pressure: float  # hPa
    visibility: float  # km
    uv_index: Optional[float] = None
    aqi: Optional[int] = None  # Air Quality Index
    wind_speed: float
    wind_direction: int  # degrees
    wind_gust: Optional[float] = None
    condition: WeatherCondition
    description: str
    icon: Optional[str] = None
    timestamp: datetime

class HourlyForecast(BaseModel):
    time: datetime
    temperature: float
    feels_like: float
    humidity: int
    precipitation_probability: int  # 0-100
    precipitation_amount: float  # mm
    wind_speed: float
    wind_direction: int
    condition: WeatherCondition
    description: str

class DailyForecast(BaseModel):
    date: datetime
    temperature_min: float
    temperature_max: float
    feels_like_morning: float
    feels_like_day: float
    feels_like_evening: float
    feels_like_night: float
    humidity: int
    precipitation_probability: int
    precipitation_amount: float
    wind_speed: float
    wind_direction: int
    condition: WeatherCondition
    description: str
    sunrise: datetime
    sunset: datetime
    uv_index: Optional[float] = None

class AirQuality(BaseModel):
    aqi: int  # 1-5 scale
    pm25: float  # μg/m³
    pm10: float  # μg/m³
    o3: float  # μg/m³
    no2: float  # μg/m³
    so2: float  # μg/m³
    co: float  # μg/m³
    category: str  # Good, Moderate, Unhealthy, etc.

class WeatherResponse(BaseModel):
    location: Location
    current: CurrentWeather
    hourly: List[HourlyForecast]
    daily: List[DailyForecast]
    air_quality: Optional[AirQuality] = None
    alerts: List[Dict[str, Any]] = []
    data_sources: List[str]
    last_updated: datetime

class WeatherAlert(BaseModel):
    title: str
    description: str
    severity: str  # Minor, Moderate, Severe, Extreme
    start_time: datetime
    end_time: datetime
    areas: List[str]

# Weather data aggregation and normalization
class WeatherDataAggregator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    def map_weather_condition(self, condition: str, source: str) -> WeatherCondition:
        """Map weather conditions from different APIs to standard enum"""
        condition_lower = condition.lower()
        
        # OpenWeatherMap conditions
        if source == "openweather":
            if "clear" in condition_lower:
                return WeatherCondition.CLEAR
            elif "cloud" in condition_lower:
                return WeatherCondition.CLOUDS
            elif "rain" in condition_lower or "drizzle" in condition_lower:
                return WeatherCondition.RAIN if "rain" in condition_lower else WeatherCondition.DRIZZLE
            elif "snow" in condition_lower:
                return WeatherCondition.SNOW
            elif "thunderstorm" in condition_lower:
                return WeatherCondition.THUNDERSTORM
            elif "mist" in condition_lower or "fog" in condition_lower:
                return WeatherCondition.FOG if "fog" in condition_lower else WeatherCondition.MIST
        
        # WeatherBit conditions
        elif source == "weatherbit":
            if "clear" in condition_lower:
                return WeatherCondition.CLEAR
            elif "cloud" in condition_lower:
                return WeatherCondition.CLOUDS
            elif "rain" in condition_lower:
                return WeatherCondition.RAIN
            elif "snow" in condition_lower:
                return WeatherCondition.SNOW
            elif "thunder" in condition_lower:
                return WeatherCondition.THUNDERSTORM
            elif "drizzle" in condition_lower:
                return WeatherCondition.DRIZZLE
            elif "fog" in condition_lower:
                return WeatherCondition.FOG
            elif "mist" in condition_lower:
                return WeatherCondition.MIST
        
        # Visual Crossing conditions
        elif source == "visualcrossing":
            if "clear" in condition_lower:
                return WeatherCondition.CLEAR
            elif "cloud" in condition_lower or "overcast" in condition_lower:
                return WeatherCondition.CLOUDS
            elif "rain" in condition_lower:
                return WeatherCondition.RAIN
            elif "snow" in condition_lower:
                return WeatherCondition.SNOW
            elif "thunder" in condition_lower:
                return WeatherCondition.THUNDERSTORM
            elif "drizzle" in condition_lower:
                return WeatherCondition.DRIZZLE
            elif "fog" in condition_lower:
                return WeatherCondition.FOG
            elif "mist" in condition_lower:
                return WeatherCondition.MIST
        
        # Default fallback
        return WeatherCondition.CLEAR
    
    def convert_temperature(self, temp: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between units"""
        if from_unit == to_unit:
            return temp
        
        # Convert to Celsius first
        if from_unit == "kelvin":
            celsius = temp - 273.15
        elif from_unit == "fahrenheit":
            celsius = (temp - 32) * 5/9
        else:  # already celsius
            celsius = temp
        
        # Convert from Celsius to target unit
        if to_unit == "kelvin":
            return celsius + 273.15
        elif to_unit == "fahrenheit":
            return celsius * 9/5 + 32
        else:  # celsius
            return celsius
    
    def convert_wind_speed(self, speed: float, from_unit: str, to_unit: str) -> float:
        """Convert wind speed between units"""
        # Convert to m/s first
        if from_unit == "km/h":
            mps = speed / 3.6
        elif from_unit == "mph":
            mps = speed * 0.44704
        else:  # already m/s
            mps = speed
        
        # Convert from m/s to target unit
        if to_unit == "km/h":
            return mps * 3.6
        elif to_unit == "mph":
            return mps * 2.237
        else:  # m/s
            return mps
    
    async def fetch_openweather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch data from OpenWeatherMap API"""
        try:
            # Current weather
            current_url = f"{BASE_URLS['openweather']}/weather"
            current_params = {
                "lat": lat,
                "lon": lon,
                "appid": API_KEYS["openweather"],
                "units": "metric"
            }
            
            # Forecast
            forecast_url = f"{BASE_URLS['openweather']}/forecast"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "appid": API_KEYS["openweather"],
                "units": "metric"
            }
            
            # Air pollution
            pollution_url = f"{BASE_URLS['openweather']}/air_pollution"
            pollution_params = {
                "lat": lat,
                "lon": lon,
                "appid": API_KEYS["openweather"]
            }
            
            # Execute requests concurrently
            current_resp, forecast_resp, pollution_resp = await asyncio.gather(
                self.client.get(current_url, params=current_params),
                self.client.get(forecast_url, params=forecast_params),
                self.client.get(pollution_url, params=pollution_params),
                return_exceptions=True
            )
            
            data = {"source": "openweather"}
            
            # Process current weather
            if isinstance(current_resp, httpx.Response) and current_resp.status_code == 200:
                data["current"] = current_resp.json()
            
            # Process forecast
            if isinstance(forecast_resp, httpx.Response) and forecast_resp.status_code == 200:
                data["forecast"] = forecast_resp.json()
            
            # Process air quality
            if isinstance(pollution_resp, httpx.Response) and pollution_resp.status_code == 200:
                data["air_quality"] = pollution_resp.json()
            
            return data
            
        except Exception as e:
            return {"source": "openweather", "error": str(e)}
    
    async def fetch_weatherbit_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch data from WeatherBit API"""
        try:
            # Current weather
            current_url = f"{BASE_URLS['weatherbit']}/current"
            current_params = {
                "lat": lat,
                "lon": lon,
                "key": API_KEYS["weatherbit"],
                "units": "M"  # Metric
            }
            
            # Forecast
            forecast_url = f"{BASE_URLS['weatherbit']}/forecast/daily"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "key": API_KEYS["weatherbit"],
                "units": "M",
                "days": 16
            }
            
            # Hourly forecast
            hourly_url = f"{BASE_URLS['weatherbit']}/forecast/hourly"
            hourly_params = {
                "lat": lat,
                "lon": lon,
                "key": API_KEYS["weatherbit"],
                "units": "M",
                "hours": 48
            }
            
            # Air quality
            aqi_url = f"{BASE_URLS['weatherbit']}/airquality"
            aqi_params = {
                "lat": lat,
                "lon": lon,
                "key": API_KEYS["weatherbit"]
            }
            
            # Execute requests concurrently
            current_resp, forecast_resp, hourly_resp, aqi_resp = await asyncio.gather(
                self.client.get(current_url, params=current_params),
                self.client.get(forecast_url, params=forecast_params),
                self.client.get(hourly_url, params=hourly_params),
                self.client.get(aqi_url, params=aqi_params),
                return_exceptions=True
            )
            
            data = {"source": "weatherbit"}
            
            # Process responses
            if isinstance(current_resp, httpx.Response) and current_resp.status_code == 200:
                data["current"] = current_resp.json()
            
            if isinstance(forecast_resp, httpx.Response) and forecast_resp.status_code == 200:
                data["forecast"] = forecast_resp.json()
            
            if isinstance(hourly_resp, httpx.Response) and hourly_resp.status_code == 200:
                data["hourly"] = hourly_resp.json()
            
            if isinstance(aqi_resp, httpx.Response) and aqi_resp.status_code == 200:
                data["air_quality"] = aqi_resp.json()
            
            return data
            
        except Exception as e:
            return {"source": "weatherbit", "error": str(e)}
    
    async def fetch_visualcrossing_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch data from Visual Crossing API"""
        try:
            # Get comprehensive weather data
            url = f"{BASE_URLS['visualcrossing']}/timeline/{lat},{lon}"
            params = {
                "key": API_KEYS["visualcrossing"],
                "unitGroup": "metric",
                "include": "current,hours,days,alerts",
                "contentType": "json"
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                return {"source": "visualcrossing", "data": response.json()}
            else:
                return {"source": "visualcrossing", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"source": "visualcrossing", "error": str(e)}
    
    def normalize_openweather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize OpenWeatherMap data to standard format"""
        if "error" in data or "current" not in data:
            return {}
        
        current = data["current"]
        normalized = {
            "location": {
                "name": current["name"],
                "country": current["sys"]["country"],
                "coordinates": {
                    "lat": current["coord"]["lat"],
                    "lon": current["coord"]["lon"]
                }
            },
            "current": {
                "temperature": current["main"]["temp"],
                "feels_like": current["main"]["feels_like"],
                "humidity": current["main"]["humidity"],
                "pressure": current["main"]["pressure"],
                "visibility": current.get("visibility", 0) / 1000,  # Convert m to km
                "wind_speed": current["wind"]["speed"],
                "wind_direction": current["wind"].get("deg", 0),
                "wind_gust": current["wind"].get("gust"),
                "condition": self.map_weather_condition(current["weather"][0]["main"], "openweather"),
                "description": current["weather"][0]["description"],
                "icon": current["weather"][0]["icon"],
                "timestamp": datetime.fromtimestamp(current["dt"])
            }
        }
        
        # Process forecast
        if "forecast" in data:
            hourly_forecasts = []
            daily_forecasts = []
            
            for item in data["forecast"]["list"][:48]:  # Next 48 hours
                hourly_forecasts.append({
                    "time": datetime.fromtimestamp(item["dt"]),
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "precipitation_probability": int(item.get("pop", 0) * 100),
                    "precipitation_amount": item.get("rain", {}).get("3h", 0),
                    "wind_speed": item["wind"]["speed"],
                    "wind_direction": item["wind"].get("deg", 0),
                    "condition": self.map_weather_condition(item["weather"][0]["main"], "openweather"),
                    "description": item["weather"][0]["description"]
                })
            
            normalized["hourly"] = hourly_forecasts
            normalized["daily"] = daily_forecasts
        
        # Process air quality
        if "air_quality" in data and data["air_quality"].get("list"):
            aqi_data = data["air_quality"]["list"][0]
            components = aqi_data.get("components", {})
            
            # Convert AQI from 0-500 to 1-5 scale
            aqi_value = aqi_data.get("main", {}).get("aqi", 1)
            aqi_category = min(5, max(1, math.ceil(aqi_value / 100)))
            
            normalized["air_quality"] = {
                "aqi": aqi_category,
                "pm25": components.get("pm2_5", 0),
                "pm10": components.get("pm10", 0),
                "o3": components.get("o3", 0),
                "no2": components.get("no2", 0),
                "so2": components.get("so2", 0),
                "co": components.get("co", 0),
                "category": self.get_aqi_category(aqi_category)
            }
        
        return normalized
    
    def normalize_weatherbit_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize WeatherBit data to standard format"""
        if "error" in data or "current" not in data:
            return {}
        
        current = data["current"]["data"][0]
        normalized = {
            "location": {
                "name": current["city_name"],
                "country": current["country_code"],
                "coordinates": {
                    "lat": current["lat"],
                    "lon": current["lon"]
                }
            },
            "current": {
                "temperature": current["temp"],
                "feels_like": current["app_temp"],
                "humidity": current["rh"],
                "pressure": current["pres"],
                "visibility": current.get("vis", 0),
                "wind_speed": current["wind_spd"],
                "wind_direction": current["wind_dir"],
                "condition": self.map_weather_condition(current["weather"]["description"], "weatherbit"),
                "description": current["weather"]["description"],
                "timestamp": datetime.fromtimestamp(current["ts"])
            }
        }
        
        # Process hourly forecast
        if "hourly" in data:
            hourly_forecasts = []
            for item in data["hourly"]["data"][:48]:
                hourly_forecasts.append({
                    "time": datetime.fromtimestamp(item["ts"]),
                    "temperature": item["temp"],
                    "feels_like": item["app_temp"],
                    "humidity": item["rh"],
                    "precipitation_probability": item["pop"],
                    "precipitation_amount": item.get("precip", 0),
                    "wind_speed": item["wind_spd"],
                    "wind_direction": item["wind_dir"],
                    "condition": self.map_weather_condition(item["weather"]["description"], "weatherbit"),
                    "description": item["weather"]["description"]
                })
            normalized["hourly"] = hourly_forecasts
        
        # Process daily forecast
        if "forecast" in data:
            daily_forecasts = []
            for item in data["forecast"]["data"][:7]:
                daily_forecasts.append({
                    "date": datetime.fromtimestamp(item["ts"]),
                    "temperature_min": item["min_temp"],
                    "temperature_max": item["max_temp"],
                    "humidity": item["rh"],
                    "precipitation_probability": item["pop"],
                    "precipitation_amount": item.get("precip", 0),
                    "wind_speed": item["wind_spd"],
                    "wind_direction": item["wind_dir"],
                    "condition": self.map_weather_condition(item["weather"]["description"], "weatherbit"),
                    "description": item["weather"]["description"],
                    "sunrise": datetime.fromtimestamp(item["sunrise_ts"]),
                    "sunset": datetime.fromtimestamp(item["sunset_ts"])
                })
            normalized["daily"] = daily_forecasts
        
        # Process air quality
        if "air_quality" in data:
            aqi_data = data["air_quality"]["data"][0]
            normalized["air_quality"] = {
                "aqi": aqi_data.get("aqi", 1),
                "pm25": aqi_data.get("pm25", 0),
                "pm10": aqi_data.get("pm10", 0),
                "o3": aqi_data.get("o3", 0),
                "no2": aqi_data.get("no2", 0),
                "so2": aqi_data.get("so2", 0),
                "co": aqi_data.get("co", 0),
                "category": self.get_aqi_category(aqi_data.get("aqi", 1))
            }
        
        return normalized
    
    def normalize_visualcrossing_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Visual Crossing data to standard format"""
        if "error" in data or "data" not in data:
            return {}
        
        weather_data = data["data"]
        current_conditions = weather_data.get("currentConditions", {})
        
        normalized = {
            "location": {
                "name": weather_data.get("address", ""),
                "country": "",  # Visual Crossing doesn't provide country in API response
                "coordinates": {
                    "lat": weather_data.get("latitude", 0),
                    "lon": weather_data.get("longitude", 0)
                }
            },
            "current": {
                "temperature": current_conditions.get("temp", 0),
                "feels_like": current_conditions.get("feelslike", 0),
                "humidity": current_conditions.get("humidity", 0),
                "pressure": current_conditions.get("pressure", 0),
                "visibility": current_conditions.get("visibility", 0),
                "wind_speed": current_conditions.get("windspeed", 0),
                "wind_direction": current_conditions.get("winddir", 0),
                "condition": self.map_weather_condition(current_conditions.get("conditions", ""), "visualcrossing"),
                "description": current_conditions.get("conditions", ""),
                "icon": current_conditions.get("icon"),
                "timestamp": datetime.now()  # Visual Crossing provides relative time
            }
        }
        
        # Process hourly forecast
        hourly_forecasts = []
        for item in weather_data.get("days", [{}])[0].get("hours", [])[:48]:
            hourly_forecasts.append({
                "time": datetime.strptime(item["datetime"], "%Y-%m-%dT%H:%M:%S"),
                "temperature": item.get("temp", 0),
                "feels_like": item.get("feelslike", 0),
                "humidity": item.get("humidity", 0),
                "precipitation_probability": item.get("precipprob", 0),
                "precipitation_amount": item.get("precip", 0),
                "wind_speed": item.get("windspeed", 0),
                "wind_direction": item.get("winddir", 0),
                "condition": self.map_weather_condition(item.get("conditions", ""), "visualcrossing"),
                "description": item.get("conditions", "")
            })
        normalized["hourly"] = hourly_forecasts
        
        # Process daily forecast
        daily_forecasts = []
        for item in weather_data.get("days", [])[:7]:
            daily_forecasts.append({
                "date": datetime.strptime(item["datetime"], "%Y-%m-%d"),
                "temperature_min": item.get("tempmin", 0),
                "temperature_max": item.get("tempmax", 0),
                "humidity": item.get("humidity", 0),
                "precipitation_probability": item.get("precipprob", 0),
                "precipitation_amount": item.get("precip", 0),
                "wind_speed": item.get("windspeed", 0),
                "wind_direction": item.get("winddir", 0),
                "condition": self.map_weather_condition(item.get("conditions", ""), "visualcrossing"),
                "description": item.get("conditions", ""),
                "sunrise": datetime.strptime(f"{item['datetime']} {item['sunrise']}", "%Y-%m-%d %H:%M"),
                "sunset": datetime.strptime(f"{item['datetime']} {item['sunset']}", "%Y-%m-%d %H:%M")
            })
        normalized["daily"] = daily_forecasts
        
        # Process alerts
        if "alerts" in weather_data:
            normalized["alerts"] = weather_data["alerts"]
        
        return normalized
    
    def get_aqi_category(self, aqi_value: int) -> str:
        """Get AQI category from value (1-5 scale)"""
        categories = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        return categories.get(aqi_value, "Unknown")
    
    def aggregate_weather_data(self, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate data from multiple weather APIs"""
        if not data_sources:
            raise HTTPException(status_code=500, detail="No weather data available")
        
        # Normalize all data sources
        normalized_sources = []
        for source_data in data_sources:
            if "source" in source_data:
                if source_data["source"] == "openweather":
                    normalized = self.normalize_openweather_data(source_data)
                elif source_data["source"] == "weatherbit":
                    normalized = self.normalize_weatherbit_data(source_data)
                elif source_data["source"] == "visualcrossing":
                    normalized = self.normalize_visualcrossing_data(source_data)
                else:
                    continue
                
                if normalized:
                    normalized_sources.append(normalized)
        
        if not normalized_sources:
            raise HTTPException(status_code=500, detail="Failed to process weather data")
        
        # Use the first successful source as base
        base_data = normalized_sources[0]
        
        # Aggregate current weather (average of available sources)
        if len(normalized_sources) > 1:
            current_temps = [s["current"]["temperature"] for s in normalized_sources if "current" in s]
            current_humidity = [s["current"]["humidity"] for s in normalized_sources if "current" in s]
            current_pressure = [s["current"]["pressure"] for s in normalized_sources if "current" in s]
            
            if current_temps:
                base_data["current"]["temperature"] = sum(current_temps) / len(current_temps)
            if current_humidity:
                base_data["current"]["humidity"] = int(sum(current_humidity) / len(current_humidity))
            if current_pressure:
                base_data["current"]["pressure"] = sum(current_pressure) / len(current_pressure)
        
        # Merge hourly forecasts (prioritize the most detailed)
        hourly_data = []
        for source in normalized_sources:
            if "hourly" in source and len(source["hourly"]) > len(hourly_data):
                hourly_data = source["hourly"]
        base_data["hourly"] = hourly_data
        
        # Merge daily forecasts (prioritize the most detailed)
        daily_data = []
        for source in normalized_sources:
            if "daily" in source and len(source["daily"]) > len(daily_data):
                daily_data = source["daily"]
        base_data["daily"] = daily_data
        
        # Merge air quality (prioritize the most complete)
        for source in normalized_sources:
            if "air_quality" in source and source["air_quality"].get("aqi"):
                base_data["air_quality"] = source["air_quality"]
                break
        
        # Merge alerts
        alerts = []
        for source in normalized_sources:
            if "alerts" in source:
                alerts.extend(source["alerts"])
        base_data["alerts"] = alerts
        
        # Add metadata
        base_data["data_sources"] = [s["source"] for s in data_sources if "error" not in s]
        base_data["last_updated"] = datetime.now()
        
        return base_data

# Initialize aggregator
aggregator = WeatherDataAggregator()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Weather API Wrapper", "version": "1.0.0"}

@app.get("/weather", response_model=WeatherResponse)
async def get_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    units: TemperatureUnit = Query(TemperatureUnit.CELSIUS, description="Temperature units"),
    wind_units: WindSpeedUnit = Query(WindSpeedUnit.KMH, description="Wind speed units"),
    sources: str = Query("openweather,weatherbit,visualcrossing", description="Comma-separated list of data sources")
):
    """Get comprehensive weather data from multiple APIs"""
    
    # Parse sources
    requested_sources = [s.strip() for s in sources.split(",")]
    valid_sources = ["openweather", "weatherbit", "visualcrossing"]
    sources_to_use = [s for s in requested_sources if s in valid_sources]
    
    if not sources_to_use:
        raise HTTPException(status_code=400, detail="No valid weather sources specified")
    
    # Fetch data from all requested sources concurrently
    tasks = []
    if "openweather" in sources_to_use:
        tasks.append(aggregator.fetch_openweather_data(lat, lon))
    if "weatherbit" in sources_to_use:
        tasks.append(aggregator.fetch_weatherbit_data(lat, lon))
    if "visualcrossing" in sources_to_use:
        tasks.append(aggregator.fetch_visualcrossing_data(lat, lon))
    
    data_sources = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and errors
    valid_data = [data for data in data_sources if isinstance(data, dict) and "error" not in data]
    
    if not valid_data:
        raise HTTPException(status_code=503, detail="All weather services are currently unavailable")
    
    # Aggregate and normalize data
    aggregated_data = aggregator.aggregate_weather_data(valid_data)
    
    # Convert units if needed
    if units != TemperatureUnit.CELSIUS:
        # Convert temperatures
        aggregated_data["current"]["temperature"] = aggregator.convert_temperature(
            aggregated_data["current"]["temperature"], "celsius", units.value
        )
        aggregated_data["current"]["feels_like"] = aggregator.convert_temperature(
            aggregated_data["current"]["feels_like"], "celsius", units.value
        )
        
        # Convert hourly forecasts
        for hour in aggregated_data.get("hourly", []):
            hour["temperature"] = aggregator.convert_temperature(
                hour["temperature"], "celsius", units.value
            )
            hour["feels_like"] = aggregator.convert_temperature(
                hour["feels_like"], "celsius", units.value
            )
        
        # Convert daily forecasts
        for day in aggregated_data.get("daily", []):
            day["temperature_min"] = aggregator.convert_temperature(
                day["temperature_min"], "celsius", units.value
            )
            day["temperature_max"] = aggregator.convert_temperature(
                day["temperature_max"], "celsius", units.value
            )
    
    if wind_units != WindSpeedUnit.KMH:
        # Convert wind speeds
        aggregated_data["current"]["wind_speed"] = aggregator.convert_wind_speed(
            aggregated_data["current"]["wind_speed"], "km/h", wind_units.value
        )
        
        # Convert hourly forecasts
        for hour in aggregated_data.get("hourly", []):
            hour["wind_speed"] = aggregator.convert_wind_speed(
                hour["wind_speed"], "km/h", wind_units.value
            )
        
        # Convert daily forecasts
        for day in aggregated_data.get("daily", []):
            day["wind_speed"] = aggregator.convert_wind_speed(
                day["wind_speed"], "km/h", wind_units.value
            )
    
    # Build response model
    location_data = aggregated_data["location"]
    location = Location(
        name=location_data["name"],
        country=location_data["country"],
        coordinates=Coordinates(
            lat=location_data["coordinates"]["lat"],
            lon=location_data["coordinates"]["lon"]
        )
    )
    
    current_data = aggregated_data["current"]
    current = CurrentWeather(
        temperature=current_data["temperature"],
        feels_like=current_data["feels_like"],
        humidity=current_data["humidity"],
        pressure=current_data["pressure"],
        visibility=current_data.get("visibility", 0),
        uv_index=current_data.get("uv_index"),
        aqi=aggregated_data.get("air_quality", {}).get("aqi"),
        wind_speed=current_data["wind_speed"],
        wind_direction=current_data["wind_direction"],
        wind_gust=current_data.get("wind_gust"),
        condition=current_data["condition"],
        description=current_data["description"],
        icon=current_data.get("icon"),
        timestamp=current_data["timestamp"]
    )
    
    hourly = [HourlyForecast(**hour) for hour in aggregated_data.get("hourly", [])]
    daily = [DailyForecast(**day) for day in aggregated_data.get("daily", [])]
    
    air_quality = None
    if "air_quality" in aggregated_data:
        aqi_data = aggregated_data["air_quality"]
        air_quality = AirQuality(**aqi_data)
    
    return WeatherResponse(
        location=location,
        current=current,
        hourly=hourly,
        daily=daily,
        air_quality=air_quality,
        alerts=aggregated_data.get("alerts", []),
        data_sources=aggregated_data["data_sources"],
        last_updated=aggregated_data["last_updated"]
    )

@app.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    sources: str = Query("openweather,weatherbit")
):
    """Get current weather only (faster response)"""
    # Parse sources
    requested_sources = [s.strip() for s in sources.split(",")]
    valid_sources = ["openweather", "weatherbit"]
    sources_to_use = [s for s in requested_sources if s in valid_sources]
    
    # Fetch only current weather data
    tasks = []
    if "openweather" in sources_to_use:
        tasks.append(aggregator.fetch_openweather_data(lat, lon))
    if "weatherbit" in sources_to_use:
        tasks.append(aggregator.fetch_weatherbit_data(lat, lon))
    
    data_sources = await asyncio.gather(*tasks, return_exceptions=True)
    valid_data = [data for data in data_sources if isinstance(data, dict) and "error" not in data]
    
    if not valid_data:
        raise HTTPException(status_code=503, detail="Weather services unavailable")
    
    aggregated_data = aggregator.aggregate_weather_data(valid_data)
    return aggregated_data["current"]

@app.get("/weather/forecast")
async def get_weather_forecast(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=16, description="Number of days to forecast"),
    sources: str = Query("openweather,weatherbit,visualcrossing")
):
    """Get weather forecast only"""
    # Parse sources
    requested_sources = [s.strip() for s in sources.split(",")]
    valid_sources = ["openweather", "weatherbit", "visualcrossing"]
    sources_to_use = [s for s in requested_sources if s in valid_sources]
    
    # Fetch forecast data
    tasks = []
    if "openweather" in sources_to_use:
        tasks.append(aggregator.fetch_openweather_data(lat, lon))
    if "weatherbit" in sources_to_use:
        tasks.append(aggregator.fetch_weatherbit_data(lat, lon))
    if "visualcrossing" in sources_to_use:
        tasks.append(aggregator.fetch_visualcrossing_data(lat, lon))
    
    data_sources = await asyncio.gather(*tasks, return_exceptions=True)
    valid_data = [data for data in data_sources if isinstance(data, dict) and "error" not in data]
    
    if not valid_data:
        raise HTTPException(status_code=503, detail="Weather services unavailable")
    
    aggregated_data = aggregator.aggregate_weather_data(valid_data)
    
    # Return only requested number of days
    daily_forecast = aggregated_data.get("daily", [])[:days]
    hourly_forecast = aggregated_data.get("hourly", [])[:days * 24]  # 24 hours per day
    
    return {
        "daily": daily_forecast,
        "hourly": hourly_forecast,
        "data_sources": aggregated_data["data_sources"]
    }

@app.get("/weather/air-quality")
async def get_air_quality(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    sources: str = Query("openweather,weatherbit")
):
    """Get air quality data"""
    # Parse sources
    requested_sources = [s.strip() for s in sources.split(",")]
    valid_sources = ["openweather", "weatherbit"]
    sources_to_use = [s for s in requested_sources if s in valid_sources]
    
    # Fetch air quality data
    tasks = []
    if "openweather" in sources_to_use:
        tasks.append(aggregator.fetch_openweather_data(lat, lon))
    if "weatherbit" in sources_to_use:
        tasks.append(aggregator.fetch_weatherbit_data(lat, lon))
    
    data_sources = await asyncio.gather(*tasks, return_exceptions=True)
    valid_data = [data for data in data_sources if isinstance(data, dict) and "error" not in data]
    
    if not valid_data:
        raise HTTPException(status_code=503, detail="Weather services unavailable")
    
    aggregated_data = aggregator.aggregate_weather_data(valid_data)
    
    if "air_quality" not in aggregated_data:
        raise HTTPException(status_code=404, detail="Air quality data not available")
    
    return aggregated_data["air_quality"]

@app.get("/weather/alerts")
async def get_weather_alerts(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    sources: str = Query("visualcrossing")
):
    """Get weather alerts"""
    # Visual Crossing is the main source for alerts
    if "visualcrossing" not in sources:
        raise HTTPException(status_code=400, detail="Visual Crossing is required for alerts")
    
    data = await aggregator.fetch_visualcrossing_data(lat, lon)
    
    if "error" in data:
        raise HTTPException(status_code=503, detail="Alert service unavailable")
    
    normalized = aggregator.normalize_visualcrossing_data(data)
    return normalized.get("alerts", [])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "available_sources": list(API_KEYS.keys()),
        "aggregator_status": "active"
    }

@app.get("/sources")
async def get_available_sources():
    """Get list of available weather data sources"""
    return {
        "sources": [
            {
                "name": "OpenWeatherMap",
                "id": "openweather",
                "features": ["current", "forecast", "air_quality"],
                "rate_limit": "1000 calls/day",
                "description": "Popular weather API with global coverage"
            },
            {
                "name": "WeatherBit",
                "id": "weatherbit",
                "features": ["current", "forecast", "hourly", "air_quality"],
                "rate_limit": "500 calls/day",
                "description": "Detailed weather data with 16-day forecast"
            },
            {
                "name": "Visual Crossing",
                "id": "visualcrossing",
                "features": ["current", "forecast", "hourly", "alerts"],
                "rate_limit": "1000 calls/day",
                "description": "Comprehensive weather data with alerts"
            }
        ]
    }

# Cleanup on shutdown
@app.on_event("shutdown")
async def cleanup():
    await aggregator.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
