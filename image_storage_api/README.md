# Image Upload + Cloud Storage API

A comprehensive image upload and processing API with cloud storage integration. Features image resizing, compression, filtering, and support for multiple storage providers including AWS S3 and Cloudinary.

## 🚀 Features

- **Image Upload**: Support for multiple image formats (JPEG, PNG, WebP, GIF, BMP, TIFF)
- **Image Processing**: Resize, compress, crop, rotate, flip, filters, watermarks
- **Thumbnail Generation**: Automatic thumbnail creation for all uploads
- **Cloud Storage**: Support for local, AWS S3, and Cloudinary storage
- **Batch Upload**: Upload multiple images simultaneously
- **Image Information**: Detailed metadata extraction (dimensions, format, color mode, etc.)
- **Format Conversion**: Convert between different image formats
- **Quality Control**: Adjustable compression quality and file size optimization
- **Security**: File validation, size limits, and secure upload handling
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Image Processing**: Pillow (PIL)
- **Cloud Storage**: boto3 (AWS S3), cloudinary
- **Async Operations**: aiofiles for file handling
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.7+
- pip package manager
- (Optional) AWS S3 credentials for S3 storage
- (Optional) Cloudinary credentials for Cloudinary storage

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8007`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8007/docs`
- ReDoc: `http://localhost:8007/redoc`

## 📸 API Endpoints

### Image Upload

#### Upload Single Image
```http
POST /upload
Content-Type: multipart/form-data

file: [image file]
resize_width: 800 (optional)
resize_height: 600 (optional)
quality: 85 (optional, 1-100)
format: jpeg (optional: jpeg, png, webp, gif)
thumbnail: true (optional)
storage_provider: local (optional: local, s3, cloudinary)
```

**Response Example**:
```json
{
  "filename": "abc123def456.jpg",
  "original_name": "my-photo.jpg",
  "file_size": 2048576,
  "mime_type": "image/jpeg",
  "width": 1920,
  "height": 1080,
  "format": "jpeg",
  "color_mode": "RGB",
  "has_transparency": false,
  "upload_date": "2024-01-15T12:00:00",
  "file_url": "/uploads/abc123def456.jpg",
  "thumbnail_url": "/thumbnails/abc123def456.jpg",
  "file_hash": "sha256hash...",
  "storage_provider": "local"
}
```

#### Upload Multiple Images
```http
POST /upload-batch
Content-Type: multipart/form-data

files: [image files]
quality: 85 (optional)
thumbnail: true (optional)
storage_provider: local (optional)
```

### Image Processing

#### Process Existing Image
```http
POST /process
Content-Type: multipart/form-data

filename: "abc123def456.jpg"
options: {
  "resize": {"width": 800, "height": 600, "mode": "contain"},
  "compress": {"quality": 80},
  "format": "jpeg",
  "rotate": 90,
  "flip": "horizontal",
  "filter": "grayscale",
  "watermark": {"text": "Copyright 2024", "position": "bottom-right"}
}
```

### Image Management

#### List Images
```http
GET /images?page=1&limit=20&format_filter=jpeg
```

#### Get Image Information
```http
GET /image-info/{filename}
```

#### Delete Image
```http
DELETE /images/{filename}
```

#### Serve Image
```http
GET /images/{filename}
```

#### Serve Thumbnail
```http
GET /thumbnails/{filename}
```

### Storage Configuration

#### Configure Cloud Storage
```http
POST /configure-storage
Content-Type: application/json

{
  "provider": "s3",
  "bucket_name": "my-bucket",
  "access_key": "your-access-key",
  "secret_key": "your-secret-key",
  "region": "us-east-1"
}
```

#### Get Storage Information
```http
GET /storage-info
```

### System

#### Health Check
```http
GET /health
```

## 🧪 Testing Examples

### Upload Image with Resizing
```bash
curl -X POST "http://localhost:8007/upload" \
  -F "file=@my-photo.jpg" \
  -F "resize_width=800" \
  -F "resize_height=600" \
  -F "quality=90" \
  -F "format=jpeg"
```

