# Book Library API

A comprehensive library management system with book catalog, borrowing, ratings, and admin panel. Built with FastAPI for maximum performance and SQLAlchemy for robust data management.

## 🚀 Features

- **Book Catalog Management**: Add, update, delete books with detailed information
- **Borrowing System**: Complete book borrowing and returning with due dates
- **Ratings & Reviews**: 5-star rating system with detailed reviews
- **Genres & Tags**: Organize books with genres and customizable tags
- **User Management**: Role-based access control (Admin, Librarian, Member)
- **Reservations**: Book reservation system for unavailable books
- **Admin Panel**: Comprehensive dashboard with statistics and management
- **Search & Filter**: Advanced search with multiple criteria
- **Fine Management**: Automatic fine calculation for overdue books
- **Real-time Updates**: Book availability and status tracking

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Bearer token with bcrypt password hashing
- **Data Validation**: Pydantic models
- **Security**: Role-based access control
- **ORM**: SQLAlchemy for database operations

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8020`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8020/docs`
- ReDoc: `http://localhost:8020/redoc`

## 📝 API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "address": "123 Library St, Book City",
  "role": "member"
}
```

**Response Example**:
```json
{
  "id": "user_123",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "address": "123 Library St, Book City",
  "role": "member",
  "membership_date": "2024-01-15",
  "is_active": true,
  "max_books_allowed": 5,
  "current_borrowed": 0,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

**Response Example**:
```json
{
  "access_token": "token_abc123def456...",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "member"
  }
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer your_token_here
```

### Books Management

#### Create Book
```http
POST /books
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "isbn": "9780321765723",
  "title": "The C++ Programming Language",
  "author": "Bjarne Stroustrup",
  "publisher": "Addison-Wesley",
  "publication_date": "2013-05-13",
  "pages": 1360,
  "language": "English",
  "description": "The definitive guide to C++ programming",
  "total_copies": 5,
  "location": "A-101",
  "replacement_cost": 89.99,
  "genre_ids": ["genre_123"],
  "tag_ids": ["tag_456"]
}
```

**Response Example**:
```json
{
  "id": "book_123",
  "isbn": "9780321765723",
  "title": "The C++ Programming Language",
  "author": "Bjarne Stroustrup",
  "publisher": "Addison-Wesley",
  "publication_date": "2013-05-13",
  "pages": 1360,
  "language": "English",
  "description": "The definitive guide to C++ programming",
  "cover_image_url": null,
  "status": "available",
  "total_copies": 5,
  "available_copies": 5,
  "location": "A-101",
  "acquisition_date": "2024-01-15",
  "replacement_cost": 89.99,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00",
  "genres": [
    {
      "id": "genre_123",
      "name": "Programming",
      "description": "Computer programming books",
      "created_at": "2024-01-15T12:00:00"
    }
  ],
  "tags": [
    {
      "id": "tag_456",
      "name": "Technical",
      "color": "#FF5722",
      "created_at": "2024-01-15T12:00:00"
    }
  ],
  "average_rating": 4.5,
  "rating_count": 12
}
```

#### Get Books
```http
GET /books?skip=0&limit=50&search=programming&author=stroustrup&genre=programming&status=available&available_only=true
```

#### Get Specific Book
```http
GET /books/{book_id}
```

#### Update Book
```http
PUT /books/{book_id}
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "title": "The C++ Programming Language (4th Edition)",
  "total_copies": 6
}
```

#### Delete Book
```http
DELETE /books/{book_id}
Authorization: Bearer your_token_here
```

### Genres Management

#### Create Genre
```http
POST /genres
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "name": "Science Fiction",
  "description": "Science fiction novels and stories"
}
```

#### Get All Genres
```http
GET /genres
```

### Tags Management

#### Create Tag
```http
POST /tags
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "name": "Bestseller",
  "color": "#4CAF50"
}
```

#### Get All Tags
```http
GET /tags
```

### Borrowing System

#### Borrow Book
```http
POST /borrow
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "book_id": "book_123",
  "due_date": "2024-02-15",
  "notes": "Needed for research project"
}
```

**Response Example**:
```json
{
  "id": "borrow_123",
  "user_id": "user_123",
  "book_id": "book_123",
  "borrow_date": "2024-01-15",
  "due_date": "2024-02-15",
  "return_date": null,
  "status": "active",
  "renewal_count": 0,
  "max_renewals": 2,
  "fine_amount": 0.0,
  "fine_paid": false,
  "notes": "Needed for research project",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Return Book
```http
POST /return/{borrow_id}
Authorization: Bearer your_token_here
```

#### Get My Borrowed Books
```http
GET /borrow/my-books
Authorization: Bearer your_token_here
```

#### Renew Book
```http
POST /renew/{borrow_id}
Authorization: Bearer your_token_here
```

### Ratings & Reviews

#### Create Rating
```http
POST /ratings
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "book_id": "book_123",
  "rating": 5,
  "review": "Excellent book for learning C++ fundamentals. Very comprehensive and well-written."
}
```

**Response Example**:
```json
{
  "id": "rating_123",
  "user_id": "user_123",
  "book_id": "book_123",
  "rating": 5,
  "review": "Excellent book for learning C++ fundamentals. Very comprehensive and well-written.",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Get Book Ratings
```http
GET /books/{book_id}/ratings?skip=0&limit=50
```

### Reservations

#### Create Reservation
```http
POST /reservations
Authorization: Bearer your_token_here
Content-Type: application/json

{
  "book_id": "book_123"
}
```

**Response Example**:
```json
{
  "id": "reservation_123",
  "user_id": "user_123",
  "book_id": "book_123",
  "reservation_date": "2024-01-15",
  "expiry_date": "2024-01-22",
  "status": "active",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Get My Reservations
```http
GET /reservations/my
Authorization: Bearer your_token_here
```

### Admin Panel

#### Get Admin Dashboard
```http
GET /admin/dashboard
Authorization: Bearer admin_token_here
```

**Response Example**:
```json
{
  "statistics": {
    "total_books": 1500,
    "total_users": 250,
    "total_borrows": 5000,
    "active_borrows": 150,
    "available_books": 1200,
    "borrowed_books": 280,
    "overdue_borrows": 12
  },
  "popular_books": [
    {
      "title": "The C++ Programming Language",
      "borrow_count": 45
    },
    {
      "title": "Clean Code",
      "borrow_count": 38
    }
  ],
  "recent_activity": {
    "recent_borrows": [
      {
        "id": "borrow_456",
        "book_title": "Clean Code",
        "user_name": "Jane Smith",
        "borrow_date": "2024-01-15",
        "status": "active"
      }
    ],
    "recent_ratings": [
      {
        "id": "rating_789",
        "book_title": "The Pragmatic Programmer",
        "user_name": "John Doe",
        "rating": 5,
        "created_at": "2024-01-15T11:30:00"
      }
    ]
  }
}
```

#### Get All Users
```http
GET /admin/users?skip=0&limit=50&role=member
Authorization: Bearer admin_token_here
```

#### Get All Borrow Records
```http
GET /admin/borrow-records?skip=0&limit=50&status=active
Authorization: Bearer admin_token_here
```

#### Get Overdue Books
```http
GET /admin/overdue-books
Authorization: Bearer admin_token_here
```

### Search

#### Search Books
```http
GET /search?q=programming&search_type=all
```

**Search Types**:
- `all`: Search in title, author, ISBN, and description
- `title`: Search only in titles
- `author`: Search only in authors
- `isbn`: Search only in ISBN numbers

## 🧪 Testing Examples

### User Management
```bash
# Register user
curl -X POST "http://localhost:8020/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "role": "member"
  }'

