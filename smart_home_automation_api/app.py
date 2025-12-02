from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
import random

app = FastAPI(title="Smart Home Automation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class DeviceType(str, Enum):
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    DOOR_LOCK = "door_lock"
    SECURITY_CAMERA = "security_camera"
    MOTION_SENSOR = "motion_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    SMART_SWITCH = "smart_switch"
    SMART_PLUG = "smart_plug"
    SMOKE_DETECTOR = "smoke_detector"
    WATER_LEAK_SENSOR = "water_leak_sensor"
    GARAGE_DOOR = "garage_door"
    WINDOW_COVERING = "window_covering"
    SPEAKER = "speaker"
    TV = "tv"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    ERROR = "error"

class AutomationTriggerType(str, Enum):
    TIME = "time"
    DEVICE_STATE = "device_state"
    SENSOR_VALUE = "sensor_value"
    LOCATION = "location"
    WEATHER = "weather"
    MANUAL = "manual"

class AutomationActionType(str, Enum):
    DEVICE_CONTROL = "device_control"
    NOTIFICATION = "notification"
    SCENE_ACTIVATION = "scene_activation"
    EMAIL = "email"
    WEBHOOK = "webhook"

# Data models
class Device(BaseModel):
    id: str
    name: str
    device_type: DeviceType
    room: str
    manufacturer: str
    model: str
    firmware_version: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: DeviceStatus
    last_seen: datetime
    properties: Dict[str, Any] = {}
    capabilities: List[str] = []
    created_at: datetime
    updated_at: datetime

class Room(BaseModel):
    id: str
    name: str
    description: str
    devices: List[str] = []  # Device IDs
    created_at: datetime
    updated_at: datetime

class Scene(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    actions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    is_active: bool = False

class Automation(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool
    trigger_type: AutomationTriggerType
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

class SensorReading(BaseModel):
    id: str
    device_id: str
    sensor_type: str
    value: Union[int, float, str, bool]
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class Notification(BaseModel):
    id: str
    title: str
    message: str
    type: str  # "info", "warning", "error", "success"
    priority: str  # "low", "medium", "high", "critical"
    device_id: Optional[str] = None
    automation_id: Optional[str] = None
    created_at: datetime
    read: bool = False
    read_at: Optional[datetime] = None

class EnergyUsage(BaseModel):
    id: str
    device_id: str
    power_consumption: float  # watts
    energy_consumed: float  # kilowatt-hours
    cost: float  # currency value
    timestamp: datetime
    duration: int  # minutes

class UserPreference(BaseModel):
    id: str
    user_id: str
    key: str
    value: Any
    category: str  # "lighting", "security", "climate", "general"
    created_at: datetime
    updated_at: datetime

# In-memory storage
devices: Dict[str, Device] = {}
rooms: Dict[str, Room] = {}
scenes: Dict[str, Scene] = {}
automations: Dict[str, Automation] = {}
sensor_readings: Dict[str, List[SensorReading]] = {}
notifications: Dict[str, Notification] = {}
energy_usage: Dict[str, List[EnergyUsage]] = {}
user_preferences: Dict[str, UserPreference] = {}
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
def generate_device_id() -> str:
    """Generate unique device ID"""
    return f"device_{uuid.uuid4().hex[:8]}"

def generate_room_id() -> str:
    """Generate unique room ID"""
    return f"room_{uuid.uuid4().hex[:8]}"

def generate_scene_id() -> str:
    """Generate unique scene ID"""
    return f"scene_{uuid.uuid4().hex[:8]}"

def generate_automation_id() -> str:
    """Generate unique automation ID"""
    return f"automation_{uuid.uuid4().hex[:8]}"

def generate_notification_id() -> str:
    """Generate unique notification ID"""
    return f"notification_{uuid.uuid4().hex[:8]}"

async def send_device_state_change(device_id: str, property_name: str, old_value: Any, new_value: Any):
    """Send device state change notification via WebSocket"""
    message = {
        "type": "device_state_change",
        "device_id": device_id,
        "property": property_name,
        "old_value": old_value,
        "new_value": new_value,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)

async def send_notification(title: str, message: str, notification_type: str = "info", priority: str = "medium", device_id: Optional[str] = None, automation_id: Optional[str] = None):
    """Create and send notification"""
    notification_id = generate_notification_id()
    
    notification = Notification(
        id=notification_id,
        title=title,
        message=message,
        type=notification_type,
        priority=priority,
        device_id=device_id,
        automation_id=automation_id,
        created_at=datetime.now()
    )
    
    notifications[notification_id] = notification
    
    # Send via WebSocket
    ws_message = {
        "type": "notification",
        "notification": notification.dict(),
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(ws_message)

async def execute_automation_actions(actions: List[Dict[str, Any]], automation_id: str):
    """Execute automation actions"""
    for action in actions:
        action_type = action.get("type")
        
        if action_type == AutomationActionType.DEVICE_CONTROL:
            await control_device_action(action)
        elif action_type == AutomationActionType.NOTIFICATION:
            await send_notification(
                title=action.get("title", "Automation Triggered"),
                message=action.get("message", "An automation was triggered"),
                notification_type=action.get("type", "info"),
                priority=action.get("priority", "medium"),
                automation_id=automation_id
            )
        elif action_type == AutomationActionType.SCENE_ACTIVATION:
            await activate_scene_action(action)
        elif action_type == AutomationActionType.WEBHOOK:
            await trigger_webhook_action(action)

async def control_device_action(action: Dict[str, Any]):
    """Execute device control action"""
    device_id = action.get("device_id")
    command = action.get("command")
    parameters = action.get("parameters", {})
    
    if device_id not in devices:
        return
    
    device = devices[device_id]
    
    # Update device properties
    for param, value in parameters.items():
        if param in device.properties:
            old_value = device.properties[param]
            device.properties[param] = value
            device.updated_at = datetime.now()
            
            # Send state change notification
            await send_device_state_change(device_id, param, old_value, value)

async def activate_scene_action(action: Dict[str, Any]):
    """Execute scene activation action"""
    scene_id = action.get("scene_id")
    
    if scene_id not in scenes:
        return
    
    scene = scenes[scene_id]
    
    # Execute all scene actions
    await execute_automation_actions(scene.actions, "scene")

async def trigger_webhook_action(action: Dict[str, Any]):
    """Execute webhook action"""
    # Mock webhook implementation
    webhook_url = action.get("url")
    method = action.get("method", "POST")
    payload = action.get("payload", {})
    
    print(f"Webhook triggered: {method} {webhook_url} with payload: {payload}")

async def check_automations():
    """Check and trigger automations based on conditions"""
    now = datetime.now()
    
    for automation in automations.values():
        if not automation.enabled:
            continue
        
        triggered = False
        
        if automation.trigger_type == AutomationTriggerType.TIME:
            # Check time-based triggers
            trigger_time = automation.trigger_config.get("time")
            if trigger_time:
                # Simple time check (in reality, would be more sophisticated)
                if now.strftime("%H:%M") == trigger_time:
                    triggered = True
        
        elif automation.trigger_type == AutomationTriggerType.DEVICE_STATE:
            # Check device state triggers
            device_id = automation.trigger_config.get("device_id")
            property_name = automation.trigger_config.get("property")
            expected_value = automation.trigger_config.get("value")
            
            if device_id in devices:
                device = devices[device_id]
                current_value = device.properties.get(property_name)
                
                if current_value == expected_value:
                    triggered = True
        
        elif automation.trigger_type == AutomationTriggerType.SENSOR_VALUE:
            # Check sensor value triggers
            device_id = automation.trigger_config.get("device_id")
            sensor_type = automation.trigger_config.get("sensor_type")
            condition = automation.trigger_config.get("condition")
            threshold = automation.trigger_config.get("threshold")
            
            if device_id in sensor_readings:
                readings = sensor_readings[device_id]
                if readings:
                    latest_reading = readings[-1]
                    if latest_reading.sensor_type == sensor_type:
                        value = latest_reading.value
                        
                        if condition == "greater_than" and value > threshold:
                            triggered = True
                        elif condition == "less_than" and value < threshold:
                            triggered = True
                        elif condition == "equals" and value == threshold:
                            triggered = True
        
        if triggered:
            await execute_automation_actions(automation.actions, automation.id)
            automation.last_triggered = now
            automation.trigger_count += 1

# Background task for automation checking
async def automation_checker():
    """Background task to check automations"""
    while True:
        await check_automations()
        await asyncio.sleep(30)  # Check every 30 seconds

# Start background task
asyncio.create_task(automation_checker())

# API Endpoints
@app.post("/api/devices", response_model=Device)
async def add_device(
    name: str,
    device_type: DeviceType,
    room: str,
    manufacturer: str,
    model: str,
    firmware_version: str,
    ip_address: Optional[str] = None,
    mac_address: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    capabilities: Optional[List[str]] = None
):
    """Add a new smart home device"""
    device_id = generate_device_id()
    
    device = Device(
        id=device_id,
        name=name,
        device_type=device_type,
        room=room,
        manufacturer=manufacturer,
        model=model,
        firmware_version=firmware_version,
        ip_address=ip_address,
        mac_address=mac_address,
        status=DeviceStatus.ONLINE,
        last_seen=datetime.now(),
        properties=properties or {},
        capabilities=capabilities or [],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    devices[device_id] = device
    
    # Initialize sensor readings storage
    if device_type in [DeviceType.TEMPERATURE_SENSOR, DeviceType.HUMIDITY_SENSOR, DeviceType.MOTION_SENSOR]:
        sensor_readings[device_id] = []
    
    # Initialize energy usage tracking
    if device_type in [DeviceType.LIGHT, DeviceType.THERMOSTAT, DeviceType.SMART_PLUG]:
        energy_usage[device_id] = []
    
    await send_notification(
        title="Device Added",
        message=f"New {device_type.value} '{name}' added to {room}",
        notification_type="info",
        device_id=device_id
    )
    
    return device

@app.get("/api/devices", response_model=List[Device])
async def get_devices(
    room: Optional[str] = None,
    device_type: Optional[DeviceType] = None,
    status: Optional[DeviceStatus] = None
):
    """Get devices with optional filters"""
    filtered_devices = list(devices.values())
    
    if room:
        filtered_devices = [d for d in filtered_devices if d.room == room]
    
    if device_type:
        filtered_devices = [d for d in filtered_devices if d.device_type == device_type]
    
    if status:
        filtered_devices = [d for d in filtered_devices if d.status == status]
    
    return filtered_devices

@app.get("/api/devices/{device_id}", response_model=Device)
async def get_device(device_id: str):
    """Get specific device"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@app.post("/api/devices/{device_id}/control")
async def control_device(device_id: str, command: str, parameters: Dict[str, Any]):
    """Control a device"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices[device_id]
    
    if device.status != DeviceStatus.ONLINE:
        raise HTTPException(status_code=400, detail="Device is not online")
    
    # Validate command based on device type and capabilities
    valid_commands = {
        DeviceType.LIGHT: ["turn_on", "turn_off", "set_brightness", "set_color"],
        DeviceType.THERMOSTAT: ["set_temperature", "set_mode", "turn_on", "turn_off"],
        DeviceType.DOOR_LOCK: ["lock", "unlock"],
        DeviceType.SMART_SWITCH: ["turn_on", "turn_off"],
        DeviceType.SMART_PLUG: ["turn_on", "turn_off"],
        DeviceType.SPEAKER: ["play", "pause", "set_volume"],
        DeviceType.TV: ["turn_on", "turn_off", "set_channel", "set_volume"],
        DeviceType.GARAGE_DOOR: ["open", "close"],
        DeviceType.WINDOW_COVERING: ["open", "close", "set_position"]
    }
    
    if command not in valid_commands.get(device.device_type, []):
        raise HTTPException(status_code=400, detail=f"Invalid command for {device.device_type.value}")
    
    # Execute command
    old_values = {}
    for param, value in parameters.items():
        if param in device.properties:
            old_values[param] = device.properties[param]
            device.properties[param] = value
    
    device.updated_at = datetime.now()
    
    # Send notifications for state changes
    for param, old_value in old_values.items():
        await send_device_state_change(device_id, param, old_value, parameters[param])
    
    await send_notification(
        title="Device Controlled",
        message=f"{device.name} in {device.room} - {command}",
        notification_type="info",
        device_id=device_id
    )
    
    return {"message": f"Command '{command}' executed successfully", "device_state": device.properties}

@app.delete("/api/devices/{device_id}")
async def remove_device(device_id: str):
    """Remove a device"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices[device_id]
    
    # Clean up related data
    if device_id in sensor_readings:
        del sensor_readings[device_id]
    
    if device_id in energy_usage:
        del energy_usage[device_id]
    
    del devices[device_id]
    
    await send_notification(
        title="Device Removed",
        message=f"{device.name} removed from {device.room}",
        notification_type="info"
    )
    
    return {"message": "Device removed successfully"}

@app.post("/api/rooms", response_model=Room)
async def create_room(name: str, description: str):
    """Create a new room"""
    room_id = generate_room_id()
    
    room = Room(
        id=room_id,
        name=name,
        description=description,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    rooms[room_id] = room
    return room

@app.get("/api/rooms", response_model=List[Room])
async def get_rooms():
    """Get all rooms"""
    return list(rooms.values())

@app.post("/api/scenes", response_model=Scene)
async def create_scene(
    name: str,
    description: str,
    icon: str,
    actions: List[Dict[str, Any]]
):
    """Create a new scene"""
    scene_id = generate_scene_id()
    
    scene = Scene(
        id=scene_id,
        name=name,
        description=description,
        icon=icon,
        actions=actions,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    scenes[scene_id] = scene
    return scene

@app.get("/api/scenes", response_model=List[Scene])
async def get_scenes():
    """Get all scenes"""
    return list(scenes.values())

@app.post("/api/scenes/{scene_id}/activate")
async def activate_scene(scene_id: str):
    """Activate a scene"""
    if scene_id not in scenes:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene = scenes[scene_id]
    
    # Execute all scene actions
    await execute_automation_actions(scene.actions, "scene")
    
    scene.is_active = True
    scene.updated_at = datetime.now()
    
    await send_notification(
        title="Scene Activated",
        message=f"Scene '{scene.name}' activated",
        notification_type="success"
    )
    
    return {"message": f"Scene '{scene.name}' activated successfully"}

@app.post("/api/automations", response_model=Automation)
async def create_automation(
    name: str,
    description: str,
    trigger_type: AutomationTriggerType,
    trigger_config: Dict[str, Any],
    actions: List[Dict[str, Any]]
):
    """Create a new automation"""
    automation_id = generate_automation_id()
    
    automation = Automation(
        id=automation_id,
        name=name,
        description=description,
        enabled=True,
        trigger_type=trigger_type,
        trigger_config=trigger_config,
        actions=actions,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    automations[automation_id] = automation
    return automation

@app.get("/api/automations", response_model=List[Automation])
async def get_automations(enabled_only: bool = False):
    """Get automations"""
    filtered_automations = list(automations.values())
    
    if enabled_only:
        filtered_automations = [a for a in filtered_automations if a.enabled]
    
    return filtered_automations

@app.post("/api/automations/{automation_id}/toggle")
async def toggle_automation(automation_id: str):
    """Toggle automation enabled/disabled"""
    if automation_id not in automations:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    automation = automations[automation_id]
    automation.enabled = not automation.enabled
    automation.updated_at = datetime.now()
    
    return {"message": f"Automation {'enabled' if automation.enabled else 'disabled'}"}

@app.post("/api/sensor-readings/{device_id}")
async def add_sensor_reading(
    device_id: str,
    sensor_type: str,
    value: Union[int, float, str, bool],
    unit: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Add sensor reading"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    reading_id = generate_notification_id()
    
    reading = SensorReading(
        id=reading_id,
        device_id=device_id,
        sensor_type=sensor_type,
        value=value,
        unit=unit,
        timestamp=datetime.now(),
        metadata=metadata or {}
    )
    
    if device_id not in sensor_readings:
        sensor_readings[device_id] = []
    
    sensor_readings[device_id].append(reading)
    
    # Keep only last 1000 readings per device
    if len(sensor_readings[device_id]) > 1000:
        sensor_readings[device_id] = sensor_readings[device_id][-1000:]
    
    # Send WebSocket notification
    message = {
        "type": "sensor_reading",
        "reading": reading.dict(),
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)
    
    return reading

@app.get("/api/sensor-readings/{device_id}", response_model=List[SensorReading])
async def get_sensor_readings(device_id: str, limit: int = 100, hours: int = 24):
    """Get sensor readings for a device"""
    if device_id not in sensor_readings:
        return []
    
    since_time = datetime.now() - timedelta(hours=hours)
    readings = sensor_readings[device_id]
    
    filtered_readings = [r for r in readings if r.timestamp >= since_time]
    
    return sorted(filtered_readings, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.get("/api/notifications", response_model=List[Notification])
async def get_notifications(unread_only: bool = False, limit: int = 50):
    """Get notifications"""
    filtered_notifications = list(notifications.values())
    
    if unread_only:
        filtered_notifications = [n for n in filtered_notifications if not n.read]
    
    return sorted(filtered_notifications, key=lambda x: x.created_at, reverse=True)[:limit]

@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    if notification_id not in notifications:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification = notifications[notification_id]
    notification.read = True
    notification.read_at = datetime.now()
    
    return {"message": "Notification marked as read"}

@app.post("/api/energy-usage/{device_id}")
async def add_energy_usage(
    device_id: str,
    power_consumption: float,
    energy_consumed: float,
    cost: float,
    duration: int
):
    """Add energy usage data"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    usage_id = generate_notification_id()
    
    usage = EnergyUsage(
        id=usage_id,
        device_id=device_id,
        power_consumption=power_consumption,
        energy_consumed=energy_consumed,
        cost=cost,
        timestamp=datetime.now(),
        duration=duration
    )
    
    if device_id not in energy_usage:
        energy_usage[device_id] = []
    
    energy_usage[device_id].append(usage)
    
    return usage

@app.get("/api/energy-usage/{device_id}", response_model=List[EnergyUsage])
async def get_energy_usage(device_id: str, days: int = 7):
    """Get energy usage for a device"""
    if device_id not in energy_usage:
        return []
    
    since_date = datetime.now() - timedelta(days=days)
    usage_data = energy_usage[device_id]
    
    filtered_usage = [u for u in usage_data if u.timestamp >= since_date]
    
    return sorted(filtered_usage, key=lambda x: x.timestamp, reverse=True)

@app.get("/api/stats")
async def get_smart_home_stats():
    """Get smart home system statistics"""
    total_devices = len(devices)
    total_rooms = len(rooms)
    total_scenes = len(scenes)
    total_automations = len(automations)
    total_notifications = len(notifications)
    
    # Device type distribution
    device_type_distribution = {}
    for device in devices.values():
        device_type = device.device_type.value
        device_type_distribution[device_type] = device_type_distribution.get(device_type, 0) + 1
    
    # Device status distribution
    status_distribution = {}
    for device in devices.values():
        status = device.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Room distribution
    room_device_count = {}
    for device in devices.values():
        room = device.room
        room_device_count[room] = room_device_count.get(room, 0) + 1
    
    # Active automations
    active_automations = len([a for a in automations.values() if a.enabled])
    
    # Recent activity
    recent_notifications = len([n for n in notifications.values() if n.created_at > datetime.now() - timedelta(hours=24)])
    
    return {
        "total_devices": total_devices,
        "total_rooms": total_rooms,
        "total_scenes": total_scenes,
        "total_automations": total_automations,
        "active_automations": active_automations,
        "total_notifications": total_notifications,
        "recent_notifications_24h": recent_notifications,
        "device_type_distribution": device_type_distribution,
        "status_distribution": status_distribution,
        "room_device_count": room_device_count,
        "supported_device_types": [t.value for t in DeviceType],
        "supported_trigger_types": [t.value for t in AutomationTriggerType]
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
            if message.get("type") == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
            
            elif message.get("type") == "subscribe_device":
                device_id = message.get("device_id")
                # In a real implementation, would subscribe to specific device updates
                await manager.send_to_client(client_id, {
                    "type": "subscribed",
                    "device_id": device_id
                })
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.get("/")
async def root():
    return {"message": "Smart Home Automation API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
