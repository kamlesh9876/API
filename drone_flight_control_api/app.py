from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Tuple
import asyncio
import json
import uuid
import math
from datetime import datetime, timedelta
from enum import Enum

app = FastAPI(title="Drone Flight Control API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class DroneStatus(str, Enum):
    IDLE = "idle"
    TAKEOFF = "takeoff"
    FLYING = "flying"
    LANDING = "landing"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    CHARGING = "charging"

class FlightMode(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"
    RETURN_HOME = "return_home"
    FOLLOW_ME = "follow_me"
    ORBIT = "orbit"
    WAYPOINT = "waypoint"

# Data models
class Position3D(BaseModel):
    latitude: float  # degrees
    longitude: float  # degrees
    altitude: float  # meters above sea level

class Velocity3D(BaseModel):
    x: float  # m/s
    y: float  # m/s
    z: float  # m/s

class Attitude(BaseModel):
    roll: float  # degrees
    pitch: float  # degrees
    yaw: float  # degrees

class Battery(BaseModel):
    voltage: float  # volts
    current: float  # amps
    percentage: float  # 0-100
    temperature: float  # celsius
    remaining_time: int  # seconds

class Drone(BaseModel):
    id: str
    name: str
    model: str
    serial_number: str
    status: DroneStatus
    position: Position3D
    velocity: Velocity3D
    attitude: Attitude
    battery: Battery
    flight_mode: FlightMode
    home_position: Position3D
    max_altitude: float  # meters
    max_distance: float  # meters
    max_speed: float  # m/s
    last_heartbeat: datetime
    firmware_version: str
    is_armed: bool = False
    gps_satellites: int = 0
    signal_strength: int  # 0-100

class Waypoint(BaseModel):
    id: str
    position: Position3D
    altitude: float  # meters above ground
    speed: float  # m/s
    wait_time: int  # seconds
    action: Optional[str] = None  # "photo", "video_start", "video_stop", "land"

class FlightPlan(BaseModel):
    id: str
    name: str
    drone_id: str
    waypoints: List[Waypoint]
    created_at: datetime
    is_active: bool = False
    total_distance: float  # meters
    estimated_duration: int  # seconds

class FlightCommand(BaseModel):
    id: str
    drone_id: str
    command: str  # "takeoff", "land", "goto", "orbit", "emergency_land"
    parameters: Dict[str, Any]
    priority: str  # "low", "normal", "high", "emergency"
    created_at: datetime
    executed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "executed", "failed"

class FlightLog(BaseModel):
    id: str
    drone_id: str
    timestamp: datetime
    position: Position3D
    attitude: Attitude
    battery: Battery
    status: DroneStatus
    event: str  # "takeoff", "landing", "emergency", "waypoint_reached"
    details: Optional[Dict[str, Any]] = None

class NoFlyZone(BaseModel):
    id: str
    name: str
    polygon: List[Position3D]  # vertices of the polygon
    min_altitude: float  # meters
    max_altitude: float  # meters
    is_active: bool = True
    reason: str

# In-memory storage
drones: Dict[str, Drone] = {}
flight_plans: Dict[str, FlightPlan] = {}
flight_commands: Dict[str, FlightCommand] = {}
flight_logs: Dict[str, List[FlightLog]] = {}
no_fly_zones: Dict[str, NoFlyZone] = {}
websocket_connections: Dict[str, WebSocket] = {}

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

    async def send_to_client(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Utility functions
def generate_drone_id() -> str:
    """Generate unique drone ID"""
    return f"drone_{uuid.uuid4().hex[:8]}"

def calculate_distance(pos1: Position3D, pos2: Position3D) -> float:
    """Calculate distance between two GPS positions in meters"""
    # Simplified distance calculation (Haversine formula would be more accurate)
    lat_diff = (pos2.latitude - pos1.latitude) * 111320  # meters per degree latitude
    lon_diff = (pos2.longitude - pos1.longitude) * 111320 * math.cos(math.radians(pos1.latitude))
    alt_diff = pos2.altitude - pos1.altitude
    
    return math.sqrt(lat_diff**2 + lon_diff**2 + alt_diff**2)

def is_in_no_fly_zone(position: Position3D, altitude: float) -> Optional[str]:
    """Check if position is in a no-fly zone"""
    for zone_id, zone in no_fly_zones.items():
        if not zone.is_active:
            continue
        
        # Simple point-in-polygon check (would need proper algorithm for production)
        if altitude >= zone.min_altitude and altitude <= zone.max_altitude:
            # For simplicity, check if position is within bounding box
            lats = [p.latitude for p in zone.polygon]
            lons = [p.longitude for p in zone.polygon]
            
            if (min(lats) <= position.latitude <= max(lats) and
                min(lons) <= position.longitude <= max(lons)):
                return zone_id
    
    return None

def calculate_flight_plan_metrics(waypoints: List[Waypoint]) -> Tuple[float, int]:
    """Calculate total distance and duration for flight plan"""
    total_distance = 0.0
    total_duration = 0
    
    for i in range(len(waypoints) - 1):
        distance = calculate_distance(
            Position3D(latitude=waypoints[i].position.latitude,
                      longitude=waypoints[i].position.longitude,
                      altitude=waypoints[i].altitude),
            Position3D(latitude=waypoints[i+1].position.latitude,
                      longitude=waypoints[i+1].position.longitude,
                      altitude=waypoints[i+1].altitude)
        )
        total_distance += distance
        
        # Calculate travel time
        speed = waypoints[i].speed
        travel_time = distance / speed if speed > 0 else 0
        total_duration += travel_time + waypoints[i].wait_time
    
    return total_distance, int(total_duration)

async def simulate_drone_movement(drone_id: str):
    """Simulate drone movement and battery consumption"""
    while drone_id in drones:
        drone = drones[drone_id]
        
        if drone.status == DroneStatus.FLYING:
            # Simulate movement based on velocity
            dt = 0.1  # 100ms update interval
            
            # Update position based on velocity (simplified)
            drone.position.latitude += drone.velocity.x * dt / 111320
            drone.position.longitude += drone.velocity.y * dt / (111320 * math.cos(math.radians(drone.position.latitude)))
            drone.position.altitude += drone.velocity.z * dt
            
            # Update battery
            power_consumption = 0.1 + abs(drone.velocity.x) + abs(drone.velocity.y) + abs(drone.velocity.z)
            drone.battery.percentage = max(0, drone.battery.percentage - power_consumption * dt)
            drone.battery.remaining_time = int(drone.battery.percentage / power_consumption)
            
            # Check for low battery
            if drone.battery.percentage < 20:
                # Trigger return to home
                if drone.flight_mode != FlightMode.RETURN_HOME:
                    drone.flight_mode = FlightMode.RETURN_HOME
                    await manager.broadcast({
                        "type": "low_battery_warning",
                        "drone_id": drone_id,
                        "battery_percentage": drone.battery.percentage
                    })
            
            # Check for emergency conditions
            if drone.battery.percentage < 5:
                drone.status = DroneStatus.EMERGENCY
                await manager.broadcast({
                    "type": "emergency_landing",
                    "drone_id": drone_id,
                    "reason": "Critical battery level"
                })
            
            # Update heartbeat
            drone.last_heartbeat = datetime.now()
            
            # Broadcast telemetry
            await manager.broadcast({
                "type": "telemetry_update",
                "drone_id": drone_id,
                "position": drone.position.dict(),
                "battery": drone.battery.dict(),
                "status": drone.status.value
            })
        
        await asyncio.sleep(0.1)

async def execute_flight_command(command: FlightCommand):
    """Execute a flight command"""
    drone = drones.get(command.drone_id)
    if not drone:
        return
    
    try:
        command.status = "executed"
        command.executed_at = datetime.now()
        
        if command.command == "takeoff":
            if drone.status == DroneStatus.IDLE and drone.is_armed:
                drone.status = DroneStatus.TAKEOFF
                await asyncio.sleep(2)  # Takeoff duration
                drone.status = DroneStatus.FLYING
                drone.velocity.z = 2.0  # Ascend at 2 m/s
                
                # Log event
                log_entry = FlightLog(
                    id=f"log_{uuid.uuid4().hex[:8]}",
                    drone_id=drone.id,
                    timestamp=datetime.now(),
                    position=drone.position,
                    attitude=drone.attitude,
                    battery=drone.battery,
                    status=drone.status,
                    event="takeoff"
                )
                if drone.id not in flight_logs:
                    flight_logs[drone.id] = []
                flight_logs[drone.id].append(log_entry)
        
        elif command.command == "land":
            if drone.status == DroneStatus.FLYING:
                drone.status = DroneStatus.LANDING
                drone.velocity.z = -1.5  # Descend at 1.5 m/s
                
                # Simulate landing
                await asyncio.sleep(drone.position.altitude / 1.5)
                drone.position.altitude = 0
                drone.velocity = Velocity3D(x=0, y=0, z=0)
                drone.status = DroneStatus.IDLE
                
                # Log event
                log_entry = FlightLog(
                    id=f"log_{uuid.uuid4().hex[:8]}",
                    drone_id=drone.id,
                    timestamp=datetime.now(),
                    position=drone.position,
                    attitude=drone.attitude,
                    battery=drone.battery,
                    status=drone.status,
                    event="landing"
                )
                flight_logs[drone.id].append(log_entry)
        
        elif command.command == "emergency_land":
            drone.status = DroneStatus.EMERGENCY
            drone.velocity = Velocity3D(x=0, y=0, z=-3.0)  # Emergency descent
            
            await asyncio.sleep(drone.position.altitude / 3.0)
            drone.position.altitude = 0
            drone.velocity = Velocity3D(x=0, y=0, z=0)
            drone.status = DroneStatus.IDLE
        
        elif command.command == "goto":
            target_lat = command.parameters.get("latitude")
            target_lon = command.parameters.get("longitude")
            target_alt = command.parameters.get("altitude", drone.position.altitude)
            speed = command.parameters.get("speed", 5.0)
            
            if target_lat and target_lon:
                # Calculate direction and set velocity
                lat_diff = target_lat - drone.position.latitude
                lon_diff = target_lon - drone.position.longitude
                alt_diff = target_alt - drone.position.altitude
                
                distance = math.sqrt(lat_diff**2 + lon_diff**2 + alt_diff**2)
                if distance > 0:
                    drone.velocity.x = (lat_diff / distance) * speed
                    drone.velocity.y = (lon_diff / distance) * speed
                    drone.velocity.z = (alt_diff / distance) * speed
        
        elif command.command == "orbit":
            center_lat = command.parameters.get("latitude")
            center_lon = command.parameters.get("longitude")
            radius = command.parameters.get("radius", 10.0)
            speed = command.parameters.get("speed", 3.0)
            
            # Start orbit mode
            drone.flight_mode = FlightMode.ORBIT
            # Orbit logic would be implemented here
        
        await manager.broadcast({
            "type": "command_executed",
            "command_id": command.id,
            "drone_id": drone.id,
            "command": command.command
        })
        
    except Exception as e:
        command.status = "failed"
        await manager.broadcast({
            "type": "command_failed",
            "command_id": command.id,
            "drone_id": drone.id,
            "error": str(e)
        })

# API Endpoints
@app.post("/api/drones", response_model=Drone)
async def create_drone(drone: Drone):
    """Register a new drone"""
    drones[drone.id] = drone
    
    # Start drone simulation
    asyncio.create_task(simulate_drone_movement(drone.id))
    
    return drone

@app.get("/api/drones", response_model=List[Drone])
async def get_drones(status: Optional[DroneStatus] = None):
    """Get all drones with optional status filter"""
    filtered_drones = list(drones.values())
    
    if status:
        filtered_drones = [d for d in filtered_drones if d.status == status]
    
    return filtered_drones

@app.get("/api/drones/{drone_id}", response_model=Drone)
async def get_drone(drone_id: str):
    """Get specific drone information"""
    if drone_id not in drones:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drones[drone_id]

@app.post("/api/drones/{drone_id}/commands", response_model=FlightCommand)
async def send_command(drone_id: str, command: FlightCommand):
    """Send command to drone"""
    if drone_id not in drones:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    command.drone_id = drone_id
    command.id = f"cmd_{uuid.uuid4().hex[:8]}"
    command.created_at = datetime.now()
    
    flight_commands[command.id] = command
    
    # Execute command asynchronously
    asyncio.create_task(execute_flight_command(command))
    
    return command

@app.get("/api/drones/{drone_id}/commands", response_model=List[FlightCommand])
async def get_drone_commands(drone_id: str, limit: int = 50):
    """Get command history for drone"""
    commands = [cmd for cmd in flight_commands.values() if cmd.drone_id == drone_id]
    return sorted(commands, key=lambda x: x.created_at, reverse=True)[:limit]

@app.post("/api/flight-plans", response_model=FlightPlan)
async def create_flight_plan(flight_plan: FlightPlan):
    """Create a new flight plan"""
    # Calculate metrics
    distance, duration = calculate_flight_plan_metrics(flight_plan.waypoints)
    flight_plan.total_distance = distance
    flight_plan.estimated_duration = duration
    
    flight_plans[flight_plan.id] = flight_plan
    return flight_plan

@app.get("/api/flight-plans", response_model=List[FlightPlan])
async def get_flight_plans(drone_id: Optional[str] = None):
    """Get all flight plans with optional drone filter"""
    plans = list(flight_plans.values())
    
    if drone_id:
        plans = [p for p in plans if p.drone_id == drone_id]
    
    return plans

@app.post("/api/flight-plans/{plan_id}/execute")
async def execute_flight_plan(plan_id: str):
    """Execute a flight plan"""
    if plan_id not in flight_plans:
        raise HTTPException(status_code=404, detail="Flight plan not found")
    
    plan = flight_plans[plan_id]
    drone = drones.get(plan.drone_id)
    
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    if drone.status != DroneStatus.IDLE:
        raise HTTPException(status_code=400, detail="Drone not ready for flight")
    
    # Execute waypoints sequentially
    plan.is_active = True
    
    for waypoint in plan.waypoints:
        # Send goto command for each waypoint
        command = FlightCommand(
            id=f"cmd_{uuid.uuid4().hex[:8]}",
            drone_id=drone.id,
            command="goto",
            parameters={
                "latitude": waypoint.position.latitude,
                "longitude": waypoint.position.longitude,
                "altitude": waypoint.altitude,
                "speed": waypoint.speed
            },
            priority="normal",
            created_at=datetime.now()
        )
        
        await execute_flight_command(command)
        
        # Wait for waypoint to be reached (simplified)
        await asyncio.sleep(5)  # Would need proper waypoint detection
        
        # Execute waypoint action if specified
        if waypoint.action:
            await manager.broadcast({
                "type": "waypoint_action",
                "drone_id": drone.id,
                "action": waypoint.action
            })
    
    plan.is_active = False
    return {"message": "Flight plan executed successfully"}

@app.get("/api/drones/{drone_id}/logs", response_model=List[FlightLog])
async def get_flight_logs(drone_id: str, limit: int = 100):
    """Get flight logs for drone"""
    if drone_id not in flight_logs:
        return []
    
    return sorted(flight_logs[drone_id], key=lambda x: x.timestamp, reverse=True)[:limit]

@app.post("/api/no-fly-zones", response_model=NoFlyZone)
async def create_no_fly_zone(zone: NoFlyZone):
    """Create a no-fly zone"""
    no_fly_zones[zone.id] = zone
    return zone

@app.get("/api/no-fly-zones", response_model=List[NoFlyZone])
async def get_no_fly_zones():
    """Get all no-fly zones"""
    return list(no_fly_zones.values())

@app.get("/api/stats")
async def get_stats():
    """Get drone fleet statistics"""
    total_drones = len(drones)
    flying_drones = len([d for d in drones.values() if d.status == DroneStatus.FLYING])
    idle_drones = len([d for d in drones.values() if d.status == DroneStatus.IDLE])
    emergency_drones = len([d for d in drones.values() if d.status == DroneStatus.EMERGENCY])
    
    # Battery statistics
    avg_battery = sum(d.battery.percentage for d in drones.values()) / total_drones if total_drones > 0 else 0
    low_battery_drones = len([d for d in drones.values() if d.battery.percentage < 20])
    
    # Flight statistics
    total_flights = sum(len(logs) for logs in flight_logs.values())
    active_flight_plans = len([p for p in flight_plans.values() if p.is_active])
    
    return {
        "total_drones": total_drones,
        "flying_drones": flying_drones,
        "idle_drones": idle_drones,
        "emergency_drones": emergency_drones,
        "average_battery": avg_battery,
        "low_battery_drones": low_battery_drones,
        "total_flights": total_flights,
        "active_flight_plans": active_flight_plans,
        "no_fly_zones": len(no_fly_zones),
        "supported_commands": ["takeoff", "land", "goto", "orbit", "emergency_land"],
        "flight_modes": [mode.value for mode in FlightMode]
    }

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages
            if message.get("type") == "subscribe_telemetry":
                drone_id = message.get("drone_id")
                if drone_id in drones:
                    # Send current telemetry
                    drone = drones[drone_id]
                    await manager.send_to_client(client_id, {
                        "type": "telemetry_update",
                        "drone_id": drone_id,
                        "position": drone.position.dict(),
                        "battery": drone.battery.dict(),
                        "status": drone.status.value
                    })
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.get("/")
async def root():
    return {"message": "Drone Flight Control API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
