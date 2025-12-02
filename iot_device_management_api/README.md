# IoT Device Management API

A comprehensive API for managing IoT devices with real-time monitoring, automation rules, and alerting capabilities.

## Features

- **Device Management**: Add, update, and monitor IoT devices
- **Real-time Monitoring**: WebSocket-based live data streaming
- **Sensor Data Collection**: Temperature, humidity, motion, light sensors
- **Device Commands**: Send commands to actuators and devices
- **Smart Alerts**: Automatic alert generation for device issues
- **Automation Rules**: Create if-then automation based on sensor data
- **Health Monitoring**: Battery level, signal strength, device status tracking
- **Multi-Device Support**: Sensors, actuators, cameras, thermostats, lights, locks

## API Endpoints

### Device Management

#### Create Device
```http
POST /api/devices
Content-Type: application/json

{
  "idame": "Living Room Thermostat",
  "type": "thermostat",
  "manufacturer": "Nest",
  "model": "T3007ES",
  "location": "Living Room",
  "status": "online",
  "firmware_version": "5.9.3",
  "battery_level": 85,
  "signal_strength": 92,
  "configuration": {
    "target_temperature": 22.0,
    "mode": "auto"
  }
}
```

#### Get All Devices
```http
GET /api/devices?status=online&type=sensor
```

#### Get Specific Device
```http
GET /api/devices/{device_id}
```

#### Update Device
```http
PUT /api/devices/{device_id}
Content-Type: application/json

{
  "status": "maintenance",
  "configuration": {
    "target_temperature": 24.0
  }
}
```

#### Delete Device
```http
DELETE /api/devices/{device_id}
```

### Device Commands

#### Send Command
```http
POST /api/devices/{device_id}/commands
Content-Type: application/json

{
  "command": "set_temperature",
  "parameters": {
    "temperature": 23.5
  },
  "priority": "high"
}
```

#### Get Command History
```http
GET /api/devices/{device_id}/commands?limit=50
```

### Sensor Data

#### Get Sensor Readings
```http
GET /api/devices/{device_id}/readings?limit=100&reading_type=temperature
```

### Alerts

#### Get All Alerts
```http
GET /api/alerts?resolved=false&severity=warning
```

#### Resolve Alert
```http
POST /api/alerts/{alert_id}/resolve
```

### Automation Rules

#### Create Automation Rule
```http
POST /api/automation-rules
Content-Type: application/json

{
  "id": "temp_control_1",
  "name": "Temperature Control",
  "description": "Turn on AC when temperature > 25°C",
  "trigger_condition": {
    "device_id": "temp_sensor_1",
    "reading_type": "temperature",
    "operator": "greater_than",
    "value": 25.0
  },
  "action": {
    "device_id": "ac_unit_1",
    "command": "turn_on",
    "parameters": {
      "temperature": 22.0
    }
  }
}
```

#### Get Automation Rules
```http
GET /api/automation-rules
```

#### Update Automation Rule
```http
PUT /api/automation-rules/{rule_id}
```

#### Delete Automation Rule
```http
DELETE /api/automation-rules/{rule_id}
```

### Statistics
```http
GET /api/stats
```

## WebSocket Connection

Connect to real-time device updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client123');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

