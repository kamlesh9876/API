# Email Marketing API

A comprehensive email marketing platform with contact management, campaign creation, automation, analytics, and real-time monitoring.

## Features

- **Contact Management**: Create, update, and manage email contacts with custom fields
- **Email Lists**: Organize contacts into static, dynamic, and segmented lists
- **Email Templates**: Create reusable email templates with personalization
- **Campaign Management**: Create, schedule, and send email campaignsvestment campaigns
.
- ** p**Real-time Analytics**: Track opens, clicks, bounces, and unsubscribe rates
- **Automation**: Set up automated email sequences based on triggers
- **WebSocket Support**: Real-time campaign monitoring and updates
- **SMTP Configuration**: Multiple SMTP providers and delivery optimization

## API Endpoints

### Contact Management

#### Create Contact
```http
POST /api/contacts
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Tech Corp",
  "job_title": "Software Engineer",
  "location": "New York, USA",
  "tags": ["developer", "newsletter"],
  "custom_fields": {
    "source": "website",
    "interests": "AI, ML"
  }
}
```

#### Get Contacts
```http
GET /api/contacts?company=Tech%20Corp&tags=developer&is_active=true&limit=50
```

#### Get Specific Contact
```http
GET /api/contacts/{contact_id}
```

#### Update Contact
```http
PUT /api/contacts/{contact_id}
Content-Type: application/json

{
  "first_name": "Johnathan",
  "company": "New Company",
  "tags": ["developer", "management"]
}
```

#### Delete Contact
```http
DELETE /api/contacts/{contact_id}
```

### Email Lists

#### Create Email List
```http
POST /api/lists
Content-Type: application/json

{
  "name": "Newsletter Subscribers",
  "description": "Main newsletter subscriber list",
  "list_type": "static",
  "tags": ["newsletter", "marketing"]
}
```

#### Get Email Lists
```http
GET /api/lists?list_type=static&created_by=admin&is_active=true&limit=50
```

#### Add Contact to List
```http
POST /api/lists/{list_id}/contacts/{contact_id}
```

#### Remove Contact from List
```http
DELETE /api/lists/{list_id}/contacts/{contact_id}
```

### Email Templates

#### Create Email Template
```http
POST /api/templates
Content-Type: application/json

{
  "name": "Weekly Newsletter",
  "subject": "Your Weekly Newsletter - {{first_name}}",
  "html_content": "<html><body><h1>Hello {{first_name}}!</h1></body></html>",
  "text_content": "Hello {{first_name}}!",
  "template_type": "marketing",
  "category": "newsletter",
  "tags": ["weekly", "newsletter"]
}
```

#### Get Email Templates
```http
GET /api/templates?template_type=marketing&category=newsletter&is_active=true&limit=50
```

### Campaign Management

#### Create Campaign
```http
POST /api/campaigns
Content-Type: application/json

{
  "name": "Summer Sale Campaign",
  "subject": "Summer Sale - {{first_name}}!",
  "from_email": "marketing@example.com",
  "from_name": "Marketing Team",
  "template_id": "template_123",
  "list_ids": ["list_123", "list_456"],
  "reply_to": "support@example.com",
  "settings": {
    "track_opens": true,
    "track_clicks": true,
    "unsubscribe_link": true,
    "suppress_duplicates": true
  }
}
```

#### Get Campaigns
```http
GET /api/campaigns?status=sent&created_by=admin&limit=50
```

#### Get Specific Campaign
```http
GET /api/campaigns/{campaign_id}
```

#### Schedule Campaign
```http
POST /api/campaigns/{campaign_id}/schedule
Content-Type: application/json

{
  "scheduled_time": "2024-01-15T10:00:00"
}
```

#### Send Campaign Now
```http
POST /api/campaigns/{campaign_id}/send
```

#### Get Campaign Analytics
```http
GET /api/campaigns/{campaign_id}/analytics?days=30
```

