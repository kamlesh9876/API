# File Sharing API

A comprehensive file sharing platform with secure file upload, download, sharing links, folder management, and access control features.

## Features

- **File Upload/Download**: Secure file upload and download with progress tracking
- **Share Links**: Create public, private, password-protected, and time-limited share links
- **Access Control**: Granular permissions and user-based access control
- **Folder Management**: Organize files in hierarchical folder structures
- **File Search**: Search files by name, tags, and metadata
- **Storage Quotas**: User storage quota management and monitoring
- **File Types**: Support for various file types with automatic categorization
- **Security**: Checksum validation, access tokens, and password protection
- **Statistics**: Comprehensive file sharing analytics and metrics

## API Endpoints

### User Management

#### Create User
```http
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "storage_quota": 1073741824
}
```

#### Get User
```http
GET /api/users/{user_id}
```

### File Management

#### Upload File
```http
POST /api/files/upload
Content-Type: multipart/form-data

file: [file]
owner_id: user_123
folder_id: folder_456 (optional)
tags: document,important (optional)
is_public: false (optional)
```

#### Get Files
```http
GET /api/files?owner_id=user_123&file_type=document&is_public=true&limit=50&offset=0
```

#### Get File Info
```http
GET /api/files/{file_id}
```

#### Download File
```http
GET /api/files/{file_id}/download?share_token=abc123&password=mypassword
```

#### Delete File
```http
DELETE /api/files/{file_id}?owner_id=user_123
```

#### Search Files
```http
GET /api/search/files?query=report&owner_id=user_123&file_type=document&limit=20
```

### Share Links

#### Create Share Link
```http
POST /api/files/{file_id}/share
Content-Type: application/json

{
  "share_type": "password_protected",
  "owner_id": "user_123",
  "password": "mypassword",
  "expires_hours": 24,
  "download_limit": 10,
  "permissions": ["read"]
}
```

#### Get Shared File Info
```http
GET /api/share/{share_token}?password=mypassword
```

### Folder Management

#### Create Folder
```http
POST /api/folders
Content-Type: application/json

{
  "name": "Documents",
  "owner_id": "user_123",
  "parent_id": "folder_456"
}
```

#### Get Folder Files
```http
GET /api/folders/{folder_id}/files
```

### Statistics
```http
GET /api/stats
```

## Data Models

### User
```json
{
  "id": "user_123",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "storage_quota": 1073741824,
  "storage_used": 524288000,
  "created_at": "2024-01-01T12:00:00",
  "is_active": true
}
```

### SharedFile
```json
{
  "id": "file_123",
  "name": "annual_report.pdf",
  "original_name": "annual_report.pdf",
  "file_type": "pdf",
  "size": 1048576,
  "mime_type": "application/pdf",
  "checksum": "sha256_hash",
  "owner_id": "user_123",
  "upload_path": "uploads/user_123/file_123",
  "created_at": "2024-01-01T12:00:00",
  "modified_at": "2024-01-01T12:00:00",
  "is_public": false,
  "download_count": 15,
  "tags": ["document", "report", "important"],
  "metadata": {
    "upload_ip": "192.168.1.100",
    "original_size": 1048576
  }
}
```

### ShareLink
```json
{
  "id": "share_123",
  "file_id": "file_123",
  "owner_id": "user_123",
  "share_type": "password_protected",
  "share_token": "abc123def456",
  "password": "mypassword",
  "expires_at": "2024-01-02T12:00:00",
  "download_limit": 10,
  "download_count": 3,
  "created_at": "2024-01-01T12:00:00",
  "is_active": true,
  "permissions": ["read"]
}
```

### Folder
```json
{
  "id": "folder_123",
  "name": "Documents",
  "parent_id": null,
  "owner_id": "user_123",
  "created_at": "2024-01-01T12:00:00",
  "modified_at": "2024-01-01T12:00:00",
  "is_public": false,
  "file_count": 25,
  "size": 52428800
}
```

## Supported File Types

### Documents
- **PDF**: `.pdf`
- **Text**: `.txt`, `.rtf`, `.doc`, `.docx`

### Images
- **Formats**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`

### Videos
- **Formats**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`

### Audio
- **Formats**: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`

### Archives
- **Formats**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`

