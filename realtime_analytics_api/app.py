from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
import random
import collections

app = FastAPI(title="Real-time Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    AVERAGE = "average"
    SUM = "sum"

class AggregationType(str, Enum):
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE_95 = "percentile_95"
    PERCENTILE_99 = "percentile_99"

class AlertType(str, Enum):
    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    RATE = "rate"
    CUSTOM = "custom"

# Data models
class Metric(BaseModel):
    id: str
    name: str
    metric_type: MetricType
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = {}
    unit: Optional[str] = None
    source: Optional[str] = None

class AnalyticsEvent(BaseModel):
    id: str
    event_type: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class Dashboard(BaseModel):
    id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    owner_id: str

class Widget(BaseModel):
    id: str
    type: str  # "chart", "metric", "table", "gauge"
    title: str
    query: str
    visualization_config: Dict[str, Any]
    refresh_interval: int  # seconds

class Alert(BaseModel):
    id: str
    name: str
    metric_name: str
    alert_type: AlertType
    threshold: Optional[float] = None
    condition: str  # ">", "<", "==", "!="
    enabled: bool = True
    created_at: datetime
    last_triggered: Optional[datetime] = None
    notification_channels: List[str] = []

class AnalyticsQuery(BaseModel):
    id: str
    name: str
    query_string: str
    time_range: str  # "1h", "24h", "7d", "30d"
    aggregation: Optional[AggregationType] = None
    group_by: Optional[List[str]] = None
    filters: Dict[str, Any] = {}

class QueryResult(BaseModel):
    query_id: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time: float
    timestamp: datetime

class RealtimeSubscription(BaseModel):
    id: str
    client_id: str
    query: AnalyticsQuery
    created_at: datetime
    last_update: Optional[datetime] = None

# In-memory storage
metrics: List[Metric] = []
events: List[AnalyticsEvent] = []
dashboards: Dict[str, Dashboard] = {}
alerts: Dict[str, Alert] = {}
queries: Dict[str, AnalyticsQuery] = {}
subscriptions: Dict[str, RealtimeSubscription] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Circular buffers for efficient storage
metric_buffer = collections.deque(maxlen=10000)
event_buffer = collections.deque(maxlen=10000)

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
def generate_metric_id() -> str:
    """Generate unique metric ID"""
    return f"metric_{uuid.uuid4().hex[:8]}"

def generate_event_id() -> str:
    """Generate unique event ID"""
    return f"event_{uuid.uuid4().hex[:8]}"

def generate_dashboard_id() -> str:
    """Generate unique dashboard ID"""
    return f"dashboard_{uuid.uuid4().hex[:8]}"

def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return f"alert_{uuid.uuid4().hex[:8]}"

def generate_query_id() -> str:
    """Generate unique query ID"""
    return f"query_{uuid.uuid4().hex[:8]}"

def parse_time_range(time_range: str) -> datetime:
    """Parse time range string to datetime"""
    now = datetime.now()
    
    if time_range == "1h":
        return now - timedelta(hours=1)
    elif time_range == "24h":
        return now - timedelta(hours=24)
    elif time_range == "7d":
        return now - timedelta(days=7)
    elif time_range == "30d":
        return now - timedelta(days=30)
    else:
        return now - timedelta(hours=1)  # Default to 1 hour

def aggregate_metrics(metrics: List[Metric], aggregation: AggregationType, time_window: str = "1m") -> Dict[str, float]:
    """Aggregate metrics based on aggregation type"""
    if not metrics:
        return {}
    
    values = [m.value for m in metrics]
    
    if aggregation == AggregationType.SUM:
        return {"value": sum(values)}
    elif aggregation == AggregationType.AVERAGE:
        return {"value": sum(values) / len(values)}
    elif aggregation == AggregationType.MIN:
        return {"value": min(values)}
    elif aggregation == AggregationType.MAX:
        return {"value": max(values)}
    elif aggregation == AggregationType.COUNT:
        return {"value": len(values)}
    elif aggregation == AggregationType.MEDIAN:
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return {"value": (sorted_values[n//2-1] + sorted_values[n//2]) / 2}
        else:
            return {"value": sorted_values[n//2]}
    elif aggregation == AggregationType.PERCENTILE_95:
        sorted_values = sorted(values)
        index = int(len(sorted_values) * 0.95)
        return {"value": sorted_values[min(index, len(sorted_values)-1)]}
    elif aggregation == AggregationType.PERCENTILE_99:
        sorted_values = sorted(values)
        index = int(len(sorted_values) * 0.99)
        return {"value": sorted_values[min(index, len(sorted_values)-1)]}
    
    return {"value": 0}

def check_alerts(metric: Metric):
    """Check if any alerts are triggered by the metric"""
    triggered_alerts = []
    
    for alert in alerts.values():
        if not alert.enabled or alert.metric_name != metric.name:
            continue
        
        condition_met = False
        
        if alert.alert_type == AlertType.THRESHOLD and alert.threshold:
            if alert.condition == ">" and metric.value > alert.threshold:
                condition_met = True
            elif alert.condition == "<" and metric.value < alert.threshold:
                condition_met = True
            elif alert.condition == "==" and abs(metric.value - alert.threshold) < 0.001:
                condition_met = True
            elif alert.condition == "!=" and abs(metric.value - alert.threshold) >= 0.001:
                condition_met = True
        
        if condition_met:
            alert.last_triggered = datetime.now()
            triggered_alerts.append(alert)
            
            # Send alert notification via WebSocket
            alert_message = {
                "type": "alert_triggered",
                "alert": alert.dict(),
                "metric": metric.dict(),
                "timestamp": datetime.now().isoformat()
            }
            asyncio.create_task(manager.broadcast(alert_message))
    
    return triggered_alerts

async def execute_query(query: AnalyticsQuery) -> QueryResult:
    """Execute analytics query"""
    start_time = time.time()
    
    # Parse time range
    since_time = parse_time_range(query.time_range)
    
    # Filter metrics based on query
    filtered_metrics = [m for m in metric_buffer if m.timestamp >= since_time]
    
    # Apply filters
    for key, value in query.filters.items():
        if key == "metric_type":
            filtered_metrics = [m for m in filtered_metrics if m.metric_type.value == value]
        elif key == "source":
            filtered_metrics = [m for m in filtered_metrics if m.source == value]
        elif any(key in m.tags for m in filtered_metrics):
            filtered_metrics = [m for m in filtered_metrics if m.tags.get(key) == value]
    
    # Group by if specified
    if query.group_by:
        grouped_data = {}
        for metric in filtered_metrics:
            group_key = "_".join([str(metric.tags.get(g, "default")) for g in query.group_by])
            if group_key not in grouped_data:
                grouped_data[group_key] = []
            grouped_data[group_key].append(metric)
        
        # Aggregate each group
        result_data = []
        for group_key, group_metrics in grouped_data.items():
            if query.aggregation:
                aggregated = aggregate_metrics(group_metrics, query.aggregation)
                result_data.append({
                    "group": group_key,
                    "value": aggregated["value"],
                    "count": len(group_metrics)
                })
            else:
                result_data.append({
                    "group": group_key,
                    "values": [m.value for m in group_metrics],
                    "count": len(group_metrics)
                })
    else:
        # Simple aggregation without grouping
        if query.aggregation:
            aggregated = aggregate_metrics(filtered_metrics, query.aggregation)
            result_data = [{"value": aggregated["value"], "count": len(filtered_metrics)}]
        else:
            result_data = [
                {
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat(),
                    "tags": m.tags
                }
                for m in filtered_metrics
            ]
    
    execution_time = time.time() - start_time
    
    return QueryResult(
        query_id=query.id,
        data=result_data,
        metadata={
            "total_metrics": len(filtered_metrics),
            "time_range": query.time_range,
            "aggregation": query.aggregation.value if query.aggregation else None
        },
        execution_time=execution_time,
        timestamp=datetime.now()
    )

async def update_realtime_subscriptions():
    """Update all real-time subscriptions with latest data"""
    for subscription in subscriptions.values():
        try:
            result = await execute_query(subscription.query)
            
            # Send update to subscribed client
            update_message = {
                "type": "realtime_update",
                "subscription_id": subscription.id,
                "data": result.dict(),
                "timestamp": datetime.now().isoformat()
            }
            
            await manager.send_to_client(subscription.client_id, update_message)
            subscription.last_update = datetime.now()
            
        except Exception as e:
            error_message = {
                "type": "subscription_error",
                "subscription_id": subscription.id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_to_client(subscription.client_id, error_message)

# Background task for real-time updates
async def realtime_updater():
    """Background task to update real-time subscriptions"""
    while True:
        await update_realtime_subscriptions()
        await asyncio.sleep(5)  # Update every 5 seconds

# Start background task
asyncio.create_task(realtime_updater())

# API Endpoints
@app.post("/api/metrics", response_model=Metric)
async def create_metric(metric: Metric):
    """Create a new metric"""
    metric.id = generate_metric_id()
    metric.timestamp = datetime.now()
    
    # Add to storage
    metric_buffer.append(metric)
    metrics.append(metric)
    
    # Check alerts
    triggered_alerts = check_alerts(metric)
    
    # Broadcast new metric to WebSocket clients
    metric_message = {
        "type": "new_metric",
        "metric": metric.dict(),
        "timestamp": datetime.now().isoformat()
    }
    asyncio.create_task(manager.broadcast(metric_message))
    
    return metric

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics(
    limit: int = 100,
    metric_type: Optional[MetricType] = None,
    source: Optional[str] = None,
    time_range: str = "1h"
):
    """Get metrics with optional filters"""
    since_time = parse_time_range(time_range)
    filtered_metrics = [m for m in metric_buffer if m.timestamp >= since_time]
    
    if metric_type:
        filtered_metrics = [m for m in filtered_metrics if m.metric_type == metric_type]
    
    if source:
        filtered_metrics = [m for m in filtered_metrics if m.source == source]
    
    return sorted(filtered_metrics, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.post("/api/events", response_model=AnalyticsEvent)
async def create_event(event: AnalyticsEvent):
    """Create a new analytics event"""
    event.id = generate_event_id()
    event.timestamp = datetime.now()
    
    # Add to storage
    event_buffer.append(event)
    events.append(event)
    
    # Broadcast new event to WebSocket clients
    event_message = {
        "type": "new_event",
        "event": event.dict(),
        "timestamp": datetime.now().isoformat()
    }
    asyncio.create_task(manager.broadcast(event_message))
    
    return event

@app.get("/api/events", response_model=List[AnalyticsEvent])
async def get_events(
    limit: int = 100,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    time_range: str = "1h"
):
    """Get events with optional filters"""
    since_time = parse_time_range(time_range)
    filtered_events = [e for e in event_buffer if e.timestamp >= since_time]
    
    if event_type:
        filtered_events = [e for e in filtered_events if e.event_type == event_type]
    
    if user_id:
        filtered_events = [e for e in filtered_events if e.user_id == user_id]
    
    return sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.post("/api/dashboards", response_model=Dashboard)
async def create_dashboard(dashboard: Dashboard):
    """Create a new dashboard"""
    dashboard.id = generate_dashboard_id()
    dashboard.created_at = datetime.now()
    dashboard.updated_at = datetime.now()
    
    dashboards[dashboard.id] = dashboard
    return dashboard

@app.get("/api/dashboards", response_model=List[Dashboard])
async def get_dashboards(owner_id: Optional[str] = None):
    """Get dashboards with optional owner filter"""
    filtered_dashboards = list(dashboards.values())
    
    if owner_id:
        filtered_dashboards = [d for d in filtered_dashboards if d.owner_id == owner_id]
    
    return filtered_dashboards

@app.get("/api/dashboards/{dashboard_id}", response_model=Dashboard)
async def get_dashboard(dashboard_id: str):
    """Get specific dashboard"""
    if dashboard_id not in dashboards:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboards[dashboard_id]

@app.post("/api/alerts", response_model=Alert)
async def create_alert(alert: Alert):
    """Create a new alert"""
    alert.id = generate_alert_id()
    alert.created_at = datetime.now()
    
    alerts[alert.id] = alert
    return alert

@app.get("/api/alerts", response_model=List[Alert])
async def get_alerts(enabled_only: bool = False):
    """Get alerts"""
    filtered_alerts = list(alerts.values())
    
    if enabled_only:
        filtered_alerts = [a for a in filtered_alerts if a.enabled]
    
    return filtered_alerts

@app.post("/api/queries", response_model=AnalyticsQuery)
async def create_query(query: AnalyticsQuery):
    """Create a new analytics query"""
    query.id = generate_query_id()
    
    queries[query.id] = query
    return query

@app.post("/api/queries/{query_id}/execute", response_model=QueryResult)
async def execute_query_endpoint(query_id: str):
    """Execute analytics query"""
    if query_id not in queries:
        raise HTTPException(status_code=404, detail="Query not found")
    
    query = queries[query_id]
    result = await execute_query(query)
    
    return result

@app.post("/api/subscriptions", response_model=RealtimeSubscription)
async def create_subscription(query_id: str, client_id: str):
    """Create real-time subscription"""
    if query_id not in queries:
        raise HTTPException(status_code=404, detail="Query not found")
    
    subscription_id = f"sub_{uuid.uuid4().hex[:8]}"
    
    subscription = RealtimeSubscription(
        id=subscription_id,
        client_id=client_id,
        query=queries[query_id],
        created_at=datetime.now()
    )
    
    subscriptions[subscription_id] = subscription
    return subscription

@app.delete("/api/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str):
    """Delete real-time subscription"""
    if subscription_id not in subscriptions:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    del subscriptions[subscription_id]
    return {"message": "Subscription deleted successfully"}

@app.get("/api/stats")
async def get_analytics_stats():
    """Get analytics platform statistics"""
    total_metrics = len(metric_buffer)
    total_events = len(event_buffer)
    total_dashboards = len(dashboards)
    total_alerts = len(alerts)
    total_queries = len(queries)
    active_subscriptions = len(subscriptions)
    
    # Metric type distribution
    metric_distribution = {}
    for metric in metric_buffer:
        metric_type = metric.metric_type.value
        metric_distribution[metric_type] = metric_distribution.get(metric_type, 0) + 1
    
    # Recent activity
    recent_metrics = len([m for m in metric_buffer if m.timestamp > datetime.now() - timedelta(hours=1)])
    recent_events = len([e for e in event_buffer if e.timestamp > datetime.now() - timedelta(hours=1)])
    
    return {
        "total_metrics": total_metrics,
        "total_events": total_events,
        "total_dashboards": total_dashboards,
        "total_alerts": total_alerts,
        "total_queries": total_queries,
        "active_subscriptions": active_subscriptions,
        "metric_distribution": metric_distribution,
        "recent_metrics_1h": recent_metrics,
        "recent_events_1h": recent_events,
        "supported_metric_types": [t.value for t in MetricType],
        "supported_aggregations": [a.value for a in AggregationType]
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
            if message.get("type") == "subscribe":
                query_id = message.get("query_id")
                if query_id and query_id in queries:
                    subscription = RealtimeSubscription(
                        id=f"sub_{uuid.uuid4().hex[:8]}",
                        client_id=client_id,
                        query=queries[query_id],
                        created_at=datetime.now()
                    )
                    subscriptions[subscription.id] = subscription
                    
                    await manager.send_to_client(client_id, {
                        "type": "subscription_created",
                        "subscription_id": subscription.id
                    })
            
            elif message.get("type") == "unsubscribe":
                subscription_id = message.get("subscription_id")
                if subscription_id in subscriptions:
                    del subscriptions[subscription_id]
                    
                    await manager.send_to_client(client_id, {
                        "type": "subscription_deleted",
                        "subscription_id": subscription_id
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        # Clean up subscriptions for disconnected client
        to_remove = [sub_id for sub_id, sub in subscriptions.items() if sub.client_id == client_id]
        for sub_id in to_remove:
            del subscriptions[sub_id]

@app.get("/")
async def root():
    return {"message": "Real-time Analytics API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
