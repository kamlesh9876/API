from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime
import json
import base64

app = FastAPI(
    title="File Compression API",
    description="Advanced file compression service supporting multiple formats and optimization levels",
    version="1.0.0"
)

# Enums
class CompressionFormat(str, Enum):
    ZIP = "zip"
    GZIP = "gzip"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    SEVEN_ZIP = "7z"
    RAR = "rar"
    LZ4 = "lz4"
    ZSTD = "zstd"

class CompressionLevel(str, Enum):
    NONE = "none"
    FASTEST = "fastest"
    FAST = "fast"
    NORMAL = "normal"
    MAXIMUM = "maximum"
    ULTRA = "ultra"

class FileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Data Models
class CompressionRequest(BaseModel):
    format: CompressionFormat
    level: CompressionLevel = CompressionLevel.NORMAL
    password: Optional[str] = None
    split_size: Optional[int] = None  # Split archive into chunks (MB)
    delete_original: bool = False
    preserve_structure: bool = True
    exclude_patterns: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class DecompressionRequest(BaseModel):
    password: Optional[str] = None
    extract_to: Optional[str] = None
    preserve_structure: bool = True
    overwrite: bool = False
    metadata: Optional[Dict[str, Any]] = {}

class CompressionJob(BaseModel):
    id: Optional[str] = None
    operation: str  # compress, decompress
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

class FileInfo(BaseModel):
    name: str
    size: int
    type: str
    compressed_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    checksum: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

# Storage (in production, use proper file storage)
compression_jobs = {}
file_storage = {}
compression_stats = {
    "total_files_compressed": 0,
    "total_files_decompressed": 0,
    "total_size_saved": 0,
    "total_operations": 0,
    "average_compression_ratio": 0.0
}

@app.get("/")
async def root():
    return {"message": "File Compression API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Compression Endpoints
@app.post("/api/compress")
async def compress_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    format: CompressionFormat = CompressionFormat.ZIP,
    level: CompressionLevel = CompressionLevel.NORMAL,
    password: Optional[str] = None,
    split_size: Optional[int] = None,
    delete_original: bool = False,
    preserve_structure: bool = True,
    exclude_patterns: Optional[str] = None,
    include_patterns: Optional[str] = None
):
    """Compress multiple files into a single archive"""
    try:
        job_id = str(uuid.uuid4())
        
        # Parse patterns
        exclude_list = exclude_patterns.split(',') if exclude_patterns else []
        include_list = include_patterns.split(',') if include_patterns else []
        
        # Calculate total original size
        total_size = sum(file.size or 0 for file in files)
        
        # Generate output filename
        output_filename = f"compressed_{job_id}.{format}"
        
        # Create compression job
        job = CompressionJob(
            id=job_id,
            operation="compress",
            files=[file.filename for file in files],
            output_file=output_filename,
            format=format,
            level=level,
            created_at=datetime.now(),
            original_size=total_size,
            metadata={
                "password_protected": bool(password),
                "split_size": split_size,
                "preserve_structure": preserve_structure,
                "exclude_patterns": exclude_list,
                "include_patterns": include_list
            }
        )
        
        compression_jobs[job_id] = job
        
        # Start compression in background
        background_tasks.add_task(compress_files_background, job_id, files, format, level, password, split_size, preserve_structure, exclude_list, include_list)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Compression job started",
            "output_file": output_filename,
            "estimated_time": estimate_compression_time(total_size, format, level)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start compression: {str(e)}")

@app.post("/api/compress-single")
async def compress_single_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    format: CompressionFormat = CompressionFormat.ZIP,
    level: CompressionLevel = CompressionLevel.NORMAL,
    password: Optional[str] = None
):
    """Compress a single file"""
    try:
        job_id = str(uuid.uuid4())
        
        # Generate output filename
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}_compressed.{format}"
        
        # Create compression job
        job = CompressionJob(
            id=job_id,
            operation="compress",
            files=[file.filename],
            output_file=output_filename,
            format=format,
            level=level,
            created_at=datetime.now(),
            original_size=file.size or 0,
            metadata={
                "password_protected": bool(password)
            }
        )
        
        compression_jobs[job_id] = job
        
        # Start compression in background
        background_tasks.add_task(compress_single_file_background, job_id, file, format, level, password)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Single file compression started",
            "output_file": output_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start compression: {str(e)}")

# Decompression Endpoints
@app.post("/api/decompress")
async def decompress_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    password: Optional[str] = None,
    extract_to: Optional[str] = None,
    preserve_structure: bool = True,
    overwrite: bool = False
):
    """Decompress an archive file"""
    try:
        job_id = str(uuid.uuid4())
        
        # Create decompression job
        job = CompressionJob(
            id=job_id,
            operation="decompress",
            files=[file.filename],
            output_file=extract_to or f"extracted_{job_id}",
            format=CompressionFormat.ZIP,  # Will be detected from file
            level=CompressionLevel.NORMAL,
            created_at=datetime.now(),
            original_size=file.size or 0,
            metadata={
                "password_protected": bool(password),
                "preserve_structure": preserve_structure,
                "overwrite": overwrite
            }
        )
        
        compression_jobs[job_id] = job
        
        # Start decompression in background
        background_tasks.add_task(decompress_file_background, job_id, file, password, extract_to, preserve_structure, overwrite)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Decompression job started",
            "extract_to": extract_to or f"extracted_{job_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start decompression: {str(e)}")

