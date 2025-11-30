# Student Management API

A comprehensive student management system with attendance tracking, grading, timetable management, and complete student information management. Built with FastAPI and SQLAlchemy for robust educational institution operations.

## 🚀 Features

- **Student Management**: Complete student profiles with enrollment, guardians, and contact information
- **Attendance Tracking**: Daily attendance recording with multiple status options and analytics
- **Grading System**: Comprehensive grading with GPA calculation, letter grades, and assignment types
- **Timetable Management**: Class scheduling with room assignments and time management
- **Class Management**: Course creation, enrollment, and capacity management
- **Guardian Information**: Parent/guardian contact details and emergency contacts
- **Academic Records**: GPA calculation, credit tracking, and academic history
- **User Management**: Role-based access for teachers, admin, and staff
- **Analytics Dashboard**: Attendance rates, performance metrics, and class statistics
- **Multi-Grade Support**: Kindergarten through college level support
- **Subject Management**: Multiple subject types and categorization
- **Enrollment System**: Student enrollment with capacity limits and status tracking

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: JWT-based user authentication
- **Data Validation**: Pydantic models for request/response validation
- **Logging**: Comprehensive logging for audit trails
- **Date/Time**: Full datetime support for scheduling and attendance

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- 100MB+ disk space for database

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8017`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8017/docs`
- ReDoc: `http://localhost:8017/redoc`

## 📝 API Endpoints

### User Management

#### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "john_teacher",
  "email": "john@school.edu",
  "password": "secure_password",
  "full_name": "John Smith",
  "role": "teacher"
}
```

#### Get Users
```http
GET /users
Authorization: Bearer {token}
```

### Student Management

#### Create Student
```http
POST /students
Content-Type: application/json

