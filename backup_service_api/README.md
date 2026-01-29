# Backup Service API

A comprehensive backup service providing data protection, recovery, and archival capabilities. Built with FastAPI, this service offers multiple backup strategies, storage options, and automated scheduling with real-time monitoring.

## 🚀 Features

### Backup Operations
- **Multiple Backup Types**: Full, incremental, differential, and mirror backups
- **Flexible Storage**: Local, S3, Azure Blob, Google Cloud, FTP, SFTP
- **Compression Options**: ZIP, TAR.GZ, TAR.BZ2, 7Z compression
- **Encryption Support**: AES256 and RSA encryption for secure backups
- **Pattern Filtering**: Include/exclude files with pattern matching
- **Progress Tracking**: Real-time backup progress monitoring

### Restore Operations
- **Selective Restore**: Restore specific files or entire backups
- **Integrity Verification**: Verify backup integrity before restore
- **Permission Handling**: Preserve file permissions and ownership
- **Overwrite Control**: Choose how to handle existing files
- **Restore Monitoring**: Track restore progress and status

### Advanced Features
- **Automated Scheduling**: Cron-based backup scheduling
- **Retention Management**: Automatic cleanup of old backups
- **Backup Verification**: Verify backup completeness and integrity
- **Multi-threading**: Parallel processing for faster backups
- **Delta Backups**: Efficient incremental backups
- **Cross-platform**: Works on Windows, Linux, and macOS

### Monitoring & Analytics
- **Backup Statistics**: Comprehensive backup metrics
- **Storage Analytics**: Monitor storage usage and trends
- **Performance Metrics**: Track backup and restore performance
- **Error Tracking**: Detailed error reporting and logging
- **Success Rates**: Monitor backup success rates

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Async Support**: Full async/await implementation
- **File Operations**: Zipfile, shutil, pathlib for file handling
- **Background Tasks**: Asyncio for long-running operations
- **Storage Backends**: Multiple storage provider support

## 📋 API Endpoints

### Backup Operations

#### Create Backup
```http
POST /api/backup/create
Content-Type: application/json

{
  "name": "daily_backup",
  "source_paths": ["/path/to/data", "/path/to/configs"],
  "backup_type": "full",
  "storage_type": "local",
  "compression": "zip",
  "encryption": "aes256",
  "encryption_key": "your_encryption_key",
  "schedule": "0 2 * * *",
  "retention_days": 30,
  "exclude_patterns": ["*.tmp", "*.log", "cache/"],
  "include_patterns": ["*.json", "*.csv"],
  "metadata": {
    "description": "Daily data backup",
    "environment": "production"
  }
}
```

#### Get Backup Details
```http
GET /api/backup/{backup_id}
```

#### List Backups
```http
GET /api/backup?status=completed&backup_type=full&limit=50&offset=0
```

#### Delete Backup
```http
DELETE /api/backup/{backup_id}
```

#### Download Backup
```http
GET /api/backup/{backup_id}/download
```

### Restore Operations

#### Create Restore
```http
POST /api/restore
Content-Type: application/json

{
  "backup_id": "backup_12345",
  "restore_path": "/path/to/restore",
  "overwrite": false,
  "restore_permissions": true,
  "restore_ownership": true,
  "verify_integrity": true
}
```

#### Get Restore Details
```http
GET /api/restore/{restore_id}
```

### Schedule Management

#### Create Backup Schedule
```http
POST /api/schedule
Content-Type: application/json

{
  "name": "daily_backup_schedule",
  "backup_request": {
    "name": "daily_backup",
    "source_paths": ["/path/to/data"],
    "backup_type": "incremental",
    "storage_type": "s3"
  },
  "cron_expression": "0 2 * * *",
  "is_active": true
}
```

#### List Schedules
```http
GET /api/schedule?is_active=true&limit=50&offset=0
```

### Analytics

#### Get Storage Statistics
```http
GET /api/storage/stats
```

## 📊 Data Models

