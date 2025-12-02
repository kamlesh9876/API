# Real-time Analytics API

A comprehensive real-time analytics platform for metrics collection, event tracking, dashboard creation, and live data streaming with WebSocket support.

## Features

- **Real-time Metrics**: Collect and analyze metrics with multiple types (counter, gauge, histogram, timer)
- **Event Tracking**: Track user events and behaviors with rich metadata
- **Live Dashboards**: Create and manage interactive dashboards with multiple widgets
- **Alert System**: Configurable alerts with threshold and anomaly detection
- **Query Engine**: Powerful analytics queries with aggregation and filtering
- **WebSocket Streaming**: Real-time data updates via WebSocket connections
- **Data Aggregation**: Multiple aggregation functions (sum, average, percentiles)
- **Time Series Analysis**: Time-based filtering and windowed analytics

## API Endpoints

### Metrics Management

#### Create Metric
```http
POST /api/metrics
Content-Type: application/json

{
  "name": "api_requests_total",
  "metric_type": "counter",
  "value": 1250,
  "tags": {
    "endpoint": "/api/users",
    "method": "GET",
    "status": "200"
  },
  "unit": "requests",
  "source": "api_server_1"
}
```

#### Get Metrics
```http
GET /api/metrics?limit=100&metric_type=counter&source=api_server_1&time_range=1h
```

### Event Tracking

#### Create Event
```http
POST /api/events
Content-Type: application/json

{
  "event_type": "user_login",
  "user_id": "user_123",
  "session_id": "session_456",
  "properties": {
    "login_method": "email",
    "device_type": "mobile",
    "location": "US"
  },
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### Get Events
```http
GET /api/events?limit=100&event_type=user_login&user_id=user_123&time_range=24h
```

### Dashboard Management

#### Create Dashboard
```http
POST /api/dashboards
Content-Type: application/json

{
  "name": "API Performance Dashboard",
  "description": "Monitor API performance metrics",
  "widgets": [
    {
      "id": "widget_1",
      "type": "chart",
      "title": "Request Rate",
      "query": "metric:api_requests_total",
      "visualization_config": {
        "chart_type": "line",
        "time_range": "1h"
      },
      "refresh_interval": 30
    }
  ],
  "owner_id": "user_123",
  "is_public": false
}
```

#### Get Dashboards
```http
GET /api/dashboards?owner_id=user_123
```

#### Get Specific Dashboard
```http
GET /api/dashboards/{dashboard_id}
```

### Alert Management

#### Create Alert
```http
POST /api/alerts
Content-Type: application/json

{
  "name": "High Error Rate Alert",
  "metric_name": "api_errors_total",
  "alert_type": "threshold",
  "threshold": 100,
  "condition": ">",
  "notification_channels": ["email", "slack"]
}
```

#### Get Alerts
```http
GET /api/alerts?enabled_only=true
```

### Query Engine

#### Create Query
```http
POST /api/queries
Content-Type: application/json

{
  "name": "Request Rate by Endpoint",
  "query_string": "metric:api_requests_total",
  "time_range": "1h",
  "aggregation": "sum",
  "group_by": ["endpoint"],
  "filters": {
    "status": "200"
  }
}
```

#### Execute Query
```http
POST /api/queries/{query_id}/execute
```

### Real-time Subscriptions

#### Create Subscription
```http
POST /api/subscriptions
Content-Type: application/json

{
  "query_id": "query_123",
  "client_id": "client_456"
}
```

#### Delete Subscription
```http
DELETE /api/subscriptions/{subscription_id}
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Metric
```json
{
  "id": "metric_123",
  "name": "api_requests_total",
  "metric_type": "counter",
  "value": 1250,
  "timestamp": "2024-01-01T12:00:00",
  "tags": {
    "endpoint": "/api/users",
    "method": "GET",
    "status": "200"
  },
  "unit": "requests",
  "source": "api_server_1"
}
```

### Analytics Event
```json
{
  "id": "event_123",
  "event_type": "user_login",
  "timestamp": "2024-01-01T12:00:00",
  "user_id": "user_123",
  "session_id": "session_456",
  "properties": {
    "login_method": "email",
    "device_type": "mobile"
  },
  "metadata": {
    "ip_address": "192.168.1.100"
  }
}
```

### Dashboard
```json
{
  "id": "dashboard_123",
  "name": "API Performance Dashboard",
  "description": "Monitor API performance metrics",
  "widgets": [...],
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:30:00",
  "is_public": false,
  "owner_id": "user_123"
}
```