{
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice.johnson@student.edu",
  "phone": "+1234567890",
  "date_of_birth": "2005-03-15",
  "gender": "female",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "country": "USA",
  "emergency_contact_name": "Mary Johnson",
  "emergency_contact_phone": "+1234567890",
  "emergency_contact_relationship": "Mother",
  "grade_level": "high",
  "guardians": [
    {
      "first_name": "Mary",
      "last_name": "Johnson",
      "relationship": "Mother",
      "email": "mary.johnson@email.com",
      "phone": "+1234567890",
      "address": "123 Main St",
      "is_primary": true
    }
  ]
}
```

**Response Example**:
```json
{
  "id": "student_123",
  "student_id": "STU20241234",
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice.johnson@student.edu",
  "phone": "+1234567890",
  "date_of_birth": "2005-03-15",
  "gender": "female",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "country": "USA",
  "emergency_contact_name": "Mary Johnson",
  "emergency_contact_phone": "+1234567890",
  "emergency_contact_relationship": "Mother",
  "grade_level": "high",
  "enrollment_date": "2024-01-15",
  "graduation_date": null,
  "gpa": 0.0,
  "total_credits": 0.0,
  "is_active": true,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Get Students
```http
GET /students?skip=0&limit=100&grade_level=high&is_active=true
Authorization: Bearer {token}
```

#### Update Student
```http
PUT /students/{student_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone": "+1234567891",
  "address": "124 Main St"
}
```

#### Delete Student
```http
DELETE /students/{student_id}
Authorization: Bearer {token}
```

### Guardian Management

#### Add Guardian
```http
POST /students/{student_id}/guardians
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Robert",
  "last_name": "Johnson",
  "relationship": "Father",
  "email": "robert.johnson@email.com",
  "phone": "+1234567891",
  "address": "123 Main St",
  "is_primary": false
}
```

#### Get Student Guardians
```http
GET /students/{student_id}/guardians
Authorization: Bearer {token}
```

### Class Management

#### Create Class
```http
POST /classes
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Advanced Mathematics",
  "description": "Calculus and advanced algebra",
  "subject": "Mathematics",
  "subject_type": "math",
  "grade_level": "high",
  "teacher_id": "user_123",
  "room_number": "101",
  "max_students": 30,
  "credits": 4.0,
  "semester": "Fall 2024",
  "academic_year": "2024-2025",
  "schedule_days": ["monday", "wednesday", "friday"],
  "schedule_time_start": "09:00",
  "schedule_time_end": "10:30"
}
```

**Response Example**:
```json
{
  "id": "class_456",
  "class_code": "CLS1234",
  "name": "Advanced Mathematics",
  "description": "Calculus and advanced algebra",
  "subject": "Mathematics",
  "subject_type": "math",
  "grade_level": "high",
  "teacher_id": "user_123",
  "room_number": "101",
  "max_students": 30,
  "current_students": 0,
  "credits": 4.0,
  "semester": "Fall 2024",
  "academic_year": "2024-2025",
  "schedule_days": ["monday", "wednesday", "friday"],
  "schedule_time_start": "09:00",
  "schedule_time_end": "10:30",
  "is_active": true,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Get Classes
```http
GET /classes?skip=0&limit=100&teacher_id=user_123&subject=Mathematics
Authorization: Bearer {token}
```

### Enrollment Management

#### Enroll Student
```http
POST /enrollments
Authorization: Bearer {token}
Content-Type: application/json

{
  "student_id": "student_123",
  "class_id": "class_456"
}
```

#### Get Class Students
```http
GET /classes/{class_id}/students
Authorization: Bearer {token}
```

#### Get Student Classes
```http
GET /students/{student_id}/classes
Authorization: Bearer {token}
```

### Attendance Management

#### Record Attendance
```http
POST /attendance
Authorization: Bearer {token}
Content-Type: application/json

{
  "student_id": "student_123",
  "class_id": "class_456",
  "date": "2024-01-15",
  "status": "present",
  "notes": "On time and prepared"
}
```

**Response Example**:
```json
{
  "id": "attendance_789",
  "student_id": "student_123",
  "class_id": "class_456",
  "date": "2024-01-15",
  "status": "present",
  "notes": "On time and prepared",
  "recorded_by_user_id": "user_123",
  "recorded_at": "2024-01-15T12:00:00"
}
```

#### Get Class Attendance
```http
GET /attendance/{class_id}/{date}
Authorization: Bearer {token}
```

#### Get Student Attendance
```http
GET /attendance/student/{student_id}?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### Grade Management

#### Create Grade
```http
POST /grades
Authorization: Bearer {token}
Content-Type: application/json

{
  "student_id": "student_123",
  "class_id": "class_456",
  "assignment_name": "Midterm Exam",
  "assignment_type": "exam",
  "max_points": 100,
  "points_earned": 85,
  "notes": "Good performance on calculus problems"
}
```

**Response Example**:
```json
{
  "id": "grade_101",
  "student_id": "student_123",
  "class_id": "class_456",
  "assignment_name": "Midterm Exam",
  "assignment_type": "exam",
  "max_points": 100,
  "points_earned": 85,
  "percentage": 85.0,
  "letter_grade": "B",
  "graded_date": "2024-01-15",
  "graded_by_user_id": "user_123",
  "notes": "Good performance on calculus problems",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

#### Get Student Grades
```http
GET /grades/student/{student_id}?class_id=class_456
Authorization: Bearer {token}
```

#### Get Class Grades
```http
GET /grades/class/{class_id}
Authorization: Bearer {token}
```

#### Get Student GPA
```http
GET /students/{student_id}/gpa
Authorization: Bearer {token}
```

**Response Example**:
```json
{
  "student_id": "student_123",
  "overall_gpa": 3.2,
  "gpa_by_assignment_type": {
    "homework": 3.5,
    "quiz": 3.0,
    "test": 3.1,
    "project": 3.8,
    "exam": 2.9
  },
  "total_assignments": 25,
  "letter_grades": {
    "A": 5,
    "B": 12,
    "C": 6,
    "D": 2
  }
}
```

### Timetable Management

#### Create Timetable Entry
```http
POST /timetable
Authorization: Bearer {token}
Content-Type: application/json

{
  "class_id": "class_456",
  "day_of_week": "monday",
  "start_time": "09:00",
  "end_time": "10:30",
  "room_number": "101",
  "semester": "Fall 2024",
  "academic_year": "2024-2025"
}
```

#### Get Class Timetable
```http
GET /timetable/class/{class_id}?semester=Fall%202024&academic_year=2024-2025
Authorization: Bearer {token}
```

#### Get Student Timetable
```http
GET /timetable/student/{student_id}?semester=Fall%202024&academic_year=2024-2025
Authorization: Bearer {token}
```

**Student Timetable Response Example**:
```json
[
  {
    "id": "timetable_1",
    "class_id": "class_456",
    "class_name": "Advanced Mathematics",
    "subject": "Mathematics",
    "teacher": "John Smith",
    "day_of_week": "monday",
    "start_time": "09:00",
    "end_time": "10:30",
    "room_number": "101",
    "semester": "Fall 2024",
    "academic_year": "2024-2025"
  },
  {
    "id": "timetable_2",
    "class_id": "class_789",
    "class_name": "Physics Lab",
    "subject": "Science",
    "teacher": "Dr. Brown",
    "day_of_week": "tuesday",
    "start_time": "14:00",
    "end_time": "16:00",
    "room_number": "Lab 201",
    "semester": "Fall 2024",
    "academic_year": "2024-2025"
  }
]
```

### Analytics and Reporting

#### Get Attendance Analytics
```http
GET /analytics/attendance?class_id=class_456&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

**Response Example**:
```json
{
  "total_records": 450,
  "present": 405,
  "absent": 30,
  "late": 10,
  "excused": 5,
  "attendance_rate": 90.0,
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

#### Get Performance Analytics
```http
GET /analytics/performance?class_id=class_456
Authorization: Bearer {token}
```

**Response Example**:
```json
{
  "total_assignments": 25,
  "average_score": 82.5,
  "highest_score": 98.0,
  "lowest_score": 65.0,
  "grade_distribution": {
    "A+": 2,
    "A": 5,
    "A-": 3,
    "B+": 4,
    "B": 6,
    "B-": 3,
    "C+": 1,
    "C": 1
  }
}
```

### Utility Endpoints

#### Get Grade Levels
```http
GET /grade-levels
```

**Response Example**:
```json
{
  "grade_levels": [
    {"value": "kindergarten", "label": "Kindergarten"},
    {"value": "elementary", "label": "Elementary"},
    {"value": "middle", "label": "Middle School"},
    {"value": "high", "label": "High School"},
    {"value": "college", "label": "College"}
  ]
}
```

#### Get Grade Scales
```http
GET /grade-scales
```

**Response Example**:
```json
{
  "grade_scales": [
    {"scale": "A+", "range": "97-100", "points": 4.0},
    {"scale": "A", "range": "93-96", "points": 4.0},
    {"scale": "A-", "range": "90-92", "points": 3.7},
    {"scale": "B+", "range": "87-89", "points": 3.3},
    {"scale": "B", "range": "83-86", "points": 3.0},
    {"scale": "B-", "range": "80-82", "points": 2.7},
    {"scale": "C+", "range": "77-79", "points": 2.3},
    {"scale": "C", "range": "73-76", "points": 2.0},
    {"scale": "C-", "range": "70-72", "points": 1.7},
    {"scale": "D+", "range": "67-69", "points": 1.3},
    {"scale": "D", "range": "63-66", "points": 1.0},
    {"scale": "D-", "range": "60-62", "points": 0.7},
    {"scale": "F", "range": "0-59", "points": 0.0}
  ]
}
```

## 📊 Data Models

### Student
```json
{
  "id": "student_123",
  "student_id": "STU20241234",
  "first_name": "Alice",
  "last_name": "Johnson",
  "email": "alice.johnson@student.edu",
  "phone": "+1234567890",
  "date_of_birth": "2005-03-15",
  "gender": "female",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "country": "USA",
  "emergency_contact_name": "Mary Johnson",
  "emergency_contact_phone": "+1234567890",
  "emergency_contact_relationship": "Mother",
  "grade_level": "high",
  "enrollment_date": "2024-01-15",
  "graduation_date": null,
  "gpa": 3.2,
  "total_credits": 24.0,
  "is_active": true,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

### Class
```json
{
  "id": "class_456",
  "class_code": "CLS1234",
  "name": "Advanced Mathematics",
  "description": "Calculus and advanced algebra",
  "subject": "Mathematics",
  "subject_type": "math",
  "grade_level": "high",
  "teacher_id": "user_123",
  "room_number": "101",
  "max_students": 30,
  "current_students": 25,
  "credits": 4.0,
  "semester": "Fall 2024",
  "academic_year": "2024-2025",
  "schedule_days": ["monday", "wednesday", "friday"],
  "schedule_time_start": "09:00",
  "schedule_time_end": "10:30",
  "is_active": true,
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

### Attendance
```json
{
  "id": "attendance_789",
  "student_id": "student_123",
  "class_id": "class_456",
  "date": "2024-01-15",
  "status": "present",
  "notes": "On time and prepared",
  "recorded_by_user_id": "user_123",
  "recorded_at": "2024-01-15T12:00:00"
}
```

### Grade
```json
{
  "id": "grade_101",
  "student_id": "student_123",
  "class_id": "class_456",
  "assignment_name": "Midterm Exam",
  "assignment_type": "exam",
  "max_points": 100,
  "points_earned": 85,
  "percentage": 85.0,
  "letter_grade": "B",
  "graded_date": "2024-01-15",
  "graded_by_user_id": "user_123",
  "notes": "Good performance on calculus problems",
  "created_at": "2024-01-15T12:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

## 🧪 Testing Examples

### Student Management
```bash
# Create student
curl -X POST "http://localhost:8017/students" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Johnson",
    "email": "alice.johnson@student.edu",
    "grade_level": "high"
  }'

# Get students
curl -X GET "http://localhost:8017/students?grade_level=high&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update student
curl -X PUT "http://localhost:8017/students/student_123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567891",
    "address": "124 Main St"
  }'
```

### Class and Enrollment
```bash
# Create class
curl -X POST "http://localhost:8017/classes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced Mathematics",
    "subject": "Mathematics",
    "subject_type": "math",
    "teacher_id": "user_123",
    "semester": "Fall 2024",
    "academic_year": "2024-2025",
    "schedule_days": ["monday", "wednesday", "friday"],
    "schedule_time_start": "09:00",
    "schedule_time_end": "10:30"
  }'

# Enroll student
curl -X POST "http://localhost:8017/enrollments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "class_id": "class_456"
  }'

# Get class students
curl -X GET "http://localhost:8017/classes/class_456/students" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Attendance and Grading
```bash
# Record attendance
curl -X POST "http://localhost:8017/attendance" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "class_id": "class_456",
    "date": "2024-01-15",
    "status": "present"
  }'

# Create grade
curl -X POST "http://localhost:8017/grades" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "class_id": "class_456",
    "assignment_name": "Midterm Exam",
    "assignment_type": "exam",
    "max_points": 100,
    "points_earned": 85
  }'

# Get student GPA
curl -X GET "http://localhost:8017/students/student_123/gpa" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Timetable and Analytics
```bash
# Create timetable entry
curl -X POST "http://localhost:8017/timetable" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": "class_456",
    "day_of_week": "monday",
    "start_time": "09:00",
    "end_time": "10:30",
    "room_number": "101",
    "semester": "Fall 2024",
    "academic_year": "2024-2025"
  }'

# Get student timetable
curl -X GET "http://localhost:8017/timetable/student/student_123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get attendance analytics
curl -X GET "http://localhost:8017/analytics/attendance?class_id=class_456&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get performance analytics
curl -X GET "http://localhost:8017/analytics/performance?class_id=class_456" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 Grade Scale System

### Letter Grade to GPA Conversion
| Letter Grade | Percentage | GPA Points |
|--------------|------------|-------------|
| A+ | 97-100% | 4.0 |
| A | 93-96% | 4.0 |
| A- | 90-92% | 3.7 |
| B+ | 87-89% | 3.3 |
| B | 83-86% | 3.0 |
| B- | 80-82% | 2.7 |
| C+ | 77-79% | 2.3 |
| C | 73-76% | 2.0 |
| C- | 70-72% | 1.7 |
| D+ | 67-69% | 1.3 |
| D | 63-66% | 1.0 |
| D- | 60-62% | 0.7 |
| F | 0-59% | 0.0 |

### Assignment Types
- **Homework**: Regular assignments and practice work
- **Quiz**: Short assessments and knowledge checks
- **Test**: Formal examinations and evaluations
- **Project**: Long-term assignments and presentations
- **Exam**: Major examinations and finals

### Attendance Status
- **Present**: Student attended class on time
- **Absent**: Student missed class without excuse
- **Late**: Student arrived after class start time
- **Excused**: Student absence is approved/justified

## 🗄️ Database Schema

### SQLite Tables
```sql
-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'teacher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    student_id TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    date_of_birth DATE,
    gender TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    emergency_contact_relationship TEXT,
    grade_level TEXT,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    graduation_date DATE,
    gpa REAL DEFAULT 0.0,
    total_credits REAL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guardians table
CREATE TABLE guardians (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    email TEXT,
    phone TEXT NOT NULL,
    address TEXT,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id)
);

