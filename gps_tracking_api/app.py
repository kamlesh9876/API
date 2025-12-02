from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
import random
import math

app = FastAPI(title="GPS Tracking API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class TrackingMode(str, Enum):
    REAL_TIME = "real_time"
    INTERVAL = "interval"
    ON_DEMAND = "on_demand"
    SLEEP = "sleep"

class AlertType(str, Enum):
    GEOFENCE_ENTER = "geofence_enter"
    GEOFENCE_EXIT = "geofence_exit"
    SPEED_LIMIT = "speed_limit"
    IDLE_TIME = "idle_time"
    LOW_BATTERY = "low_battery"
    DEVICE_OFFLINE = "device_offline"
    SOS = "sos"

class Device(BaseModel):
    id: str
    name: str
    device_id: str
    imei: Optional[str] = None
    phone_number: Optional[str] = None
    model: str
    manufacturer: str
    firmware_version: str
    status: DeviceStatus
    tracking_mode: TrackingMode
    battery_level: int
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
    owner_id: str
    metadata: Dict[str, Any] = {}

class Location(BaseModel):
    id: str
    device_id: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: float
    speed: float
    heading: float
    timestamp: datetime
    address: Optional[str] = None
    created_at: datetime

class Geofence(BaseModel):
    id: str
    name: str
    device_id: str
    fence_type: str  # "circle", "polygon", "rectangle"
    coordinates: Dict[str, Any]
    radius: Optional[float] = None  # for circle
    is_active: bool
    created_at: datetime
    updated_at: datetime

class Alert(BaseModel):
    id: str
    device_id: str
    alert_type: AlertType
    message: str
    severity: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    location_data: Optional[Dict[str, Any]] = None

class Trip(BaseModel):
    id: str
    device_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    start_location: Dict[str, float]
    end_location: Optional[Dict[str, float]] = None
    distance: float
    duration: Optional[int] = None
    max_speed: float
    avg_speed: float
    is_active: bool
    created_at: datetime

devices: Dict[str, Device] = {}
locations: Dict[str, List[Location]] = {}
geofences: Dict[str, List[Geofence]] = {}
alerts: Dict[str, List[Alert]] = {}
trips: Dict[str, List[Trip]] = {}
websocket_connections: Dict[str, WebSocket] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: str, client_id: str):
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = []
        self.active_connections[device_id].append(websocket)
        websocket_connections[client_id] = websocket

    def disconnect(self, device_id: str, websocket: WebSocket, client_id: str):
        if device_id in self.active_connections:
            if websocket in self.active_connections[device_id]:
                self.active_connections[device_id].remove(websocket)
        if client_id in websocket_connections:
            del websocket_connections[client_id]

    async def broadcast_to_device(self, device_id: str, message: dict):
        if device_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[device_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[device_id].remove(conn)

manager = ConnectionManager()

def generate_device_id() -> str:
    return f"device_{uuid.uuid4().hex[:8]}"

def generate_location_id() -> str:
    return f"loc_{uuid.uuid4().hex[:8]}"

def generate_geofence_id() -> str:
    return f"geo_{uuid.uuid4().hex[:8]}"

def generate_alert_id() -> str:
    return f"alert_{uuid.uuid4().hex[:8]}"

def generate_trip_id() -> str:
    return f"trip_{uuid.uuid4().hex[:8]}"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def is_point_in_geofence(lat: float, lon: float, geofence: Geofence) -> bool:
    if geofence.fence_type == "circle":
        center_lat = geofence.coordinates["latitude"]
        center_lon = geofence.coordinates["longitude"]
        distance = calculate_distance(lat, lon, center_lat, center_lon)
        return distance <= geofence.radius
    return False

async def check_geofence_alerts(device_id: str, location: Location):
    if device_id not in geofences:
        return
    
    for fence in geofences[device_id]:
        if not fence.is_active:
            continue
        
        is_inside = is_point_in_geofence(location.latitude, location.longitude, fence)
        
        alert_id = generate_alert_id()
        alert = Alert(
            id=alert_id,
            device_id=device_id,
            alert_type=AlertType.GEOFENCE_ENTER if is_inside else AlertType.GEOFENCE_EXIT,
            message=f"Device {'entered' if is_inside else 'exited'} geofence: {fence.name}",
            severity="medium",
            is_resolved=False,
            created_at=datetime.now(),
            location_data={"latitude": location.latitude, "longitude": location.longitude}
        )
        
        if device_id not in alerts:
            alerts[device_id] = []
        alerts[device_id].append(alert)
        
        await manager.broadcast_to_device(device_id, {
            "type": "geofence_alert",
            "alert": alert.dict(),
            "timestamp": datetime.now().isoformat()
        })

async def simulate_gps_data():
    while True:
        for device_id, device in devices.items():
            if device.status == DeviceStatus.ACTIVE:
                # Simulate movement
                if device_id not in locations:
                    locations[device_id] = []
                
                last_location = locations[device_id][-1] if locations[device_id] else None
                
                if last_location:
                    # Simulate movement
                    new_lat = last_location.latitude + random.uniform(-0.001, 0.001)
                    new_lon = last_location.longitude + random.uniform(-0.001, 0.001)
                    speed = random.uniform(0, 80)
                    heading = random.uniform(0, 360)
                else:
                    # Initial location
                    new_lat = 40.7128 + random.uniform(-0.1, 0.1)
                    new_lon = -74.0060 + random.uniform(-0.1, 0.1)
                    speed = random.uniform(0, 60)
                    heading = random.uniform(0, 360)
                
                location_id = generate_location_id()
                location = Location(
                    id=location_id,
                    device_id=device_id,
                    latitude=new_lat,
                    longitude=new_lon,
                    altitude=random.uniform(0, 100),
                    accuracy=random.uniform(5, 20),
                    speed=speed,
                    heading=heading,
                    timestamp=datetime.now(),
                    created_at=datetime.now()
                )
                
                locations[device_id].append(location)
                
                # Keep only last 1000 locations
                if len(locations[device_id]) > 1000:
                    locations[device_id] = locations[device_id][-1000:]
                
                # Update device last seen
                device.last_seen = datetime.now()
                device.updated_at = datetime.now()
                
                # Broadcast location update
                await manager.broadcast_to_device(device_id, {
                    "type": "location_update",
                    "location": location.dict(),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check geofence alerts
                await check_geofence_alerts(device_id, location)
        
        await asyncio.sleep(30)

asyncio.create_task(simulate_gps_data())

def initialize_sample_data():
    device_id = generate_device_id()
    device = Device(
        id=device_id,
        name="Company Vehicle 001",
        device_id="GPS001",
        imei="123456789012345",
        phone_number="+1234567890",
        model="Tracker Pro",
        manufacturer="GPS Corp",
        firmware_version="v2.1.0",
        status=DeviceStatus.ACTIVE,
        tracking_mode=TrackingMode.REAL_TIME,
        battery_level=85,
        last_seen=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        owner_id="user_123"
    )
    devices[device_id] = device
    locations[device_id] = []
    geofences[device_id] = []
    alerts[device_id] = []
    trips[device_id] = []

initialize_sample_data()

@app.post("/api/devices", response_model=Device)
async def create_device(
    name: str,
    device_id: str,
    model: str,
    manufacturer: str,
    firmware_version: str,
    imei: Optional[str] = None,
    phone_number: Optional[str] = None,
    tracking_mode: TrackingMode = TrackingMode.REAL_TIME,
    owner_id: str = "user_123"
):
    device_id_internal = generate_device_id()
    
    device = Device(
        id=device_id_internal,
        name=name,
        device_id=device_id,
        imei=imei,
        phone_number=phone_number,
        model=model,
        manufacturer=manufacturer,
        firmware_version=firmware_version,
        status=DeviceStatus.ACTIVE,
        tracking_mode=tracking_mode,
        battery_level=100,
        last_seen=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        owner_id=owner_id
    )
    
    devices[device_id_internal] = device
    locations[device_id_internal] = []
    geofences[device_id_internal] = []
    alerts[device_id_internal] = []
    trips[device_id_internal] = []
    
    return device

@app.get("/api/devices", response_model=List[Device])
async def get_devices(
    status: Optional[DeviceStatus] = None,
    owner_id: Optional[str] = None,
    limit: int = 50
):
    filtered_devices = list(devices.values())
    
    if status:
        filtered_devices = [d for d in filtered_devices if d.status == status]
    
    if owner_id:
        filtered_devices = [d for d in filtered_devices if d.owner_id == owner_id]
    
    return filtered_devices[:limit]

@app.get("/api/devices/{device_id}", response_model=Device)
async def get_device(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@app.post("/api/devices/{device_id}/locations", response_model=Location)
async def add_location(
    device_id: str,
    latitude: float,
    longitude: float,
    altitude: Optional[float] = None,
    accuracy: float = 10.0,
    speed: float = 0.0,
    heading: float = 0.0
):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    location_id = generate_location_id()
    location = Location(
        id=location_id,
        device_id=device_id,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        accuracy=accuracy,
        speed=speed,
        heading=heading,
        timestamp=datetime.now(),
        created_at=datetime.now()
    )
    
    if device_id not in locations:
        locations[device_id] = []
    
    locations[device_id].append(location)
    
    # Update device last seen
    devices[device_id].last_seen = datetime.now()
    devices[device_id].updated_at = datetime.now()
    
    # Broadcast update
    await manager.broadcast_to_device(device_id, {
        "type": "location_update",
        "location": location.dict(),
        "timestamp": datetime.now().isoformat()
    })
    
    # Check geofence alerts
    await check_geofence_alerts(device_id, location)
    
    return location

@app.get("/api/devices/{device_id}/locations", response_model=List[Location])
async def get_locations(
    device_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_locations = locations.get(device_id, [])
    
    if start_time:
        device_locations = [loc for loc in device_locations if loc.timestamp >= start_time]
    
    if end_time:
        device_locations = [loc for loc in device_locations if loc.timestamp <= end_time]
    
    return sorted(device_locations, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.post("/api/devices/{device_id}/geofences", response_model=Geofence)
async def create_geofence(
    device_id: str,
    name: str,
    fence_type: str,
    coordinates: Dict[str, Any],
    radius: Optional[float] = None
):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    geofence_id = generate_geofence_id()
    geofence = Geofence(
        id=geofence_id,
        name=name,
        device_id=device_id,
        fence_type=fence_type,
        coordinates=coordinates,
        radius=radius,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    if device_id not in geofences:
        geofences[device_id] = []
    
    geofences[device_id].append(geofence)
    return geofence

@app.get("/api/devices/{device_id}/geofences", response_model=List[Geofence])
async def get_geofences(device_id: str, is_active: Optional[bool] = None):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_geofences = geofences.get(device_id, [])
    
    if is_active is not None:
        device_geofences = [g for g in device_geofences if g.is_active == is_active]
    
    return device_geofences

@app.get("/api/devices/{device_id}/alerts", response_model=List[Alert])
async def get_alerts(
    device_id: str,
    alert_type: Optional[AlertType] = None,
    is_resolved: Optional[bool] = None,
    limit: int = 100
):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device_alerts = alerts.get(device_id, [])
    
    if alert_type:
        device_alerts = [a for a in device_alerts if a.alert_type == alert_type]
    
    if is_resolved is not None:
        device_alerts = [a for a in device_alerts if a.is_resolved == is_resolved]
    
    return sorted(device_alerts, key=lambda x: x.created_at, reverse=True)[:limit]

@app.get("/api/stats")
async def get_tracking_stats():
    total_devices = len(devices)
    active_devices = len([d for d in devices.values() if d.status == DeviceStatus.ACTIVE])
    total_locations = sum(len(locs) for locs in locations.values())
    total_geofences = sum(len(fences) for fences in geofences.values())
    total_alerts = sum(len(alert_list) for alert_list in alerts.values())
    
    return {
        "total_devices": total_devices,
        "active_devices": active_devices,
        "total_locations": total_locations,
        "total_geofences": total_geofences,
        "total_alerts": total_alerts,
        "supported_device_statuses": [s.value for s in DeviceStatus],
        "supported_tracking_modes": [m.value for m in TrackingMode],
        "supported_alert_types": [t.value for t in AlertType]
    }

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, device_id, client_id)
    
    try:
        if device_id in devices:
            device = devices[device_id]
            await manager.send_to_client(client_id, {
                "type": "device_status",
                "device": device.dict(),
                "timestamp": datetime.now().isoformat()
            })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(device_id, websocket, client_id)

@app.get("/")
async def root():
    return {"message": "GPS Tracking API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