# Login
curl -X POST "http://localhost:8020/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "password123"
  }'
```

### Book Management
```bash
# Create book
curl -X POST "http://localhost:8020/books" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "publisher": "Prentice Hall",
    "pages": 464,
    "total_copies": 3,
    "location": "B-205"
  }'

# Get books
curl -X GET "http://localhost:8020/books?search=clean"

# Get specific book
curl -X GET "http://localhost:8020/books/book_123"
```

### Borrowing System
```bash
# Borrow book
curl -X POST "http://localhost:8020/borrow" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "book_123",
    "due_date": "2024-02-15"
  }'

# Return book
curl -X POST "http://localhost:8020/return/borrow_123" \
  -H "Authorization: Bearer your_token"

# Get my borrowed books
curl -X GET "http://localhost:8020/borrow/my-books" \
  -H "Authorization: Bearer your_token"
```

### Ratings
```bash
# Create rating
curl -X POST "http://localhost:8020/ratings" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "book_123",
    "rating": 5,
    "review": "Excellent book!"
  }'

# Get book ratings
curl -X GET "http://localhost:8020/books/book_123/ratings"
```

### Admin Operations
```bash
# Get admin dashboard
curl -X GET "http://localhost:8020/admin/dashboard" \
  -H "Authorization: Bearer admin_token"

