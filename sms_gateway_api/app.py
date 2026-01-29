from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime, timedelta
import re
import json

app = FastAPI(
    title="SMS Gateway API",
    description="Advanced SMS gateway service for text messaging, OTP verification, and SMS campaigns",
    version="1.0.0"
)

# Enums
class SMSStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"
    EXPIRED = "expired"
    REJECTED = "rejected"

class SMSType(str, Enum):
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    OTP = "otp"
    ALERT = "alert"
    MARKETING = "marketing"

class MessageType(str, Enum):
    TEXT = "text"
    UNICODE = "unicode"
    BINARY = "binary"
    FLASH = "flash"

class Provider(str, Enum):
    TWILIO = "twilio"
    AWS_SNS = "aws_sns"
    PLIVO = "plivo"
    NEXMO = "nexmo"
    CLICKATELL = "clickatell"

# Data Models
class PhoneNumber(BaseModel):
    number: str
    country_code: Optional[str] = None
    name: Optional[str] = None
    
    @validator('number')
    def validate_phone_number(cls, v):
        # Basic phone number validation
        if not re.match(r'^\+?[1-9]\d{1,14}$', v.replace('-', '').replace(' ', '')):
            raise ValueError('Invalid phone number format')
        return v

class SMSMessage(BaseModel):
    to: List[PhoneNumber]
    from_number: Optional[str] = None
    message: str
    message_type: MessageType = MessageType.TEXT
    sms_type: SMSType = SMSType.TRANSACTIONAL
    provider: Optional[Provider] = None
    schedule_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None
    priority: Optional[int] = 1  # 1 (highest) to 5 (lowest)
    callback_url: Optional[str] = None
    custom_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('message')
    def validate_message_length(cls, v):
        if len(v) > 1600:  # Standard SMS limit
            raise ValueError('Message too long (max 1600 characters)')
        return v

class OTPRequest(BaseModel):
    phone_number: PhoneNumber
    length: int = 6
    expiry_minutes: int = 5
    alphanumeric: bool = False
    custom_message: Optional[str] = None
    template_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class OTPVerification(BaseModel):
    phone_number: PhoneNumber
    otp_code: str
    session_id: Optional[str] = None

class SMSTemplate(BaseModel):
    id: Optional[str] = None
    name: str
    content: str
    variables: Optional[List[str]] = []
    category: Optional[str] = None
    sms_type: SMSType = SMSType.TRANSACTIONAL
    is_active: bool = True

class SMSBatch(BaseModel):
    name: str
    recipients: List[PhoneNumber]
    message: str
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = {}
    sms_type: SMSType = SMSType.TRANSACTIONAL
    schedule_at: Optional[datetime] = None
    send_immediately: bool = False
    callback_url: Optional[str] = None

class SMSFilter(BaseModel):
    status: Optional[SMSStatus] = None
    sms_type: Optional[SMSType] = None
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    provider: Optional[Provider] = None

# Storage (in production, use database)
sms_messages = {}
otp_sessions = {}
sms_templates = {}
sms_batches = {}
sms_stats = {
    "total_sent": 0,
    "total_delivered": 0,
    "total_failed": 0,
    "total_otp_generated": 0,
    "total_otp_verified": 0
}

