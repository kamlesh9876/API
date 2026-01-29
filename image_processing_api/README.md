# Image Processing API

A comprehensive image processing service providing advanced filters, transformations, adjustments, and AI-powered features. Built with FastAPI, this service offers real-time image manipulation with support for various formats and professional-grade processing capabilities.

## 🚀 Features

### Image Filters
- **Blur**: Gaussian blur with adjustable intensity
- **Sharpen**: Image sharpening filter
- **Edge Detection**: Find edges and contours
- **Emboss**: Emboss effect for 3D appearance
- **Smooth**: Smoothing filter for noise reduction
- **Detail**: Detail enhancement filter
- **Contour**: Contour detection and highlighting

### Image Adjustments
- **Brightness**: Adjust image brightness levels
- **Contrast**: Modify image contrast
- **Saturation**: Control color saturation
- **Hue**: Adjust color hue
- **Sharpness**: Image sharpness enhancement
- **Gamma**: Gamma correction for exposure

### Image Transformations
- **Rotation**: Rotate images by any angle
- **Flip**: Horizontal and vertical flipping
- **Crop**: Precise image cropping
- **Resize**: Multiple resize methods with aspect ratio preservation
- **Format Conversion**: Convert between image formats

### Advanced Features
- **Batch Processing**: Apply multiple operations in sequence
- **Color Analysis**: Extract dominant colors and color statistics
- **Quality Assessment**: Analyze image sharpness, brightness, contrast
- **Face Detection**: AI-powered face detection (placeholder)
- **Object Recognition**: Object detection capabilities (placeholder)
- **Text Extraction**: OCR text extraction (placeholder)

### Processing Options
- **Multiple Formats**: JPEG, PNG, WebP, BMP, TIFF, GIF support
- **Quality Control**: Adjustable compression quality
- **Metadata Preservation**: Optional metadata handling
- **Background Processing**: Async processing for large images

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Image Processing**: PIL (Pillow), OpenCV, NumPy
- **Async Support**: Full async/await implementation
- **File Handling**: UploadFile support for image uploads
- **Background Tasks**: Asyncio for long-running operations

## 📋 API Endpoints

### Image Upload

#### Upload Image
```http
POST /api/image/upload
Content-Type: multipart/form-data

file: [Image File]
```

### Image Processing

#### Apply Filter
```http
POST /api/image/{image_id}/filter
Content-Type: application/json

{
  "filter_type": "blur",
  "intensity": 1.5,
  "parameters": {
    "radius": 5
  }
}
```

#### Adjust Image
```http
POST /api/image/{image_id}/adjust
Content-Type: application/json

{
  "adjustment_type": "brightness",
  "value": 1.2,
  "parameters": {
    "preserve_highlights": true
  }
}
```

#### Transform Image
```http
POST /api/image/{image_id}/transform
Content-Type: application/json

{
  "rotation": 45.0,
  "flip_horizontal": false,
  "flip_vertical": false,
  "crop": {
    "x": 100,
    "y": 100,
    "width": 500,
    "height": 400
  },
  "resize": {
    "width": 800,
    "height": 600,
    "maintain_aspect_ratio": true,
    "resize_method": "lanczos",
    "quality": 95
  }
}
```

#### Batch Process
```http
POST /api/image/{image_id}/batch-process
Content-Type: application/json

{
  "operations": [
    {
      "type": "filter",
      "parameters": {
        "filter_type": "blur",
        "intensity": 1.0
      }
    },
    {
      "type": "adjust",
      "parameters": {
        "adjustment_type": "brightness",
        "value": 1.2
      }
    },
    {
      "type": "resize",
      "parameters": {
        "width": 800,
        "height": 600,
        "maintain_aspect_ratio": true
      }
    }
  ],
  "output_format": "jpeg",
  "quality": 90,
  "preserve_metadata": true
}
```

### Image Analysis

#### Analyze Image
```http
POST /api/image/{image_id}/analyze
Content-Type: application/json

{
  "analyze_colors": true,
  "analyze_faces": false,
  "analyze_objects": false,
  "analyze_text": false,
  "analyze_quality": true
}
```

### File Management

#### Download Image
```http
GET /api/image/{image_id}/download?processed_type=original
```

#### List Images
```http
GET /api/images?limit=50&offset=0
```

#### Delete Image
```http
DELETE /api/image/{image_id}?delete_processed=true
```

## 📊 Data Models

### ImageFilterRequest
```python
class ImageFilterRequest(BaseModel):
    filter_type: FilterType
    intensity: float = 1.0
    parameters: Optional[Dict[str, Any]] = {}
```

### ImageAdjustmentRequest
```python
class ImageAdjustmentRequest(BaseModel):
    adjustment_type: AdjustmentType
    value: float
    parameters: Optional[Dict[str, Any]] = {}
```

### ImageTransformRequest
```python
class ImageTransformRequest(BaseModel):
    rotation: Optional[float] = None
    flip_horizontal: bool = False
    flip_vertical: bool = False
    crop: Optional[Dict[str, int]] = None
    resize: Optional[ImageResizeRequest] = None
```

