from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import json
import uuid
import asyncio
from collections import defaultdict, deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Messaging API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    TYPING = "typing"
    ONLINE_STATUS = "online_status"

class UserStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"

class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"

# Pydantic models
class User(BaseModel):
    id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    status: UserStatus = UserStatus.OFFLINE
    last_seen: Optional[datetime] = None
    is_typing: bool = False

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.now)
    edited: bool = False
    edited_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
    reactions: Dict[str, List[str]] = {}  # emoji -> list of user_ids
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    description: Optional[str] = None
    type: ConversationType
    participant_ids: List[str]
    admin_ids: List[str] = []
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_message: Optional[Message] = None
    last_activity: datetime = Field(default_factory=datetime.now)
    avatar_url: Optional[str] = None
    is_archived: bool = False
    settings: Dict[str, Any] = {}

class TypingIndicator(BaseModel):
    conversation_id: str
    user_id: str
    is_typing: bool
    timestamp: datetime = Field(default_factory=datetime.now)

class OnlineStatusUpdate(BaseModel):
    user_id: str
    status: UserStatus
    timestamp: datetime = Field(default_factory=datetime.now)

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# In-memory storage (for demo purposes)
# In production, replace with Redis and database
class ConnectionManager:
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        # User information
        self.users: Dict[str, User] = {}
        # Conversations
        self.conversations: Dict[str, Conversation] = {}
        # Messages by conversation
        self.messages: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        # Typing indicators
        self.typing_indicators: Dict[str, Set[str]] = defaultdict(set)  # conversation_id -> set of user_ids
        # Online users by conversation
        self.online_users: Dict[str, Set[str]] = defaultdict(set)  # conversation_id -> set of user_ids

    async def connect(self, websocket: WebSocket, user_id: str, user_info: Dict[str, Any]):
        """Connect a new user"""
        await websocket.accept()
        
        # Store connection
        self.active_connections[user_id] = websocket
        
        # Create or update user
        user = User(
            id=user_id,
            username=user_info.get("username", f"user_{user_id[:8]}"),
            display_name=user_info.get("display_name"),
            avatar_url=user_info.get("avatar_url"),
            status=UserStatus.ONLINE,
            last_seen=datetime.now()
        )
        self.users[user_id] = user
        
        # Add user to online users in their conversations
        for conv_id, conv in self.conversations.items():
            if user_id in conv.participant_ids:
                self.online_users[conv_id].add(user_id)
        
        # Broadcast online status
        await self.broadcast_user_status(user_id, UserStatus.ONLINE)
        
        logger.info(f"User {user_id} connected")

    def disconnect(self, user_id: str):
        """Disconnect a user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.users:
            self.users[user_id].status = UserStatus.OFFLINE
            self.users[user_id].last_seen = datetime.now()
        
        # Remove from online users in conversations
        for conv_id in self.online_users:
            if user_id in self.online_users[conv_id]:
                self.online_users[conv_id].discard(user_id)
        
        # Remove typing indicators
        for conv_id in self.typing_indicators:
            if user_id in self.typing_indicators[conv_id]:
                self.typing_indicators[conv_id].discard(user_id)
        
        logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, user_id: str, message: WebSocketMessage):
        """Send message to specific user"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message.json())

    async def broadcast_to_conversation(self, conversation_id: str, message: WebSocketMessage, exclude_user: Optional[str] = None):
        """Broadcast message to all users in conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return
        
        for participant_id in conversation.participant_ids:
            if participant_id != exclude_user and participant_id in self.active_connections:
                await self.send_personal_message(participant_id, message)

    async def broadcast_user_status(self, user_id: str, status: UserStatus):
        """Broadcast user status to all conversations they're in"""
        user = self.users.get(user_id)
        if not user:
            return
        
        status_update = WebSocketMessage(
            type="user_status",
            data={
                "user_id": user_id,
                "status": status.value,
                "last_seen": user.last_seen.isoformat() if user.last_seen else None
            }
        )
        
        for conv_id, conv in self.conversations.items():
            if user_id in conv.participant_ids:
                await self.broadcast_to_conversation(conv_id, status_update)

    async def handle_typing_indicator(self, typing_data: TypingIndicator):
        """Handle typing indicator"""
        conv_id = typing_data.conversation_id
        user_id = typing_data.user_id
        
        if typing_data.is_typing:
            self.typing_indicators[conv_id].add(user_id)
        else:
            self.typing_indicators[conv_id].discard(user_id)
        
        # Broadcast to conversation
        typing_message = WebSocketMessage(
            type="typing_indicator",
            data={
                "conversation_id": conv_id,
                "user_id": user_id,
                "is_typing": typing_data.is_typing,
                "typing_users": list(self.typing_indicators[conv_id])
            }
        )
        
        await self.broadcast_to_conversation(conv_id, typing_message, exclude_user=user_id)

    def get_conversation_messages(self, conversation_id: str, limit: int = 50, before: Optional[datetime] = None) -> List[Message]:
        """Get messages for a conversation"""
        messages = list(self.messages[conversation_id])
        
        # Filter by timestamp if provided
        if before:
            messages = [msg for msg in messages if msg.timestamp < before]
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Limit results
        return messages[:limit]

    def create_conversation(self, creator_id: str, participant_ids: List[str], conv_type: ConversationType, name: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        # Ensure creator is in participants
        if creator_id not in participant_ids:
            participant_ids.append(creator_id)
        
        conversation = Conversation(
            name=name,
            type=conv_type,
            participant_ids=participant_ids,
            admin_ids=[creator_id],
            created_by=creator_id
        )
        
        self.conversations[conversation.id] = conversation
        
        # Initialize online users for this conversation
        self.online_users[conversation.id] = set()
        for participant_id in participant_ids:
            if participant_id in self.active_connections:
                self.online_users[conversation.id].add(participant_id)
        
        return conversation

    def add_message(self, message: Message):
        """Add a message to conversation"""
        self.messages[message.conversation_id].append(message)
        
        # Update conversation last activity and last message
        if message.conversation_id in self.conversations:
            conv = self.conversations[message.conversation_id]
            conv.last_activity = message.timestamp
            conv.last_message = message

# Initialize connection manager
manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time messaging"""
    try:
        # Receive initial user info
        await websocket.receive_text()
        user_info = {"username": f"user_{user_id[:8]}"}
        
        # Connect user
        await manager.connect(websocket, user_id, user_info)
        
        # Send user's conversations and messages
        await send_user_data(user_id)
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            await handle_websocket_message(user_id, message_data)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

async def handle_websocket_message(user_id: str, message_data: Dict[str, Any]):
    """Handle incoming WebSocket message"""
    message_type = message_data.get("type")
    data = message_data.get("data", {})
    
    if message_type == "send_message":
        await handle_send_message(user_id, data)
    elif message_type == "typing":
        await handle_typing(user_id, data)
    elif message_type == "join_conversation":
        await handle_join_conversation(user_id, data)
    elif message_type == "leave_conversation":
        await handle_leave_conversation(user_id, data)

async def send_user_data(user_id: str):
    """Send user's conversations and messages"""
    # Get user's conversations
    user_conversations = []
    for conv_id, conv in manager.conversations.items():
        if user_id in conv.participant_ids:
            # Get recent messages
            messages = manager.get_conversation_messages(conv_id, limit=20)
            
            # Get participant details
            participants = []
            for participant_id in conv.participant_ids:
                participant = manager.users.get(participant_id)
                if participant:
                    participants.append({
                        "id": participant.id,
                        "username": participant.username,
                        "display_name": participant.display_name,
                        "avatar_url": participant.avatar_url,
                        "status": participant.status.value,
                        "is_online": participant_id in manager.active_connections
                    })
            
            user_conversations.append({
                "id": conv.id,
                "name": conv.name,
                "type": conv.type.value,
                "participants": participants,
                "created_at": conv.created_at.isoformat(),
                "last_activity": conv.last_activity.isoformat(),
                "last_message": conv.last_message.dict() if conv.last_message else None,
                "unread_count": len([m for m in messages if m.sender_id != user_id])  # Simplified
            })
    
    # Send user data
    user_data = WebSocketMessage(
        type="user_data",
        data={
            "user": manager.users[user_id].dict(),
            "conversations": user_conversations
        }
    )
    await manager.send_personal_message(user_id, user_data)

async def handle_send_message(user_id: str, data: Dict[str, Any]):
    """Handle sending a message"""
    conversation_id = data.get("conversation_id")
    content = data.get("content", "")
    message_type = MessageType(data.get("message_type", "text"))
    reply_to = data.get("reply_to")
    
    if not conversation_id or not content:
        return
    
    # Check if user is in conversation
    conversation = manager.conversations.get(conversation_id)
    if not conversation or user_id not in conversation.participant_ids:
        return
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=user_id,
        content=content,
        message_type=message_type,
        reply_to=reply_to
    )
    
    # Add message
    manager.add_message(message)
    
    # Broadcast to conversation
    message_ws = WebSocketMessage(
        type="new_message",
        data=message.dict()
    )
    await manager.broadcast_to_conversation(conversation_id, message_ws)

