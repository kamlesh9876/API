# File Compression API

A comprehensive file compression service supporting multiple formats and optimization levels. Built with FastAPI, this service provides advanced compression capabilities including batch processing, password protection, and real-time progress tracking.

## 🚀 Features

### Compression Capabilities
- **Multiple Formats**: Support for ZIP, GZIP, TAR, 7Z, and more
- **Compression Levels**: From fastest to ultra compression
- **Batch Processing**: Compress multiple files simultaneously
- **Password Protection**: Secure archives with password encryption
- **Split Archives**: Split large archives into smaller chunks
- **Pattern Filtering**: Include/exclude files with patterns

### Decompression Features
- **Format Support**: Decompress all supported archive formats
- **Password Support**: Handle password-protected archives
- **Structure Preservation**: Maintain directory structure
- **Selective Extraction**: Extract specific files or folders
- **Overwrite Control**: Choose how to handle existing files

### Advanced Features
- **Background Processing**: Async compression/decompression jobs
- **Progress Tracking**: Real-time progress updates
- **Job Management**: Queue, monitor, and cancel jobs
- **File Management**: Store and manage compressed files
- **Analytics**: Compression statistics and performance metrics
- **API Integration**: RESTful API with comprehensive endpoints

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Async Support**: Full async/await implementation
- **File Handling**: UploadFile, FileResponse
- **Background Tasks**: Asyncio for long-running operations
- **Enum Types**: Type-safe format and level management

## 📋 API Endpoints

### Compression

#### Compress Multiple Files
```http
POST /api/compress
Content-Type: multipart/form-data

files: [File1, File2, File3]
format: zip
level: normal
password: optional_password
split_size: 100
delete_original: false
preserve_structure: true
exclude_patterns: "*.tmp,*.log"
include_patterns: "*.txt,*.pdf"
```

#### Compress Single File
```http
POST /api/compress-single
Content-Type: multipart/form-data

file: [File]
format: zip
level: maximum
password: optional_password
```

### Decompression

#### Decompress Archive
```http
POST /api/decompress
Content-Type: multipart/form-data

file: [Archive File]
password: optional_password
extract_to: /path/to/extract
preserve_structure: true
overwrite: false
```

### Job Management

#### List Jobs
```http
GET /api/jobs?status=completed&operation=compress&limit=50&offset=0
```

#### Get Job Details
```http
GET /api/jobs/{job_id}
```

#### Cancel Job
```http
DELETE /api/jobs/{job_id}
```

### File Management

#### List Files
```http
GET /api/files?format=zip&limit=50&offset=0
```

#### Get File Details
```http
GET /api/files/{file_id}
```

#### Download File
```http
GET /api/files/{file_id}/download
```

#### Delete File
```http
DELETE /api/files/{file_id}
```

### Analytics

#### Get Statistics
```http
GET /api/stats
```

#### Get Supported Formats
```http
GET /api/formats
```

## 📊 Data Models

### CompressionRequest
```python
class CompressionRequest(BaseModel):
    format: CompressionFormat
    level: CompressionLevel = CompressionLevel.NORMAL
    password: Optional[str] = None
    split_size: Optional[int] = None
    delete_original: bool = False
    preserve_structure: bool = True
    exclude_patterns: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
```

### CompressionJob
```python
class CompressionJob(BaseModel):
    id: Optional[str] = None
    operation: str
    files: List[str]
    output_file: str
    format: CompressionFormat
    level: CompressionLevel
    status: FileStatus = FileStatus.PENDING
    progress: float = 0.0
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0
    metadata: Optional[Dict[str, Any]] = {}
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart aiofiles

# Install compression libraries
pip install py7zr zipfile gzip tarfile

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
MAX_FILE_SIZE=100MB
MAX_BATCH_SIZE=50
COMPRESSION_TIMEOUT=3600
STORAGE_PATH=./compressed_files
TEMP_PATH=./temp
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Compress multiple files
files = [
    ('files', open('document1.pdf', 'rb')),
    ('files', open('document2.txt', 'rb')),
    ('files', open('image.png', 'rb'))
]

data = {
    'format': 'zip',
    'level': 'normal',
    'password': 'secure123',
    'preserve_structure': 'true'
}

response = requests.post(
    "http://localhost:8000/api/compress",
    files=files,
    data=data
)

if response.status_code == 200:
    result = response.json()
    print(f"Compression started with job ID: {result['job_id']}")
    
    # Check job status
    job_response = requests.get(f"http://localhost:8000/api/jobs/{result['job_id']}")
    job_data = job_response.json()
    print(f"Job status: {job_data['job']['status']}")
    print(f"Progress: {job_data['job']['progress']}%")

# Decompress file
with open('archive.zip', 'rb') as f:
    files = [('file', f)]
    data = {
        'password': 'secure123',
        'preserve_structure': 'true'
    }
    
    decompress_response = requests.post(
        "http://localhost:8000/api/decompress",
        files=files,
        data=data
    )
    
    print(f"Decompression: {decompress_response.json()}")

# Get statistics
stats_response = requests.get("http://localhost:8000/api/stats")
stats = stats_response.json()
print(f"Compression statistics: {stats['statistics']}")
```

