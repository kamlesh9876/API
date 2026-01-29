# SMS Gateway API

A comprehensive SMS gateway service for text messaging, OTP verification, and SMS campaigns. Built with FastAPI, this service provides advanced SMS capabilities including multiple provider support, template management, real-time tracking, and analytics.

## 🚀 Features

### SMS Messaging
- **Single & Bulk SMS**: Send messages to individuals or large groups
- **Multiple Providers**: Support for Twilio, AWS SNS, Plivo, Nexmo, Clickatell
- **Message Types**: Text, Unicode, Binary, Flash messages
- **Scheduling**: Schedule SMS for future delivery
- **Priority Levels**: Set message priority for optimal delivery
- **Custom Callbacks**: Webhook support for delivery notifications

### OTP Verification
- **Secure OTP Generation**: Generate numeric or alphanumeric codes
- **Flexible Configuration**: Customizable length and expiry time
- **Multiple Attempts**: Configurable retry limits
- **Session Management**: Track OTP sessions and verification status
- **Resend Functionality**: Resend OTP codes when needed

### Template Management
- **Dynamic Templates**: Create reusable SMS templates
- **Variable Substitution**: Personalize messages with recipient data
- **Template Categories**: Organize templates by category
- **Usage Tracking**: Monitor template usage statistics
- **Version Control**: Track template changes

### Advanced Features
- **Phone Validation**: Validate phone number formats
- **International Support**: Support for international phone numbers
- **Message Segmentation**: Handle long messages automatically
- **Cost Tracking**: Monitor SMS costs per message
- **Delivery Analytics**: Comprehensive delivery statistics
- **Rate Limiting**: Control SMS sending rates

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Async Support**: Full async/await implementation
- **Data Validation**: Pydantic models with phone validation
- **Background Tasks**: Asyncio for scheduled sending
- **Enum Types**: Type-safe status and provider management

## 📋 API Endpoints

### SMS Sending

#### Send SMS
```http
POST /api/sms/send
Content-Type: application/json

{
  "to": [
    {
      "number": "+1234567890",
      "country_code": "US",
      "name": "John Doe"
    }
  ],
  "from_number": "+0987654321",
  "message": "Hello! This is a test message.",
  "message_type": "text",
  "sms_type": "transactional",
  "provider": "twilio",
  "schedule_at": "2024-01-15T10:00:00Z",
  "expire_at": "2024-01-15T12:00:00Z",
  "priority": 1,
  "callback_url": "https://yourapp.com/webhook/sms",
  "custom_id": "msg_12345",
  "metadata": {"campaign": "welcome"}
}
```

#### Send Bulk SMS
```http
POST /api/sms/send-batch
Content-Type: application/json

{
  "name": "Marketing Campaign",
  "recipients": [
    {"number": "+1234567890", "name": "User 1"},
    {"number": "+1234567891", "name": "User 2"}
  ],
  "message": "Special offer! Get 50% off today.",
  "template_id": "promo_template",
  "template_variables": {"discount": "50%"},
  "sms_type": "promotional",
  "schedule_at": "2024-01-15T09:00:00Z",
  "send_immediately": false,
  "callback_url": "https://yourapp.com/webhook/sms"
}
```

### OTP Management

#### Generate OTP
```http
POST /api/otp/generate
Content-Type: application/json

{
  "phone_number": {
    "number": "+1234567890",
    "name": "John Doe"
  },
  "length": 6,
  "expiry_minutes": 5,
  "alphanumeric": false,
  "custom_message": "Your verification code is: {otp}. Valid for {expiry} minutes.",
  "template_id": "otp_template",
  "metadata": {"purpose": "login"}
}
```

#### Verify OTP
```http
POST /api/otp/verify
Content-Type: application/json

{
  "phone_number": {
    "number": "+1234567890"
  },
  "otp_code": "123456",
  "session_id": "session_12345"
}
```

#### Resend OTP
```http
POST /api/otp/resend/{session_id}
```

### Template Management

#### Create Template
```http
POST /api/templates
Content-Type: application/json

{
  "name": "Welcome Template",
  "content": "Welcome {{name}}! Your account has been created. Use code {{code}} to verify.",
  "variables": ["name", "code"],
  "category": "onboarding",
  "sms_type": "transactional",
  "is_active": true
}
```

