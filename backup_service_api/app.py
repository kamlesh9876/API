from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime, timedelta
import json
import zipfile
import shutil
from pathlib import Path

app = FastAPI(
    title="Backup Service API",
    description="Comprehensive backup service for data protection, recovery, and archival",
    version="1.0.0"
)

# Enums
class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    MIRROR = "mirror"

class BackupStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RESTORING = "restoring"

class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    FTP = "ftp"
    SFTP = "sftp"

class CompressionType(str, Enum):
    NONE = "none"
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    SEVEN_ZIP = "7z"

class EncryptionType(str, Enum):
    NONE = "none"
    AES256 = "aes256"
    RSA = "rsa"

# Data Models
class BackupRequest(BaseModel):
    name: str
    source_paths: List[str]
    backup_type: BackupType = BackupType.FULL
    storage_type: StorageType = StorageType.LOCAL
    compression: CompressionType = CompressionType.ZIP
    encryption: EncryptionType = EncryptionType.NONE
    encryption_key: Optional[str] = None
    schedule: Optional[str] = None  # Cron expression
    retention_days: int = 30
    exclude_patterns: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

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

class RestoreRequest(BaseModel):
    backup_id: str
    restore_path: str
    overwrite: bool = False
    restore_permissions: bool = True
    restore_ownership: bool = True
    verify_integrity: bool = True

class BackupSchedule(BaseModel):
    id: Optional[str] = None
    name: str
    backup_request: BackupRequest
    cron_expression: str
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: Optional[datetime] = None

# Storage (in production, use database)
backup_jobs = {}
backup_schedules = {}
backup_storage = {}
restore_jobs = {}
backup_stats = {
    "total_backups": 0,
    "successful_backups": 0,
    "failed_backups": 0,
    "total_storage_used": 0,
    "average_backup_time": 0.0
}

