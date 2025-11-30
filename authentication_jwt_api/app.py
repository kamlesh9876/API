from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
import secrets
import hashlib
import jwt
from enum import Enum

app = FastAPI(title="Authentication & JWT API", version="1.0.0")

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
OTP_EXPIRE_MINUTES = 5

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

class OTPResponse(BaseModel):
    message: str
    otp_id: str
    expires_at: datetime

# In-memory database (for demo purposes)
users_db = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "is_verified": True,
        "is_active": True,
        "created_at": datetime.now() - timedelta(days=30),
        "last_login": datetime.now() - timedelta(hours=2),
        "refresh_tokens": []
    }
]

otp_db = []
reset_tokens_db = []
next_user_id = 2
next_otp_id = 1

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
    if user is None or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def generate_otp() -> str:
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Authentication & JWT API", "version": "1.0.0"}

# User Registration
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
        "role": user.role,
        "is_verified": False,
        "is_active": True,
        "created_at": datetime.now(),
        "last_login": None,
        "refresh_tokens": []
    }
    
    users_db.append(new_user)
    next_user_id += 1
    
    # Generate and store OTP
    otp_code = generate_otp()
    global next_otp_id
    otp_entry = {
        "id": next_otp_id,
        "email": user.email,
        "otp": otp_code,
        "expires_at": datetime.now() + timedelta(minutes=OTP_EXPIRE_MINUTES),
        "is_used": False
    }
    otp_db.append(otp_entry)
    next_otp_id += 1
    
    # Remove password hash from response
    user_response = new_user.copy()
    del user_response["password_hash"]
    del user_response["refresh_tokens"]
    
    return user_response

# Send OTP
@app.post("/send-otp", response_model=OTPResponse)
async def send_otp(email: EmailStr):
    """Send OTP for email verification"""
    user = next((u for u in users_db if u["email"] == email), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate and store OTP
    otp_code = generate_otp()
    global next_otp_id
    otp_entry = {
        "id": next_otp_id,
        "email": email,
        "otp": otp_code,
        "expires_at": datetime.now() + timedelta(minutes=OTP_EXPIRE_MINUTES),
        "is_used": False
    }
    otp_db.append(otp_entry)
    next_otp_id += 1
    
    return {
        "message": f"OTP sent to {email}",
        "otp_id": str(otp_entry["id"]),
        "expires_at": otp_entry["expires_at"]
    }

# Verify OTP
@app.post("/verify-otp", response_model=dict)
async def verify_otp_endpoint(otp_data: OTPVerify):
    """Verify OTP for email verification"""
    # Find valid OTP
    otp_entry = None
    for otp in otp_db:
        if (otp["email"] == otp_data.email and 
            otp["otp"] == otp_data.otp and 
            not otp["is_used"] and 
            otp["expires_at"] > datetime.now()):
            otp_entry = otp
            break
    
    if not otp_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp_entry["is_used"] = True
    
    # Verify user
    user = next((u for u in users_db if u["email"] == otp_data.email), None)
    if user:
        user["is_verified"] = True
    
    return {"message": "Email verified successfully"}

# User Login
@app.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """User login with email and password"""
    user = next((u for u in users_db if u["email"] == login_data.email), None)
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified. Please verify your email first."
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
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

# Refresh Token
@app.post("/refresh-token", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = next((u for u in users_db if u["id"] == int(user_id)), None)
        
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Check if refresh token exists in user's tokens
        if token_data.refresh_token not in user["refresh_tokens"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": token_data.refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# Logout
@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (remove refresh token)"""
    # In a real implementation, you'd want to remove the specific refresh token
    # For demo purposes, we'll clear all refresh tokens
    current_user["refresh_tokens"] = []
    return {"message": "Logged out successfully"}

# Get Current User
@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user_response = current_user.copy()
    del user_response["password_hash"]
    del user_response["refresh_tokens"]
    return user_response

# Password Reset Request
@app.post("/password-reset-request")
async def password_reset_request(email: EmailStr):
    """Request password reset"""
    user = next((u for u in users_db if u["email"] == email), None)
    
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If email exists, password reset instructions have been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_entry = {
        "email": email,
        "token": reset_token,
        "expires_at": datetime.now() + timedelta(hours=1),
        "is_used": False
    }
    reset_tokens_db.append(reset_entry)
    
    return {
        "message": "Password reset instructions sent to your email",
        "reset_token": reset_token  # In production, send via email
    }

# Password Reset Confirmation
@app.post("/password-reset-confirm")
async def password_reset_confirm(reset_data: PasswordResetConfirm):
    """Confirm password reset with token"""
    # Find valid reset token
    reset_entry = None
    for token in reset_tokens_db:
        if (token["token"] == reset_data.reset_token and 
            token["email"] == reset_data.email and
            not token["is_used"] and 
            token["expires_at"] > datetime.now()):
            reset_entry = token
            break
    
    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Mark token as used
    reset_entry["is_used"] = True
    
    # Update user password
    user = next((u for u in users_db if u["email"] == reset_data.email), None)
    if user:
        user["password_hash"] = hash_password(reset_data.new_password)
    
    return {"message": "Password reset successfully"}

# Change Password (authenticated)
@app.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """Change password for authenticated user"""
    if not verify_password(current_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user["password_hash"] = hash_password(new_password)
    return {"message": "Password changed successfully"}

# Admin endpoints
@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users_response = []
    for user in users_db:
        user_copy = user.copy()
        del user_copy["password_hash"]
        del user_copy["refresh_tokens"]
        users_response.append(user_copy)
    
    return users_response

@app.post("/admin/deactivate-user/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate user (admin only)"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["is_active"] = False
    return {"message": f"User {user['username']} deactivated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
