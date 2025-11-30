# QR Code Generator API

A comprehensive QR code generation API with custom colors, multiple formats, logo support, and complete history tracking. Built with FastAPI and the qrcode library for professional QR code creation.

## 🚀 Features

- **QR Code Generation**: Create QR codes for text, URLs, and any content
- **Multiple Formats**: PNG, SVG, JPEG, BMP support
- **Custom Colors**: Customizable foreground and background colors
- **Logo Integration**: Add logos to QR codes
- **Style Options**: Square, rounded, and circular module styles
- **Error Correction**: Multiple error correction levels
- **Download Support**: Direct file download with proper headers
- **History Tracking**: Complete generation and download history
- **Analytics**: Track downloads, views, and access patterns
- **User Management**: User-specific QR code collections
- **Expiration**: Optional QR code expiration
- **Batch Operations**: Generate multiple QR codes efficiently
- **Preview Mode**: Quick preview before download
- **File Management**: Automatic file cleanup and storage

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **QR Generation**: qrcode library with PIL support
- **Image Processing**: Pillow for image manipulation
- **Database**: SQLite for storage and analytics
- **File Storage**: Local file system with organized structure
- **HTTP Requests**: Requests for logo download

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- 1GB+ disk space for QR code storage

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create output directory**:
```bash
mkdir -p generated_qr_codes
```

3. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8015`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8015/docs`
- ReDoc: `http://localhost:8015/redoc`

## 📝 API Endpoints

### QR Code Generation

#### Generate QR Code
```http
POST /generate
Content-Type: application/json

{
  "content": "https://www.example.com",
  "format": "PNG",
  "size": 200,
  "error_correction": "M",
  "box_size": 10,
  "border": 4,
  "fill_color": "#000000",
  "back_color": "#FFFFFF",
  "logo_url": "https://example.com/logo.png",
  "logo_size": 50,
  "style": "square",
  "user_id": "user123",
  "expires_in_hours": 168
}
```

**Response Example**:
```json
{
  "id": "qr_12345678-1234-1234-1234-123456789abc",
  "content": "https://www.example.com",
  "format": "PNG",
  "size": 200,
  "download_url": "/download/qr_12345678-1234-1234-1234-123456789abc",
  "preview_url": "/preview/qr_12345678-1234-1234-1234-123456789abc",
  "content_hash": "d41d8cd98f00b204e9800998ecf8427e",
  "created_at": "2024-01-15T12:00:00",
  "expires_at": "2024-01-22T12:00:00",
  "download_count": 0,
  "file_size": 2048
}
```

#### Preview QR Code
```http
GET /preview/{qr_id}
```

#### Download QR Code
```http
GET /download/{qr_id}
```

### History and Analytics

#### Get User History
```http
GET /history/{user_id}?limit=50
```

**Response Example**:
```json
[
  {
    "id": "qr_12345678-1234-1234-1234-123456789abc",
    "content": "https://www.example.com",
    "format": "PNG",
    "size": 200,
    "fill_color": "#000000",
    "back_color": "#FFFFFF",
    "created_at": "2024-01-15T12:00:00",
    "download_count": 15,
    "expires_at": "2024-01-22T12:00:00",
    "is_active": true
  }
]
```

#### Get QR Analytics
```http
GET /analytics/{qr_id}
```

**Response Example**:
```json
{
  "qr_id": "qr_12345678-1234-1234-1234-123456789abc",
  "total_downloads": 15,
  "total_views": 45,
  "last_accessed": "2024-01-15T14:30:00",
  "access_by_ip": {
    "192.168.1.100": 8,
    "192.168.1.101": 7
  },
  "access_by_date": {
    "2024-01-15": 23,
    "2024-01-14": 22
  }
}
```

#### Delete QR Code
```http
DELETE /qr/{qr_id}?user_id=user123
```

### Utility Endpoints

#### Supported Formats
```http
GET /formats
```

**Response Example**:
```json
{
  "formats": [
    {
      "format": "PNG",
      "description": "Portable Network Graphics - supports transparency",
      "recommended": true
    },
    {
      "format": "SVG",
      "description": "Scalable Vector Graphics - infinitely scalable",
      "recommended": true
    },
    {
      "format": "JPEG",
      "description": "Joint Photographic Experts Group - smaller file size",
      "recommended": false
    },
    {
      "format": "BMP",
      "description": "Bitmap - uncompressed format",
      "recommended": false
    }
  ]
}
```

#### Supported Styles
```http
GET /styles
```

#### Error Correction Levels
```http
GET /error-correction-levels
```

## 📊 Data Models