### BackupRequest
```python
class BackupRequest(BaseModel):
    name: str
    source_paths: List[str]
    backup_type: BackupType = BackupType.FULL
    storage_type: StorageType = StorageType.LOCAL
    compression: CompressionType = CompressionType.ZIP
    encryption: EncryptionType = EncryptionType.NONE
    encryption_key: Optional[str] = None
    schedule: Optional[str] = None
    retention_days: int = 30
    exclude_patterns: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
```

### BackupJob
```python
class BackupJob(BaseModel):
    id: Optional[str] = None
    name: str
    source_paths: List[str]
    backup_type: BackupType
    storage_type: StorageType
    compression: CompressionType
    encryption: EncryptionType
    status: BackupStatus = BackupStatus.PENDING
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    files_processed: int = 0
    total_files: int = 0
    bytes_processed: int = 0
    total_bytes: int = 0
    backup_file_path: Optional[str] = None
    backup_size: int = 0
    error_message: Optional[str] = None
    retention_days: int = 30
    metadata: Optional[Dict[str, Any]] = {}
```

### RestoreRequest
```python
class RestoreRequest(BaseModel):
    backup_id: str
    restore_path: str
    overwrite: bool = False
    restore_permissions: bool = True
    restore_ownership: bool = True
    verify_integrity: bool = True
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

# Install storage backends (optional)
pip install boto3 azure-storage-blob google-cloud-storage

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
BACKUP_STORAGE_PATH=./backups
MAX_CONCURRENT_BACKUPS=5
DEFAULT_RETENTION_DAYS=30
COMPRESSION_LEVEL=6
ENCRYPTION_ENABLED=true

# S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2
S3_BUCKET_NAME=your-backup-bucket

# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_CONTAINER_NAME=backups

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GCS_BUCKET_NAME=your-backup-bucket
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json
import time

# Create a backup
backup_data = {
    "name": "my_app_backup",
    "source_paths": ["/path/to/app/data", "/path/to/app/config"],
    "backup_type": "full",
    "storage_type": "local",
    "compression": "zip",
    "encryption": "none",
    "retention_days": 30,
    "exclude_patterns": ["*.tmp", "*.log", "cache/"],
    "metadata": {
        "environment": "production",
        "application": "my_app"
    }
}

response = requests.post(
    "http://localhost:8000/api/backup/create",
    json=backup_data
)

backup_result = response.json()
backup_id = backup_result["backup_id"]
print(f"Backup created with ID: {backup_id}")

# Monitor backup progress
while True:
    status_response = requests.get(f"http://localhost:8000/api/backup/{backup_id}")
    backup_status = status_response.json()
    
    status = backup_status["backup"]["status"]
    progress = backup_status["backup"]["progress"]
    
    print(f"Backup status: {status}, Progress: {progress:.1f}%")
    
    if status in ["completed", "failed"]:
        break
    
    time.sleep(5)

if status == "completed":
    print("Backup completed successfully!")
    print(f"Backup size: {backup_status['backup']['backup_size']} bytes")
    print(f"Files processed: {backup_status['backup']['files_processed']}")
else:
    print(f"Backup failed: {backup_status['backup']['error_message']}")

# Create a restore
restore_data = {
    "backup_id": backup_id,
    "restore_path": "/path/to/restore",
    "overwrite": False,
    "restore_permissions": True,
    "verify_integrity": True
}

restore_response = requests.post(
    "http://localhost:8000/api/restore",
    json=restore_data
)

restore_result = restore_response.json()
restore_id = restore_result["restore_id"]
print(f"Restore created with ID: {restore_id}")

# Monitor restore progress
while True:
    restore_status_response = requests.get(f"http://localhost:8000/api/restore/{restore_id}")
    restore_status = restore_status_response.json()
    
    status = restore_status["restore"]["status"]
    progress = restore_status["restore"]["progress"]
    
    print(f"Restore status: {status}, Progress: {progress:.1f}%")
    
    if status in ["completed", "failed"]:
        break
    
    time.sleep(5)

if status == "completed":
    print("Restore completed successfully!")
else:
    print(f"Restore failed: {restore_status['restore']['error_message']}")

# Create a backup schedule
schedule_data = {
    "name": "daily_backup_schedule",
    "backup_request": {
        "name": "daily_backup",
        "source_paths": ["/path/to/important/data"],
        "backup_type": "incremental",
        "storage_type": "local",
        "retention_days": 7
    },
    "cron_expression": "0 2 * * *",  # Daily at 2 AM
    "is_active": True
}

schedule_response = requests.post(
    "http://localhost:8000/api/schedule",
    json=schedule_data
)

print(f"Schedule created: {schedule_response.json()}")

# Get storage statistics
stats_response = requests.get("http://localhost:8000/api/storage/stats")
stats = stats_response.json()
print(f"Storage statistics: {stats['statistics']}")
```