-- Classes table
CREATE TABLE classes (
    id TEXT PRIMARY KEY,
    class_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    subject TEXT NOT NULL,
    subject_type TEXT,
    grade_level TEXT,
    teacher_id TEXT,
    room_number TEXT,
    max_students INTEGER DEFAULT 30,
    current_students INTEGER DEFAULT 0,
    credits REAL DEFAULT 1.0,
    semester TEXT,
    academic_year TEXT,
    schedule_days TEXT,  -- JSON array
    schedule_time_start TIME,
    schedule_time_end TIME,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users (id)
);

-- Enrollments table
CREATE TABLE enrollments (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'enrolled',
    final_grade TEXT,
    credits_earned REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (class_id) REFERENCES classes (id)
);

-- Attendance table
CREATE TABLE attendance (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    date DATE NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    recorded_by_user_id TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (class_id) REFERENCES classes (id),
    FOREIGN KEY (recorded_by_user_id) REFERENCES users (id)
);

-- Grades table
CREATE TABLE grades (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    assignment_name TEXT NOT NULL,
    assignment_type TEXT,
    max_points REAL NOT NULL,
    points_earned REAL NOT NULL,
    percentage REAL,
    letter_grade TEXT,
    graded_date DATE DEFAULT CURRENT_DATE,
    graded_by_user_id TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (class_id) REFERENCES classes (id),
    FOREIGN KEY (graded_by_user_id) REFERENCES users (id)
);