### Alert
```json
{
  "id": "alert_123",
  "name": "High Error Rate Alert",
  "metric_name": "api_errors_total",
  "alert_type": "threshold",
  "threshold": 100,
  "condition": ">",
  "enabled": true,
  "created_at": "2024-01-01T12:00:00",
  "last_triggered": "2024-01-01T15:30:00",
  "notification_channels": ["email", "slack"]
}
```

### Query Result
```json
{
  "query_id": "query_123",
  "data": [
    {
      "group": "GET_/api/users",
      "value": 450,
      "count": 450
    },
    {
      "group": "POST_/api/users",
      "value": 200,
      "count": 200
    }
  ],
  "metadata": {
    "total_metrics": 650,
    "time_range": "1h",
    "aggregation": "sum"
  },
  "execution_time": 0.025,
  "timestamp": "2024-01-01T12:00:00"
}
```

## Supported Metric Types

### 1. Counter
- **Description**: Cumulative counter that only increases
- **Use Cases**: Request counts, error counts, user registrations
- **Operations**: Increment, reset
- **Example**: Total API requests

### 2. Gauge
- **Description**: Current value that can go up or down
- **Use Cases**: Memory usage, CPU usage, active connections
- **Operations**: Set, increment, decrement
- **Example**: Current memory usage in MB

### 3. Histogram
- **Description**: Distribution of values over time
- **Use Cases**: Request latency distribution, response sizes
- **Operations**: Observe values, calculate percentiles
- **Example**: Request latency histogram

### 4. Timer
- **Description**: Duration measurements
- **Use Cases**: Function execution time, API response time
- **Operations**: Start, stop, record duration
- **Example**: Database query time

### 5. Average
- **Description**: Running average of values
- **Use Cases**: Average response time, average order value
- **Operations**: Add value, calculate average
- **Example**: Average response time

## Aggregation Functions

### Basic Aggregations
- **Sum**: Sum of all values
- **Average**: Arithmetic mean of values
- **Min**: Minimum value
- **Max**: Maximum value
- **Count**: Number of values

### Statistical Aggregations
- **Median**: Middle value when sorted
- **Percentile 95**: 95th percentile
- **Percentile 99**: 99th percentile

## WebSocket Streaming

Connect to real-time data updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client123');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'new_metric':
      console.log('New metric:', message.metric);
      break;
    case 'new_event':
      console.log('New event:', message.event);
      break;
    case 'realtime_update':
      console.log('Query update:', message.data);
      break;
    case 'alert_triggered':
      console.log('Alert triggered:', message.alert);
      break;
  }
};

// Subscribe to real-time updates
ws.send(JSON.stringify({
  type: 'subscribe',
  query_id: 'query_123'
}));
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
import json
import websocket
import threading

# Create metrics
for i in range(100):
    metric_data = {
        "name": "api_requests_total",
        "metric_type": "counter",
        "value": i + 1,
        "tags": {
            "endpoint": "/api/users",
            "method": "GET",
            "status": "200"
        },
        "unit": "requests"
    }
    
    response = requests.post("http://localhost:8000/api/metrics", json=metric_data)
    print(f"Created metric {i+1}")

# Create analytics query
query_data = {
    "name": "Request Rate by Endpoint",
    "query_string": "metric:api_requests_total",
    "time_range": "1h",
    "aggregation": "sum",
    "group_by": ["endpoint"]
}

response = requests.post("http://localhost:8000/api/queries", json=query_data)
query = response.json()

# Execute query
response = requests.post(f"http://localhost:8000/api/queries/{query['id']}/execute")
result = response.json()

print("Query Results:")
for row in result['data']:
    print(f"{row['group']}: {row['value']}")

# Create alert
alert_data = {
    "name": "High Request Rate Alert",
    "metric_name": "api_requests_total",
    "alert_type": "threshold",
    "threshold": 50,
    "condition": ">",
    "notification_channels": ["email"]
}

response = requests.post("http://localhost:8000/api/alerts", json=alert_data)
alert = response.json()
print(f"Created alert: {alert['id']}")

# WebSocket client for real-time updates
def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data['type']}")

def on_open(ws):
    print("WebSocket connected")
    # Subscribe to query updates
    ws.send(json.dumps({
        "type": "subscribe",
        "query_id": query['id']
    }))

ws = websocket.WebSocketApp("ws://localhost:8000/ws/python_client",
                          on_message=on_message,
                          on_open=on_open)