@app.get("/")
async def root():
    return {"message": "Backup Service API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Backup Operations
@app.post("/api/backup/create")
async def create_backup(request: BackupRequest, background_tasks: BackgroundTasks):
    """Create a new backup job"""
    try:
        backup_id = str(uuid.uuid4())
        
        # Validate source paths
        for path in request.source_paths:
            if not os.path.exists(path):
                raise HTTPException(status_code=400, detail=f"Source path does not exist: {path}")
        
        # Create backup job
        backup_job = BackupJob(
            id=backup_id,
            name=request.name,
            source_paths=request.source_paths,
            backup_type=request.backup_type,
            storage_type=request.storage_type,
            compression=request.compression,
            encryption=request.encryption,
            status=BackupStatus.PENDING,
            created_at=datetime.now(),
            retention_days=request.retention_days,
            metadata=request.metadata
        )
        
        backup_jobs[backup_id] = backup_job
        
        # Start backup in background
        background_tasks.add_task(execute_backup, backup_id, request)
        
        return {
            "success": True,
            "backup_id": backup_id,
            "message": "Backup job created successfully",
            "backup_job": backup_job.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.get("/api/backup/{backup_id}")
async def get_backup(backup_id: str):
    """Get backup job details"""
    if backup_id not in backup_jobs:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    return {
        "success": True,
        "backup": backup_jobs[backup_id]
    }

@app.get("/api/backup")
async def list_backups(
    status: Optional[BackupStatus] = None,
    backup_type: Optional[BackupType] = None,
    limit: int = 50,
    offset: int = 0
):
    """List backup jobs"""
    try:
        filtered_backups = list(backup_jobs.values())
        
        # Apply filters
        if status:
            filtered_backups = [b for b in filtered_backups if b.get("status") == status]
        if backup_type:
            filtered_backups = [b for b in filtered_backups if b.get("backup_type") == backup_type]
        
        # Apply pagination
        total = len(filtered_backups)
        paginated_backups = filtered_backups[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "backups": paginated_backups
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@app.delete("/api/backup/{backup_id}")
async def delete_backup(backup_id: str):
    """Delete a backup job and its files"""
    try:
        if backup_id not in backup_jobs:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        backup_job = backup_jobs[backup_id]
        
        # Delete backup file if exists
        if backup_job.get("backup_file_path") and os.path.exists(backup_job["backup_file_path"]):
            os.remove(backup_job["backup_file_path"])
        
        # Remove from storage
        del backup_jobs[backup_id]
        
        return {
            "success": True,
            "message": "Backup deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete backup: {str(e)}")

# Restore Operations
@app.post("/api/restore")
async def create_restore(request: RestoreRequest, background_tasks: BackgroundTasks):
    """Create a restore job"""
    try:
        if request.backup_id not in backup_jobs:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        restore_id = str(uuid.uuid4())
        
        # Create restore job
        restore_job = {
            "id": restore_id,
            "backup_id": request.backup_id,
            "restore_path": request.restore_path,
            "overwrite": request.overwrite,
            "restore_permissions": request.restore_permissions,
            "restore_ownership": request.restore_ownership,
            "verify_integrity": request.verify_integrity,
            "status": BackupStatus.PENDING,
            "created_at": datetime.now(),
            "progress": 0.0,
            "files_restored": 0,
            "total_files": 0,
            "bytes_restored": 0,
            "total_bytes": 0,
            "error_message": None
        }
        
        restore_jobs[restore_id] = restore_job
        
        # Start restore in background
        background_tasks.add_task(execute_restore, restore_id, request)
        
        return {
            "success": True,
            "restore_id": restore_id,
            "message": "Restore job created successfully",
            "restore_job": restore_job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create restore: {str(e)}")

@app.get("/api/restore/{restore_id}")
async def get_restore(restore_id: str):
    """Get restore job details"""
    if restore_id not in restore_jobs:
        raise HTTPException(status_code=404, detail="Restore job not found")
    
    return {
        "success": True,
        "restore": restore_jobs[restore_id]
    }

# Schedule Operations
@app.post("/api/schedule")
async def create_schedule(schedule: BackupSchedule):
    """Create a backup schedule"""
    try:
        schedule_id = str(uuid.uuid4())
        
        schedule_record = schedule.dict()
        schedule_record["id"] = schedule_id
        schedule_record["created_at"] = datetime.now()
        
        # Calculate next run time (simplified)
        schedule_record["next_run"] = datetime.now() + timedelta(hours=24)  # Daily for demo
        
        backup_schedules[schedule_id] = schedule_record
        
        return {
            "success": True,
            "schedule_id": schedule_id,
            "message": "Backup schedule created successfully",
            "schedule": schedule_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")

@app.get("/api/schedule")
async def list_schedules(
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """List backup schedules"""
    try:
        filtered_schedules = list(backup_schedules.values())
        
        if is_active is not None:
            filtered_schedules = [s for s in filtered_schedules if s.get("is_active") == is_active]
        
        total = len(filtered_schedules)
        paginated_schedules = filtered_schedules[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "schedules": paginated_schedules
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list schedules: {str(e)}")

# Storage and Analytics
@app.get("/api/storage/stats")
async def get_storage_stats():
    """Get storage statistics"""
    try:
        # Calculate storage usage
        total_storage = 0
        backup_count = 0
        
        for backup in backup_jobs.values():
            if backup.get("backup_size"):
                total_storage += backup["backup_size"]
                backup_count += 1
        
        stats = {
            "total_backups": len(backup_jobs),
            "completed_backups": len([b for b in backup_jobs.values() if b.get("status") == BackupStatus.COMPLETED]),
            "failed_backups": len([b for b in backup_jobs.values() if b.get("status") == BackupStatus.FAILED]),
            "total_storage_used": total_storage,
            "average_backup_size": total_storage / backup_count if backup_count > 0 else 0,
            "active_schedules": len([s for s in backup_schedules.values() if s.get("is_active")]),
            "storage_types": {},
            "backup_types": {}
        }
        
        # Storage types breakdown
        for backup in backup_jobs.values():
            storage_type = backup.get("storage_type", "unknown")
            if storage_type not in stats["storage_types"]:
                stats["storage_types"][storage_type] = {"count": 0, "size": 0}
            stats["storage_types"][storage_type]["count"] += 1
            if backup.get("backup_size"):
                stats["storage_types"][storage_type]["size"] += backup["backup_size"]
        
        # Backup types breakdown
        for backup in backup_jobs.values():
            backup_type = backup.get("backup_type", "unknown")
            if backup_type not in stats["backup_types"]:
                stats["backup_types"][backup_type] = 0
            stats["backup_types"][backup_type] += 1
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage stats: {str(e)}")

@app.get("/api/backup/{backup_id}/download")
async def download_backup(backup_id: str):
    """Download backup file"""
    try:
        if backup_id not in backup_jobs:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        backup_job = backup_jobs[backup_id]
        
        if backup_job.get("status") != BackupStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Backup not completed")
        
        backup_file_path = backup_job.get("backup_file_path")
        
        if not backup_file_path or not os.path.exists(backup_file_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        return FileResponse(
            path=backup_file_path,
            filename=f"{backup_job['name']}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download backup: {str(e)}")

# Background Tasks
async def execute_backup(backup_id: str, request: BackupRequest):
    """Execute backup job in background"""
    try:
        backup_job = backup_jobs[backup_id]
        backup_job["status"] = BackupStatus.RUNNING
        backup_job["started_at"] = datetime.now()
        
        # Create backup directory
        backup_dir = Path("./backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{request.name}_{timestamp}.zip"
        backup_file_path = backup_dir / backup_filename
        
        # Calculate total files and size
        total_files = 0
        total_bytes = 0
        
        for source_path in request.source_paths:
            for root, dirs, files in os.walk(source_path):
                total_files += len(files)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_bytes += os.path.getsize(file_path)
                    except OSError:
                        continue
        
        backup_job["total_files"] = total_files
        backup_job["total_bytes"] = total_bytes
        
        # Create backup
        files_processed = 0
        bytes_processed = 0
        
        with zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source_path in request.source_paths:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Apply include/exclude patterns
                        if should_include_file(file_path, request.include_patterns, request.exclude_patterns):
                            try:
                                zipf.write(file_path, os.path.relpath(file_path, source_path))
                                files_processed += 1
                                bytes_processed += os.path.getsize(file_path)
                                
                                # Update progress
                                progress = (files_processed / total_files) * 100 if total_files > 0 else 0
                                backup_job["progress"] = progress
                                backup_job["files_processed"] = files_processed
                                backup_job["bytes_processed"] = bytes_processed
                                
                                # Small delay to prevent blocking
                                await asyncio.sleep(0.01)
                                
                            except OSError:
                                continue
        
        # Update backup job
        backup_job["status"] = BackupStatus.COMPLETED
        backup_job["completed_at"] = datetime.now()
        backup_job["backup_file_path"] = str(backup_file_path)
        backup_job["backup_size"] = os.path.getsize(backup_file_path)
        backup_job["progress"] = 100.0
        
        # Update statistics
        backup_stats["total_backups"] += 1
        backup_stats["successful_backups"] += 1
        backup_stats["total_storage_used"] += backup_job["backup_size"]
        
        # Calculate average backup time
        backup_time = (backup_job["completed_at"] - backup_job["started_at"]).total_seconds()
        total_successful = backup_stats["successful_backups"]
        backup_stats["average_backup_time"] = (
            (backup_stats["average_backup_time"] * (total_successful - 1) + backup_time) / total_successful
        )
        
    except Exception as e:
        if backup_id in backup_jobs:
            backup_jobs[backup_id]["status"] = BackupStatus.FAILED
            backup_jobs[backup_id]["error_message"] = str(e)
            backup_jobs[backup_id]["completed_at"] = datetime.now()
        
        backup_stats["failed_backups"] += 1

async def execute_restore(restore_id: str, request: RestoreRequest):
    """Execute restore job in background"""
    try:
        restore_job = restore_jobs[restore_id]
        restore_job["status"] = BackupStatus.RESTORING
        restore_job["started_at"] = datetime.now()
        
        backup_job = backup_jobs[request.backup_id]
        backup_file_path = backup_job.get("backup_file_path")
        
        if not backup_file_path or not os.path.exists(backup_file_path):
            raise FileNotFoundError("Backup file not found")
        
        # Create restore directory
        restore_path = Path(request.restore_path)
        restore_path.mkdir(parents=True, exist_ok=True)
        
        # Extract backup
        with zipfile.ZipFile(backup_file_path, 'r') as zipf:
            file_list = zipf.namelist()
            restore_job["total_files"] = len(file_list)
            
            files_restored = 0
            
            for file_info in file_list:
                try:
                    zipf.extract(file_info, restore_path)
                    files_restored += 1
                    
                    # Update progress
                    progress = (files_restored / len(file_list)) * 100
                    restore_job["progress"] = progress
                    restore_job["files_restored"] = files_restored
                    
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    # Log error but continue
                    print(f"Error restoring {file_info}: {e}")
        
        restore_job["status"] = BackupStatus.COMPLETED
        restore_job["completed_at"] = datetime.now()
        restore_job["progress"] = 100.0
        
    except Exception as e:
        if restore_id in restore_jobs:
            restore_jobs[restore_id]["status"] = BackupStatus.FAILED
            restore_jobs[restore_id]["error_message"] = str(e)
            restore_jobs[restore_id]["completed_at"] = datetime.now()

def should_include_file(file_path: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
    """Check if file should be included based on patterns"""
    filename = os.path.basename(file_path)
    
    # Check exclude patterns
    for pattern in exclude_patterns:
        if pattern in filename:
            return False
    
    # Check include patterns (if specified)
    if include_patterns:
        for pattern in include_patterns:
            if pattern in filename:
                return True
        return False
    
    return True

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