-- Timetable table
CREATE TABLE timetable (
    id TEXT PRIMARY KEY,
    class_id TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_number TEXT,
    semester TEXT,
    academic_year TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes (id)
);
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8017
DEBUG=false
RELOAD=false

# Database Configuration
DATABASE_URL=sqlite:///student_management.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30
DATABASE_ECHO=false
ENABLE_DATABASE_BACKUP=true
BACKUP_INTERVAL_HOURS=6
BACKUP_RETENTION_DAYS=30

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ENABLE_SESSION_MANAGEMENT=true
SESSION_CLEANUP_INTERVAL=3600

# Academic Configuration
DEFAULT_SEMESTER=Fall
DEFAULT_ACADEMIC_YEAR=2024-2025
DEFAULT_CLASS_CAPACITY=30
DEFAULT_CREDITS=1.0
MIN_STUDENT_AGE=5
MAX_STUDENT_AGE=25

# Grade Configuration
GRADE_SCALE_TYPE=standard
PASSING_GRADE=60
HONORS_GPA_THRESHOLD=3.5
MAX_GPA_POINTS=4.0
ENABLE_PLUS_MINUS_GRADES=true

# Attendance Configuration
AUTO_ATTENDANCE_ENABLED=false
ATTENDANCE_GRACE_PERIOD_MINUTES=15
MAX_ABSENCE_PERCENTAGE=20
ATTENDANCE_NOTIFICATION_ENABLED=false

