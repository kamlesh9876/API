# Social Media Integration API

A comprehensive social media management platform for posting, scheduling, analytics, and multi-platform content management with support for major social networks.

## Features

- **Multi-Platform Support**: Twitter, Facebook, Instagram, LinkedIn, YouTube, TikTok, Reddit
- **Account Management**: Connect and manage multiple social media accounts
- **Content Publishing**: Create, schedule, and publish posts across platforms
- **Campaign Management**: Organize posts into marketing campaigns
- **Analytics & Insights**: Track engagement, reach, and performance metrics
- **Scheduled Posting**: Automated posting with retry mechanisms
- **Bulk Operations**: Publish multiple posts simultaneously
- **Webhook Integration**: Real-time event notifications
- **Content Optimization**: Platform-specific content validation and formatting

## API Endpoints

### Account Management

#### Connect Social Account
```http
POST /api/accounts
Content-Type: application/json

{
  "user_id": "user_123",
  "platform": "twitter",
  "account_id": "123456789",
  "username": "myhandle",
  "display_name": "My Display Name",
  "access_token": "oauth_token_here",
  "refresh_token": "refresh_token_here"
}
```

#### Get User Accounts
```http
GET /api/accounts?user_id=user_123&platform=twitter
```

#### Disconnect Account
```http
DELETE /api/accounts/{account_id}?user_id=user_123
```

### Post Management

#### Create Post
```http
POST /api/posts
Content-Type: application/json

{
  "user_id": "user_123",
  "platform": "twitter",
  "post_type": "text",
  "content": "Check out our new product! #innovation #tech",
  "media_urls": ["https://example.com/image.jpg"],
  "hashtags": ["innovation", "tech"],
  "mentions": ["@company"],
  "scheduled_at": "2024-01-01T12:00:00"
}
```

#### Publish Post
```http
POST /api/posts/{post_id}/publish
```

#### Get Posts
```http
GET /api/posts?user_id=user_123&platform=twitter&status=published&limit=50&offset=0
```

#### Get Specific Post
```http
GET /api/posts/{post_id}
```

#### Delete Post
```http
DELETE /api/posts/{post_id}?user_id=user_123
```

#### Bulk Publish
```http
POST /api/posts/bulk-publish
Content-Type: application/json

{
  "post_ids": ["post_123", "post_456", "post_789"]
}
```

### Campaign Management

#### Create Campaign
```http
POST /api/campaigns
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Summer Launch Campaign",
  "description": "Product launch campaign for summer collection",
  "platforms": ["twitter", "facebook", "instagram"],
  "start_date": "2024-06-01T00:00:00",
  "end_date": "2024-06-30T23:59:59",
  "budget": 5000.00,
  "target_audience": {
    "age_range": [18, 35],
    "interests": ["technology", "fashion"],
    "location": "US"
  }
}
```

#### Get Campaigns
```http
GET /api/campaigns?user_id=user_123&status=active
```

#### Add Post to Campaign
```http
POST /api/campaigns/{campaign_id}/posts/{post_id}?user_id=user_123
```

### Analytics

#### Get Post Analytics
```http
GET /api/posts/{post_id}/analytics?days=30
```

### Webhooks

#### Create Webhook
```http
POST /api/webhooks
Content-Type: application/json

{
  "user_id": "user_123",
  "platform": "twitter",
  "webhook_url": "https://your-app.com/webhooks/twitter",
  "events": ["post_published", "comment_received", "mention"]
}
```

#### Get Webhooks
```http
GET /api/webhooks?user_id=user_123&platform=twitter
```

### Statistics
```http
GET /api/stats
```

## Data Models

### SocialAccount
```json
{
  "id": "account_123",
  "user_id": "user_123",
  "platform": "twitter",
  "account_id": "123456789",
  "username": "myhandle",
  "display_name": "My Display Name",
  "access_token": "oauth_token_here",
  "refresh_token": "refresh_token_here",
  "token_expires_at": "2024-12-31T23:59:59",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00",
  "last_sync": "2024-01-01T15:30:00",
  "followers_count": 1500,
  "following_count": 300,
  "posts_count": 250
}
```