### Upload Multiple Images
```bash
curl -X POST "http://localhost:8007/upload-batch" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.png" \
  -F "quality=85"
```

### Process Existing Image
```bash
curl -X POST "http://localhost:8007/process" \
  -F "filename=abc123def456.jpg" \
  -F 'options={"resize": {"width": 400, "height": 300}, "filter": "grayscale"}'
```

### Configure S3 Storage
```bash
curl -X POST "http://localhost:8007/configure-storage" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "s3",
    "bucket_name": "my-image-bucket",
    "access_key": "AKIA...",
    "secret_key": "secret...",
    "region": "us-west-2"
  }'
```

## 🎨 Image Processing Features

### Resize Modes
- **contain**: Fit within dimensions, maintaining aspect ratio
- **cover**: Cover dimensions, maintaining aspect ratio (may crop)
- **fill**: Exact dimensions, may distort aspect ratio
- **pad**: Fit within dimensions with padding

### Filters
- **grayscale**: Convert to black and white
- **blur**: Apply blur effect
- **sharpen**: Enhance edges
- **edge_enhance**: Enhance edge detection
- **smooth**: Smooth the image
- **emboss**: Apply emboss effect

### Watermark Options
- **text**: Watermark text
- **position**: top-left, top-right, bottom-left, bottom-right, center
- **opacity**: Transparency level (0.0-1.0)

### Format Support
- **Input**: JPEG, PNG, WebP, GIF, BMP, TIFF
- **Output**: JPEG, PNG, WebP, GIF

## 🗄️ Storage Providers

### Local Storage
- Default storage option
- Files stored in local directories
- Suitable for development and small-scale applications

### AWS S3 Storage
```python
# Configuration
{
  "provider": "s3",
  "bucket_name": "your-bucket",
  "access_key": "your-access-key",
  "secret_key": "your-secret-key",
  "region": "us-east-1"
}
```

### Cloudinary Storage
```python
# Configuration
{
  "provider": "cloudinary",
  "cloud_name": "your-cloud-name",
  "api_key": "your-api-key",
  "api_secret": "your-api-secret"
}
```

## 📊 Data Models

### ImageInfo
```json
{
  "filename": "unique-filename.jpg",
  "original_name": "user-upload.jpg",
  "file_size": 2048576,
  "mime_type": "image/jpeg",
  "width": 1920,
  "height": 1080,
  "format": "jpeg",
  "color_mode": "RGB",
  "has_transparency": false,
  "upload_date": "2024-01-15T12:00:00",
  "file_url": "https://example.com/uploads/filename.jpg",
  "thumbnail_url": "https://example.com/thumbnails/filename.jpg",
  "file_hash": "sha256hash...",
  "storage_provider": "s3"
}
```

### ProcessingOptions
```json
{
  "resize": {
    "width": 800,
    "height": 600,
    "mode": "contain"
  },
  "compress": {
    "quality": 85
  },
  "format": "jpeg",
  "rotate": 90,
  "flip": "horizontal",
  "crop": {
    "left": 100,
    "top": 100,
    "right": 700,
    "bottom": 500
  },
  "filter": "grayscale",
  "watermark": {
    "text": "Copyright 2024",
    "position": "bottom-right",
    "opacity": 0.7
  }
}
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# File Upload Settings
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=uploads
THUMBNAIL_DIR=thumbnails
DEFAULT_QUALITY=85

# Storage Configuration
DEFAULT_STORAGE_PROVIDER=local
S3_BUCKET_NAME=my-bucket
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=us-east-1

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Security
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.gif,.webp,.bmp,.tiff
ENABLE_FILE_VALIDATION=true

# Performance
MAX_CONCURRENT_UPLOADS=10
THUMBNAIL_SIZE=300,300
```

