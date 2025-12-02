from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import asyncio
import uuid
from datetime import datetime

app = FastAPI(title="Real-time Collaboration API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class User(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    cursor_position: Optional[Dict] = None

class Document(BaseModel):
    id: str
    title: str
    content: str
    collaborators: List[str]
    last_modified: datetime

class Operation(BaseModel):
    type: str  # "insert", "delete", "retain"
    position: int
    content: Optional[str] = None
    length: Optional[int] = None
    user_id: str

# In-memory storage
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.document_rooms: Dict[str, List[str]] = {}
        self.users: Dict[str, User] = {}
        self.documents: Dict[str, Document] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        # Remove from all document rooms
        for room_id, users in self.document_rooms.items():
            if user_id in users:
                users.remove(user_id)

    async def join_document(self, user_id: str, document_id: str):
        if document_id not in self.document_rooms:
            self.document_rooms[document_id] = []
        if user_id not in self.document_rooms[document_id]:
            self.document_rooms[document_id].append(user_id)

    async def leave_document(self, user_id: str, document_id: str):
        if document_id in self.document_rooms and user_id in self.document_rooms[document_id]:
            self.document_rooms[document_id].remove(user_id)

    async def broadcast_to_document(self, message: dict, document_id: str, exclude_user: str = None):
        if document_id in self.document_rooms:
            for user_id in self.document_rooms[document_id]:
                if user_id != exclude_user and user_id in self.active_connections:
                    await self.active_connections[user_id].send_text(json.dumps(message))

manager = ConnectionManager()

# REST Endpoints
@app.post("/api/users")
async def create_user(user: User):
    manager.users[user.id] = user
    return {"message": "User created successfully", "user": user}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    if user_id in manager.users:
        return manager.users[user_id]
    return {"error": "User not found"}

@app.post("/api/documents")
async def create_document(document: Document):
    manager.documents[document.id] = document
    return {"message": "Document created successfully", "document": document}

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    if document_id in manager.documents:
        return manager.documents[document_id]
    return {"error": "Document not found"}

@app.get("/api/documents")
async def list_documents():
    return {"documents": list(manager.documents.values())}

# WebSocket endpoints
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "join_document":
                await manager.join_document(user_id, message["document_id"])
                # Notify other users
                await manager.broadcast_to_document({
                    "type": "user_joined",
                    "user": manager.users[user_id].dict() if user_id in manager.users else {"id": user_id}
                }, message["document_id"], exclude_user=user_id)
                
            elif message["type"] == "leave_document":
                await manager.leave_document(user_id, message["document_id"])
                await manager.broadcast_to_document({
                    "type": "user_left",
                    "user_id": user_id
                }, message["document_id"], exclude_user=user_id)
                
            elif message["type"] == "operation":
                # Apply operation to document
                if message["document_id"] in manager.documents:
                    doc = manager.documents[message["document_id"]]
                    # Simple operation application (would need proper OT in production)
                    if message["operation"]["type"] == "insert":
                        doc.content = doc.content[:message["operation"]["position"]] + \
                                     message["operation"]["content"] + \
                                     doc.content[message["operation"]["position"]:]
                    elif message["operation"]["type"] == "delete":
                        doc.content = doc.content[:message["operation"]["position"]] + \
                                     doc.content[message["operation"]["position"] + message["operation"]["length"]:]
                    
                    doc.last_modified = datetime.now()
                    
                    # Broadcast to other users
                    await manager.broadcast_to_document({
                        "type": "operation",
                        "operation": message["operation"],
                        "document_id": message["document_id"],
                        "user_id": user_id
                    }, message["document_id"], exclude_user=user_id)
                    
            elif message["type"] == "cursor_position":
                # Update cursor position
                if user_id in manager.users:
                    manager.users[user_id].cursor_position = message["position"]
                
                # Broadcast cursor position to other users
                await manager.broadcast_to_document({
                    "type": "cursor_update",
                    "user_id": user_id,
                    "position": message["position"]
                }, message["document_id"], exclude_user=user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # Notify all documents that user left
        for document_id in manager.document_rooms:
            if user_id in manager.document_rooms[document_id]:
                await manager.broadcast_to_document({
                    "type": "user_left",
                    "user_id": user_id
                }, document_id)

@app.get("/")
async def root():
    return {"message": "Real-time Collaboration API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
