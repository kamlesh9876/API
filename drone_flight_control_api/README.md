# Drone Flight Control API

A comprehensive drone fleet management system with real-time flight control, telemetry monitoring, and autonomous flight capabilities.

## Features

- **Drone Fleet Management**: Register, monitor, and control multiple drones
- **Real-time Telemetry**: Live position, battery, and status updates via WebSocket
- **Flight Control**: Takeoff, landing, waypoint navigation, and emergency procedures
- **Flight Planning**: Create and execute autonomous flight plans with waypoints
- **Safety Systems**: No-fly zones, low battery warnings, emergency landing
- **Flight Logging**: Complete flight history and event tracking
- **Multiple Flight Modes**: Manual, auto, return-to-home, orbit, follow-me
- **Battery Management**: Real-time battery monitoring and consumption tracking
- **Geofencing**: No-fly zone enforcement and boundary checking

## API Endpoints

### Drone Management

#### Register Drone
```http
POST /api/drones
Content-Type: application/json

{
  "id": "drone_001",
  "name": "Survey Drone Alpha",
  "model": "DJI Phantom 4",
  "serial_number": "SN123456789",
  "status": "idle",
  "position": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 10.0
  },
  "velocity": {"x": 0, "y": 0, "z": 0},
  "attitude": {"roll": 0, "pitch": 0, "yaw": 0},
  "battery": {
    "voltage": 11.1,
    "current": 2.5,
    "percentage": 85.0,
    "temperature": 25.0,
    "remaining_time": 1800
  },
  "flight_mode": "manual",
  "home_position": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 0.0
  },
  "max_altitude": 120.0,
  "max_distance": 1000.0,
  "max_speed": 15.0,
  "firmware_version": "1.2.3"
}
```

#### Get All Drones
```http
GET /api/drones?status=flying
```

#### Get Specific Drone
```http
GET /api/drones/{drone_id}
```

### Flight Commands

#### Send Command
```http
POST /api/drones/{drone_id}/commands
Content-Type: application/json

{
  "command": "takeoff",
  "parameters": {},
  "priority": "normal"
}
```

#### Supported Commands
- **takeoff**: Initiate takeoff sequence
- **land**: Controlled landing at current position
- **emergency_land**: Immediate emergency landing
- **goto**: Navigate to specific coordinates
- **orbit**: Orbit around a point

#### Goto Command Example
```json
{
  "command": "goto",
  "parameters": {
    "latitude": 37.7849,
    "longitude": -122.4094,
    "altitude": 50.0,
    "speed": 8.0
  },
  "priority": "normal"
}
```

#### Get Command History
```http
GET /api/drones/{drone_id}/commands?limit=50
```

### Flight Planning

#### Create Flight Plan
```http
POST /api/flight-plans
Content-Type: application/json

{
  "id": "plan_survey_001",
  "name": "Aerial Survey Route",
  "drone_id": "drone_001",
  "waypoints": [
    {
      "id": "wp_001",
      "position": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 50.0
      },
      "altitude": 50.0,
      "speed": 5.0,
      "wait_time": 5,
      "action": "photo"
    },
    {
      "id": "wp_002",
      "position": {
        "latitude": 37.7849,
        "longitude": -122.4094,
        "altitude": 50.0
      },
      "altitude": 50.0,
      "speed": 5.0,
      "wait_time": 3,
      "action": "photo"
    }
  ]
}
```

#### Get Flight Plans
```http
GET /api/flight-plans?drone_id=drone_001
```

#### Execute Flight Plan
```http
POST /api/flight-plans/{plan_id}/execute
```

### Safety & Geofencing

#### Create No-Fly Zone
```http
POST /api/no-fly-zones
Content-Type: application/json

{
  "id": "nfz_airport",
  "name": "Airport Restricted Zone",
  "polygon": [
    {"latitude": 37.7749, "longitude": -122.4194, "altitude": 0},
    {"latitude": 37.7849, "longitude": -122.4194, "altitude": 0},
    {"latitude": 37.7849, "longitude": -122.4094, "altitude": 0},
    {"latitude": 37.7749, "longitude": -122.4094, "altitude": 0}
  ],
  "min_altitude": 0,
  "max_altitude": 200,
  "reason": "Airport safety zone"
}
```

