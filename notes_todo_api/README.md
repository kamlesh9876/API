# Notes/Todo REST API

A comprehensive notes and todo management API built with FastAPI, featuring user authentication, cloud sync, and advanced note organization capabilities.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication system
- **CRUD Operations**: Complete create, read, update, delete for notes
- **Note Types**: Support for notes, todos, and checklists
- **Priority Levels**: Low, Medium, High, Urgent priority system
- **Tag System**: Organize notes with custom tags
- **Reminders**: Set date/time reminders for notes
- **Due Dates**: Track todo deadlines
- **Checklists**: Interactive checklist items within notes
- **Pinned Notes**: Keep important notes at the top
- **Cloud Sync**: Multi-device synchronization
- **Search & Filter**: Advanced search and filtering capabilities
- **Analytics**: Comprehensive statistics and insights

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (with SQLAlchemy)
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Security**: Password hashing, CORS protection

## 📋 Prerequisites

- Python 3.7+
- PostgreSQL database
- pip package manager

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL database**:
```sql
CREATE DATABASE notes_todo;
CREATE USER notes_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE notes_todo TO notes_user;
```

3. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8004`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8004/docs`
- ReDoc: `http://localhost:8004/redoc`

## 🔐 Authentication

### Register User
```http
POST /register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

### User Login
```http
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### Default Admin Account
For testing, a default admin account is available:
- **Email**: admin@example.com
- **Password**: admin123

## 📝 Note Management

### Create Note
```http
POST /notes
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Meeting Notes",
  "content": "Discussion about Q4 targets...",
  "note_type": "note",
  "priority": "high",
  "tags": ["work", "meeting", "q4"],
  "reminder_at": "2024-01-15T09:00:00",
  "is_pinned": true
}
```

### Create Todo
```http
POST /notes
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Complete project proposal",
  "note_type": "todo",
  "priority": "urgent",
  "tags": ["work", "project"],
  "due_date": "2024-01-20",
  "reminder_at": "2024-01-19T09:00:00"
}
```

### Create Checklist
```http
POST /notes
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Shopping List",
  "note_type": "checklist",
  "priority": "medium",
  "tags": ["personal", "shopping"],
  "checklist_items": [
    {"text": "Buy groceries", "completed": false},
    {"text": "Pick up dry cleaning", "completed": true},
    {"text": "Call dentist", "completed": false}
  ]
}
```

### Get Notes
```http
GET /notes?note_type=todo&priority=high&tags=work
Authorization: Bearer <access_token>
```

### Update Note
```http
PUT /notes/{note_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "task_status": "completed",
  "priority": "low"
}
```

### Delete Note
```http
DELETE /notes/{note_id}
Authorization: Bearer <access_token>
```

## 🔍 Search & Filter

### Search Notes
```http
GET /notes/search?q=meeting&limit=20
Authorization: Bearer <access_token>
```

### Get User Tags
```http
GET /notes/tags
Authorization: Bearer <access_token>
```

### Get Upcoming Reminders
```http
GET /notes/reminders?days=7
Authorization: Bearer <access_token>
```

## 📊 Analytics

### Get Statistics
```http
GET /notes/stats
Authorization: Bearer <access_token>
```

**Response Example**:
```json
{
  "total_notes": 45,
  "notes_by_type": {
    "note": 25,
    "todo": 15,
    "checklist": 5
  },
  "notes_by_priority": {
    "low": 10,
    "medium": 20,
    "high": 12,
    "urgent": 3
  },
  "completed_todos": 8,
  "pending_todos": 7,
  "overdue_todos": 2,
  "pinned_notes": 5,
  "notes_with_reminders": 12,
  "top_tags": {
    "work": 15,
    "personal": 8,
    "project": 6
  }
}
```

## ☁️ Cloud Sync

### Upload Notes
```http
POST /sync/upload
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "notes": [
    {
      "title": "New Note",
      "content": "Content...",
      "note_type": "note",
      "priority": "medium"
    }
  ],
  "device_id": "iphone-13-pro"
}
```

### Download Notes
```http
GET /sync/download?last_sync=2024-01-01T00:00:00
Authorization: Bearer <access_token>
```

### Merge Notes
```http
POST /sync/merge
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "notes": [
    {
      "id": 1,
      "title": "Updated Note",
      "content": "Updated content...",
      "updated_at": "2024-01-02T10:00:00"
    }
  ]
}
```