# File Storage
ENABLE_FILE_STORAGE=false
STORAGE_PATH=./uploads
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,doc,docx,jpg,png

# Email Configuration
ENABLE_EMAIL_NOTIFICATIONS=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@school.edu
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@school.edu

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_RETRIES=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/student_management.log
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_ATTENDANCE=true
LOG_GRADES=true
LOG_ENROLLMENTS=true

# Performance
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_REQUESTS=10
ENABLE_CACHING=true
CACHE_TTL=3600
ENABLE_COMPRESSION=true

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8018
HEALTH_CHECK_INTERVAL=30
ENABLE_PERFORMANCE_MONITORING=true

# Development
TEST_MODE=false
TEST_DATABASE_URL=test_student_management.db
ENABLE_PROFILING=false
DEBUG_RESPONSES=false
MOCK_EMAIL_SENDING=false

# API Versioning
ENABLE_API_VERSIONING=true
DEFAULT_API_VERSION=v1
SUPPORTED_VERSIONS=v1,v2

# Documentation
ENABLE_DOCS=true
DOCS_URL=/docs
ENABLE_REDOC=true
REDOC_URL=/redoc

# Compliance
ENABLE_DATA_RETENTION=true
DATA_RETENTION_YEARS=7
ENABLE_AUDIT_LOG=true
GDPR_COMPLIANCE=falseFERpa_COMPLIANCE=true
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs data uploads

# Set permissions
RUN chmod +x data uploads