#### List Templates
```http
GET /api/templates?category=onboarding&sms_type=transactional&is_active=true&limit=50&offset=0
```

### SMS Tracking

#### List SMS Messages
```http
GET /api/sms?status=delivered&sms_type=transactional&date_from=2024-01-01T00:00:00Z&limit=50&offset=0
```

#### Get SMS Details
```http
GET /api/sms/{sms_id}
```

#### Handle Webhook
```http
POST /api/sms/{sms_id}/webhook
Content-Type: application/json

{
  "status": "delivered",
  "timestamp": "2024-01-15T10:05:00Z",
  "provider": "twilio",
  "error_code": null
}
```

### Analytics

#### Get SMS Statistics
```http
GET /api/analytics/stats?date_from=2024-01-01T00:00:00Z&date_to=2024-01-31T23:59:59Z
```

### Utilities

#### Validate Phone Number
```http
GET /api/phone/validate/{phone_number}
```

## 📊 Data Models

### SMSMessage
```python
class SMSMessage(BaseModel):
    to: List[PhoneNumber]
    from_number: Optional[str] = None
    message: str
    message_type: MessageType = MessageType.TEXT
    sms_type: SMSType = SMSType.TRANSACTIONAL
    provider: Optional[Provider] = None
    schedule_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None
    priority: Optional[int] = 1
    callback_url: Optional[str] = None
    custom_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
```

### OTPRequest
```python
class OTPRequest(BaseModel):
    phone_number: PhoneNumber
    length: int = 6
    expiry_minutes: int = 5
    alphanumeric: bool = False
    custom_message: Optional[str] = None
    template_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
```

### SMSTemplate
```python
class SMSTemplate(BaseModel):
    id: Optional[str] = None
    name: str
    content: str
    variables: Optional[List[str]] = []
    category: Optional[str] = None
    sms_type: SMSType = SMSType.TRANSACTIONAL
    is_active: bool = True
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn pydantic[email]

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

DEFAULT_PROVIDER=twilio
DEFAULT_FROM_NUMBER=+1234567890
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Send a simple SMS
sms_data = {
    "to": [
        {
            "number": "+1234567890",
            "name": "John Doe"
        }
    ],
    "message": "Hello! This is a test message from our API.",
    "sms_type": "transactional",
    "provider": "twilio"
}

response = requests.post(
    "http://localhost:8000/api/sms/send",
    json=sms_data
)

if response.status_code == 200:
    result = response.json()
    print(f"SMS sent with batch ID: {result['batch_id']}")

# Generate OTP
otp_data = {
    "phone_number": {
        "number": "+1234567890",
        "name": "John Doe"
    },
    "length": 6,
    "expiry_minutes": 5
}

otp_response = requests.post(
    "http://localhost:8000/api/otp/generate",
    json=otp_data
)

print(f"OTP generated: {otp_response.json()}")

# Verify OTP
verify_data = {
    "phone_number": {
        "number": "+1234567890"
    },
    "otp_code": "123456"
}

verify_response = requests.post(
    "http://localhost:8000/api/otp/verify",
    json=verify_data
)

print(f"OTP verification: {verify_response.json()}")
```

### JavaScript Client
```javascript
// Send SMS using fetch
const smsData = {
    to: [
        {
            number: "+1234567890",
            name: "John Doe"
        }
    ],
    message: "Hello! This is a test message.",
    sms_type: "transactional",
    provider: "twilio"
};

fetch('http://localhost:8000/api/sms/send', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(smsData)
})
.then(response => response.json())
.then(data => {
    console.log('SMS sent:', data);
})
.catch(error => console.error('Error:', error));

// Generate OTP
const otpData = {
    phone_number: {
        number: "+1234567890",
        name: "John Doe"
    },
    length: 6,
    expiry_minutes: 5
};

fetch('http://localhost:8000/api/otp/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(otpData)
})
.then(response => response.json())
.then(data => {
    console.log('OTP generated:', data);
});
```

## 🔧 Configuration

