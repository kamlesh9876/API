# GPS Tracking API

A comprehensive GPS tracking platform for real-time location monitoring, geofencing, alerts, and fleet management.

## Features

- **Real-time Tracking**: Live GPS location updates with WebSocket support
- **Device Management**: Register and monitor GPS tracking devices
- **Geofencing**: Create virtual boundaries with entry/exit alerts
- **Alert System**: Customizable alerts for various tracking events
- **Location History**: Store and retrieve historical location data
- **Trip Tracking**: Monitor trips with distance, speed, and duration metrics
- **WebSocket Integration**: Real-time updates and notifications
- **Multi-device Support**: Track multiple devices simultaneously

## API Endpoints

### Device Management

#### Create Device
```http
POST /api/devices
Content-Type: application/json

{
  "name": "Company Vehicle 001",
  "device_id": "GPS001",
  "imei": "123456789012345",
  "phone_number": "+1234567890",
  "model": "Tracker Pro",
  "manufacturer": "GPS Corp",
  "firmware_version": "v2.1.0",
  "tracking_mode": "real_time",
  "owner_id": "user_123"
}
```

#### Get Devices
```http
GET /api/devices?status=active&owner_id=user_123&limit=50
```

#### Get Specific Device
```http
GET /api/devices/{device_id}
```

### Location Tracking

#### Add Location
```http
POST /api/devices/{device_id}/locations
Content-Type: application/json

{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "altitude": 10.5,
  "accuracy": 5.0,
  "speed": 45.2,
  "heading": 90.0
}
```

#### Get Locations
```http
GET /api/devices/{device_id}/locations?start_time=2024-01-01T00:00:00&end_time=2024-01-02T00:00:00&limit=100
```

### Geofencing

#### Create Geofence
```http
POST /api/devices/{device_id}/geofences
Content-Type: application/json

{
  "name": "Office Area",
  "fence_type": "circle",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "radius": 500.0
}
```

#### Get Geofences
```http
GET /api/devices/{device_id}/geofences?is_active=true
```

### Alerts

#### Get Alerts
```http
GET /api/devices/{device_id}/alerts?alert_type=geofence_enter&is_resolved=false&limit=100
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
  "name": "Company Vehicle 001",
  "device_id": "GPS001",
  "imei": "123456789012345",
  "phone_number": "+1234567890",
  "model": "Tracker Pro",
  "manufacturer": "GPS Corp",
  "firmware_version": "v2.1.0",
  "status": "active",
  "tracking_mode": "real_time",
  "battery_level": 85,
  "last_seen": "2024-01-01T12:00:00",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "owner_id": "user_123",
  "metadata": {}
}
```

### Location
```json
{
  "id": "loc_123",
  "device_id": "device_123",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "altitude": 10.5,
  "accuracy": 5.0,
  "speed": 45.2,
  "heading": 90.0,
  "timestamp": "2024-01-01T12:00:00",
  "address": "123 Main St, New York, NY",
  "created_at": "2024-01-01T12:00:00"
}
```

