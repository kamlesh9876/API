# Video Streaming API

A comprehensive video streaming platform supporting live streaming, video uploads, real-time chat, analytics, and content management.

## Features

- **Live Streaming**: RTMP/HLS streaming with real-time viewer tracking
- **Video Upload**: File upload with processing and metadata extraction
- **Real-time Chat**: WebSocket-based live chat for streams
- **Analytics**: Stream performance metrics and viewer analytics
- **Content Management**: Playlists, categories, and content organization
- **Multi-quality Support**: Adaptive bitrate streaming (360p to 4K)
- **WebSocket Integration**: Real-time updates and notifications
- **User Engagement**: Likes, comments, and viewer interactions

## API Endpoints

### Stream Management

#### Create Stream
```http
POST /api/streams
Content-Type: application/json

{
  "title": "Live Gaming Session",
  "description": "Playing the latest games with friends",
  "streamer_id": "streamer_123",
  "content_type": "gaming",
  "category": "Gaming",
  "tags": ["gaming", "live", "fps"],
  "max_viewers": 1000,
  "quality": "auto",
  "is_private": false,
  "language": "en"
}
```

#### Get Streams
```http
GET /api/streams?status=live&content_type=gaming&category=Gaming&limit=50
```

#### Get Specific Stream
```http
GET /api/streams/{stream_id}
```

#### Start Stream
```http
POST /api/streams/{stream_id}/start?streamer_id=streamer_123
```

#### End Stream
```http
POST /api/streams/{stream_id}/end?streamer_id=streamer_123
```

### Video Management

#### Upload Video
```http
POST /api/videos/upload
Content-Type: multipart/form-data

file: [video file]
title: "My Awesome Video"
description: "Check out this amazing video!"
uploader_id: "user_123"
category: "Entertainment"
tags: "funny,awesome,viral"
is_public: true
```

#### Get Videos
```http
GET /api/videos?category=Entertainment&uploader_id=user_123&is_public=true&limit=50
```

#### Get Specific Video
```http
GET /api/videos/{video_id}
```

#### Like/Dislike Video
```http
POST /api/videos/{video_id}/like
POST /api/videos/{video_id}/dislike
```

### Chat System

#### Get Chat Messages
```http
GET /api/streams/{stream_id}/chat?limit=100
```

#### Send Chat Message
```http
POST /api/streams/{stream_id}/chat
Content-Type: application/json

{
  "username": "JohnDoe",
  "message": "Great stream! 👍",
  "user_id": "user_123"
}
```

### Playlists

#### Create Playlist
```http
POST /api/playlists
Content-Type: application/json

{
  "name": "My Favorite Videos",
  "description": "Collection of my favorite content",
  "creator_id": "user_123",
  "video_ids": ["video_123", "video_456"],
  "is_public": true
}
```

#### Get Playlists
```http
GET /api/playlists?creator_id=user_123&is_public=true&limit=50
```

#### Add Video to Playlist
```http
POST /api/playlists/{playlist_id}/videos/{video_id}
```

### Analytics

