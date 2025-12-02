from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from enum import Enum
import random
import re

app = FastAPI(title="Email Marketing API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"

class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    UNSUBSCRIBED = "unsubscribed"
    FAILED = "failed"

class ListType(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    SEGMENTED = "segmented"

class AutomationTriggerType(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    PURCHASE = "purchase"
    BIRTHDAY = "birthday"
    ANNIVERSARY = "anniversary"
    CUSTOM_EVENT = "custom_event"

# Data models
class Contact(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    is_active: bool = True
    date_added: datetime
    last_updated: datetime
    email_stats: Dict[str, Any] = {
        "emails_sent": 0,
        "emails_opened": 0,
        "emails_clicked": 0,
        "last_opened": None,
        "last_clicked": None
    }

class EmailList(BaseModel):
    id: str
    name: str
    description: str
    list_type: ListType
    contact_count: int = 0
    tags: List[str] = []
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class EmailTemplate(BaseModel):
    id: str
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    template_type: str  # "marketing", "transactional", "newsletter"
    category: Optional[str] = None
    tags: List[str] = []
    variables: List[str] = []  # Template variables like {{first_name}}
    is_active: bool = True
    created_by: str
    created_at: datetime
    updated_at: datetime

class Campaign(BaseModel):
    id: str
    name: str
    subject: str
    from_email: str
    from_name: str
    reply_to: Optional[str] = None
    template_id: str
    list_ids: List[str]
    status: CampaignStatus
    scheduled_time: Optional[datetime] = None
    sent_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    total_recipients: int = 0
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    bounced_count: int = 0
    unsubscribed_count: int = 0
    complained_count: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    unsubscribe_rate: float = 0.0
    settings: Dict[str, Any] = {
        "track_opens": True,
        "track_clicks": True,
        "unsubscribe_link": True,
        "suppress_duplicates": True
    }
    created_by: str
    created_at: datetime
    updated_at: datetime

class Email(BaseModel):
    id: str
    campaign_id: Optional[str] = None
    contact_id: str
    to_email: str
    from_email: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    status: EmailStatus
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    opened_time: Optional[datetime] = None
    clicked_time: Optional[datetime] = None
    bounced_time: Optional[datetime] = None
    unsubscribed_time: Optional[datetime] = None
    error_message: Optional[str] = None
    tracking_pixel_id: Optional[str] = None
    unsubscribe_link_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Automation(BaseModel):
    id: str
    name: str
    description: str
    trigger_type: AutomationTriggerType
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

class EmailAnalytics(BaseModel):
    id: str
    campaign_id: Optional[str] = None
    date: datetime
    emails_sent: int = 0
    emails_delivered: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    emails_bounced: int = 0
    emails_unsubscribed: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    unsubscribe_rate: float = 0.0

class SMTPConfig(BaseModel):
    id: str
    name: str
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    from_email: str
    from_name: str
    reply_to: Optional[str] = None
    daily_limit: int = 10000
    hourly_limit: int = 1000
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

# In-memory storage
contacts: Dict[str, Contact] = {}
email_lists: Dict[str, EmailList] = {}
list_contacts: Dict[str, List[str]] = {}  # list_id -> list of contact_ids
email_templates: Dict[str, EmailTemplate] = {}
campaigns: Dict[str, Campaign] = {}
emails: Dict[str, Email] = {}
automations: Dict[str, Automation] = {}
email_analytics: Dict[str, List[EmailAnalytics]] = {}  # campaign_id -> list of analytics
smtp_configs: Dict[str, SMTPConfig] = {}
websocket_connections: Dict[str, WebSocket] = {}

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # campaign_id -> list of connections

    async def connect(self, websocket: WebSocket, campaign_id: str, client_id: str):
        await websocket.accept()
        if campaign_id not in self.active_connections:
            self.active_connections[campaign_id] = []
        self.active_connections[campaign_id].append(websocket)
        websocket_connections[client_id] = websocket

    def disconnect(self, campaign_id: str, websocket: WebSocket, client_id: str):
        if campaign_id in self.active_connections:
            if websocket in self.active_connections[campaign_id]:
                self.active_connections[campaign_id].remove(websocket)
        if client_id in websocket_connections:
            del websocket_connections[client_id]

    async def broadcast_to_campaign(self, campaign_id: str, message: dict):
        if campaign_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[campaign_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[campaign_id].remove(conn)

    async def send_to_client(self, client_id: str, message: dict):
        if client_id in websocket_connections:
            try:
                await websocket_connections[client_id].send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Utility functions
def generate_contact_id() -> str:
    """Generate unique contact ID"""
    return f"contact_{uuid.uuid4().hex[:8]}"

def generate_list_id() -> str:
    """Generate unique list ID"""
    return f"list_{uuid.uuid4().hex[:8]}"

def generate_template_id() -> str:
    """Generate unique template ID"""
    return f"template_{uuid.uuid4().hex[:8]}"

def generate_campaign_id() -> str:
    """Generate unique campaign ID"""
    return f"campaign_{uuid.uuid4().hex[:8]}"

def generate_email_id() -> str:
    """Generate unique email ID"""
    return f"email_{uuid.uuid4().hex[:8]}"

def generate_automation_id() -> str:
    """Generate unique automation ID"""
    return f"automation_{uuid.uuid4().hex[:8]}"

def generate_tracking_id() -> str:
    """Generate unique tracking ID"""
    return uuid.uuid4().hex

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def personalize_content(content: str, contact: Contact) -> str:
    """Personalize email content with contact data"""
    replacements = {
        'first_name': contact.first_name or 'there',
        'last_name': contact.last_name or '',
        'email': contact.email,
        'company': contact.company or '',
        'job_title': contact.job_title or '',
        'location': contact.location or ''
    }
    
    for key, value in replacements.items():
        content = content.replace(f'{{{{{key}}}}}', str(value))
    
    # Handle custom fields
    for key, value in contact.custom_fields.items():
        content = content.replace(f'{{{{{key}}}}}', str(value))
    
    return content

def calculate_campaign_stats(campaign_id: str) -> Dict[str, float]:
    """Calculate campaign statistics"""
    if campaign_id not in campaigns:
        return {}
    
    campaign = campaigns[campaign_id]
    
    if campaign.total_recipients == 0:
        return {
            "open_rate": 0.0,
            "click_rate": 0.0,
            "bounce_rate": 0.0,
            "unsubscribe_rate": 0.0
        }
    
    open_rate = (campaign.opened_count / campaign.total_recipients) * 100
    click_rate = (campaign.clicked_count / campaign.total_recipients) * 100
    bounce_rate = (campaign.bounced_count / campaign.total_recipients) * 100
    unsubscribe_rate = (campaign.unsubscribed_count / campaign.total_recipients) * 100
    
    return {
        "open_rate": round(open_rate, 2),
        "click_rate": round(click_rate, 2),
        "bounce_rate": round(bounce_rate, 2),
        "unsubscribe_rate": round(unsubscribe_rate, 2)
    }

async def send_email(email: Email) -> bool:
    """Send email (mock implementation)"""
    try:
        # Simulate email sending delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simulate delivery success/failure
        success_rate = 0.95  # 95% success rate
        
        if random.random() < success_rate:
            email.status = EmailStatus.SENT
            email.sent_time = datetime.now()
            
            # Simulate delivery
            await asyncio.sleep(random.uniform(0.5, 2.0))
            email.status = EmailStatus.DELIVERED
            email.delivered_time = datetime.now()
            
            return True
        else:
            email.status = EmailStatus.FAILED
            email.error_message = "SMTP connection failed"
            return False
            
    except Exception as e:
        email.status = EmailStatus.FAILED
        email.error_message = str(e)
        return False

async def process_campaign(campaign_id: str):
    """Process email campaign sending"""
    if campaign_id not in campaigns:
        return
    
    campaign = campaigns[campaign_id]
    
    if campaign.status != CampaignStatus.SCHEDULED:
        return
    
    campaign.status = CampaignStatus.SENDING
    campaign.sent_time = datetime.now()
    campaign.updated_at = datetime.now()
    
    # Get all contacts from campaign lists
    all_contact_ids = set()
    for list_id in campaign.list_ids:
        if list_id in list_contacts:
            all_contact_ids.update(list_contacts[list_id])
    
    campaign.total_recipients = len(all_contact_ids)
    
    # Get template
    if campaign.template_id not in email_templates:
        campaign.status = CampaignStatus.FAILED
        return
    
    template = email_templates[campaign.template_id]
    
    # Send emails
    sent_count = 0
    for contact_id in all_contact_ids:
        if contact_id not in contacts:
            continue
        
        contact = contacts[contact_id]
        
        # Create email
        email_id = generate_email_id()
        tracking_pixel_id = generate_tracking_id()
        unsubscribe_link_id = generate_tracking_id()
        
        # Personalize content
        personalized_html = personalize_content(template.html_content, contact)
        personalized_text = personalize_content(template.text_content or "", contact)
        
        email = Email(
            id=email_id,
            campaign_id=campaign_id,
            contact_id=contact_id,
            to_email=contact.email,
            from_email=campaign.from_email,
            subject=personalize_content(campaign.subject, contact),
            html_content=personalized_html,
            text_content=personalized_text,
            status=EmailStatus.PENDING,
            tracking_pixel_id=tracking_pixel_id,
            unsubscribe_link_id=unsubscribe_link_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        emails[email_id] = email
        
        # Send email
        success = await send_email(email)
        
        if success:
            sent_count += 1
            campaign.sent_count = sent_count
            
            # Update contact stats
            contact.email_stats["emails_sent"] += 1
            contact.last_updated = datetime.now()
        
        # Broadcast progress
        progress = (sent_count / campaign.total_recipients) * 100
        await manager.broadcast_to_campaign(campaign_id, {
            "type": "campaign_progress",
            "campaign_id": campaign_id,
            "sent_count": sent_count,
            "total_recipients": campaign.total_recipients,
            "progress": round(progress, 2),
            "timestamp": datetime.now().isoformat()
        })
        
        # Rate limiting
        await asyncio.sleep(0.1)  # 10 emails per second
    
    # Update campaign status
    campaign.status = CampaignStatus.SENT
    campaign.completed_time = datetime.now()
    campaign.updated_at = datetime.now()
    
    # Broadcast completion
    await manager.broadcast_to_campaign(campaign_id, {
        "type": "campaign_completed",
        "campaign_id": campaign_id,
        "final_stats": calculate_campaign_stats(campaign_id),
        "timestamp": datetime.now().isoformat()
    })

async def simulate_email_interactions():
    """Simulate email opens, clicks, bounces, etc."""
    while True:
        await asyncio.sleep(60)  # Check every minute
        
        for email in emails.values():
            if email.status == EmailStatus.DELIVERED and not email.opened_time:
                # Simulate email open (30% chance)
                if random.random() < 0.3:
                    email.status = EmailStatus.OPENED
                    email.opened_time = datetime.now()
                    
                    # Update campaign stats
                    if email.campaign_id and email.campaign_id in campaigns:
                        campaigns[email.campaign_id].opened_count += 1
                        campaigns[email.campaign_id].updated_at = datetime.now()
                    
                    # Update contact stats
                    if email.contact_id in contacts:
                        contacts[email.contact_id].email_stats["emails_opened"] += 1
                        contacts[email.contact_id].email_stats["last_opened"] = datetime.now()
                        contacts[email.contact_id].last_updated = datetime.now()
            
            elif email.status == EmailStatus.OPENED and not email.clicked_time:
                # Simulate email click (20% chance of opened emails)
                if random.random() < 0.2:
                    email.status = EmailStatus.CLICKED
                    email.clicked_time = datetime.now()
                    
                    # Update campaign stats
                    if email.campaign_id and email.campaign_id in campaigns:
                        campaigns[email.campaign_id].clicked_count += 1
                        campaigns[email.campaign_id].updated_at = datetime.now()
                    
                    # Update contact stats
                    if email.contact_id in contacts:
                        contacts[email.contact_id].email_stats["emails_clicked"] += 1
                        contacts[email.contact_id].email_stats["last_clicked"] = datetime.now()
                        contacts[email.contact_id].last_updated = datetime.now()
            
            elif email.status == EmailStatus.SENT and not email.bounced_time:
                # Simulate bounce (2% chance)
                if random.random() < 0.02:
                    email.status = EmailStatus.BOUNCED
                    email.bounced_time = datetime.now()
                    
                    # Update campaign stats
                    if email.campaign_id and email.campaign_id in campaigns:
                        campaigns[email.campaign_id].bounced_count += 1
                        campaigns[email.campaign_id].updated_at = datetime.now()

# Background task for scheduled campaigns
async def campaign_scheduler():
    """Background task to check and start scheduled campaigns"""
    while True:
        current_time = datetime.now()
        
        for campaign in campaigns.values():
            if (campaign.status == CampaignStatus.SCHEDULED and 
                campaign.scheduled_time and 
                campaign.scheduled_time <= current_time):
                
                # Start campaign processing
                asyncio.create_task(process_campaign(campaign.id))
        
        await asyncio.sleep(60)  # Check every minute

# Start background tasks
asyncio.create_task(campaign_scheduler())
asyncio.create_task(simulate_email_interactions())

# Initialize sample data
def initialize_sample_data():
    """Initialize sample data for testing"""
    # Sample SMTP config
    smtp_config = SMTPConfig(
        id="smtp_default",
        name="Default SMTP",
        host="smtp.example.com",
        port=587,
        username="user@example.com",
        password="password",
        use_tls=True,
        from_email="marketing@example.com",
        from_name="Marketing Team",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    smtp_configs["smtp_default"] = smtp_config
    
    # Sample contacts
    sample_contacts = [
        {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "Tech Corp",
            "job_title": "Software Engineer",
            "location": "New York, USA"
        },
        {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "Design Studio",
            "job_title": "UX Designer",
            "location": "San Francisco, USA"
        },
        {
            "email": "mike.wilson@example.com",
            "first_name": "Mike",
            "last_name": "Wilson",
            "company": "Marketing Agency",
            "job_title": "Marketing Manager",
            "location": "London, UK"
        }
    ]
    
    for contact_data in sample_contacts:
        contact_id = generate_contact_id()
        contact = Contact(
            id=contact_id,
            **contact_data,
            date_added=datetime.now(),
            last_updated=datetime.now()
        )
        contacts[contact_id] = contact
    
    # Sample email list
    list_id = generate_list_id()
    email_list = EmailList(
        id=list_id,
        name="Newsletter Subscribers",
        description="Main newsletter subscriber list",
        list_type=ListType.STATIC,
        contact_count=len(contacts),
        tags=["newsletter", "marketing"],
        created_by="admin",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    email_lists[list_id] = email_list
    list_contacts[list_id] = list(contacts.keys())
    
    # Sample template
    template_id = generate_template_id()
    template = EmailTemplate(
        id=template_id,
        name="Weekly Newsletter",
        subject="Your Weekly Newsletter - {{first_name}}",
        html_content="""
        <html>
        <body>
            <h1>Hello {{first_name}}!</h1>
            <p>Here's your weekly newsletter with the latest updates.</p>
            <p>Best regards,<br>The Marketing Team</p>
            <img src="https://example.com/track/{{tracking_pixel_id}}" width="1" height="1">
        </body>
        </html>
        """,
        text_content="Hello {{first_name}}! Here's your weekly newsletter.",
        template_type="marketing",
        category="newsletter",
        variables=["first_name", "tracking_pixel_id"],
        created_by="admin",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    email_templates[template_id] = template

# Initialize sample data
initialize_sample_data()

# API Endpoints
@app.post("/api/contacts", response_model=Contact)
async def create_contact(
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    job_title: Optional[str] = None,
    location: Optional[str] = None,
    tags: Optional[List[str]] = None,
    custom_fields: Optional[Dict[str, Any]] = None
):
    """Create a new contact"""
    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if contact already exists
    for contact in contacts.values():
        if contact.email == email:
            raise HTTPException(status_code=400, detail="Contact with this email already exists")
    
    contact_id = generate_contact_id()
    
    contact = Contact(
        id=contact_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        company=company,
        job_title=job_title,
        location=location,
        tags=tags or [],
        custom_fields=custom_fields or {},
        date_added=datetime.now(),
        last_updated=datetime.now()
    )
    
    contacts[contact_id] = contact
    return contact

@app.get("/api/contacts", response_model=List[Contact])
async def get_contacts(
    email: Optional[str] = None,
    company: Optional[str] = None,
    tags: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
    limit: int = 50
):
    """Get contacts with optional filters"""
    filtered_contacts = list(contacts.values())
    
    if email:
        filtered_contacts = [c for c in filtered_contacts if email.lower() in c.email.lower()]
    
    if company:
        filtered_contacts = [c for c in filtered_contacts if c.company and company.lower() in c.company.lower()]
    
    if tags:
        filtered_contacts = [c for c in filtered_contacts if any(tag in c.tags for tag in tags)]
    
    if is_active is not None:
        filtered_contacts = [c for c in filtered_contacts if c.is_active == is_active]
    
    return filtered_contacts[:limit]

@app.get("/api/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: str):
    """Get specific contact"""
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contacts[contact_id]

@app.put("/api/contacts/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    job_title: Optional[str] = None,
    location: Optional[str] = None,
    tags: Optional[List[str]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    is_active: Optional[bool] = None
):
    """Update contact"""
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact = contacts[contact_id]
    
    if first_name is not None:
        contact.first_name = first_name
    if last_name is not None:
        contact.last_name = last_name
    if phone is not None:
        contact.phone = phone
    if company is not None:
        contact.company = company
    if job_title is not None:
        contact.job_title = job_title
    if location is not None:
        contact.location = location
    if tags is not None:
        contact.tags = tags
    if custom_fields is not None:
        contact.custom_fields = custom_fields
    if is_active is not None:
        contact.is_active = is_active
    
    contact.last_updated = datetime.now()
    return contact

@app.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: str):
    """Delete contact"""
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Remove from all lists
    for list_id, contact_ids in list_contacts.items():
        if contact_id in contact_ids:
            contact_ids.remove(contact_id)
    
    del contacts[contact_id]
    return {"message": "Contact deleted successfully"}

@app.post("/api/lists", response_model=EmailList)
async def create_email_list(
    name: str,
    description: str,
    list_type: ListType,
    tags: Optional[List[str]] = None,
    created_by: str = "admin"
):
    """Create a new email list"""
    list_id = generate_list_id()
    
    email_list = EmailList(
        id=list_id,
        name=name,
        description=description,
        list_type=list_type,
        contact_count=0,
        tags=tags or [],
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    email_lists[list_id] = email_list
    list_contacts[list_id] = []
    
    return email_list

@app.get("/api/lists", response_model=List[EmailList])
async def get_email_lists(
    list_type: Optional[ListType] = None,
    created_by: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50
):
    """Get email lists"""
    filtered_lists = list(email_lists.values())
    
    if list_type:
        filtered_lists = [l for l in filtered_lists if l.list_type == list_type]
    
    if created_by:
        filtered_lists = [l for l in filtered_lists if l.created_by == created_by]
    
    if is_active is not None:
        filtered_lists = [l for l in filtered_lists if l.is_active == is_active]
    
    return filtered_lists[:limit]

@app.post("/api/lists/{list_id}/contacts/{contact_id}")
async def add_contact_to_list(list_id: str, contact_id: str):
    """Add contact to email list"""
    if list_id not in email_lists:
        raise HTTPException(status_code=404, detail="Email list not found")
    
    if contact_id not in contacts:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if contact_id not in list_contacts[list_id]:
        list_contacts[list_id].append(contact_id)
        email_lists[list_id].contact_count = len(list_contacts[list_id])
        email_lists[list_id].updated_at = datetime.now()
    
    return {"message": "Contact added to list successfully"}

@app.delete("/api/lists/{list_id}/contacts/{contact_id}")
async def remove_contact_from_list(list_id: str, contact_id: str):
    """Remove contact from email list"""
    if list_id not in email_lists:
        raise HTTPException(status_code=404, detail="Email list not found")
    
    if contact_id in list_contacts[list_id]:
        list_contacts[list_id].remove(contact_id)
        email_lists[list_id].contact_count = len(list_contacts[list_id])
        email_lists[list_id].updated_at = datetime.now()
    
    return {"message": "Contact removed from list successfully"}

@app.post("/api/templates", response_model=EmailTemplate)
async def create_email_template(
    name: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    template_type: str = "marketing",
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    created_by: str = "admin"
):
    """Create email template"""
    template_id = generate_template_id()
    
    # Extract variables from content
    variables = re.findall(r'\{\{(\w+)\}\}', html_content + (text_content or ""))
    variables = list(set(variables))
    
    template = EmailTemplate(
        id=template_id,
        name=name,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        template_type=template_type,
        category=category,
        tags=tags or [],
        variables=variables,
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    email_templates[template_id] = template
    return template

@app.get("/api/templates", response_model=List[EmailTemplate])
async def get_email_templates(
    template_type: Optional[str] = None,
    category: Optional[str] = None,
    created_by: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50
):
    """Get email templates"""
    filtered_templates = list(email_templates.values())
    
    if template_type:
        filtered_templates = [t for t in filtered_templates if t.template_type == template_type]
    
    if category:
        filtered_templates = [t for t in filtered_templates if t.category == category]
    
    if created_by:
        filtered_templates = [t for t in filtered_templates if t.created_by == created_by]
    
    if is_active is not None:
        filtered_templates = [t for t in filtered_templates if t.is_active == is_active]
    
    return filtered_templates[:limit]

@app.post("/api/campaigns", response_model=Campaign)
async def create_campaign(
    name: str,
    subject: str,
    from_email: str,
    from_name: str,
    template_id: str,
    list_ids: List[str],
    reply_to: Optional[str] = None,
    scheduled_time: Optional[datetime] = None,
    settings: Optional[Dict[str, Any]] = None,
    created_by: str = "admin"
):
    """Create email campaign"""
    if not validate_email(from_email):
        raise HTTPException(status_code=400, detail="Invalid from email format")
    
    if template_id not in email_templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate lists
    for list_id in list_ids:
        if list_id not in email_lists:
            raise HTTPException(status_code=404, detail=f"Email list {list_id} not found")
    
    campaign_id = generate_campaign_id()
    
    campaign = Campaign(
        id=campaign_id,
        name=name,
        subject=subject,
        from_email=from_email,
        from_name=from_name,
        reply_to=reply_to,
        template_id=template_id,
        list_ids=list_ids,
        status=CampaignStatus.DRAFT,
        scheduled_time=scheduled_time,
        settings=settings or {
            "track_opens": True,
            "track_clicks": True,
            "unsubscribe_link": True,
            "suppress_duplicates": True
        },
        created_by=created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    campaigns[campaign_id] = campaign
    email_analytics[campaign_id] = []
    
    return campaign

@app.get("/api/campaigns", response_model=List[Campaign])
async def get_campaigns(
    status: Optional[CampaignStatus] = None,
    created_by: Optional[str] = None,
    limit: int = 50
):
    """Get email campaigns"""
    filtered_campaigns = list(campaigns.values())
    
    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c.status == status]
    
    if created_by:
        filtered_campaigns = [c for c in filtered_campaigns if c.created_by == created_by]
    
    return sorted(filtered_campaigns, key=lambda x: x.created_at, reverse=True)[:limit]

@app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str):
    """Get specific campaign"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns[campaign_id]
    
    # Update statistics
    stats = calculate_campaign_stats(campaign_id)
    campaign.open_rate = stats["open_rate"]
    campaign.click_rate = stats["click_rate"]
    campaign.bounce_rate = stats["bounce_rate"]
    campaign.unsubscribe_rate = stats["unsubscribe_rate"]
    
    return campaign

@app.post("/api/campaigns/{campaign_id}/schedule")
async def schedule_campaign(campaign_id: str, scheduled_time: datetime):
    """Schedule campaign for sending"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns[campaign_id]
    
    if campaign.status != CampaignStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft campaigns can be scheduled")
    
    if scheduled_time <= datetime.now():
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
    
    campaign.status = CampaignStatus.SCHEDULED
    campaign.scheduled_time = scheduled_time
    campaign.updated_at = datetime.now()
    
    return {"message": f"Campaign scheduled for {scheduled_time}"}

@app.post("/api/campaigns/{campaign_id}/send")
async def send_campaign_now(campaign_id: str):
    """Send campaign immediately"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns[campaign_id]
    
    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
        raise HTTPException(status_code=400, detail="Campaign cannot be sent in current status")
    
    # Start campaign processing
    asyncio.create_task(process_campaign(campaign_id))
    
    return {"message": "Campaign sending started"}

@app.get("/api/campaigns/{campaign_id}/analytics", response_model=List[EmailAnalytics])
async def get_campaign_analytics(campaign_id: str, days: int = 30):
    """Get campaign analytics"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    since_date = datetime.now() - timedelta(days=days)
    
    analytics = email_analytics.get(campaign_id, [])
    filtered_analytics = [a for a in analytics if a.date >= since_date]
    
    return sorted(filtered_analytics, key=lambda x: x.date, reverse=True)

@app.get("/api/campaigns/{campaign_id}/emails", response_model=List[Email])
async def get_campaign_emails(
    campaign_id: str,
    status: Optional[EmailStatus] = None,
    limit: int = 100
):
    """Get emails sent in a campaign"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign_emails = [e for e in emails.values() if e.campaign_id == campaign_id]
    
    if status:
        campaign_emails = [e for e in campaign_emails if e.status == status]
    
    return sorted(campaign_emails, key=lambda x: x.created_at, reverse=True)[:limit]

@app.get("/api/stats")
async def get_email_marketing_stats():
    """Get email marketing platform statistics"""
    total_contacts = len(contacts)
    total_lists = len(email_lists)
    total_templates = len(email_templates)
    total_campaigns = len(campaigns)
    total_emails = len(emails)
    
    # Contact status distribution
    active_contacts = len([c for c in contacts.values() if c.is_active])
    
    # Campaign status distribution
    status_distribution = {}
    for campaign in campaigns.values():
        status = campaign.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Email status distribution
    email_status_distribution = {}
    for email in emails.values():
        status = email.status.value
        email_status_distribution[status] = email_status_distribution.get(status, 0) + 1
    
    # Overall performance metrics
    total_sent = len([e for e in emails.values() if e.status == EmailStatus.SENT])
    total_delivered = len([e for e in emails.values() if e.status == EmailStatus.DELIVERED])
    total_opened = len([e for e in emails.values() if e.status == EmailStatus.OPENED])
    total_clicked = len([e for e in emails.values() if e.status == EmailStatus.CLICKED])
    
    overall_open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    overall_click_rate = (total_clicked / total_delivered * 100) if total_delivered > 0 else 0
    
    return {
        "total_contacts": total_contacts,
        "active_contacts": active_contacts,
        "total_lists": total_lists,
        "total_templates": total_templates,
        "total_campaigns": total_campaigns,
        "total_emails": total_emails,
        "total_sent": total_sent,
        "total_delivered": total_delivered,
        "total_opened": total_opened,
        "total_clicked": total_clicked,
        "overall_open_rate": round(overall_open_rate, 2),
        "overall_click_rate": round(overall_click_rate, 2),
        "status_distribution": status_distribution,
        "email_status_distribution": email_status_distribution,
        "supported_campaign_statuses": [s.value for s in CampaignStatus],
        "supported_email_statuses": [s.value for s in EmailStatus]
    }

# WebSocket endpoint for campaign monitoring
@app.websocket("/ws/{campaign_id}")
async def websocket_endpoint(websocket: WebSocket, campaign_id: str):
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, campaign_id, client_id)
    
    try:
        # Send current campaign status
        if campaign_id in campaigns:
            campaign = campaigns[campaign_id]
            await manager.send_to_client(client_id, {
                "type": "campaign_status",
                "campaign": campaign.dict(),
                "timestamp": datetime.now().isoformat()
            })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages
            if message.get("type") == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(campaign_id, websocket, client_id)

@app.get("/")
async def root():
    return {"message": "Email Marketing API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
