from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import secrets
import string
from collections import defaultdict
import json

app = FastAPI(title="URL Shortener API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"

class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    OPERA = "opera"
    UNKNOWN = "unknown"

# Pydantic models
class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_slug: Optional[str] = None
    expires_at: Optional[datetime] = None
    password: Optional[str] = None

class URLResponse(BaseModel):
    id: int
    short_url: str
    original_url: str
    custom_slug: Optional[str]
    slug: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    is_active: bool
    has_password: bool

class ClickAnalytics(BaseModel):
    timestamp: datetime
    ip_address: str
    user_agent: str
    referrer: Optional[str]
    country: Optional[str]
    city: Optional[str]
    device_type: DeviceType
    browser_type: BrowserType
    os: Optional[str]

class URLAnalytics(BaseModel):
    short_url: str
    total_clicks: int
    unique_clicks: int
    clicks_today: int
    clicks_this_week: int
    clicks_this_month: int
    top_countries: List[Dict[str, Any]]
    top_cities: List[Dict[str, Any]]
    device_breakdown: Dict[str, int]
    browser_breakdown: Dict[str, int]
    hourly_clicks: Dict[str, int]
    daily_clicks: Dict[str, int]
    recent_clicks: List[ClickAnalytics]

class URLUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

# In-memory database (for demo purposes)
urls_db = []
clicks_db = []
analytics_db = defaultdict(lambda: defaultdict(int))
next_url_id = 1

# Helper functions
def generate_short_slug(length: int = 6) -> str:
    """Generate a random short slug"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def parse_user_agent(user_agent: str) -> tuple:
    """Simple user agent parsing"""
    user_agent_lower = user_agent.lower()
    
    # Device detection
    if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone', 'ipad']):
        if 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            device_type = DeviceType.TABLET
        else:
            device_type = DeviceType.MOBILE
    else:
        device_type = DeviceType.DESKTOP
    
    # Browser detection
    if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
        browser_type = BrowserType.CHROME
    elif 'firefox' in user_agent_lower:
        browser_type = BrowserType.FIREFOX
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        browser_type = BrowserType.SAFARI
    elif 'edg' in user_agent_lower:
        browser_type = BrowserType.EDGE
    elif 'opera' in user_agent_lower:
        browser_type = BrowserType.OPERA
    else:
        browser_type = BrowserType.UNKNOWN
    
    # OS detection (simplified)
    os = "unknown"
    if 'windows' in user_agent_lower:
        os = "Windows"
    elif 'mac' in user_agent_lower:
        os = "macOS"
    elif 'linux' in user_agent_lower:
        os = "Linux"
    elif 'android' in user_agent_lower:
        os = "Android"
    elif 'ios' in user_agent_lower:
        os = "iOS"
    
    return device_type, browser_type, os

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded header (common in production)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Fallback to direct IP
    return request.client.host if request.client else "unknown"

def get_geo_location(ip_address: str) -> tuple:
    """Mock geo location - in production, use a real GeoIP service"""
    # Simulate different locations based on IP patterns
    if ip_address.startswith("127.") or ip_address == "unknown":
        return "Localhost", "Development"
    elif ip_address.startswith("192.168."):
        return "Private Network", "Local"
    else:
        # Mock some common locations
        locations = [
            ("United States", "New York"),
            ("United Kingdom", "London"),
            ("Germany", "Berlin"),
            ("India", "Mumbai"),
            ("Japan", "Tokyo"),
            ("Canada", "Toronto"),
            ("Australia", "Sydney"),
            ("Brazil", "São Paulo")
        ]
        return locations[hash(ip_address) % len(locations)]

def track_click(url_id: int, request: Request):
    """Track click analytics"""
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    referrer = request.headers.get("Referer")
    
    device_type, browser_type, os = parse_user_agent(user_agent)
    country, city = get_geo_location(ip_address)
    
    click_data = {
        "id": len(clicks_db) + 1,
        "url_id": url_id,
        "timestamp": datetime.now(),
        "ip_address": ip_address,
        "user_agent": user_agent,
        "referrer": referrer,
        "country": country,
        "city": city,
        "device_type": device_type,
        "browser_type": browser_type,
        "os": os
    }
    
    clicks_db.append(click_data)
    
    # Update analytics counters
    analytics_db[url_id]["total_clicks"] += 1
    analytics_db[url_id]["countries"][country] += 1
    analytics_db[url_id]["cities"][city] += 1
    analytics_db[url_id]["devices"][device_type.value] += 1
    analytics_db[url_id]["browsers"][browser_type.value] += 1
    
    # Time-based analytics
    hour_key = click_data["timestamp"].strftime("%H")
    day_key = click_data["timestamp"].strftime("%Y-%m-%d")
    analytics_db[url_id]["hourly"][hour_key] += 1
    analytics_db[url_id]["daily"][day_key] += 1

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to URL Shortener API", "version": "1.0.0"}

# Create short URL
@app.post("/shorten", response_model=URLResponse)
async def create_short_url(url_data: URLCreate, request: Request):
    """Create a shortened URL"""
    global next_url_id
    
    # Check if custom slug is already taken
    if url_data.custom_slug:
        if any(url["custom_slug"] == url_data.custom_slug for url in urls_db):
            raise HTTPException(
                status_code=400,
                detail="Custom slug already taken"
            )
        slug = url_data.custom_slug
    else:
        # Generate unique slug
        while True:
            slug = generate_short_slug()
            if not any(url["slug"] == slug for url in urls_db):
                break
    
    # Create URL entry
    new_url = {
        "id": next_url_id,
        "original_url": str(url_data.original_url),
        "custom_slug": url_data.custom_slug,
        "slug": slug,
        "created_at": datetime.now(),
        "expires_at": url_data.expires_at,
        "click_count": 0,
        "is_active": True,
        "password": url_data.password,
        "created_by_ip": get_client_ip(request)
    }
    
    urls_db.append(new_url)
    next_url_id += 1
    
    # Initialize analytics
    analytics_db[new_url["id"]] = {
        "total_clicks": 0,
        "countries": defaultdict(int),
        "cities": defaultdict(int),
        "devices": defaultdict(int),
        "browsers": defaultdict(int),
        "hourly": defaultdict(int),
        "daily": defaultdict(int)
    }
    
    # Build response
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{slug}"
    
    return URLResponse(
        id=new_url["id"],
        short_url=short_url,
        original_url=new_url["original_url"],
        custom_slug=new_url["custom_slug"],
        slug=new_url["slug"],
        created_at=new_url["created_at"],
        expires_at=new_url["expires_at"],
        click_count=new_url["click_count"],
        is_active=new_url["is_active"],
        has_password=bool(new_url["password"])
    )

# Redirect to original URL
@app.get("/{slug}")
async def redirect_to_url(slug: str, request: Request):
    """Redirect short URL to original URL"""
    url_entry = next((url for url in urls_db if url["slug"] == slug), None)
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if not url_entry["is_active"]:
        raise HTTPException(status_code=410, detail="URL is no longer active")
    
    if url_entry["expires_at"] and url_entry["expires_at"] < datetime.now():
        raise HTTPException(status_code=410, detail="URL has expired")
    
    # Track click
    track_click(url_entry["id"], request)
    url_entry["click_count"] += 1
    
    return RedirectResponse(url_entry["original_url"])

# Get URL info
@app.get("/url/{slug}", response_model=URLResponse)
async def get_url_info(slug: str, request: Request):
    """Get information about a shortened URL"""
    url_entry = next((url for url in urls_db if url["slug"] == slug), None)
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")
    
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{slug}"
    
    return URLResponse(
        id=url_entry["id"],
        short_url=short_url,
        original_url=url_entry["original_url"],
        custom_slug=url_entry["custom_slug"],
        slug=url_entry["slug"],
        created_at=url_entry["created_at"],
        expires_at=url_entry["expires_at"],
        click_count=url_entry["click_count"],
        is_active=url_entry["is_active"],
        has_password=bool(url_entry["password"])
    )

# Get URL analytics
@app.get("/analytics/{slug}", response_model=URLAnalytics)
async def get_url_analytics(slug: str):
    """Get detailed analytics for a shortened URL"""
    url_entry = next((url for url in urls_db if url["slug"] == slug), None)
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")
    
    url_id = url_entry["id"]
    analytics = analytics_db[url_id]
    
    # Calculate time-based metrics
    now = datetime.now()
    today = now.date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    clicks_today = sum(1 for click in clicks_db 
                      if click["url_id"] == url_id and click["timestamp"].date() == today)
    
    clicks_this_week = sum(1 for click in clicks_db 
                          if click["url_id"] == url_id and click["timestamp"].date() >= week_ago)
    
    clicks_this_month = sum(1 for click in clicks_db 
                           if click["url_id"] == url_id and click["timestamp"].date() >= month_ago)
    
    # Get unique clicks (by IP)
    unique_ips = set(click["ip_address"] for click in clicks_db if click["url_id"] == url_id)
    unique_clicks = len(unique_ips)
    
    # Top countries
    top_countries = [
        {"country": country, "clicks": count}
        for country, count in sorted(analytics["countries"].items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Top cities
    top_cities = [
        {"city": city, "clicks": count}
        for city, count in sorted(analytics["cities"].items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Recent clicks
    recent_clicks = [
        ClickAnalytics(
            timestamp=click["timestamp"],
            ip_address=click["ip_address"],
            user_agent=click["user_agent"],
            referrer=click["referrer"],
            country=click["country"],
            city=click["city"],
            device_type=click["device_type"],
            browser_type=click["browser_type"],
            os=click["os"]
        )
        for click in sorted(
            [c for c in clicks_db if c["url_id"] == url_id],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:50]
    ]
    
    return URLAnalytics(
        short_url=f"http://localhost:8002/{slug}",
        total_clicks=analytics["total_clicks"],
        unique_clicks=unique_clicks,
        clicks_today=clicks_today,
        clicks_this_week=clicks_this_week,
        clicks_this_month=clicks_this_month,
        top_countries=top_countries,
        top_cities=top_cities,
        device_breakdown=dict(analytics["devices"]),
        browser_breakdown=dict(analytics["browsers"]),
        hourly_clicks=dict(analytics["hourly"]),
        daily_clicks=dict(analytics["daily"]),
        recent_clicks=recent_clicks
    )

# List all URLs
@app.get("/urls", response_model=List[URLResponse])
async def list_urls(request: Request, limit: int = 50, offset: int = 0):
    """List all shortened URLs with pagination"""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    urls_response = []
    for url in urls_db[offset:offset + limit]:
        short_url = f"{base_url}/{url['slug']}"
        urls_response.append(URLResponse(
            id=url["id"],
            short_url=short_url,
            original_url=url["original_url"],
            custom_slug=url["custom_slug"],
            slug=url["slug"],
            created_at=url["created_at"],
            expires_at=url["expires_at"],
            click_count=url["click_count"],
            is_active=url["is_active"],
            has_password=bool(url["password"])
        ))
    
    return urls_response

# Update URL
@app.put("/url/{slug}", response_model=URLResponse)
async def update_url(slug: str, url_update: URLUpdate, request: Request):
    """Update a shortened URL"""
    url_entry = next((url for url in urls_db if url["slug"] == slug), None)
    
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Update fields
    if url_update.original_url:
        url_entry["original_url"] = str(url_update.original_url)
    
    if url_update.expires_at is not None:
        url_entry["expires_at"] = url_update.expires_at
    
    if url_update.is_active is not None:
        url_entry["is_active"] = url_update.is_active
    
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    short_url = f"{base_url}/{slug}"
    
    return URLResponse(
        id=url_entry["id"],
        short_url=short_url,
        original_url=url_entry["original_url"],
        custom_slug=url_entry["custom_slug"],
        slug=url_entry["slug"],
        created_at=url_entry["created_at"],
        expires_at=url_entry["expires_at"],
        click_count=url_entry["click_count"],
        is_active=url_entry["is_active"],
        has_password=bool(url_entry["password"])
    )

# Delete URL
@app.delete("/url/{slug}")
async def delete_url(slug: str):
    """Delete a shortened URL"""
    url_index = next((i for i, url in enumerate(urls_db) if url["slug"] == slug), None)
    
    if url_index is None:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Remove URL
    del urls_db[url_index]
    
    # Clean up analytics
    url_id = urls_db[url_index]["id"] if url_index < len(urls_db) else None
    if url_id in analytics_db:
        del analytics_db[url_id]
    
    # Remove associated clicks
    clicks_db[:] = [click for click in clicks_db if click["url_id"] != url_id]
    
    return {"message": "URL deleted successfully"}

# Get global statistics
@app.get("/stats")
async def get_global_stats():
    """Get global statistics for all URLs"""
    total_urls = len(urls_db)
    total_clicks = sum(url["click_count"] for url in urls_db)
    
    active_urls = len([url for url in urls_db if url["is_active"]])
    expired_urls = len([url for url in urls_db if url["expires_at"] and url["expires_at"] < datetime.now()])
    
    # Most popular URLs
    popular_urls = sorted(urls_db, key=lambda x: x["click_count"], reverse=True)[:5]
    
    return {
        "total_urls": total_urls,
        "active_urls": active_urls,
        "expired_urls": expired_urls,
        "total_clicks": total_clicks,
        "average_clicks_per_url": total_clicks / total_urls if total_urls > 0 else 0,
        "popular_urls": [
            {
                "slug": url["slug"],
                "original_url": url["original_url"],
                "click_count": url["click_count"]
            }
            for url in popular_urls
        ]
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "total_urls": len(urls_db),
        "total_clicks": sum(url["click_count"] for url in urls_db)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