#### Get Campaign Emails
```http
GET /api/campaigns/{campaign_id}/emails?status=opened&limit=100
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Contact
```json
{
  "id": "contact_123",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "company": "Tech Corp",
  "job_title": "Software Engineer",
  "location": "New York, USA",
  "tags": ["developer", "newsletter"],
  "custom_fields": {
    "source": "website",
    "interests": "AI, ML"
  },
  "is_active": true,
  "date_added": "2024-01-01T10:00:00",
  "last_updated": "2024-01-01T10:00:00",
  "email_stats": {
    "emails_sent": 5,
    "emails_opened": 3,
    "emails_clicked": 1,
    "last_opened": "2024-01-01T12:00:00",
    "last_clicked": "2024-01-01T12:05:00"
  }
}
```

### Email List
```json
{
  "id": "list_123",
  "name": "Newsletter Subscribers",
  "description": "Main newsletter subscriber list",
  "list_type": "static",
  "contact_count": 1500,
  "tags": ["newsletter", "marketing"],
  "created_by": "admin",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "is_active": true
}
```

### Email Template
```json
{
  "id": "template_123",
  "name": "Weekly Newsletter",
  "subject": "Your Weekly Newsletter - {{first_name}}",
  "html_content": "<html><body><h1>Hello {{first_name}}!</h1></body></html>",
  "text_content": "Hello {{first_name}}!",
  "template_type": "marketing",
  "category": "newsletter",
  "tags": ["weekly", "newsletter"],
  "variables": ["first_name"],
  "is_active": true,
  "created_by": "admin",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### Campaign
```json
{
  "id": "campaign_123",
  "name": "Summer Sale Campaign",
  "subject": "Summer Sale - {{first_name}}!",
  "from_email": "marketing@example.com",
  "from_name": "Marketing Team",
  "reply_to": "support@example.com",
  "template_id": "template_123",
  "list_ids": ["list_123", "list_456"],
  "status": "sent",
  "scheduled_time": "2024-01-15T10:00:00",
  "sent_time": "2024-01-15T10:00:00",
  "completed_time": "2024-01-15T10:30:00",
  "total_recipients": 2000,
  "sent_count": 2000,
  "delivered_count": 1950,
  "opened_count": 780,
  "clicked_count": 156,
  "bounced_count": 50,
  "unsubscribed_count": 10,
  "complained_count": 2,
  "open_rate": 40.0,
  "click_rate": 8.0,
  "bounce_rate": 2.5,
  "unsubscribe_rate": 0.5,
  "settings": {
    "track_opens": true,
    "track_clicks": true,
    "unsubscribe_link": true,
    "suppress_duplicates": true
  },
  "created_by": "admin",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Email
```json
{
  "id": "email_123",
  "campaign_id": "campaign_123",
  "contact_id": "contact_123",
  "to_email": "john.doe@example.com",
  "from_email": "marketing@example.com",
  "subject": "Summer Sale - John!",
  "html_content": "<html><body><h1>Hello John!</h1></body></html>",
  "text_content": "Hello John!",
  "status": "opened",
  "sent_time": "2024-01-15T10:05:00",
  "delivered_time": "2024-01-15T10:05:30",
  "opened_time": "2024-01-15T12:30:00",
  "clicked_time": null,
  "bounced_time": null,
  "unsubscribed_time": null,
  "error_message": null,
  "tracking_pixel_id": "track_123",
  "unsubscribe_link_id": "unsub_123",
  "created_at": "2024-01-15T10:05:00",
  "updated_at": "2024-01-15T12:30:00"
}
```

### Email Analytics
```json
{
  "id": "analytics_123",
  "campaign_id": "campaign_123",
  "date": "2024-01-15T00:00:00",
  "emails_sent": 2000,
  "emails_delivered": 1950,
  "emails_opened": 780,
  "emails_clicked": 156,
  "emails_bounced": 50,
  "emails_unsubscribed": 10,
  "open_rate": 40.0,
  "click_rate": 8.0,
  "bounce_rate": 2.5,
  "unsubscribe_rate": 0.5
}
```

## Campaign Statuses

### Draft
- **Description**: Campaign is being created and configured
- **Actions**: Edit, schedule, send, delete
- **Transitions**: Scheduled, Sending

### Scheduled
- **Description**: Campaign is scheduled for future sending
- **Actions**: Edit schedule, cancel, send now
- **Transitions**: Sending, Cancelled

### Sending
- **Description**: Campaign is currently being sent
- **Actions**: Pause, monitor
- **Transitions**: Sent, Paused, Failed

### Sent
- **Description**: Campaign has been successfully sent
- **Actions**: View analytics, duplicate
- **Transitions**: None (final state)

### Paused
- **Description**: Campaign sending has been paused
- **Actions**: Resume, cancel
- **Transitions**: Sending, Cancelled

### Cancelled
- **Description**: Campaign has been cancelled
- **Actions**: View logs, duplicate
- **Transitions**: None (final state)

### Failed
- **Description**: Campaign failed to send
- **Actions**: Retry, view errors
- **Transitions**: Draft, Sending

## Email Statuses

### Pending
- **Description**: Email is queued for sending
- **Next States**: Sent, Failed

### Sent
- **Description**: Email has been sent to SMTP server
- **Next States**: Delivered, Bounced

### Delivered
- **Description**: Email has been delivered to recipient's server
- **Next States**: Opened, Bounced

### Opened
- **Description**: Recipient has opened the email
- **Next States**: Clicked

### Clicked
- **Description**: Recipient has clicked a link in the email
- **Next States**: None (final engagement state)

### Bounced
- **Description**: Email delivery failed
- **Next States**: None (final state)

### Complained
- **Description**: Recipient marked as spam
- **Next States**: None (final state)

### Unsubscribed
- **Description**: Recipient unsubscribed
- **Next States**: None (final state)

### Failed
- **Description**: Email sending failed
- **Next States**: None (final state)

## List Types

### Static
- **Description**: Manually managed contact list
- **Use Cases**: Specific campaigns, manual segmentation
- **Management**: Add/remove contacts manually

### Dynamic
- **Description**: Automatically updated based on criteria
- **Use Cases**: Ongoing campaigns, real-time segmentation
- **Management**: Rules-based updates

### Segmented
- **Description**: Subsets of larger lists
- **Use Cases**: Targeted campaigns, A/B testing
- **Management**: Filter-based segmentation

## Template Variables

### Standard Variables
- `{{first_name}}`: Contact's first name
- `{{last_name}}`: Contact's last name
- `{{email}}`: Contact's email address
- `{{company}}`: Contact's company
- `{{job_title}}`: Contact's job title
- `{{location}}`: Contact's location

### Custom Variables
- `{{custom_field_name}}`: Any custom field from contact
- `{{tracking_pixel_id}}`: Email tracking pixel ID
- `{{unsubscribe_link_id}}`: Unsubscribe link ID

### Conditional Variables
```html
{% if first_name %}
  Hello {{first_name}}!
{% else %}
  Hello there!
{% endif %}
```

## WebSocket Events

### Campaign Progress
```javascript
{
  "type": "campaign_progress",
  "campaign_id": "campaign_123",
  "sent_count": 1500,
  "total_recipients": 2000,
  "progress": 75.0,
  "timestamp": "2024-01-15T10:20:00"
}
```

### Campaign Completion
```javascript
{
  "type": "campaign_completed",
  "campaign_id": "campaign_123",
  "final_stats": {
    "open_rate": 40.0,
    "click_rate": 8.0,
    "bounce_rate": 2.5,
    "unsubscribe_rate": 0.5
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Campaign Status
```javascript
{
  "type": "campaign_status",
  "campaign": {
    "id": "campaign_123",
    "name": "Summer Sale Campaign",
    "status": "sending",
    "progress": 45.0
  },
  "timestamp": "2024-01-15T10:15:00"
}
```

## Installation

```bash
pip install fastapi uvicorn websockets python-multipart
```

## Usage

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Example Usage

### Python Client
```python
import requests
import asyncio
import websockets
import json

# Create a contact
contact_data = {
    "email": "jane.smith@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "company": "Design Studio",
    "job_title": "UX Designer",
    "location": "San Francisco, USA",
    "tags": ["designer", "newsletter"],
    "custom_fields": {
        "source": "website",
        "interests": "UI/UX, Design"
    }
}

response = requests.post("http://localhost:8000/api/contacts", json=contact_data)
contact = response.json()
print(f"Created contact: {contact['id']}")

# Create email list
list_data = {
    "name": "Design Newsletter",
    "description": "Newsletter for design professionals",
    "list_type": "static",
    "tags": ["design", "newsletter"]
}

response = requests.post("http://localhost:8000/api/lists", json=list_data)
email_list = response.json()
print(f"Created email list: {email_list['id']}")

# Add contact to list
response = requests.post(f"http://localhost:8000/api/lists/{email_list['id']}/contacts/{contact['id']}")
print(f"Added contact to list")

# Create email template
template_data = {
    "name": "Design Tips Newsletter",
    "subject": "Weekly Design Tips - {{first_name}}",
    html_content = """
    <html>
    <body>
        <h1>Hello {{first_name}}!</h1>
        <p>Here are this week's design tips and inspiration.</p>
        <p>Best regards,<br>The Design Team</p>
        <img src="https://example.com/track/{{tracking_pixel_id}}" width="1" height="1">
    </body>
    </html>
    """,
    "text_content": "Hello {{first_name}}! Here are this week's design tips.",
    "template_type": "marketing",
    "category": "newsletter",
    "tags": ["design", "weekly"]
}

response = requests.post("http://localhost:8000/api/templates", json=template_data)
template = response.json()
print(f"Created template: {template['id']}")

# Create campaign
campaign_data = {
    "name": "Weekly Design Newsletter",
    "subject": "Weekly Design Tips - {{first_name}}",
    "from_email": "design@example.com",
    "from_name": "Design Team",
    "template_id": template['id'],
    "list_ids": [email_list['id']],
    "reply_to": "support@example.com",
    "settings": {
        "track_opens": True,
        "track_clicks": True,
        "unsubscribe_link": True,
        "suppress_duplicates": True
    }
}

response = requests.post("http://localhost:8000/api/campaigns", json=campaign_data)
campaign = response.json()
print(f"Created campaign: {campaign['id']}")

# Send campaign immediately
response = requests.post(f"http://localhost:8000/api/campaigns/{campaign['id']}/send")
print(f"Campaign sending started")

# WebSocket client for campaign monitoring
async def campaign_monitor():
    uri = f"ws://localhost:8000/ws/{campaign['id']}"
    async with websockets.connect(uri) as websocket:
        print(f"Monitoring campaign: {campaign['name']}")
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'campaign_progress':
                progress = data['progress']
                print(f"Progress: {progress}% ({data['sent_count']}/{data['total_recipients']})")
            elif data['type'] == 'campaign_completed':
                stats = data['final_stats']
                print(f"Campaign completed!")
                print(f"Open rate: {stats['open_rate']}%")
                print(f"Click rate: {stats['click_rate']}%")
                print(f"Bounce rate: {stats['bounce_rate']}%")
                break
            elif data['type'] == 'campaign_status':
                status = data['campaign']['status']
                print(f"Campaign status: {status}")

# Run campaign monitor
asyncio.run(campaign_monitor())

# Get campaign analytics
response = requests.get(f"http://localhost:8000/api/campaigns/{campaign['id']}/analytics?days=7")
analytics = response.json()

print(f"\nCampaign analytics for last 7 days:")
for day_data in analytics:
    date = day_data['date'].split('T')[0]
    print(f"  {date}: {day_data['emails_sent']} sent, {day_data['open_rate']}% open rate")

# Get platform statistics
response = requests.get("http://localhost:8000/api/stats")
stats = response.json()

print(f"\nPlatform statistics:")
print(f"  Total contacts: {stats['total_contacts']}")
print(f"  Active contacts: {stats['active_contacts']}")
print(f"  Total campaigns: {stats['total_campaigns']}")
print(f"  Overall open rate: {stats['overall_open_rate']}%")
print(f"  Overall click rate: {stats['overall_click_rate']}%")
```

### JavaScript Client
```javascript
// Email marketing client
class EmailMarketingClient {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }

  async createContact(contactData) {
    const response = await fetch(`${this.baseURL}/api/contacts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(contactData)
    });
    return response.json();
  }

  async createEmailList(listData) {
    const response = await fetch(`${this.baseURL}/api/lists`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(listData)
    });
    return response.json();
  }

  async createTemplate(templateData) {
    const response = await fetch(`${this.baseURL}/api/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateData)
    });
    return response.json();
  }

  async createCampaign(campaignData) {
    const response = await fetch(`${this.baseURL}/api/campaigns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(campaignData)
    });
    return response.json();
  }

  async sendCampaign(campaignId) {
    const response = await fetch(`${this.baseURL}/api/campaigns/${campaignId}/send`, {
      method: 'POST'
    });
    return response.json();
  }

  async getCampaignAnalytics(campaignId, days = 30) {
    const response = await fetch(`${this.baseURL}/api/campaigns/${campaignId}/analytics?days=${days}`);
    return response.json();
  }
}

