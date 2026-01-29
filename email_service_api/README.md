# Email Service API

A comprehensive email service API for transactional emails, newsletters, and email campaigns. Built with FastAPI, this service provides advanced email management capabilities including templates, campaigns, analytics, and real-time tracking.

## 🚀 Features

### Email Sending
- **Single Email**: Send individual emails with rich formatting
- **Bulk Email**: Send multiple emails efficiently in batches
- **Scheduled Sending**: Schedule emails for future delivery
- **Priority Levels**: Set email priority (low, normal, high)
- **Attachments**: Support for file attachments with inline images

### Template Management
- **Dynamic Templates**: Create reusable email templates
- **Variable Substitution**: Personalize emails with recipient data
- **Multiple Formats**: Support for HTML, text, and MJML templates
- **Template Categories**: Organize templates by category
- **Version Control**: Track template changes and usage

### Campaign Management
- **Email Campaigns**: Create and manage email campaigns
- **Campaign Scheduling**: Schedule campaigns for optimal delivery
- **Recipient Management**: Manage campaign recipients with personalization
- **Campaign Analytics**: Track campaign performance metrics
- **A/B Testing**: Support for campaign variations

### Tracking & Analytics
- **Open Tracking**: Track when emails are opened
- **Click Tracking**: Monitor link clicks in emails
- **Delivery Status**: Real-time delivery status updates
- **Bounce Handling**: Handle bounced emails automatically
- **Performance Metrics**: Comprehensive analytics dashboard

### Advanced Features
- **Webhooks**: Real-time event notifications
- **Rate Limiting**: Control email sending rates
- **Unsubscribe Management**: Handle unsubscribe requests
- **SPF/DKIM Support**: Email authentication
- **Multi-tenant**: Support for multiple senders

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Async Support**: Full async/await implementation
- **Data Validation**: Pydantic models with email validation
- **Background Tasks**: Asyncio for scheduled sending
- **Enum Types**: Type-safe status and type management

## 📋 API Endpoints

### Email Sending

#### Send Single Email
```http
POST /api/email/send
Content-Type: application/json

{
  "from_email": "sender@example.com",
  "from_name": "Sender Name",
  "to": [
    {
      "email": "recipient@example.com",
      "name": "Recipient Name",
      "variables": {"first_name": "John"}
    }
  ],
  "cc": [],
  "bcc": [],
  "subject": "Welcome to Our Service",
  "content": "<h1>Hello {{first_name}}</h1><p>Thank you for joining!</p>",
  "content_type": "html",
  "attachments": [
    {
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size": 1024000,
      "inline": false
    }
  ],
  "template_id": "welcome_template",
  "template_variables": {"first_name": "John"},
  "priority": "normal",
  "send_at": "2024-01-15T10:00:00Z",
  "track_opens": true,
  "track_clicks": true,
  "unsubscribe_url": "https://example.com/unsubscribe",
  "reply_to": "support@example.com",
  "headers": {"X-Custom-Header": "value"},
  "tags": ["welcome", "onboarding"]
}
```

#### Send Bulk Emails
```http
POST /api/email/send-bulk
Content-Type: application/json

[
  {
    "from_email": "sender@example.com",
    "to": [{"email": "user1@example.com"}],
    "subject": "Bulk Email 1",
    "content": "Content for email 1"
  },
  {
    "from_email": "sender@example.com",
    "to": [{"email": "user2@example.com"}],
    "subject": "Bulk Email 2",
    "content": "Content for email 2"
  }
]
```

### Template Management

#### Create Template
```http
POST /api/templates
Content-Type: application/json

{
  "name": "Welcome Template",
  "subject": "Welcome {{first_name}}!",
  "content": "<h1>Hello {{first_name}}</h1><p>Welcome to our service!</p>",
  "content_type": "html",
  "description": "Welcome email for new users",
  "variables": ["first_name", "last_name"],
  "category": "onboarding",
  "is_active": true
}
```

#### List Templates
```http
GET /api/templates?category=onboarding&is_active=true&limit=50&offset=0
```

#### Get Template
```http
GET /api/templates/{template_id}
```