### QRCodeRequest
```json
{
  "content": "https://www.example.com",
  "format": "PNG",
  "size": 200,
  "error_correction": "M",
  "box_size": 10,
  "border": 4,
  "fill_color": "#000000",
  "back_color": "#FFFFFF",
  "logo_url": "https://example.com/logo.png",
  "logo_size": 50,
  "style": "square",
  "user_id": "user123",
  "expires_in_hours": 168,
  "custom_data": {}
}
```

### QRCodeResponse
```json
{
  "id": "qr_12345678-1234-1234-1234-123456789abc",
  "content": "https://www.example.com",
  "format": "PNG",
  "size": 200,
  "download_url": "/download/qr_12345678-1234-1234-1234-123456789abc",
  "preview_url": "/preview/qr_12345678-1234-1234-1234-123456789abc",
  "content_hash": "d41d8cd98f00b204e9800998ecf8427e",
  "created_at": "2024-01-15T12:00:00",
  "expires_at": "2024-01-22T12:00:00",
  "download_count": 0,
  "file_size": 2048
}
```

### QRAnalytics
```json
{
  "qr_id": "qr_12345678-1234-1234-1234-123456789abc",
  "total_downloads": 15,
  "total_views": 45,
  "last_accessed": "2024-01-15T14:30:00",
  "access_by_ip": {
    "192.168.1.100": 8,
    "192.168.1.101": 7
  },
  "access_by_date": {
    "2024-01-15": 23,
    "2024-01-14": 22
  }
}
```

## 🧪 Testing Examples

### Basic QR Code Generation
```bash
# Generate simple QR code
curl -X POST "http://localhost:8015/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://www.example.com",
    "format": "PNG",
    "size": 200,
    "user_id": "test_user"
  }'
```

### Custom Colors and Style
```bash
# Generate with custom colors and style
curl -X POST "http://localhost:8015/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://www.example.com",
    "format": "PNG",
    "size": 300,
    "fill_color": "#FF5733",
    "back_color": "#F0F0F0",
    "style": "rounded",
    "error_correction": "H",
    "user_id": "test_user"
  }'
```

### QR Code with Logo
```bash
# Generate QR code with logo
curl -X POST "http://localhost:8015/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://www.example.com",
    "format": "PNG",
    "size": 400,
    "logo_url": "https://via.placeholder.com/100",
    "logo_size": 80,
    "error_correction": "H",
    "user_id": "test_user"
  }'
```

### SVG Format
```bash
# Generate SVG QR code
curl -X POST "http://localhost:8015/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://www.example.com",
    "format": "SVG",
    "size": 500,
    "fill_color": "#1E88E5",
    "back_color": "#E3F2FD",
    "user_id": "test_user"
  }'
```

### Preview and Download
```bash
# Preview QR code
curl -X GET "http://localhost:8015/preview/qr_12345678-1234-1234-1234-123456789abc"

# Download QR code
curl -X GET "http://localhost:8015/download/qr_12345678-1234-1234-1234-123456789abc" \
  -o qr_code.png
```

### History and Analytics
```bash
# Get user history
curl -X GET "http://localhost:8015/history/test_user?limit=10"

# Get QR analytics
curl -X GET "http://localhost:8015/analytics/qr_12345678-1234-1234-1234-123456789abc"

# Delete QR code
curl -X DELETE "http://localhost:8015/qr/qr_12345678-1234-1234-1234-123456789abc?user_id=test_user"
```

## 🎨 QR Code Customization

### Color Options
- **Foreground Color**: QR code module color (hex format)
- **Background Color**: Background color (hex format)
- **Recommended**: High contrast for better scanning

### Style Options
- **Square**: Traditional square modules
- **Rounded**: Rounded corner modules
- **Circle**: Circular dot modules
- **Custom**: Advanced custom styling

### Error Correction Levels
- **L (Low)**: ~7% correction, max data capacity
- **M (Medium)**: ~15% correction, balanced (recommended)
- **Q (Quartile)**: ~25% correction, high reliability
- **H (High)**: ~30% correction, maximum reliability

### Format Comparison
| Format | Transparency | Scalability | File Size | Recommended |
|--------|---------------|-------------|-----------|-------------|
| PNG | ✅ | Good | Medium | ✅ |
| SVG | ✅ | Infinite | Small | ✅ |
| JPEG | ❌ | Poor | Small | ❌ |
| BMP | ❌ | Poor | Large | ❌ |

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8015
DEBUG=false
RELOAD=false

# File Storage
OUTPUT_DIR=./generated_qr_codes
MAX_FILE_SIZE_MB=10
MAX_STORAGE_GB=10
CLEANUP_INTERVAL_HOURS=24
RETENTION_DAYS=30

# Database Configuration
DATABASE_URL=qr_codes.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30

# QR Code Defaults
DEFAULT_SIZE=200
DEFAULT_FORMAT=PNG
DEFAULT_ERROR_CORRECTION=M
DEFAULT_BOX_SIZE=10
DEFAULT_BORDER=4
DEFAULT_FILL_COLOR=#000000
DEFAULT_BACK_COLOR=#FFFFFF