### JavaScript Client
```javascript
// Compress files using fetch
const formData = new FormData();
const files = [
    new File(['content'], 'document1.txt'),
    new File(['content'], 'document2.txt')
];

files.forEach(file => {
    formData.append('files', file);
});

formData.append('format', 'zip');
formData.append('level', 'maximum');
formData.append('password', 'secure123');

fetch('http://localhost:8000/api/compress', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Compression started:', data);
    
    // Poll job status
    const jobId = data.job_id;
    const checkStatus = () => {
        fetch(`http://localhost:8000/api/jobs/${jobId}`)
        .then(response => response.json())
        .then(jobData => {
            console.log(`Job status: ${jobData.job.status}, Progress: ${jobData.job.progress}%`);
            
            if (jobData.job.status === 'completed') {
                console.log('Compression completed!');
            } else if (jobData.job.status === 'processing') {
                setTimeout(checkStatus, 2000); // Check again in 2 seconds
            }
        });
    };
    
    checkStatus();
})
.catch(error => console.error('Error:', error));
```

## 🔧 Configuration

### Environment Variables
```bash
# File Handling
MAX_FILE_SIZE=100MB
MAX_BATCH_SIZE=50
MAX_CONCURRENT_JOBS=10
COMPRESSION_TIMEOUT=3600

# Storage Configuration
STORAGE_PATH=./compressed_files
TEMP_PATH=./temp
CLEANUP_INTERVAL_HOURS=24
RETENTION_DAYS=30

# Compression Settings
DEFAULT_FORMAT=zip
DEFAULT_LEVEL=normal
MAX_SPLIT_SIZE=1000MB
PASSWORD_MIN_LENGTH=8

# Performance
WORKER_THREADS=4
QUEUE_SIZE=1000
PROGRESS_UPDATE_INTERVAL=1

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
API_KEY_REQUIRED=false
MAX_PASSWORD_ATTEMPTS=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/compression.log
AUDIT_LOG_ENABLED=true
```

### Compression Formats
- **ZIP**: Standard ZIP format with password support
- **GZIP**: GZIP compression for single files
- **TAR**: TAR archive without compression
- **TAR.GZ**: TAR archive with GZIP compression
- **7Z**: 7-Zip format with high compression ratio
- **TAR.BZ2**: TAR archive with BZIP2 compression

### Compression Levels
- **none**: No compression (store only)
- **fastest**: Fastest compression, lower ratio
- **fast**: Fast compression, good balance
- **normal**: Standard compression (default)
- **maximum**: High compression, slower
- **ultra**: Maximum compression, slowest

## 📈 Use Cases

### Data Backup
- **File Archiving**: Compress old files for storage
- **Backup Creation**: Create compressed backups
- **Incremental Backups**: Compress only changed files
- **Cloud Storage**: Reduce storage costs

### File Transfer
- **Email Attachments**: Compress large attachments
- **Web Uploads**: Reduce upload times
- **API Responses**: Compress response data
- **Mobile Apps**: Reduce data usage

### Content Delivery
- **Static Assets**: Compress CSS, JS, images
- **Media Files**: Compress videos and audio
- **Document Distribution**: Share compressed documents
- **Software Distribution**: Package applications

## 🛡️ Security Features

### File Security
- **Password Protection**: Encrypt archives with passwords
- **File Type Validation**: Validate uploaded file types
- **Size Limits**: Prevent oversized uploads
- **Malware Scanning**: Optional malware detection
- **Access Control**: Restrict file access

### API Security
- **CORS Support**: Cross-origin request handling
- **Input Validation**: Comprehensive input validation
- **Rate Limiting**: API rate limiting
- **Authentication**: Optional API key protection
- **Audit Logging**: Track all operations

## 📊 Monitoring

### Compression Metrics
- **Compression Ratio**: Average compression achieved
- **Processing Speed**: Files processed per second
- **Success Rate**: Percentage of successful operations
- **Storage Savings**: Total space saved
- **Queue Length**: Number of pending jobs

### Performance Metrics
- **Job Duration**: Average processing time
- **Memory Usage**: Memory consumption during compression
- **CPU Usage**: CPU utilization
- **Disk I/O**: Read/write operations
- **Network Usage**: Bandwidth consumption

## 🔗 Related APIs

- **File Storage API**: For storing compressed files
- **Backup Service API**: For automated backups
- **Data Validation API**: For validating file integrity
- **Analytics API**: For detailed compression analytics

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API. In production, integrate with actual compression libraries like:
- **zipfile**: Built-in ZIP support
- **py7zr**: 7-Zip compression
- **gzip**: GZIP compression
- **tarfile**: TAR archive support
- **lz4**: LZ4 fast compression
- **zstandard**: Zstandard compression