#### Update Template
```http
PUT /api/templates/{template_id}
Content-Type: application/json

{
  "name": "Updated Welcome Template",
  "subject": "Welcome {{first_name}} {{last_name}}!",
  "content": "<h1>Hello {{first_name}} {{last_name}}</h1>",
  "content_type": "html"
}
```

#### Delete Template
```http
DELETE /api/templates/{template_id}
```

### Campaign Management

#### Create Campaign
```http
POST /api/campaigns
Content-Type: application/json

{
  "name": "Summer Sale Campaign",
  "subject": "Summer Sale - 50% Off!",
  "content": "<h1>Summer Sale</h1><p>Get 50% off on all items!</p>",
  "content_type": "html",
  "template_id": "sale_template",
  "recipients": [
    {
      "email": "customer1@example.com",
      "name": "Customer One",
      "variables": {"discount": "50%"}
    }
  ],
  "scheduled_at": "2024-06-01T09:00:00Z",
  "send_immediately": false,
  "track_opens": true,
  "track_clicks": true,
  "unsubscribe_url": "https://example.com/unsubscribe",
  "tags": ["sale", "summer"]
}
```

#### List Campaigns
```http
GET /api/campaigns?status=completed&limit=50&offset=0
```

#### Get Campaign
```http
GET /api/campaigns/{campaign_id}
```

### Email Tracking

#### List Emails
```http
GET /api/emails?status=delivered&limit=50&offset=0
```

#### Get Email Details
```http
GET /api/emails/{email_id}
```

#### Track Email Open
```http
POST /api/emails/{email_id}/track-open
```

#### Track Email Click
```http
POST /api/emails/{email_id}/track-click?url=https://example.com
```

### Analytics

#### Get Email Statistics
```http
GET /api/analytics/stats?date_from=2024-01-01T00:00:00Z&date_to=2024-01-31T23:59:59Z
```

## 📊 Data Models

### EmailRequest
```python
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
    priority: Optional[str] = "normal"
    send_at: Optional[datetime] = None
    track_opens: bool = True
    track_clicks: bool = True
    unsubscribe_url: Optional[str] = None
    reply_to: Optional[EmailStr] = None
    headers: Optional[Dict[str, str]] = {}
    tags: Optional[List[str]] = []
```

### EmailTemplate
```python
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
```

### EmailCampaign
```python
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
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart email-validator

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# API Configuration
API_BASE_URL=http://localhost:8000
DEFAULT_FROM_EMAIL=noreply@example.com
DEFAULT_FROM_NAME=Your App
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Send a simple email
email_data = {
    "from_email": "sender@example.com",
    "from_name": "Your App",
    "to": [
        {
            "email": "recipient@example.com",
            "name": "John Doe"
        }
    ],
    "subject": "Welcome to Our Service",
    "content": "<h1>Welcome!</h1><p>Thank you for joining our service.</p>",
    "content_type": "html"
}

response = requests.post(
    "http://localhost:8000/api/email/send",
    json=email_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Email queued with ID: {result['email_id']}")

# Create a template
template_data = {
    "name": "Welcome Template",
    "subject": "Welcome {{first_name}}!",
    "content": "<h1>Hello {{first_name}}</h1><p>Welcome to our service!</p>",
    "content_type": "html",
    "variables": ["first_name"],
    "category": "onboarding"
}

template_response = requests.post(
    "http://localhost:8000/api/templates",
    json=template_data
)

print(f"Template created: {template_response.json()}")

# Send email using template
email_with_template = {
    "from_email": "sender@example.com",
    "to": [{"email": "user@example.com", "name": "John"}],
    "template_id": template_response.json()["template_id"],
    "template_variables": {"first_name": "John"}
}

template_email_response = requests.post(
    "http://localhost:8000/api/email/send",
    json=email_with_template
)

print(f"Template email sent: {template_email_response.json()}")
```