@app.get("/")
async def root():
    return {"message": "SMS Gateway API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# SMS Sending Endpoints
@app.post("/api/sms/send")
async def send_sms(sms_message: SMSMessage, background_tasks: BackgroundTasks):
    """Send SMS message to one or more recipients"""
    try:
        sms_id = str(uuid.uuid4())
        
        # Create SMS records for each recipient
        sms_records = []
        for recipient in sms_message.to:
            record_id = str(uuid.uuid4())
            
            sms_record = {
                "id": record_id,
                "batch_id": sms_id,
                "to": recipient.dict(),
                "from_number": sms_message.from_number,
                "message": sms_message.message,
                "message_type": sms_message.message_type,
                "sms_type": sms_message.sms_type,
                "provider": sms_message.provider,
                "schedule_at": sms_message.schedule_at.isoformat() if sms_message.schedule_at else None,
                "expire_at": sms_message.expire_at.isoformat() if sms_message.expire_at else None,
                "priority": sms_message.priority,
                "callback_url": sms_message.callback_url,
                "custom_id": sms_message.custom_id,
                "metadata": sms_message.metadata,
                "status": SMSStatus.PENDING,
                "created_at": datetime.now().isoformat(),
                "sent_at": None,
                "delivered_at": None,
                "error_message": None,
                "segments": 1,  # Calculate based on message length
                "cost": 0.05  # Calculate based on provider and destination
            }
            
            sms_messages[record_id] = sms_record
            sms_records.append(sms_record)
            
            # Schedule sending
            if sms_message.schedule_at and sms_message.schedule_at > datetime.now():
                background_tasks.add_task(schedule_sms, record_id)
            else:
                background_tasks.add_task(send_sms_background, record_id)
        
        return {
            "success": True,
            "batch_id": sms_id,
            "message_count": len(sms_records),
            "message_ids": [record["id"] for record in sms_records],
            "scheduled_for": sms_message.schedule_at.isoformat() if sms_message.schedule_at else "immediately"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")

@app.post("/api/sms/send-batch")
async def send_sms_batch(
    batch_request: SMSBatch,
    background_tasks: BackgroundTasks,
    batch_size: int = 100
):
    """Send SMS to multiple recipients in batches"""
    try:
        batch_id = str(uuid.uuid4())
        sms_ids = []
        
        # Process in batches
        for i in range(0, len(batch_request.recipients), batch_size):
            batch_recipients = batch_request.recipients[i:i + batch_size]
            
            for recipient in batch_recipients:
                sms_id = str(uuid.uuid4())
                
                sms_record = {
                    "id": sms_id,
                    "batch_id": batch_id,
                    "to": recipient.dict(),
                    "from_number": None,
                    "message": batch_request.message,
                    "message_type": MessageType.TEXT,
                    "sms_type": batch_request.sms_type,
                    "template_id": batch_request.template_id,
                    "template_variables": batch_request.template_variables,
                    "callback_url": batch_request.callback_url,
                    "status": SMSStatus.PENDING,
                    "created_at": datetime.now().isoformat(),
                    "batch_index": i // batch_size
                }
                
                sms_messages[sms_id] = sms_record
                sms_ids.append(sms_id)
                
                # Schedule sending
                if batch_request.send_immediately:
                    background_tasks.add_task(send_sms_background, sms_id)
                elif batch_request.schedule_at:
                    background_tasks.add_task(schedule_sms, sms_id)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "recipient_count": len(batch_request.recipients),
            "message_ids": sms_ids,
            "message": f"Batch SMS job created with {len(batch_request.recipients)} recipients"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create batch SMS: {str(e)}")

# OTP Management
@app.post("/api/otp/generate")
async def generate_otp(otp_request: OTPRequest, background_tasks: BackgroundTasks):
    """Generate and send OTP to phone number"""
    try:
        session_id = str(uuid.uuid4())
        
        # Generate OTP code
        import random
        import string
        
        if otp_request.alphanumeric:
            characters = string.ascii_uppercase + string.digits
            otp_code = ''.join(random.choice(characters) for _ in range(otp_request.length))
        else:
            otp_code = ''.join(random.choice(string.digits) for _ in range(otp_request.length))
        
        # Create OTP session
        otp_session = {
            "session_id": session_id,
            "phone_number": otp_request.phone_number.dict(),
            "otp_code": otp_code,
            "length": otp_request.length,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=otp_request.expiry_minutes)).isoformat(),
            "attempts": 0,
            "max_attempts": 3,
            "is_verified": False,
            "custom_message": otp_request.custom_message,
            "template_id": otp_request.template_id,
            "metadata": otp_request.metadata
        }
        
        otp_sessions[session_id] = otp_session
        
        # Create message
        message = otp_request.custom_message or f"Your verification code is: {otp_code}. Valid for {otp_request.expiry_minutes} minutes."
        
        # Send OTP via SMS
        sms_message = SMSMessage(
            to=[otp_request.phone_number],
            message=message,
            sms_type=SMSType.OTP,
            priority=1,  # High priority for OTP
            metadata={"otp_session_id": session_id}
        )
        
        await send_sms(sms_message, background_tasks)
        
        # Schedule OTP expiry
        background_tasks.add_task(expire_otp, session_id, otp_request.expiry_minutes * 60)
        
        sms_stats["total_otp_generated"] += 1
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "OTP generated and sent successfully",
            "expires_at": otp_session["expires_at"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate OTP: {str(e)}")

@app.post("/api/otp/verify")
async def verify_otp(verification: OTPVerification):
    """Verify OTP code"""
    try:
        # Find OTP session for this phone number
        session = None
        for sess_id, sess_data in otp_sessions.items():
            if (sess_data["phone_number"]["number"] == verification.phone_number.number and 
                not sess_data["is_verified"] and
                datetime.fromisoformat(sess_data["expires_at"]) > datetime.now()):
                session = sess_data
                break
        
        if not session:
            raise HTTPException(status_code=404, detail="No active OTP session found")
        
        # Check attempts
        if session["attempts"] >= session["max_attempts"]:
            raise HTTPException(status_code=429, detail="Maximum attempts exceeded")
        
        # Verify OTP
        session["attempts"] += 1
        
        if verification.otp_code == session["otp_code"]:
            session["is_verified"] = True
            session["verified_at"] = datetime.now().isoformat()
            sms_stats["total_otp_verified"] += 1
            
            return {
                "success": True,
                "message": "OTP verified successfully",
                "session_id": session["session_id"],
                "verified_at": session["verified_at"]
            }
        else:
            return {
                "success": False,
                "message": "Invalid OTP code",
                "attempts_remaining": session["max_attempts"] - session["attempts"]
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")

@app.post("/api/otp/resend")
async def resend_otp(session_id: str, background_tasks: BackgroundTasks):
    """Resend OTP"""
    try:
        if session_id not in otp_sessions:
            raise HTTPException(status_code=404, detail="OTP session not found")
        
        session = otp_sessions[session_id]
        
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            raise HTTPException(status_code=400, detail="OTP session expired")
        
        # Generate new OTP
        import random
        import string
        
        if session["length"] > 6 or any(c.isalpha() for c in session["otp_code"]):
            characters = string.ascii_uppercase + string.digits
            new_otp = ''.join(random.choice(characters) for _ in range(session["length"]))
        else:
            new_otp = ''.join(random.choice(string.digits) for _ in range(session["length"]))
        
        session["otp_code"] = new_otp
        session["attempts"] = 0
        session["created_at"] = datetime.now().isoformat()
        
        # Resend SMS
        message = session["custom_message"] or f"Your verification code is: {new_otp}. Valid for 5 minutes."
        
        phone_number = PhoneNumber(**session["phone_number"])
        sms_message = SMSMessage(
            to=[phone_number],
            message=message,
            sms_type=SMSType.OTP,
            priority=1,
            metadata={"otp_session_id": session_id}
        )
        
        await send_sms(sms_message, background_tasks)
        
        return {
            "success": True,
            "message": "OTP resent successfully",
            "expires_at": session["expires_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend OTP: {str(e)}")

# Template Management
@app.post("/api/templates")
async def create_template(template: SMSTemplate):
    """Create SMS template"""
    try:
        template_id = str(uuid.uuid4())
        
        template_record = template.dict()
        template_record["id"] = template_id
        template_record["created_at"] = datetime.now().isoformat()
        template_record["updated_at"] = datetime.now().isoformat()
        template_record["usage_count"] = 0
        
        sms_templates[template_id] = template_record
        
        return {
            "success": True,
            "template_id": template_id,
            "message": "Template created successfully",
            "template": template_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

@app.get("/api/templates")
async def list_templates(
    category: Optional[str] = None,
    sms_type: Optional[SMSType] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """List SMS templates"""
    try:
        filtered_templates = list(sms_templates.values())
        
        # Apply filters
        if category:
            filtered_templates = [t for t in filtered_templates if t.get("category") == category]
        if sms_type:
            filtered_templates = [t for t in filtered_templates if t.get("sms_type") == sms_type]
        if is_active is not None:
            filtered_templates = [t for t in filtered_templates if t.get("is_active") == is_active]
        
        # Apply pagination
        total = len(filtered_templates)
        paginated_templates = filtered_templates[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "templates": paginated_templates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")

# SMS Tracking and Analytics
@app.get("/api/sms")
async def list_sms(
    filters: Optional[SMSFilter] = None,
    limit: int = 50,
    offset: int = 0
):
    """List SMS messages with optional filtering"""
    try:
        filtered_messages = list(sms_messages.values())
        
        # Apply filters
        if filters:
            if filters.status:
                filtered_messages = [m for m in filtered_messages if m.get("status") == filters.status]
            if filters.sms_type:
                filtered_messages = [m for m in filtered_messages if m.get("sms_type") == filters.sms_type]
            if filters.from_number:
                filtered_messages = [m for m in filtered_messages if m.get("from_number") == filters.from_number]
            if filters.to_number:
                filtered_messages = [m for m in filtered_messages if m["to"]["number"] == filters.to_number]
            if filters.date_from:
                filtered_messages = [m for m in filtered_messages if datetime.fromisoformat(m.get("created_at")) >= filters.date_from]
            if filters.date_to:
                filtered_messages = [m for m in filtered_messages if datetime.fromisoformat(m.get("created_at")) <= filters.date_to]
        
        # Apply pagination
        total = len(filtered_messages)
        paginated_messages = filtered_messages[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "messages": paginated_messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list SMS: {str(e)}")

@app.get("/api/sms/{sms_id}")
async def get_sms(sms_id: str):
    """Get SMS details"""
    if sms_id not in sms_messages:
        raise HTTPException(status_code=404, detail="SMS not found")
    
    return {
        "success": True,
        "sms": sms_messages[sms_id]
    }

@app.post("/api/sms/{sms_id}/webhook")
async def sms_webhook(sms_id: str, webhook_data: Dict[str, Any]):
    """Handle SMS delivery webhook"""
    try:
        if sms_id not in sms_messages:
            raise HTTPException(status_code=404, detail="SMS not found")
        
        sms_record = sms_messages[sms_id]
        
        # Update status based on webhook
        status = webhook_data.get("status")
        if status:
            sms_record["status"] = status
            sms_record["delivered_at"] = datetime.now().isoformat()
            
            # Update stats
            if status == SMSStatus.DELIVERED:
                sms_stats["total_delivered"] += 1
            elif status in [SMSStatus.FAILED, SMSStatus.UNDELIVERED]:
                sms_stats["total_failed"] += 1
        
        # Store webhook data
        sms_record["webhook_data"] = webhook_data
        sms_record["webhook_received_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Webhook processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.get("/api/analytics/stats")
async def get_sms_stats(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """Get SMS statistics and analytics"""
    try:
        # Filter SMS by date range if provided
        filtered_messages = list(sms_messages.values())
        if date_from:
            filtered_messages = [m for m in filtered_messages if datetime.fromisoformat(m.get("created_at")) >= date_from]
        if date_to:
            filtered_messages = [m for m in filtered_messages if datetime.fromisoformat(m.get("created_at")) <= date_to]
        
        # Calculate stats
        stats = {
            "total_sms": len(filtered_messages),
            "sent": len([m for m in filtered_messages if m.get("status") == SMSStatus.SENT]),
            "delivered": len([m for m in filtered_messages if m.get("status") == SMSStatus.DELIVERED]),
            "failed": len([m for m in filtered_messages if m.get("status") in [SMSStatus.FAILED, SMSStatus.UNDELIVERED]]),
            "pending": len([m for m in filtered_messages if m.get("status") == SMSStatus.PENDING]),
            "delivery_rate": 0,
            "total_cost": sum(m.get("cost", 0) for m in filtered_messages),
            "total_segments": sum(m.get("segments", 1) for m in filtered_messages)
        }
        
        # Calculate delivery rate
        if stats["sent"] > 0:
            stats["delivery_rate"] = (stats["delivered"] / stats["sent"]) * 100
        
        # Add OTP stats
        stats.update({
            "total_otp_generated": sms_stats["total_otp_generated"],
            "total_otp_verified": sms_stats["total_otp_verified"],
            "otp_success_rate": (sms_stats["total_otp_verified"] / sms_stats["total_otp_generated"] * 100) if sms_stats["total_otp_generated"] > 0 else 0
        })
        
        return {
            "success": True,
            "statistics": stats,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Utility Endpoints
@app.get("/api/phone/validate/{phone_number}")
async def validate_phone_number(phone_number: str):
    """Validate phone number format"""
    try:
        # Remove non-numeric characters except +
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        
        # Basic validation
        if not re.match(r'^\+?[1-9]\d{1,14}$', clean_number):
            return {
                "valid": False,
                "error": "Invalid phone number format"
            }
        
        # Get country info (simplified)
        country_code = None
        if clean_number.startswith('+'):
            country_code = clean_number[1:3]  # Simple country code extraction
        
        return {
            "valid": True,
            "formatted": clean_number,
            "country_code": country_code,
            "international": clean_number if clean_number.startswith('+') else f"+{clean_number}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phone validation failed: {str(e)}")

# Background Tasks
async def send_sms_background(sms_id: str):
    """Background task to send SMS"""
    try:
        if sms_id not in sms_messages:
            return
        
        sms_record = sms_messages[sms_id]
        
        # Simulate SMS sending
        await asyncio.sleep(1)  # Simulate provider delay
        
        # Update status
        sms_record["status"] = SMSStatus.SENT
        sms_record["sent_at"] = datetime.now().isoformat()
        sms_stats["total_sent"] += 1
        
        # Simulate delivery
        await asyncio.sleep(2)
        sms_record["status"] = SMSStatus.DELIVERED
        sms_record["delivered_at"] = datetime.now().isoformat()
        sms_stats["total_delivered"] += 1
        
        # Send webhook if callback URL provided
        if sms_record.get("callback_url"):
            # In production, make actual HTTP request
            pass
        
    except Exception as e:
        if sms_id in sms_messages:
            sms_messages[sms_id]["status"] = SMSStatus.FAILED
            sms_messages[sms_id]["error_message"] = str(e)
        sms_stats["total_failed"] += 1

async def schedule_sms(sms_id: str):
    """Schedule SMS for future sending"""
    try:
        if sms_id not in sms_messages:
            return
        
        sms_record = sms_messages[sms_id]
        schedule_at = datetime.fromisoformat(sms_record["schedule_at"])
        
        # Wait until scheduled time
        now = datetime.now()
        if schedule_at > now:
            await asyncio.sleep((schedule_at - now).total_seconds())
        
        # Send the SMS
        await send_sms_background(sms_id)
        
    except Exception as e:
        if sms_id in sms_messages:
            sms_messages[sms_id]["status"] = SMSStatus.FAILED
            sms_messages[sms_id]["error_message"] = str(e)

async def expire_otp(session_id: str, delay_seconds: int):
    """Expire OTP session after delay"""
    await asyncio.sleep(delay_seconds)
    
    if session_id in otp_sessions:
        otp_sessions[session_id]["expired"] = True

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