#### Get Stream Analytics
```http
GET /api/streams/{stream_id}/analytics?hours=24
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Stream
```json
{
  "id": "stream_123",
  "title": "Live Gaming Session",
  "description": "Playing the latest games with friends",
  "streamer_id": "streamer_123",
  "content_type": "gaming",
  "status": "live",
  "stream_key": "abc123def456",
  "rtmp_url": "rtmp://localhost:1935/live/abc123def456",
  "hls_url": "http://localhost:8080/hls/abc123def456.m3u8",
  "websocket_url": "ws://localhost:8000/ws/stream_123",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "viewer_count": 150,
  "max_viewers": 1000,
  "start_time": "2024-01-01T12:00:00",
  "end_time": null,
  "duration": null,
  "quality": "auto",
  "is_private": false,
  "password": null,
  "tags": ["gaming", "live", "fps"],
  "category": "Gaming",
  "language": "en",
  "created_at": "2024-01-01T11:30:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### Video
```json
{
  "id": "video_123",
  "title": "My Awesome Video",
  "description": "Check out this amazing video!",
  "uploader_id": "user_123",
  "filename": "awesome_video.mp4",
  "file_path": "uploads/videos/video_123_awesome_video.mp4",
  "file_size": 1073741824,
  "duration": 1800,
  "format": "MP4",
  "resolution": "1920x1080",
  "bitrate": 5000,
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "view_count": 1500,
  "like_count": 125,
  "dislike_count": 3,
  "category": "Entertainment",
  "tags": ["funny", "awesome", "viral"],
  "is_public": true,
  "is_processed": true,
  "processing_status": "completed",
  "upload_date": "2024-01-01T10:00:00",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:30:00"
}
```

### Chat Message
```json
{
  "id": "msg_123",
  "stream_id": "stream_123",
  "user_id": "user_456",
  "username": "JohnDoe",
  "message": "Great stream! 👍",
  "timestamp": "2024-01-01T12:05:00",
  "is_deleted": false
}
```

### Stream Analytics
```json
{
  "id": "analytics_123",
  "stream_id": "stream_123",
  "timestamp": "2024-01-01T12:00:00",
  "viewer_count": 150,
  "bandwidth_usage": 750.5,
  "average_quality": "720p",
  "chat_messages_count": 25,
  "likes_count": 50,
  "shares_count": 10
}
```

## Stream Quality Options

### Auto
- **Description**: Adaptive bitrate streaming
- **Use Cases**: Variable network conditions
- **Benefits**: Optimal quality based on bandwidth

### 360p (Low)
- **Resolution**: 640x360
- **Bitrate**: 800-1200 kbps
- **Use Cases**: Low bandwidth, mobile devices

### 720p (Medium)
- **Resolution**: 1280x720
- **Bitrate**: 2000-3000 kbps
- **Use Cases**: Standard quality streaming

### 1080p (High)
- **Resolution**: 1920x1080
- **Bitrate**: 4000-6000 kbps
- **Use Cases**: High quality streaming

### 4K (Ultra)
- **Resolution**: 3840x2160
- **Bitrate**: 8000-15000 kbps
- **Use Cases**: Premium content, high bandwidth

## Content Types

### Live Stream
- **Description**: Real-time broadcasting
- **Features**: Live chat, real-time analytics
- **Use Cases**: Events, gaming, tutorials

### Recorded
- **Description**: Pre-recorded video content
- **Features**: VOD, playlists, search
- **Use Cases**: Educational content, entertainment

### Webinar
- **Description**: Interactive presentations
- **Features**: Q&A, screen sharing, polls
- **Use Cases**: Business presentations, education

### Conference
- **Description**: Multi-participant meetings
- **Features**: Video conferencing, screen sharing
- **Use Cases**: Business meetings, remote work

### Gaming
- **Description**: Gaming content and streams
- **Features**: Low latency, chat integration
- **Use Cases**: Live gaming, tournaments

### Education
- **Description**: Educational content
- **Features**: Chapters, subtitles, notes
- **Use Cases**: Online courses, tutorials

### Entertainment
- **Description**: Entertainment content
- **Features**: Comments, recommendations
- **Use Cases**: Shows, movies, music

## WebSocket Events

### Stream Events
```javascript
// Stream started
{
  "type": "stream_started",
  "stream": {...},
  "timestamp": "2024-01-01T12:00:00"
}

// Stream ended
{
  "type": "stream_ended",
  "stream": {...},
  "timestamp": "2024-01-01T13:00:00"
}

// Viewer count update
{
  "type": "viewer_count_update",
  "viewer_count": 150,
  "timestamp": "2024-01-01T12:05:00"
}
```

### Chat Events
```javascript
// New chat message
{
  "type": "chat_message",
  "message": {
    "id": "msg_123",
    "username": "JohnDoe",
    "message": "Great stream! 👍",
    "timestamp": "2024-01-01T12:05:00"
  }
}
```

### Connection Events
```javascript
// Ping/Pong for connection health
{
  "type": "ping"
}

{
  "type": "pong"
}

// Quality change
{
  "type": "quality_change",
  "quality": "720p"
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

# Create a stream
stream_data = {
    "title": "Live Coding Session",
    "description": "Building a web application live",
    "streamer_id": "streamer_123",
    "content_type": "education",
    "category": "Technology",
    "tags": ["coding", "web", "live"],
    "max_viewers": 500
}

response = requests.post("http://localhost:8000/api/streams", json=stream_data)
stream = response.json()
print(f"Created stream: {stream['id']}")

# Start the stream
response = requests.post(f"http://localhost:8000/api/streams/{stream['id']}/start?streamer_id=streamer_123")
print(f"Stream started: {response.json()}")

# Upload a video
files = {"file": open("my_video.mp4", "rb")}
data = {
    "title": "My Tutorial Video",
    "description": "Learn how to build web apps",
    "uploader_id": "user_123",
    "category": "Education",
    "tags": "tutorial,web,development",
    "is_public": "true"
}

response = requests.post("http://localhost:8000/api/videos/upload", files=files, data=data)
video = response.json()
print(f"Uploaded video: {video['id']}")

# Get live streams
response = requests.get("http://localhost:8000/api/streams?status=live")
live_streams = response.json()

print("Live streams:")
for stream in live_streams:
    print(f"  {stream['title']}: {stream['viewer_count']} viewers")

# Create a playlist
playlist_data = {
    "name": "My Web Development Series",
    "description": "Collection of web development tutorials",
    "creator_id": "user_123",
    "video_ids": [video['id']],
    "is_public": "true"
}

response = requests.post("http://localhost:8000/api/playlists", json=playlist_data)
playlist = response.json()
print(f"Created playlist: {playlist['id']}")

# WebSocket client for live stream
async def stream_client():
    uri = f"ws://localhost:8000/ws/{stream['id']}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to stream: {stream['title']}")
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'stream_started':
                print(f"Stream started at {data['timestamp']}")
            elif data['type'] == 'viewer_count_update':
                print(f"Current viewers: {data['viewer_count']}")
            elif data['type'] == 'chat_message':
                msg = data['message']
                print(f"Chat - {msg['username']}: {msg['message']}")
            elif data['type'] == 'pong':
                print("Connection healthy")

# Run WebSocket client
asyncio.run(stream_client())
```

### JavaScript Client
```javascript
// Stream management client
class StreamingClient {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }

  async createStream(streamData) {
    const response = await fetch(`${this.baseURL}/api/streams`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(streamData)
    });
    return response.json();
  }

  async startStream(streamId, streamerId) {
    const response = await fetch(`${this.baseURL}/api/streams/${streamId}/start?streamer_id=${streamerId}`, {
      method: 'POST'
    });
    return response.json();
  }

  async getLiveStreams() {
    const response = await fetch(`${this.baseURL}/api/streams?status=live`);
    return response.json();
  }

  async uploadVideo(file, videoData) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.keys(videoData).forEach(key => {
      formData.append(key, videoData[key]);
    });

    const response = await fetch(`${this.baseURL}/api/videos/upload`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  }

  async createPlaylist(playlistData) {
    const response = await fetch(`${this.baseURL}/api/playlists`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(playlistData)
    });
    return response.json();
  }
}

// WebSocket stream viewer
class StreamViewer {
  constructor(streamId) {
    this.streamId = streamId;
    this.ws = new WebSocket(`ws://localhost:8000/ws/${streamId}`);
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('Connected to stream');
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from stream');
      clearInterval(this.pingInterval);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'stream_started':
        this.onStreamStarted(message.stream);
        break;
      case 'stream_ended':
        this.onStreamEnded(message.stream);
        break;
      case 'viewer_count_update':
        this.updateViewerCount(message.viewer_count);
        break;
      case 'chat_message':
        this.displayChatMessage(message.message);
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

  sendChatMessage(username, message, userId = null) {
    this.ws.send(JSON.stringify({
      type: 'chat_message',
      username,
      message,
      user_id: userId
    }));
  }

  changeQuality(quality) {
    this.ws.send(JSON.stringify({
      type: 'quality_change',
      quality
    }));
  }

  // Event handlers
  onStreamStarted(stream) {
    console.log('Stream started:', stream.title);
    document.getElementById('stream-title').textContent = stream.title;
    document.getElementById('stream-status').textContent = 'LIVE';
    document.getElementById('stream-status').className = 'status-live';
  }

  onStreamEnded(stream) {
    console.log('Stream ended:', stream.title);
    document.getElementById('stream-status').textContent = 'ENDED';
    document.getElementById('stream-status').className = 'status-ended';
  }

  updateViewerCount(count) {
    document.getElementById('viewer-count').textContent = count.toLocaleString();
  }

  displayChatMessage(message) {
    const chatContainer = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message';
    messageElement.innerHTML = `
      <span class="username">${message.username}:</span>
      <span class="message">${message.message}</span>
      <span class="timestamp">${new Date(message.timestamp).toLocaleTimeString()}</span>
    `;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
}

// Usage example
const streamingClient = new StreamingClient();

// Create and start a stream
document.getElementById('create-stream-btn').addEventListener('click', async () => {
  const streamData = {
    title: document.getElementById('stream-title-input').value,
    description: document.getElementById('stream-description').value,
    streamer_id: 'streamer_123',
    content_type: 'gaming',
    category: 'Gaming',
    tags: document.getElementById('stream-tags').value.split(','),
    max_viewers: parseInt(document.getElementById('max-viewers').value) || 1000
  };

  try {
    const stream = await streamingClient.createStream(streamData);
    console.log('Stream created:', stream);
    
    // Start the stream
    await streamingClient.startStream(stream.id, 'streamer_123');
    
    // Connect WebSocket viewer
    const viewer = new StreamViewer(stream.id);
    
    // Setup chat
    document.getElementById('chat-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const username = document.getElementById('chat-username').value;
      const message = document.getElementById('chat-message').value;
      
      viewer.sendChatMessage(username, message);
      document.getElementById('chat-message').value = '';
    });
    
    // Setup quality selector
    document.getElementById('quality-selector').addEventListener('change', (e) => {
      viewer.changeQuality(e.target.value);
    });
    
  } catch (error) {
    console.error('Error creating stream:', error);
  }
});