### JavaScript Client
```javascript
// Create a backup
const backupData = {
    name: 'my_app_backup',
    source_paths: ['/path/to/app/data', '/path/to/app/config'],
    backup_type: 'full',
    storage_type: 'local',
    compression: 'zip',
    encryption: 'none',
    retention_days: 30,
    exclude_patterns: ['*.tmp', '*.log', 'cache/'],
    metadata: {
        environment: 'production',
        application: 'my_app'
    }
};

fetch('http://localhost:8000/api/backup/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(backupData)
})
.then(response => response.json())
.then(data => {
    console.log('Backup created:', data);
    const backupId = data.backup_id;
    
    // Monitor backup progress
    const monitorBackup = () => {
        fetch(`http://localhost:8000/api/backup/${backupId}`)
        .then(response => response.json())
        .then(backupStatus => {
            const status = backupStatus.backup.status;
            const progress = backupStatus.backup.progress;
            
            console.log(`Backup status: ${status}, Progress: ${progress.toFixed(1)}%`);
            
            if (status === 'completed') {
                console.log('Backup completed successfully!');
                console.log(`Backup size: ${backupStatus.backup.backup_size} bytes`);
            } else if (status === 'failed') {
                console.log(`Backup failed: ${backupStatus.backup.error_message}`);
            } else {
                setTimeout(monitorBackup, 5000); // Check again in 5 seconds
            }
        })
        .catch(error => console.error('Error monitoring backup:', error));
    };
    
    monitorBackup();
})
.catch(error => console.error('Error creating backup:', error));

// Create a restore
const restoreData = {
    backup_id: 'backup_12345',
    restore_path: '/path/to/restore',
    overwrite: false,
    restore_permissions: true,
    verify_integrity: true
};

fetch('http://localhost:8000/api/restore', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(restoreData)
})
.then(response => response.json())
.then(data => {
    console.log('Restore created:', data);
    
    // Monitor restore progress
    const restoreId = data.restore_id;
    const monitorRestore = () => {
        fetch(`http://localhost:8000/api/restore/${restoreId}`)
        .then(response => response.json())
        .then(restoreStatus => {
            const status = restoreStatus.restore.status;
            const progress = restoreStatus.restore.progress;
            
            console.log(`Restore status: ${status}, Progress: ${progress.toFixed(1)}%`);
            
            if (status === 'completed') {
                console.log('Restore completed successfully!');
            } else if (status === 'failed') {
                console.log(`Restore failed: ${restoreStatus.restore.error_message}`);
            } else {
                setTimeout(monitorRestore, 5000);
            }
        })
        .catch(error => console.error('Error monitoring restore:', error));
    };
    
    monitorRestore();
})
.catch(error => console.error('Error creating restore:', error));

// Get storage statistics
fetch('http://localhost:8000/api/storage/stats')
.then(response => response.json())
.then(data => {
    console.log('Storage statistics:', data.statistics);
    console.log(`Total backups: ${data.statistics.total_backups}`);
    console.log(`Storage used: ${(data.statistics.total_storage_used / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Success rate: ${((data.statistics.completed_backups / data.statistics.total_backups) * 100).toFixed(2)}%`);
})
.catch(error => console.error('Error getting stats:', error));
```

## 🔧 Configuration

### Environment Variables
```bash
# Backup Configuration
BACKUP_STORAGE_PATH=./backups
MAX_CONCURRENT_BACKUPS=5
DEFAULT_RETENTION_DAYS=30
COMPRESSION_LEVEL=6
ENCRYPTION_ENABLED=true
DEFAULT_BACKUP_TYPE=full

