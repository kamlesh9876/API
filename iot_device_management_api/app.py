from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import json
import uuid
from datetime import datetime, timedelta
import random

app = FastAPI(title="IoT Device Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Device(BaseModel):
    id: str
    name: str
    type: str  # "sensor", "actuator", "camera", "thermostat", "light", "lock"
    manufacturer: str
    model: str
    location: str
    status: str  # "online", "offline", "maintenance", "error"
    last_seen: datetime
    firmware_version: str
    battery_level: Optional[int] = None  # 0-100
    signal_strength: Optional[int] = None  # 0-100
    configuration: Dict[str, Any] = {}

class SensorReading(BaseModel):
    device_id: str
    timestamp: datetime
    reading_type: str  # "temperature", "humidity", "motion", "light", "pressure"
    value: float
    unit: str
    metadata: Optional[Dict[str, Any]] = {}

class DeviceCommand(BaseModel):
    device_id: str
    command: str
    parameters: Dict[str, Any] = {}
    priority: str = "normal"  # "low", "normal", "high", "urgent"

class DeviceAlert(BaseModel):
    id: str
    device_id: str
    alert_type: str  # "offline", "low_battery", "malfunction", "security"
    message: str
    severity: str  # "info", "warning", "error", "critical"
    timestamp: datetime
    is_resolved: bool = False

class AutomationRule(BaseModel):
    id: str
    name: str
    description: str
    trigger_condition: Dict[str, Any]
    action: Dict[str, Any]
    is_active: bool = True
    created_at: datetime

# In-memory storage
devices: Dict[str, Device] = {}
sensor_readings: Dict[str, List[SensorReading]] = {}
device_commands: Dict[str, List[DeviceCommand]] = {}
device_alerts: Dict[str, DeviceAlert] = {}
automation_rules: Dict[str, AutomationRule] = {}
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

def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return f"alert_{uuid.uuid4().hex[:8]}"

def check_device_health(device: Device) -> List[DeviceAlert]:
    """Check device health and generate alerts"""
    alerts = []
    
    # Check if device is offline
    if device.status == "offline":
        if datetime.now() - device.last_seen > timedelta(minutes=5):
            alerts.append(DeviceAlert(
                id=generate_alert_id(),
                device_id=device.id,
                alert_type="offline",
                message=f"Device {device.name} has been offline for more than 5 minutes",
                severity="warning",
                timestamp=datetime.now()
            ))
    
    # Check battery level
    if device.battery_level is not None and device.battery_level < 20:
        alerts.append(DeviceAlert(
            id=generate_alert_id(),
            device_id=device.id,
            alert_type="low_battery",
            message=f"Device {device.name} battery level is {device.battery_level}%",
            severity="warning" if device.battery_level > 10 else "critical",
            timestamp=datetime.now()
        ))
    
    # Check signal strength
    if device.signal_strength is not None and device.signal_strength < 30:
        alerts.append(DeviceAlert(
            id=generate_alert_id(),
            device_id=device.id,
            alert_type="malfunction",
            message=f"Device {device.name} has poor signal strength ({device.signal_strength}%)",
            severity="info",
            timestamp=datetime.now()
        ))
    
    return alerts

async def simulate_device_data(device: Device):
    """Simulate IoT device data generation"""
    while device.status == "online":
        # Generate sensor readings based on device type
        if device.type == "sensor":
            reading_types = ["temperature", "humidity", "motion", "light"]
            reading_type = random.choice(reading_types)
            
            if reading_type == "temperature":
                value = random.uniform(18.0, 28.0)
                unit = "°C"
            elif reading_type == "humidity":
                value = random.uniform(30.0, 70.0)
                unit = "%"
            elif reading_type == "motion":
                value = random.choice([0, 1])
                unit = "binary"
            else:  # light
                value = random.uniform(0, 1000)
                unit = "lux"
            
            reading = SensorReading(
                device_id=device.id,
                timestamp=datetime.now(),
                reading_type=reading_type,
                value=value,
                unit=unit
            )
            
            if device.id not in sensor_readings:
                sensor_readings[device.id] = []
            sensor_readings[device.id].append(reading)
            
            # Broadcast new reading
            await manager.broadcast({
                "type": "sensor_reading",
                "device_id": device.id,
                "reading": reading.dict()
            })
        
        # Update device status
        device.last_seen = datetime.now()
        if device.battery_level is not None:
            device.battery_level = max(0, device.battery_level - random.randint(0, 2))
        if device.signal_strength is not None:
            device.signal_strength = max(0, min(100, device.signal_strength + random.randint(-5, 5)))
        
        # Check for alerts
        new_alerts = check_device_health(device)
        for alert in new_alerts:
            device_alerts[alert.id] = alert
            await manager.broadcast({
                "type": "alert",
                "alert": alert.dict()
            })
        
        await asyncio.sleep(random.randint(10, 30))

async def execute_automation_rules():
    """Execute automation rules based on sensor readings"""
    while True:
        for rule in automation_rules.values():
            if not rule.is_active:
                continue
            
            # Check trigger conditions
            trigger_met = False
            for device_id, readings in sensor_readings.items():
                if not readings:
                    continue
                
                latest_reading = readings[-1]
                condition = rule.trigger_condition
                
                if condition.get("device_id") == device_id:
                    if condition.get("reading_type") == latest_reading.reading_type:
                        operator = condition.get("operator", "equals")
                        threshold = condition.get("value", 0)
                        
                        if operator == "greater_than" and latest_reading.value > threshold:
                            trigger_met = True
                        elif operator == "less_than" and latest_reading.value < threshold:
                            trigger_met = True
                        elif operator == "equals" and latest_reading.value == threshold:
                            trigger_met = True
            
            # Execute action if trigger is met
            if trigger_met:
                action = rule.action
                target_device_id = action.get("device_id")
                
                if target_device_id in devices:
                    command = DeviceCommand(
                        device_id=target_device_id,
                        command=action.get("command", "update"),
                        parameters=action.get("parameters", {}),
                        priority="normal"
                    )
                    
                    if target_device_id not in device_commands:
                        device_commands[target_device_id] = []
                    device_commands[target_device_id].append(command)
                    
                    await manager.broadcast({
                        "type": "automation_executed",
                        "rule_id": rule.id,
                        "command": command.dict()
                    })
        
        await asyncio.sleep(10)

# API Endpoints
@app.post("/api/devices", response_model=Device)
async def create_device(device: Device):
    """Create a new IoT device"""
    devices[device.id] = device
    
    # Start device simulation
    asyncio.create_task(simulate_device_data(device))
    
    return device

@app.get("/api/devices", response_model=List[Device])
async def get_devices(status: Optional[str] = None, device_type: Optional[str] = None):
    """Get all devices with optional filters"""
    filtered_devices = list(devices.values())
    
    if status:
        filtered_devices = [d for d in filtered_devices if d.status == status]
    if device_type:
        filtered_devices = [d for d in filtered_devices if d.type == device_type]
    
    return filtered_devices

@app.get("/api/devices/{device_id}", response_model=Device)
async def get_device(device_id: str):
    """Get specific device information"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[device_id]

@app.put("/api/devices/{device_id}", response_model=Device)
async def update_device(device_id: str, device_update: Dict[str, Any]):
    """Update device information"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices[device_id]
    for key, value in device_update.items():
        if hasattr(device, key):
            setattr(device, key, value)
    
    return device

@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str):
    """Delete a device"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    del devices[device_id]
    # Clean up related data
    if device_id in sensor_readings:
        del sensor_readings[device_id]
    if device_id in device_commands:
        del device_commands[device_id]
    
    return {"message": "Device deleted successfully"}

@app.post("/api/devices/{device_id}/commands", response_model=DeviceCommand)
async def send_command(device_id: str, command: DeviceCommand):
    """Send command to device"""
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device_id not in device_commands:
        device_commands[device_id] = []
    
    device_commands[device_id].append(command)
    
    # Broadcast command
    await manager.broadcast({
        "type": "command_sent",
        "device_id": device_id,
        "command": command.dict()
    })
    
    return command

@app.get("/api/devices/{device_id}/readings", response_model=List[SensorReading])
async def get_sensor_readings(device_id: str, limit: int = 100, reading_type: Optional[str] = None):
    """Get sensor readings for a device"""
    if device_id not in sensor_readings:
        return []
    
    readings = sensor_readings[device_id]
    
    if reading_type:
        readings = [r for r in readings if r.reading_type == reading_type]
    
    return sorted(readings, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.get("/api/devices/{device_id}/commands", response_model=List[DeviceCommand])
async def get_device_commands(device_id: str, limit: int = 50):
    """Get command history for a device"""
    if device_id not in device_commands:
        return []
    
    return device_commands[device_id][-limit:]

@app.get("/api/alerts", response_model=List[DeviceAlert])
async def get_alerts(resolved: Optional[bool] = None, severity: Optional[str] = None):
    """Get all device alerts"""
    filtered_alerts = list(device_alerts.values())
    
    if resolved is not None:
        filtered_alerts = [a for a in filtered_alerts if a.is_resolved == resolved]
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
    
    return sorted(filtered_alerts, key=lambda x: x.timestamp, reverse=True)

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    if alert_id not in device_alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    device_alerts[alert_id].is_resolved = True
    return {"message": "Alert resolved successfully"}

@app.post("/api/automation-rules", response_model=AutomationRule)
async def create_automation_rule(rule: AutomationRule):
    """Create an automation rule"""
    automation_rules[rule.id] = rule
    return rule

@app.get("/api/automation-rules", response_model=List[AutomationRule])
async def get_automation_rules():
    """Get all automation rules"""
    return list(automation_rules.values())

@app.put("/api/automation-rules/{rule_id}")
async def update_automation_rule(rule_id: str, rule_update: Dict[str, Any]):
    """Update an automation rule"""
    if rule_id not in automation_rules:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    rule = automation_rules[rule_id]
    for key, value in rule_update.items():
        if hasattr(rule, key):
            setattr(rule, key, value)
    
    return {"message": "Automation rule updated successfully"}

@app.delete("/api/automation-rules/{rule_id}")
async def delete_automation_rule(rule_id: str):
    """Delete an automation rule"""
    if rule_id not in automation_rules:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    
    del automation_rules[rule_id]
    return {"message": "Automation rule deleted successfully"}

@app.get("/api/stats")
async def get_stats():
    """Get IoT system statistics"""
    return {
        "total_devices": len(devices),
        "online_devices": len([d for d in devices.values() if d.status == "online"]),
        "offline_devices": len([d for d in devices.values() if d.status == "offline"]),
        "total_readings": sum(len(readings) for readings in sensor_readings.values()),
        "unresolved_alerts": len([a for a in device_alerts.values() if not a.is_resolved]),
        "active_automation_rules": len([r for r in automation_rules.values() if r.is_active]),
        "device_types": list(set(d.type for d in devices.values())),
        "alert_distribution": {
            severity: len([a for a in device_alerts.values() if a.severity == severity])
            for severity in ["info", "warning", "error", "critical"]
        }
    }

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages (device commands, status updates, etc.)
            if message.get("type") == "device_status_update":
                device_id = message.get("device_id")
                if device_id in devices:
                    devices[device_id].status = message.get("status", "online")
                    devices[device_id].last_seen = datetime.now()
                    
                    await manager.broadcast({
                        "type": "device_status_updated",
                        "device_id": device_id,
                        "status": devices[device_id].status
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Start background tasks
@app.on_event("startup")
async def startup_event():
    """Start background automation task"""
    asyncio.create_task(execute_automation_rules())

@app.get("/")
async def root():
    return {"message": "IoT Device Management API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