# Get overdue books
curl -X GET "http://localhost:8020/admin/overdue-books" \
  -H "Authorization: Bearer admin_token"
```

## 📊 Database Schema

### Users Table
- **id**: Primary key (UUID)
- **username**: Unique username
- **email**: Unique email address
- **password_hash**: Bcrypt hashed password
- **full_name**: User's full name
- **phone**: Phone number
- **address**: Physical address
- **role**: User role (admin, librarian, member)
- **membership_date**: Date of membership
- **is_active**: Account status
- **max_books_allowed**: Maximum books user can borrow
- **current_borrowed**: Currently borrowed books count
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp

### Books Table
- **id**: Primary key (UUID)
- **isbn**: ISBN number (unique)
- **title**: Book title
- **author**: Book author
- **publisher**: Publisher name
- **publication_date**: Publication date
- **pages**: Number of pages
- **language**: Book language
- **description**: Book description
- **cover_image_url**: Cover image URL
- **status**: Book status (available, borrowed, reserved, maintenance, lost)
- **total_copies**: Total number of copies
- **available_copies**: Available copies for borrowing
- **location**: Shelf location
- **acquisition_date**: Date added to library
- **replacement_cost**: Cost for replacement
- **created_at**: Book creation timestamp
- **updated_at**: Last update timestamp

### Genres Table
- **id**: Primary key (UUID)
- **name**: Genre name (unique)
- **description**: Genre description
- **created_at**: Genre creation timestamp

### Tags Table
- **id**: Primary key (UUID)
- **name**: Tag name (unique)
- **color**: Hex color code for UI
- **created_at**: Tag creation timestamp

### Borrow Records Table
- **id**: Primary key (UUID)
- **user_id**: Foreign key to Users table
- **book_id**: Foreign key to Books table
- **borrow_date**: Date of borrowing
- **due_date**: Due date for return
- **return_date**: Actual return date
- **status**: Borrow status (active, returned, overdue, lost)
- **renewal_count**: Number of renewals
- **max_renewals**: Maximum allowed renewals
- **fine_amount**: Fine amount for overdue
- **fine_paid**: Whether fine is paid
- **notes**: Additional notes
- **created_at**: Record creation timestamp
- **updated_at**: Last update timestamp

### Ratings Table
- **id**: Primary key (UUID)
- **user_id**: Foreign key to Users table
- **book_id**: Foreign key to Books table
- **rating**: Star rating (1-5)
- **review**: User review text
- **created_at**: Rating creation timestamp
- **updated_at**: Last update timestamp

### Reservations Table
- **id**: Primary key (UUID)
- **user_id**: Foreign key to Users table
- **book_id**: Foreign key to Books table
- **reservation_date**: Date of reservation
- **expiry_date**: Reservation expiry date
- **status**: Reservation status (active, fulfilled, cancelled, expired)
- **created_at**: Reservation creation timestamp
- **updated_at**: Last update timestamp

## 👥 User Roles

### Admin
- Full system access
- User management
- All book management
- Admin dashboard access
- System configuration

### Librarian
- Book management (add, update, delete)
- Borrow/return operations
- User management (limited)
- Genre and tag management
- Reports and analytics

### Member
- Browse books
- Borrow/return books
- Create ratings and reviews
- Create reservations
- View own borrowing history

## 🔐 Security Features

### Authentication
- **Bearer Token**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Role-based Access**: Different permissions for different roles
- **Session Management**: Token expiration and validation

### Authorization
- **Endpoint Protection**: Role-based access to endpoints
- **Resource Ownership**: Users can only access their own resources
- **Admin Privileges**: Elevated permissions for admin users
- **Librarian Access**: Library management permissions

## 📚 Book Management Features

### Book Catalog
- **Detailed Information**: ISBN, title, author, publisher, pages, language
- **Cover Images**: URL support for book covers
- **Physical Location**: Shelf location tracking
- **Multiple Copies**: Track total and available copies
- **Status Management**: Available, borrowed, reserved, maintenance, lost

### Classification
- **Genres**: Hierarchical genre classification
- **Tags**: Flexible tagging system with colors
- **Search**: Full-text search across all fields
- **Filtering**: Filter by author, genre, status, availability

### Availability Tracking
- **Real-time Updates**: Automatic availability updates
- **Reservation System**: Queue unavailable books
- **Fine Calculation**: Automatic overdue fine calculation
- **Renewal System**: Book renewal with limits

## 📊 Borrowing System

### Borrowing Rules
- **Book Limits**: Maximum books per user based on role
- **Due Dates**: Configurable borrowing periods
- **Overdue Detection**: Automatic overdue status
- **Fine Calculation**: $0.50 per day overdue

### Renewal System
- **Renewal Limits**: Maximum 2 renewals per book
- **Reservation Check**: Cannot renew if book is reserved
- **Due Date Extension**: 14 days per renewal
- **Automatic Tracking**: Renewal count tracking

### Fine Management
- **Automatic Calculation**: Based on overdue days
- **Fine Status**: Track paid/unpaid fines
- **Fine Amount**: Configurable fine rates
- **Payment Tracking**: Fine payment status

## ⭐ Rating System

### 5-Star Rating
- **Rating Scale**: 1-5 stars
- **Average Calculation**: Automatic average rating
- **Rating Count**: Total number of ratings
- **User Reviews**: Detailed review text

### Review Features
- **Review Text**: Optional detailed reviews
- **Update Capability**: Users can update their ratings
- **Book Display**: Average ratings shown in book listings
- **Review History**: Track all reviews per book

## 🏷️ Genres and Tags

### Genre System
- **Hierarchical**: Parent-child genre relationships
- **Book Classification**: Multiple genres per book
- **Genre Statistics**: Track books per genre
- **Search Filtering**: Filter by genre

### Tag System
- **Flexible Tags**: Custom tags for books
- **Color Coding**: Visual tag colors
- **Multiple Tags**: Multiple tags per book
- **Tag Management**: Create and manage tags

## 📈 Admin Dashboard

### Statistics Overview
- **Library Metrics**: Total books, users, borrowings
- **Availability Stats**: Available vs borrowed books
- **Overdue Tracking**: Overdue books and fines
- **Popular Books**: Most borrowed books

### User Management
- **User List**: All library users
- **Role Management**: Assign and change user roles
- **Membership Tracking**: User membership dates
- **Activity Monitoring**: User borrowing activity

### System Monitoring
- **Recent Activity**: Latest borrowings and returns
- **Overdue Alerts**: Overdue book notifications
- **Fine Reports**: Unpaid fine tracking
- **Popular Content**: Most popular books and genres

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8020
DEBUG=false
RELOAD=false

# Database Configuration
DATABASE_URL=sqlite:///book_library.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30
DATABASE_ECHO=false

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PASSWORD_MIN_LENGTH=6
ENABLE_PASSWORD_STRENGTH_CHECK=true

# Library Configuration
DEFAULT_BORROW_PERIOD_DAYS=14
MAX_RENEWALS=2
FINE_PER_DAY=0.50
RESERVATION_EXPIRY_DAYS=7
MAX_BOOKS_PER_MEMBER=5
MAX_BOOKS_PER_LIBRARIAN=10
MAX_BOOKS_PER_ADMIN=20

# Search Configuration
ENABLE_FULL_TEXT_SEARCH=true
SEARCH_RESULTS_LIMIT=50
MIN_SEARCH_LENGTH=2
ENABLE_SEARCH_HIGHLIGHTING=true

# Rating Configuration
MIN_RATING=1
MAX_RATING=5
ENABLE_REVIEWS=true
REVIEW_MAX_LENGTH=1000
ENABLE_RATING_VALIDATION=true

# File Upload Configuration
ENABLE_COVER_UPLOAD=false
MAX_FILE_SIZE_MB=5
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,gif
COVER_IMAGE_STORAGE_PATH=./covers

# Email Configuration
ENABLE_EMAIL_NOTIFICATIONS=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@library.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@library.com

# Notification Settings
ENABLE_DUE_DATE_REMINDERS=false
REMINDER_DAYS_BEFORE=3
ENABLE_OVERDUE_NOTIFICATIONS=false
OVERDUE_NOTIFICATION_INTERVAL=7
ENABLE_RESERVATION_NOTIFICATIONS=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/book_library.log
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_BORROWING_EVENTS=true
LOG_FINE_EVENTS=true
LOG_ADMIN_ACTIONS=true

# Performance Configuration
ENABLE_CACHING=true
CACHE_TTL=300
CACHE_STORAGE=memory
ENABLE_COMPRESSION=true
COMPRESSION_LEVEL=6
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_REQUESTS=10

# CORS Configuration
ENABLE_CORS=true
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Development Configuration
TEST_MODE=false
ENABLE_PROFILING=false
DEBUG_RESPONSES=false
ENABLE_SWAGGER_UI=true
ENABLE_REDOC=true
ENABLE_API_DOCS_AUTH=false

# Backup Configuration
ENABLE_AUTO_BACKUP=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_STORAGE=local
BACKUP_ENCRYPTION=false
BACKUP_COMPRESSION=true
BACKUP_RETENTION_COPIES=30

# Maintenance Configuration
ENABLE_MAINTENANCE_MODE=false
MAINTENANCE_MESSAGE=System under maintenance. Please try again later.
ENABLE_SCHEDULED_MAINTENANCE=false
MAINTENANCE_SCHEDULE=0 3 * * 0  # Sunday 3 AM
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs data covers

# Set permissions
RUN chmod +x logs data covers

EXPOSE 8020

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8020"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  library-api:
    build: .
    ports:
      - "8020:8020"
    environment:
      - DATABASE_URL=sqlite:///data/book_library.db
      - LOG_LEVEL=INFO
      - SECRET_KEY=your-production-secret-key
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./covers:/app/covers
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8020/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

volumes:
  data_data:
  logs_data:
  covers_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: book-library-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: book-library-api
  template:
    metadata:
      labels:
        app: book-library-api
    spec:
      containers:
      - name: api
        image: book-library-api:latest
        ports:
        - containerPort: 8020
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: library-secrets
              key: secret-key
        - name: DATABASE_URL
          value: sqlite:///data/book_library.db
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        - name: covers
          mountPath: /app/covers
        livenessProbe:
          httpGet:
            path: /health
            port: 8020
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8020
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
      - name: covers
        persistentVolumeClaim:
          claimName: covers-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: book-library-service
spec:
  selector:
    app: book-library-api
  ports:
  - port: 8020
    targetPort: 8020
  type: LoadBalancer
```

