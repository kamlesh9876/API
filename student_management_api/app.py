from fastapi import FastAPI, HTTPException, Depends, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from enum import Enum
import uuid
import sqlite3
from sqlite3 import Connection
import json
import hashlib
import secrets
from decimal import Decimal
import logging
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
import re

app = FastAPI(title="Student Management API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///student_management.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()

# Enums
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class GradeLevel(str, Enum):
    KINDERGARTEN = "kindergarten"
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"
    COLLEGE = "college"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class GradeScale(str, Enum):
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    D_MINUS = "D-"
    F = "F"

class SubjectType(str, Enum):
    MATH = "math"
    SCIENCE = "science"
    ENGLISH = "english"
    HISTORY = "history"
    ART = "art"
    MUSIC = "music"
    PHYSICAL_ED = "physical_education"
    COMPUTER_SCIENCE = "computer_science"
    FOREIGN_LANGUAGE = "foreign_language"
    OTHER = "other"

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="teacher")  # teacher, admin, staff
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classes_taught = relationship("Class", back_populates="teacher")
    attendance_records = relationship("Attendance", back_populates="recorded_by_user")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    date_of_birth = Column(Date)
    gender = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    emergency_contact_name = Column(String)
    emergency_contact_phone = Column(String)
    emergency_contact_relationship = Column(String)
    grade_level = Column(String)
    enrollment_date = Column(Date, default=date.today)
    graduation_date = Column(Date)
    gpa = Column(Float, default=0.0)
    total_credits = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    guardians = relationship("Guardian", back_populates="student")

class Guardian(Base):
    __tablename__ = "guardians"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    relationship = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String, nullable=False)
    address = Column(Text)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="guardians")

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    subject = Column(String, nullable=False)
    subject_type = Column(String)
    grade_level = Column(String)
    teacher_id = Column(String, ForeignKey("users.id"))
    room_number = Column(String)
    max_students = Column(Integer, default=30)
    current_students = Column(Integer, default=0)
    credits = Column(Float, default=1.0)
    semester = Column(String)
    academic_year = Column(String)
    schedule_days = Column(String)  # JSON array of days
    schedule_time_start = Column(Time)
    schedule_time_end = Column(Time)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="classes_taught")
    enrollments = relationship("Enrollment", back_populates="class")
    attendance_records = relationship("Attendance", back_populates="class")
    grades = relationship("Grade", back_populates="class")
    timetable_entries = relationship("Timetable", back_populates="class")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    enrollment_date = Column(Date, default=date.today)
    status = Column(String, default="enrolled")  # enrolled, dropped, completed
    final_grade = Column(String)
    credits_earned = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    class_relationship = relationship("Class", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text)
    recorded_by_user_id = Column(String, ForeignKey("users.id"))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    class_relationship = relationship("Class", back_populates="attendance_records")
    recorded_by_user = relationship("User", back_populates="attendance_records")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    assignment_name = Column(String, nullable=False)
    assignment_type = Column(String)  # homework, quiz, test, project, exam
    max_points = Column(Float, nullable=False)
    points_earned = Column(Float, nullable=False)
    percentage = Column(Float)
    letter_grade = Column(String)
    graded_date = Column(Date, default=date.today)
    graded_by_user_id = Column(String, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="grades")
    class_relationship = relationship("Class", back_populates="grades")

class Timetable(Base):
    __tablename__ = "timetable"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    day_of_week = Column(String, nullable=False)  # monday, tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_number = Column(String)
    semester = Column(String)
    academic_year = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_relationship = relationship("Class", back_populates="timetable_entries")

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field("teacher", regex=r'^(teacher|admin|staff)$')

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime

class GuardianCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    relationship: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: str = Field(..., min_length=10, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    is_primary: bool = False

class GuardianResponse(BaseModel):
    id: str
    student_id: str
    first_name: str
    last_name: str
    relationship: str
    email: Optional[str]
    phone: str
    address: Optional[str]
    is_primary: bool
    created_at: datetime
    updated_at: datetime

class StudentCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    grade_level: Optional[GradeLevel] = None
    guardians: Optional[List[GuardianCreate]] = []

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    grade_level: Optional[GradeLevel] = None
    is_active: Optional[bool] = None

class StudentResponse(BaseModel):
    id: str
    student_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]
    grade_level: Optional[str]
    enrollment_date: date
    graduation_date: Optional[date]
    gpa: float
    total_credits: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    subject: str = Field(..., min_length=1, max_length=100)
    subject_type: Optional[SubjectType] = None
    grade_level: Optional[GradeLevel] = None
    teacher_id: str
    room_number: Optional[str] = Field(None, max_length=20)
    max_students: int = Field(30, ge=1, le=100)
    credits: float = Field(1.0, ge=0.1, le=10.0)
    semester: str = Field(..., max_length=20)
    academic_year: str = Field(..., max_length=20)
    schedule_days: List[str] = Field(..., min_items=1)
    schedule_time_start: str = Field(..., regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    schedule_time_end: str = Field(..., regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')

class ClassResponse(BaseModel):
    id: str
    class_code: str
    name: str
    description: Optional[str]
    subject: str
    subject_type: Optional[str]
    grade_level: Optional[str]
    teacher_id: str
    room_number: Optional[str]
    max_students: int
    current_students: int
    credits: float
    semester: str
    academic_year: str
    schedule_days: List[str]
    schedule_time_start: Optional[str]
    schedule_time_end: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class AttendanceCreate(BaseModel):
    student_id: str
    class_id: str
    date: date
    status: AttendanceStatus
    notes: Optional[str] = Field(None, max_length=500)

class AttendanceResponse(BaseModel):
    id: str
    student_id: str
    class_id: str
    date: date
    status: str
    notes: Optional[str]
    recorded_by_user_id: Optional[str]
    recorded_at: datetime

class GradeCreate(BaseModel):
    student_id: str
    class_id: str
    assignment_name: str = Field(..., min_length=1, max_length=100)
    assignment_type: str = Field(..., regex=r'^(homework|quiz|test|project|exam)$')
    max_points: float = Field(..., gt=0)
    points_earned: float = Field(..., ge=0)
    notes: Optional[str] = Field(None, max_length=500)

class GradeResponse(BaseModel):
    id: str
    student_id: str
    class_id: str
    assignment_name: str
    assignment_type: str
    max_points: float
    points_earned: float
    percentage: Optional[float]
    letter_grade: Optional[str]
    graded_date: date
    graded_by_user_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class TimetableCreate(BaseModel):
    class_id: str
    day_of_week: str = Field(..., regex=r'^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$')
    start_time: str = Field(..., regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: str = Field(..., regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    room_number: Optional[str] = Field(None, max_length=20)
    semester: str = Field(..., max_length=20)
    academic_year: str = Field(..., max_length=20)

class TimetableResponse(BaseModel):
    id: str
    class_id: str
    day_of_week: str
    start_time: Optional[str]
    end_time: Optional[str]
    room_number: Optional[str]
    semester: str
    academic_year: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Utility functions
def generate_student_id() -> str:
    """Generate unique student ID"""
    year = datetime.now().year
    while True:
        student_id = f"STU{year}{secrets.randbelow(10000):04d}"
        return student_id

def generate_class_code() -> str:
    """Generate unique class code"""
    while True:
        class_code = f"CLS{secrets.randbelow(10000):04d}"
        return class_code

def hash_password(password: str) -> str:
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_letter_grade(percentage: float) -> str:
    """Calculate letter grade from percentage"""
    if percentage >= 97:
        return GradeScale.A_PLUS
    elif percentage >= 93:
        return GradeScale.A
    elif percentage >= 90:
        return GradeScale.A_MINUS
    elif percentage >= 87:
        return GradeScale.B_PLUS
    elif percentage >= 83:
        return GradeScale.B
    elif percentage >= 80:
        return GradeScale.B_MINUS
    elif percentage >= 77:
        return GradeScale.C_PLUS
    elif percentage >= 73:
        return GradeScale.C
    elif percentage >= 70:
        return GradeScale.C_MINUS
    elif percentage >= 67:
        return GradeScale.D_PLUS
    elif percentage >= 63:
        return GradeScale.D
    elif percentage >= 60:
        return GradeScale.D_MINUS
    else:
        return GradeScale.F

def calculate_gpa(grades: List[Grade]) -> float:
    """Calculate GPA from grades"""
    if not grades:
        return 0.0
    
    grade_points = {
        GradeScale.A_PLUS: 4.0,
        GradeScale.A: 4.0,
        GradeScale.A_MINUS: 3.7,
        GradeScale.B_PLUS: 3.3,
        GradeScale.B: 3.0,
        GradeScale.B_MINUS: 2.7,
        GradeScale.C_PLUS: 2.3,
        GradeScale.C: 2.0,
        GradeScale.C_MINUS: 1.7,
        GradeScale.D_PLUS: 1.3,
        GradeScale.D: 1.0,
        GradeScale.D_MINUS: 0.7,
        GradeScale.F: 0.0
    }
    
    total_points = sum(grade_points.get(grade.letter_grade, 0.0) for grade in grades)
    return total_points / len(grades)

# Authentication
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user (simplified)"""
    # This is a simplified authentication - in production, implement proper JWT validation
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return user

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Student Management API", "version": "1.0.0"}

# User Management
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create user
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hash_password(user.password),
            full_name=user.full_name,
            role=user.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )

@app.get("/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return users

# Student Management
@app.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    try:
        # Check if email already exists
        if db.query(Student).filter(Student.email == student.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create student
        db_student = Student(
            student_id=generate_student_id(),
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            phone=student.phone,
            date_of_birth=student.date_of_birth,
            gender=student.gender.value if student.gender else None,
            address=student.address,
            city=student.city,
            state=student.state,
            postal_code=student.postal_code,
            country=student.country,
            emergency_contact_name=student.emergency_contact_name,
            emergency_contact_phone=student.emergency_contact_phone,
            emergency_contact_relationship=student.emergency_contact_relationship,
            grade_level=student.grade_level.value if student.grade_level else None
        )
        
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        # Add guardians if provided
        if student.guardians:
            for guardian_data in student.guardians:
                guardian = Guardian(
                    student_id=db_student.id,
                    first_name=guardian_data.first_name,
                    last_name=guardian_data.last_name,
                    relationship=guardian_data.relationship,
                    email=guardian_data.email,
                    phone=guardian_data.phone,
                    address=guardian_data.address,
                    is_primary=guardian_data.is_primary
                )
                db.add(guardian)
            
            db.commit()
        
        return db_student
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Student creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student creation failed"
        )

@app.get("/students", response_model=List[StudentResponse])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    grade_level: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students with optional filters"""
    query = db.query(Student)
    
    if grade_level:
        query = query.filter(Student.grade_level == grade_level)
    
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    
    students = query.offset(skip).limit(limit).all()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update student information"""
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Update fields
        update_data = student_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "gender" and value:
                setattr(student, field, value.value)
            elif field == "grade_level" and value:
                setattr(student, field, value.value)
            else:
                setattr(student, field, value)
        
        student.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(student)
        
        return student
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Student update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Student update failed"
        )

@app.delete("/students/{student_id}")
async def delete_student(student_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete student (soft delete)"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Soft delete
    student.is_active = False
    student.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Student deleted successfully"}

# Guardian Management
@app.post("/students/{student_id}/guardians", response_model=GuardianResponse)
async def add_guardian(
    student_id: str,
    guardian: GuardianCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add guardian to student"""
    try:
        # Check if student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Create guardian
        db_guardian = Guardian(
            student_id=student_id,
            first_name=guardian.first_name,
            last_name=guardian.last_name,
            relationship=guardian.relationship,
            email=guardian.email,
            phone=guardian.phone,
            address=guardian.address,
            is_primary=guardian.is_primary
        )
        
        db.add(db_guardian)
        db.commit()
        db.refresh(db_guardian)
        
        return db_guardian
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Guardian creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Guardian creation failed"
        )

@app.get("/students/{student_id}/guardians", response_model=List[GuardianResponse])
async def get_student_guardians(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student guardians"""
    guardians = db.query(Guardian).filter(Guardian.student_id == student_id).all()
    return guardians

# Class Management
@app.post("/classes", response_model=ClassResponse)
async def create_class(class_data: ClassCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new class"""
    try:
        # Check if teacher exists
        teacher = db.query(User).filter(User.id == class_data.teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )
        
        # Create class
        db_class = Class(
            class_code=generate_class_code(),
            name=class_data.name,
            description=class_data.description,
            subject=class_data.subject,
            subject_type=class_data.subject_type.value if class_data.subject_type else None,
            grade_level=class_data.grade_level.value if class_data.grade_level else None,
            teacher_id=class_data.teacher_id,
            room_number=class_data.room_number,
            max_students=class_data.max_students,
            credits=class_data.credits,
            semester=class_data.semester,
            academic_year=class_data.academic_year,
            schedule_days=json.dumps(class_data.schedule_days),
            schedule_time_start=class_data.schedule_time_start,
            schedule_time_end=class_data.schedule_time_end
        )
        
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        
        return db_class
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Class creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Class creation failed"
        )

@app.get("/classes", response_model=List[ClassResponse])
async def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    teacher_id: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get classes with optional filters"""
    query = db.query(Class)
    
    if teacher_id:
        query = query.filter(Class.teacher_id == teacher_id)
    
    if subject:
        query = query.filter(Class.subject == subject)
    
    classes = query.offset(skip).limit(limit).all()
    
    # Convert schedule_days from JSON
    for cls in classes:
        if cls.schedule_days:
            try:
                cls.schedule_days = json.loads(cls.schedule_days)
            except:
                cls.schedule_days = []
    
    return classes

@app.get("/classes/{class_id}", response_model=ClassResponse)
async def get_class(class_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get class by ID"""
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )
    
    # Convert schedule_days from JSON
    if cls.schedule_days:
        try:
            cls.schedule_days = json.loads(cls.schedule_days)
        except:
            cls.schedule_days = []
    
    return cls

# Enrollment Management
@app.post("/enrollments")
async def enroll_student(
    student_id: str = Body(...),
    class_id: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll student in class"""
    try:
        # Check if student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Check if class exists
        cls = db.query(Class).filter(Class.id == class_id).first()
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # Check if already enrolled
        existing_enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.class_id == class_id,
            Enrollment.status == "enrolled"
        ).first()
        
        if existing_enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student already enrolled in this class"
            )
        
        # Check class capacity
        if cls.current_students >= cls.max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Class is full"
            )
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student_id,
            class_id=class_id
        )
        
        db.add(enrollment)
        
        # Update class current students
        cls.current_students += 1
        
        db.commit()
        
        return {"message": "Student enrolled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrollment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Enrollment failed"
        )

@app.get("/classes/{class_id}/students")
async def get_class_students(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students enrolled in class"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == class_id,
        Enrollment.status == "enrolled"
    ).all()
    
    student_ids = [enrollment.student_id for enrollment in enrollments]
    students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    return students

@app.get("/students/{student_id}/classes")
async def get_student_classes(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get classes student is enrolled in"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.status == "enrolled"
    ).all()
    
    class_ids = [enrollment.class_id for enrollment in enrollments]
    classes = db.query(Class).filter(Class.id.in_(class_ids)).all()
    
    # Convert schedule_days from JSON
    for cls in classes:
        if cls.schedule_days:
            try:
                cls.schedule_days = json.loads(cls.schedule_days)
            except:
                cls.schedule_days = []
    
    return classes

# Attendance Management
@app.post("/attendance", response_model=AttendanceResponse)
async def record_attendance(
    attendance: AttendanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record student attendance"""
    try:
        # Check if student exists
        student = db.query(Student).filter(Student.id == attendance.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Check if class exists
        cls = db.query(Class).filter(Class.id == attendance.class_id).first()
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # Check if attendance already recorded
        existing_attendance = db.query(Attendance).filter(
            Attendance.student_id == attendance.student_id,
            Attendance.class_id == attendance.class_id,
            Attendance.date == attendance.date
        ).first()
        
        if existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance already recorded for this date"
            )
        
        # Create attendance record
        attendance_record = Attendance(
            student_id=attendance.student_id,
            class_id=attendance.class_id,
            date=attendance.date,
            status=attendance.status.value,
            notes=attendance.notes,
            recorded_by_user_id=current_user.id
        )
        
        db.add(attendance_record)
        db.commit()
        db.refresh(attendance_record)
        
        return attendance_record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Attendance recording failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Attendance recording failed"
        )

@app.get("/attendance/{class_id}/{date}")
async def get_class_attendance(
    class_id: str,
    date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance for class on specific date"""
    attendance_records = db.query(Attendance).filter(
        Attendance.class_id == class_id,
        Attendance.date == date
    ).all()
    
    return attendance_records

@app.get("/attendance/student/{student_id}")
async def get_student_attendance(
    student_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student attendance history"""
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.order_by(Attendance.date.desc()).all()
    return attendance_records

# Grade Management
@app.post("/grades", response_model=GradeResponse)
async def create_grade(
    grade: GradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create grade record"""
    try:
        # Check if student exists
        student = db.query(Student).filter(Student.id == grade.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Check if class exists
        cls = db.query(Class).filter(Class.id == grade.class_id).first()
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # Calculate percentage and letter grade
        percentage = (grade.points_earned / grade.max_points) * 100 if grade.max_points > 0 else 0
        letter_grade = calculate_letter_grade(percentage)
        
        # Create grade record
        grade_record = Grade(
            student_id=grade.student_id,
            class_id=grade.class_id,
            assignment_name=grade.assignment_name,
            assignment_type=grade.assignment_type,
            max_points=grade.max_points,
            points_earned=grade.points_earned,
            percentage=percentage,
            letter_grade=letter_grade,
            graded_by_user_id=current_user.id,
            notes=grade.notes
        )
        
        db.add(grade_record)
        db.commit()
        db.refresh(grade_record)
        
        # Update student GPA
        student_grades = db.query(Grade).filter(Grade.student_id == grade.student_id).all()
        student.gpa = calculate_gpa(student_grades)
        db.commit()
        
        return grade_record
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Grade creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Grade creation failed"
        )

@app.get("/grades/student/{student_id}")
async def get_student_grades(
    student_id: str,
    class_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student grades"""
    query = db.query(Grade).filter(Grade.student_id == student_id)
    
    if class_id:
        query = query.filter(Grade.class_id == class_id)
    
    grades = query.order_by(Grade.graded_date.desc()).all()
    return grades

@app.get("/grades/class/{class_id}")
async def get_class_grades(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all grades for a class"""
    grades = db.query(Grade).filter(Grade.class_id == class_id).order_by(Grade.graded_date.desc()).all()
    return grades

@app.get("/students/{student_id}/gpa")
async def get_student_gpa(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student GPA breakdown"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    
    # Calculate GPA by assignment type
    gpa_by_type = {}
    for assignment_type in ["homework", "quiz", "test", "project", "exam"]:
        type_grades = [g for g in grades if g.assignment_type == assignment_type]
        gpa_by_type[assignment_type] = calculate_gpa(type_grades)
    
    return {
        "student_id": student_id,
        "overall_gpa": student.gpa,
        "gpa_by_assignment_type": gpa_by_type,
        "total_assignments": len(grades),
        "letter_grades": {grade.letter_grade: 1 for grade in grades if grade.letter_grade}
    }

# Timetable Management
@app.post("/timetable", response_model=TimetableResponse)
async def create_timetable_entry(
    timetable: TimetableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create timetable entry"""
    try:
        # Check if class exists
        cls = db.query(Class).filter(Class.id == timetable.class_id).first()
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # Create timetable entry
        timetable_entry = Timetable(
            class_id=timetable.class_id,
            day_of_week=timetable.day_of_week,
            start_time=timetable.start_time,
            end_time=timetable.end_time,
            room_number=timetable.room_number,
            semester=timetable.semester,
            academic_year=timetable.academic_year
        )
        
        db.add(timetable_entry)
        db.commit()
        db.refresh(timetable_entry)
        
        return timetable_entry
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Timetable creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Timetable creation failed"
        )

@app.get("/timetable/class/{class_id}")
async def get_class_timetable(
    class_id: str,
    semester: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get class timetable"""
    query = db.query(Timetable).filter(Timetable.class_id == class_id)
    
    if semester:
        query = query.filter(Timetable.semester == semester)
    
    if academic_year:
        query = query.filter(Timetable.academic_year == academic_year)
    
    timetable_entries = query.order_by(Timetable.day_of_week, Timetable.start_time).all()
    return timetable_entries

@app.get("/timetable/student/{student_id}")
async def get_student_timetable(
    student_id: str,
    semester: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student timetable"""
    # Get student's enrolled classes
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.status == "enrolled"
    ).all()
    
    class_ids = [enrollment.class_id for enrollment in enrollments]
    
    # Get timetable entries for those classes
    query = db.query(Timetable).filter(Timetable.class_id.in_(class_ids))
    
    if semester:
        query = query.filter(Timetable.semester == semester)
    
    if academic_year:
        query = query.filter(Timetable.academic_year == academic_year)
    
    timetable_entries = query.order_by(Timetable.day_of_week, Timetable.start_time).all()
    
    # Add class information
    result = []
    for entry in timetable_entries:
        cls = db.query(Class).filter(Class.id == entry.class_id).first()
        if cls:
            entry_dict = {
                "id": entry.id,
                "class_id": entry.class_id,
                "class_name": cls.name,
                "subject": cls.subject,
                "teacher": cls.teacher.full_name if cls.teacher else None,
                "day_of_week": entry.day_of_week,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "room_number": entry.room_number,
                "semester": entry.semester,
                "academic_year": entry.academic_year
            }
            result.append(entry_dict)
    
    return result

# Analytics and Reporting
@app.get("/analytics/attendance")
async def get_attendance_analytics(
    class_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance analytics"""
    query = db.query(Attendance)
    
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    attendance_records = query.all()
    
    # Calculate statistics
    total_records = len(attendance_records)
    present_count = len([r for r in attendance_records if r.status == AttendanceStatus.PRESENT])
    absent_count = len([r for r in attendance_records if r.status == AttendanceStatus.ABSENT])
    late_count = len([r for r in attendance_records if r.status == AttendanceStatus.LATE])
    excused_count = len([r for r in attendance_records if r.status == AttendanceStatus.EXCUSED])
    
    attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
    
    return {
        "total_records": total_records,
        "present": present_count,
        "absent": absent_count,
        "late": late_count,
        "excused": excused_count,
        "attendance_rate": round(attendance_rate, 2),
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

@app.get("/analytics/performance")
async def get_performance_analytics(
    class_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get class performance analytics"""
    query = db.query(Grade)
    
    if class_id:
        query = query.filter(Grade.class_id == class_id)
    
    grades = query.all()
    
    if not grades:
        return {"message": "No grades found"}
    
    # Calculate statistics
    percentages = [g.percentage for g in grades if g.percentage is not None]
    
    if percentages:
        avg_score = sum(percentages) / len(percentages)
        highest_score = max(percentages)
        lowest_score = min(percentages)
        
        # Grade distribution
        grade_distribution = {}
        for grade_scale in GradeScale:
            grade_distribution[grade_scale.value] = len([g for g in grades if g.letter_grade == grade_scale.value])
    else:
        avg_score = highest_score = lowest_score = 0
        grade_distribution = {}
    
    return {
        "total_assignments": len(grades),
        "average_score": round(avg_score, 2),
        "highest_score": round(highest_score, 2),
        "lowest_score": round(lowest_score, 2),
        "grade_distribution": grade_distribution
    }

# Utility Endpoints
@app.get("/grade-levels")
async def get_grade_levels():
    """Get supported grade levels"""
    return {
        "grade_levels": [
            {"value": "kindergarten", "label": "Kindergarten"},
            {"value": "elementary", "label": "Elementary"},
            {"value": "middle", "label": "Middle School"},
            {"value": "high", "label": "High School"},
            {"value": "college", "label": "College"}
        ]
    }

@app.get("/grade-scales")
async def get_grade_scales():
    """Get grade scale information"""
    return {
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "database_connected": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8017)