#### Get No-Fly Zones
```http
GET /api/no-fly-zones
```

### Flight Logs

#### Get Flight Logs
```http
GET /api/drones/{drone_id}/logs?limit=100
```

### Statistics
```http
GET /api/stats
```

## WebSocket Connection

Connect to real-time telemetry updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client123');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

// Subscribe to drone telemetry
ws.send(JSON.stringify({
  type: 'subscribe_telemetry',
  drone_id: 'drone_001'
}));
```

## Data Models

### Drone
```json
{
  "id": "drone_001",
  "name": "Survey Drone Alpha",
  "model": "DJI Phantom 4",
  "status": "flying",
  "position": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 50.0
  },
  "velocity": {"x": 5.0, "y": 2.0, "z": 0.5},
  "attitude": {"roll": 2.5, "pitch": -1.0, "yaw": 45.0},
  "battery": {
    "voltage": 11.1,
    "current": 3.2,
    "percentage": 78.5,
    "temperature": 28.0,
    "remaining_time": 1560
  },
  "flight_mode": "auto",
  "is_armed": true,
  "gps_satellites": 12,
  "signal_strength": 85
}
```

### Flight Command
```json
{
  "id": "cmd_001",
  "drone_id": "drone_001",
  "command": "goto",
  "parameters": {
    "latitude": 37.7849,
    "longitude": -122.4094,
    "altitude": 75.0,
    "speed": 8.0
  },
  "priority": "normal",
  "created_at": "2024-01-01T12:00:00",
  "executed_at": "2024-01-01T12:00:01",
  "status": "executed"
}
```

### Flight Plan
```json
{
  "id": "plan_survey_001",
  "name": "Aerial Survey Route",
  "drone_id": "drone_001",
  "waypoints": [...],
  "is_active": false,
  "total_distance": 1250.5,
  "estimated_duration": 300
}
```

### Flight Log
```json
{
  "id": "log_001",
  "drone_id": "drone_001",
  "timestamp": "2024-01-01T12:00:00",
  "position": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 50.0
  },
  "status": "flying",
  "event": "takeoff",
  "details": {"altitude_reached": 50.0}
}
```

## Drone Statuses

- **idle**: Drone on ground, ready for flight
- **takeoff**: Drone ascending to flight altitude
- **flying**: Drone in flight, executing commands
- **landing**: Drone descending for landing
- **emergency**: Emergency situation, immediate landing required
- **maintenance**: Drone undergoing maintenance
- **charging**: Drone battery charging

## Flight Modes

- **manual**: Direct manual control
- **auto**: Autonomous flight following waypoints
- **return_home**: Automatic return to home position
- **follow_me**: Track and follow a target
- **orbit**: Circular orbit around a point
- **waypoint**: Sequential waypoint navigation

## Safety Features

### Battery Management
- Real-time battery monitoring
- Low battery warnings at 20%
- Critical battery warnings at 10%
- Automatic return-to-home on low battery
- Emergency landing on critical battery

### Geofencing
- No-fly zone enforcement
- Altitude limits
- Distance limits from home position
- Boundary breach notifications

### Emergency Procedures
- Emergency landing capability
- Automatic obstacle avoidance
- Signal loss procedures
- Weather condition monitoring

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
import json

# Register a drone
drone_data = {
    "id": "drone_001",
    "name": "Test Drone",
    "model": "Test Model",
    "serial_number": "TEST123",
    "status": "idle",
    "position": {"latitude": 37.7749, "longitude": -122.4194, "altitude": 0.0},
    "velocity": {"x": 0, "y": 0, "z": 0},
    "attitude": {"roll": 0, "pitch": 0, "yaw": 0},
    "battery": {
        "voltage": 11.1,
        "current": 0.0,
        "percentage": 100.0,
        "temperature": 20.0,
        "remaining_time": 3600
    },
    "flight_mode": "manual",
    "home_position": {"latitude": 37.7749, "longitude": -122.4194, "altitude": 0.0},
    "max_altitude": 120.0,
    "max_distance": 500.0,
    "max_speed": 10.0,
    "firmware_version": "1.0.0"
}

response = requests.post("http://localhost:8000/api/drones", json=drone_data)
drone = response.json()

# Send takeoff command
command_data = {
    "command": "takeoff",
    "parameters": {},
    "priority": "normal"
}

response = requests.post(f"http://localhost:8000/api/drones/{drone['id']}/commands", json=command_data)
command = response.json()

# Monitor drone status
while True:
    response = requests.get(f"http://localhost:8000/api/drones/{drone['id']}")
    current_drone = response.json()
    print(f"Status: {current_drone['status']}, Battery: {current_drone['battery']['percentage']}%")
    
    if current_drone['status'] == 'flying':
        # Send goto command
        goto_command = {
            "command": "goto",
            "parameters": {
                "latitude": 37.7849,
                "longitude": -122.4094,
                "altitude": 50.0,
                "speed": 5.0
            },
            "priority": "normal"
        }
        requests.post(f"http://localhost:8000/api/drones/{drone['id']}/commands", json=goto_command)
        break
    
    asyncio.sleep(1)
```