### Geofence
```json
{
  "id": "geo_123",
  "name": "Office Area",
  "device_id": "device_123",
  "fence_type": "circle",
  "coordinates": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "radius": 500.0,
  "is_active": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### Alert
```json
{
  "id": "alert_123",
  "device_id": "device_123",
  "alert_type": "geofence_enter",
  "message": "Device entered geofence: Office Area",
  "severity": "medium",
  "is_resolved": false,
  "created_at": "2024-01-01T12:00:00",
  "resolved_at": null,
  "location_data": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

### Trip
```json
{
  "id": "trip_123",
  "device_id": "device_123",
  "name": "Morning Commute",
  "start_time": "2024-01-01T08:00:00",
  "end_time": "2024-01-01T08:45:00",
  "start_location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "end_location": {
    "latitude": 40.7580,
    "longitude": -73.9855
  },
  "distance": 15.2,
  "duration": 2700,
  "max_speed": 65.5,
  "avg_speed": 20.2,
  "is_active": false,
  "created_at": "2024-01-01T08:00:00"
}
```

## Device Statuses

### Active
- **Description**: Device is actively transmitting location data
- **Behavior**: Regular location updates, full functionality
- **Battery**: Normal consumption

### Inactive
- **Description**: Device is powered but not transmitting
- **Behavior**: No location updates, can be reactivated
- **Battery**: Low consumption

### Offline
- **Description**: Device is not connected or reachable
- **Behavior**: No communication, may be out of range
- **Battery**: Unknown status

### Maintenance
- **Description**: Device is under maintenance
- **Behavior**: Limited functionality, service mode
- **Battery**: Variable

### Error
- **Description**: Device has encountered an error
- **Behavior**: Limited or no functionality
- **Battery**: May be affected

## Tracking Modes

### Real-time
- **Update Frequency**: Every 5-30 seconds
- **Accuracy**: High
- **Battery Usage**: High
- **Use Cases**: High-value assets, emergency tracking

### Interval
- **Update Frequency**: Every 1-60 minutes
- **Accuracy**: Medium
- **Battery Usage**: Medium
- **Use Cases**: Regular fleet tracking

### On-demand
- **Update Frequency**: When requested
- **Accuracy**: Variable
- **Battery Usage**: Low
- **Use Cases**: Periodic checks, security

### Sleep
- **Update Frequency**: Minimal
- **Accuracy**: Low
- **Battery Usage**: Very Low
- **Use Cases**: Long-term storage, battery conservation

## Alert Types

### Geofence Enter
- **Trigger**: Device enters defined geofence
- **Use Cases**: Arrival notifications, zone monitoring
- **Severity**: Low to Medium

### Geofence Exit
- **Trigger**: Device exits defined geofence
- **Use Cases**: Departure alerts, unauthorized movement
- **Severity**: Medium to High

### Speed Limit
- **Trigger**: Device exceeds speed threshold
- **Use Cases**: Speed monitoring, safety compliance
- **Severity**: Medium

### Idle Time
- **Trigger**: Device remains stationary too long
- **Use Cases**: Efficiency monitoring, theft detection
- **Severity**: Low

### Low Battery
- **Trigger**: Device battery below threshold
- **Use Cases**: Maintenance scheduling, device health
- **Severity**: Medium

### Device Offline
- **Trigger**: Device stops transmitting
- **Use Cases**: Connectivity issues, device failure
- **Severity**: High

### SOS
- **Trigger**: Manual emergency activation
- **Use Cases**: Emergency situations, panic button
- **Severity**: Critical

## Geofence Types

### Circle
- **Description**: Circular boundary with center point and radius
- **Coordinates**: `{"latitude": 40.7128, "longitude": -74.0060}`
- **Radius**: Distance in meters
- **Use Cases**: Buildings, areas, zones

### Polygon
- **Description**: Custom polygon with multiple vertices
- **Coordinates**: Array of latitude/longitude points
- **Use Cases**: Complex boundaries, property lines

### Rectangle
- **Description**: Rectangular boundary
- **Coordinates**: `{"lat_min": 40.7, "lat_max": 40.8, "lon_min": -74.1, "lon_max": -74.0}`
- **Use Cases**: Simple rectangular areas

## WebSocket Events

### Location Updates
```javascript
{
  "type": "location_update",
  "location": {
    "id": "loc_123",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "speed": 45.2,
    "timestamp": "2024-01-01T12:00:00"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Geofence Alerts
```javascript
{
  "type": "geofence_alert",
  "alert": {
    "id": "alert_123",
    "alert_type": "geofence_enter",
    "message": "Device entered geofence: Office Area",
    "severity": "medium"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Device Status
```javascript
{
  "type": "device_status",
  "device": {
    "id": "device_123",
    "name": "Company Vehicle 001",
    "status": "active",
    "battery_level": 85,
    "last_seen": "2024-01-01T12:00:00"
  },
  "timestamp": "2024-01-01T12:00:00"
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

# Create a device
device_data = {
    "name": "Delivery Truck 001",
    "device_id": "TRUCK001",
    "imei": "987654321098765",
    "phone_number": "+19876543210",
    "model": "Fleet Tracker",
    "manufacturer": "TrackTech",
    "firmware_version": "v3.2.1",
    "tracking_mode": "real_time",
    "owner_id": "fleet_manager"
}

response = requests.post("http://localhost:8000/api/devices", json=device_data)
device = response.json()
print(f"Created device: {device['id']}")

# Add location data
location_data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "altitude": 12.5,
    "accuracy": 3.2,
    "speed": 35.5,
    "heading": 45.0
}

response = requests.post(f"http://localhost:8000/api/devices/{device['id']}/locations", json=location_data)
location = response.json()
print(f"Added location: {location['id']}")

# Create geofence
geofence_data = {
    "name": "Warehouse",
    "fence_type": "circle",
    "coordinates": {
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    "radius": 1000.0
}

response = requests.post(f"http://localhost:8000/api/devices/{device['id']}/geofences", json=geofence_data)
geofence = response.json()
print(f"Created geofence: {geofence['id']}")

# Get device locations
response = requests.get(f"http://localhost:8000/api/devices/{device['id']}/locations?limit=10")
locations = response.json()

print(f"Recent locations for {device['name']}:")
for loc in locations:
    print(f"  {loc['timestamp']}: {loc['latitude']}, {loc['longitude']} (Speed: {loc['speed']} km/h)")

# Get alerts
response = requests.get(f"http://localhost:8000/api/devices/{device['id']}/alerts")
alerts = response.json()

print(f"\nAlerts for {device['name']}:")
for alert in alerts:
    print(f"  {alert['created_at']}: {alert['alert_type']} - {alert['message']}")

# WebSocket client for real-time updates
async def tracking_client():
    uri = f"ws://localhost:8000/ws/{device['id']}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to tracking for {device['name']}")
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'location_update':
                loc = data['location']
                print(f"Location update: {loc['latitude']}, {loc['longitude']} (Speed: {loc['speed']} km/h)")
            elif data['type'] == 'geofence_alert':
                alert = data['alert']
                print(f"Geofence alert: {alert['message']}")
            elif data['type'] == 'device_status':
                dev = data['device']
                print(f"Device status: {dev['status']} (Battery: {dev['battery_level']}%)")

# Run WebSocket client
asyncio.run(tracking_client())
```

### JavaScript Client
```javascript
// GPS tracking client
class GPSTrackingClient {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }

  async createDevice(deviceData) {
    const response = await fetch(`${this.baseURL}/api/devices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deviceData)
    });
    return response.json();
  }

  async addLocation(deviceId, locationData) {
    const response = await fetch(`${this.baseURL}/api/devices/${deviceId}/locations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locationData)
    });
    return response.json();
  }

  async createGeofence(deviceId, geofenceData) {
    const response = await fetch(`${this.baseURL}/api/devices/${deviceId}/geofences`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(geofenceData)
    });
    return response.json();
  }

  async getLocations(deviceId, options = {}) {
    const params = new URLSearchParams(options);
    const response = await fetch(`${this.baseURL}/api/devices/${deviceId}/locations?${params}`);
    return response.json();
  }

  async getAlerts(deviceId, options = {}) {
    const params = new URLSearchParams(options);
    const response = await fetch(`${this.baseURL}/api/devices/${deviceId}/alerts?${params}`);
    return response.json();
  }
}

// WebSocket tracking monitor
class TrackingMonitor {
  constructor(deviceId) {
    this.deviceId = deviceId;
    this.ws = new WebSocket(`ws://localhost:8000/ws/${deviceId}`);
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('Connected to GPS tracking');
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from GPS tracking');
      clearInterval(this.pingInterval);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'location_update':
        this.updateLocationDisplay(message.location);
        break;
      case 'geofence_alert':
        this.showGeofenceAlert(message.alert);
        break;
      case 'device_status':
        this.updateDeviceStatus(message.device);
        break;
      case 'pong':
        console.log('Connection healthy');
        break;
    }
  }

  startPingInterval() {
    this.pingInterval = setInterval(() => {
      this.ws.send(JSON.stringify({ type: 'ping' }));
    }, 30000);
  }

  updateLocationDisplay(location) {
    const locationElement = document.getElementById('current-location');
    if (locationElement) {
      locationElement.innerHTML = `
        <div class="location-info">
          <span class="coordinates">${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}</span>
          <span class="speed">${location.speed.toFixed(1)} km/h</span>
          <span class="heading">${location.heading.toFixed(0)}°</span>
          <span class="time">${new Date(location.timestamp).toLocaleTimeString()}</span>
        </div>
      `;
    }

    // Update map marker
    if (window.map && window.deviceMarker) {
      const newPos = { lat: location.latitude, lng: location.longitude };
      window.deviceMarker.setPosition(newPos);
      window.map.setCenter(newPos);
    }

    console.log(`Location update: ${location.latitude}, ${location.longitude}`);
  }

  showGeofenceAlert(alert) {
    const alertContainer = document.getElementById('alerts-container');
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alert.severity}`;
    alertElement.innerHTML = `
      <div class="alert-header">
        <span class="alert-type">${alert.alert_type.replace('_', ' ').toUpperCase()}</span>
        <span class="alert-time">${new Date(alert.created_at).toLocaleTimeString()}</span>
      </div>
      <div class="alert-message">${alert.message}</div>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      alertElement.remove();
    }, 10000);

    console.log(`Geofence alert: ${alert.message}`);
  }

  updateDeviceStatus(device) {
    const statusElement = document.getElementById('device-status');
    if (statusElement) {
      statusElement.innerHTML = `
        <div class="status-info">
          <span class="status ${device.status}">${device.status.toUpperCase()}</span>
          <span class="battery">Battery: ${device.battery_level}%</span>
          <span class="last-seen">Last seen: ${new Date(device.last_seen).toLocaleString()}</span>
        </div>
      `;
    }

    console.log(`Device status: ${device.status} (Battery: ${device.battery_level}%)`);
  }
}

