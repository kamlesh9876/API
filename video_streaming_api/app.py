from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import os
import time
from datetime import datetime, timedelta
from enum import Enum
import random

app = FastAPI(title="Video Streaming API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class StreamStatus(str, Enum):
    IDLE = "idle"
    PREPARING = "preparing"
    LIVE = "live"
    ENDED = "ended"
    ERROR = "error"

class VideoQuality(str, Enum):
    AUTO = "auto"
    LOW = "360p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4K"

class ContentType(str, Enum):
    LIVE_STREAM = "live_stream"
    RECORDED = "recorded"
    WEBINAR = "webinar"
    CONFERENCE = "conference"
    GAMING = "gaming"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"

# Data models
class Stream(BaseModel):
    id: str
    title: str
    description: str
    streamer_id: str
    content_type: ContentType
    status: StreamStatus
    stream_key: str
    rtmp_url: str
    hls_url: str
    websocket_url: str
    thumbnail_url: Optional[str] = None
    viewer_count: int = 0
    max_viewers: int = 1000
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    quality: VideoQuality = VideoQuality.AUTO
    is_private: bool = False
    password: Optional[str] = None
    tags: List[str] = []
    category: str
    language: str = "en"
    created_at: datetime
    updated_at: datetime

class Video(BaseModel):
    id: str
    title: str
    description: str
    uploader_id: str
    filename: str
    file_path: str
    file_size: int  # bytes
    duration: int  # seconds
    format: str
    resolution: str
    bitrate: int  # kbps
    thumbnail_url: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    category: str
    tags: List[str] = []
    is_public: bool = True
    is_processed: bool = False
    processing_status: str = "pending"
    upload_date: datetime
    created_at: datetime
    updated_at: datetime

class Viewer(BaseModel):
    id: str
    stream_id: str
    user_id: Optional[str] = None
    ip_address: str
    user_agent: str
    joined_at: datetime
    last_activity: datetime
    quality: VideoQuality = VideoQuality.AUTO
    is_active: bool = True

class ChatMessage(BaseModel):
    id: str
    stream_id: str
    user_id: Optional[str] = None
    username: str
    message: str
    timestamp: datetime
    is_deleted: bool = False

class StreamAnalytics(BaseModel):
    id: str
    stream_id: str
    timestamp: datetime
    viewer_count: int
    bandwidth_usage: float  # Mbps
    average_quality: str
    chat_messages_count: int
    likes_count: int
    shares_count: int

class Playlist(BaseModel):
    id: str
    name: str
    description: str
    creator_id: str
    video_ids: List[str] = []
    is_public: bool = True
    view_count: int = 0
    created_at: datetime
    updated_at: datetime

class Subscription(BaseModel):
    id: str
    user_id: str
    channel_id: str
    created_at: datetime

# In-memory storage
streams: Dict[str, Stream] = {}
videos: Dict[str, Video] = {}
viewers: Dict[str, List[Viewer]] = {}  # stream_id -> list of viewers
chat_messages: Dict[str, List[ChatMessage]] = {}  # stream_id -> list of messages
stream_analytics: Dict[str, List[StreamAnalytics]] = {}  # stream_id -> list of analytics
playlists: Dict[str, Playlist] = {}
subscriptions: Dict[str, Subscription] = {}
websocket_connections: Dict[str, WebSocket] = {}

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # stream_id -> list of connections

    async def connect(self, websocket: WebSocket, stream_id: str, client_id: str):
        await websocket.accept()
        if stream_id not in self.active_connections:
            self.active_connections[stream_id] = []
        self.active_connections[stream_id].append(websocket)
        websocket_connections[client_id] = websocket

    def disconnect(self, stream_id: str, websocket: WebSocket, client_id: str):
        if stream_id in self.active_connections:
            if websocket in self.active_connections[stream_id]:
                self.active_connections[stream_id].remove(websocket)
        if client_id in websocket_connections:
            del websocket_connections[client_id]

    async def broadcast_to_stream(self, stream_id: str, message: dict):
        if stream_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[stream_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[stream_id].remove(conn)

    async def send_to_client(self, client_id: str, message: dict):
        if client_id in websocket_connections:
            try:
                await websocket_connections[client_id].send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Utility functions
def generate_stream_key() -> str:
    """Generate unique stream key"""
    return uuid.uuid4().hex[:16]

def generate_stream_id() -> str:
    """Generate unique stream ID"""
    return f"stream_{uuid.uuid4().hex[:8]}"

def generate_video_id() -> str:
    """Generate unique video ID"""
    return f"video_{uuid.uuid4().hex[:8]}"

def generate_chat_message_id() -> str:
    """Generate unique chat message ID"""
    return f"msg_{uuid.uuid4().hex[:8]}"

def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

async def update_stream_viewers(stream_id: str):
    """Update stream viewer count"""
    if stream_id in viewers:
        active_viewers = [v for v in viewers[stream_id] if v.is_active]
        viewers[stream_id] = active_viewers
        
        if stream_id in streams:
            streams[stream_id].viewer_count = len(active_viewers)
            streams[stream_id].updated_at = datetime.now()
    
    # Broadcast viewer count update
    await manager.broadcast_to_stream(stream_id, {
        "type": "viewer_count_update",
        "viewer_count": len(viewers.get(stream_id, [])),
        "timestamp": datetime.now().isoformat()
    })

async def send_chat_message(stream_id: str, message: ChatMessage):
    """Send chat message to all viewers"""
    if stream_id not in chat_messages:
        chat_messages[stream_id] = []
    
    chat_messages[stream_id].append(message)
    
    # Keep only last 1000 messages
    if len(chat_messages[stream_id]) > 1000:
        chat_messages[stream_id] = chat_messages[stream_id][-1000:]
    
    # Broadcast message
    await manager.broadcast_to_stream(stream_id, {
        "type": "chat_message",
        "message": message.dict(),
        "timestamp": datetime.now().isoformat()
    })

# Background task for analytics collection
async def analytics_collector():
    """Background task to collect stream analytics"""
    while True:
        for stream_id, stream in streams.items():
            if stream.status == StreamStatus.LIVE:
                # Collect analytics data
                viewer_count = len(viewers.get(stream_id, []))
                bandwidth_usage = viewer_count * random.uniform(1.0, 5.0)  # Mock bandwidth usage
                chat_messages_count = len(chat_messages.get(stream_id, []))
                
                analytics_id = f"analytics_{uuid.uuid4().hex[:8]}"
                analytics_data = StreamAnalytics(
                    id=analytics_id,
                    stream_id=stream_id,
                    timestamp=datetime.now(),
                    viewer_count=viewer_count,
                    bandwidth_usage=bandwidth_usage,
                    average_quality="720p",  # Mock quality
                    chat_messages_count=chat_messages_count,
                    likes_count=random.randint(0, 100),
                    shares_count=random.randint(0, 50)
                )
                
                if stream_id not in stream_analytics:
                    stream_analytics[stream_id] = []
                
                stream_analytics[stream_id].append(analytics_data)
                
                # Keep only last 24 hours of analytics
                cutoff_time = datetime.now() - timedelta(hours=24)
                stream_analytics[stream_id] = [
                    a for a in stream_analytics[stream_id] if a.timestamp >= cutoff_time
                ]
        
        await asyncio.sleep(60)  # Collect analytics every minute

# Start background task
asyncio.create_task(analytics_collector())

# Initialize sample data
def initialize_sample_data():
    """Initialize sample stream and video data"""
    # Sample streams
    sample_streams = [
        {
            "title": "Live Gaming Session",
            "description": "Playing the latest games with friends",
            "streamer_id": "streamer_123",
            "content_type": ContentType.GAMING,
            "category": "Gaming",
            "tags": ["gaming", "live", "fps"],
            "language": "en"
        },
        {
            "title": "Music Production Tutorial",
            "description": "Learn music production techniques",
            "streamer_id": "streamer_456",
            "content_type": ContentType.EDUCATION,
            "category": "Music",
            "tags": ["music", "tutorial", "production"],
            "language": "en"
        },
        {
            "title": "Cooking Show",
            "description": "Live cooking demonstration",
            "streamer_id": "streamer_789",
            "content_type": ContentType.ENTERTAINMENT,
            "category": "Cooking",
            "tags": ["cooking", "food", "live"],
            "language": "en"
        }
    ]
    
    for stream_data in sample_streams:
        stream_id = generate_stream_id()
        stream_key = generate_stream_key()
        
        stream = Stream(
            id=stream_id,
            **stream_data,
            status=StreamStatus.LIVE,
            stream_key=stream_key,
            rtmp_url=f"rtmp://localhost:1935/live/{stream_key}",
            hls_url=f"http://localhost:8080/hls/{stream_key}.m3u8",
            websocket_url=f"ws://localhost:8000/ws/{stream_id}",
            start_time=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        streams[stream_id] = stream
        viewers[stream_id] = []
        chat_messages[stream_id] = []
        stream_analytics[stream_id] = []

# Initialize sample data
initialize_sample_data()

# API Endpoints
@app.post("/api/streams", response_model=Stream)
async def create_stream(
    title: str,
    description: str,
    streamer_id: str,
    content_type: ContentType,
    category: str,
    tags: Optional[List[str]] = None,
    max_viewers: int = 1000,
    quality: VideoQuality = VideoQuality.AUTO,
    is_private: bool = False,
    password: Optional[str] = None,
    language: str = "en"
):
    """Create a new stream"""
    stream_id = generate_stream_id()
    stream_key = generate_stream_key()
    
    stream = Stream(
        id=stream_id,
        title=title,
        description=description,
        streamer_id=streamer_id,
        content_type=content_type,
        status=StreamStatus.IDLE,
        stream_key=stream_key,
        rtmp_url=f"rtmp://localhost:1935/live/{stream_key}",
        hls_url=f"http://localhost:8080/hls/{stream_key}.m3u8",
        websocket_url=f"ws://localhost:8000/ws/{stream_id}",
        max_viewers=max_viewers,
        quality=quality,
        is_private=is_private,
        password=password,
        tags=tags or [],
        category=category,
        language=language,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    streams[stream_id] = stream
    viewers[stream_id] = []
    chat_messages[stream_id] = []
    stream_analytics[stream_id] = []
    
    return stream

@app.get("/api/streams", response_model=List[Stream])
async def get_streams(
    status: Optional[StreamStatus] = None,
    content_type: Optional[ContentType] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """Get streams with optional filters"""
    filtered_streams = [s for s in streams.values() if s.status != StreamStatus.ENDED]
    
    if status:
        filtered_streams = [s for s in filtered_streams if s.status == status]
    
    if content_type:
        filtered_streams = [s for s in filtered_streams if s.content_type == content_type]
    
    if category:
        filtered_streams = [s for s in filtered_streams if s.category == category]
    
    # Sort by viewer count (most popular first)
    filtered_streams.sort(key=lambda x: x.viewer_count, reverse=True)
    
    return filtered_streams[:limit]

@app.get("/api/streams/{stream_id}", response_model=Stream)
async def get_stream(stream_id: str):
    """Get specific stream"""
    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    return streams[stream_id]

@app.post("/api/streams/{stream_id}/start")
async def start_stream(stream_id: str, streamer_id: str):
    """Start a stream"""
    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    stream = streams[stream_id]
    
    if stream.streamer_id != streamer_id:
        raise HTTPException(status_code=403, detail="Not authorized to start this stream")
    
    if stream.status != StreamStatus.IDLE:
        raise HTTPException(status_code=400, detail="Stream is not idle")
    
    stream.status = StreamStatus.PREPARING
    stream.updated_at = datetime.now()
    
    # Simulate preparation time
    await asyncio.sleep(2)
    
    stream.status = StreamStatus.LIVE
    stream.start_time = datetime.now()
    stream.updated_at = datetime.now()
    
    # Broadcast stream start
    await manager.broadcast_to_stream(stream_id, {
        "type": "stream_started",
        "stream": stream.dict(),
        "timestamp": datetime.now().isoformat()
    })
    
    return {"message": "Stream started successfully"}

@app.post("/api/streams/{stream_id}/end")
async def end_stream(stream_id: str, streamer_id: str):
    """End a stream"""
    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    stream = streams[stream_id]
    
    if stream.streamer_id != streamer_id:
        raise HTTPException(status_code=403, detail="Not authorized to end this stream")
    
    if stream.status != StreamStatus.LIVE:
        raise HTTPException(status_code=400, detail="Stream is not live")
    
    stream.status = StreamStatus.ENDED
    stream.end_time = datetime.now()
    stream.updated_at = datetime.now()
    
    if stream.start_time:
        stream.duration = int((stream.end_time - stream.start_time).total_seconds())
    
    # Broadcast stream end
    await manager.broadcast_to_stream(stream_id, {
        "type": "stream_ended",
        "stream": stream.dict(),
        "timestamp": datetime.now().isoformat()
    })
    
    return {"message": "Stream ended successfully"}

@app.post("/api/videos/upload", response_model=Video)
async def upload_video(
    file: UploadFile = File(...),
    title: str = "",
    description: str = "",
    uploader_id: str = "",
    category: str = "",
    tags: Optional[str] = None,
    is_public: bool = True
):
    """Upload a video file"""
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Generate video ID and save file
    video_id = generate_video_id()
    upload_dir = f"uploads/videos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{video_id}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Parse tags
    tag_list = tags.split(",") if tags else []
    
    # Create video record
    video = Video(
        id=video_id,
        title=title or file.filename,
        description=description,
        uploader_id=uploader_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        duration=0,  # Would be determined during processing
        format=file.filename.split(".")[-1].upper(),
        resolution="1920x1080",  # Mock resolution
        bitrate=5000,  # Mock bitrate
        category=category,
        tags=tag_list,
        is_public=is_public,
        upload_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    videos[video_id] = video
    
    # Start background processing (mock)
    video.processing_status = "processing"
    
    return video

@app.get("/api/videos", response_model=List[Video])
async def get_videos(
    category: Optional[str] = None,
    uploader_id: Optional[str] = None,
    is_public: Optional[bool] = None,
    limit: int = 50
):
    """Get videos with optional filters"""
    filtered_videos = list(videos.values())
    
    if category:
        filtered_videos = [v for v in filtered_videos if v.category == category]
    
    if uploader_id:
        filtered_videos = [v for v in filtered_videos if v.uploader_id == uploader_id]
    
    if is_public is not None:
        filtered_videos = [v for v in filtered_videos if v.is_public == is_public]
    
    # Sort by upload date (newest first)
    filtered_videos.sort(key=lambda x: x.upload_date, reverse=True)
    
    return filtered_videos[:limit]

@app.get("/api/videos/{video_id}", response_model=Video)
async def get_video(video_id: str):
    """Get specific video"""
    if video_id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Increment view count
    videos[video_id].view_count += 1
    videos[video_id].updated_at = datetime.now()
    
    return videos[video_id]

@app.post("/api/videos/{video_id}/like")
async def like_video(video_id: str):
    """Like a video"""
    if video_id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    videos[video_id].like_count += 1
    videos[video_id].updated_at = datetime.now()
    
    return {"message": "Video liked successfully", "like_count": videos[video_id].like_count}

@app.post("/api/videos/{video_id}/dislike")
async def dislike_video(video_id: str):
    """Dislike a video"""
    if video_id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    videos[video_id].dislike_count += 1
    videos[video_id].updated_at = datetime.now()
    
    return {"message": "Video disliked successfully", "dislike_count": videos[video_id].dislike_count}

@app.post("/api/playlists", response_model=Playlist)
async def create_playlist(
    name: str,
    description: str,
    creator_id: str,
    video_ids: Optional[List[str]] = None,
    is_public: bool = True
):
    """Create a new playlist"""
    playlist_id = f"playlist_{uuid.uuid4().hex[:8]}"
    
    playlist = Playlist(
        id=playlist_id,
        name=name,
        description=description,
        creator_id=creator_id,
        video_ids=video_ids or [],
        is_public=is_public,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    playlists[playlist_id] = playlist
    return playlist

@app.get("/api/playlists", response_model=List[Playlist])
async def get_playlists(
    creator_id: Optional[str] = None,
    is_public: Optional[bool] = None,
    limit: int = 50
):
    """Get playlists with optional filters"""
    filtered_playlists = list(playlists.values())
    
    if creator_id:
        filtered_playlists = [p for p in filtered_playlists if p.creator_id == creator_id]
    
    if is_public is not None:
        filtered_playlists = [p for p in filtered_playlists if p.is_public == is_public]
    
    return sorted(filtered_playlists, key=lambda x: x.created_at, reverse=True)[:limit]

@app.post("/api/playlists/{playlist_id}/videos/{video_id}")
async def add_video_to_playlist(playlist_id: str, video_id: str):
    """Add video to playlist"""
    if playlist_id not in playlists:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if video_id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    playlist = playlists[playlist_id]
    
    if video_id not in playlist.video_ids:
        playlist.video_ids.append(video_id)
        playlist.updated_at = datetime.now()
    
    return {"message": "Video added to playlist successfully"}

@app.get("/api/streams/{stream_id}/analytics", response_model=List[StreamAnalytics])
async def get_stream_analytics(stream_id: str, hours: int = 24):
    """Get stream analytics"""
    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    since_time = datetime.now() - timedelta(hours=hours)
    
    analytics_data = stream_analytics.get(stream_id, [])
    filtered_analytics = [a for a in analytics_data if a.timestamp >= since_time]
    
    return sorted(filtered_analytics, key=lambda x: x.timestamp, reverse=True)

@app.get("/api/streams/{stream_id}/chat", response_model=List[ChatMessage])
async def get_chat_messages(stream_id: str, limit: int = 100):
    """Get chat messages for a stream"""
    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    messages = chat_messages.get(stream_id, [])
    
    # Filter out deleted messages
    active_messages = [m for m in messages if not m.is_deleted]
    
    return sorted(active_messages, key=lambda x: x.timestamp, reverse=True)[:limit]

@app.post("/api/streams/{stream_id}/chat", response_model=ChatMessage)
async def send_chat_message(
    stream_id: str,
    username: str,
    message: str,
    user_id: Optional[str] = None
):
    """Send a chat message"""
    if stream_id not in streams:
        raise HTTPException(status_code=404, detail="Stream not found")
    
    stream = streams[stream_id]
    
    if stream.status != StreamStatus.LIVE:
        raise HTTPException(status_code=400, detail="Stream is not live")
    
    # Create message
    message_id = generate_chat_message_id()
    chat_message = ChatMessage(
        id=message_id,
        stream_id=stream_id,
        user_id=user_id,
        username=username,
        message=message,
        timestamp=datetime.now()
    )
    
    # Send message
    await send_chat_message(stream_id, chat_message)
    
    return chat_message

@app.get("/api/stats")
async def get_streaming_stats():
    """Get streaming platform statistics"""
    total_streams = len(streams)
    total_videos = len(videos)
    total_playlists = len(playlists)
    
    # Stream status distribution
    status_distribution = {}
    for stream in streams.values():
        status = stream.status.value
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Content type distribution
    content_type_distribution = {}
    for stream in streams.values():
        content_type = stream.content_type.value
        content_type_distribution[content_type] = content_type_distribution.get(content_type, 0) + 1
    
    # Total viewers
    total_viewers = sum(len(v) for v in viewers.values())
    
    # Total video views
    total_video_views = sum(v.view_count for v in videos.values())
    
    # Most popular streams
    popular_streams = sorted(streams.values(), key=lambda x: x.viewer_count, reverse=True)[:5]
    
    # Most viewed videos
    popular_videos = sorted(videos.values(), key=lambda x: x.view_count, reverse=True)[:5]
    
    return {
        "total_streams": total_streams,
        "total_videos": total_videos,
        "total_playlists": total_playlists,
        "total_viewers": total_viewers,
        "total_video_views": total_video_views,
        "status_distribution": status_distribution,
        "content_type_distribution": content_type_distribution,
        "popular_streams": [
            {"id": s.id, "title": s.title, "viewer_count": s.viewer_count}
            for s in popular_streams
        ],
        "popular_videos": [
            {"id": v.id, "title": v.title, "view_count": v.view_count}
            for v in popular_videos
        ],
        "supported_qualities": [q.value for q in VideoQuality],
        "supported_content_types": [t.value for t in ContentType]
    }

# WebSocket endpoint for streaming
@app.websocket("/ws/{stream_id}")
async def websocket_endpoint(websocket: WebSocket, stream_id: str):
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, stream_id, client_id)
    
    # Add viewer
    if stream_id not in viewers:
        viewers[stream_id] = []
    
    viewer = Viewer(
        id=client_id,
        stream_id=stream_id,
        ip_address="127.0.0.1",  # Would get from request
        user_agent="WebSocket Client",
        joined_at=datetime.now(),
        last_activity=datetime.now()
    )
    
    viewers[stream_id].append(viewer)
    await update_stream_viewers(stream_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket messages
            if message.get("type") == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
                viewer.last_activity = datetime.now()
            
            elif message.get("type") == "chat_message":
                chat_msg = ChatMessage(
                    id=generate_chat_message_id(),
                    stream_id=stream_id,
                    user_id=message.get("user_id"),
                    username=message.get("username", "Anonymous"),
                    message=message.get("message"),
                    timestamp=datetime.now()
                )
                await send_chat_message(stream_id, chat_msg)
            
            elif message.get("type") == "quality_change":
                quality = message.get("quality")
                viewer.quality = VideoQuality(quality) if quality else VideoQuality.AUTO
                viewer.last_activity = datetime.now()
    
    except WebSocketDisconnect:
        # Remove viewer
        if stream_id in viewers:
            viewers[stream_id] = [v for v in viewers[stream_id] if v.id != client_id]
        
        manager.disconnect(stream_id, websocket, client_id)
        await update_stream_viewers(stream_id)

@app.get("/")
async def root():
    return {"message": "Video Streaming API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