## 📈 Advanced Features

### Advanced Search
```python
# Full-text search with ranking
def advanced_search(query: str, filters: Dict[str, Any], db: Session):
    """Advanced search with multiple filters and ranking"""
    base_query = db.query(Book)
    
    # Apply text search
    if query:
        search_terms = query.split()
        search_conditions = []
        for term in search_terms:
            search_conditions.append(Book.title.ilike(f"%{term}%"))
            search_conditions.append(Book.author.ilike(f"%{term}%"))
            search_conditions.append(Book.description.ilike(f"%{term}%"))
        
        if search_conditions:
            base_query = base_query.filter(or_(*search_conditions))
    
    # Apply filters
    if filters.get("author"):
        base_query = base_query.filter(Book.author.ilike(f"%{filters['author']}%"))
    
    if filters.get("genre"):
        base_query = base_query.join(Book.genres).filter(Genre.name == filters["genre"])
    
    if filters.get("rating_min"):
        # Subquery for average rating
        avg_rating_subq = db.query(
            Rating.book_id,
            func.avg(Rating.rating).label('avg_rating')
        ).group_by(Rating.book_id).having(
            func.avg(Rating.rating) >= filters["rating_min"]
        ).subquery()
        
        base_query = base_query.join(avg_rating_subq, Book.id == avg_rating_subq.c.book_id)
    
    return base_query.all()
```

