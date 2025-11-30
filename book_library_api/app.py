from fastapi import FastAPI, HTTPException, Query, Body, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, date
from enum import Enum
import uuid
import re
import logging
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
import secrets
import hashlib
from passlib.context import CryptContext

app = FastAPI(
    title="Book Library API",
    description="A comprehensive library management system with book catalog, borrowing, ratings, and admin panel",
    version="1.0.0"
)

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
DATABASE_URL = "sqlite:///book_library.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"

class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    LOST = "lost"

class BorrowStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"

# Association tables for many-to-many relationships
book_genres = Table(
    'book_genres',
    Base.metadata,
    Column('book_id', String, ForeignKey('books.id'), primary_key=True),
    Column('genre_id', String, ForeignKey('genres.id'), primary_key=True)
)

book_tags = Table(
    'book_tags',
    Base.metadata,
    Column('book_id', String, ForeignKey('books.id'), primary_key=True),
    Column('tag_id', String, ForeignKey('tags.id'), primary_key=True)
)

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    address = Column(Text)
    role = Column(String, default=UserRole.MEMBER)
    membership_date = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)
    max_books_allowed = Column(Integer, default=5)
    current_borrowed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrow_records = relationship("BorrowRecord", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    isbn = Column(String, unique=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    publisher = Column(String)
    publication_date = Column(Date)
    pages = Column(Integer)
    language = Column(String, default="English")
    description = Column(Text)
    cover_image_url = Column(String)
    status = Column(String, default=BookStatus.AVAILABLE)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    location = Column(String)  # Shelf location
    acquisition_date = Column(Date, default=date.today)
    replacement_cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrow_records = relationship("BorrowRecord", back_populates="book")
    ratings = relationship("Rating", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")
    genres = relationship("Genre", secondary=book_genres, back_populates="books")
    tags = relationship("Tag", secondary=book_tags, back_populates="books")

class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    books = relationship("Book", secondary=book_genres, back_populates="genres")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    color = Column(String)  # Hex color code for UI
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    books = relationship("Book", secondary=book_tags, back_populates="tags")

class BorrowRecord(Base):
    __tablename__ = "borrow_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    borrow_date = Column(Date, default=date.today)
    due_date = Column(Date)
    return_date = Column(Date)
    status = Column(String, default=BorrowStatus.ACTIVE)
    renewal_count = Column(Integer, default=0)
    max_renewals = Column(Integer, default=2)
    fine_amount = Column(Float, default=0.0)
    fine_paid = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    reservation_date = Column(Date, default=date.today)
    expiry_date = Column(Date)
    status = Column(String, default="active")  # active, fulfilled, cancelled, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    role: UserRole = Field(UserRole.MEMBER)

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    role: str
    membership_date: date
    is_active: bool
    max_books_allowed: int
    current_borrowed: int
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class GenreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

class GenreResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')

class TagResponse(BaseModel):
    id: str
    name: str
    color: Optional[str]
    created_at: datetime

class BookCreate(BaseModel):
    isbn: Optional[str] = Field(None, regex=r'^\d{10}(\d{3})?$')
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    publisher: Optional[str] = Field(None, max_length=100)
    publication_date: Optional[date] = Field(None)
    pages: Optional[int] = Field(None, gt=0)
    language: str = Field("English", max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    cover_image_url: Optional[str] = Field(None)
    total_copies: int = Field(1, gt=0)
    location: Optional[str] = Field(None, max_length=50)
    replacement_cost: Optional[float] = Field(None, gt=0)
    genre_ids: Optional[List[str]] = Field([])
    tag_ids: Optional[List[str]] = Field([])

class BookResponse(BaseModel):
    id: str
    isbn: Optional[str]
    title: str
    author: str
    publisher: Optional[str]
    publication_date: Optional[date]
    pages: Optional[int]
    language: str
    description: Optional[str]
    cover_image_url: Optional[str]
    status: str
    total_copies: int
    available_copies: int
    location: Optional[str]
    acquisition_date: date
    replacement_cost: Optional[float]
    created_at: datetime
    updated_at: datetime
    genres: List[GenreResponse] = []
    tags: List[TagResponse] = []
    average_rating: Optional[float] = None
    rating_count: int = 0

class BorrowRecordCreate(BaseModel):
    book_id: str
    due_date: Optional[date] = Field(None)
    notes: Optional[str] = Field(None, max_length=500)

class BorrowRecordResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    borrow_date: date
    due_date: date
    return_date: Optional[date]
    status: str
    renewal_count: int
    max_renewals: int
    fine_amount: float
    fine_paid: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class RatingCreate(BaseModel):
    book_id: str
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=1000)

class RatingResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    rating: int
    review: Optional[str]
    created_at: datetime
    updated_at: datetime

class ReservationCreate(BaseModel):
    book_id: str

class ReservationResponse(BaseModel):
    id: str
    user_id: str
    book_id: str
    reservation_date: date
    expiry_date: date
    status: str
    created_at: datetime
    updated_at: datetime

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token (simplified)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    # Simplified token generation (in production, use JWT)
    token = f"token_{uuid.uuid4().hex}"
    return token

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from token"""
    # Simplified token validation (in production, use JWT)
    token = credentials.credentials
    if not token.startswith("token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For demo purposes, we'll use a simple approach
    # In production, decode JWT and get user_id
    user = db.query(User).first()  # Simplified - should get from token
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get admin user"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_librarian_user(current_user: User = Depends(get_current_user)) -> User:
    """Get librarian or admin user"""
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Librarian access required"
        )
    return current_user

def calculate_fine(due_date: date, return_date: date) -> float:
    """Calculate fine for overdue books"""
    if return_date <= due_date:
        return 0.0
    
    overdue_days = (return_date - due_date).days
    fine_per_day = 0.50  # $0.50 per day
    return overdue_days * fine_per_day

def update_book_availability(db: Session, book_id: str):
    """Update book availability based on borrow records"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return
    
    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.status == BorrowStatus.ACTIVE
    ).count()
    
    book.available_copies = book.total_copies - active_borrows
    
    if book.available_copies > 0:
        book.status = BookStatus.AVAILABLE
    elif active_borrows > 0:
        book.status = BookStatus.BORROWED
    
    db.commit()

def get_book_rating_stats(db: Session, book_id: str) -> tuple:
    """Get book rating statistics"""
    ratings = db.query(Rating).filter(Rating.book_id == book_id).all()
    if not ratings:
        return None, 0
    
    avg_rating = sum(r.rating for r in ratings) / len(ratings)
    return avg_rating, len(ratings)

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to Book Library API",
        "version": "1.0.0",
        "features": [
            "Book catalog management",
            "Borrowing and returning",
            "Ratings and reviews",
            "Genres and tags",
            "Admin panel"
        ]
    }

# Authentication
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        # Check if username already exists
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )
        
        # Create user
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=get_password_hash(user.password),
            full_name=user.full_name,
            phone=user.phone,
            address=user.address,
            role=user.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Books Management