async def handle_typing(user_id: str, data: Dict[str, Any]):
    """Handle typing indicator"""
    conversation_id = data.get("conversation_id")
    is_typing = data.get("is_typing", False)
    
    if not conversation_id:
        return
    
    typing_data = TypingIndicator(
        conversation_id=conversation_id,
        user_id=user_id,
        is_typing=is_typing
    )
    
    await manager.handle_typing_indicator(typing_data)

async def handle_join_conversation(user_id: str, data: Dict[str, Any]):
    """Handle joining a conversation"""
    conversation_id = data.get("conversation_id")
    
    if not conversation_id:
        return
    
    conversation = manager.conversations.get(conversation_id)
    if not conversation:
        return
    
    # Add user to online users
    manager.online_users[conversation_id].add(user_id)
    
    # Broadcast user joined
    join_message = WebSocketMessage(
        type="user_joined",
        data={
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user": manager.users[user_id].dict()
        }
    )
    await manager.broadcast_to_conversation(conversation_id, join_message, exclude_user=user_id)

async def handle_leave_conversation(user_id: str, data: Dict[str, Any]):
    """Handle leaving a conversation"""
    conversation_id = data.get("conversation_id")
    
    if not conversation_id:
        return
    
    # Remove user from online users
    manager.online_users[conversation_id].discard(user_id)
    
    # Broadcast user left
    leave_message = WebSocketMessage(
        type="user_left",
        data={
            "conversation_id": conversation_id,
            "user_id": user_id
        }
    )
    await manager.broadcast_to_conversation(conversation_id, leave_message)

