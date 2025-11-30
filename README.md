# APIs Collection

A collection of production-ready REST APIs built with FastAPI and Python.

## 🚀 Available APIs

### 1. Myth Buster API
**Port**: 8000  
**Purpose**: Debunk and verify common myths and misconceptions

**Features**:
- CRUD operations for myths
- Search functionality
- Category filtering
- Evidence and source tracking
- Truth status verification

**Quick Start**:
```bash
cd myth_buster_api
pip install -r requirements.txt
python app.py
```

**Documentation**: http://localhost:8000/docs

---

### 2. DevOps Analytics API
**Port**: 8001  
**Purpose**: Comprehensive DevOps monitoring and analytics

**Features**:
- Deployment tracking and analytics
- CI/CD pipeline performance monitoring
- Alert management with severity levels
- System health monitoring
- Metrics collection and trends
- Analytics dashboard

**Quick Start**:
```bash
cd devops_analytics_api
pip install -r requirements.txt
python app.py
```

**Documentation**: http://localhost:8001/docs

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Documentation**: Auto-generated Swagger/OpenAPI
- **CORS**: Enabled for cross-origin requests

## 📋 Prerequisites

- Python 3.7+
- pip package manager

## 🚀 Quick Setup

1. **Clone the repository**:
```bash
git clone https://github.com/kamlesh9876/API.git
cd API
```

2. **Install dependencies for each API**:
```bash
# For Myth Buster API
cd myth_buster_api
pip install -r requirements.txt

# For DevOps Analytics API  
cd ../devops_analytics_api
pip install -r requirements.txt
```

3. **Run the APIs**:
```bash
# Terminal 1 - Myth Buster API
cd myth_buster_api
python app.py

# Terminal 2 - DevOps Analytics API
cd devops_analytics_api
python app.py
```

## 📚 API Documentation

Each API includes comprehensive interactive documentation:

- **Myth Buster API**: http://localhost:8000/docs
- **DevOps Analytics API**: http://localhost:8001/docs

Features of the documentation:
- Interactive API testing
- Request/response examples
- Parameter descriptions
- Authentication info (if applicable)

## 🔧 Configuration

### Port Configuration
- Myth Buster API: Port 8000
- DevOps Analytics API: Port 8001

Both APIs can run simultaneously without conflicts.

### CORS Configuration
Both APIs are configured with permissive CORS settings for development. For production deployment, update the CORS middleware configuration in `app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🧪 Testing

### Using curl

**Myth Buster API Examples**:
```bash
# Get all myths
curl http://localhost:8000/myths

# Get only false myths
curl http://localhost:8000/myths?is_true=false

# Search myths
curl http://localhost:8000/myths/search?q=brain
```

**DevOps Analytics API Examples**:
```bash
# Get all deployments
curl http://localhost:8001/deployments

# Get dashboard data
curl http://localhost:8001/dashboard

# Get system health
curl http://localhost:8001/health
```

### Using Python requests
```python
import requests

# Test Myth Buster API
response = requests.get("http://localhost:8000/myths")
print(response.json())

# Test DevOps Analytics API
response = requests.get("http://localhost:8001/dashboard")
print(response.json())
```

## 📊 Sample Data

Both APIs include realistic sample data for testing and demonstration:

### Myth Buster API
- 3 sample myths covering different categories
- Evidence and sources for each myth
- Truth status verification

### DevOps Analytics API
- Sample deployments (success/failed)
- Pipeline executions with stages
- Alerts with different severity levels
- System health metrics
- Performance metrics

## 🚀 Deployment

### Docker (Recommended)
Create a `Dockerfile` for each API:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Platforms
These APIs can be deployed on:
- **AWS Lambda** (with API Gateway)
- **Google Cloud Functions**
- **Azure Functions**
- **Heroku**
- **DigitalOcean App Platform**
- **Railway**
- **Render**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit: `git commit -m "Add feature description"`
5. Push: `git push origin feature-name`
6. Submit a pull request

## 📝 Project Structure

```
API/
├── README.md                    # This file
├── myth_buster_api/            # Myth Buster API
│   ├── app.py                  # Main FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── README.md              # API-specific documentation
└── devops_analytics_api/       # DevOps Analytics API
    ├── app.py                  # Main FastAPI application
    ├── requirements.txt        # Python dependencies
    └── README.md              # API-specific documentation
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   - Change the port in `app.py`: `uvicorn.run(app, host="0.0.0.0", port=8002)`

2. **Module not found**:
   - Ensure you're in the correct directory
   - Install dependencies: `pip install -r requirements.txt`

3. **CORS errors**:
   - Check your frontend is making requests to the correct port
   - Verify CORS configuration in `app.py`

## 📄 License

This project is licensed under the MIT License - see the individual API README files for details.

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub: https://github.com/kamlesh9876/API/issues
- Check the API-specific documentation in each subfolder

---

**Built with ❤️ using FastAPI**