# Run WebSocket in separate thread
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.daemon = True
ws_thread.start()

# Keep sending metrics to trigger real-time updates
import time
for i in range(10):
    metric_data = {
        "name": "api_requests_total",
        "metric_type": "counter",
        "value": 100 + i,
        "tags": {"endpoint": "/api/users"}
    }
    requests.post("http://localhost:8000/api/metrics", json=metric_data)
    time.sleep(1)
```

### JavaScript Client
```javascript
// Send metrics
const sendMetric = async (name, value, tags = {}) => {
  const metricData = {
    name,
    metric_type: "counter",
    value,
    tags,
    unit: "requests"
  };

  const response = await fetch('http://localhost:8000/api/metrics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metricData)
  });

  return response.json();
};

// Send analytics events
const trackEvent = async (eventType, properties = {}) => {
  const eventData = {
    event_type: eventType,
    properties,
    metadata: {
      timestamp: new Date().toISOString()
    }
  };

  const response = await fetch('http://localhost:8000/api/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(eventData)
  });

  return response.json();
};

// Real-time WebSocket client
class AnalyticsClient {
  constructor(clientId) {
    this.ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
    this.subscriptions = new Map();

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'new_metric':
        console.log('New metric received:', message.metric);
        break;
      case 'new_event':
        console.log('New event received:', message.event);
        break;
      case 'realtime_update':
        console.log('Real-time update:', message.data);
        break;
      case 'alert_triggered':
        console.log('Alert triggered:', message.alert);
        break;
    }
  }

  async subscribe(queryId, callback) {
    this.ws.send(JSON.stringify({
      type: 'subscribe',
      query_id: queryId
    }));

    this.subscriptions.set(queryId, callback);
  }

  async unsubscribe(queryId) {
    this.ws.send(JSON.stringify({
      type: 'unsubscribe',
      subscription_id: queryId
    }));

    this.subscriptions.delete(queryId);
  }
}

// Usage
const client = new AnalyticsClient('web_client_123');

// Track user interactions
document.addEventListener('click', (event) => {
  trackEvent('button_click', {
    button_id: event.target.id,
    button_text: event.target.textContent,
    page: window.location.pathname
  });
});

// Subscribe to real-time metrics
client.subscribe('query_123', (data) => {
  console.log('Real-time metrics update:', data);
});
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# WebSocket Settings
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=1000

# Data Storage
METRIC_BUFFER_SIZE=10000
EVENT_BUFFER_SIZE=10000
DATA_RETENTION_HOURS=24

# Performance
ENABLE_CACHING=true
CACHE_TTL=300
MAX_QUERY_EXECUTION_TIME=30

# Database (for persistence)
DATABASE_URL=sqlite:///./analytics.db
ENABLE_PERSISTENCE=true

# Logging
LOG_LEVEL=info
ENABLE_QUERY_LOGGING=true
METRICS_LOG_INTERVAL=60
```

## Use Cases

- **Application Monitoring**: Real-time application performance monitoring
- **Business Analytics**: Track user behavior and business metrics
- **IoT Data Collection**: Collect and analyze sensor data
- **Financial Analytics**: Real-time trading and market data analysis
- **DevOps Monitoring**: System and infrastructure monitoring
- **E-commerce**: Track sales, user behavior, and inventory

## Advanced Features

### Custom Aggregations
```python
# Custom aggregation function
def custom_aggregation(values, params):
    # Implement custom logic
    return custom_result

# Register with query engine
query_engine.register_aggregation("custom", custom_aggregation)
```

### Alert Templates
```json
{
  "alert_templates": {
    "high_error_rate": {
      "condition": "metric:api_errors_total > 100",
      "severity": "critical",
      "message": "High error rate detected: {value} errors"
    },
    "low_memory": {
      "condition": "metric:memory_usage < 10",
      "severity": "warning",
      "message": "Low memory: {value}% remaining"
    }
  }
}
```

### Data Export
```python
# Export metrics to CSV
export_metrics_to_csv(
    query_id="query_123",
    time_range="24h",
    format="csv"
)

# Export to external systems
export_to_prometheus(metrics)
export_to_influxdb(events)
```

## Production Considerations

- **Scalability**: Horizontal scaling with load balancers
- **Persistence**: Database integration for long-term storage
- **Monitoring**: System health and performance monitoring
- **Security**: API authentication and rate limiting
- **Data Retention**: Configurable data retention policies
- **Backup**: Regular data backup and recovery procedures