# REST API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Chat Messaging API", "version": "1.0.0"}

@app.post("/conversations", response_model=Conversation)
async def create_conversation(
    participant_ids: List[str] = Body(...),
    type: ConversationType = Body(...),
    name: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    creator_id: str = Body(...)
):
    """Create a new conversation"""
    conversation = manager.create_conversation(creator_id, participant_ids, type, name)
    conversation.description = description
    
    # Notify participants
    notification = WebSocketMessage(
        type="conversation_created",
        data=conversation.dict()
    )
    
    for participant_id in participant_ids:
        if participant_id in manager.active_connections:
            await manager.send_personal_message(participant_id, notification)
    
    return conversation

@app.get("/conversations", response_model=List[Conversation])
async def get_conversations(user_id: str = Query(...)):
    """Get user's conversations"""
    user_conversations = []
    for conv_id, conv in manager.conversations.items():
        if user_id in conv.participant_ids:
            user_conversations.append(conv)
    
    return user_conversations

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str, user_id: str = Query(...)):
    """Get conversation details"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@app.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(
    conversation_id: str,
    user_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    before: Optional[datetime] = Query(None)
):
    """Get conversation messages"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = manager.get_conversation_messages(conversation_id, limit, before)
    return messages

@app.post("/conversations/{conversation_id}/messages", response_model=Message)
async def send_message(
    conversation_id: str,
    message_data: Dict[str, Any] = Body(...),
    user_id: str = Body(...)
):
    """Send a message via REST API"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    content = message_data.get("content", "")
    message_type = MessageType(message_data.get("message_type", "text"))
    reply_to = message_data.get("reply_to")
    
    if not content:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=user_id,
        content=content,
        message_type=message_type,
        reply_to=reply_to
    )
    
    # Add message
    manager.add_message(message)
    
    # Broadcast via WebSocket
    message_ws = WebSocketMessage(
        type="new_message",
        data=message.dict()
    )
    await manager.broadcast_to_conversation(conversation_id, message_ws)
    
    return message

@app.put("/messages/{message_id}")
async def edit_message(
    message_id: str,
    content: str = Body(...),
    user_id: str = Body(...)
):
    """Edit a message"""
    # Find message (simplified - in production use database)
    for conv_messages in manager.messages.values():
        for message in conv_messages:
            if message.id == message_id and message.sender_id == user_id:
                message.content = content
                message.edited = True
                message.edited_at = datetime.now()
                
                # Broadcast edit
                edit_ws = WebSocketMessage(
                    type="message_edited",
                    data=message.dict()
                )
                await manager.broadcast_to_conversation(message.conversation_id, edit_ws)
                
                return message
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.delete("/messages/{message_id}")
async def delete_message(message_id: str, user_id: str = Body(...)):
    """Delete a message"""
    for conv_messages in manager.messages.values():
        for message in conv_messages:
            if message.id == message_id and message.sender_id == user_id:
                message.is_deleted = True
                message.deleted_at = datetime.now()
                
                # Broadcast deletion
                delete_ws = WebSocketMessage(
                    type="message_deleted",
                    data={
                        "message_id": message_id,
                        "conversation_id": message.conversation_id
                    }
                )
                await manager.broadcast_to_conversation(message.conversation_id, delete_ws)
                
                return {"message": "Message deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Message not found")

@app.post("/conversations/{conversation_id}/typing")
async def send_typing_indicator(
    conversation_id: str,
    is_typing: bool = Body(...),
    user_id: str = Body(...)
):
    """Send typing indicator"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    typing_data = TypingIndicator(
        conversation_id=conversation_id,
        user_id=user_id,
        is_typing=is_typing
    )
    
    await manager.handle_typing_indicator(typing_data)
    
    return {"message": "Typing indicator sent"}

