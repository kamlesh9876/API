# Chat Messaging API

A comprehensive real-time chat messaging API with WebSocket support, online/offline status tracking, typing indicators, and conversation management. Built with FastAPI and WebSockets.

## 🚀 Features

- **Real-time Messaging**: WebSocket-based instant messaging
- **Conversation Management**: Create private chats, group chats, and channels
- **Online/Offline Status**: Track user presence and last seen
- **Typing Indicators**: Real-time typing notifications
- **Message Types**: Text, images, files, system messages
- **Message Reactions**: Emoji reactions to messages
- **Message Editing**: Edit sent messages
- **Message Deletion**: Delete messages for everyone
- **Reply Messages**: Threaded conversations
- **User Management**: Profile information and status
- **Participant Management**: Add/remove users from conversations
- **Message History**: Persistent message storage
- **Search & Filter**: Find messages and conversations
- **File Attachments**: Support for image and file sharing
- **Read Receipts**: Track message read status
- **Push Notifications**: Real-time notifications

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Real-time**: WebSockets
- **Storage**: Redis (for production), In-memory (for demo)
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Testing**: Built-in HTML client

## 📋 Prerequisites

- Python 3.7+
- pip package manager
- (Optional) Redis server for production deployment

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8008`

3. **Test with the built-in client**:
Visit `http://localhost:8008/client` for a simple chat interface

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8008/docs`
- ReDoc: `http://localhost:8008/redoc`
- Test Client: `http://localhost:8008/client`

## 💬 WebSocket Connection

### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8008/ws/{user_id}');

ws.onopen = function(event) {
    console.log('Connected to chat server');
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleIncomingMessage(message);
};
```

### WebSocket Message Types

#### Send Message
```json
{
    "type": "send_message",
    "data": {
        "conversation_id": "conv_123",
        "content": "Hello, world!",
        "message_type": "text",
        "reply_to": null
    }
}
```

#### Typing Indicator
```json
{
    "type": "typing",
    "data": {
        "conversation_id": "conv_123",
        "is_typing": true
    }
}
```

#### Join Conversation
```json
{
    "type": "join_conversation",
    "data": {
        "conversation_id": "conv_123"
    }
}
```

## 📡 REST API Endpoints

### Conversations

#### Create Conversation
```http
POST /conversations
Content-Type: application/json

{
    "participant_ids": ["user1", "user2"],
    "type": "private",
    "name": "Chat Room",
    "description": "Our private chat",
    "creator_id": "user1"
}
```

#### Get User Conversations
```http
GET /conversations?user_id=user1
```

#### Get Conversation Details
```http
GET /conversations/{conversation_id}?user_id=user1
```

### Messages

#### Get Messages
```http
GET /conversations/{conversation_id}/messages?user_id=user1&limit=50
```

#### Send Message (REST)
```http
POST /conversations/{conversation_id}/messages
Content-Type: application/json

{
    "content": "Hello!",
    "message_type": "text",
    "reply_to": null,
    "user_id": "user1"
}
```

#### Edit Message
```http
PUT /messages/{message_id}
Content-Type: application/json

{
    "content": "Edited message",
    "user_id": "user1"
}
```

#### Delete Message
```http
DELETE /messages/{message_id}
Content-Type: application/json

{
    "user_id": "user1"
}
```

### User Management

#### Get Online Users
```http
GET /users
```

#### Get User Info
```http
GET /users/{user_id}
```

#### Update User Status
```http
PUT /users/{user_id}/status
Content-Type: application/json

{
    "status": "online",
    "current_user_id": "user1"
}
```

### Typing Indicators

#### Send Typing Indicator
```http
POST /conversations/{conversation_id}/typing
Content-Type: application/json

{
    "is_typing": true,
    "user_id": "user1"
}
```

### Participants

#### Get Conversation Participants
```http
GET /conversations/{conversation_id}/participants?user_id=user1
```

#### Get Online Users in Conversation
```http
GET /conversations/{conversation_id}/online-users?user_id=user1
```

#### Add Participant
```http
POST /conversations/{conversation_id}/participants
Content-Type: application/json

{
    "participant_id": "user3",
    "user_id": "user1"
}
```

#### Remove Participant
```http
DELETE /conversations/{conversation_id}/participants/{participant_id}
Content-Type: application/json