// WebSocket campaign monitor
class CampaignMonitor {
  constructor(campaignId) {
    this.campaignId = campaignId;
    this.ws = new WebSocket(`ws://localhost:8000/ws/${campaignId}`);
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('Connected to campaign monitor');
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from campaign monitor');
      clearInterval(this.pingInterval);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'campaign_progress':
        this.updateProgress(message);
        break;
      case 'campaign_completed':
        this.showCompletion(message);
        break;
      case 'campaign_status':
        this.updateStatus(message);
        break;
      case 'pong':
        console.log('Connection healthy');
        break;
    }
  }

  startPingInterval() {
    this.pingInterval = setInterval(() => {
      this.ws.send(JSON.stringify({ type: 'ping' }));
    }, 30000);
  }

  updateProgress(data) {
    const progressBar = document.getElementById('campaign-progress');
    const progressText = document.getElementById('progress-text');
    const sentCount = document.getElementById('sent-count');
    const totalCount = document.getElementById('total-count');

    if (progressBar) {
      progressBar.style.width = `${data.progress}%`;
      progressText.textContent = `${data.progress.toFixed(1)}%`;
      sentCount.textContent = data.sent_count;
      totalCount.textContent = data.total_recipients;
    }

    console.log(`Campaign progress: ${data.progress.toFixed(1)}%`);
  }

  showCompletion(data) {
    const stats = data.final_stats;
    const completionMessage = document.getElementById('completion-message');
    
    if (completionMessage) {
      completionMessage.innerHTML = `
        <h3>Campaign Completed!</h3>
        <div class="stats">
          <div class="stat">
            <span class="label">Open Rate:</span>
            <span class="value">${stats.open_rate}%</span>
          </div>
          <div class="stat">
            <span class="label">Click Rate:</span>
            <span class="value">${stats.click_rate}%</span>
          </div>
          <div class="stat">
            <span class="label">Bounce Rate:</span>
            <span class="value">${stats.bounce_rate}%</span>
          </div>
          <div class="stat">
            <span class="label">Unsubscribe Rate:</span>
            <span class="value">${stats.unsubscribe_rate}%</span>
          </div>
        </div>
      `;
    }

    console.log('Campaign completed with stats:', stats);
  }

  updateStatus(data) {
    const campaign = data.campaign;
    const statusElement = document.getElementById('campaign-status');
    
    if (statusElement) {
      statusElement.textContent = campaign.status;
      statusElement.className = `status ${campaign.status}`;
    }

    console.log(`Campaign status: ${campaign.status}`);
  }
}