// Upload video
document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const fileInput = document.getElementById('video-file');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Please select a video file');
    return;
  }
  
  const videoData = {
    title: document.getElementById('video-title').value,
    description: document.getElementById('video-description').value,
    uploader_id: 'user_123',
    category: document.getElementById('video-category').value,
    tags: document.getElementById('video-tags').value,
    is_public: document.getElementById('video-public').checked
  };
  
  try {
    const video = await streamingClient.uploadVideo(file, videoData);
    console.log('Video uploaded:', video);
    alert('Video uploaded successfully!');
    
    // Reset form
    document.getElementById('upload-form').reset();
    
  } catch (error) {
    console.error('Error uploading video:', error);
    alert('Error uploading video');
  }
});

// Load live streams
streamingClient.getLiveStreams().then(streams => {
  const streamsContainer = document.getElementById('live-streams');
  
  streams.forEach(stream => {
    const streamCard = document.createElement('div');
    streamCard.className = 'stream-card';
    streamCard.innerHTML = `
      <h3>${stream.title}</h3>
      <p>${stream.description}</p>
      <div class="stream-info">
        <span class="viewer-count">${stream.viewer_count} viewers</span>
        <span class="category">${stream.category}</span>
      </div>
      <button class="watch-btn" data-stream-id="${stream.id}">Watch Stream</button>
    `;
    
    streamsContainer.appendChild(streamCard);
  });
  
  // Add click handlers for watch buttons
  document.querySelectorAll('.watch-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const streamId = e.target.dataset.streamId;
      const viewer = new StreamViewer(streamId);
    });
  });
});
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

