from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import hashlib
import base64
import os
import shutil
from datetime import datetime, timedelta
from enum import Enum
import random
import mimetypes

app = FastAPI(title="File Sharing API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class FileType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    PDF = "pdf"
    OTHER = "other"

class ShareType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PASSWORD_PROTECTED = "password_protected"
    TIME_LIMITED = "time_limited"
    DOWNLOAD_LIMITED = "download_limited"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"

# Data models
class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    storage_quota: int  # bytes
    storage_used: int = 0
    created_at: datetime
    is_active: bool = True

class SharedFile(BaseModel):
    id: str
    name: str
    original_name: str
    file_type: FileType
    size: int  # bytes
    mime_type: str
    checksum: str
    owner_id: str
    upload_path: str
    created_at: datetime
    modified_at: datetime
    is_public: bool = False
    download_count: int = 0
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ShareLink(BaseModel):
    id: str
    file_id: str
    owner_id: str
    share_type: ShareType
    share_token: str
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    download_limit: Optional[int] = None
    download_count: int = 0
    created_at: datetime
    is_active: bool = True
    permissions: List[Permission] = [Permission.READ]

class Folder(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    owner_id: str
    created_at: datetime
    modified_at: datetime
    is_public: bool = False
    file_count: int = 0
    size: int = 0

class FileShare(BaseModel):
    id: str
    file_id: str
    shared_with_user_id: str
    shared_by_user_id: str
    permissions: List[Permission]
    created_at: datetime
    expires_at: Optional[datetime] = None

class UploadSession(BaseModel):
    id: str
    file_id: str
    owner_id: str
    chunk_size: int
    total_chunks: int
    uploaded_chunks: List[int] = []
    created_at: datetime
    expires_at: datetime
    is_completed: bool = False

class DownloadRequest(BaseModel):
    file_id: str
    share_token: Optional[str] = None
    password: Optional[str] = None

# In-memory storage
users: Dict[str, User] = {}
files: Dict[str, SharedFile] = {}
folders: Dict[str, Folder] = {}
share_links: Dict[str, ShareLink] = {}
file_shares: Dict[str, FileShare] = {}
upload_sessions: Dict[str, UploadSession] = {}

# Utility functions
def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"user_{uuid.uuid4().hex[:8]}"

def generate_file_id() -> str:
    """Generate unique file ID"""
    return f"file_{uuid.uuid4().hex[:8]}"

def generate_share_token() -> str:
    """Generate unique share token"""
    return uuid.uuid4().hex[:16]

def calculate_checksum(content: bytes) -> str:
    """Calculate SHA-256 checksum"""
    return hashlib.sha256(content).hexdigest()

def determine_file_type(filename: str, mime_type: str) -> FileType:
    """Determine file type from filename and MIME type"""
    extension = os.path.splitext(filename)[1].lower()
    
    if extension in ['.pdf']:
        return FileType.PDF
    elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
        return FileType.IMAGE
    elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
        return FileType.VIDEO
    elif extension in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
        return FileType.AUDIO
    elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        return FileType.ARCHIVE
    elif extension in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php']:
        return FileType.CODE
    elif extension in ['.xls', '.xlsx', '.csv']:
        return FileType.SPREADSHEET
    elif extension in ['.ppt', '.pptx']:
        return FileType.PRESENTATION
    elif extension in ['.doc', '.docx', '.txt', '.rtf']:
        return FileType.DOCUMENT
    else:
        return FileType.OTHER

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def check_storage_quota(user: User, additional_size: int) -> bool:
    """Check if user has enough storage quota"""
    return (user.storage_used + additional_size) <= user.storage_quota

def update_user_storage(user_id: str, size_change: int):
    """Update user's storage usage"""
    if user_id in users:
        users[user_id].storage_used += size_change

# API Endpoints
@app.post("/api/users", response_model=User)
async def create_user(username: str, email: str, full_name: str, storage_quota: int = 1073741824):  # 1GB default
    """Create a new user"""
    user_id = generate_user_id()
    
    user = User(
        id=user_id,
        username=username,
        email=email,
        full_name=full_name,
        storage_quota=storage_quota,
        created_at=datetime.now()
    )
    
    users[user_id] = user
    return user

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user information"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.post("/api/files/upload", response_model=SharedFile)
async def upload_file(
    file: UploadFile = File(...),
    owner_id: str = "",
    folder_id: Optional[str] = None,
    tags: Optional[str] = None,
    is_public: bool = False
):
    """Upload a file"""
    if owner_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users[owner_id]
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check storage quota
    if not check_storage_quota(user, file_size):
        raise HTTPException(status_code=413, detail="Storage quota exceeded")
    
    # Generate file ID and path
    file_id = generate_file_id()
    upload_dir = f"uploads/{owner_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file_id)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Calculate checksum and determine file type
    checksum = calculate_checksum(content)
    mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    file_type = determine_file_type(file.filename, mime_type)
    
    # Parse tags
    tag_list = tags.split(",") if tags else []
    
    # Create file record
    shared_file = SharedFile(
        id=file_id,
        name=file.filename,
        original_name=file.filename,
        file_type=file_type,
        size=file_size,
        mime_type=mime_type,
        checksum=checksum,
        owner_id=owner_id,
        upload_path=file_path,
        created_at=datetime.now(),
        modified_at=datetime.now(),
        is_public=is_public,
        tags=tag_list,
        metadata={
            "upload_ip": "127.0.0.1",  # Would get from request
            "original_size": file_size
        }
    )
    
    files[file_id] = shared_file
    update_user_storage(owner_id, file_size)
    
    return shared_file

@app.get("/api/files", response_model=List[SharedFile])
async def get_files(
    owner_id: Optional[str] = None,
    file_type: Optional[FileType] = None,
    is_public: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get files with optional filters"""
    filtered_files = list(files.values())
    
    if owner_id:
        filtered_files = [f for f in filtered_files if f.owner_id == owner_id]
    
    if file_type:
        filtered_files = [f for f in filtered_files if f.file_type == file_type]
    
    if is_public is not None:
        filtered_files = [f for f in filtered_files if f.is_public == is_public]
    
    # Sort by creation date (newest first)
    filtered_files.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_files[offset:offset + limit]

@app.get("/api/files/{file_id}", response_model=SharedFile)
async def get_file(file_id: str):
    """Get specific file information"""
    if file_id not in files:
        raise HTTPException(status_code=404, detail="File not found")
    return files[file_id]

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str, share_token: Optional[str] = None, password: Optional[str] = None):
    """Download a file"""
    if file_id not in files:
        raise HTTPException(status_code=404, detail="File not found")
    
    shared_file = files[file_id]
    
    # Check if file is public or user has access
    if not shared_file.is_public:
        if not share_token:
            raise HTTPException(status_code=403, detail="Access denied - file is private")
        
        # Check share link
        if share_token not in [s.share_token for s in share_links.values()]:
            raise HTTPException(status_code=403, detail="Invalid share token")
        
        # Get share link
        share_link = next(s for s in share_links.values() if s.share_token == share_token)
        
        # Check if share link is active
        if not share_link.is_active:
            raise HTTPException(status_code=403, detail="Share link is inactive")
        
        # Check expiration
        if share_link.expires_at and datetime.now() > share_link.expires_at:
            raise HTTPException(status_code=403, detail="Share link has expired")
        
        # Check download limit
        if share_link.download_limit and share_link.download_count >= share_link.download_limit:
            raise HTTPException(status_code=403, detail="Download limit exceeded")
        
        # Check password
        if share_link.share_type == ShareType.PASSWORD_PROTECTED:
            if not password or password != share_link.password:
                raise HTTPException(status_code=403, detail="Invalid password")
        
        # Increment download count
        share_link.download_count += 1
    
    # Increment file download count
    shared_file.download_count += 1
    
    # Stream file
    def iterfile():
        with open(shared_file.upload_path, "rb") as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type=shared_file.mime_type,
        headers={"Content-Disposition": f"attachment; filename={shared_file.original_name}"}
    )

@app.post("/api/files/{file_id}/share", response_model=ShareLink)
async def create_share_link(
    file_id: str,
    share_type: ShareType,
    owner_id: str,
    password: Optional[str] = None,
    expires_hours: Optional[int] = None,
    download_limit: Optional[int] = None,
    permissions: Optional[List[Permission]] = None
):
    """Create a share link for a file"""
    if file_id not in files:
        raise HTTPException(status_code=404, detail="File not found")
    
    if owner_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    file_record = files[file_id]
    
    if file_record.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="You don't own this file")
    
    share_id = generate_file_id()
    share_token = generate_share_token()
    
    # Calculate expiration
    expires_at = None
    if expires_hours:
        expires_at = datetime.now() + timedelta(hours=expires_hours)
    
    share_link = ShareLink(
        id=share_id,
        file_id=file_id,
        owner_id=owner_id,
        share_type=share_type,
        share_token=share_token,
        password=password,
        expires_at=expires_at,
        download_limit=download_limit,
        created_at=datetime.now(),
        permissions=permissions or [Permission.READ]
    )
    
    share_links[share_id] = share_link
    return share_link

@app.get("/api/share/{share_token}")
async def get_shared_file_info(share_token: str, password: Optional[str] = None):
    """Get shared file information"""
    # Find share link
    share_link = next((s for s in share_links.values() if s.share_token == share_token), None)
    
    if not share_link:
        raise HTTPException(status_code=404, detail="Share link not found")
    
    if not share_link.is_active:
        raise HTTPException(status_code=403, detail="Share link is inactive")
    
    if share_link.expires_at and datetime.now() > share_link.expires_at:
        raise HTTPException(status_code=403, detail="Share link has expired")
    
    if share_link.share_type == ShareType.PASSWORD_PROTECTED:
        if not password or password != share_link.password:
            raise HTTPException(status_code=403, detail="Invalid password")
    
    file_record = files[share_link.file_id]
    
    # Return file info without sensitive data
    return {
        "id": file_record.id,
        "name": file_record.name,
        "file_type": file_record.file_type,
        "size": file_record.size,
        "mime_type": file_record.mime_type,
        "created_at": file_record.created_at,
        "download_count": share_link.download_count,
        "download_limit": share_link.download_limit,
        "expires_at": share_link.expires_at,
        "permissions": share_link.permissions
    }

@app.post("/api/folders", response_model=Folder)
async def create_folder(name: str, owner_id: str, parent_id: Optional[str] = None):
    """Create a new folder"""
    if owner_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    folder_id = generate_file_id()
    
    folder = Folder(
        id=folder_id,
        name=name,
        parent_id=parent_id,
        owner_id=owner_id,
        created_at=datetime.now(),
        modified_at=datetime.now()
    )
    
    folders[folder_id] = folder
    return folder

@app.get("/api/folders/{folder_id}/files", response_model=List[SharedFile])
async def get_folder_files(folder_id: str):
    """Get files in a folder"""
    if folder_id not in folders:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # In a real implementation, this would query files by folder_id
    # For now, return empty list as files don't have folder association in this mock
    return []

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str, owner_id: str):
    """Delete a file"""
    if file_id not in files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_record = files[file_id]
    
    if file_record.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="You don't own this file")
    
    # Delete physical file
    try:
        os.remove(file_record.upload_path)
    except FileNotFoundError:
        pass
    
    # Update storage usage
    update_user_storage(owner_id, -file_record.size)
    
    # Delete file record
    del files[file_id]
    
    # Delete associated share links
    to_delete = [share_id for share_id, share in share_links.items() if share.file_id == file_id]
    for share_id in to_delete:
        del share_links[share_id]
    
    return {"message": "File deleted successfully"}

@app.get("/api/search/files", response_model=List[SharedFile])
async def search_files(
    query: str,
    owner_id: Optional[str] = None,
    file_type: Optional[FileType] = None,
    limit: int = 50
):
    """Search files by name or tags"""
    query_lower = query.lower()
    filtered_files = []
    
    for file_record in files.values():
        # Check if file matches search criteria
        name_match = query_lower in file_record.name.lower()
        tag_match = any(query_lower in tag.lower() for tag in file_record.tags)
        
        if name_match or tag_match:
            if owner_id and file_record.owner_id != owner_id:
                continue
            
            if file_type and file_record.file_type != file_type:
                continue
            
            filtered_files.append(file_record)
    
    # Sort by relevance (name matches first, then tag matches)
    filtered_files.sort(key=lambda x: (query_lower in x.name.lower(), x.created_at), reverse=True)
    
    return filtered_files[:limit]

@app.get("/api/stats")
async def get_file_sharing_stats():
    """Get file sharing platform statistics"""
    total_files = len(files)
    total_folders = len(folders)
    total_share_links = len(share_links)
    total_users = len(users)
    
    # File type distribution
    file_type_distribution = {}
    for file_record in files.values():
        file_type = file_record.file_type.value
        file_type_distribution[file_type] = file_type_distribution.get(file_type, 0) + 1
    
    # Storage statistics
    total_storage = sum(f.size for f in files.values())
    average_file_size = total_storage / total_files if total_files > 0 else 0
    
    # Share link statistics
    share_type_distribution = {}
    active_share_links = 0
    
    for share_link in share_links.values():
        if share_link.is_active:
            active_share_links += 1
        
        share_type = share_link.share_type.value
        share_type_distribution[share_type] = share_type_distribution.get(share_type, 0) + 1
    
    # Most downloaded files
    most_downloaded = sorted(files.values(), key=lambda x: x.download_count, reverse=True)[:5]
    
    return {
        "total_files": total_files,
        "total_folders": total_folders,
        "total_share_links": total_share_links,
        "active_share_links": active_share_links,
        "total_users": total_users,
        "total_storage_bytes": total_storage,
        "total_storage_formatted": format_file_size(total_storage),
        "average_file_size": average_file_size,
        "file_type_distribution": file_type_distribution,
        "share_type_distribution": share_type_distribution,
        "most_downloaded_files": [
            {"id": f.id, "name": f.name, "downloads": f.download_count}
            for f in most_downloaded
        ],
        "supported_file_types": [t.value for t in FileType],
        "supported_share_types": [t.value for t in ShareType]
    }

@app.get("/")
async def root():
    return {"message": "File Sharing API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