### Recommendation System
```python
# Book recommendations based on user ratings
def get_book_recommendations(user_id: str, db: Session, limit: int = 10):
    """Get book recommendations based on user preferences"""
    # Get user's highly rated books
    user_ratings = db.query(Rating).filter(
        Rating.user_id == user_id,
        Rating.rating >= 4
    ).all()
    
    if not user_ratings:
        # Return popular books for new users
        return get_popular_books(db, limit)
    
    # Get genres user likes
    preferred_genres = set()
    for rating in user_ratings:
        book = db.query(Book).filter(Book.id == rating.book_id).first()
        if book:
            for genre in book.genres:
                preferred_genres.add(genre.id)
    
    # Recommend books in preferred genres
    recommendations = db.query(Book).join(Book.genres).filter(
        Genre.id.in_(preferred_genres),
        Book.available_copies > 0,
        ~Book.id.in_([r.book_id for r in user_ratings])  # Exclude already rated
    ).limit(limit).all()
    
    return recommendations
```

### Analytics Dashboard
```python
# Advanced analytics for admin dashboard
def get_library_analytics(db: Session):
    """Get comprehensive library analytics"""
    
    # Monthly borrowing trends
    monthly_borrows = db.query(
        func.date_trunc('month', BorrowRecord.borrow_date).label('month'),
        func.count(BorrowRecord.id).label('borrow_count')
    ).group_by(func.date_trunc('month', BorrowRecord.borrow_date)).all()
    
    # Genre popularity
    genre_popularity = db.query(
        Genre.name,
        func.count(BorrowRecord.id).label('borrow_count')
    ).join(Book, Book.genres).join(BorrowRecord).group_by(Genre.id).all()
    
    # User activity heatmap
    user_activity = db.query(
        func.extract('hour', BorrowRecord.borrow_date).label('hour'),
        func.count(BorrowRecord.id).label('activity_count')
    ).group_by(func.extract('hour', BorrowRecord.borrow_date)).all()
    
    # Fine collection statistics
    fine_stats = db.query(
        func.sum(BorrowRecord.fine_amount).label('total_fines'),
        func.sum(func.case([(BorrowRecord.fine_paid == True, BorrowRecord.fine_amount)], else_=0)).label('paid_fines'),
        func.sum(func.case([(BorrowRecord.fine_paid == False, BorrowRecord.fine_amount)], else_=0)).label('unpaid_fines')
    ).first()
    
    return {
        "monthly_trends": [
            {"month": str(month), "count": count}
            for month, count in monthly_borrows
        ],
        "genre_popularity": [
            {"genre": genre, "count": count}
            for genre, count in genre_popularity
        ],
        "activity_heatmap": [
            {"hour": int(hour), "count": count}
            for hour, count in user_activity
        ],
        "fine_statistics": {
            "total_fines": float(fine_stats.total_fines or 0),
            "paid_fines": float(fine_stats.paid_fines or 0),
            "unpaid_fines": float(fine_stats.unpaid_fines or 0)
        }
    }
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
book_operations = Counter('book_operations_total', 'Total book operations', operation='create|update|delete')
borrow_operations = Counter('borrow_operations_total', 'Total borrow operations', operation='borrow|return|renew')
rating_operations = Counter('rating_operations_total', 'Total rating operations')
user_registrations = Counter('user_registrations_total', 'Total user registrations')
search_queries = Counter('search_queries_total', 'Total search queries')

# Response times
book_operation_duration = Histogram('book_operation_duration_seconds', 'Book operation duration')
borrow_operation_duration = Histogram('borrow_operation_duration_seconds', 'Borrow operation duration')
search_duration = Histogram('search_duration_seconds', 'Search query duration')
```