### Post
```json
{
  "id": "post_123",
  "user_id": "user_123",
  "platform": "twitter",
  "post_type": "text",
  "content": "Check out our new product! #innovation #tech",
  "media_urls": ["https://example.com/image.jpg"],
  "hashtags": ["innovation", "tech"],
  "mentions": ["@company"],
  "status": "published",
  "platform_post_id": "twitter_123456",
  "scheduled_at": "2024-01-01T12:00:00",
  "published_at": "2024-01-01T12:00:00",
  "created_at": "2024-01-01T11:30:00",
  "updated_at": "2024-01-01T12:00:00",
  "metrics": {
    "likes": 45,
    "comments": 12,
    "shares": 8,
    "views": 1200
  }
}
```

### Campaign
```json
{
  "id": "campaign_123",
  "user_id": "user_123",
  "name": "Summer Launch Campaign",
  "description": "Product launch campaign for summer collection",
  "platforms": ["twitter", "facebook", "instagram"],
  "start_date": "2024-06-01T00:00:00",
  "end_date": "2024-06-30T23:59:59",
  "budget": 5000.00,
  "target_audience": {
    "age_range": [18, 35],
    "interests": ["technology", "fashion"],
    "location": "US"
  },
  "posts": ["post_123", "post_456"],
  "status": "active",
  "created_at": "2024-05-15T10:00:00",
  "updated_at": "2024-05-15T10:00:00"
}
```

### Analytics
```json
{
  "id": "analytics_123",
  "post_id": "post_123",
  "platform": "twitter",
  "date": "2024-01-01T12:00:00",
  "impressions": 2500,
  "reach": 1800,
  "engagement": 65,
  "likes": 45,
  "comments": 12,
  "shares": 8,
  "clicks": 25,
  "saves": 5,
  "views": 1200
}
```

## Supported Platforms

### 1. Twitter/X
- **Post Types**: Text, Image, Video, Link
- **Character Limit**: 280 characters
- **Features**: Hashtags, Mentions, Threads
- **Analytics**: Impressions, Engagement, Clicks

### 2. Facebook
- **Post Types**: Text, Image, Video, Link
- **Character Limit**: 63,206 characters
- **Features**: Hashtags, Mentions, Stories, Reels
- **Analytics**: Reach, Engagement, Clicks, Shares

### 3. Instagram
- **Post Types**: Image, Video, Story, Reel
- **Character Limit**: 2,200 characters
- **Features**: Hashtags, Mentions, Location Tags
- **Analytics**: Reach, Engagement, Saves, Shares

### 4. LinkedIn
- **Post Types**: Text, Image, Video, Article
- **Character Limit**: 3,000 characters
- **Features**: Mentions, Hashtags, Professional Content
- **Analytics**: Impressions, Clicks, Engagement

### 5. YouTube
- **Post Types**: Video, Short
- **Character Limit**: 5,000 characters
- **Features**: Tags, Categories, Thumbnails
- **Analytics**: Views, Watch Time, Subscribers

### 6. TikTok
- **Post Types**: Video, Short
- **Character Limit**: 2,200 characters
- **Features**: Hashtags, Effects, Music
- **Analytics**: Views, Likes, Comments, Shares

### 7. Reddit
- **Post Types**: Text, Link, Image, Video
- **Character Limit**: 40,000 characters
- **Features**: Subreddits, Flairs, Crossposting
- **Analytics**: Upvotes, Comments, Awards

## Post Types

### Text Posts
- **Description**: Plain text content
- **Platforms**: All platforms
- **Best For**: Announcements, Updates, Questions

### Image Posts
- **Description**: Single or multiple images
- **Platforms**: Facebook, Instagram, Twitter, LinkedIn
- **Best For**: Visual content, Product showcases

### Video Posts
- **Description**: Video content with captions
- **Platforms**: All platforms (with varying limits)
- **Best For**: Tutorials, Demos, Stories

### Link Posts
- **Description**: Shared external links
- **Platforms**: Facebook, Twitter, LinkedIn, Reddit
- **Best For**: Blog posts, Articles, Resources

### Stories
- **Description**: Ephemeral content (24 hours)
- **Platforms**: Instagram, Facebook, TikTok
- **Best For**: Behind-the-scenes, Quick updates

## Campaign Management

### Campaign Types
- **Product Launch**: New product announcements
- **Brand Awareness**: Increasing brand visibility
- **Lead Generation**: Capturing customer leads
- **Event Promotion**: Marketing events and webinars
- **Content Series**: Themed content campaigns