@app.get("/users", response_model=List[User])
async def get_online_users():
    """Get all online users"""
    online_users = []
    for user_id, user in manager.users.items():
        if user_id in manager.active_connections:
            online_users.append(user)
    
    return online_users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user information"""
    user = manager.users.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: UserStatus = Body(...),
    current_user_id: str = Body(...)
):
    """Update user status"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot update other user's status")
    
    user = manager.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.status = status
    user.last_seen = datetime.now()
    
    # Broadcast status change
    await manager.broadcast_user_status(user_id, status)
    
    return {"message": "Status updated successfully"}

@app.get("/conversations/{conversation_id}/participants")
async def get_conversation_participants(conversation_id: str, user_id: str = Query(...)):
    """Get conversation participants with online status"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    participants = []
    for participant_id in conversation.participant_ids:
        user = manager.users.get(participant_id)
        if user:
            participants.append({
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
                "status": user.status.value,
                "is_online": participant_id in manager.active_connections,
                "is_typing": participant_id in manager.typing_indicators.get(conversation_id, set()),
                "last_seen": user.last_seen.isoformat() if user.last_seen else None
            })
    
    return participants

@app.get("/conversations/{conversation_id}/online-users")
async def get_online_users_in_conversation(conversation_id: str, user_id: str = Query(...)):
    """Get online users in conversation"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    online_user_ids = manager.online_users.get(conversation_id, set())
    online_users = []
    
    for user_id in online_user_ids:
        user = manager.users.get(user_id)
        if user:
            online_users.append({
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
                "status": user.status.value
            })
    
    return online_users