### Code
- **Languages**: `.py`, `.js`, `.html`, `.css`, `.java`, `.cpp`, `.c`, `.php`

### Office Documents
- **Spreadsheets**: `.xls`, `.xlsx`, `.csv`
- **Presentations**: `.ppt`, `.pptx`

## Share Link Types

### 1. Public
- **Description**: Anyone with the link can access
- **Use Cases**: Public documents, marketing materials
- **Security**: No authentication required

### 2. Private
- **Description**: Only specific users can access
- **Use Cases**: Internal documents, team collaboration
- **Security**: User authentication required

### 3. Password Protected
- **Description**: Requires password to access
- **Use Cases**: Sensitive documents, client files
- **Security**: Password authentication

### 4. Time Limited
- **Description**: Link expires after specified time
- **Use Cases**: Temporary access, event-based sharing
- **Security**: Automatic expiration

### 5. Download Limited
- **Description**: Limited number of downloads
- **Use Cases**: Controlled distribution, trial access
- **Security**: Download count enforcement

## Permission System

### Permission Types
- **Read**: View and download file
- **Write**: Modify file content
- **Delete**: Remove file
- **Share**: Create share links
- **Admin**: Full control over file

### Permission Matrix
| Role | Read | Write | Delete | Share | Admin |
|------|------|-------|--------|-------|-------|
| Owner | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shared User | ✓ | ✓ | ✗ | ✗ | ✗ |
| Public Link | ✓ | ✗ | ✗ | ✗ | ✗ |

## Security Features

### File Security
- **Checksum Validation**: SHA-256 checksum for file integrity
- **Access Control**: Role-based access control
- **Token Security**: Secure share token generation
- **Password Protection**: Optional password protection for shares

### Storage Security
- **Quota Management**: User storage quota enforcement
- **Path Isolation**: User-specific upload directories
- **File Validation**: MIME type and size validation
- **Secure Deletion**: Complete file removal

## Installation

```bash
pip install fastapi uvicorn python-multipart
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
import os

# Create user
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "full_name": "Alice Smith",
    "storage_quota": 1073741824  # 1GB
}

response = requests.post("http://localhost:8000/api/users", json=user_data)
user = response.json()
print(f"Created user: {user['id']}")

# Upload file
file_path = "document.pdf"
with open(file_path, "rb") as f:
    files = {"file": f}
    data = {
        "owner_id": user['id'],
        "tags": "document,important",
        "is_public": "false"
    }
    
    response = requests.post("http://localhost:8000/api/files/upload", files=files, data=data)
    uploaded_file = response.json()
    print(f"Uploaded file: {uploaded_file['id']}")

# Create share link
share_data = {
    "share_type": "password_protected",
    "owner_id": user['id'],
    "password": "secret123",
    "expires_hours": 24,
    "download_limit": 5
}

response = requests.post(f"http://localhost:8000/api/files/{uploaded_file['id']}/share", json=share_data)
share_link = response.json()
print(f"Share token: {share_link['share_token']}")

# Get shared file info
response = requests.get(f"http://localhost:8000/api/share/{share_link['share_token']}", params={"password": "secret123"})
shared_info = response.json()
print(f"Shared file: {shared_info['name']}")

# Download file (simulated)
download_url = f"http://localhost:8000/api/files/{uploaded_file['id']}/download?share_token={share_link['share_token']}&password=secret123"
print(f"Download URL: {download_url}")

# Search files
response = requests.get("http://localhost:8000/api/search/files", params={
    "query": "document",
    "owner_id": user['id'],
    "limit": 10
})
search_results = response.json()

print("Search results:")
for file_result in search_results:
    print(f"  - {file_result['name']} ({file_result['size']} bytes)")
```

### JavaScript Client
```javascript
// Upload file with progress
const uploadFile = async (file, userId, tags = []) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('owner_id', userId);
  formData.append('tags', tags.join(','));
  formData.append('is_public', 'false');

  const response = await fetch('http://localhost:8000/api/files/upload', {
    method: 'POST',
    body: formData
  });

  return response.json();
};

// Create share link
const createShareLink = async (fileId, userId, options = {}) => {
  const shareData = {
    share_type: options.type || 'public',
    owner_id: userId,
    password: options.password,
    expires_hours: options.expiresHours,
    download_limit: options.downloadLimit,
    permissions: options.permissions || ['read']
  };

  const response = await fetch(`http://localhost:8000/api/files/${fileId}/share`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(shareData)
  });

  return response.json();
};

