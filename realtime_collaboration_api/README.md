# Real-time Collaboration API

A WebSocket-based API for real-time document collaboration with cursor tracking, operational transformations, and user presence.

## Features

- **Real-time Document Editing**: Multiple users can edit documents simultaneously
- **Cursor Tracking**: See other users' cursor positions in real-time
- **User Presence**: Shows who's currently viewing/editing a document
- **WebSocket Communication**: Low-latency bidirectional communication
- **Operational Transformations**: Basic conflict resolution for concurrent edits
- **Document Management**: Create, read, and manage collaborative documents

## API Endpoints

### REST Endpoints

#### Users
- `POST /api/users` - Create a new user
- `GET /api/users/{user_id}` - Get user information

#### Documents
- `POST /api/documents` - Create a new document
- `GET /api/documents/{document_id}` - Get document details
- `GET /api/documents` - List all documents

### WebSocket Endpoint

#### Connection
- `WS /ws/{user_id}` - WebSocket connection for real-time updates

#### WebSocket Messages

**Join Document**
```json
{
  "type": "join_document",
  "document_id": "doc_123"
}
```

**Leave Document**
```json
{
  "type": "leave_document",
  "document_id": "doc_123"
}
```

**Send Operation**
```json
{
  "type": "operation",
  "document_id": "doc_123",
  "operation": {
    "type": "insert",
    "position": 10,
    "content": "Hello World"
  }
}
```

**Update Cursor Position**
```json
{
  "type": "cursor_position",
  "document_id": "doc_123",
  "position": {
    "line": 5,
    "column": 10
  }
}
```

## Installation

```bash
pip install fastapi uvicorn websockets
```

## Usage

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Example Usage

### JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onopen = () => {
  // Join a document
  ws.send(JSON.stringify({
    type: 'join_document',
    document_id: 'doc_123'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

// Send an operation
ws.send(JSON.stringify({
  type: 'operation',
  document_id: 'doc_123',
  operation: {
    type: 'insert',
    position: 0,
    content: 'Hello'
  }
}));
```

## Data Models

### User
```json
{
  "id": "string",
  "name": "string",
  "avatar": "string (optional)",
  "cursor_position": "object (optional)"
}
```

### Document
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "collaborators": ["string"],
  "last_modified": "datetime"
}
```

### Operation
```json
{
  "type": "insert|delete|retain",
  "position": "number",
  "content": "string (optional)",
  "length": "number (optional)",
  "user_id": "string"
}
```

## Use Cases

- **Collaborative Code Editors**: Real-time code editing like VS Code Live Share
- **Document Collaboration**: Google Docs-like editing experience
- **Whiteboard Applications**: Real-time drawing and annotation
- **Chat Applications**: Live messaging with typing indicators
- **Gaming**: Real-time multiplayer game state synchronization

## Production Considerations

For production use, consider:
- Implementing proper Operational Transformation algorithms
- Adding authentication and authorization
- Scaling with Redis for multi-server deployments
- Adding persistence with a database
- Implementing proper error handling and reconnection logic
- Adding rate limiting and security measures