### Environment Variables
```bash
# Provider Configuration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

PLIVO_AUTH_ID=your_plivo_id
PLIVO_AUTH_TOKEN=your_plivo_token

NEXMO_API_KEY=your_nexmo_key
NEXMO_API_SECRET=your_nexmo_secret

# API Configuration
DEFAULT_PROVIDER=twilio
DEFAULT_FROM_NUMBER=+1234567890
MAX_MESSAGE_LENGTH=1600
MAX_RECIPIENTS_PER_REQUEST=1000

# Rate Limiting
RATE_LIMIT_PER_SECOND=10
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# OTP Configuration
OTP_DEFAULT_LENGTH=6
OTP_DEFAULT_EXPIRY=300
OTP_MAX_ATTEMPTS=3
OTP_RESEND_COOLDOWN=60

# Webhook Configuration
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=5

# Database Configuration (for production)
DATABASE_URL=postgresql://user:password@localhost/smsdb
REDIS_URL=redis://localhost:6379

# Security
API_KEY_REQUIRED=false
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
WEBHOOK_SECRET=your-webhook-secret
```

### SMS Types
- **transactional**: Transactional messages (alerts, notifications)
- **promotional**: Marketing messages (offers, campaigns)
- **otp**: One-time passwords and verification codes
- **alert**: Critical alerts and emergency messages
- **marketing**: General marketing communications

### Message Types
- **text**: Standard text messages
- **unicode**: Unicode messages for special characters
- **binary**: Binary data messages
- **flash**: Flash messages that display immediately

### Providers
- **twilio**: Twilio SMS service
- **aws_sns**: AWS Simple Notification Service
- **plivo**: Plivo SMS service
- **nexmo**: Vonage/Nexmo SMS service
- **clickatell**: Clickatell SMS service

## 📈 Use Cases

### Authentication & Security
- **Two-Factor Authentication**: Secure login processes
- **Account Verification**: Verify user phone numbers
- **Password Reset**: Secure password recovery
- **Transaction Alerts**: Financial transaction notifications
- **Security Alerts**: Suspicious activity notifications

### Business Communications
- **Appointment Reminders**: Healthcare and service appointments
- **Order Updates**: E-commerce order status
- **Shipping Notifications**: Package delivery updates
- **Payment Confirmations**: Transaction confirmations
- **Customer Support**: Support ticket notifications

### Marketing & Engagement
- **Promotional Campaigns**: Special offers and discounts
- **Event Invitations**: Webinar and event invitations
- **Customer Surveys**: Feedback collection
- **Loyalty Programs**: Rewards and points notifications
- **Product Announcements**: New product launches

### Emergency Communications
- **System Alerts**: Critical system notifications
- **Weather Alerts**: Weather warnings and updates
- **Emergency Notifications**: Urgent communications
- **Service Outages**: Service disruption notifications

## 🛡️ Security Features

### SMS Security
- **Phone Validation**: Validate phone number formats
- **Rate Limiting**: Prevent SMS bombing and abuse
- **OTP Security**: Secure OTP generation and verification
- **Message Encryption**: Encrypt sensitive message content
- **Audit Logging**: Track all SMS activities

### API Security
- **API Key Authentication**: Optional API key protection
- **CORS Support**: Cross-origin request handling
- **Input Validation**: Comprehensive input validation
- **Rate Limiting**: API rate limiting
- **Webhook Security**: Secure webhook handling

## 📊 Monitoring

### SMS Metrics
- **Delivery Rate**: Percentage of messages delivered
- **Success Rate**: Percentage of successful sends
- **OTP Success Rate**: OTP verification success rate
- **Cost Analysis**: Cost per message and total spend
- **Provider Performance**: Compare provider reliability

### Performance Metrics
- **Send Rate**: Messages sent per second
- **Queue Size**: Number of messages in queue
- **Processing Time**: Average processing time
- **Error Rate**: Percentage of failed sends
- **API Response Time**: API performance metrics

## 🔗 Related APIs

- **Email Service API**: For email notifications
- **User Management API**: For managing user phone numbers
- **Analytics API**: For advanced analytics
- **Notification API**: For multi-channel notifications

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API. In production, integrate with actual SMS providers like:
- **Twilio**: For reliable SMS delivery
- **AWS SNS**: For AWS integration
- **Plivo**: For cost-effective SMS
- **Nexmo/Vonage**: For global SMS coverage
- **Clickatell**: For enterprise SMS solutions