### JavaScript Client with WebSocket
```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/client123');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'telemetry_update') {
    console.log(`Drone ${message.drone_id}:`, {
      position: message.position,
      battery: message.battery,
      status: message.status
    });
  } else if (message.type === 'low_battery_warning') {
    console.warn(`Low battery warning: Drone ${message.drone_id} at ${message.battery_percentage}%`);
  } else if (message.type === 'emergency_landing') {
    console.error(`Emergency landing: Drone ${message.drone_id} - ${message.reason}`);
  }
};

// Subscribe to telemetry
ws.send(JSON.stringify({
  type: 'subscribe_telemetry',
  drone_id: 'drone_001'
}));

// Send commands via REST API
async function sendCommand(droneId, command, parameters = {}) {
  const response = await fetch(`http://localhost:8000/api/drones/${droneId}/commands`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      command: command,
      parameters: parameters,
      priority: 'normal'
    })
  });
  
  return response.json();
}

// Example: Takeoff and fly to waypoint
await sendCommand('drone_001', 'takeoff');
setTimeout(async () => {
  await sendCommand('drone_001', 'goto', {
    latitude: 37.7849,
    longitude: -122.4094,
    altitude: 50.0,
    speed: 8.0
  });
}, 3000);
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Drone Settings
MAX_DRONES=100
DEFAULT_MAX_ALTITUDE=120
DEFAULT_MAX_DISTANCE=1000
DEFAULT_MAX_SPEED=15

# Safety Settings
LOW_BATTERY_THRESHOLD=20
CRITICAL_BATTERY_THRESHOLD=5
EMERGENCY_LANDING_ALTITUDE=5

# WebSocket Settings
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=1000

# Database (for persistence)
DATABASE_URL=sqlite:///./drone_control.db

# Logging
LOG_LEVEL=info
ENABLE_FLIGHT_LOGGING=true
```

## Use Cases

- **Agriculture**: Crop monitoring and precision agriculture
- **Surveying**: Land survey and mapping missions
- **Inspection**: Infrastructure inspection (power lines, buildings)
- **Delivery**: Package delivery and logistics
- **Surveillance**: Security monitoring and surveillance
- **Photography**: Aerial photography and videography
- **Emergency Response**: Search and rescue operations

## Advanced Features

### Swarm Operations
- Multi-drone coordination
- Formation flying
- Collaborative missions
- Distributed task allocation

### AI Integration
- Object detection and tracking
- Autonomous obstacle avoidance
- Intelligent flight path optimization
- Predictive maintenance

### Weather Integration
- Real-time weather monitoring
- Wind compensation
- Flight condition assessment
- Automatic ground operations

## Production Considerations

- **Database Integration**: PostgreSQL for persistent storage
- **Message Queuing**: Redis/RabbitMQ for command queuing
- **Authentication**: API key-based drone authentication
- **Rate Limiting**: Prevent command spam
- **Monitoring**: System health and drone fleet metrics
- **Scalability**: Horizontal scaling for large fleets
- **Compliance**: FAA/CAA regulation compliance
- **Security**: Encrypted communication and command verification