### Advanced Configuration
```python
# Custom processing settings
PROCESSING_CONFIG = {
    "thumbnail_size": (300, 300),
    "default_quality": 85,
    "max_resize_width": 10000,
    "max_resize_height": 10000,
    "supported_formats": ["JPEG", "PNG", "WebP", "GIF"],
    "compression_presets": {
        "low": {"quality": 60},
        "medium": {"quality": 80},
        "high": {"quality": 95}
    }
}
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create directories
RUN mkdir -p uploads thumbnails

COPY . .
EXPOSE 8007

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8007"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  image-api:
    build: .
    ports:
      - "8007:8007"
    environment:
      - DEFAULT_STORAGE_PROVIDER=s3
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./thumbnails:/app/thumbnails

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-storage-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: image-storage-api
  template:
    metadata:
      labels:
        app: image-storage-api
    spec:
      containers:
      - name: image-api
        image: image-storage-api:latest
        ports:
        - containerPort: 8007
        env:
        - name: DEFAULT_STORAGE_PROVIDER
          value: "s3"
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
        - name: thumbnails
          mountPath: /app/thumbnails
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
      - name: thumbnails
        persistentVolumeClaim:
          claimName: thumbnails-pvc
```

## 📈 Performance Optimization

### Caching Strategy
```python
# Redis caching for image metadata
cache_config = {
    "image_info_ttl": 3600,  # 1 hour
    "thumbnail_ttl": 86400,   # 24 hours
    "processing_cache": True
}
```

### Async Processing
```python
# Background processing for large images
from celery import Celery

celery_app = Celery('image_processor')

@celery_app.task
def process_large_image(file_path, options):
    # Process image in background
    pass
```

### CDN Integration
```python
# CDN configuration
cdn_config = {
    "enabled": True,
    "base_url": "https://cdn.example.com",
    "cache_headers": {
        "Cache-Control": "public, max-age=31536000"
    }
}
```

## 🛡️ Security Features

### File Validation
- **Extension checking**: Only allowed image extensions
- **MIME type validation**: Verify actual file type
- **File size limits**: Prevent oversized uploads
- **Content scanning**: Check for malicious content

### Access Control
```python
# API key authentication
from fastapi import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### Rate Limiting
```python
# Rate limiting implementation
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/upload")
@limiter.limit("10/minute")
async def upload_image(request: Request, file: UploadFile = File(...)):
    # Rate limited upload endpoint
    pass
```

## 🔍 Monitoring & Analytics

### Metrics Collection
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

upload_counter = Counter('image_uploads_total', 'Total image uploads')
processing_time = Histogram('image_processing_seconds', 'Image processing time')
storage_usage = Gauge('storage_usage_bytes', 'Total storage usage')
```

### Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_api.log'),
        logging.StreamHandler()
    ]
)
```

## 📱 Client Integration

### JavaScript Example
```javascript
async function uploadImage(file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add processing options
    Object.keys(options).forEach(key => {
        formData.append(key, options[key]);
    });
    
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// Usage
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

const result = await uploadImage(file, {
    resize_width: 800,
    quality: 85,
    format: 'jpeg'
});

console.log('Image uploaded:', result.file_url);
```

### Python Example
```python
import httpx

async def upload_image(file_path: str, options: dict = None):
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = options or {}
            
            response = await client.post(
                'http://localhost:8007/upload',
                files=files,
                data=data
            )
            
            return response.json()

# Usage
result = await upload_image(
    'my-photo.jpg',
    {'resize_width': 800, 'quality': 90}
)
print(f"Uploaded: {result['file_url']}")
```

## 🔮 Future Enhancements

### Planned Features
- **Image Optimization**: Automatic quality optimization based on content
- **Face Detection**: Automatic face detection and cropping
- **Object Recognition**: AI-powered object tagging
- **Color Analysis**: Extract dominant colors and palettes
- **Duplicate Detection**: Find similar or duplicate images
- **Batch Processing**: Queue-based batch image processing
- **Webhooks**: Notifications for processing completion

### AI Integration
- **Smart Cropping**: AI-powered intelligent cropping
- **Style Transfer**: Apply artistic styles to images
- **Super Resolution**: AI-powered image upscaling
- **Background Removal**: Automatic background removal
- **Image Enhancement**: AI-powered quality improvement

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review Pillow documentation for image processing
- Consult cloud provider documentation for storage setup

---

**Built with ❤️ using FastAPI and Pillow**