## 📊 Data Models

### Note
```json
{
  "id": 1,
  "title": "Meeting Notes",
  "content": "Discussion content...",
  "note_type": "note",
  "priority": "high",
  "tags": ["work", "meeting"],
  "reminder_at": "2024-01-15T09:00:00",
  "due_date": "2024-01-20",
  "checklist_items": [
    {"id": 1, "text": "Item 1", "completed": false}
  ],
  "is_pinned": true,
  "task_status": "pending",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "user_id": 1
}
```

### User
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "user",
  "created_at": "2024-01-01T12:00:00",
  "last_login": "2024-01-02T09:00:00"
}
```

## 🧪 Testing Examples

### Create and manage a todo
```bash
# Login
curl -X POST http://localhost:8004/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Create todo
curl -X POST http://localhost:8004/notes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete API documentation",
    "note_type": "todo",
    "priority": "high",
    "due_date": "2024-01-15"
  }'

# Get all todos
curl -X GET "http://localhost:8004/notes?note_type=todo" \
  -H "Authorization: Bearer <token>"

# Mark as completed
curl -X PUT http://localhost:8004/notes/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"task_status": "completed"}'
```

### Search and filter
```bash
# Search notes
curl -X GET "http://localhost:8004/notes/search?q=meeting" \
  -H "Authorization: Bearer <token>"

# Get high priority todos
curl -X GET "http://localhost:8004/notes?note_type=todo&priority=high" \
  -H "Authorization: Bearer <token>"

# Get statistics
curl -X GET http://localhost:8004/notes/stats \
  -H "Authorization: Bearer <token>"
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    note_type VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    tags TEXT[],
    reminder_at TIMESTAMP,
    due_date DATE,
    checklist_items JSONB,
    is_pinned BOOLEAN DEFAULT FALSE,
    task_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://notes_user:password@localhost:5432/notes_todo

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Cloud Sync
SYNC_ENCRYPTION_KEY=your-encryption-key
MAX_SYNC_PAYLOAD_SIZE=10485760  # 10MB
```

### PostgreSQL Integration
Replace in-memory storage with SQLAlchemy:

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    full_name = Column(String(100))
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    note_type = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    tags = Column(ARRAY(String))
    reminder_at = Column(DateTime)
    due_date = Column(Date)
    checklist_items = Column(JSON)
    is_pinned = Column(Boolean, default=False)
    task_status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8004

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  notes-api:
    build: .
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql://notes_user:password@postgres:5432/notes_todo
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=notes_todo
      - POSTGRES_USER=notes_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📱 Mobile App Integration

### Sync Protocol
The API supports a robust sync protocol for mobile apps:

1. **Initial Sync**: Download all notes
2. **Incremental Sync**: Only sync changes since last sync
3. **Conflict Resolution**: Server-side conflict detection
4. **Device Management**: Track multiple devices per user

### Offline Support
- Store notes locally
- Queue changes when offline
- Batch sync when connection restored

## 🔍 Advanced Features

### Full-Text Search
```python
# PostgreSQL full-text search
@app.get("/notes/search-fulltext")
async def fulltext_search(q: str, current_user: dict = Depends(get_current_user)):
    query = text("""
        SELECT *, ts_rank(search_vector, plainto_tsquery(:query)) as rank
        FROM notes 
        WHERE user_id = :user_id AND search_vector @@ plainto_tsquery(:query)
        ORDER BY rank DESC
    """)
    
    results = db.execute(query, {"user_id": current_user["id"], "query": q})
    return results.fetchall()
```

### Recurring Reminders
```python
# Support for recurring reminders
class RecurringPattern(BaseModel):
    frequency: str  # daily, weekly, monthly
    interval: int = 1
    end_date: Optional[date] = None
```

### Note Templates
```python
# Predefined note templates
@app.post("/notes/from-template")
async def create_from_template(template_id: int, data: dict):
    # Create note from predefined template
    pass
```

## 🛡️ Security Features

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/notes")
@limiter.limit("10/minute")
async def create_note(request: Request, note: NoteCreate):
    # Rate limited note creation
    pass
```

### Data Encryption
- Encrypt sensitive note content
- Secure cloud sync with end-to-end encryption
- GDPR compliance options

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code comments for implementation details

---

**Built with ❤️ using FastAPI**