// Usage example
const emailClient = new EmailMarketingClient();

// Create contact form
document.getElementById('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const contactData = {
    email: document.getElementById('contact-email').value,
    first_name: document.getElementById('contact-first-name').value,
    last_name: document.getElementById('contact-last-name').value,
    company: document.getElementById('contact-company').value,
    job_title: document.getElementById('contact-job-title').value,
    location: document.getElementById('contact-location').value,
    tags: document.getElementById('contact-tags').value.split(',').map(t => t.trim()),
    custom_fields: {
      source: document.getElementById('contact-source').value,
      interests: document.getElementById('contact-interests').value
    }
  };

  try {
    const contact = await emailClient.createContact(contactData);
    console.log('Contact created:', contact);
    alert('Contact created successfully!');
    
    // Reset form
    document.getElementById('contact-form').reset();
    
  } catch (error) {
    console.error('Error creating contact:', error);
    alert('Error creating contact');
  }
});

// Create campaign form
document.getElementById('campaign-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const campaignData = {
    name: document.getElementById('campaign-name').value,
    subject: document.getElementById('campaign-subject').value,
    from_email: document.getElementById('campaign-from-email').value,
    from_name: document.getElementById('campaign-from-name').value,
    template_id: document.getElementById('campaign-template').value,
    list_ids: document.getElementById('campaign-lists').value.split(','),
    reply_to: document.getElementById('campaign-reply-to').value,
    settings: {
      track_opens: document.getElementById('track-opens').checked,
      track_clicks: document.getElementById('track-clicks').checked,
      unsubscribe_link: document.getElementById('unsubscribe-link').checked,
      suppress_duplicates: document.getElementById('suppress-duplicates').checked
    }
  };

  try {
    const campaign = await emailClient.createCampaign(campaignData);
    console.log('Campaign created:', campaign);
    
    // Send campaign immediately
    await emailClient.sendCampaign(campaign.id);
    
    // Start monitoring
    const monitor = new CampaignMonitor(campaign.id);
    
    // Show campaign monitor UI
    document.getElementById('campaign-monitor').style.display = 'block';
    document.getElementById('campaign-name-display').textContent = campaign.name;
    
  } catch (error) {
    console.error('Error creating campaign:', error);
    alert('Error creating campaign');
  }
});

