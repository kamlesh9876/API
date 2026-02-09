# Voice Transcription API

An async voice-to-text transcription API with job-based processing, file uploads, language and model selection, and optional word timestamps. This implementation uses a mock transcription engine for demo and testing purposes.

## Features
- Job-based transcription with progress tracking
- JSON (base64) and multipart file upload inputs
- Multiple languages and model sizes
- Optional word timestamps and profanity filtering
- Batch transcription requests
- Job management endpoints and stats
- Health check endpoint

## Technology Stack
- FastAPI (Python)
- Pydantic models for validation
- Async background tasks

## Prerequisites
- Python 3.8+
- pip package manager

## Quick Setup
1. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

2. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:8000`.

## API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Create Transcription Job (Base64)
```http
POST /api/transcribe
Content-Type: application/json

{
  "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=",
  "language": "en",
  "model": "base",
  "format": "wav",
  "timestamps": true,
  "speakers": false,
  "profanity_filter": false
}
```

Response:
```json
{
  "id": "job_a1b2c3d4",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2024-01-15T12:00:00",
  "completed_at": null,
  "result": null,
  "error_message": null
}
```

### Create Transcription Job (File Upload)
```http
POST /api/transcribe/file
Content-Type: multipart/form-data

file: [audio file]
language: en
model: base
timestamps: true
speakers: false
profanity_filter: false
```

### Get Job Status
```http
GET /api/transcribe/{job_id}
```

### Get Transcription Result
```http
GET /api/transcribe/{job_id}/result
```

### Get Transcribed Text Only
```http
GET /api/transcribe/{job_id}/text
```

### Delete Job
```http
DELETE /api/transcribe/{job_id}
```

### Batch Transcription
```http
POST /api/transcribe/batch
Content-Type: application/json

[
  {
    "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=",
    "language": "en",
    "model": "base",
    "format": "wav",
    "timestamps": true,
    "speakers": false,
    "profanity_filter": false
  },
  {
    "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=",
    "language": "es",
    "model": "small",
    "format": "wav",
    "timestamps": false,
    "speakers": false,
    "profanity_filter": true
  }
]
```

### List Jobs
```http
GET /api/jobs?status=completed&limit=50
```

### Supported Languages
```http
GET /api/languages
```

### Supported Models
```http
GET /api/models
```

### Service Stats
```http
GET /api/stats
```

### Health Check
```http
GET /api/health
```

## Usage Examples

### Python (requests)
```python
import base64
import requests

audio_bytes = b"RIFF...."  # read your audio file here
audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

payload = {
    "audio_data": audio_b64,
    "language": "en",
    "model": "base",
    "format": "wav",
    "timestamps": True,
    "speakers": False,
    "profanity_filter": False
}

resp = requests.post("http://localhost:8000/api/transcribe", json=payload)
job = resp.json()

job_id = job["id"]
result = requests.get(f"http://localhost:8000/api/transcribe/{job_id}/result").json()
print(result["text"])
```

### JavaScript (fetch)
```javascript
const audioBytes = new Uint8Array([82, 73, 70, 70]); // replace with real bytes
const audioB64 = btoa(String.fromCharCode(...audioBytes));

const payload = {
  audio_data: audioB64,
  language: "en",
  model: "base",
  format: "wav",
  timestamps: true,
  speakers: false,
  profanity_filter: false
};

const jobResp = await fetch("http://localhost:8000/api/transcribe", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});
const job = await jobResp.json();

const resultResp = await fetch(`http://localhost:8000/api/transcribe/${job.id}/result`);
const result = await resultResp.json();
console.log(result.text);
```

## Data Models

### TranscriptionRequest
```json
{
  "audio_data": "base64-encoded-audio",
  "language": "en",
  "model": "base",
  "format": "wav",
  "timestamps": true,
  "speakers": false,
  "profanity_filter": false
}
```

### TranscriptionJob
```json
{
  "id": "job_a1b2c3d4",
  "status": "completed",
  "progress": 1.0,
  "created_at": "2024-01-15T12:00:00",
  "completed_at": "2024-01-15T12:00:02",
  "result": {
    "id": "job_a1b2c3d4",
    "text": "Hello, this is a sample transcription of the audio file.",
    "confidence": 0.91,
    "language": "en",
    "duration": 3.2,
    "timestamp": "2024-01-15T12:00:02",
    "word_timestamps": [
      { "word": "Hello,", "start": 0.0, "end": 0.32, "confidence": 0.91 }
    ],
    "speakers": null,
    "metadata": {
      "model": "base",
      "format": "wav",
      "processing_time": 0.12,
      "original_confidence": 0.91
    }
  },
  "error_message": null
}
```

### TranscriptionResult
```json
{
  "id": "job_a1b2c3d4",
  "text": "Hello, this is a sample transcription of the audio file.",
  "confidence": 0.91,
  "language": "en",
  "duration": 3.2,
  "timestamp": "2024-01-15T12:00:02",
  "word_timestamps": [
    { "word": "Hello,", "start": 0.0, "end": 0.32, "confidence": 0.91 }
  ],
  "speakers": null,
  "metadata": {
    "model": "base",
    "format": "wav",
    "processing_time": 0.12,
    "original_confidence": 0.91
  }
}
```

### Language
```json
{
  "code": "en",
  "name": "English",
  "supported": true
}
```

### Model
```json
{
  "name": "base",
  "description": "Fast, good accuracy",
  "accuracy": 0.85,
  "speed": "fast",
  "size_mb": 142
}
```

## Environment Variables
- `HOST`: Server host (default `0.0.0.0`)
- `PORT`: Server port (default `8000`)
- `DEBUG`: Enable debug mode
- `RELOAD`: Auto-reload on changes
- `ALLOWED_ORIGINS`: CORS allowed origins (use `*` for all)
- `SUPPORTED_AUDIO_FORMATS`: Comma-separated audio formats
- `MAX_AUDIO_SIZE_MB`: Max upload size
- `MAX_AUDIO_DURATION_SECONDS`: Max audio duration
- `DEFAULT_LANGUAGE`: Default language code
- `DEFAULT_MODEL`: Default model size
- `ENABLE_TIMESTAMPS`: Enable word timestamps by default
- `ENABLE_SPEAKER_DIARIZATION`: Enable speaker diarization (stub)
- `ENABLE_PROFANITY_FILTER`: Enable profanity filtering
- `MAX_CONCURRENT_JOBS`: Max concurrent jobs
- `JOB_RETENTION_HOURS`: Retention window for completed jobs
- `LOG_LEVEL`: Logging level
- `LOG_FILE`: Log file path

## Use Cases
- Customer support call transcription
- Podcast and meeting notes generation
- Voice memo to text
- Accessibility features for audio content
- Multilingual transcription workflows

## Integration Notes
- For production, replace the mock transcription with a real ASR engine.
- Consider persisting jobs and results in a database for durability.
- Enable authentication and rate limiting when exposing publicly.

## Notes
- Transcription is mocked for demo purposes; replace `mock_transcription` with a real ASR engine for production.
- Jobs are stored in memory and will be lost on restart.
- Speaker diarization is included in the schema but not implemented.