@app.post("/books", response_model=BookResponse)
async def create_book(
    book: BookCreate,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Create new book"""
    try:
        # Check if ISBN already exists
        if book.isbn and db.query(Book).filter(Book.isbn == book.isbn).first():
            raise HTTPException(
                status_code=400,
                detail="ISBN already exists"
            )
        
        # Create book
        db_book = Book(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            publication_date=book.publication_date,
            pages=book.pages,
            language=book.language,
            description=book.description,
            cover_image_url=book.cover_image_url,
            total_copies=book.total_copies,
            available_copies=book.total_copies,
            location=book.location,
            replacement_cost=book.replacement_cost
        )
        
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        
        # Add genres
        if book.genre_ids:
            for genre_id in book.genre_ids:
                genre = db.query(Genre).filter(Genre.id == genre_id).first()
                if genre:
                    db_book.genres.append(genre)
        
        # Add tags
        if book.tag_ids:
            for tag_id in book.tag_ids:
                tag = db.query(Tag).filter(Tag.id == tag_id).first()
                if tag:
                    db_book.tags.append(tag)
        
        db.commit()
        db.refresh(db_book)
        
        # Add rating stats
        avg_rating, rating_count = get_book_rating_stats(db, db_book.id)
        db_book.average_rating = avg_rating
        db_book.rating_count = rating_count
        
        return db_book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book creation failed: {e}")
        raise HTTPException(status_code=500, detail="Book creation failed")

@app.get("/books", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    status: Optional[BookStatus] = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get books with filtering"""
    try:
        query = db.query(Book)
        
        if search:
            query = query.filter(
                Book.title.ilike(f"%{search}%") |
                Book.author.ilike(f"%{search}%") |
                Book.description.ilike(f"%{search}%")
            )
        
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        
        if genre:
            query = query.join(Book.genres).filter(Genre.name.ilike(f"%{genre}%"))
        
        if status:
            query = query.filter(Book.status == status)
        
        if available_only:
            query = query.filter(Book.available_copies > 0)
        
        books = query.offset(skip).limit(limit).all()
        
        # Add rating stats
        for book in books:
            avg_rating, rating_count = get_book_rating_stats(db, book.id)
            book.average_rating = avg_rating
            book.rating_count = rating_count
        
        return books
        
    except Exception as e:
        logger.error(f"Error fetching books: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch books")

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """Get specific book"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Add rating stats
        avg_rating, rating_count = get_book_rating_stats(db, book.id)
        book.average_rating = avg_rating
        book.rating_count = rating_count
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching book: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch book")

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    book_update: BookCreate,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Update book"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Update book fields
        book.isbn = book_update.isbn
        book.title = book_update.title
        book.author = book_update.author
        book.publisher = book_update.publisher
        book.publication_date = book_update.publication_date
        book.pages = book_update.pages
        book.language = book_update.language
        book.description = book_update.description
        book.cover_image_url = book_update.cover_image_url
        book.total_copies = book_update.total_copies
        book.location = book_update.location
        book.replacement_cost = book_update.replacement_cost
        book.updated_at = datetime.utcnow()
        
        # Update genres
        book.genres.clear()
        if book_update.genre_ids:
            for genre_id in book_update.genre_ids:
                genre = db.query(Genre).filter(Genre.id == genre_id).first()
                if genre:
                    book.genres.append(genre)
        
        # Update tags
        book.tags.clear()
        if book_update.tag_ids:
            for tag_id in book_update.tag_ids:
                tag = db.query(Tag).filter(Tag.id == tag_id).first()
                if tag:
                    book.tags.append(tag)
        
        db.commit()
        db.refresh(book)
        
        # Add rating stats
        avg_rating, rating_count = get_book_rating_stats(db, book.id)
        book.average_rating = avg_rating
        book.rating_count = rating_count
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book update failed: {e}")
        raise HTTPException(status_code=500, detail="Book update failed")

@app.delete("/books/{book_id}")
async def delete_book(
    book_id: str,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Delete book"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Check if book has active borrow records
        active_borrows = db.query(BorrowRecord).filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.status == BorrowStatus.ACTIVE
        ).first()
        
        if active_borrows:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete book with active borrow records"
            )
        
        db.delete(book)
        db.commit()
        
        return {"message": "Book deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Book deletion failed")

# Genres Management
@app.post("/genres", response_model=GenreResponse)
async def create_genre(
    genre: GenreCreate,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Create new genre"""
    try:
        # Check if genre already exists
        if db.query(Genre).filter(Genre.name == genre.name).first():
            raise HTTPException(
                status_code=400,
                detail="Genre already exists"
            )
        
        db_genre = Genre(
            name=genre.name,
            description=genre.description
        )
        
        db.add(db_genre)
        db.commit()
        db.refresh(db_genre)
        
        return db_genre
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Genre creation failed: {e}")
        raise HTTPException(status_code=500, detail="Genre creation failed")

@app.get("/genres", response_model=List[GenreResponse])
async def get_genres(db: Session = Depends(get_db)):
    """Get all genres"""
    try:
        genres = db.query(Genre).all()
        return genres
    except Exception as e:
        logger.error(f"Error fetching genres: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch genres")

# Tags Management
@app.post("/tags", response_model=TagResponse)
async def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Create new tag"""
    try:
        # Check if tag already exists
        if db.query(Tag).filter(Tag.name == tag.name).first():
            raise HTTPException(
                status_code=400,
                detail="Tag already exists"
            )
        
        db_tag = Tag(
            name=tag.name,
            color=tag.color
        )
        
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        
        return db_tag
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tag creation failed: {e}")
        raise HTTPException(status_code=500, detail="Tag creation failed")

@app.get("/tags", response_model=List[TagResponse])
async def get_tags(db: Session = Depends(get_db)):
    """Get all tags"""
    try:
        tags = db.query(Tag).all()
        return tags
    except Exception as e:
        logger.error(f"Error fetching tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tags")

# Borrowing Management
@app.post("/borrow", response_model=BorrowRecordResponse)
async def borrow_book(
    borrow: BorrowRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Borrow a book"""
    try:
        # Check if book exists and is available
        book = db.query(Book).filter(Book.id == borrow.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book.available_copies <= 0:
            raise HTTPException(
                status_code=400,
                detail="Book not available"
            )
        
        # Check user's current borrowed books
        current_borrows = db.query(BorrowRecord).filter(
            BorrowRecord.user_id == current_user.id,
            BorrowRecord.status == BorrowStatus.ACTIVE
        ).count()
        
        if current_borrows >= current_user.max_books_allowed:
            raise HTTPException(
                status_code=400,
                detail="Maximum books limit reached"
            )
        
        # Check for overdue books
        overdue_books = db.query(BorrowRecord).filter(
            BorrowRecord.user_id == current_user.id,
            BorrowRecord.status == BorrowStatus.ACTIVE,
            BorrowRecord.due_date < date.today()
        ).first()
        
        if overdue_books:
            raise HTTPException(
                status_code=400,
                detail="Cannot borrow with overdue books"
            )
        
        # Set due date (default 14 days from today)
        due_date = borrow.due_date or (date.today() + timedelta(days=14))
        
        # Create borrow record
        db_borrow = BorrowRecord(
            user_id=current_user.id,
            book_id=borrow.book_id,
            due_date=due_date,
            notes=borrow.notes
        )
        
        db.add(db_borrow)
        
        # Update book availability
        book.available_copies -= 1
        if book.available_copies == 0:
            book.status = BookStatus.BORROWED
        
        # Update user's current borrowed count
        current_user.current_borrowed += 1
        
        db.commit()
        db.refresh(db_borrow)
        
        return db_borrow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book borrowing failed: {e}")
        raise HTTPException(status_code=500, detail="Book borrowing failed")

@app.post("/return/{borrow_id}", response_model=BorrowRecordResponse)
async def return_book(
    borrow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return a borrowed book"""
    try:
        # Get borrow record
        borrow = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
        if not borrow:
            raise HTTPException(status_code=404, detail="Borrow record not found")
        
        # Check ownership
        if borrow.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
            raise HTTPException(
                status_code=403_FORBIDDEN,
                detail="Not authorized to return this book"
            )
        
        if borrow.status != BorrowStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Book already returned"
            )
        
        # Update borrow record
        borrow.return_date = date.today()
        borrow.status = BorrowStatus.RETURNED
        
        # Calculate fine if overdue
        if date.today() > borrow.due_date:
            borrow.fine_amount = calculate_fine(borrow.due_date, date.today())
        
        borrow.updated_at = datetime.utcnow()
        
        # Update book availability
        book = db.query(Book).filter(Book.id == borrow.book_id).first()
        if book:
            book.available_copies += 1
            if book.available_copies > 0:
                book.status = BookStatus.AVAILABLE
        
        # Update user's current borrowed count
        user = db.query(User).filter(User.id == borrow.user_id).first()
        if user:
            user.current_borrowed = max(0, user.current_borrowed - 1)
        
        db.commit()
        db.refresh(borrow)
        
        return borrow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book return failed: {e}")
        raise HTTPException(status_code=500, detail="Book return failed")

@app.get("/borrow/my-books", response_model=List[BorrowRecordResponse])
async def get_my_borrowed_books(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's borrowed books"""
    try:
        borrows = db.query(BorrowRecord).filter(
            BorrowRecord.user_id == current_user.id,
            BorrowRecord.status == BorrowStatus.ACTIVE
        ).all()
        
        return borrows
        
    except Exception as e:
        logger.error(f"Error fetching borrowed books: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch borrowed books")

@app.post("/renew/{borrow_id}", response_model=BorrowRecordResponse)
async def renew_book(
    borrow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Renew a borrowed book"""
    try:
        # Get borrow record
        borrow = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
        if not borrow:
            raise HTTPException(status_code=404, detail="Borrow record not found")
        
        # Check ownership
        if borrow.user_id != current_user.id:
            raise HTTPException(
                status_code=403_FORBIDDEN,
                detail="Not authorized to renew this book"
            )
        
        if borrow.status != BorrowStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Cannot renew returned book"
            )
        
        if borrow.renewal_count >= borrow.max_renewals:
            raise HTTPException(
                status_code=400,
                detail="Maximum renewals reached"
            )
        
        # Check if book is reserved
        reservation = db.query(Reservation).filter(
            Reservation.book_id == borrow.book_id,
            Reservation.status == "active"
        ).first()
        
        if reservation:
            raise HTTPException(
                status_code=400,
                detail="Cannot renew - book is reserved"
            )
        
        # Extend due date by 14 days
        borrow.due_date += timedelta(days=14)
        borrow.renewal_count += 1
        borrow.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(borrow)
        
        return borrow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book renewal failed: {e}")
        raise HTTPException(status_code=500, detail="Book renewal failed")

# Ratings and Reviews
@app.post("/ratings", response_model=RatingResponse)
async def create_rating(
    rating: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create rating and review"""
    try:
        # Check if book exists
        book = db.query(Book).filter(Book.id == rating.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Check if user already rated this book
        existing_rating = db.query(Rating).filter(
            Rating.user_id == current_user.id,
            Rating.book_id == rating.book_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating.rating
            existing_rating.review = rating.review
            existing_rating.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_rating)
            return existing_rating
        
        # Create new rating
        db_rating = Rating(
            user_id=current_user.id,
            book_id=rating.book_id,
            rating=rating.rating,
            review=rating.review
        )
        
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        
        return db_rating
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rating creation failed: {e}")
        raise HTTPException(status_code=500, detail="Rating creation failed")

@app.get("/books/{book_id}/ratings", response_model=List[RatingResponse])
async def get_book_ratings(
    book_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get book ratings and reviews"""
    try:
        # Check if book exists
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        ratings = db.query(Rating).filter(
            Rating.book_id == book_id
        ).order_by(Rating.created_at.desc()).offset(skip).limit(limit).all()
        
        return ratings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ratings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch ratings")

# Reservations
@app.post("/reservations", response_model=ReservationResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create reservation"""
    try:
        # Check if book exists
        book = db.query(Book).filter(Book.id == reservation.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Check if book is available
        if book.available_copies > 0:
            raise HTTPException(
                status_code=400,
                detail="Book is available for borrowing"
            )
        
        # Check if user already has active reservation
        existing_reservation = db.query(Reservation).filter(
            Reservation.user_id == current_user.id,
            Reservation.book_id == reservation.book_id,
            Reservation.status == "active"
        ).first()
        
        if existing_reservation:
            raise HTTPException(
                status_code=400,
                detail="You already have an active reservation for this book"
            )
        
        # Create reservation
        expiry_date = date.today() + timedelta(days=7)  # 7 days expiry
        
        db_reservation = Reservation(
            user_id=current_user.id,
            book_id=reservation.book_id,
            expiry_date=expiry_date
        )
        
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        
        return db_reservation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reservation creation failed: {e}")
        raise HTTPException(status_code=500, detail="Reservation creation failed")

@app.get("/reservations/my", response_model=List[ReservationResponse])
async def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's reservations"""
    try:
        reservations = db.query(Reservation).filter(
            Reservation.user_id == current_user.id,
            Reservation.status == "active"
        ).all()
        
        return reservations
        
    except Exception as e:
        logger.error(f"Error fetching reservations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reservations")

# Admin Panel Endpoints
@app.get("/admin/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    try:
        # Basic statistics
        total_books = db.query(Book).count()
        total_users = db.query(User).count()
        total_borrows = db.query(BorrowRecord).count()
        active_borrows = db.query(BorrowRecord).filter(BorrowRecord.status == BorrowStatus.ACTIVE).count()
        
        # Books by status
        available_books = db.query(Book).filter(Book.status == BookStatus.AVAILABLE).count()
        borrowed_books = db.query(Book).filter(Book.status == BookStatus.BORROWED).count()
        
        # Overdue books
        overdue_borrows = db.query(BorrowRecord).filter(
            BorrowRecord.status == BorrowStatus.ACTIVE,
            BorrowRecord.due_date < date.today()
        ).count()
        
        # Popular books (most borrowed)
        popular_books_query = db.query(
            Book.title,
            func.count(BorrowRecord.id).label('borrow_count')
        ).join(BorrowRecord).group_by(Book.id).order_by(func.count(BorrowRecord.id).desc()).limit(5)
        
        popular_books = popular_books_query.all()
        
        # Recent activity
        recent_borrows = db.query(BorrowRecord).order_by(BorrowRecord.created_at.desc()).limit(10).all()
        recent_ratings = db.query(Rating).order_by(Rating.created_at.desc()).limit(10).all()
        
        return {
            "statistics": {
                "total_books": total_books,
                "total_users": total_users,
                "total_borrows": total_borrows,
                "active_borrows": active_borrows,
                "available_books": available_books,
                "borrowed_books": borrowed_books,
                "overdue_borrows": overdue_borrows
            },
            "popular_books": [
                {"title": book.title, "borrow_count": book.borrow_count}
                for book in popular_books
            ],
            "recent_activity": {
                "recent_borrows": [
                    {
                        "id": borrow.id,
                        "book_title": borrow.book.title if borrow.book else "Unknown",
                        "user_name": borrow.user.full_name or borrow.user.username,
                        "borrow_date": borrow.borrow_date,
                        "status": borrow.status
                    }
                    for borrow in recent_borrows
                ],
                "recent_ratings": [
                    {
                        "id": rating.id,
                        "book_title": rating.book.title if rating.book else "Unknown",
                        "user_name": rating.user.full_name or rating.user.username,
                        "rating": rating.rating,
                        "created_at": rating.created_at
                    }
                    for rating in recent_ratings
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching admin dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        users = query.offset(skip).limit(limit).all()
        return users
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@app.get("/admin/borrow-records", response_model=List[BorrowRecordResponse])
async def get_all_borrow_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[BorrowStatus] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all borrow records (admin only)"""
    try:
        query = db.query(BorrowRecord)
        
        if status:
            query = query.filter(BorrowRecord.status == status)
        
        records = query.order_by(BorrowRecord.created_at.desc()).offset(skip).limit(limit).all()
        return records
        
    except Exception as e:
        logger.error(f"Error fetching borrow records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch borrow records")

@app.get("/admin/overdue-books", response_model=List[BorrowRecordResponse])
async def get_overdue_books(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get overdue books (admin only)"""
    try:
        overdue_records = db.query(BorrowRecord).filter(
            BorrowRecord.status == BorrowStatus.ACTIVE,
            BorrowRecord.due_date < date.today()
        ).all()
        
        return overdue_records
        
    except Exception as e:
        logger.error(f"Error fetching overdue books: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch overdue books")

# Utility Endpoints
@app.get("/search")
async def search_books(
    q: str = Query(..., min_length=1),
    search_type: str = Query("all", regex=r'^(all|title|author|isbn)$'),
    db: Session = Depends(get_db)
):
    """Search books"""
    try:
        query = db.query(Book)
        
        if search_type == "title":
            query = query.filter(Book.title.ilike(f"%{q}%"))
        elif search_type == "author":
            query = query.filter(Book.author.ilike(f"%{q}%"))
        elif search_type == "isbn":
            query = query.filter(Book.isbn.ilike(f"%{q}%"))
        else:  # all
            query = query.filter(
                Book.title.ilike(f"%{q}%") |
                Book.author.ilike(f"%{q}%") |
                Book.isbn.ilike(f"%{q}%") |
                Book.description.ilike(f"%{q}%")
            )
        
        books = query.limit(50).all()
        
        # Add rating stats
        for book in books:
            avg_rating, rating_count = get_book_rating_stats(db, book.id)
            book.average_rating = avg_rating
            book.rating_count = rating_count
        
        return books
        
    except Exception as e:
        logger.error(f"Error searching books: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