// Usage example
const trackingClient = new GPSTrackingClient();

// Create device form
document.getElementById('device-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const deviceData = {
    name: document.getElementById('device-name').value,
    device_id: document.getElementById('device-id').value,
    imei: document.getElementById('device-imei').value,
    phone_number: document.getElementById('device-phone').value,
    model: document.getElementById('device-model').value,
    manufacturer: document.getElementById('device-manufacturer').value,
    firmware_version: document.getElementById('device-firmware').value,
    tracking_mode: document.getElementById('tracking-mode').value,
    owner_id: document.getElementById('owner-id').value
  };

  try {
    const device = await trackingClient.createDevice(deviceData);
    console.log('Device created:', device);
    
    // Start tracking monitor
    const monitor = new TrackingMonitor(device.id);
    
    // Show device tracking UI
    document.getElementById('tracking-ui').style.display = 'block';
    document.getElementById('device-name-display').textContent = device.name;
    
    // Initialize map
    initializeMap();
    
  } catch (error) {
    console.error('Error creating device:', error);
    alert('Error creating device');
  }
});

// Create geofence form
document.getElementById('geofence-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const deviceId = document.getElementById('geofence-device-id').value;
  const geofenceData = {
    name: document.getElementById('geofence-name').value,
    fence_type: document.getElementById('fence-type').value,
    coordinates: {
      latitude: parseFloat(document.getElementById('fence-lat').value),
      longitude: parseFloat(document.getElementById('fence-lon').value)
    },
    radius: parseFloat(document.getElementById('fence-radius').value)
  };

  try {
    const geofence = await trackingClient.createGeofence(deviceId, geofenceData);
    console.log('Geofence created:', geofence);
    alert('Geofence created successfully!');
    
    // Add geofence to map
    if (window.map) {
      addGeofenceToMap(geofence);
    }
    
    // Reset form
    document.getElementById('geofence-form').reset();
    
  } catch (error) {
    console.error('Error creating geofence:', error);
    alert('Error creating geofence');
  }
});