{
    "user_id": "user1"
}
```

### System

#### Get Statistics
```http
GET /stats
```

#### Health Check
```http
GET /health
```

## 📊 Data Models

### User
```json
{
    "id": "user_123",
    "username": "john_doe",
    "display_name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "status": "online",
    "last_seen": "2024-01-15T12:00:00",
    "is_typing": false
}
```

### Conversation
```json
{
    "id": "conv_123",
    "name": "Team Chat",
    "description": "Internal team communication",
    "type": "group",
    "participant_ids": ["user1", "user2", "user3"],
    "admin_ids": ["user1"],
    "created_by": "user1",
    "created_at": "2024-01-15T10:00:00",
    "last_activity": "2024-01-15T12:00:00",
    "last_message": {
        "id": "msg_456",
        "content": "Hello everyone!",
        "sender_id": "user1",
        "timestamp": "2024-01-15T12:00:00"
    },
    "avatar_url": "https://example.com/group-avatar.jpg",
    "is_archived": false
}
```

### Message
```json
{
    "id": "msg_456",
    "conversation_id": "conv_123",
    "sender_id": "user1",
    "content": "Hello, world!",
    "message_type": "text",
    "timestamp": "2024-01-15T12:00:00",
    "edited": false,
    "edited_at": null,
    "reply_to": null,
    "attachments": [],
    "reactions": {
        "👍": ["user2", "user3"],
        "❤️": ["user2"]
    },
    "is_deleted": false,
    "deleted_at": null
}
```

## 🎯 WebSocket Events

### Incoming Events
- **user_data**: Initial user data and conversations
- **new_message**: New message in conversation
- **message_edited**: Message was edited
- **message_deleted**: Message was deleted
- **typing_indicator**: User typing status
- **user_status**: User online/offline status change
- **user_joined**: User joined conversation
- **user_left**: User left conversation
- **conversation_created**: New conversation created
- **participant_added**: New participant added
- **participant_removed**: Participant removed

### Outgoing Events
- **send_message**: Send a new message
- **typing**: Send typing indicator
- **join_conversation**: Join a conversation
- **leave_conversation**: Leave a conversation

## 🧪 Testing Examples

### JavaScript Client Example
```javascript
class ChatClient {
    constructor(userId) {
        this.userId = userId;
        this.ws = null;
        this.conversations = new Map();
    }
    
    connect() {
        this.ws = new WebSocket(`ws://localhost:8008/ws/${this.userId}`);
        
        this.ws.onopen = () => {
            console.log('Connected to chat server');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from chat server');
        };
    }
    
    sendMessage(conversationId, content) {
        this.ws.send(JSON.stringify({
            type: 'send_message',
            data: {
                conversation_id: conversationId,
                content: content,
                message_type: 'text'
            }
        }));
    }
    
    sendTyping(conversationId, isTyping) {
        this.ws.send(JSON.stringify({
            type: 'typing',
            data: {
                conversation_id: conversationId,
                is_typing: isTyping
            }
        }));
    }
    
    handleMessage(data) {
        switch(data.type) {
            case 'new_message':
                this.displayMessage(data.data);
                break;
            case 'typing_indicator':
                this.updateTypingIndicator(data.data);
                break;
            case 'user_status':
                this.updateUserStatus(data.data);
                break;
        }
    }
    
    displayMessage(message) {
        console.log(`${message.sender_id}: ${message.content}`);
    }
}

// Usage
const client = new ChatClient('user_123');
client.connect();
client.sendMessage('conv_456', 'Hello, world!');
```

### Python Client Example
```python
import asyncio
import websockets
import json

async def chat_client(user_id):
    uri = f"ws://localhost:8008/ws/{user_id}"
    
    async with websockets.connect(uri) as websocket:
        print(f"Connected as {user_id}")
        
        # Send a message
        message = {
            "type": "send_message",
            "data": {
                "conversation_id": "conv_123",
                "content": "Hello from Python!",
                "message_type": "text"
            }
        }
        
        await websocket.send(json.dumps(message))
        
        # Listen for messages
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received: {data}")
            except websockets.exceptions.ConnectionClosed:
                break

# Usage
asyncio.run(chat_client("python_user"))
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8008
DEBUG=false

# Redis Configuration (for production)
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=1000

# Message Configuration
MAX_MESSAGE_LENGTH=4000
MAX_MESSAGE_HISTORY=1000
MESSAGE_RETENTION_DAYS=30

# Rate Limiting
RATE_LIMIT_MESSAGES=100
RATE_LIMIT_WINDOW=60

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/chat_api.log
```

### Advanced Configuration
```python
# WebSocket settings
WEBSOCKET_CONFIG = {
    "max_connections": 1000,
    "heartbeat_interval": 30,
    "message_queue_size": 1000,
    "connection_timeout": 300
}

