from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from enum import Enum
import uvicorn
import secrets
import hashlib
import jwt
from collections import defaultdict

app = FastAPI(title="Notes/Todo REST API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer()

# Enums
class NoteType(str, Enum):
    NOTE = "note"
    TODO = "todo"
    CHECKLIST = "checklist"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class ChecklistItem(BaseModel):
    id: Optional[int] = None
    text: str
    completed: bool = False

class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    note_type: NoteType = NoteType.NOTE
    priority: Priority = Priority.MEDIUM
    tags: List[str] = []
    reminder_at: Optional[datetime] = None
    due_date: Optional[date] = None
    checklist_items: Optional[List[ChecklistItem]] = None
    is_pinned: bool = False

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[NoteType] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    reminder_at: Optional[datetime] = None
    due_date: Optional[date] = None
    checklist_items: Optional[List[ChecklistItem]] = None
    is_pinned: Optional[bool] = None
    task_status: Optional[TaskStatus] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    note_type: NoteType
    priority: Priority
    tags: List[str]
    reminder_at: Optional[datetime]
    due_date: Optional[date]
    checklist_items: List[ChecklistItem]
    is_pinned: bool
    task_status: Optional[TaskStatus]
    created_at: datetime
    updated_at: datetime
    user_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]

class CloudSync(BaseModel):
    last_sync_at: datetime
    device_id: str
    sync_token: str

# In-memory database (for demo purposes)
users_db = []
notes_db = []
next_user_id = 1
next_note_id = 1
next_checklist_item_id = 1

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = next((u for u in users_db if u["id"] == int(user_id)), None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Create default admin user
def create_default_admin():
    global next_user_id
    admin_user = {
        "id": next_user_id,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": hash_password("admin123"),
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "created_at": datetime.now(),
        "last_login": None,
        "refresh_tokens": []
    }
    users_db.append(admin_user)
    next_user_id += 1

# Initialize with admin user
create_default_admin()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Notes/Todo REST API", "version": "1.0.0"}

# Authentication endpoints
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user"""
    # Check if user already exists
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    global next_user_id
    new_user = {
        "id": next_user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "full_name": user.full_name,
        "role": UserRole.USER,
        "created_at": datetime.now(),
        "last_login": None,
        "refresh_tokens": []
    }
    
    users_db.append(new_user)
    next_user_id += 1
    
    return UserResponse(**new_user)

@app.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """User login"""
    user = next((u for u in users_db if u["email"] == login_data.email), None)
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user["last_login"] = datetime.now()
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user["id"]), "email": user["email"]}
    )
    
    # Store refresh token
    user["refresh_tokens"].append(refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

# Notes endpoints
@app.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    """Create a new note or todo item"""
    global next_note_id, next_checklist_item_id
    
    # Process checklist items
    checklist_items = []
    if note.checklist_items:
        for item in note.checklist_items:
            checklist_items.append({
                "id": next_checklist_item_id,
                "text": item.text,
                "completed": item.completed
            })
            next_checklist_item_id += 1
    
    # Create note
    new_note = {
        "id": next_note_id,
        "title": note.title,
        "content": note.content,
        "note_type": note.note_type,
        "priority": note.priority,
        "tags": note.tags,
        "reminder_at": note.reminder_at,
        "due_date": note.due_date,
        "checklist_items": checklist_items,
        "is_pinned": note.is_pinned,
        "task_status": TaskStatus.PENDING if note.note_type == NoteType.TODO else None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "user_id": current_user["id"]
    }
    
    notes_db.append(new_note)
    next_note_id += 1
    
    return NoteResponse(**new_note)

@app.get("/notes", response_model=List[NoteResponse])
async def get_notes(
    current_user: dict = Depends(get_current_user),
    note_type: Optional[NoteType] = None,
    priority: Optional[Priority] = None,
    task_status: Optional[TaskStatus] = None,
    tags: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get user's notes with filtering and pagination"""
    user_notes = [note for note in notes_db if note["user_id"] == current_user["id"]]
    
    # Apply filters
    if note_type:
        user_notes = [note for note in user_notes if note["note_type"] == note_type]
    
    if priority:
        user_notes = [note for note in user_notes if note["priority"] == priority]
    
    if task_status:
        user_notes = [note for note in user_notes if note["task_status"] == task_status]
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        user_notes = [note for note in user_notes if any(tag in note["tags"] for tag in tag_list)]
    
    if is_pinned is not None:
        user_notes = [note for note in user_notes if note["is_pinned"] == is_pinned]
    
    # Sort by pinned status and updated date
    user_notes.sort(key=lambda x: (not x["is_pinned"], x["updated_at"]), reverse=True)
    
    # Apply pagination
    return user_notes[offset:offset + limit]

@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, current_user: dict = Depends(get_current_user)):
    """Get a specific note"""
    note = next((n for n in notes_db if n["id"] == note_id and n["user_id"] == current_user["id"]), None)
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteResponse(**note)

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a note"""
    note = next((n for n in notes_db if n["id"] == note_id and n["user_id"] == current_user["id"]), None)
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update fields
    if note_update.title is not None:
        note["title"] = note_update.title
    
    if note_update.content is not None:
        note["content"] = note_update.content
    
    if note_update.note_type is not None:
        note["note_type"] = note_update.note_type
    
    if note_update.priority is not None:
        note["priority"] = note_update.priority
    
    if note_update.tags is not None:
        note["tags"] = note_update.tags
    
    if note_update.reminder_at is not None:
        note["reminder_at"] = note_update.reminder_at
    
    if note_update.due_date is not None:
        note["due_date"] = note_update.due_date
    
    if note_update.checklist_items is not None:
        global next_checklist_item_id
        checklist_items = []
        for item in note_update.checklist_items:
            if item.id is None:
                checklist_items.append({
                    "id": next_checklist_item_id,
                    "text": item.text,
                    "completed": item.completed
                })
                next_checklist_item_id += 1
            else:
                checklist_items.append({
                    "id": item.id,
                    "text": item.text,
                    "completed": item.completed
                })
        note["checklist_items"] = checklist_items
    
    if note_update.is_pinned is not None:
        note["is_pinned"] = note_update.is_pinned
    
    if note_update.task_status is not None:
        note["task_status"] = note_update.task_status
    
    note["updated_at"] = datetime.now()
    
    return NoteResponse(**note)

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a note"""
    note_index = next((i for i, n in enumerate(notes_db) if n["id"] == note_id and n["user_id"] == current_user["id"]), None)
    
    if note_index is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    del notes_db[note_index]
    
    return {"message": "Note deleted successfully"}