### Usage Analytics
```python
@app.get("/analytics/usage")
async def get_usage_analytics(current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Get detailed usage analytics"""
    
    # User statistics
    user_stats = db.query(
        func.count(User.id).label('total_users'),
        func.count(func.case([(User.role == 'member', User.id)], else_=None)).label('members'),
        func.count(func.case([(User.role == 'librarian', User.id)], else_=None)).label('librarians'),
        func.count(func.case([(User.role == 'admin', User.id)], else_=None)).label('admins')
    ).first()
    
    # Book statistics
    book_stats = db.query(
        func.count(Book.id).label('total_books'),
        func.count(func.case([(Book.status == 'available', Book.id)], else_=None)).label('available'),
        func.count(func.case([(Book.status == 'borrowed', Book.id)], else_=None)).label('borrowed'),
        func.sum(Book.total_copies).label('total_copies'),
        func.sum(Book.available_copies).label('available_copies')
    ).first()
    
    # Borrowing statistics
    borrow_stats = db.query(
        func.count(BorrowRecord.id).label('total_borrows'),
        func.count(func.case([(BorrowRecord.status == 'active', BorrowRecord.id)], else_=None)).label('active_borrows'),
        func.count(func.case([(BorrowRecord.status == 'overdue', BorrowRecord.id)], else_=None)).label('overdue_borrows'),
        func.sum(BorrowRecord.fine_amount).label('total_fines')
    ).first()
    
    return {
        "user_statistics": {
            "total_users": user_stats.total_users,
            "members": user_stats.members,
            "librarians": user_stats.librarians,
            "admins": user_stats.admins
        },
        "book_statistics": {
            "total_books": book_stats.total_books,
            "available": book_stats.available,
            "borrowed": book_stats.borrowed,
            "total_copies": book_stats.total_copies,
            "available_copies": book_stats.available_copies
        },
        "borrowing_statistics": {
            "total_borrows": borrow_stats.total_borrows,
            "active_borrows": borrow_stats.active_borrows,
            "overdue_borrows": borrow_stats.overdue_borrows,
            "total_fines": float(borrow_stats.total_fines or 0)
        }
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Email Notifications**: Due date reminders and overdue notices
- **Fine Payment System**: Online fine payment integration
- **Book Cover Upload**: Image upload and storage
- **Advanced Analytics**: Reading patterns and recommendations
- **Mobile App**: Native mobile application
- **Barcode/QR Code**: Book scanning and checkout
- **Multi-language Support**: Internationalization
- **Reporting System**: Advanced reports and exports

### Advanced Library Features
- **Inter-library Loan**: Borrow from other libraries
- **Digital Books**: E-book integration and management
- **Reading Programs**: Summer reading and book clubs
- **Author Events**: Event management and registration
- **Book Suggestions**: Community book recommendations
- **Reading History**: Personal reading tracking
- **Book Clubs**: Club management and discussion

### Integration Opportunities
- **Payment Gateways**: Stripe/PayPal for fine payments
- **Email Services**: SendGrid/Mailgun for notifications
- **Cloud Storage**: AWS S3 for book covers
- **Analytics**: Google Analytics for usage tracking
- **Calendar Integration**: Google Calendar for due dates
- **Social Media**: Share book reviews and recommendations

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review FastAPI documentation for API development
- Consult SQLAlchemy documentation for database operations
- Check passlib documentation for password hashing

---

**Built with ❤️ using FastAPI for comprehensive library management**
