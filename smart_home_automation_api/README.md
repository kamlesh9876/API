# Smart Home Automation API

A comprehensive smart home automation platform for device management, scene control, automation rules, and real-time monitoring with WebSocket support.

## Features

- **Device Management**: Add, control, and monitor smart home devices
- **Room Organization**: Organize devices by rooms and locations
- **Scene Control**: Create and activate custom scenes for multiple devices
- **Automation Rules**: Set up triggers and actions for automated control
- **Real-time Monitoring**: Live sensor readings and device status updates
- **Energy Tracking**: Monitor energy consumption and costs
- **Notifications**: System notifications and alerts
- **WebSocket Support**: Real-time updates and live monitoring
- **Multi-Device Support**: Lights, thermostats, locks, sensors, and more

## API Endpoints

### Device Management

#### Add Device
```http
POST /api/devices
Content-Type: application/json

{
  "name": "Living Room Light",
  "device_type": "light",
  "room": "Living Room",
  "manufacturer": "Philips",
  "model": "Hue White",
  "firmware_version": "1.2.3",
  "ip_address": "192.168.1.100",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "properties": {
    "brightness": 75,
    "color": "#FFFFFF",
    "power": true
  },
  "capabilities": ["dimming", "color_control", "on_off"]
}
```

#### Get Devices
```http
GET /api/devices?room=Living%20Room&device_type=light&status=online
```

#### Get Specific Device
```http
GET /api/devices/{device_id}
```

#### Control Device
```http
POST /api/devices/{device_id}/control
Content-Type: application/json

{
  "command": "set_brightness",
  "parameters": {
    "brightness": 80,
    "color": "#FF6B6B"
  }
}
```

#### Remove Device
```http
DELETE /api/devices/{device_id}
```

### Room Management

#### Create Room
```http
POST /api/rooms
Content-Type: application/json

{
  "name": "Master Bedroom",
  "description": "Main bedroom with ensuite bathroom"
}
```

#### Get Rooms
```http
GET /api/rooms
```

### Scene Management

#### Create Scene
```http
POST /api/scenes
Content-Type: application/json

{
  "name": "Movie Night",
  "description": "Dim lights and turn on TV for movie watching",
  "icon": "movie",
  "actions": [
    {
      "type": "device_control",
      "device_id": "device_123",
      "command": "set_brightness",
      "parameters": {"brightness": 20}
    },
    {
      "type": "device_control",
      "device_id": "device_456",
      "command": "turn_on",
      "parameters": {}
    }
  ]
}
```

#### Get Scenes
```http
GET /api/scenes
```

#### Activate Scene
```http
POST /api/scenes/{scene_id}/activate
```

### Automation Management

#### Create Automation
```http
POST /api/automations
Content-Type: application/json

{
  "name": "Sunset Lights",
  "description": "Turn on lights at sunset",
  "trigger_type": "time",
  "trigger_config": {
    "time": "18:30",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  },
  "actions": [
    {
      "type": "device_control",
      "device_id": "device_123",
      "command": "turn_on",
      "parameters": {"brightness": 70}
    }
  ]
}
```

#### Get Automations
```http
GET /api/automations?enabled_only=true
```

#### Toggle Automation
```http
POST /api/automations/{automation_id}/toggle
```

### Sensor Data

#### Add Sensor Reading
```http
POST /api/sensor-readings/{device_id}
Content-Type: application/json

{
  "sensor_type": "temperature",
  "value": 22.5,
  "unit": "°C",
  "metadata": {
    "location": "living_room",
    "calibrated": true
  }
}
```

#### Get Sensor Readings
```http
GET /api/sensor-readings/{device_id}?limit=100&hours=24
```

### Energy Usage

#### Add Energy Usage Data
```http
POST /api/energy-usage/{device_id}
Content-Type: application/json

{
  "power_consumption": 15.2,
  "energy_consumed": 0.25,
  "cost": 0.04,
  "duration": 60
}
```

