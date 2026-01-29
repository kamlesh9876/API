from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any, Union
import os
import uuid
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json

app = FastAPI(
    title="Email Service API",
    description="Advanced email service for transactional emails, newsletters, and email campaigns",
    version="1.0.0"
)

# Enums
class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"

class EmailType(str, Enum):
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    NOTIFICATION = "notification"
    NEWSLETTER = "newsletter"
    ALERT = "alert"

class TemplateType(str, Enum):
    HTML = "html"
    TEXT = "text"
    MJML = "mjml"

# Data Models
class EmailAttachment(BaseModel):
    filename: str
    content_type: str
    size: int
    content_id: Optional[str] = None
    inline: bool = False

class EmailRecipient(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    variables: Optional[Dict[str, Any]] = {}

class EmailRequest(BaseModel):
    from_email: EmailStr
    from_name: Optional[str] = None
    to: List[EmailRecipient]
    cc: Optional[List[EmailRecipient]] = []
    bcc: Optional[List[EmailRecipient]] = []
    subject: str
    content: str
    content_type: TemplateType = TemplateType.HTML
    attachments: Optional[List[EmailAttachment]] = []
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = {}
    priority: Optional[str] = "normal"  # low, normal, high
    send_at: Optional[datetime] = None
    track_opens: bool = True
    track_clicks: bool = True
    unsubscribe_url: Optional[str] = None
    reply_to: Optional[EmailStr] = None
    headers: Optional[Dict[str, str]] = {}
    tags: Optional[List[str]] = []

class EmailTemplate(BaseModel):
    id: Optional[str] = None
    name: str
    subject: str
    content: str
    content_type: TemplateType = TemplateType.HTML
    description: Optional[str] = None
    variables: Optional[List[str]] = []
    category: Optional[str] = None
    is_active: bool = True

class EmailCampaign(BaseModel):
    name: str
    subject: str
    content: str
    content_type: TemplateType = TemplateType.HTML
    template_id: Optional[str] = None
    recipients: List[EmailRecipient]
    scheduled_at: Optional[datetime] = None
    send_immediately: bool = False
    track_opens: bool = True
    track_clicks: bool = True
    unsubscribe_url: Optional[str] = None
    tags: Optional[List[str]] = []

class EmailFilter(BaseModel):
    status: Optional[EmailStatus] = None
    email_type: Optional[EmailType] = None
    from_email: Optional[EmailStr] = None
    to_email: Optional[EmailStr] = None
    subject_contains: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None

# Storage (in production, use database)
emails = {}
templates = {}
campaigns = {}
email_stats = {
    "total_sent": 0,
    "total_delivered": 0,
    "total_opened": 0,
    "total_clicked": 0,
    "total_failed": 0,
    "total_bounced": 0
}

@app.get("/")
async def root():
    return {"message": "Email Service API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Email Sending Endpoints
@app.post("/api/email/send")
async def send_email(email_request: EmailRequest, background_tasks: BackgroundTasks):
    """Send a single email or multiple emails"""
    try:
        email_id = str(uuid.uuid4())
        
        # Create email record
        email_record = {
            "id": email_id,
            "from_email": email_request.from_email,
            "from_name": email_request.from_name,
            "to": [recipient.dict() for recipient in email_request.to],
            "cc": [recipient.dict() for recipient in email_request.cc],
            "bcc": [recipient.dict() for recipient in email_request.bcc],
            "subject": email_request.subject,
            "content": email_request.content,
            "content_type": email_request.content_type,
            "attachments": [att.dict() for att in email_request.attachments] if email_request.attachments else [],
            "template_id": email_request.template_id,
            "template_variables": email_request.template_variables,
            "priority": email_request.priority,
            "send_at": email_request.send_at.isoformat() if email_request.send_at else None,
            "track_opens": email_request.track_opens,
            "track_clicks": email_request.track_clicks,
            "unsubscribe_url": email_request.unsubscribe_url,
            "reply_to": email_request.reply_to,
            "headers": email_request.headers,
            "tags": email_request.tags,
            "status": EmailStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "sent_at": None,
            "delivered_at": None,
            "opened_at": None,
            "clicked_at": None,
            "error_message": None
        }
        
        emails[email_id] = email_record
        
        # Schedule email sending
        if email_request.send_at and email_request.send_at > datetime.now():
            # Schedule for later
            background_tasks.add_task(schedule_email, email_id)
        else:
            # Send immediately
            background_tasks.add_task(send_email_background, email_id)
        
        return {
            "success": True,
            "email_id": email_id,
            "message": "Email queued for sending",
            "scheduled_for": email_request.send_at.isoformat() if email_request.send_at else "immediately"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue email: {str(e)}")

@app.post("/api/email/send-bulk")
async def send_bulk_emails(
    email_requests: List[EmailRequest],
    background_tasks: BackgroundTasks,
    batch_size: int = 100
):
    """Send multiple emails in bulk"""
    try:
        batch_id = str(uuid.uuid4())
        email_ids = []
        
        # Process in batches
        for i in range(0, len(email_requests), batch_size):
            batch = email_requests[i:i + batch_size]
            
            for email_request in batch:
                email_id = str(uuid.uuid4())
                
                email_record = {
                    "id": email_id,
                    "batch_id": batch_id,
                    "from_email": email_request.from_email,
                    "from_name": email_request.from_name,
                    "to": [recipient.dict() for recipient in email_request.to],
                    "subject": email_request.subject,
                    "content": email_request.content,
                    "content_type": email_request.content_type,
                    "status": EmailStatus.PENDING,
                    "created_at": datetime.now().isoformat(),
                    "batch_index": i // batch_size
                }
                
                emails[email_id] = email_record
                email_ids.append(email_id)
                
                # Schedule sending
                background_tasks.add_task(send_email_background, email_id)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "email_count": len(email_requests),
            "email_ids": email_ids,
            "message": f"Bulk email job created with {len(email_requests)} emails"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bulk email job: {str(e)}")

# Template Management
@app.post("/api/templates")
async def create_template(template: EmailTemplate):
    """Create a new email template"""
    try:
        template_id = str(uuid.uuid4())
        
        template_record = template.dict()
        template_record["id"] = template_id
        template_record["created_at"] = datetime.now().isoformat()
        template_record["updated_at"] = datetime.now().isoformat()
        template_record["usage_count"] = 0
        
        templates[template_id] = template_record
        
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
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """List email templates"""
    try:
        filtered_templates = list(templates.values())
        
        # Apply filters
        if category:
            filtered_templates = [t for t in filtered_templates if t.get("category") == category]
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

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template"""
    if template_id not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "success": True,
        "template": templates[template_id]
    }

@app.put("/api/templates/{template_id}")
async def update_template(template_id: str, template: EmailTemplate):
    """Update an existing template"""
    try:
        if template_id not in templates:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_record = template.dict()
        template_record["id"] = template_id
        template_record["updated_at"] = datetime.now().isoformat()
        
        templates[template_id] = template_record
        
        return {
            "success": True,
            "message": "Template updated successfully",
            "template": template_record
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    try:
        if template_id not in templates:
            raise HTTPException(status_code=404, detail="Template not found")
        
        del templates[template_id]
        
        return {
            "success": True,
            "message": "Template deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")

# Campaign Management
@app.post("/api/campaigns")
async def create_campaign(campaign: EmailCampaign, background_tasks: BackgroundTasks):
    """Create an email campaign"""
    try:
        campaign_id = str(uuid.uuid4())
        
        campaign_record = {
            "id": campaign_id,
            "name": campaign.name,
            "subject": campaign.subject,
            "content": campaign.content,
            "content_type": campaign.content_type,
            "template_id": campaign.template_id,
            "recipients": [recipient.dict() for recipient in campaign.recipients],
            "scheduled_at": campaign.scheduled_at.isoformat() if campaign.scheduled_at else None,
            "send_immediately": campaign.send_immediately,
            "track_opens": campaign.track_opens,
            "track_clicks": campaign.track_clicks,
            "unsubscribe_url": campaign.unsubscribe_url,
            "tags": campaign.tags,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "sent_count": 0,
            "delivered_count": 0,
            "opened_count": 0,
            "clicked_count": 0,
            "failed_count": 0
        }
        
        campaigns[campaign_id] = campaign_record
        
        # Schedule campaign
        if campaign.send_immediately:
            background_tasks.add_task(execute_campaign, campaign_id)
        elif campaign.scheduled_at:
            background_tasks.add_task(schedule_campaign, campaign_id)
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": "Campaign created successfully",
            "campaign": campaign_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

@app.get("/api/campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List email campaigns"""
    try:
        filtered_campaigns = list(campaigns.values())
        
        if status:
            filtered_campaigns = [c for c in filtered_campaigns if c.get("status") == status]
        
        total = len(filtered_campaigns)
        paginated_campaigns = filtered_campaigns[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "campaigns": paginated_campaigns
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list campaigns: {str(e)}")

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "success": True,
        "campaign": campaigns[campaign_id]
    }

# Email Tracking and Analytics
@app.get("/api/emails")
async def list_emails(
    filters: Optional[EmailFilter] = None,
    limit: int = 50,
    offset: int = 0
):
    """List emails with optional filtering"""
    try:
        filtered_emails = list(emails.values())
        
        # Apply filters
        if filters:
            if filters.status:
                filtered_emails = [e for e in filtered_emails if e.get("status") == filters.status]
            if filters.from_email:
                filtered_emails = [e for e in filtered_emails if e.get("from_email") == filters.from_email]
            if filters.subject_contains:
                filtered_emails = [e for e in filtered_emails if filters.subject_contains.lower() in e.get("subject", "").lower()]
            if filters.date_from:
                filtered_emails = [e for e in filtered_emails if datetime.fromisoformat(e.get("created_at")) >= filters.date_from]
            if filters.date_to:
                filtered_emails = [e for e in filtered_emails if datetime.fromisoformat(e.get("created_at")) <= filters.date_to]
        
        # Apply pagination
        total = len(filtered_emails)
        paginated_emails = filtered_emails[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "emails": paginated_emails
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list emails: {str(e)}")

@app.get("/api/emails/{email_id}")
async def get_email(email_id: str):
    """Get email details"""
    if email_id not in emails:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {
        "success": True,
        "email": emails[email_id]
    }

@app.post("/api/emails/{email_id}/track-open")
async def track_email_open(email_id: str):
    """Track email open event"""
    try:
        if email_id not in emails:
            raise HTTPException(status_code=404, detail="Email not found")
        
        emails[email_id]["status"] = EmailStatus.OPENED
        emails[email_id]["opened_at"] = datetime.now().isoformat()
        email_stats["total_opened"] += 1
        
        # Return tracking pixel
        return JSONResponse(
            content={"status": "tracked"},
            headers={"Content-Type": "image/gif"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track open: {str(e)}")

@app.post("/api/emails/{email_id}/track-click")
async def track_email_click(email_id: str, url: str):
    """Track email click event"""
    try:
        if email_id not in emails:
            raise HTTPException(status_code=404, detail="Email not found")
        
        emails[email_id]["status"] = EmailStatus.CLICKED
        emails[email_id]["clicked_at"] = datetime.now().isoformat()
        email_stats["total_clicked"] += 1
        
        return {
            "success": True,
            "message": "Click tracked successfully",
            "redirect_url": url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track click: {str(e)}")

@app.get("/api/analytics/stats")
async def get_email_stats(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """Get email statistics and analytics"""
    try:
        # Filter emails by date range if provided
        filtered_emails = list(emails.values())
        if date_from:
            filtered_emails = [e for e in filtered_emails if datetime.fromisoformat(e.get("created_at")) >= date_from]
        if date_to:
            filtered_emails = [e for e in filtered_emails if datetime.fromisoformat(e.get("created_at")) <= date_to]
        
        # Calculate stats
        stats = {
            "total_emails": len(filtered_emails),
            "sent": len([e for e in filtered_emails if e.get("status") == EmailStatus.SENT]),
            "delivered": len([e for e in filtered_emails if e.get("status") == EmailStatus.DELIVERED]),
            "opened": len([e for e in filtered_emails if e.get("status") == EmailStatus.OPENED]),
            "clicked": len([e for e in filtered_emails if e.get("status") == EmailStatus.CLICKED]),
            "failed": len([e for e in filtered_emails if e.get("status") == EmailStatus.FAILED]),
            "bounced": len([e for e in filtered_emails if e.get("status") == EmailStatus.BOUNCED]),
            "open_rate": 0,
            "click_rate": 0,
            "delivery_rate": 0
        }
        
        # Calculate rates
        if stats["delivered"] > 0:
            stats["open_rate"] = (stats["opened"] / stats["delivered"]) * 100
            stats["click_rate"] = (stats["clicked"] / stats["delivered"]) * 100
        
        if stats["total_emails"] > 0:
            stats["delivery_rate"] = (stats["delivered"] / stats["total_emails"]) * 100
        
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

# Background Tasks
async def send_email_background(email_id: str):
    """Background task to send email"""
    try:
        if email_id not in emails:
            return
        
        email_record = emails[email_id]
        
        # Simulate email sending
        await asyncio.sleep(1)  # Simulate SMTP delay
        
        # Update status
        email_record["status"] = EmailStatus.SENT
        email_record["sent_at"] = datetime.now().isoformat()
        email_stats["total_sent"] += 1
        
        # Simulate delivery
        await asyncio.sleep(2)
        email_record["status"] = EmailStatus.DELIVERED
        email_record["delivered_at"] = datetime.now().isoformat()
        email_stats["total_delivered"] += 1
        
    except Exception as e:
        if email_id in emails:
            emails[email_id]["status"] = EmailStatus.FAILED
            emails[email_id]["error_message"] = str(e)
        email_stats["total_failed"] += 1

async def schedule_email(email_id: str):
    """Schedule email for future sending"""
    try:
        if email_id not in emails:
            return
        
        email_record = emails[email_id]
        send_at = datetime.fromisoformat(email_record["send_at"])
        
        # Wait until scheduled time
        now = datetime.now()
        if send_at > now:
            await asyncio.sleep((send_at - now).total_seconds())
        
        # Send the email
        await send_email_background(email_id)
        
    except Exception as e:
        if email_id in emails:
            emails[email_id]["status"] = EmailStatus.FAILED
            emails[email_id]["error_message"] = str(e)

async def execute_campaign(campaign_id: str):
    """Execute email campaign"""
    try:
        if campaign_id not in campaigns:
            return
        
        campaign = campaigns[campaign_id]
        campaign["status"] = "running"
        
        recipients = campaign["recipients"]
        
        for i, recipient in enumerate(recipients):
            # Create email request for each recipient
            email_request = EmailRequest(
                from_email="campaign@example.com",
                to=[EmailRecipient(**recipient)],
                subject=campaign["subject"],
                content=campaign["content"],
                content_type=campaign["content_type"],
                track_opens=campaign["track_opens"],
                track_clicks=campaign["track_clicks"],
                unsubscribe_url=campaign["unsubscribe_url"]
            )
            
            # Send email
            email_id = str(uuid.uuid4())
            emails[email_id] = {
                "id": email_id,
                "campaign_id": campaign_id,
                **email_request.dict(),
                "status": EmailStatus.PENDING,
                "created_at": datetime.now().isoformat()
            }
            
            await send_email_background(email_id)
            
            # Update campaign stats
            campaign["sent_count"] = i + 1
            
            # Small delay between sends
            await asyncio.sleep(0.1)
        
        campaign["status"] = "completed"
        
    except Exception as e:
        if campaign_id in campaigns:
            campaigns[campaign_id]["status"] = "failed"
            campaigns[campaign_id]["error_message"] = str(e)

async def schedule_campaign(campaign_id: str):
    """Schedule campaign for future execution"""
    try:
        if campaign_id not in campaigns:
            return
        
        campaign = campaigns[campaign_id]
        scheduled_at = datetime.fromisoformat(campaign["scheduled_at"])
        
        # Wait until scheduled time
        now = datetime.now()
        if scheduled_at > now:
            await asyncio.sleep((scheduled_at - now).total_seconds())
        
        # Execute the campaign
        await execute_campaign(campaign_id)
        
    except Exception as e:
        if campaign_id in campaigns:
            campaigns[campaign_id]["status"] = "failed"
            campaigns[campaign_id]["error_message"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