### Target Audience Options
```json
{
  "demographics": {
    "age_range": [18, 65],
    "gender": ["male", "female", "other"],
    "location": ["US", "CA", "UK"],
    "language": ["en", "es", "fr"]
  },
  "interests": ["technology", "fashion", "sports"],
  "behaviors": ["online_shoppers", "frequent_travelers"],
  "custom_segments": ["vip_customers", "newsletter_subscribers"]
}
```

## Analytics Metrics

### Engagement Metrics
- **Likes**: Number of likes/reactions
- **Comments**: Number of comments
- **Shares**: Number of shares/retweets
- **Saves**: Number of saves/bookmarks

### Reach Metrics
- **Impressions**: Total times content displayed
- **Reach**: Unique users who saw content
- **Views**: Video views or story views

### Performance Metrics
- **Clicks**: Link clicks or call-to-actions
- **Engagement Rate**: (Likes + Comments + Shares) / Reach
- **Click-Through Rate**: Clicks / Impressions

## Installation

```bash
pip install fastapi uvicorn
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
from datetime import datetime, timedelta

# Connect social account
account_data = {
    "user_id": "user_123",
    "platform": "twitter",
    "account_id": "123456789",
    "username": "mybrand",
    "display_name": "My Brand",
    "access_token": "oauth_token_here"
}

response = requests.post("http://localhost:8000/api/accounts", json=account_data)
account = response.json()
print(f"Connected account: {account['id']}")

# Create and schedule post
post_data = {
    "user_id": "user_123",
    "platform": "twitter",
    "post_type": "text",
    "content": "Excited to announce our new feature! 🚀 #innovation #tech",
    "hashtags": ["innovation", "tech"],
    "scheduled_at": (datetime.now() + timedelta(hours=2)).isoformat()
}

response = requests.post("http://localhost:8000/api/posts", json=post_data)
post = response.json()
print(f"Created post: {post['id']}")

# Create campaign
campaign_data = {
    "user_id": "user_123",
    "name": "Q4 Product Launch",
    "description": "Launch campaign for Q4 products",
    "platforms": ["twitter", "facebook", "instagram"],
    "start_date": datetime.now().isoformat(),
    "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
    "budget": 10000.0,
    "target_audience": {
        "age_range": [18, 45],
        "interests": ["technology", "innovation"]
    }
}

response = requests.post("http://localhost:8000/api/campaigns", json=campaign_data)
campaign = response.json()
print(f"Created campaign: {campaign['id']}")

# Add post to campaign
response = requests.post(f"http://localhost:8000/api/campaigns/{campaign['id']}/posts/{post['id']}", params={"user_id": "user_123"})
print("Added post to campaign")

# Publish post immediately
response = requests.post(f"http://localhost:8000/api/posts/{post['id']}/publish")
result = response.json()
print(f"Published post: {result['platform_post_id']}")

# Get analytics
response = requests.get(f"http://localhost:8000/api/posts/{post['id']}/analytics")
analytics = response.json()

print("Post Analytics:")
for data in analytics:
    print(f"  Date: {data['date']}")
    print(f"  Likes: {data['likes']}, Comments: {data['comments']}")
    print(f"  Reach: {data['reach']}, Engagement: {data['engagement']}")
```