### BatchProcessRequest
```python
class BatchProcessRequest(BaseModel):
    operations: List[Dict[str, Any]]
    output_format: Optional[ImageFormat] = None
    quality: int = 95
    preserve_metadata: bool = True
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Pillow (PIL)
- OpenCV
- NumPy

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart pillow opencv-python numpy

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
UPLOAD_DIR=./uploads
PROCESSED_DIR=./processed
MAX_FILE_SIZE=50MB
SUPPORTED_FORMATS=jpeg,png,webp,bmp,tiff,gif
DEFAULT_QUALITY=95
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Upload an image
with open('example.jpg', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post(
        "http://localhost:8000/api/image/upload",
        files=files
    )

upload_result = upload_response.json()
image_id = upload_result["image_id"]
print(f"Image uploaded with ID: {image_id}")

# Apply blur filter
filter_data = {
    "filter_type": "blur",
    "intensity": 2.0
}

filter_response = requests.post(
    f"http://localhost:8000/api/image/{image_id}/filter",
    json=filter_data
)

filter_result = filter_response.json()
print(f"Filter applied: {filter_result['processed_filename']}")

# Adjust brightness
adjustment_data = {
    "adjustment_type": "brightness",
    "value": 1.3
}

adjustment_response = requests.post(
    f"http://localhost:8000/api/image/{image_id}/adjust",
    json=adjustment_data
)

adjustment_result = adjustment_response.json()
print(f"Adjustment applied: {adjustment_result['processed_filename']}")

# Transform image (resize and rotate)
transform_data = {
    "rotation": 45.0,
    "resize": {
        "width": 800,
        "height": 600,
        "maintain_aspect_ratio": True,
        "resize_method": "lanczos"
    }
}

transform_response = requests.post(
    f"http://localhost:8000/api/image/{image_id}/transform",
    json=transform_data
)

transform_result = transform_response.json()
print(f"Transform applied: {transform_result['processed_filename']}")

# Batch process multiple operations
batch_data = {
    "operations": [
        {
            "type": "filter",
            "parameters": {
                "filter_type": "sharpen",
                "intensity": 1.2
            }
        },
        {
            "type": "adjust",
            "parameters": {
                "adjustment_type": "contrast",
                "value": 1.1
            }
        },
        {
            "type": "resize",
            "parameters": {
                "width": 1200,
                "height": 800,
                "maintain_aspect_ratio": True
            }
        }
    ],
    "output_format": "jpeg",
    "quality": 90
}

batch_response = requests.post(
    f"http://localhost:8000/api/image/{image_id}/batch-process",
    json=batch_data
)

batch_result = batch_response.json()
print(f"Batch processing: {batch_result['processed_filename']}")

# Analyze image
analysis_data = {
    "analyze_colors": True,
    "analyze_quality": True,
    "analyze_faces": False,
    "analyze_objects": False,
    "analyze_text": False
}

analysis_response = requests.post(
    f"http://localhost:8000/api/image/{image_id}/analyze",
    json=analysis_data
)

analysis_result = analysis_response.json()
print(f"Color analysis: {analysis_result['analysis_results']['color_analysis']}")
print(f"Quality analysis: {analysis_result['analysis_results']['quality_analysis']}")

# Download processed image
download_response = requests.get(
    f"http://localhost:8000/api/image/{image_id}/download",
    params={"processed_type": "batch"}
)

with open('processed_image.jpg', 'wb') as f:
    f.write(download_response.content)

print("Processed image downloaded successfully")

# List all images
list_response = requests.get("http://localhost:8000/api/images")
images = list_response.json()
print(f"Total images: {images['total']}")
for image in images['images']:
    print(f"- {image['filename']} ({image['size']}, {image['file_size']} bytes)")
```

### JavaScript Client
```javascript
// Upload image
const fileInput = document.getElementById('imageInput');
const file = fileInput.files[0];

if (file) {
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('http://localhost:8000/api/image/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Image uploaded:', data);
        const imageId = data.image_id;
        
        // Apply filter
        const filterData = {
            filter_type: 'blur',
            intensity: 1.5
        };
        
        return fetch(`http://localhost:8000/api/image/${imageId}/filter`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filterData)
        });
    })
    .then(response => response.json())
    .then(filterResult => {
        console.log('Filter applied:', filterResult);
        
        // Download processed image
        const downloadUrl = `http://localhost:8000/api/image/${filterResult.processed_image_id}/download?processed_type=filtered`;
        
        // Create download link
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filterResult.processed_filename;
        link.click();
    })
    .catch(error => console.error('Error:', error));
}

// Batch processing example
const batchData = {
    operations: [
        {
            type: 'filter',
            parameters: {
                filter_type: 'sharpen',
                intensity: 1.2
            }
        },
        {
            type: 'adjust',
            parameters: {
                adjustment_type: 'brightness',
                value: 1.2
            }
        },
        {
            type: 'resize',
            parameters: {
                width: 800,
                height: 600,
                maintain_aspect_ratio: true
            }
        }
    ],
    output_format: 'png',
    quality: 95
};

