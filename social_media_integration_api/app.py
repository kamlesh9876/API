from fastapi import FastAPI, HTTPException, BackgroundTasks
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

app = FastAPI(title="Social Media Integration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class Platform(str, Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    REDDIT = "reddit"

class PostType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    STORY = "story"
    REEL = "reel"
    TWEET = "tweet"
    POST = "post"

class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"

# Data models
class SocialAccount(BaseModel):
    id: str
    user_id: str
    platform: Platform
    account_id: str
    username: str
    display_name: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    last_sync: Optional[datetime] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0

class Post(BaseModel):
    id: str
    user_id: str
    platform: Platform
    post_type: PostType
    content: str
    media_urls: List[str] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    status: PostStatus
    platform_post_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metrics: Dict[str, int] = {}

class Campaign(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    platforms: List[Platform]
    start_date: datetime
    end_date: datetime
    budget: Optional[float] = None
    target_audience: Dict[str, Any] = {}
    posts: List[str] = []  # Post IDs
    status: str = "active"
    created_at: datetime
    updated_at: datetime

class Analytics(BaseModel):
    id: str
    post_id: str
    platform: Platform
    date: datetime
    impressions: int = 0
    reach: int = 0
    engagement: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    saves: int = 0
    views: int = 0

class ScheduledPost(BaseModel):
    id: str
    post_id: str
    scheduled_at: datetime
    platforms: List[Platform]
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime

class Webhook(BaseModel):
    id: str
    user_id: str
    platform: Platform
    webhook_url: str
    events: List[str] = []
    is_active: bool = True
    secret: str
    created_at: datetime
    last_triggered: Optional[datetime] = None

# In-memory storage
social_accounts: Dict[str, SocialAccount] = {}
posts: Dict[str, Post] = {}
campaigns: Dict[str, Campaign] = {}
analytics: Dict[str, List[Analytics]] = {}
scheduled_posts: Dict[str, ScheduledPost] = {}
webhooks: Dict[str, Webhook] = {}

# Utility functions
def generate_account_id() -> str:
    """Generate unique account ID"""
    return f"account_{uuid.uuid4().hex[:8]}"

def generate_post_id() -> str:
    """Generate unique post ID"""
    return f"post_{uuid.uuid4().hex[:8]}"

def generate_campaign_id() -> str:
    """Generate unique campaign ID"""
    return f"campaign_{uuid.uuid4().hex[:8]}"

def generate_webhook_secret() -> str:
    """Generate webhook secret"""
    return uuid.uuid4().hex[:32]

def validate_content_length(content: str, platform: Platform) -> bool:
    """Validate content length for platform"""
    limits = {
        Platform.TWITTER: 280,
        Platform.FACEBOOK: 63206,
        Platform.INSTAGRAM: 2200,
        Platform.LINKEDIN: 3000,
        Platform.REDDIT: 40000
    }
    
    return len(content) <= limits.get(platform, 1000)

def extract_hashtags(content: str) -> List[str]:
    """Extract hashtags from content"""
    import re
    return re.findall(r"#(\w+)", content)

def extract_mentions(content: str) -> List[str]:
    """Extract mentions from content"""
    import re
    return re.findall(r"@(\w+)", content)

async def publish_to_platform(post: Post, account: SocialAccount) -> str:
    """Publish post to specific platform (mock implementation)"""
    # Simulate API call to platform
    await asyncio.sleep(0.1)
    
    # Mock platform post ID
    platform_post_id = f"{account.platform.value}_{random.randint(100000, 999999)}"
    
    # Update post metrics
    post.metrics = {
        "likes": random.randint(0, 100),
        "comments": random.randint(0, 50),
        "shares": random.randint(0, 20),
        "views": random.randint(100, 1000)
    }
    
    return platform_post_id

async def process_scheduled_posts():
    """Process scheduled posts"""
    now = datetime.now()
    
    for scheduled_post in list(scheduled_posts.values()):
        if scheduled_post.status == "pending" and scheduled_post.scheduled_at <= now:
            post = posts.get(scheduled_post.post_id)
            
            if not post:
                continue
            
            try:
                # Find account for the platform
                account = next(
                    (acc for acc in social_accounts.values() 
                     if acc.platform == post.platform and acc.user_id == post.user_id),
                    None
                )
                
                if account:
                    platform_post_id = await publish_to_platform(post, account)
                    post.platform_post_id = platform_post_id
                    post.status = PostStatus.PUBLISHED
                    post.published_at = now
                    scheduled_post.status = "completed"
                else:
                    scheduled_post.retry_count += 1
                    if scheduled_post.retry_count >= scheduled_post.max_retries:
                        scheduled_post.status = "failed"
                        post.status = PostStatus.FAILED
                    
            except Exception as e:
                scheduled_post.retry_count += 1
                if scheduled_post.retry_count >= scheduled_post.max_retries:
                    scheduled_post.status = "failed"
                    post.status = PostStatus.FAILED

# Background task for scheduled posts
async def scheduled_post_processor():
    """Background task to process scheduled posts"""
    while True:
        await process_scheduled_posts()
        await asyncio.sleep(60)  # Check every minute

# Start background task
asyncio.create_task(scheduled_post_processor())

# API Endpoints
@app.post("/api/accounts", response_model=SocialAccount)
async def connect_social_account(
    user_id: str,
    platform: Platform,
    account_id: str,
    username: str,
    display_name: str,
    access_token: str,
    refresh_token: Optional[str] = None,
    token_expires_at: Optional[datetime] = None
):
    """Connect a social media account"""
    account_id_db = generate_account_id()
    
    account = SocialAccount(
        id=account_id_db,
        user_id=user_id,
        platform=platform,
        account_id=account_id,
        username=username,
        display_name=display_name,
        access_token=access_token,
        refresh_token=refresh_token,
        token_expires_at=token_expires_at,
        created_at=datetime.now()
    )
    
    social_accounts[account_id_db] = account
    return account

@app.get("/api/accounts", response_model=List[SocialAccount])
async def get_user_accounts(user_id: str, platform: Optional[Platform] = None):
    """Get user's social media accounts"""
    filtered_accounts = [acc for acc in social_accounts.values() if acc.user_id == user_id]
    
    if platform:
        filtered_accounts = [acc for acc in filtered_accounts if acc.platform == platform]
    
    return filtered_accounts

@app.delete("/api/accounts/{account_id}")
async def disconnect_account(account_id: str, user_id: str):
    """Disconnect social media account"""
    if account_id not in social_accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = social_accounts[account_id]
    
    if account.user_id != user_id:
        raise HTTPException(status_code=403, detail="Account does not belong to user")
    
    del social_accounts[account_id]
    return {"message": "Account disconnected successfully"}

@app.post("/api/posts", response_model=Post)
async def create_post(
    user_id: str,
    platform: Platform,
    post_type: PostType,
    content: str,
    media_urls: Optional[List[str]] = None,
    scheduled_at: Optional[datetime] = None,
    hashtags: Optional[List[str]] = None,
    mentions: Optional[List[str]] = None
):
    """Create a new post"""
    # Validate content length
    if not validate_content_length(content, platform):
        raise HTTPException(status_code=400, detail=f"Content too long for {platform.value}")
    
    post_id = generate_post_id()
    
    # Extract hashtags and mentions if not provided
    if hashtags is None:
        hashtags = extract_hashtags(content)
    
    if mentions is None:
        mentions = extract_mentions(content)
    
    # Determine status
    status = PostStatus.SCHEDULED if scheduled_at else PostStatus.DRAFT
    
    post = Post(
        id=post_id,
        user_id=user_id,
        platform=platform,
        post_type=post_type,
        content=content,
        media_urls=media_urls or [],
        hashtags=hashtags,
        mentions=mentions,
        status=status,
        scheduled_at=scheduled_at,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    posts[post_id] = post
    
    # Create scheduled post if needed
    if scheduled_at:
        scheduled_post_id = generate_post_id()
        scheduled_post = ScheduledPost(
            id=scheduled_post_id,
            post_id=post_id,
            scheduled_at=scheduled_at,
            platforms=[platform],
            created_at=datetime.now()
        )
        scheduled_posts[scheduled_post_id] = scheduled_post
    
    return post

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """Publish a post immediately"""
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts[post_id]
    
    if post.status == PostStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Post already published")
    
    # Find account for the platform
    account = next(
        (acc for acc in social_accounts.values() 
         if acc.platform == post.platform and acc.user_id == post.user_id),
        None
    )
    
    if not account:
        raise HTTPException(status_code=400, detail="No connected account for this platform")
    
    try:
        platform_post_id = await publish_to_platform(post, account)
        post.platform_post_id = platform_post_id
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.now()
        post.updated_at = datetime.now()
        
        # Record analytics
        analytics_id = f"analytics_{uuid.uuid4().hex[:8]}"
        if post_id not in analytics:
            analytics[post_id] = []
        
        analytics_data = Analytics(
            id=analytics_id,
            post_id=post_id,
            platform=post.platform,
            date=datetime.now(),
            **post.metrics
        )
        analytics[post_id].append(analytics_data)
        
        return {"message": "Post published successfully", "platform_post_id": platform_post_id}
        
    except Exception as e:
        post.status = PostStatus.FAILED
        raise HTTPException(status_code=500, detail=f"Failed to publish post: {str(e)}")

@app.get("/api/posts", response_model=List[Post])
async def get_posts(
    user_id: str,
    platform: Optional[Platform] = None,
    status: Optional[PostStatus] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get user's posts with filters"""
    filtered_posts = [post for post in posts.values() if post.user_id == user_id]
    
    if platform:
        filtered_posts = [post for post in filtered_posts if post.platform == platform]
    
    if status:
        filtered_posts = [post for post in filtered_posts if post.status == status]
    
    # Sort by creation date (newest first)
    filtered_posts.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_posts[offset:offset + limit]

@app.get("/api/posts/{post_id}", response_model=Post)
async def get_post(post_id: str):
    """Get specific post"""
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts[post_id]

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str, user_id: str):
    """Delete a post"""
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts[post_id]
    
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="Post does not belong to user")
    
    post.status = PostStatus.DELETED
    post.updated_at = datetime.now()
    
    return {"message": "Post deleted successfully"}

@app.post("/api/campaigns", response_model=Campaign)
async def create_campaign(
    user_id: str,
    name: str,
    description: str,
    platforms: List[Platform],
    start_date: datetime,
    end_date: datetime,
    budget: Optional[float] = None,
    target_audience: Optional[Dict[str, Any]] = None
):
    """Create a new campaign"""
    campaign_id = generate_campaign_id()
    
    campaign = Campaign(
        id=campaign_id,
        user_id=user_id,
        name=name,
        description=description,
        platforms=platforms,
        start_date=start_date,
        end_date=end_date,
        budget=budget,
        target_audience=target_audience or {},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    campaigns[campaign_id] = campaign
    return campaign

@app.get("/api/campaigns", response_model=List[Campaign])
async def get_campaigns(user_id: str, status: Optional[str] = None):
    """Get user's campaigns"""
    filtered_campaigns = [c for c in campaigns.values() if c.user_id == user_id]
    
    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c.status == status]
    
    return filtered_campaigns

@app.post("/api/campaigns/{campaign_id}/posts/{post_id}")
async def add_post_to_campaign(campaign_id: str, post_id: str, user_id: str):
    """Add post to campaign"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    campaign = campaigns[campaign_id]
    post = posts[post_id]
    
    if campaign.user_id != user_id or post.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if post_id not in campaign.posts:
        campaign.posts.append(post_id)
        campaign.updated_at = datetime.now()
    
    return {"message": "Post added to campaign successfully"}

@app.get("/api/posts/{post_id}/analytics", response_model=List[Analytics])
async def get_post_analytics(post_id: str, days: int = 30):
    """Get post analytics"""
    if post_id not in posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    since_date = datetime.now() - timedelta(days=days)
    
    post_analytics = analytics.get(post_id, [])
    filtered_analytics = [a for a in post_analytics if a.date >= since_date]
    
    return sorted(filtered_analytics, key=lambda x: x.date, reverse=True)

@app.post("/api/webhooks", response_model=Webhook)
async def create_webhook(
    user_id: str,
    platform: Platform,
    webhook_url: str,
    events: List[str]
):
    """Create webhook for platform events"""
    webhook_id = generate_webhook_id()
    
    webhook = Webhook(
        id=webhook_id,
        user_id=user_id,
        platform=platform,
        webhook_url=webhook_url,
        events=events,
        secret=generate_webhook_secret(),
        created_at=datetime.now()
    )
    
    webhooks[webhook_id] = webhook
    return webhook

@app.get("/api/webhooks", response_model=List[Webhook])
async def get_webhooks(user_id: str, platform: Optional[Platform] = None):
    """Get user's webhooks"""
    filtered_webhooks = [w for w in webhooks.values() if w.user_id == user_id]
    
    if platform:
        filtered_webhooks = [w for w in filtered_webhooks if w.platform == platform]
    
    return filtered_webhooks

@app.post("/api/posts/bulk-publish")
async def bulk_publish_posts(post_ids: List[str]):
    """Publish multiple posts at once"""
    results = []
    
    for post_id in post_ids:
        try:
            result = await publish_post(post_id)
            results.append({"post_id": post_id, "status": "success", "result": result})
        except Exception as e:
            results.append({"post_id": post_id, "status": "error", "error": str(e)})
    
    return {"results": results}

@app.get("/api/stats")
async def get_social_media_stats():
    """Get social media platform statistics"""
    total_accounts = len(social_accounts)
    total_posts = len(posts)
    total_campaigns = len(campaigns)
    total_webhooks = len(webhooks)
    
    # Platform distribution
    platform_distribution = {}
    for account in social_accounts.values():
        platform = account.platform.value
        platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
    
    # Post status distribution
    status_distribution = {}
    for post in posts.values():
        status = post.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Recent activity
    recent_posts = len([p for p in posts.values() if p.created_at > datetime.now() - timedelta(hours=24)])
    published_posts = len([p for p in posts.values() if p.status == PostStatus.PUBLISHED])
    
    # Engagement metrics
    total_engagement = sum(
        sum(post.metrics.values()) 
        for post in posts.values() 
        if post.metrics
    )
    
    return {
        "total_accounts": total_accounts,
        "total_posts": total_posts,
        "total_campaigns": total_campaigns,
        "total_webhooks": total_webhooks,
        "platform_distribution": platform_distribution,
        "status_distribution": status_distribution,
        "recent_posts_24h": recent_posts,
        "published_posts": published_posts,
        "total_engagement": total_engagement,
        "supported_platforms": [p.value for p in Platform],
        "supported_post_types": [t.value for t in PostType]
    }

@app.get("/")
async def root():
    return {"message": "Social Media Integration API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