# Job Management
@app.get("/api/jobs")
async def list_jobs(
    status: Optional[FileStatus] = None,
    operation: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List compression/decompression jobs"""
    try:
        filtered_jobs = list(compression_jobs.values())
        
        # Apply filters
        if status:
            filtered_jobs = [j for j in filtered_jobs if j.get("status") == status]
        if operation:
            filtered_jobs = [j for j in filtered_jobs if j.get("operation") == operation]
        
        # Apply pagination
        total = len(filtered_jobs)
        paginated_jobs = filtered_jobs[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "jobs": paginated_jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details"""
    if job_id not in compression_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "success": True,
        "job": compression_jobs[job_id]
    }

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    try:
        if job_id not in compression_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = compression_jobs[job_id]
        
        if job["status"] not in [FileStatus.PENDING, FileStatus.PROCESSING]:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled")
        
        job["status"] = FileStatus.CANCELLED
        job["completed_at"] = datetime.now()
        
        return {
            "success": True,
            "message": "Job cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

# File Management
@app.get("/api/files")
async def list_files(
    format: Optional[CompressionFormat] = None,
    limit: int = 50,
    offset: int = 0
):
    """List compressed files"""
    try:
        filtered_files = list(file_storage.values())
        
        if format:
            filtered_files = [f for f in filtered_files if f.get("format") == format]
        
        total = len(filtered_files)
        paginated_files = filtered_files[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "files": paginated_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Get file details"""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "success": True,
        "file": file_storage[file_id]
    }

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """Download compressed file"""
    try:
        if file_id not in file_storage:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_info = file_storage[file_id]
        
        # In production, return actual file
        return {
            "message": "Download endpoint - in production, this would return the actual compressed file",
            "file_info": file_info,
            "download_url": f"/api/files/{file_id}/download"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a compressed file"""
    try:
        if file_id not in file_storage:
            raise HTTPException(status_code=404, detail="File not found")
        
        del file_storage[file_id]
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

# Analytics and Statistics
@app.get("/api/stats")
async def get_compression_stats():
    """Get compression statistics"""
    try:
        # Calculate current stats
        total_jobs = len(compression_jobs)
        completed_jobs = [j for j in compression_jobs.values() if j.get("status") == FileStatus.COMPLETED]
        
        # Calculate average compression ratio
        if completed_jobs:
            avg_ratio = sum(j.get("compression_ratio", 0) for j in completed_jobs) / len(completed_jobs)
        else:
            avg_ratio = 0.0
        
        stats = {
            "total_jobs": total_jobs,
            "completed_jobs": len(completed_jobs),
            "failed_jobs": len([j for j in compression_jobs.values() if j.get("status") == FileStatus.FAILED]),
            "total_files_compressed": compression_stats["total_files_compressed"],
            "total_files_decompressed": compression_stats["total_files_decompressed"],
            "total_size_saved": compression_stats["total_size_saved"],
            "average_compression_ratio": avg_ratio,
            "success_rate": (len(completed_jobs) / total_jobs * 100) if total_jobs > 0 else 0
        }
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/formats")
async def get_supported_formats():
    """Get list of supported compression formats"""
    formats = {
        "compression": [
            {
                "format": "zip",
                "description": "ZIP archive format",
                "extension": ".zip",
                "levels": ["none", "fastest", "fast", "normal", "maximum", "ultra"],
                "password_support": True,
                "split_support": True
            },
            {
                "format": "gzip",
                "description": "GZIP compression",
                "extension": ".gz",
                "levels": ["none", "fastest", "fast", "normal", "maximum", "ultra"],
                "password_support": False,
                "split_support": False
            },
            {
                "format": "tar.gz",
                "description": "TAR archive with GZIP compression",
                "extension": ".tar.gz",
                "levels": ["none", "fastest", "fast", "normal", "maximum", "ultra"],
                "password_support": False,
                "split_support": True
            },
            {
                "format": "7z",
                "description": "7-Zip archive format",
                "extension": ".7z",
                "levels": ["none", "fastest", "fast", "normal", "maximum", "ultra"],
                "password_support": True,
                "split_support": True
            }
        ],
        "decompression": [
            {
                "format": "zip",
                "description": "ZIP archive format",
                "password_support": True
            },
            {
                "format": "gzip",
                "description": "GZIP compressed files",
                "password_support": False
            },
            {
                "format": "tar.gz",
                "description": "TAR with GZIP compression",
                "password_support": False
            },
            {
                "format": "7z",
                "description": "7-Zip archive format",
                "password_support": True
            }
        ]
    }
    
    return {
        "success": True,
        "formats": formats
    }

# Utility Functions
def estimate_compression_time(file_size: int, format: CompressionFormat, level: CompressionLevel) -> str:
    """Estimate compression time based on file size and settings"""
    # Simple estimation algorithm
    base_time = file_size / (1024 * 1024)  # MB
    
    # Format multipliers
    format_multipliers = {
        CompressionFormat.ZIP: 1.0,
        CompressionFormat.GZIP: 0.8,
        CompressionFormat.TAR_GZ: 1.2,
        CompressionFormat.SEVEN_ZIP: 1.5
    }
    
    # Level multipliers
    level_multipliers = {
        CompressionLevel.FASTEST: 0.5,
        CompressionLevel.FAST: 0.7,
        CompressionLevel.NORMAL: 1.0,
        CompressionLevel.MAXIMUM: 2.0,
        CompressionLevel.ULTRA: 3.0
    }
    
    multiplier = format_multipliers.get(format, 1.0) * level_multipliers.get(level, 1.0)
    estimated_seconds = base_time * multiplier
    
    if estimated_seconds < 60:
        return f"{int(estimated_seconds)} seconds"
    elif estimated_seconds < 3600:
        return f"{int(estimated_seconds / 60)} minutes"
    else:
        return f"{int(estimated_seconds / 3600)} hours"

# Background Tasks
async def compress_files_background(
    job_id: str,
    files: List[UploadFile],
    format: CompressionFormat,
    level: CompressionLevel,
    password: Optional[str],
    split_size: Optional[int],
    preserve_structure: bool,
    exclude_patterns: List[str],
    include_patterns: List[str]
):
    """Background task for file compression"""
    try:
        job = compression_jobs[job_id]
        job["status"] = FileStatus.PROCESSING
        job["started_at"] = datetime.now()
        
        # Simulate compression progress
        total_files = len(files)
        for i, file in enumerate(files):
            # Simulate file processing
            await asyncio.sleep(1)  # Simulate processing time
            
            # Update progress
            progress = (i + 1) / total_files * 100
            job["progress"] = progress
        
        # Simulate final compression
        await asyncio.sleep(2)
        
        # Calculate compression results (simulated)
        original_size = sum(f.size or 0 for f in files)
        compression_ratios = {
            CompressionLevel.FASTEST: 0.7,
            CompressionLevel.FAST: 0.6,
            CompressionLevel.NORMAL: 0.5,
            CompressionLevel.MAXIMUM: 0.4,
            CompressionLevel.ULTRA: 0.3
        }
        
        ratio = compression_ratios.get(level, 0.5)
        compressed_size = int(original_size * ratio)
        
        # Update job
        job["status"] = FileStatus.COMPLETED
        job["completed_at"] = datetime.now()
        job["compressed_size"] = compressed_size
        job["compression_ratio"] = (1 - ratio) * 100
        job["progress"] = 100.0
        
        # Store file info
        file_info = {
            "id": str(uuid.uuid4()),
            "filename": job["output_file"],
            "format": format,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": (1 - ratio) * 100,
            "created_at": datetime.now(),
            "job_id": job_id,
            "password_protected": bool(password)
        }
        
        file_storage[file_info["id"]] = file_info
        
        # Update stats
        compression_stats["total_files_compressed"] += total_files
        compression_stats["total_size_saved"] += (original_size - compressed_size)
        compression_stats["total_operations"] += 1
        
    except Exception as e:
        if job_id in compression_jobs:
            compression_jobs[job_id]["status"] = FileStatus.FAILED
            compression_jobs[job_id]["error_message"] = str(e)
            compression_jobs[job_id]["completed_at"] = datetime.now()

async def compress_single_file_background(
    job_id: str,
    file: UploadFile,
    format: CompressionFormat,
    level: CompressionLevel,
    password: Optional[str]
):
    """Background task for single file compression"""
    await compress_files_background(
        job_id, [file], format, level, password, None, True, [], []
    )

async def decompress_file_background(
    job_id: str,
    file: UploadFile,
    password: Optional[str],
    extract_to: Optional[str],
    preserve_structure: bool,
    overwrite: bool
):
    """Background task for file decompression"""
    try:
        job = compression_jobs[job_id]
        job["status"] = FileStatus.PROCESSING
        job["started_at"] = datetime.now()
        
        # Simulate decompression
        await asyncio.sleep(3)
        
        # Update job
        job["status"] = FileStatus.COMPLETED
        job["completed_at"] = datetime.now()
        job["progress"] = 100.0
        
        # Update stats
        compression_stats["total_files_decompressed"] += 1
        compression_stats["total_operations"] += 1
        
    except Exception as e:
        if job_id in compression_jobs:
            compression_jobs[job_id]["status"] = FileStatus.FAILED
            compression_jobs[job_id]["error_message"] = str(e)
            compression_jobs[job_id]["completed_at"] = datetime.now()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