// Download file
const downloadFile = async (fileId, shareToken, password) => {
  const url = new URL(`http://localhost:8000/api/files/${fileId}/download`);
  
  if (shareToken) url.searchParams.set('share_token', shareToken);
  if (password) url.searchParams.set('password', password);

  const response = await fetch(url);
  
  if (response.ok) {
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = response.headers.get('Content-Disposition').split('filename=')[1].replace(/"/g, '');
    a.click();
    window.URL.revokeObjectURL(downloadUrl);
  }
  
  return response;
};

// Usage example
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const fileInput = document.getElementById('fileInput');
  const file = fileInput.files[0];
  const userId = 'user_123';
  
  try {
    const uploadedFile = await uploadFile(file, userId, ['document', 'important']);
    console.log('File uploaded:', uploadedFile);
    
    // Create share link
    const shareLink = await createShareLink(uploadedFile.id, userId, {
      type: 'password_protected',
      password: 'secret123',
      expiresHours: 24
    });
    
    console.log('Share link created:', shareLink);
    
    // Display share info
    const shareInfo = await fetch(`http://localhost:8000/api/share/${shareLink.share_token}?password=secret123`);
    const info = await shareInfo.json();
    
    console.log('Shared file info:', info);
    
  } catch (error) {
    console.error('Error:', error);
  }
});
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=pdf,doc,docx,jpg,png,mp4,mp3,zip

# User Settings
DEFAULT_STORAGE_QUOTA=1073741824
MAX_STORAGE_QUOTA=10737418240

# Security
ENABLE_PASSWORD_PROTECTION=true
SHARE_TOKEN_LENGTH=16
FILE_CHECKSUM_ALGORITHM=sha256

# Database (for persistence)
DATABASE_URL=sqlite:///./file_sharing.db
ENABLE_FILE_METADATA_INDEXING=true

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
MAX_CONCURRENT_UPLOADS=10

# Logging
LOG_LEVEL=info
ENABLE_UPLOAD_LOGGING=true
FILE_ACCESS_LOG_RETENTION_DAYS=30
```

## Use Cases

- **Document Sharing**: Secure document sharing for teams and clients
- **Media Distribution**: Share videos, images, and audio files
- **Software Distribution**: Distribute software packages and updates
- **Educational Resources**: Share course materials and assignments
- **Backup Services**: Personal file backup and synchronization
- **Collaboration**: Team file sharing and version control

## Advanced Features

### Chunked Upload
```python
# Support for large file uploads in chunks
upload_session = await create_upload_session(
    file_id="file_123",
    chunk_size=1048576,  # 1MB chunks
    total_chunks=100
)

# Upload chunks
for chunk_number in range(100):
    chunk_data = get_chunk_data(file_path, chunk_number, chunk_size)
    await upload_chunk(upload_session.id, chunk_number, chunk_data)
```

### Virus Scanning
```python
# Integrate with virus scanning service
def scan_file(file_path: str) -> bool:
    # Integrate with ClamAV or similar service
    scan_result = clamav_scan(file_path)
    return scan_result.is_clean

# Apply during upload
if not scan_file(temp_file_path):
    raise HTTPException(status_code=400, detail="File contains virus")
```

### File Conversion
```python
# Automatic file conversion
def convert_file(file_path: str, target_format: str) -> str:
    if target_format == "pdf" and file_path.endswith(".docx"):
        return convert_docx_to_pdf(file_path)
    elif target_format == "jpg" and file_path.endswith(".png"):
        return convert_png_to_jpg(file_path)
    return file_path
```

## Production Considerations

- **Storage Backend**: Use cloud storage (AWS S3, Google Cloud Storage)
- **Database**: PostgreSQL for metadata and user management
- **CDN Integration**: Content delivery network for fast downloads
- **Load Balancing**: Horizontal scaling for high traffic
- **Backup Strategy**: Regular backups of user files and metadata
- **Security**: HTTPS, rate limiting, input validation
- **Monitoring**: File upload/download metrics and system health
