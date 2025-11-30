from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
from enum import Enum

app = FastAPI(title="DevOps Analytics API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class DeploymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    ROLLED_BACK = "rolled_back"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Pydantic models
class Deployment(BaseModel):
    id: Optional[int] = None
    application: str
    environment: str
    version: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    deployed_by: str
    commit_hash: str
    rollback_info: Optional[Dict[str, Any]] = None

class Pipeline(BaseModel):
    id: Optional[int] = None
    name: str
    project: str
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    triggered_by: str
    branch: str
    commit_hash: str
    stages: List[str]

class Alert(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    affected_services: List[str]

class Metric(BaseModel):
    id: Optional[int] = None
    name: str
    value: float
    unit: str
    timestamp: datetime
    service: str
    environment: str

class SystemHealth(BaseModel):
    service: str
    status: str
    uptime_percentage: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    last_check: datetime

# In-memory database (for demo purposes)
deployments_db = [
    {
        "id": 1,
        "application": "user-service",
        "environment": "production",
        "version": "v2.1.0",
        "status": DeploymentStatus.SUCCESS,
        "start_time": datetime.now() - timedelta(hours=2),
        "end_time": datetime.now() - timedelta(hours=1, minutes=55),
        "duration_seconds": 300,
        "deployed_by": "john.doe",
        "commit_hash": "abc123def",
        "rollback_info": None
    },
    {
        "id": 2,
        "application": "payment-service",
        "environment": "staging",
        "version": "v1.5.2",
        "status": DeploymentStatus.FAILED,
        "start_time": datetime.now() - timedelta(hours=4),
        "end_time": datetime.now() - timedelta(hours=3, minutes=45),
        "duration_seconds": 900,
        "deployed_by": "jane.smith",
        "commit_hash": "def456ghi",
        "rollback_info": {"reason": "Health check failed", "rollback_version": "v1.5.1"}
    }
]

pipelines_db = [
    {
        "id": 1,
        "name": "CI/CD Pipeline",
        "project": "frontend-app",
        "status": PipelineStatus.SUCCESS,
        "start_time": datetime.now() - timedelta(hours=3),
        "end_time": datetime.now() - timedelta(hours=2, minutes=50),
        "duration_seconds": 600,
        "triggered_by": "alice.johnson",
        "branch": "main",
        "commit_hash": "xyz789abc",
        "stages": ["build", "test", "security-scan", "deploy"]
    },
    {
        "id": 2,
        "name": "Backend Pipeline",
        "project": "api-service",
        "status": PipelineStatus.FAILED,
        "start_time": datetime.now() - timedelta(hours=5),
        "end_time": datetime.now() - timedelta(hours=4, minutes=30),
        "duration_seconds": 1800,
        "triggered_by": "bob.wilson",
        "branch": "feature/new-endpoint",
        "commit_hash": "uvw456xyz",
        "stages": ["build", "test", "integration-test"]
    }
]

alerts_db = [
    {
        "id": 1,
        "title": "High CPU Usage",
        "description": "CPU usage exceeded 90% on production server",
        "severity": AlertSeverity.HIGH,
        "source": "monitoring-system",
        "timestamp": datetime.now() - timedelta(minutes=30),
        "resolved": False,
        "resolved_at": None,
        "resolved_by": None,
        "affected_services": ["user-service", "auth-service"]
    },
    {
        "id": 2,
        "title": "Database Connection Pool Exhausted",
        "description": "Database connection pool reached maximum capacity",
        "severity": AlertSeverity.CRITICAL,
        "source": "database-monitor",
        "timestamp": datetime.now() - timedelta(hours=1),
        "resolved": True,
        "resolved_at": datetime.now() - timedelta(minutes=45),
        "resolved_by": "admin.team",
        "affected_services": ["payment-service"]
    }
]

metrics_db = [
    {
        "id": 1,
        "name": "response_time",
        "value": 245.6,
        "unit": "ms",
        "timestamp": datetime.now() - timedelta(minutes=5),
        "service": "user-service",
        "environment": "production"
    },
    {
        "id": 2,
        "name": "error_rate",
        "value": 0.02,
        "unit": "percentage",
        "timestamp": datetime.now() - timedelta(minutes=5),
        "service": "payment-service",
        "environment": "production"
    }
]

system_health_db = [
    {
        "service": "user-service",
        "status": "healthy",
        "uptime_percentage": 99.9,
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 23.4,
        "last_check": datetime.now()
    },
    {
        "service": "payment-service",
        "status": "degraded",
        "uptime_percentage": 95.5,
        "cpu_usage": 78.9,
        "memory_usage": 82.1,
        "disk_usage": 45.6,
        "last_check": datetime.now()
    }
]

next_id = max(len(deployments_db), len(pipelines_db), len(alerts_db), len(metrics_db)) + 1

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to DevOps Analytics API", "version": "1.0.0"}

# Deployments
@app.get("/deployments", response_model=List[Deployment])
async def get_deployments(environment: Optional[str] = None, status: Optional[DeploymentStatus] = None):
    """Get all deployments with optional filtering"""
    filtered_deployments = deployments_db.copy()
    
    if environment:
        filtered_deployments = [d for d in filtered_deployments if d["environment"].lower() == environment.lower()]
    
    if status:
        filtered_deployments = [d for d in filtered_deployments if d["status"] == status]
    
    return filtered_deployments

@app.get("/deployments/{deployment_id}", response_model=Deployment)
async def get_deployment(deployment_id: int):
    """Get a specific deployment by ID"""
    for deployment in deployments_db:
        if deployment["id"] == deployment_id:
            return deployment
    raise HTTPException(status_code=404, detail="Deployment not found")

# Pipelines
@app.get("/pipelines", response_model=List[Pipeline])
async def get_pipelines(status: Optional[PipelineStatus] = None, project: Optional[str] = None):
    """Get all pipelines with optional filtering"""
    filtered_pipelines = pipelines_db.copy()
    
    if status:
        filtered_pipelines = [p for p in filtered_pipelines if p["status"] == status]
    
    if project:
        filtered_pipelines = [p for p in filtered_pipelines if p["project"].lower() == project.lower()]
    
    return filtered_pipelines

@app.get("/pipelines/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(pipeline_id: int):
    """Get a specific pipeline by ID"""
    for pipeline in pipelines_db:
        if pipeline["id"] == pipeline_id:
            return pipeline
    raise HTTPException(status_code=404, detail="Pipeline not found")

# Alerts
@app.get("/alerts", response_model=List[Alert])
async def get_alerts(severity: Optional[AlertSeverity] = None, resolved: Optional[bool] = None):
    """Get all alerts with optional filtering"""
    filtered_alerts = alerts_db.copy()
    
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
    
    if resolved is not None:
        filtered_alerts = [a for a in filtered_alerts if a["resolved"] == resolved]
    
    return sorted(filtered_alerts, key=lambda x: x["timestamp"], reverse=True)

@app.get("/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: int):
    """Get a specific alert by ID"""
    for alert in alerts_db:
        if alert["id"] == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")

# Metrics
@app.get("/metrics", response_model=List[Metric])
async def get_metrics(service: Optional[str] = None, environment: Optional[str] = None):
    """Get all metrics with optional filtering"""
    filtered_metrics = metrics_db.copy()
    
    if service:
        filtered_metrics = [m for m in filtered_metrics if m["service"].lower() == service.lower()]
    
    if environment:
        filtered_metrics = [m for m in filtered_metrics if m["environment"].lower() == environment.lower()]
    
    return sorted(filtered_metrics, key=lambda x: x["timestamp"], reverse=True)

# System Health
@app.get("/health", response_model=List[SystemHealth])
async def get_system_health():
    """Get system health status for all services"""
    return system_health_db

@app.get("/health/{service}", response_model=SystemHealth)
async def get_service_health(service: str):
    """Get health status for a specific service"""
    for health in system_health_db:
        if health["service"].lower() == service.lower():
            return health
    raise HTTPException(status_code=404, detail="Service not found")

# Analytics and Statistics
@app.get("/analytics/deployment-success-rate")
async def get_deployment_success_rate(days: int = 30):
    """Get deployment success rate for the last N days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_deployments = [d for d in deployments_db if d["start_time"] > cutoff_date]
    
    if not recent_deployments:
        return {"success_rate": 0.0, "total_deployments": 0}
    
    successful_deployments = len([d for d in recent_deployments if d["status"] == DeploymentStatus.SUCCESS])
    success_rate = (successful_deployments / len(recent_deployments)) * 100
    
    return {
        "success_rate": round(success_rate, 2),
        "total_deployments": len(recent_deployments),
        "successful_deployments": successful_deployments,
        "failed_deployments": len(recent_deployments) - successful_deployments
    }

@app.get("/analytics/pipeline-performance")
async def get_pipeline_performance(days: int = 7):
    """Get pipeline performance metrics"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_pipelines = [p for p in pipelines_db if p["start_time"] > cutoff_date]
    
    if not recent_pipelines:
        return {"average_duration": 0, "success_rate": 0, "total_pipelines": 0}
    
    successful_pipelines = len([p for p in recent_pipelines if p["status"] == PipelineStatus.SUCCESS])
    total_duration = sum([p["duration_seconds"] or 0 for p in recent_pipelines])
    
    return {
        "average_duration": total_duration // len(recent_pipelines) if recent_pipelines else 0,
        "success_rate": round((successful_pipelines / len(recent_pipelines)) * 100, 2),
        "total_pipelines": len(recent_pipelines),
        "successful_pipelines": successful_pipelines
    }

@app.get("/analytics/alert-trends")
async def get_alert_trends(days: int = 7):
    """Get alert trends for the last N days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_alerts = [a for a in alerts_db if a["timestamp"] > cutoff_date]
    
    severity_counts = {}
    for severity in AlertSeverity:
        severity_counts[severity.value] = len([a for a in recent_alerts if a["severity"] == severity])
    
    resolved_count = len([a for a in recent_alerts if a["resolved"]])
    
    return {
        "total_alerts": len(recent_alerts),
        "resolved_alerts": resolved_count,
        "unresolved_alerts": len(recent_alerts) - resolved_count,
        "severity_breakdown": severity_counts
    }

@app.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    return {
        "summary": {
            "total_deployments": len(deployments_db),
            "successful_deployments": len([d for d in deployments_db if d["status"] == DeploymentStatus.SUCCESS]),
            "active_pipelines": len([p for p in pipelines_db if p["status"] == PipelineStatus.RUNNING]),
            "unresolved_alerts": len([a for a in alerts_db if not a["resolved"]]),
            "healthy_services": len([h for h in system_health_db if h["status"] == "healthy"])
        },
        "recent_deployments": sorted(deployments_db, key=lambda x: x["start_time"], reverse=True)[:5],
        "recent_alerts": sorted(alerts_db, key=lambda x: x["timestamp"], reverse=True)[:5],
        "system_health": system_health_db
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