### JavaScript Client
```javascript
// Send email using fetch
const emailData = {
    from_email: "sender@example.com",
    from_name: "Your App",
    to: [
        {
            email: "recipient@example.com",
            name: "John Doe"
        }
    ],
    subject: "Welcome to Our Service",
    content: "<h1>Welcome!</h1><p>Thank you for joining our service.</p>",
    content_type: "html"
};

fetch('http://localhost:8000/api/email/send', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(emailData)
})
.then(response => response.json())
.then(data => {
    console.log('Email sent:', data);
})
.catch(error => console.error('Error:', error));

// Create campaign
const campaignData = {
    name: "Newsletter Campaign",
    subject: "This Week's Newsletter",
    content: "<h1>Newsletter</h1><p>Latest updates...</p>",
    recipients: [
        {email: "subscriber1@example.com"},
        {email: "subscriber2@example.com"}
    ],
    send_immediately: true,
    track_opens: true,
    track_clicks: true
};

fetch('http://localhost:8000/api/campaigns', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(campaignData)
})
.then(response => response.json())
.then(data => {
    console.log('Campaign created:', data);
});
```

## 🔧 Configuration

### Environment Variables
```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false

# API Configuration
API_BASE_URL=http://localhost:8000
DEFAULT_FROM_EMAIL=noreply@example.com
DEFAULT_FROM_NAME=Your App
MAX_EMAIL_SIZE=25MB
MAX_ATTACHMENTS=10

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# Tracking Configuration
TRACKING_DOMAIN=track.yourdomain.com
OPEN_TRACKING_ENABLED=true
CLICK_TRACKING_ENABLED=true
UNSUBSCRIBE_TRACKING_ENABLED=true

# Database Configuration (for production)
DATABASE_URL=postgresql://user:password@localhost/emaildb
REDIS_URL=redis://localhost:6379

# Security
API_KEY_REQUIRED=false
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
WEBHOOK_SECRET=your-webhook-secret
```

### Email Types
- **transactional**: Transactional emails (passwords, receipts)
- **marketing**: Marketing emails (promotions, newsletters)
- **notification**: Notification emails (alerts, updates)
- **newsletter**: Newsletter emails (digests, updates)
- **alert**: Alert emails (urgent notifications)

### Email Status
- **pending**: Queued for sending
- **sent**: Sent to SMTP server
- **delivered**: Delivered to recipient
- **failed**: Failed to send
- **bounced**: Bounced back
- **opened**: Opened by recipient
- **clicked**: Link clicked

## 📈 Use Cases

### Transactional Emails
- **Welcome Emails**: Onboarding new users
- **Password Resets**: Secure password recovery
- **Order Confirmations**: E-commerce transactions
- **Shipping Notifications**: Order status updates
- **Account Alerts**: Security notifications

### Marketing Campaigns
- **Newsletters**: Regular content distribution
- **Promotional Emails**: Sales and special offers
- **Product Announcements**: New product launches
- **Event Invitations**: Webinar and event marketing
- **Customer Surveys**: Feedback collection

### Notification Systems
- **App Notifications**: In-app email notifications
- **System Alerts**: System status updates
- **User Mentions**: Social media notifications
- **Content Updates**: New content alerts
- **Reminder Emails**: Scheduled reminders

## 🛡️ Security Features

### Email Security
- **SPF/DKIM**: Email authentication support
- **TLS Encryption**: Secure email transmission
- **Rate Limiting**: Prevent abuse
- **Content Filtering**: Malicious content detection
- **Unsubscribe Compliance**: CAN-SPAM compliance

### API Security
- **API Key Authentication**: Optional API key protection
- **CORS Support**: Cross-origin request handling
- **Input Validation**: Comprehensive input validation
- **Rate Limiting**: API rate limiting
- **Audit Logging**: Activity tracking

## 📊 Monitoring

### Email Metrics
- **Delivery Rate**: Percentage of emails delivered
- **Open Rate**: Percentage of emails opened
- **Click Rate**: Percentage of clicks
- **Bounce Rate**: Percentage of bounced emails
- **Unsubscribe Rate**: Unsubscribe percentage

### Performance Metrics
- **Send Rate**: Emails sent per minute
- **Queue Size**: Number of emails in queue
- **Processing Time**: Average processing time
- **Error Rate**: Percentage of failed sends
- **API Response Time**: API performance metrics

## 🔗 Related APIs

- **User Management API**: For managing email recipients
- **Analytics API**: For advanced email analytics
- **Template Service API**: For advanced template management
- **Notification API**: For multi-channel notifications

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API. In production, integrate with actual email services like:
- **SendGrid**: For reliable email delivery
- **Mailgun**: For email API services
- **AWS SES**: For Amazon email services
- **Postmark**: For transactional emails
- **Mailchimp**: For marketing campaigns
