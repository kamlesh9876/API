# DevOps Analytics API

A comprehensive FastAPI-based REST API for DevOps monitoring, analytics, and insights.

## Features

- **Deployment Tracking**: Monitor deployment status, duration, and success rates
- **Pipeline Analytics**: Track CI/CD pipeline performance and metrics
- **Alert Management**: Monitor and manage system alerts with severity levels
- **System Health**: Real-time service health monitoring
- **Metrics Collection**: Performance metrics for services and environments
- **Analytics Dashboard**: Comprehensive analytics and trends

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:8001`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## API Endpoints

### Deployments
- `GET /deployments` - Get all deployments (with optional filtering)
- `GET /deployments/{id}` - Get a specific deployment

### Pipelines
- `GET /pipelines` - Get all pipelines (with optional filtering)
- `GET /pipelines/{id}` - Get a specific pipeline

### Alerts
- `GET /alerts` - Get all alerts (with optional filtering)
- `GET /alerts/{id}` - Get a specific alert

### Metrics & Health
- `GET /metrics` - Get all metrics (with optional filtering)
- `GET /health` - Get system health for all services
- `GET /health/{service}` - Get health for specific service

### Analytics
- `GET /analytics/deployment-success-rate` - Deployment success rate analytics
- `GET /analytics/pipeline-performance` - Pipeline performance metrics
- `GET /analytics/alert-trends` - Alert trends and statistics
- `GET /dashboard` - Comprehensive dashboard data

## Data Models

### Deployment
- Application, environment, version, status
- Start/end times, duration, deployed by
- Commit hash, rollback information

### Pipeline
- Name, project, status, duration
- Triggered by, branch, commit hash
- Pipeline stages

### Alert
- Title, description, severity level
- Source, timestamp, resolution status
- Affected services

### System Health
- Service status, uptime percentage
- CPU, memory, disk usage
- Last check timestamp

## Example Usage

### Get all deployments
```bash
curl http://localhost:8001/deployments
```

### Get only failed deployments
```bash
curl http://localhost:8001/deployments?status=failed
```

### Get deployment success rate (last 30 days)
```bash
curl http://localhost:8001/analytics/deployment-success-rate?days=30
```

### Get dashboard data
```bash
curl http://localhost:8001/dashboard
```

### Get system health
```bash
curl http://localhost:8001/health
```

### Get high severity alerts
```bash
curl http://localhost:8001/alerts?severity=high
```

## Port Configuration

- **Myth Buster API**: Port 8000
- **DevOps Analytics API**: Port 8001

Both APIs can run simultaneously without conflicts.

## Sample Data

The API includes sample data for:
- 2 deployments (success/failed)
- 2 pipelines (success/failed)
- 2 alerts (high/critical severity)
- 2 metrics (response time, error rate)
- 2 system health entries (healthy/degraded)

This provides realistic data for testing and demonstration purposes.