// Send device status update
ws.send(JSON.stringify({
  type: 'device_status_update',
  device_id: 'device_123',
  status: 'online'
}));
```

## Data Models

### Device
```json
{
  "id": "device_123",
  "name": "Living Room Sensor",
  "type": "sensor",
  "manufacturer": "Philips",
  "model": "Hue Sensor",
  "location": "Living Room",
  "status": "online",
  "last_seen": "2024-01-01T12:00:00",
  "firmware_version": "1.2.3",
  "battery_level": 85,
  "signal_strength": 92,
  "configuration": {
    "sensitivity": "medium",
    "update_interval": 30
  }
}
```

### Sensor Reading
```json
{
  "device_id": "device_123",
  "timestamp": "2024-01-01T12:00:00",
  "reading_type": "temperature",
  "value": 23.5,
  "unit": "°C",
  "metadata": {
    "quality": "good",
    "calibrated": true
  }
}
```

### Device Alert
```json
{
  "id": "alert_123",
  "device_id": "device_123",
  "alert_type": "low_battery",
  "message": "Device battery level is 15%",
  "severity": "warning",
  "timestamp": "2024-01-01T12:00:00",
  "is_resolved": false
}
```

### Automation Rule
```json
{
  "id": "rule_123",
  "name": "Smart Lighting",
  "description": "Turn on lights when motion detected",
  "trigger_condition": {
    "device_id": "motion_sensor_1",
    "reading_type": "motion",
    "operator": "equals",
    "value": 1
  },
  "action": {
    "device_id": "light_1",
    "command": "turn_on",
    "parameters": {
      "brightness": 80
    }
  },
  "is_active": true,
  "created_at": "2024-01-01T12:00:00"
}
```

## Supported Device Types

### Sensors
- **Temperature Sensors**: Monitor ambient temperature
- **Humidity Sensors**: Track humidity levels
- **Motion Sensors**: Detect movement and presence
- **Light Sensors**: Measure ambient light levels
- **Pressure Sensors**: Monitor atmospheric pressure

### Actuators
- **Smart Lights**: Control lighting and brightness
- **Smart Locks**: Manage access control
- **Thermostats**: Control heating and cooling
- **Smart Switches**: Control electrical devices
- **Motorized Devices**: Control motors and actuators

### Monitoring Devices
- **Cameras**: Video surveillance and monitoring
- **Door Sensors**: Open/close detection
- **Window Sensors**: Security monitoring
- **Smoke Detectors**: Safety monitoring

## Alert Types

### 1. Offline Alerts
- **Trigger**: Device offline for extended period
- **Severity**: Warning to Critical
- **Action**: Check connectivity and power

### 2. Low Battery Alerts
- **Trigger**: Battery level below threshold
- **Severity**: Warning (20%) to Critical (10%)
- **Action**: Replace or recharge battery

### 3. Malfunction Alerts
- **Trigger**: Poor signal strength, unusual behavior
- **Severity**: Info to Error
- **Action**: Device maintenance

### 4. Security Alerts
- **Trigger**: Unauthorized access, tampering
- **Severity**: Critical
- **Action**: Immediate investigation

## Automation Examples

### Temperature Control
```json
{
  "trigger": {
    "device_id": "temp_sensor",
    "reading_type": "temperature",
    "operator": "greater_than",
    "value": 25.0
  },
  "action": {
    "device_id": "ac_unit",
    "command": "turn_on"
  }
}
```

### Smart Lighting
```json
{
  "trigger": {
    "device_id": "motion_sensor",
    "reading_type": "motion",
    "operator": "equals",
    "value": 1
  },
  "action": {
    "device_id": "smart_light",
    "command": "turn_on",
    "parameters": {
      "brightness": 70
    }
  }
}
```

### Security Monitoring
```json
{
  "trigger": {
    "device_id": "door_sensor",
    "reading_type": "contact",
    "operator": "equals",
    "value": 1
  },
  "action": {
    "device_id": "security_camera",
    "command": "start_recording"
  }
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

# Create a device
device = {
    "id": "temp_sensor_1",
    "name": "Living Room Temperature",
    "type": "sensor",
    "manufacturer": "Philips",
    "model": "Hue Temp Sensor",
    "location": "Living Room",
    "status": "online",
    "firmware_version": "1.0.0"
}

response = requests.post("http://localhost:8000/api/devices", json=device)
print(f"Created device: {response.json()}")

# Get sensor readings
readings = requests.get(f"http://localhost:8000/api/devices/{device['id']}/readings").json()
for reading in readings:
    print(f"{reading['reading_type']}: {reading['value']} {reading['unit']}")
```

### JavaScript Client
```javascript
// Create device
const device = {
  id: 'light_1',
  name: 'Living Room Light',
  type: 'actuator',
  manufacturer: 'Philips',
  model: 'Hue Light',
  location: 'Living Room',
  status: 'online',
  firmware_version: '2.0.0'
};

fetch('http://localhost:8000/api/devices', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(device)
}).then(res => res.json()).then(console.log);

// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/client123');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'sensor_reading') {
    console.log('New reading:', message.reading);
  }
};
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Settings
ALLOWED_ORIGINS=*

# Database (for persistence)
DATABASE_URL=sqlite:///./iot_devices.db

# WebSocket Settings
WEBSOCKET_HEARTBEAT_INTERVAL=30

# Device Settings
DEFAULT_OFFLINE_TIMEOUT=300
LOW_BATTERY_THRESHOLD=20
POOR_SIGNAL_THRESHOLD=30

# Logging
LOG_LEVEL=info
```

## Use Cases

- **Smart Home**: Manage home automation devices
- **Industrial IoT**: Monitor manufacturing equipment
- **Agriculture**: Track environmental conditions
- **Healthcare**: Monitor medical devices
- **Building Management**: Control building systems
- **Security Systems**: Manage security devices

## Advanced Features

### Device Groups
- Organize devices by location or function
- Apply settings to entire groups
- Group-based automation rules

### Scheduled Tasks
- Time-based device control
- Periodic maintenance tasks
- Energy-saving schedules

### Analytics Dashboard
- Device performance metrics
- Energy consumption tracking
- Usage pattern analysis

### Integration Support
- MQTT protocol support
- Third-party device integration
- Cloud platform connectivity

## Production Considerations

- **Database Integration**: PostgreSQL for device storage
- **Message Queuing**: Redis/RabbitMQ for command queuing
- **Security**: Device authentication and encryption
- **Scalability**: Horizontal scaling support
- **Monitoring**: System health and performance metrics
- **Backup**: Device configuration and data backup