# Streaming Configuration
RTMP_SERVER_HOST=localhost
RTMP_SERVER_PORT=1935
HLS_SERVER_HOST=localhost
HLS_SERVER_PORT=8080
MAX_STREAM_DURATION=14400  # 4 hours in seconds

# File Upload
MAX_FILE_SIZE=5368709120  # 5GB in bytes
SUPPORTED_FORMATS=mp4,avi,mov,wmv,flv,webm,mkv
UPLOAD_DIR=./uploads/videos
THUMBNAIL_DIR=./uploads/thumbnails

# Quality Settings
ENABLE_ADAPTIVE_BITRATE=true
DEFAULT_QUALITY=auto
MAX_BITRATE_4K=15000
MAX_BITRATE_1080P=6000
MAX_BITRATE_720P=3000
MAX_BITRATE_360P=1200

# Chat System
ENABLE_CHAT=true
MAX_CHAT_MESSAGE_LENGTH=500
CHAT_HISTORY_LIMIT=1000
CHAT_RATE_LIMIT=5  # messages per minute

# Analytics
ENABLE_ANALYTICS=true
ANALYTICS_RETENTION_HOURS=24
VIEWER_UPDATE_INTERVAL=30
BANDWIDTH_CALCULATION_INTERVAL=60

# WebSocket
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS_PER_STREAM=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=10000
WEBSOCKET_PING_TIMEOUT=10