### JavaScript Client
```javascript
// Connect social account
const connectAccount = async (userId, platform, credentials) => {
  const accountData = {
    user_id: userId,
    platform,
    account_id: credentials.accountId,
    username: credentials.username,
    display_name: credentials.displayName,
    access_token: credentials.accessToken
  };

  const response = await fetch('http://localhost:8000/api/accounts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(accountData)
  });

  return response.json();
};

// Create and schedule post
const createPost = async (userId, platform, content, mediaUrls = [], scheduledAt = null) => {
  const postData = {
    user_id: userId,
    platform,
    post_type: mediaUrls.length > 0 ? 'image' : 'text',
    content,
    media_urls: mediaUrls,
    scheduled_at: scheduledAt
  };

  const response = await fetch('http://localhost:8000/api/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(postData)
  });

  return response.json();
};

// Create campaign
const createCampaign = async (userId, campaignData) => {
  const data = {
    user_id: userId,
    ...campaignData
  };

  const response = await fetch('http://localhost:8000/api/campaigns', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  return response.json();
};

// Bulk publish posts
const bulkPublish = async (postIds) => {
  const response = await fetch('http://localhost:8000/api/posts/bulk-publish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ post_ids: postIds })
  });

  return response.json();
};

// Usage example
const main = async () => {
  try {
    // Connect accounts
    const twitterAccount = await connectAccount('user_123', 'twitter', {
      accountId: '123456789',
      username: 'mybrand',
      displayName: 'My Brand',
      accessToken: 'oauth_token_here'
    });

    console.log('Connected Twitter account:', twitterAccount.id);

    // Create posts
    const posts = await Promise.all([
      createPost('user_123', 'twitter', 'Check out our new feature! 🚀 #innovation'),
      createPost('user_123', 'facebook', 'We\'re excited to share our latest updates with you!'),
      createPost('user_123', 'instagram', 'Behind the scenes at our office #worklife')
    ]);

    console.log('Created posts:', posts.map(p => p.id));

    // Create campaign
    const campaign = await createCampaign('user_123', {
      name: 'Q4 Launch Campaign',
      description: 'Q4 product launch campaign',
      platforms: ['twitter', 'facebook', 'instagram'],
      start_date: new Date().toISOString(),
      end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      budget: 10000
    });

    console.log('Created campaign:', campaign.id);

    // Add posts to campaign
    for (const post of posts) {
      await fetch(`http://localhost:8000/api/campaigns/${campaign.id}/posts/${post.id}?user_id=user_123`, {
        method: 'POST'
      });
    }

    // Bulk publish
    const publishResults = await bulkPublish(posts.map(p => p.id));
    console.log('Publish results:', publishResults.results);

  } catch (error) {
    console.error('Error:', error);
  }
};

main();
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

# Social Media APIs
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
MAX_POSTS_PER_DAY=1000

# Scheduling
SCHEDULED_POST_CHECK_INTERVAL=60
MAX_RETRY_ATTEMPTS=3

# Database (for persistence)
DATABASE_URL=sqlite:///./social_media.db
ENABLE_POST_ANALYTICS=true

# Webhooks
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3

# Logging
LOG_LEVEL=info
ENABLE_API_LOGGING=true
POST_PUBLISH_LOG_RETENTION_DAYS=30
```

## Use Cases

- **Social Media Management**: Manage multiple social media accounts from one platform
- **Content Marketing**: Plan and execute content campaigns across platforms
- **Brand Management**: Maintain consistent brand presence across social networks
- **Influencer Marketing**: Coordinate influencer campaigns and track performance
- **Customer Engagement**: Monitor and respond to social media interactions
- **Analytics Reporting**: Generate comprehensive social media performance reports

## Advanced Features

### Content Optimization
```python
# Platform-specific content formatting
def optimize_content_for_platform(content: str, platform: Platform) -> str:
    if platform == Platform.TWITTER:
        # Add hashtags and mentions optimally
        return optimize_twitter_content(content)
    elif platform == Platform.INSTAGRAM:
        # Format for Instagram with proper spacing
        return format_instagram_content(content)
    elif platform == Platform.LINKEDIN:
        # Professional tone and formatting
        return format_linkedin_content(content)
    return content
```

### A/B Testing
```python
# Create A/B test variants
def create_ab_test_campaign(base_content: str, variants: List[str]) -> Campaign:
    posts = []
    for i, variant in enumerate(variants):
        post = create_post_with_content(variant, test_group=f"variant_{i}")
        posts.append(post.id)
    
    return create_campaign_with_posts(
        name="A/B Test Campaign",
        posts=posts,
        test_type="content_variant"
    )
```

### Automated Scheduling
```python
# Optimal posting time analysis
def get_optimal_posting_times(account_id: str, platform: Platform) -> List[datetime]:
    # Analyze historical engagement data
    engagement_data = get_historical_engagement(account_id, platform)
    
    # Find peak engagement times
    optimal_times = analyze_engagement_patterns(engagement_data)
    
    return optimal_times
```

## Production Considerations

- **API Rate Limits**: Respect platform-specific rate limits
- **Token Management**: Secure storage and refresh of OAuth tokens
- **Content Moderation**: Automated content filtering and approval
- **Scalability**: Horizontal scaling for high-volume posting
- **Error Handling**: Robust error handling and retry mechanisms
- **Compliance**: GDPR, CCPA compliance for user data
- **Monitoring**: Real-time monitoring of posting success rates
- **Backup**: Regular backups of campaigns and analytics data