// Initialize map (using Google Maps API)
function initializeMap() {
  if (typeof google !== 'undefined' && google.maps) {
    window.map = new google.maps.Map(document.getElementById('map'), {
      center: { lat: 40.7128, lng: -74.0060 },
      zoom: 13
    });

    window.deviceMarker = new google.maps.Marker({
      map: window.map,
      position: { lat: 40.7128, lng: -74.0060 },
      title: 'Device Location'
    });
  }
}

// Add geofence to map
function addGeofenceToMap(geofence) {
  if (!window.map) return;

  if (geofence.fence_type === 'circle') {
    const circle = new google.maps.Circle({
      map: window.map,
      center: {
        lat: geofence.coordinates.latitude,
        lng: geofence.coordinates.longitude
      },
      radius: geofence.radius,
      fillColor: '#FF0000',
      fillOpacity: 0.2,
      strokeColor: '#FF0000',
      strokeOpacity: 0.8
    });

    // Store reference for later removal
    if (!window.geofences) {
      window.geofences = [];
    }
    window.geofences.push(circle);
  }
}

// Load location history
document.getElementById('load-history-btn').addEventListener('click', async () => {
  const deviceId = document.getElementById('history-device-id').value;
  const hours = parseInt(document.getElementById('history-hours').value) || 24;
  
  try {
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - hours * 60 * 60 * 1000);
    
    const locations = await trackingClient.getLocations(deviceId, {
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString(),
      limit: 1000
    });
    
    // Display location history on map
    displayLocationHistory(locations);
    
  } catch (error) {
    console.error('Error loading location history:', error);
    alert('Error loading location history');
  }
});