# Search and filter endpoints
@app.get("/notes/search", response_model=List[NoteResponse])
async def search_notes(
    q: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 50
):
    """Search notes by title, content, or tags"""
    user_notes = [note for note in notes_db if note["user_id"] == current_user["id"]]
    query = q.lower()
    
    results = []
    for note in user_notes:
        if (query in note["title"].lower() or 
            (note["content"] and query in note["content"].lower()) or
            any(query in tag.lower() for tag in note["tags"])):
            results.append(note)
    
    return results[:limit]

@app.get("/notes/tags", response_model=List[str])
async def get_user_tags(current_user: dict = Depends(get_current_user)):
    """Get all tags used by the user"""
    user_notes = [note for note in notes_db if note["user_id"] == current_user["id"]]
    all_tags = set()
    
    for note in user_notes:
        all_tags.update(note["tags"])
    
    return sorted(list(all_tags))

# Reminder endpoints
@app.get("/notes/reminders", response_model=List[NoteResponse])
async def get_upcoming_reminders(
    current_user: dict = Depends(get_current_user),
    days: int = 7
):
    """Get notes with upcoming reminders"""
    user_notes = [note for note in notes_db if note["user_id"] == current_user["id"]]
    now = datetime.now()
    future_date = now + timedelta(days=days)
    
    reminder_notes = [
        note for note in user_notes 
        if note["reminder_at"] and now <= note["reminder_at"] <= future_date
    ]
    
    return sorted(reminder_notes, key=lambda x: x["reminder_at"])

# Statistics and analytics
@app.get("/notes/stats")
async def get_notes_stats(current_user: dict = Depends(get_current_user)):
    """Get user's notes statistics"""
    user_notes = [note for note in notes_db if note["user_id"] == current_user["id"]]
    
    total_notes = len(user_notes)
    notes_by_type = defaultdict(int)
    notes_by_priority = defaultdict(int)
    notes_by_status = defaultdict(int)
    
    completed_todos = 0
    pending_todos = 0
    overdue_todos = 0
    
    today = date.today()
    
    for note in user_notes:
        notes_by_type[note["note_type"].value] += 1
        notes_by_priority[note["priority"].value] += 1
        
        if note["task_status"]:
            notes_by_status[note["task_status"].value] += 1
            if note["task_status"] == TaskStatus.COMPLETED:
                completed_todos += 1
            elif note["task_status"] == TaskStatus.PENDING:
                pending_todos += 1
                if note["due_date"] and note["due_date"] < today:
                    overdue_todos += 1
    
    # Tag statistics
    all_tags = []
    for note in user_notes:
        all_tags.extend(note["tags"])
    
    tag_counts = defaultdict(int)
    for tag in all_tags:
        tag_counts[tag] += 1
    
    return {
        "total_notes": total_notes,
        "notes_by_type": dict(notes_by_type),
        "notes_by_priority": dict(notes_by_priority),
        "notes_by_status": dict(notes_by_status),
        "completed_todos": completed_todos,
        "pending_todos": pending_todos,
        "overdue_todos": overdue_todos,
        "pinned_notes": len([n for n in user_notes if n["is_pinned"]]),
        "notes_with_reminders": len([n for n in user_notes if n["reminder_at"]]),
        "top_tags": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    }