# Security
ENABLE_AUTHENTICATION=false
API_KEY_HEADER=X-API-Key
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
ENABLE_CORS=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logo Processing
MAX_LOGO_SIZE_MB=2
SUPPORTED_LOGO_FORMATS=PNG,JPEG,JPG
LOGO_CACHE_TTL=3600
ENABLE_LOGO_OPTIMIZATION=true

# Analytics
ENABLE_ANALYTICS=true
TRACK_IP_ADDRESSES=true
TRACK_USER_AGENTS=true
ANALYTICS_RETENTION_DAYS=90
ENABLE_DETAILED_LOGGING=true

# Performance
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_REQUESTS=10
ENABLE_CACHING=true
CACHE_TTL=3600
ENABLE_COMPRESSION=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/qr_api.log
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760
LOG_REQUESTS=true
LOG_ERRORS=true

# Advanced Features
ENABLE_BATCH_GENERATION=true
MAX_BATCH_SIZE=10
ENABLE_CUSTOM_STYLES=false
ENABLE_ADVANCED_ERROR_CORRECTION=true
ENABLE_VECTOR_OPTIMIZATION=true

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8016
HEALTH_CHECK_INTERVAL=30
ENABLE_DISK_USAGE_MONITORING=true
DISK_USAGE_WARNING_THRESHOLD=80