@app.post("/conversations/{conversation_id}/participants")
async def add_participant(
    conversation_id: str,
    participant_id: str = Body(...),
    user_id: str = Body(...)
):
    """Add participant to conversation"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.admin_ids:
        raise HTTPException(status_code=403, detail="Not authorized to add participants")
    
    if participant_id in conversation.participant_ids:
        raise HTTPException(status_code=400, detail="User already in conversation")
    
    conversation.participant_ids.append(participant_id)
    
    # Add to online users if currently connected
    if participant_id in manager.active_connections:
        manager.online_users[conversation_id].add(participant_id)
    
    # Notify participants
    notification = WebSocketMessage(
        type="participant_added",
        data={
            "conversation_id": conversation_id,
            "participant_id": participant_id
        }
    )
    await manager.broadcast_to_conversation(conversation_id, notification)
    
    return {"message": "Participant added successfully"}

@app.delete("/conversations/{conversation_id}/participants/{participant_id}")
async def remove_participant(
    conversation_id: str,
    participant_id: str,
    user_id: str = Body(...)
):
    """Remove participant from conversation"""
    conversation = manager.conversations.get(conversation_id)
    
    if not conversation or user_id not in conversation.admin_ids:
        raise HTTPException(status_code=403, detail="Not authorized to remove participants")
    
    if participant_id not in conversation.participant_ids:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    conversation.participant_ids.remove(participant_id)
    
    # Remove from online users
    manager.online_users[conversation_id].discard(participant_id)
    
    # Notify participants
    notification = WebSocketMessage(
        type="participant_removed",
        data={
            "conversation_id": conversation_id,
            "participant_id": participant_id
        }
    )
    await manager.broadcast_to_conversation(conversation_id, notification)
    
    return {"message": "Participant removed successfully"}

@app.get("/stats")
async def get_stats():
    """Get chat system statistics"""
    total_users = len(manager.users)
    online_users = len(manager.active_connections)
    total_conversations = len(manager.conversations)
    total_messages = sum(len(messages) for messages in manager.messages.values())
    
    return {
        "total_users": total_users,
        "online_users": online_users,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "active_connections": len(manager.active_connections),
        "typing_indicators": sum(len(users) for users in manager.typing_indicators.values())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "active_connections": len(manager.active_connections),
        "total_conversations": len(manager.conversations),
        "online_users": len(manager.active_connections)
    }

# Simple HTML client for testing
@app.get("/client", response_class=HTMLResponse)
async def get_client():
    """Simple chat client for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat API Test Client</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .message { margin: 5px 0; padding: 5px; border-radius: 5px; }
            .sent { background-color: #dcf8c6; margin-left: 20%; }
            .received { background-color: #f1f0f0; margin-right: 20%; }
            .typing { color: #666; font-style: italic; }
            input, button { padding: 10px; margin: 5px; }
            .online-users { border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Chat API Test Client</h1>
            
            <div>
                <input type="text" id="userId" placeholder="Enter your user ID" value="test_user_1">
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
            </div>
            
            <div>
                <input type="text" id="conversationId" placeholder="Conversation ID" value="">
                <button onclick="joinConversation()">Join Conversation</button>
            </div>
            
            <div class="online-users" id="onlineUsers">
                <h3>Online Users</h3>
                <div id="onlineUsersList"></div>
            </div>
            
            <div class="messages" id="messages"></div>
            
            <div class="typing" id="typingIndicator"></div>
            
            <div>
                <input type="text" id="messageInput" placeholder="Type a message..." onkeypress="handleTyping()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let ws = null;
            let currentUserId = '';
            let typingTimer = null;

            function connect() {
                const userId = document.getElementById('userId').value;
                if (!userId) {
                    alert('Please enter a user ID');
                    return;
                }

                currentUserId = userId;
                ws = new WebSocket(`ws://localhost:8008/ws/${userId}`);
                
                ws.onopen = function(event) {
                    console.log('Connected to WebSocket');
                    addMessage('System', 'Connected to chat server', 'system');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                ws.onclose = function(event) {
                    console.log('Disconnected from WebSocket');
                    addMessage('System', 'Disconnected from chat server', 'system');
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }

            function handleWebSocketMessage(data) {
                switch(data.type) {
                    case 'user_data':
                        updateConversations(data.data.conversations);
                        break;
                    case 'new_message':
                        addMessage(data.data.sender_id, data.data.content, 'received');
                        break;
                    case 'typing_indicator':
                        updateTypingIndicator(data.data);
                        break;
                    case 'user_status':
                        updateUserStatus(data.data);
                        break;
                    case 'user_joined':
                        addMessage('System', `${data.data.user.username} joined the conversation`, 'system');
                        break;
                    case 'user_left':
                        addMessage('System', `User left the conversation`, 'system');
                        break;
                }
            }

            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                const conversationId = document.getElementById('conversationId').value;
                
                if (!message || !conversationId || !ws) {
                    return;
                }
                
                ws.send(JSON.stringify({
                    type: 'send_message',
                    data: {
                        conversation_id: conversationId,
                        content: message
                    }
                }));
                
                addMessage(currentUserId, message, 'sent');
                input.value = '';
                
                // Stop typing indicator
                sendTypingIndicator(false);
            }

            function handleTyping() {
                if (typingTimer) {
                    clearTimeout(typingTimer);
                }
                
                sendTypingIndicator(true);
                
                typingTimer = setTimeout(() => {
                    sendTypingIndicator(false);
                }, 1000);
            }

            function sendTypingIndicator(isTyping) {
                const conversationId = document.getElementById('conversationId').value;
                
                if (ws && conversationId) {
                    ws.send(JSON.stringify({
                        type: 'typing',
                        data: {
                            conversation_id: conversationId,
                            is_typing: isTyping
                        }
                    }));
                }
            }

            function joinConversation() {
                const conversationId = document.getElementById('conversationId').value;
                
                if (ws && conversationId) {
                    ws.send(JSON.stringify({
                        type: 'join_conversation',
                        data: {
                            conversation_id: conversationId
                        }
                    }));
                }
            }

            function addMessage(sender, content, type) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function updateTypingIndicator(data) {
                const typingDiv = document.getElementById('typingIndicator');
                if (data.typing_users && data.typing_users.length > 0) {
                    typingDiv.textContent = `${data.typing_users.join(', ')} is typing...`;
                } else {
                    typingDiv.textContent = '';
                }
            }

            function updateConversations(conversations) {
                console.log('Conversations:', conversations);
            }

            function updateUserStatus(data) {
                console.log('User status update:', data);
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