# Cloud sync endpoints
@app.post("/sync/upload")
async def upload_notes(
    notes: List[NoteCreate],
    current_user: dict = Depends(get_current_user),
    device_id: Optional[str] = None
):
    """Upload notes for cloud sync"""
    uploaded_notes = []
    
    for note_data in notes:
        global next_note_id, next_checklist_item_id
        
        # Process checklist items
        checklist_items = []
        if note_data.checklist_items:
            for item in note_data.checklist_items:
                checklist_items.append({
                    "id": next_checklist_item_id,
                    "text": item.text,
                    "completed": item.completed
                })
                next_checklist_item_id += 1
        
        # Create note
        new_note = {
            "id": next_note_id,
            "title": note_data.title,
            "content": note_data.content,
            "note_type": note_data.note_type,
            "priority": note_data.priority,
            "tags": note_data.tags,
            "reminder_at": note_data.reminder_at,
            "due_date": note_data.due_date,
            "checklist_items": checklist_items,
            "is_pinned": note_data.is_pinned,
            "task_status": TaskStatus.PENDING if note_data.note_type == NoteType.TODO else None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": current_user["id"]
        }
        
        notes_db.append(new_note)
        uploaded_notes.append(NoteResponse(**new_note))
        next_note_id += 1
    
    sync_token = secrets.token_urlsafe(32)
    
    return {
        "uploaded_count": len(uploaded_notes),
        "notes": uploaded_notes,
        "sync_token": sync_token,
        "sync_time": datetime.now()
    }

@app.get("/sync/download")
async def download_notes(
    current_user: dict = Depends(get_current_user),
    last_sync: Optional[datetime] = None
):
    """Download notes for cloud sync"""
    user_notes = [note for note in notes_db if note["user_id"] == current_user["id"]]
    
    if last_sync:
        user_notes = [note for note in user_notes if note["updated_at"] > last_sync]
    
    return {
        "notes": user_notes,
        "sync_time": datetime.now(),
        "count": len(user_notes)
    }

@app.post("/sync/merge")
async def merge_notes(
    notes: List[NoteResponse],
    current_user: dict = Depends(get_current_user)
):
    """Merge notes from multiple devices"""
    merged_count = 0
    conflicts = []
    
    for note_data in notes:
        existing_note = next((n for n in notes_db if n["id"] == note_data.id and n["user_id"] == current_user["id"]), None)
        
        if existing_note:
            # Check for conflicts (simplified - in production, use more sophisticated conflict resolution)
            if existing_note["updated_at"] > note_data.updated_at:
                conflicts.append({
                    "note_id": note_data.id,
                    "title": note_data.title,
                    "reason": "Server version is newer"
                })
            else:
                # Update existing note
                existing_note.update({
                    "title": note_data.title,
                    "content": note_data.content,
                    "note_type": note_data.note_type,
                    "priority": note_data.priority,
                    "tags": note_data.tags,
                    "reminder_at": note_data.reminder_at,
                    "due_date": note_data.due_date,
                    "checklist_items": note_data.checklist_items,
                    "is_pinned": note_data.is_pinned,
                    "task_status": note_data.task_status,
                    "updated_at": datetime.now()
                })
                merged_count += 1
        else:
            # Create new note
            new_note = {
                "id": note_data.id,
                "title": note_data.title,
                "content": note_data.content,
                "note_type": note_data.note_type,
                "priority": note_data.priority,
                "tags": note_data.tags,
                "reminder_at": note_data.reminder_at,
                "due_date": note_data.due_date,
                "checklist_items": note_data.checklist_items,
                "is_pinned": note_data.is_pinned,
                "task_status": note_data.task_status,
                "created_at": note_data.created_at,
                "updated_at": datetime.now(),
                "user_id": current_user["id"]
            }
            notes_db.append(new_note)
            merged_count += 1
    
    return {
        "merged_count": merged_count,
        "conflicts": conflicts,
        "sync_time": datetime.now()
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "total_users": len(users_db),
        "total_notes": len(notes_db)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