// Load analytics
document.getElementById('load-analytics-btn').addEventListener('click', async () => {
  const campaignId = document.getElementById('analytics-campaign-id').value;
  const days = parseInt(document.getElementById('analytics-days').value) || 30;
  
  try {
    const analytics = await emailClient.getCampaignAnalytics(campaignId, days);
    
    // Display analytics chart
    displayAnalyticsChart(analytics);
    
  } catch (error) {
    console.error('Error loading analytics:', error);
    alert('Error loading analytics');
  }
});

function displayAnalyticsChart(analytics) {
  const ctx = document.getElementById('analytics-chart').getContext('2d');
  
  const labels = analytics.map(a => a.date.split('T')[0]);
  const openRates = analytics.map(a => a.open_rate);
  const clickRates = analytics.map(a => a.click_rate);
  
  // Simple chart implementation
  const chartData = {
    labels: labels,
    datasets: [
      {
        label: 'Open Rate (%)',
        data: openRates,
        borderColor: 'blue',
        backgroundColor: 'rgba(0, 0, 255, 0.1)'
      },
      {
        label: 'Click Rate (%)',
        data: clickRates,
        borderColor: 'green',
        backgroundColor: 'rgba(0, 255, 0, 0.1)'
      }
    ]
  };
  
  console.log('Analytics data:', chartData);
  
  // Update chart display
  const chartContainer = document.getElementById('chart-container');
  chartContainer.innerHTML = `
    <h3>Campaign Analytics</h3>
    <div class="chart-summary">
      <div class="summary-item">
        <span class="label">Average Open Rate:</span>
        <span class="value">${(openRates.reduce((a, b) => a + b, 0) / openRates.length).toFixed(1)}%</span>
      </div>
      <div class="summary-item">
        <span class="label">Average Click Rate:</span>
        <span class="value">${(clickRates.reduce((a, b) => a + b, 0) / clickRates.length).toFixed(1)}%</span>
      </div>
    </div>
  `;
}
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Environment
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=*