EXPOSE 8017

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8017"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  student-api:
    build: .
    ports:
      - "8017:8017"
    environment:
      - DATABASE_URL=sqlite:///data/student_management.db
      - SECRET_KEY=your-production-secret-key
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8017/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./uploads:/var/www/uploads
    depends_on:
      - student-api
    restart: unless-stopped

volumes:
  student_data:
  logs_data:
  uploads_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: student-management-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: student-management-api
  template:
    metadata:
      labels:
        app: student-management-api
    spec:
      containers:
      - name: api
        image: student-management-api:latest
        ports:
        - containerPort: 8017
        env:
        - name: DATABASE_URL
          value: "sqlite:///data/student_management.db"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: student-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: student-storage
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        - name: uploads
          mountPath: /app/uploads
        livenessProbe:
          httpGet:
            path: /health
            port: 8017
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8017
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: student-storage
        persistentVolumeClaim:
          claimName: student-storage-pvc
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: student-management-service
spec:
  selector:
    app: student-management-api
  ports:
  - port: 8017
    targetPort: 8017
  type: LoadBalancer
```

## 📈 Advanced Features

### Automated Attendance
```python
@app.post("/attendance/auto")
async def auto_attendance(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Automatically mark all enrolled students as present"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.status == "enrolled"
    ).all()
    
    today = date.today()
    attendance_records = []
    
    for enrollment in enrollments:
        # Check if attendance already recorded
        existing = db.query(Attendance).filter(
            Attendance.student_id == enrollment.student_id,
            Attendance.class_id == class_id,
            Attendance.date == today
        ).first()
        
        if not existing:
            attendance = Attendance(
                student_id=enrollment.student_id,
                class_id=class_id,
                date=today,
                status=AttendanceStatus.PRESENT,
                recorded_by_user_id=current_user.id
            )
            attendance_records.append(attendance)
    
    db.add_all(attendance_records)
    db.commit()
    
    return {"message": f"Auto-attendance recorded for {len(attendance_records)} students"}