# Message settings
MESSAGE_CONFIG = {
    "max_length": 4000,
    "max_attachments": 5,
    "supported_types": ["text", "image", "file"],
    "edit_timeout": 300,  # 5 minutes
    "delete_timeout": 3600  # 1 hour
}

# Rate limiting
RATE_LIMITS = {
    "messages_per_minute": 100,
    "conversations_per_hour": 10,
    "uploads_per_hour": 20
}
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8008

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8008"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  chat-api:
    build: .
    ports:
      - "8008:8008"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-messaging-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chat-messaging-api
  template:
    metadata:
      labels:
        app: chat-messaging-api
    spec:
      containers:
      - name: chat-api
        image: chat-messaging-api:latest
        ports:
        - containerPort: 8008
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: chat-messaging-api-service
spec:
  selector:
    app: chat-messaging-api
  ports:
  - port: 8008
    targetPort: 8008
  type: LoadBalancer
```

## 📈 Performance Optimization

### Redis Integration
```python
import aioredis
from aioredis import Redis

class RedisConnectionManager:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await aioredis.from_url("redis://localhost:6379")
    
    async def store_message(self, conversation_id: str, message: dict):
        await self.redis.lpush(
            f"messages:{conversation_id}",
            json.dumps(message)
        )
        await self.redis.ltrim(f"messages:{conversation_id}", 0, 999)
    
    async def get_messages(self, conversation_id: str, limit: int = 50):
        messages = await self.redis.lrange(
            f"messages:{conversation_id}",
            0,
            limit - 1
        )
        return [json.loads(msg) for msg in messages]
```

### Connection Pooling
```python
# WebSocket connection pool
class ConnectionPool:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.connections: Dict[str, WebSocket] = {}
        self.connection_count = 0
    
    async def add_connection(self, user_id: str, websocket: WebSocket):
        if self.connection_count >= self.max_size:
            raise Exception("Maximum connections reached")
        
        self.connections[user_id] = websocket
        self.connection_count += 1
```

### Message Queue
```python
# Async message processing
import asyncio
from asyncio import Queue

class MessageProcessor:
    def __init__(self):
        self.message_queue = Queue()
        self.processing = False
    
    async def start_processing(self):
        self.processing = True
        while self.processing:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self.process_message(message)
            except asyncio.TimeoutError:
                continue
    
    async def process_message(self, message: dict):
        # Process and store message
        pass
```

## 🛡️ Security Features

### Authentication
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_from_token(token)
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/conversations/{conversation_id}/messages")
@limiter.limit("100/minute")
async def send_message(request: Request, ...):
    # Rate limited message sending
    pass
```

### Message Validation
```python
def validate_message_content(content: str, message_type: str):
    if message_type == "text":
        if len(content) > 4000:
            raise ValueError("Message too long")
        if contains_inappropriate_content(content):
            raise ValueError("Inappropriate content")
    
    # Additional validation based on message type
    pass
```

## 🔍 Monitoring & Analytics

### Metrics Collection
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
messages_sent = Counter('chat_messages_sent_total', 'Total messages sent')
active_connections = Gauge('chat_active_connections', 'Active WebSocket connections')
message_processing_time = Histogram('chat_message_processing_seconds', 'Message processing time')

# Usage
@messages_sent.inc()
async def send_message(...):
    pass
```

### Logging
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logger = logging.getLogger('chat_api')
handler = RotatingFileHandler('logs/chat_api.log', maxBytes=10485760, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
```

### Health Monitoring
```python
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "active_connections": len(manager.active_connections),
        "total_conversations": len(manager.conversations),
        "total_messages": sum(len(msgs) for msgs in manager.messages.values()),
        "redis_status": await check_redis_health(),
        "memory_usage": get_memory_usage()
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Message Search**: Full-text search across messages
- **File Sharing**: Upload and share files
- **Voice Messages**: Audio message support
- **Video Calling**: WebRTC integration
- **Message Encryption**: End-to-end encryption
- **Bots & Automation**: Chat bot framework
- **Channels**: Public channels and broadcasting
- **Message Threads**: Nested conversations
- **Mentions & Notifications**: @mentions and push notifications
- **Message Reactions**: Emoji reactions with counts
- **Polls & Surveys**: Interactive message types

### AI Integration
- **Smart Replies**: AI-powered message suggestions
- **Content Moderation**: Automated content filtering
- **Sentiment Analysis**: Message sentiment detection
- **Translation**: Real-time message translation
- **Spam Detection**: Automated spam filtering

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Test with the built-in client at `/client`
- Review WebSocket documentation for real-time features

---

**Built with ❤️ using FastAPI and WebSockets**