# SMTP Configuration
DEFAULT_SMTP_HOST=smtp.example.com
DEFAULT_SMTP_PORT=587
DEFAULT_SMTP_USERNAME=user@example.com
DEFAULT_SMTP_PASSWORD=password
DEFAULT_FROM_EMAIL=marketing@example.com
DEFAULT_FROM_NAME=Marketing Team

# Email Sending
MAX_EMAILS_PER_SECOND=10
MAX_EMAILS_PER_HOUR=1000
MAX_EMAILS_PER_DAY=10000
EMAIL_SEND_TIMEOUT=30
RETRY_FAILED_EMAILS=true
MAX_RETRY_ATTEMPTS=3

# Tracking and Analytics
ENABLE_EMAIL_TRACKING=true
ENABLE_CLICK_TRACKING=true
ENABLE_OPEN_TRACKING=true
TRACKING_PIXEL_URL=https://example.com/track
UNSUBSCRIBE_URL=https://example.com/unsubscribe
CLICK_TRACKING_URL=https://example.com/click

# Campaign Management
CAMPAIGN_SCHEDULER_INTERVAL=60
CAMPAIGN_PROCESSING_BATCH_SIZE=100
MAX_CONCURRENT_CAMPAIGNS=5
CAMPAIGN_RETENTION_DAYS=365