```

### Bulk Grade Import
```python
@app.post("/grades/bulk")
async def bulk_import_grades(
    class_id: str,
    grades_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk import grades for a class"""
    results = []
    
    for grade_data in grades_data:
        try:
            # Validate student exists
            student = db.query(Student).filter(Student.id == grade_data["student_id"]).first()
            if not student:
                results.append({"student_id": grade_data["student_id"], "status": "error", "message": "Student not found"})
                continue
            
            # Calculate grade
            percentage = (grade_data["points_earned"] / grade_data["max_points"]) * 100
            letter_grade = calculate_letter_grade(percentage)
            
            # Create grade record
            grade = Grade(
                student_id=grade_data["student_id"],
                class_id=class_id,
                assignment_name=grade_data["assignment_name"],
                assignment_type=grade_data["assignment_type"],
                max_points=grade_data["max_points"],
                points_earned=grade_data["points_earned"],
                percentage=percentage,
                letter_grade=letter_grade,
                graded_by_user_id=current_user.id
            )
            
            db.add(grade)
            results.append({"student_id": grade_data["student_id"], "status": "success", "grade": letter_grade})
            
        except Exception as e:
            results.append({"student_id": grade_data.get("student_id", "unknown"), "status": "error", "message": str(e)})
    
    db.commit()
    
    return {"results": results, "total_processed": len(grades_data)}
```

### Class Performance Reports
```python
@app.get("/reports/class/{class_id}/performance")
async def class_performance_report(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive class performance report"""
    # Get class info
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Get enrolled students
    enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.status == "enrolled"
    ).all()
    
    student_ids = [e.student_id for e in enrollments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    # Get grades
    grades = db.query(Grade).filter(Grade.class_id == class_id).all()
    
    # Calculate statistics
    total_students = len(students)
    avg_gpa = sum(s.gpa for s in students) / total_students if total_students > 0 else 0
    
    # Grade distribution
    grade_dist = {}
    for grade in grades:
        grade_dist[grade.letter_grade] = grade_dist.get(grade.letter_grade, 0) + 1
    
    # Assignment type performance
    assignment_performance = {}
    for assignment_type in ["homework", "quiz", "test", "project", "exam"]:
        type_grades = [g for g in grades if g.assignment_type == assignment_type]
        if type_grades:
            avg_score = sum(g.percentage for g in type_grades) / len(type_grades)
            assignment_performance[assignment_type] = round(avg_score, 2)
    
    return {
        "class_info": {
            "name": cls.name,
            "subject": cls.subject,
            "teacher": cls.teacher.full_name if cls.teacher else None,
            "total_students": total_students
        },
        "performance_summary": {
            "average_gpa": round(avg_gpa, 2),
            "total_assignments": len(grades),
            "grade_distribution": grade_dist,
            "assignment_type_performance": assignment_performance
        },
        "student_performance": [
            {
                "student_id": s.id,
                "name": f"{s.first_name} {s.last_name}",
                "gpa": s.gpa,
                "assignment_count": len([g for g in grades if g.student_id == s.id])
            }
            for s in students
        ]
    }
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
student_operations = Counter('student_operations_total', 'Total student operations')
attendance_records = Counter('attendance_records_total', 'Total attendance records')
grade_entries = Counter('grade_entries_total', 'Total grade entries')
class_operations = Counter('class_operations_total', 'Total class operations')
active_students = Gauge('active_students', 'Number of active students')
average_gpa = Gauge('average_gpa', 'Average GPA across all students')
```

### Academic Analytics
```python
@app.get("/analytics/academic")
async def get_academic_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive academic analytics"""
    # Student statistics
    total_students = db.query(Student).filter(Student.is_active == True).count()
    new_enrollments = db.query(Student).filter(
        Student.enrollment_date >= start_date if start_date else True,
        Student.enrollment_date <= end_date if end_date else True
    ).count()
    
    # Grade statistics
    grades = db.query(Grade).all()
    avg_gpa = sum(s.gpa for s in db.query(Student).all()) / total_students if total_students > 0 else 0
    
    # Attendance statistics
    attendance_records = db.query(Attendance).all()
    attendance_rate = len([r for r in attendance_records if r.status == AttendanceStatus.PRESENT]) / len(attendance_records) * 100 if attendance_records else 0
    
    return {
        "student_statistics": {
            "total_active_students": total_students,
            "new_enrollments": new_enrollments,
            "students_by_grade_level": {
                level: db.query(Student).filter(Student.grade_level == level).count()
                for level in ["kindergarten", "elementary", "middle", "high", "college"]
            }
        },
        "academic_performance": {
            "average_gpa": round(avg_gpa, 2),
            "total_grades_recorded": len(grades),
            "grade_distribution": {
                grade: len([g for g in grades if g.letter_grade == grade])
                for grade in GradeScale
            }
        },
        "attendance_statistics": {
            "total_attendance_records": len(attendance_records),
            "overall_attendance_rate": round(attendance_rate, 2),
            "attendance_by_status": {
                status: len([r for r in attendance_records if r.status == status])
                for status in AttendanceStatus
            }
        }
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Mobile App Support**: Native iOS/Android applications
- **Parent Portal**: Dedicated portal for parents to monitor progress
- **Online Learning**: Integration with video conferencing platforms
- **Automated Reporting**: Scheduled report generation and email delivery
- **Behavior Tracking**: Student behavior and conduct records
- **Health Records**: Student medical information and allergies
- **Transportation**: School bus routing and tracking
- **Library Integration**: Book checkout and library management
- **Cafeteria Management**: Meal plans and lunch tracking
- **Extracurricular Activities**: Clubs, sports, and activity management

### Advanced Academic Features
- **Learning Analytics**: AI-powered learning pattern analysis
- **Adaptive Learning**: Personalized learning paths
- **Plagiarism Detection**: Assignment originality checking
- **Online Assessments**: Digital exam proctoring
- **Peer Review**: Student peer grading systems
- **Portfolio Development**: Student portfolio creation
- **Career Guidance**: College and career counseling tools
- **Skill Tracking**: Competency and skill development tracking

### Integration Opportunities
- **Learning Management Systems**: Moodle, Canvas, Blackboard integration
- **Student Information Systems**: PowerSchool, Skyward integration
- **Communication Platforms**: Slack, Microsoft Teams integration
- **Payment Systems**: Tuition and fee payment processing
- **Calendar Systems**: Google Calendar, Outlook integration
- **Document Management**: Google Drive, OneDrive integration
- **Video Platforms**: Zoom, Google Meet integration
- **Assessment Tools**: Online quiz and exam platforms

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review SQLAlchemy documentation for database operations
- Consult FastAPI documentation for API development
- Check educational technology best practices

---

**Built with ❤️ using FastAPI and SQLAlchemy for comprehensive student management**
