from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import hashlib
import base64
from datetime import datetime, timedelta
from enum import Enum
import random

app = FastAPI(title="Biometric Authentication API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class BiometricType(str, Enum):
    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"
    IRIS = "iris"
    RETINA = "retina"
    PALM = "palm"
    SIGNATURE = "signature"
    KEystroke = "keystroke"

class AuthStatus(str, Enum):
    PENDING = "pending"
    AUTHENTICATED = "authenticated"
    FAILED = "failed"
    EXPIRED = "expired"
    LOCKED = "locked"

# Data models
class BiometricTemplate(BaseModel):
    id: str
    user_id: str
    biometric_type: BiometricType
    template_data: str  # Base64 encoded template
    quality_score: float  # 0.0 to 1.0
    created_at: datetime
    is_active: bool = True
    device_info: Optional[Dict[str, str]] = None

class AuthenticationRequest(BaseModel):
    user_id: str
    biometric_type: BiometricType
    biometric_data: str  # Base64 encoded biometric data
    device_id: Optional[str] = None
    challenge: Optional[str] = None  # For liveness detection

class AuthenticationResult(BaseModel):
    request_id: str
    user_id: str
    biometric_type: BiometricType
    status: AuthStatus
    confidence_score: float  # 0.0 to 1.0
    match_score: float  # 0.0 to 1.0
    liveness_score: Optional[float] = None
    processing_time: float
    timestamp: datetime
    failure_reason: Optional[str] = None

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    biometric_templates: List[str]  # Template IDs

class AuthenticationSession(BaseModel):
    id: str
    user_id: str
    request_id: str
    status: AuthStatus
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    max_attempts: int = 3

class SecurityPolicy(BaseModel):
    id: str
    name: str
    biometric_types: List[BiometricType]
    min_confidence_threshold: float
    liveness_required: bool
    multi_factor_required: bool
    session_timeout_minutes: int
    max_attempts: int
    lockout_duration_minutes: int

class AuditLog(BaseModel):
    id: str
    user_id: str
    event_type: str  # "login", "logout", "template_created", "template_deleted"
    biometric_type: Optional[BiometricType] = None
    success: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

# In-memory storage
users: Dict[str, User] = {}
biometric_templates: Dict[str, BiometricTemplate] = {}
auth_sessions: Dict[str, AuthenticationSession] = {}
auth_requests: Dict[str, AuthenticationRequest] = {}
auth_results: Dict[str, AuthenticationResult] = {}
security_policies: Dict[str, SecurityPolicy] = {}
audit_logs: Dict[str, List[AuditLog]] = {}

# Utility functions
def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"user_{uuid.uuid4().hex[:8]}"

def generate_template_id() -> str:
    """Generate unique template ID"""
    return f"template_{uuid.uuid4().hex[:8]}"

def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req_{uuid.uuid4().hex[:8]}"

def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"session_{uuid.uuid4().hex[:8]}"

def calculate_match_score(template1: str, template2: str) -> float:
    """Calculate biometric match score (mock implementation)"""
    # In a real implementation, this would use sophisticated matching algorithms
    # For now, we'll simulate matching with some randomness
    
    # Convert to bytes for comparison
    t1_bytes = base64.b64decode(template1)
    t2_bytes = base64.b64decode(template2)
    
    # Simple similarity calculation (mock)
    if len(t1_bytes) != len(t2_bytes):
        return 0.0
    
    matching_bytes = sum(1 for a, b in zip(t1_bytes, t2_bytes) if a == b)
    base_similarity = matching_bytes / len(t1_bytes)
    
    # Add some randomness to simulate real biometric variation
    noise = random.gauss(0, 0.1)
    match_score = max(0.0, min(1.0, base_similarity + noise))
    
    return match_score

def calculate_liveness_score(biometric_data: str, challenge: Optional[str] = None) -> float:
    """Calculate liveness detection score (mock implementation)"""
    # In a real implementation, this would analyze various liveness indicators
    # For now, we'll simulate with randomness
    
    base_score = 0.7  # Base liveness score
    
    # Simulate challenge-response for face recognition
    if challenge:
        # Check if challenge was properly responded to
        challenge_response = random.random()
        base_score += challenge_response * 0.3
    
    # Add some randomness
    noise = random.gauss(0, 0.05)
    liveness_score = max(0.0, min(1.0, base_score + noise))
    
    return liveness_score

def calculate_confidence_score(match_score: float, liveness_score: Optional[float] = None, quality_score: float = 0.8) -> float:
    """Calculate overall confidence score"""
    if liveness_score is not None:
        # Weighted combination of match, liveness, and quality
        confidence = (match_score * 0.5 + liveness_score * 0.3 + quality_score * 0.2)
    else:
        # Only match and quality available
        confidence = (match_score * 0.7 + quality_score * 0.3)
    
    return max(0.0, min(1.0, confidence))

def is_user_locked(user: User) -> bool:
    """Check if user account is locked"""
    if user.locked_until is None:
        return False
    return datetime.now() < user.locked_until

def lock_user(user: User, duration_minutes: int = 15):
    """Lock user account for specified duration"""
    user.locked_until = datetime.now() + timedelta(minutes=duration_minutes)
    user.failed_attempts = 0

def unlock_user(user: User):
    """Unlock user account"""
    user.locked_until = None
    user.failed_attempts = 0

def create_audit_log(user_id: str, event_type: str, success: bool, **kwargs):
    """Create audit log entry"""
    log_id = f"log_{uuid.uuid4().hex[:8]}"
    
    log = AuditLog(
        id=log_id,
        user_id=user_id,
        event_type=event_type,
        biometric_type=kwargs.get("biometric_type"),
        success=success,
        ip_address=kwargs.get("ip_address"),
        user_agent=kwargs.get("user_agent"),
        timestamp=datetime.now(),
        details=kwargs.get("details")
    )
    
    if user_id not in audit_logs:
        audit_logs[user_id] = []
    audit_logs[user_id].append(log)

async def process_authentication(request_id: str):
    """Process biometric authentication request"""
    start_time = datetime.now()
    
    try:
        request = auth_requests[request_id]
        user = users.get(request.user_id)
        
        if not user:
            # Create failed result
            result = AuthenticationResult(
                request_id=request_id,
                user_id=request.user_id,
                biometric_type=request.biometric_type,
                status=AuthStatus.FAILED,
                confidence_score=0.0,
                match_score=0.0,
                processing_time=0.0,
                timestamp=datetime.now(),
                failure_reason="User not found"
            )
            auth_results[request_id] = result
            create_audit_log(request.user_id, "login", False, biometric_type=request.biometric_type, details={"reason": "User not found"})
            return
        
        # Check if user is locked
        if is_user_locked(user):
            result = AuthenticationResult(
                request_id=request_id,
                user_id=request.user_id,
                biometric_type=request.biometric_type,
                status=AuthStatus.LOCKED,
                confidence_score=0.0,
                match_score=0.0,
                processing_time=0.0,
                timestamp=datetime.now(),
                failure_reason="Account locked"
            )
            auth_results[request_id] = result
            create_audit_log(request.user_id, "login", False, biometric_type=request.biometric_type, details={"reason": "Account locked"})
            return
        
        # Find matching biometric template
        user_templates = [t for t in biometric_templates.values() if t.user_id == user.id and t.biometric_type == request.biometric_type and t.is_active]
        
        if not user_templates:
            result = AuthenticationResult(
                request_id=request_id,
                user_id=request.user_id,
                biometric_type=request.biometric_type,
                status=AuthStatus.FAILED,
                confidence_score=0.0,
                match_score=0.0,
                processing_time=0.0,
                timestamp=datetime.now(),
                failure_reason="No biometric template found"
            )
            auth_results[request_id] = result
            create_audit_log(request.user_id, "login", False, biometric_type=request.biometric_type, details={"reason": "No template found"})
            return
        
        # Find best matching template
        best_match = None
        best_score = 0.0
        
        for template in user_templates:
            match_score = calculate_match_score(template.template_data, request.biometric_data)
            if match_score > best_score:
                best_score = match_score
                best_match = template
        
        # Calculate liveness score
        liveness_score = calculate_liveness_score(request.biometric_data, request.challenge)
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(best_score, liveness_score, best_match.quality_score if best_match else 0.0)
        
        # Get security policy (mock - would be based on user/organization)
        min_confidence = 0.7  # Default threshold
        
        # Determine authentication result
        if confidence_score >= min_confidence:
            status = AuthStatus.AUTHENTICATED
            user.last_login = datetime.now()
            user.failed_attempts = 0
            failure_reason = None
            
            create_audit_log(user.id, "login", True, biometric_type=request.biometric_type, 
                           details={"confidence": confidence_score, "match_score": best_score})
        else:
            status = AuthStatus.FAILED
            user.failed_attempts += 1
            failure_reason = f"Low confidence score: {confidence_score:.3f}"
            
            # Lock user after too many failed attempts
            if user.failed_attempts >= 3:
                lock_user(user)
                failure_reason += " - Account locked"
            
            create_audit_log(user.id, "login", False, biometric_type=request.biometric_type,
                           details={"confidence": confidence_score, "match_score": best_score, "reason": failure_reason})
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = AuthenticationResult(
            request_id=request_id,
            user_id=request.user_id,
            biometric_type=request.biometric_type,
            status=status,
            confidence_score=confidence_score,
            match_score=best_score,
            liveness_score=liveness_score,
            processing_time=processing_time,
            timestamp=datetime.now(),
            failure_reason=failure_reason
        )
        
        auth_results[request_id] = result
        
    except Exception as e:
        # Create failed result for any errors
        result = AuthenticationResult(
            request_id=request_id,
            user_id=request.user_id,
            biometric_type=request.biometric_type,
            status=AuthStatus.FAILED,
            confidence_score=0.0,
            match_score=0.0,
            processing_time=0.0,
            timestamp=datetime.now(),
            failure_reason=f"Processing error: {str(e)}"
        )
        auth_results[request_id] = result

# API Endpoints
@app.post("/api/users", response_model=User)
async def create_user(username: str, email: str, full_name: str):
    """Create a new user"""
    user_id = generate_user_id()
    
    user = User(
        id=user_id,
        username=username,
        email=email,
        full_name=full_name,
        created_at=datetime.now()
    )
    
    users[user_id] = user
    create_audit_log(user_id, "user_created", True, details={"username": username, "email": email})
    
    return user

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user information"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.post("/api/users/{user_id}/biometric-templates", response_model=BiometricTemplate)
async def create_biometric_template(user_id: str, biometric_type: BiometricType, template_data: str, device_info: Optional[Dict[str, str]] = None):
    """Create biometric template for user"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    template_id = generate_template_id()
    
    # Calculate quality score (mock implementation)
    quality_score = random.uniform(0.7, 1.0)
    
    template = BiometricTemplate(
        id=template_id,
        user_id=user_id,
        biometric_type=biometric_type,
        template_data=template_data,
        quality_score=quality_score,
        created_at=datetime.now(),
        device_info=device_info
    )
    
    biometric_templates[template_id] = template
    
    # Update user's template list
    users[user_id].biometric_templates.append(template_id)
    
    create_audit_log(user_id, "template_created", True, biometric_type=biometric_type,
                   details={"template_id": template_id, "quality": quality_score})
    
    return template

@app.get("/api/users/{user_id}/biometric-templates", response_model=List[BiometricTemplate])
async def get_user_biometric_templates(user_id: str, biometric_type: Optional[BiometricType] = None):
    """Get user's biometric templates"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    templates = [t for t in biometric_templates.values() if t.user_id == user_id and t.is_active]
    
    if biometric_type:
        templates = [t for t in templates if t.biometric_type == biometric_type]
    
    return templates

@app.post("/api/authenticate", response_model=Dict[str, str])
async def initiate_authentication(request: AuthenticationRequest, background_tasks: BackgroundTasks):
    """Initiate biometric authentication"""
    if request.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    request_id = generate_request_id()
    auth_requests[request_id] = request
    
    # Process authentication asynchronously
    background_tasks.add_task(process_authentication, request_id)
    
    return {"request_id": request_id, "status": "processing"}

@app.get("/api/authenticate/{request_id}/result", response_model=AuthenticationResult)
async def get_authentication_result(request_id: str):
    """Get authentication result"""
    if request_id not in auth_results:
        raise HTTPException(status_code=404, detail="Authentication request not found or not completed")
    
    return auth_results[request_id]

@app.post("/api/authenticate/{request_id}/challenge", response_model=Dict[str, str])
async def generate_liveness_challenge(request_id: str):
    """Generate liveness challenge for face recognition"""
    if request_id not in auth_requests:
        raise HTTPException(status_code=404, detail="Authentication request not found")
    
    # Generate a simple challenge (in reality, this would be more sophisticated)
    challenges = [
        "blink_twice",
        "turn_head_left",
        "smile",
        "raise_eyebrows"
    ]
    
    challenge = random.choice(challenges)
    
    # Update request with challenge
    auth_requests[request_id].challenge = challenge
    
    return {"challenge": challenge, "expires_in": 30}

@app.delete("/api/users/{user_id}/biometric-templates/{template_id}")
async def delete_biometric_template(user_id: str, template_id: str):
    """Delete biometric template"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    if template_id not in biometric_templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = biometric_templates[template_id]
    
    if template.user_id != user_id:
        raise HTTPException(status_code=403, detail="Template does not belong to user")
    
    # Deactivate template (soft delete)
    template.is_active = False
    
    # Remove from user's template list
    if template_id in users[user_id].biometric_templates:
        users[user_id].biometric_templates.remove(template_id)
    
    create_audit_log(user_id, "template_deleted", True, biometric_type=template.biometric_type,
                   details={"template_id": template_id})
    
    return {"message": "Biometric template deleted successfully"}

@app.post("/api/users/{user_id}/unlock")
async def unlock_user_account(user_id: str):
    """Unlock user account"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users[user_id]
    unlock_user(user)
    
    create_audit_log(user_id, "account_unlocked", True, details={"unlocked_by": "admin"})
    
    return {"message": "User account unlocked successfully"}

@app.get("/api/users/{user_id}/audit-logs", response_model=List[AuditLog])
async def get_user_audit_logs(user_id: str, limit: int = 100, event_type: Optional[str] = None):
    """Get user's audit logs"""
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    logs = audit_logs.get(user_id, [])
    
    if event_type:
        logs = [log for log in logs if log.event_type == event_type]
    
    return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.get("/api/stats")
async def get_authentication_stats():
    """Get authentication statistics"""
    total_users = len(users)
    total_templates = len([t for t in biometric_templates.values() if t.is_active])
    total_auth_requests = len(auth_results)
    
    # Calculate success rate
    successful_auths = len([r for r in auth_results.values() if r.status == AuthStatus.AUTHENTICATED])
    success_rate = successful_auths / total_auth_requests if total_auth_requests > 0 else 0
    
    # Biometric type distribution
    biometric_distribution = {}
    for template in biometric_templates.values():
        if template.is_active:
            bio_type = template.biometric_type.value
            biometric_distribution[bio_type] = biometric_distribution.get(bio_type, 0) + 1
    
    # Recent activity
    recent_logs = []
    for user_logs in audit_logs.values():
        recent_logs.extend([log for log in user_logs if log.timestamp > datetime.now() - timedelta(hours=24)])
    
    return {
        "total_users": total_users,
        "total_templates": total_templates,
        "total_authentications": total_auth_requests,
        "success_rate": success_rate,
        "biometric_distribution": biometric_distribution,
        "recent_activity_24h": len(recent_logs),
        "supported_biometric_types": [t.value for t in BiometricType],
        "average_confidence_score": sum(r.confidence_score for r in auth_results.values()) / len(auth_results) if auth_results else 0
    }

@app.get("/api/biometric-types")
async def get_supported_biometric_types():
    """Get supported biometric types"""
    return {
        "types": [
            {
                "type": "fingerprint",
                "name": "Fingerprint Recognition",
                "description": "Fingerprint pattern matching",
                "accuracy": 0.95,
                "liveness_support": True
            },
            {
                "type": "face",
                "name": "Face Recognition",
                "description": "Facial feature analysis",
                "accuracy": 0.97,
                "liveness_support": True
            },
            {
                "type": "iris",
                "name": "Iris Recognition",
                "description": "Iris pattern matching",
                "accuracy": 0.99,
                "liveness_support": True
            },
            {
                "type": "voice",
                "name": "Voice Recognition",
                "description": "Voice print analysis",
                "accuracy": 0.92,
                "liveness_support": True
            },
            {
                "type": "retina",
                "name": "Retina Scan",
                "description": "Retinal blood vessel pattern",
                "accuracy": 0.98,
                "liveness_support": False
            },
            {
                "type": "palm",
                "name": "Palm Recognition",
                "description": "Palm print and vein pattern",
                "accuracy": 0.94,
                "liveness_support": True
            },
            {
                "type": "signature",
                "name": "Signature Verification",
                "description": "Handwritten signature analysis",
                "accuracy": 0.88,
                "liveness_support": False
            },
            {
                "type": "keystroke",
                "name": "Keystroke Dynamics",
                "description": "Typing rhythm analysis",
                "accuracy": 0.85,
                "liveness_support": True
            }
        ]
    }

@app.get("/")
async def root():
    return {"message": "Biometric Authentication API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