# Data Management
CONTACT_DATA_RETENTION_DAYS=1825  # 5 years
EMAIL_DATA_RETENTION_DAYS=365
ANALYTICS_DATA_RETENTION_DAYS=730
DATA_CLEANUP_INTERVAL=86400  # 24 hours

# Security
ENABLE_EMAIL_VALIDATION=true
ENABLE_SUPPRESSION_LIST=true
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=100
ENABLE_SPAM_CHECK=true

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=10000
WEBSOCKET_PING_TIMEOUT=10

# Database (for persistence)
DATABASE_URL=sqlite:///./email_marketing.db
ENABLE_DATA_BACKUP=true
BACKUP_INTERVAL_HOURS=24
DATABASE_POOL_SIZE=10

# External Services
WEBHOOK_URL=https://example.com/webhooks
WEBHOOK_EVENTS=campaign_sent,email_opened,email_clicked
ENABLE_WEBHOOKS=false

# Logging
LOG_LEVEL=info
ENABLE_EMAIL_LOGGING=true
CAMPAIGN_LOG_RETENTION_DAYS=90
ERROR_LOG_RETENTION_DAYS=30
LOG_FILE_PATH=./logs/email_marketing.log
ENABLE_PERFORMANCE_LOGGING=true
```

## Use Cases

- **Email Marketing**: Complete email marketing automation platform
- **Newsletter Management**: Send and track newsletter campaigns
- **Transactional Emails**: Automated transactional email delivery
- **Lead Nurturing**: Automated email sequences for leads
- **Customer Engagement**: Targeted email campaigns for retention
- **Event Marketing**: Event invitation and follow-up campaigns
- **E-commerce**: Product promotions and abandoned cart emails

## Advanced Features

### Email Personalization
```python
def advanced_personalization(content: str, contact: Contact, campaign_data: dict) -> str:
    """Advanced email personalization with conditional logic"""
    
    # Basic variable replacement
    content = personalize_content(content, contact)
    
    # Conditional blocks
    content = process_conditional_blocks(content, contact)
    
    # Dynamic content based on behavior
    content = add_behavioral_content(content, contact, campaign_data)
    
    # Personalized recommendations
    if contact.custom_fields.get('interests'):
        content = add_recommendations(content, contact.custom_fields['interests'])
    
    return content

def process_conditional_blocks(content: str, contact: Contact) -> str:
    """Process conditional content blocks"""
    import re
    
    # Process {% if condition %} blocks
    pattern = r'\{% if (\w+) %\}(.*?)\{% endif %\}'
    
    def replace_conditional(match):
        condition = match.group(1)
        block_content = match.group(2)
        
        if condition == 'first_name' and contact.first_name:
            return block_content
        elif condition == 'company' and contact.company:
            return block_content
        else:
            return ""
    
    return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)
```

### A/B Testing
```python
def create_ab_campaign(campaign_data: dict, variants: list) -> dict:
    """Create A/B test campaign"""
    
    ab_campaign = {
        "id": generate_campaign_id(),
        "name": campaign_data["name"],
        "type": "ab_test",
        "variants": [],
        "traffic_split": 50/50,  # Default 50/50 split
        "test_duration_days": 7,
        "confidence_level": 95,
        "winner_criteria": "open_rate"
    }
    
    for i, variant_data in enumerate(variants):
        variant = {
            "id": f"variant_{i}",
            "name": f"Variant {chr(65 + i)}",  # A, B, C...
            "subject": variant_data.get("subject"),
            "content": variant_data.get("content"),
            "traffic_percentage": 100 / len(variants),
            "metrics": {
                "sent": 0,
                "opened": 0,
                "clicked": 0,
                "converted": 0
            }
        }
        ab_campaign["variants"].append(variant)
    
    return ab_campaign