fetch(`http://localhost:8000/api/image/${imageId}/batch-process`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(batchData)
})
.then(response => response.json())
.then(batchResult => {
    console.log('Batch processing completed:', batchResult);
    
    // Display processed image
    const img = document.createElement('img');
    img.src = `http://localhost:8000/api/image/${batchResult.processed_image_id}/download?processed_type=batch`;
    document.body.appendChild(img);
})
.catch(error => console.error('Error:', error));
```

## 🔧 Configuration

### Environment Variables
```bash
# File Handling
UPLOAD_DIR=./uploads
PROCESSED_DIR=./processed
MAX_FILE_SIZE=50MB
SUPPORTED_FORMATS=jpeg,png,webp,bmp,tiff,gif
DEFAULT_QUALITY=95

# Processing Settings
MAX_IMAGE_DIMENSION=10000
MAX_CONCURRENT_PROCESSING=5
PROCESSING_TIMEOUT=300
ENABLE_AI_FEATURES=false

# Quality Settings
DEFAULT_SHARPEN_FACTOR=1.0
DEFAULT_BLUR_RADIUS=2.0
DEFAULT_BRIGHTNESS_FACTOR=1.0
DEFAULT_CONTRAST_FACTOR=1.0

# Storage
CLEANUP_TEMP_FILES=true
TEMP_FILE_RETENTION_HOURS=24
PRESERVE_ORIGINAL_METADATA=true

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
RATE_LIMIT_PER_MINUTE=100
SCAN_UPLOADS_FOR_MALWARE=false

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
COMPRESSION_LEVEL=6
PARALLEL_PROCESSING=true
```

### Filter Types
- **blur**: Gaussian blur with adjustable radius
- **sharpen**: Image sharpening enhancement
- **edge_detect**: Edge detection and highlighting
- **emboss**: 3D emboss effect
- **contour**: Contour detection
- **smooth**: Noise reduction smoothing
- **detail**: Detail enhancement
- **find_edges**: Edge finding algorithm

### Adjustment Types
- **brightness**: Brightness adjustment (0.0 - 2.0)
- **contrast**: Contrast modification (0.0 - 2.0)
- **saturation**: Color saturation control (0.0 - 2.0)
- **hue**: Color hue adjustment (0.0 - 360.0)
- **sharpness**: Sharpness enhancement (0.0 - 2.0)
- **gamma**: Gamma correction (0.1 - 3.0)

### Resize Methods
- **nearest**: Nearest neighbor interpolation
- **bilinear**: Bilinear interpolation
- **bicubic**: Bicubic interpolation
- **lanczos**: Lanczos resampling (highest quality)

## 📈 Use Cases

### E-commerce
- **Product Images**: Resize and optimize product photos
- **Image Enhancement**: Improve product photo quality
- **Watermarking**: Add watermarks to protected images
- **Format Conversion**: Convert images for different platforms

### Social Media
- **Avatar Processing**: Resize and crop profile pictures
- **Image Filters**: Apply artistic filters to user photos
- **Auto-enhancement**: Automatically improve photo quality
- **Thumbnail Generation**: Create thumbnails from large images

### Content Management
- **Image Optimization**: Reduce file sizes while maintaining quality
- **Batch Processing**: Process multiple images simultaneously
- **Format Standardization**: Convert all images to standard formats
- **Quality Analysis**: Assess image quality before publishing

### Photography
- **Photo Enhancement**: Professional photo editing features
- **Color Correction**: Automatic color balance adjustment
- **Noise Reduction**: Remove digital noise from photos
- **Artistic Effects**: Apply creative filters and effects

## 🛡️ Security Features

### File Security
- **File Type Validation**: Only allow image file uploads
- **Size Limits**: Restrict maximum file sizes
- **Malware Scanning**: Optional malware detection
- **Content Validation**: Verify image file integrity

### Processing Security
- **Resource Limits**: Prevent resource exhaustion
- **Timeout Protection**: Limit processing time
- **Memory Management**: Control memory usage
- **Access Control**: Restrict processing access

## 📊 Monitoring

### Processing Metrics
- **Processing Time**: Track image processing duration
- **Success Rate**: Monitor successful processing
- **Error Tracking**: Log processing errors
- **Resource Usage**: Monitor CPU and memory usage

### Quality Metrics
- **Image Quality Scores**: Automated quality assessment
- **Format Distribution**: Track image format usage
- **Size Reduction**: Monitor compression effectiveness
- **User Satisfaction**: Track user feedback

## 🔗 Related APIs

- **File Storage API**: For image storage and management
- **AI Vision API**: For advanced computer vision features
- **Content Moderation API**: For image content filtering
- **Analytics API**: For processing analytics and metrics

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This API provides comprehensive image processing capabilities. For production use, consider:
- **GPU Acceleration**: Use GPU processing for faster performance
- **Cloud Storage**: Integrate with cloud storage services
- **CDN Integration**: Use CDN for image delivery
- **Advanced AI**: Integrate with ML services for AI features
- **Load Balancing**: Handle high-volume processing requests