function displayLocationHistory(locations) {
  if (!window.map || !locations.length) return;

  const path = locations.map(loc => ({
    lat: loc.latitude,
    lng: loc.longitude
  }));

  const polyline = new google.maps.Polyline({
    path: path,
    geodesic: true,
    strokeColor: '#0000FF',
    strokeOpacity: 1.0,
    strokeWeight: 2,
    map: window.map
  });

  // Fit map to show entire path
  const bounds = new google.maps.LatLngBounds();
  path.forEach(point => bounds.extend(point));
  window.map.fitBounds(bounds);
}

// Load alerts
document.getElementById('load-alerts-btn').addEventListener('click', async () => {
  const deviceId = document.getElementById('alerts-device-id').value;
  
  try {
    const alerts = await trackingClient.getAlerts(deviceId);
    
    // Display alerts
    const alertsContainer = document.getElementById('alerts-list');
    alertsContainer.innerHTML = '';
    
    alerts.forEach(alert => {
      const alertElement = document.createElement('div');
      alertElement.className = `alert-item ${alert.severity}`;
      alertElement.innerHTML = `
        <div class="alert-header">
          <span class="alert-type">${alert.alert_type.replace('_', ' ').toUpperCase()}</span>
          <span class="alert-time">${new Date(alert.created_at).toLocaleString()}</span>
        </div>
        <div class="alert-message">${alert.message}</div>
        <div class="alert-status ${alert.is_resolved ? 'resolved' : 'unresolved'}">
          ${alert.is_resolved ? 'Resolved' : 'Unresolved'}
        </div>
      `;
      
      alertsContainer.appendChild(alertElement);
    });
    
  } catch (error) {
    console.error('Error loading alerts:', error);
    alert('Error loading alerts');
  }
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

# GPS Data Processing
LOCATION_UPDATE_INTERVAL=30
MAX_LOCATION_AGE=86400
LOCATION_ACCURACY_THRESHOLD=100
SPEED_VALIDATION_ENABLED=true

# Geofencing
GEOFENCE_CHECK_INTERVAL=60
MAX_GEOFENCES_PER_DEVICE=50
GEOFENCE_BUFFER_DISTANCE=10
GEOFENCE_ALERT_COOLDOWN=300

# Alert System
ENABLE_ALERTS=true
ALERT_RETENTION_DAYS=90
ALERT_BATCH_SIZE=100
ALERT_PROCESSING_INTERVAL=30

# Device Management
DEVICE_OFFLINE_THRESHOLD=300
DEVICE_BATTERY_LOW_THRESHOLD=20
DEVICE_STATUS_UPDATE_INTERVAL=60
MAX_DEVICES_PER_USER=100

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=10000
WEBSOCKET_PING_TIMEOUT=10

# Database (for persistence)
DATABASE_URL=sqlite:///./gps_tracking.db
ENABLE_DATA_BACKUP=true
BACKUP_INTERVAL_HOURS=24
DATA_RETENTION_DAYS=365

# External Services
MAPS_API_KEY=your_maps_api_key
GEOCODING_SERVICE=google
REVERSE_GEOCODING_ENABLED=true
ADDRESS_CACHE_TTL=86400

# Logging
LOG_LEVEL=info
ENABLE_LOCATION_LOGGING=true
ALERT_LOG_RETENTION_DAYS=30
ERROR_LOG_RETENTION_DAYS=7
LOG_FILE_PATH=./logs/gps_tracking.log

# Security
ENABLE_DEVICE_AUTHENTICATION=false
API_KEY_REQUIRED=false
RATE_LIMIT_PER_MINUTE=100
ENABLE_LOCATION_ENCRYPTION=false
```

## Use Cases

- **Fleet Management**: Track company vehicles, optimize routes
- **Asset Tracking**: Monitor valuable equipment and assets
- **Personal Safety**: Track family members or employees
- **Logistics**: Monitor delivery vehicles and packages
- **Security**: Monitor perimeter and restricted areas
- **Emergency Services**: Track emergency vehicles and personnel
- **Outdoor Activities**: Track hikers, cyclists, and adventurers

## Advanced Features

### Route Optimization
```python
def optimize_route(locations: List[Location], start_point: Location, end_point: Location) -> List[Location]:
    """Optimize route for multiple stops"""
    # Implement traveling salesman problem solver
    # Consider traffic, road conditions, and time windows
    pass

def calculate_eta(current_location: Location, destination: Location, traffic_data: dict) -> datetime:
    """Calculate estimated time of arrival"""
    distance = calculate_distance(
        current_location.latitude, current_location.longitude,
        destination.latitude, destination.longitude
    )
    
    # Consider current speed, traffic conditions, and route
    base_speed = 50  # km/h
    traffic_factor = traffic_data.get('congestion_factor', 1.0)
    adjusted_speed = base_speed / traffic_factor
    
    travel_time_hours = distance / adjusted_speed
    eta = datetime.now() + timedelta(hours=travel_time_hours)
    
    return eta
```

### Predictive Analytics
```python
def predict_next_location(device_id: str, historical_locations: List[Location]) -> Location:
    """Predict next location based on historical patterns"""
    # Analyze movement patterns, time-based behavior
    # Use machine learning for prediction
    pass

def detect_anomalies(location: Location, device_id: str) -> List[str]:
    """Detect unusual location patterns"""
    anomalies = []
    
    # Check for impossible speeds
    if location.speed > 200:  # km/h
        anomalies.append("Unrealistic speed detected")
    
    # Check for location jumps
    if device_id in locations:
        last_location = locations[device_id][-1]
        time_diff = (location.timestamp - last_location.timestamp).total_seconds()
        distance = calculate_distance(
            last_location.latitude, last_location.longitude,
            location.latitude, location.longitude
        )
        
        if time_diff > 0:
            speed = distance / (time_diff / 3600)  # km/h
            if speed > 200:
                anomalies.append("Location jump detected")
    
    return anomalies
```

### Battery Optimization
```python
def optimize_tracking_mode(device_id: str, battery_level: int, usage_pattern: dict) -> TrackingMode:
    """Optimize tracking mode based on battery level and usage"""
    
    if battery_level < 10:
        return TrackingMode.SLEEP
    elif battery_level < 30:
        return TrackingMode.INTERVAL
    elif usage_pattern.get('high_activity', False):
        return TrackingMode.REAL_TIME
    else:
        return TrackingMode.INTERVAL

def schedule_battery_alerts(device_id: str, battery_level: int):
    """Schedule battery-related alerts"""
    alerts = []
    
    if battery_level < 20:
        alerts.append({
            "type": AlertType.LOW_BATTERY,
            "severity": "high",
            "message": f"Device battery critically low: {battery_level}%"
        })
    elif battery_level < 50:
        alerts.append({
            "type": AlertType.LOW_BATTERY,
            "severity": "medium",
            "message": f"Device battery low: {battery_level}%"
        })
    
    return alerts
```

## Production Considerations

- **Scalability**: Handle thousands of devices simultaneously
- **Data Storage**: Efficient storage of high-frequency location data
- **Battery Life**: Optimize tracking frequency to conserve battery
- **Privacy**: Implement data privacy and security measures
- **Reliability**: Handle network interruptions and device failures
- **Performance**: Real-time processing of location updates
- **Compliance**: Follow location tracking regulations and laws
- **Monitoring**: System health and device status monitoring