# Database (for persistence)
DATABASE_URL=sqlite:///./video_streaming.db
ENABLE_STREAM_RECORDING=false
RECORDING_DIR=./recordings
METADATA_RETENTION_DAYS=365

# Security
ENABLE_STREAM_AUTHENTICATION=false
STREAM_KEY_LENGTH=16
ENABLE_CONTENT_MODERATION=false
CHAT_PROFANITY_FILTER=false

# Performance
ENABLE_CDN_INTEGRATION=false
CDN_BASE_URL=
ENABLE_TRANSCODING=true
TRANSCODING_CONCURRENCY=4
TRANSCODING_PRESET=fast

# Logging
LOG_LEVEL=info
ENABLE_STREAM_LOGGING=true
CHAT_LOG_RETENTION_DAYS=30
ANALYTICS_LOG_RETENTION_DAYS=90
```

## Use Cases

- **Live Streaming Platform**: Complete live streaming service with chat and analytics
- **Video Hosting**: Video-on-demand platform with playlists and recommendations
- **Educational Platform**: Online learning with live classes and recorded content
- **Gaming Platform**: Game streaming with low latency and viewer interaction
- **Conference Platform**: Virtual events and webinars with interactive features
- **Entertainment Platform**: Content creation and distribution platform

## Advanced Features

### Adaptive Bitrate Streaming
```python
# Generate multiple quality variants
def generate_hls_variants(video_path, output_dir):
    qualities = [
        {"name": "360p", "video_bitrate": "800k", "audio_bitrate": "96k"},
        {"name": "720p", "video_bitrate": "2800k", "audio_bitrate": "128k"},
        {"name": "1080p", "video_bitrate": "5000k", "audio_bitrate": "192k"}
    ]
    
    for quality in qualities:
        output_path = f"{output_dir}/{quality['name']}.m3u8"
        # FFmpeg command to generate variant
        ffmpeg_command = [
            "ffmpeg", "-i", video_path,
            "-vf", f"scale=-2:{quality['name'].replace('p', '')}",
            "-b:v", quality['video_bitrate'],
            "-b:a", quality['audio_bitrate'],
            "-hls_time", "6",
            "-hls_list_size", "0",
            output_path
        ]
        subprocess.run(ffmpeg_command)
```

### Stream Recording
```python
# Record live streams for VOD
async def record_stream(stream_key, output_path):
    """Record RTMP stream to file"""
    ffmpeg_command = [
        "ffmpeg", "-i", f"rtmp://localhost:1935/live/{stream_key}",
        "-c", "copy",
        "-f", "mp4",
        output_path
    ]
    
    process = await asyncio.create_subprocess_exec(*ffmpeg_command)
    return process
```

### Content Moderation
```python
# Automated content moderation
def moderate_content(content_type, content_data):
    """Moderate uploaded content"""
    if content_type == "chat_message":
        return moderate_chat_message(content_data)
    elif content_type == "video":
        return moderate_video_content(content_data)
    elif content_type == "stream_title":
        return moderate_text_content(content_data)

def moderate_chat_message(message):
    """Check chat message for inappropriate content"""
    blocked_words = ["spam", "abuse", "inappropriate"]
    
    for word in blocked_words:
        if word.lower() in message.lower():
            return {"allowed": False, "reason": "Inappropriate content"}
    
    return {"allowed": True}
```

## Production Considerations

- **CDN Integration**: Content delivery network for global streaming
- **Transcoding**: Video transcoding for multiple quality levels
- **Storage**: Scalable storage for video files and recordings
- **Security**: Content protection, DRM, and access control
- **Scalability**: Horizontal scaling for high traffic
- **Monitoring**: Real-time monitoring of stream health and performance
- **Backup**: Redundant systems and data backup strategies
- **Compliance**: Content licensing and copyright management