def determine_ab_winner(ab_campaign: dict) -> dict:
    """Determine A/B test winner using statistical significance"""
    
    from scipy import stats
    
    winner = None
    best_p_value = 1.0
    
    for i, variant_a in enumerate(ab_campaign["variants"]):
        for j, variant_b in enumerate(ab_campaign["variants"]):
            if i >= j:
                continue
            
            # Perform statistical test
            if ab_campaign["winner_criteria"] == "open_rate":
                rate_a = variant_a["metrics"]["opened"] / variant_a["metrics"]["sent"]
                rate_b = variant_b["metrics"]["opened"] / variant_b["metrics"]["sent"]
            else:
                rate_a = variant_b["metrics"]["clicked"] / variant_a["metrics"]["sent"]
                rate_b = variant_b["metrics"]["clicked"] / variant_b["metrics"]["sent"]
            
            # Two-proportion z-test
            count = [variant_a["metrics"]["opened"], variant_b["metrics"]["opened"]]
            nobs = [variant_a["metrics"]["sent"], variant_b["metrics"]["sent"]]
            
            z_stat, p_value = stats.proportions_ztest(count, nobs)
            
            if p_value < best_p_value and p_value < (1 - ab_campaign["confidence_level"]/100):
                best_p_value = p_value
                winner = variant_a if rate_a > rate_b else variant_b
    
    return {
        "winner": winner,
        "confidence": (1 - best_p_value) * 100,
        "statistical_significance": best_p_value < (1 - ab_campaign["confidence_level"]/100)
    }
```

### Email Automation Workflows
```python
class AutomationEngine:
    def __init__(self):
        self.active_workflows = {}
        self.trigger_handlers = {
            "subscribe": self.handle_subscribe_trigger,
            "email_open": self.handle_email_open_trigger,
            "email_click": self.handle_email_click_trigger,
            "purchase": self.handle_purchase_trigger
        }
    
    def register_workflow(self, workflow: dict):
        """Register automation workflow"""
        workflow_id = workflow["id"]
        self.active_workflows[workflow_id] = workflow
    
    def process_trigger(self, trigger_type: str, contact_id: str, trigger_data: dict):
        """Process automation trigger"""
        if trigger_type in self.trigger_handlers:
            handler = self.trigger_handlers[trigger_type]
            handler(contact_id, trigger_data)
    
    def handle_subscribe_trigger(self, contact_id: str, trigger_data: dict):
        """Handle new subscriber trigger"""
        for workflow in self.active_workflows.values():
            if workflow["trigger_type"] == "subscribe":
                self.execute_workflow_actions(workflow, contact_id, trigger_data)
    
    def execute_workflow_actions(self, workflow: dict, contact_id: str, trigger_data: dict):
        """Execute workflow actions"""
        for action in workflow["actions"]:
            if action["type"] == "send_email":
                self.send_automated_email(action, contact_id, trigger_data)
            elif action["type"] == "wait":
                self.schedule_delayed_action(action, contact_id, trigger_data)
            elif action["type"] == "add_tag":
                self.add_contact_tag(action, contact_id)
    
    def send_automated_email(self, action: dict, contact_id: str, trigger_data: dict):
        """Send automated email"""
        # Implementation for sending automated email
        pass

# Example automation workflow
welcome_workflow = {
    "id": "welcome_series",
    "name": "Welcome Email Series",
    "trigger_type": "subscribe",
    "actions": [
        {
            "type": "send_email",
            "template_id": "welcome_template",
            "delay": 0
        },
        {
            "type": "wait",
            "delay": 86400  # 1 day
        },
        {
            "type": "send_email",
            "template_id": "onboarding_template",
            "delay": 0
        },
        {
            "type": "wait",
            "delay": 604800  # 7 days
        },
        {
            "type": "send_email",
            "template_id": "engagement_template",
            "delay": 0
        }
    ]
}
```

## Production Considerations

- **Email Deliverability**: SPF, DKIM, DMARC configuration
- **Compliance**: GDPR, CAN-SPAM, CASL compliance
- **Scalability**: Handle high-volume email sending
- **Security**: Email validation and spam protection
- **Monitoring**: Real-time delivery and engagement tracking
- **Backup**: Regular backups of contact and campaign data
- **Rate Limiting**: Prevent abuse and maintain sender reputation
- **Analytics**: Comprehensive reporting and insights