#### Get Energy Usage
```http
GET /api/energy-usage/{device_id}?days=7
```

### Notifications

#### Get Notifications
```http
GET /api/notifications?unread_only=true&limit=50
```

#### Mark Notification as Read
```http
POST /api/notifications/{notification_id}/read
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Device
```json
{
  "id": "device_123",
  "name": "Living Room Light",
  "device_type": "light",
  "room": "Living Room",
  "manufacturer": "Philips",
  "model": "Hue White",
  "firmware_version": "1.2.3",
  "ip_address": "192.168.1.100",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "status": "online",
  "last_seen": "2024-01-01T12:00:00",
  "properties": {
    "brightness": 75,
    "color": "#FFFFFF",
    "power": true
  },
  "capabilities": ["dimming", "color_control", "on_off"],
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### Scene
```json
{
  "id": "scene_123",
  "name": "Movie Night",
  "description": "Dim lights and turn on TV for movie watching",
  "icon": "movie",
  "actions": [
    {
      "type": "device_control",
      "device_id": "device_123",
      "command": "set_brightness",
      "parameters": {"brightness": 20}
    }
  ],
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "is_active": false
}
```

### Automation
```json
{
  "id": "automation_123",
  "name": "Sunset Lights",
  "description": "Turn on lights at sunset",
  "enabled": true,
  "trigger_type": "time",
  "trigger_config": {
    "time": "18:30",
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  },
  "actions": [
    {
      "type": "device_control",
      "device_id": "device_123",
      "command": "turn_on",
      "parameters": {"brightness": 70}
    }
  ],
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "last_triggered": "2024-01-01T18:30:00",
  "trigger_count": 5
}
```

### Sensor Reading
```json
{
  "id": "reading_123",
  "device_id": "device_456",
  "sensor_type": "temperature",
  "value": 22.5,
  "unit": "°C",
  "timestamp": "2024-01-01T12:00:00",
  "metadata": {
    "location": "living_room",
    "calibrated": true
  }
}
```

## Supported Device Types

### Lighting
- **Light**: Smart bulbs and light fixtures
  - Commands: turn_on, turn_off, set_brightness, set_color
  - Properties: brightness, color, power, color_temperature

### Climate Control
- **Thermostat**: Smart thermostats and HVAC control
  - Commands: set_temperature, set_mode, turn_on, turn_off
  - Properties: current_temperature, target_temperature, mode, fan_speed

### Security
- **Door Lock**: Smart door locks
  - Commands: lock, unlock
  - Properties: locked, battery_level

- **Security Camera**: IP cameras and security systems
  - Commands: start_recording, stop_recording, take_snapshot
  - Properties: recording, motion_detected, night_vision

- **Motion Sensor**: Motion detection sensors
  - Commands: calibrate
  - Properties: motion_detected, sensitivity, battery_level

- **Smoke Detector**: Smoke and fire detection
  - Commands: test, silence
  - Properties: smoke_detected, alarm_active, battery_level

### Sensors
- **Temperature Sensor**: Temperature monitoring
  - Properties: temperature, humidity, battery_level

- **Humidity Sensor**: Humidity monitoring
  - Properties: humidity, temperature, battery_level

- **Water Leak Sensor**: Water leak detection
  - Properties: leak_detected, battery_level

### Power Control
- **Smart Switch**: Wall switches and relays
  - Commands: turn_on, turn_off, toggle
  - Properties: power, dimmer_level

- **Smart Plug**: Smart outlets and plugs
  - Commands: turn_on, turn_off, toggle
  - Properties: power, energy_consumption, voltage

### Entertainment
- **Speaker**: Smart speakers and audio systems
  - Commands: play, pause, set_volume, next_track
  - Properties: playing, volume, current_track

- **TV**: Smart televisions
  - Commands: turn_on, turn_off, set_channel, set_volume
  - Properties: power, channel, volume, input_source

### Other
- **Garage Door**: Garage door openers
  - Commands: open, close, stop
  - Properties: position, moving, obstruction_detected

- **Window Covering**: Blinds, shades, and curtains
  - Commands: open, close, set_position
  - Properties: position, battery_level

## Automation Triggers

### Time-Based Triggers
- **Specific Time**: Trigger at specific times
- **Sunrise/Sunset**: Trigger based on sunrise/sunset
- **Intervals**: Trigger at regular intervals
- **Days of Week**: Trigger on specific days

### Device State Triggers
- **Device On/Off**: Trigger when device changes state
- **Property Change**: Trigger when device property changes
- **Multiple Devices**: Trigger based on multiple device states

### Sensor Value Triggers
- **Threshold**: Trigger when sensor value crosses threshold
- **Range**: Trigger when sensor value is in range
- **Change Detection**: Trigger when sensor value changes

### Location Triggers
- **Geofencing**: Trigger based on user location
- **Home/Away**: Trigger when user arrives/leaves

### Weather Triggers
- **Temperature**: Trigger based on weather conditions
- **Rain/Snow**: Trigger based on precipitation
- **Sunlight**: Trigger based on sunlight conditions

## WebSocket Events

### Device Events
```javascript
// Device state change
{
  "type": "device_state_change",
  "device_id": "device_123",
  "property": "brightness",
  "old_value": 50,
  "new_value": 75,
  "timestamp": "2024-01-01T12:00:00"
}
```

### Sensor Events
```javascript
// New sensor reading
{
  "type": "sensor_reading",
  "reading": {
    "id": "reading_123",
    "device_id": "device_456",
    "sensor_type": "temperature",
    "value": 22.5,
    "unit": "°C",
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

### Notification Events
```javascript
// New notification
{
  "type": "notification",
  "notification": {
    "id": "notification_123",
    "title": "Motion Detected",
    "message": "Motion detected in Living Room",
    "type": "warning",
    "priority": "medium",
    "device_id": "device_456",
    "created_at": "2024-01-01T12:00:00",
    "read": false
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
import websockets
import json

# Add devices
light_data = {
    "name": "Living Room Light",
    "device_type": "light",
    "room": "Living Room",
    "manufacturer": "Philips",
    "model": "Hue White",
    "firmware_version": "1.2.3",
    "properties": {"brightness": 75, "color": "#FFFFFF", "power": True},
    "capabilities": ["dimming", "color_control", "on_off"]
}

response = requests.post("http://localhost:8000/api/devices", json=light_data)
light = response.json()
print(f"Added light: {light['id']}")

# Add temperature sensor
sensor_data = {
    "name": "Living Room Sensor",
    "device_type": "temperature_sensor",
    "room": "Living Room",
    "manufacturer": "Nest",
    "model": "Temperature Sensor",
    "firmware_version": "2.1.0"
}

response = requests.post("http://localhost:8000/api/devices", json=sensor_data)
sensor = response.json()
print(f"Added sensor: {sensor['id']}")

# Create scene
scene_data = {
    "name": "Evening Mode",
    "description": "Comfortable lighting for evening",
    "icon": "evening",
    "actions": [
        {
            "type": "device_control",
            "device_id": light['id'],
            "command": "set_brightness",
            "parameters": {"brightness": 40, "color": "#FFA500"}
        }
    ]
}

response = requests.post("http://localhost:8000/api/scenes", json=scene_data)
scene = response.json()
print(f"Created scene: {scene['id']}")

# Create automation
automation_data = {
    "name": "Evening Lights",
    "description": "Set evening lighting at 6 PM",
    "trigger_type": "time",
    "trigger_config": {"time": "18:00"},
    "actions": [
        {
            "type": "scene_activation",
            "scene_id": scene['id']
        }
    ]
}

response = requests.post("http://localhost:8000/api/automations", json=automation_data)
automation = response.json()
print(f"Created automation: {automation['id']}")

# Control device
response = requests.post(f"http://localhost:8000/api/devices/{light['id']}/control", json={
    "command": "set_brightness",
    "parameters": {"brightness": 80}
})
print(f"Control result: {response.json()}")

# Add sensor reading
response = requests.post(f"http://localhost:8000/api/sensor-readings/{sensor['id']}", json={
    "sensor_type": "temperature",
    "value": 22.5,
    "unit": "°C"
})
print(f"Added sensor reading: {response.json()}")

# WebSocket client for real-time updates
async def websocket_client():
    uri = "ws://localhost:8000/ws/python_client"
    async with websockets.connect(uri) as websocket:
        # Subscribe to device updates
        await websocket.send(json.dumps({
            "type": "subscribe_device",
            "device_id": light['id']
        }))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            if data['type'] == 'device_state_change':
                print(f"Device {data['device_id']} changed: {data['property']} = {data['new_value']}")
            elif data['type'] == 'sensor_reading':
                print(f"Sensor reading: {data['reading']['value']} {data['reading']['unit']}")
            elif data['type'] == 'notification':
                print(f"Notification: {data['notification']['title']} - {data['notification']['message']}")

# Run WebSocket client
asyncio.run(websocket_client())
```

### JavaScript Client
```javascript
// WebSocket client for real-time updates
class SmartHomeClient {
  constructor() {
    this.ws = new WebSocket('ws://localhost:8000/ws/javascript_client');
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }
  
  handleMessage(message) {
    switch (message.type) {
      case 'device_state_change':
        console.log(`Device ${message.device_id} changed:`, message.property, '=', message.new_value);
        this.updateDeviceUI(message.device_id, message.property, message.new_value);
        break;
        
      case 'sensor_reading':
        console.log('Sensor reading:', message.reading);
        this.updateSensorUI(message.reading);
        break;
        
      case 'notification':
        console.log('Notification:', message.notification);
        this.showNotification(message.notification);
        break;
    }
  }
  
  async controlDevice(deviceId, command, parameters) {
    const response = await fetch(`http://localhost:8000/api/devices/${deviceId}/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, parameters })
    });
    
    return response.json();
  }
  
  async activateScene(sceneId) {
    const response = await fetch(`http://localhost:8000/api/scenes/${sceneId}/activate`, {
      method: 'POST'
    });
    
    return response.json();
  }
  
  async getDevices() {
    const response = await fetch('http://localhost:8000/api/devices');
    return response.json();
  }
  
  async getSensorReadings(deviceId, hours = 24) {
    const response = await fetch(`http://localhost:8000/api/sensor-readings/${deviceId}?hours=${hours}`);
    return response.json();
  }
  
  updateDeviceUI(deviceId, property, value) {
    // Update device UI based on state change
    const deviceElement = document.querySelector(`[data-device-id="${deviceId}"]`);
    if (deviceElement) {
      const propertyElement = deviceElement.querySelector(`[data-property="${property}"]`);
      if (propertyElement) {
        propertyElement.textContent = value;
      }
    }
  }
  
  updateSensorUI(reading) {
    // Update sensor display
    const sensorElement = document.querySelector(`[data-sensor-id="${reading.device_id}"]`);
    if (sensorElement) {
      sensorElement.querySelector('.value').textContent = reading.value;
      sensorElement.querySelector('.unit').textContent = reading.unit;
      sensorElement.querySelector('.timestamp').textContent = new Date(reading.timestamp).toLocaleTimeString();
    }
  }
  
  showNotification(notification) {
    // Display notification to user
    const notificationElement = document.createElement('div');
    notificationElement.className = `notification ${notification.type}`;
    notificationElement.innerHTML = `
      <h4>${notification.title}</h4>
      <p>${notification.message}</p>
    `;
    
    document.getElementById('notifications').appendChild(notificationElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      notificationElement.remove();
    }, 5000);
  }
}

// Usage
const client = new SmartHomeClient();

// Control devices
document.getElementById('light-dimmer').addEventListener('input', async (e) => {
  const deviceId = e.target.dataset.deviceId;
  await client.controlDevice(deviceId, 'set_brightness', { brightness: e.target.value });
});

document.getElementById('scene-buttons').addEventListener('click', async (e) => {
  if (e.target.classList.contains('scene-button')) {
    const sceneId = e.target.dataset.sceneId;
    await client.activateScene(sceneId);
  }
});

// Load devices and sensors
client.getDevices().then(devices => {
  devices.forEach(device => {
    console.log(`Device: ${device.name} (${device.device_type}) in ${device.room}`);
  });
});

client.getSensorReadings('sensor_123').then(readings => {
  console.log('Recent sensor readings:', readings);
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

# Device Discovery
DEVICE_DISCOVERY_ENABLED=true
DEVICE_DISCOVERY_INTERVAL=30
DEVICE_TIMEOUT=300

# Automation
AUTOMATION_CHECK_INTERVAL=30
MAX_AUTOMATION_EXECUTIONS=100
AUTOMATION_HISTORY_RETENTION_DAYS=30

# Sensor Data
SENSOR_DATA_RETENTION_DAYS=90
SENSOR_READING_BATCH_SIZE=100
SENSOR_DATA_COMPRESSION=true

# Energy Tracking
ENERGY_COST_PER_KWH=0.12
ENERGY_DATA_RETENTION_DAYS=365
ENERGY_REPORTING_INTERVAL=60

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=100
WEBSOCKET_MESSAGE_QUEUE_SIZE=1000

# Security
API_KEY_REQUIRED=false
DEVICE_AUTHENTICATION=true
WEBHOOK_SIGNATURE_VALIDATION=true

# Database (for persistence)
DATABASE_URL=sqlite:///./smart_home.db
ENABLE_DEVICE_BACKUP=true
BACKUP_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=info
ENABLE_DEVICE_LOGGING=true
AUTOMATION_LOG_RETENTION_DAYS=7
SECURITY_LOG_RETENTION_DAYS=90
```

## Use Cases

- **Home Automation**: Automated lighting, climate, and security control
- **Energy Management**: Monitor and optimize energy consumption
- **Security Monitoring**: Real-time security alerts and monitoring
- **Elderly Care**: Monitoring and assistance for elderly family members
- **Vacation Mode**: Simulate occupancy when away from home
- **Voice Control Integration**: Integration with voice assistants
- **Mobile Apps**: Remote control and monitoring via mobile applications

## Advanced Features

### Machine Learning Integration
```python
# Predictive automation based on usage patterns
def predict_user_behavior(device_id: str, time_of_day: datetime) -> Dict[str, Any]:
    # Analyze historical usage patterns
    usage_data = get_device_usage_history(device_id, days=30)
    
    # Train simple model to predict user preferences
    predicted_state = ml_model.predict(time_of_day, usage_data)
    
    return predicted_state
```

### Voice Assistant Integration
```python
# Integration with voice assistants
def handle_voice_command(command: str, user_id: str) -> str:
    # Parse natural language command
    intent = nlp_processor.parse_intent(command)
    
    if intent.action == "control_device":
        device = find_device_by_name(intent.device_name)
        if device:
            await control_device(device.id, intent.command, intent.parameters)
            return f"Turning {intent.device_name} {intent.command}"
    
    return "I didn't understand that command"
```

### Geofencing Automation
```python
# Location-based automation
def handle_location_change(user_id: str, location: str, is_home: bool):
    if is_home:
        # User arrived home
        await activate_scene("welcome_home")
    else:
        # User left home
        await activate_scene("away_mode")
        # Enable security features
        await enable_security_mode()
```

## Production Considerations

- **Device Security**: Secure device authentication and communication
- **Network Reliability**: Handle network outages and device disconnections
- **Scalability**: Support for hundreds of devices and sensors
- **Data Privacy**: Protect user data and privacy preferences
- **Backup & Recovery**: Regular backups of configurations and data
- **Performance**: Efficient handling of real-time data and automation
- **Compliance**: GDPR and other privacy regulations compliance