# Storage Configuration
MAX_STORAGE_SIZE=10GB
STORAGE_CLEANUP_ENABLED=true
STORAGE_WARNING_THRESHOLD=0.9
BACKUP_VERIFICATION_ENABLED=true

# Performance Settings
BACKUP_CHUNK_SIZE=8192
MAX_FILE_SIZE=1GB
PARALLEL_PROCESSING=true
MAX_WORKER_THREADS=4
PROGRESS_UPDATE_INTERVAL=1

# Security
ENCRYPTION_KEY=your_encryption_key
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
API_KEY_REQUIRED=false
BACKUP_ACCESS_LOG_ENABLED=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/backup.log
AUDIT_LOG_ENABLED=true
MAX_LOG_SIZE=100MB
LOG_RETENTION_DAYS=30

# Cloud Storage
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-west-2
S3_BUCKET_NAME=your-backup-bucket

AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_CONTAINER_NAME=backups

GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GCS_BUCKET_NAME=your-backup-bucket
```

### Backup Types
- **full**: Complete backup of all specified files
- **incremental**: Backup only changed files since last backup
- **differential**: Backup all files changed since last full backup
- **mirror**: Create exact mirror of source

### Storage Types
- **local**: Local filesystem storage
- **s3**: Amazon S3 storage
- **azure_blob**: Azure Blob storage
- **google_cloud**: Google Cloud Storage
- **ftp**: FTP server storage
- **sftp**: SFTP server storage

### Compression Types
- **none**: No compression
- **zip**: ZIP compression
- **tar.gz**: TAR with GZIP compression
- **tar.bz2**: TAR with BZIP2 compression
- **7z**: 7-Zip compression

## 📈 Use Cases

### Data Protection
- **Database Backups**: Regular database backups and point-in-time recovery
- **Application Backups**: Complete application state backups
- **File Server Backups**: Network file server backups
- **Configuration Backups**: System and application configuration backups
- **User Data Backups**: User home directory and profile backups

### Disaster Recovery
- **Off-site Backups**: Cloud storage for disaster recovery
- **Automated Recovery**: Automated restore procedures
- **Replication**: Cross-region backup replication
- **Testing**: Regular backup testing and verification
- **Compliance**: Meet regulatory backup requirements

### Business Continuity
- **RTO/RPO**: Meet recovery time and point objectives
- **High Availability**: Ensure business continuity
- **Data Retention**: Long-term data archival
- **Version Control**: Keep multiple backup versions
- **Monitoring**: Proactive backup monitoring and alerting

## 🛡️ Security Features

### Data Protection
- **Encryption**: AES256 and RSA encryption support
- **Access Control**: Role-based access to backups
- **Secure Transfer**: Encrypted data transfer to cloud storage
- **Key Management**: Secure encryption key handling
- **Audit Trail**: Complete audit logging

### Backup Security
- **Integrity Verification**: Verify backup integrity
- **Tamper Detection**: Detect backup tampering
- **Secure Storage**: Secure cloud storage configuration
- **Network Security**: Secure network connections
- **Compliance**: Meet security compliance requirements

## 📊 Monitoring

### Backup Metrics
- **Success Rate**: Percentage of successful backups
- **Backup Size**: Monitor backup size trends
- **Duration**: Track backup completion times
- **Storage Usage**: Monitor storage consumption
- **Error Rates**: Track backup failure rates

### Performance Metrics
- **Throughput**: Data transfer rates
- **Compression Ratio**: Compression effectiveness
- **Resource Usage**: CPU and memory usage
- **Network Usage**: Bandwidth consumption
- **Storage Performance**: I/O performance metrics

## 🔗 Related APIs

- **Storage API**: For storage backend management
- **File Management API**: For file operations
- **Compression API**: For advanced compression options
- **Encryption API**: For encryption key management
- **Monitoring API**: For backup monitoring and alerting

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API. In production, integrate with actual backup solutions like:
- **BorgBackup**: For deduplicated backups
- **Restic**: For secure backups
- **Rclone**: For cloud storage synchronization
- **AWS Backup**: For AWS backup services
- **Azure Backup**: For Azure backup services