# Development
TEST_MODE=false
TEST_DATABASE_URL=test_qr_codes.db
MOCK_LOGO_DOWNLOAD=false
ENABLE_PROFILING=false
DEBUG_RESPONSES=false
```

## 📊 Database Schema

### SQLite Tables
```sql
-- QR codes table
CREATE TABLE qr_codes (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    content TEXT NOT NULL,
    format TEXT DEFAULT 'PNG',
    size INTEGER DEFAULT 200,
    error_correction TEXT DEFAULT 'M',
    box_size INTEGER DEFAULT 10,
    border INTEGER DEFAULT 4,
    fill_color TEXT DEFAULT '#000000',
    back_color TEXT DEFAULT '#FFFFFF',
    logo_path TEXT,
    logo_size INTEGER,
    custom_data TEXT,  -- JSON
    file_path TEXT,
    file_size INTEGER,
    content_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- Analytics table
CREATE TABLE qr_analytics (
    id TEXT PRIMARY KEY,
    qr_id TEXT,
    action TEXT,  -- generate, download, view
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (qr_id) REFERENCES qr_codes (id)
);

-- User sessions table
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    session_data TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p generated_qr_codes logs

# Set permissions
RUN chmod +x generated_qr_codes

EXPOSE 8015

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8015"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  qr-api:
    build: .
    ports:
      - "8015:8015"
    environment:
      - DATABASE_URL=/app/data/qr_codes.db
      - OUTPUT_DIR=/app/generated_qr_codes
    volumes:
      - ./generated_qr_codes:/app/generated_qr_codes
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8015/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./generated_qr_codes:/var/www/qr_codes
    depends_on:
      - qr-api
    restart: unless-stopped

volumes:
  qr_codes_data:
  logs_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qr-code-generator-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qr-code-generator-api
  template:
    metadata:
      labels:
        app: qr-code-generator-api
    spec:
      containers:
      - name: api
        image: qr-code-generator-api:latest
        ports:
        - containerPort: 8015
        env:
        - name: DATABASE_URL
          value: "/app/data/qr_codes.db"
        - name: OUTPUT_DIR
          value: "/app/generated_qr_codes"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: qr-storage
          mountPath: /app/generated_qr_codes
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8015
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8015
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: qr-storage
        persistentVolumeClaim:
          claimName: qr-storage-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: qr-code-generator-service
spec:
  selector:
    app: qr-code-generator-api
  ports:
  - port: 8015
    targetPort: 8015
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qr-storage-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## 📈 Advanced Features

### Batch Generation
```python
@app.post("/generate/batch")
async def generate_batch_qr_codes(
    requests: List[QRCodeRequest],
    user_id: str = Query(...),
    db: Connection = Depends(get_db)
):
    """Generate multiple QR codes in batch"""
    results = []
    
    for request in requests:
        request.user_id = user_id
        try:
            result = await generate_qr_code(request, db)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    
    return {"results": results, "total": len(results)}
```

### Custom Styling
```python
def apply_custom_style(img: Image.Image, style_config: Dict[str, Any]) -> Image.Image:
    """Apply custom styling to QR code"""
    if style_config.get("gradient"):
        img = apply_gradient(img, style_config["gradient"])
    
    if style_config.get("pattern"):
        img = apply_pattern(img, style_config["pattern"])
    
    if style_config.get("rounded_corners"):
        img = apply_rounded_corners(img, style_config["rounded_corners"])
    
    return img
```

### Advanced Analytics
```python
@app.get("/analytics/summary/{user_id}")
async def get_user_analytics_summary(user_id: str, db: Connection = Depends(get_db)):
    """Get comprehensive user analytics"""
    return {
        "total_qr_codes": get_user_qr_count(db, user_id),
        "total_downloads": get_user_total_downloads(db, user_id),
        "most_popular_qr": get_most_popular_qr(db, user_id),
        "usage_by_format": get_usage_by_format(db, user_id),
        "daily_generation_trend": get_daily_generation_trend(db, user_id)
    }
```

### QR Code Validation
```python
def validate_qr_code(content: str) -> Dict[str, Any]:
    """Validate QR code content and provide suggestions"""
    validation_result = {
        "valid": True,
        "warnings": [],
        "suggestions": []
    }
    
    # Check URL validity
    if content.startswith("http"):
        try:
            response = requests.head(content, timeout=5)
            if response.status_code >= 400:
                validation_result["warnings"].append("URL returns error status")
        except:
            validation_result["warnings"].append("URL is not accessible")
    
    # Check content length
    if len(content) > 2000:
        validation_result["warnings"].append("Content is very long, may affect scannability")
        validation_result["suggestions"].append("Consider using a URL shortener")
    
    return validation_result
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
qr_generations = Counter('qr_generations_total', 'Total QR code generations')
qr_downloads = Counter('qr_downloads_total', 'Total QR code downloads')
generation_time = Histogram('qr_generation_seconds', 'QR code generation time')
active_qr_codes = Gauge('active_qr_codes', 'Number of active QR codes')
storage_usage = Gauge('storage_usage_bytes', 'Storage usage in bytes')
```

### Health Monitoring
```python
@app.get("/health/detailed")
async def detailed_health():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "database": await check_database_health(),
            "storage": await check_storage_health(),
            "logo_processing": await check_logo_processing_health()
        },
        "metrics": {
            "total_qr_codes": qr_generations._value._value,
            "active_qr_codes": active_qr_codes._value._value,
            "storage_usage": storage_usage._value._value
        }
    }
```

### Storage Management
```python
@app.post("/admin/cleanup")
async def cleanup_expired_files():
    """Clean up expired QR codes and files"""
    deleted_count = 0
    freed_space = 0
    
    # Find expired QR codes
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM qr_codes WHERE expires_at < ? AND is_active = 1",
        (datetime.now(),)
    )
    expired_qrs = cursor.fetchall()
    
    for qr in expired_qrs:
        # Delete file
        if qr["file_path"] and os.path.exists(qr["file_path"]):
            file_size = os.path.getsize(qr["file_path"])
            os.remove(qr["file_path"])
            freed_space += file_size
        
        # Mark as inactive
        cursor.execute(
            "UPDATE qr_codes SET is_active = 0 WHERE id = ?",
            (qr["id"],)
        )
        deleted_count += 1
    
    db.commit()
    
    return {
        "deleted_qr_codes": deleted_count,
        "freed_space_bytes": freed_space,
        "freed_space_mb": freed_space / (1024 * 1024)
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Advanced Styling**: Gradient fills, patterns, custom shapes
- **QR Code Analytics**: Real-time scanning analytics
- **Batch Operations**: Bulk generation and management
- **API Rate Limiting**: Advanced rate limiting and quotas
- **User Authentication**: JWT-based user management
- **Cloud Storage**: S3, Google Cloud, Azure integration
- **QR Code Templates**: Predefined templates for common use cases
- **Dynamic QR Codes**: Editable QR codes with redirect URLs
- **QR Code Scanning**: Built-in QR code verification
- **Custom Branding**: White-label solutions

### Advanced QR Code Features
- **Animated QR Codes**: GIF and animated SVG support
- **Color Gradients**: Multi-color gradient QR codes
- **Pattern Overlays**: Decorative pattern integration
- **Micro QR Codes**: Smaller format for limited content
- **Frame QR Codes**: QR codes with decorative frames
- **Logo Optimization**: Automatic logo sizing and positioning
- **Error Recovery**: Advanced error correction algorithms
- **Vector Optimization**: Optimized SVG generation

### Integration Opportunities
- **Payment Systems**: QR code payment integration
- **Social Media**: Social media sharing QR codes
- **Event Management**: Event ticket and check-in QR codes
- **Inventory Management**: Product tracking QR codes
- **Marketing Campaigns**: Campaign-specific QR codes
- **Contact Information**: vCard QR code generation
- **WiFi Networks**: WiFi connection QR codes
- **Location Services**: GPS location QR codes

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review qrcode library documentation
- Consult Pillow documentation for image processing
- Check SQLite documentation for database management

---

**Built with ❤️ using FastAPI and qrcode library**
