from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import json
import uuid
import wave
import io
from datetime import datetime, timedelta
import hashlib
import base64

app = FastAPI(title="Voice-to-Text Transcription API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TranscriptionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str = "en"
    model: str = "base"  # "base", "small", "medium", "large"
    format: str = "wav"  # "wav", "mp3", "flac", "m4a"
    timestamps: bool = True
    speakers: bool = False
    profanity_filter: bool = False

class TranscriptionResult(BaseModel):
    id: str
    text: str
    confidence: float
    language: str
    duration: float
    timestamp: datetime
    word_timestamps: Optional[List[Dict]] = None
    speakers: Optional[List[Dict]] = None
    metadata: Dict[str, Any]

class TranscriptionJob(BaseModel):
    id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[TranscriptionResult] = None
    error_message: Optional[str] = None

class Language(BaseModel):
    code: str
    name: str
    supported: bool = True

class Model(BaseModel):
    name: str
    description: str
    accuracy: float
    speed: str  # "fast", "medium", "slow"
    size_mb: int

# In-memory storage
transcription_jobs: Dict[str, TranscriptionJob] = {}
supported_languages: List[Language] = [
    Language(code="en", name="English"),
    Language(code="es", name="Spanish"),
    Language(code="fr", name="French"),
    Language(code="de", name="German"),
    Language(code="it", name="Italian"),
    Language(code="pt", name="Portuguese"),
    Language(code="ru", name="Russian"),
    Language(code="ja", name="Japanese"),
    Language(code="ko", name="Korean"),
    Language(code="zh", name="Chinese")
]

supported_models: List[Model] = [
    Model(name="base", description="Fast, good accuracy", accuracy=0.85, speed="fast", size_mb=142),
    Model(name="small", description="Better accuracy", accuracy=0.90, speed="medium", size_mb=466),
    Model(name="medium", description="High accuracy", accuracy=0.94, speed="medium", size_mb=1420),
    Model(name="large", description="Best accuracy", accuracy=0.97, speed="slow", size_mb=2890)
]

# Utility functions
def generate_job_id() -> str:
    """Generate unique job ID"""
    return f"job_{uuid.uuid4().hex[:8]}"

def decode_base64_audio(base64_data: str) -> bytes:
    """Decode base64 audio data"""
    try:
        # Remove data URL prefix if present
        if base64_data.startswith("data:"):
            base64_data = base64_data.split(",")[1]
        return base64.b64decode(base64_data)
    except Exception as e:
        raise ValueError(f"Invalid base64 audio data: {e}")

def get_audio_duration(audio_data: bytes) -> float:
    """Get audio duration in seconds (mock implementation)"""
    # In production, use librosa or similar to get actual duration
    # For now, estimate based on file size
    estimated_duration = len(audio_data) / 16000  # Rough estimate for 16kHz audio
    return max(1.0, estimated_duration)

def mock_transcription(audio_data: bytes, language: str, model: str) -> Dict:
    """Mock transcription service (replace with real ASR in production)"""
    # Simulate processing time based on model and audio size
    processing_time = len(audio_data) / 100000  # Mock processing delay
    
    # Mock transcription text based on language
    transcriptions = {
        "en": "Hello, this is a sample transcription of the audio file. The speech recognition system has processed this audio and converted it to text.",
        "es": "Hola, esta es una transcripción de muestra del archivo de audio. El sistema de reconocimiento de voz ha procesado este audio y lo ha convertido en texto.",
        "fr": "Bonjour, ceci est une transcription d'exemple du fichier audio. Le système de reconnaissance vocale a traité cet audio et l'a converti en texte.",
        "de": "Hallo, dies ist eine Beispieltranskription der Audiodatei. Das Spracherkennungssystem hat dieses Audio verarbeitet und in Text umgewandelt.",
        "it": "Ciao, questa è una trascrizione di esempio del file audio. Il sistema di riconoscimento vocale ha elaborato questo audio e l'ha convertito in testo."
    }
    
    base_text = transcriptions.get(language, transcriptions["en"])
    
    # Model accuracy affects confidence
    model_accuracy = next((m.accuracy for m in supported_models if m.name == model), 0.85)
    confidence = min(0.99, model_accuracy + (hash(audio_data) % 10) / 100)
    
    # Generate word timestamps
    words = base_text.split()
    word_timestamps = []
    start_time = 0.0
    
    for i, word in enumerate(words):
        word_duration = 0.3 + (hash(word) % 20) / 100  # Variable word duration
        word_timestamps.append({
            "word": word,
            "start": start_time,
            "end": start_time + word_duration,
            "confidence": confidence - (i * 0.01)
        })
        start_time += word_duration
    
    return {
        "text": base_text,
        "confidence": confidence,
        "word_timestamps": word_timestamps,
        "processing_time": processing_time
    }

async def process_transcription_job(job_id: str, request: TranscriptionRequest):
    """Background task to process transcription"""
    job = transcription_jobs[job_id]
    
    try:
        # Update job status
        job.status = "processing"
        job.progress = 0.1
        
        # Decode audio data
        audio_data = decode_base64_audio(request.audio_data)
        job.progress = 0.3
        
        # Get audio duration
        duration = get_audio_duration(audio_data)
        job.progress = 0.5
        
        # Perform transcription (mock service)
        await asyncio.sleep(1)  # Simulate processing time
        transcription_data = mock_transcription(audio_data, request.language, request.model)
        job.progress = 0.8
        
        # Apply profanity filter if requested
        filtered_text = transcription_data["text"]
        if request.profanity_filter:
            # Simple profanity filter (mock implementation)
            profanity_words = ["damn", "hell", "crap"]
            for word in profanity_words:
                filtered_text = filtered_text.replace(word, "***")
        
        # Create transcription result
        result = TranscriptionResult(
            id=job_id,
            text=filtered_text,
            confidence=transcription_data["confidence"],
            language=request.language,
            duration=duration,
            timestamp=datetime.now(),
            word_timestamps=transcription_data["word_timestamps"] if request.timestamps else None,
            metadata={
                "model": request.model,
                "format": request.format,
                "processing_time": transcription_data["processing_time"],
                "original_confidence": transcription_data["confidence"]
            }
        )
        
        # Update job with result
        job.result = result
        job.status = "completed"
        job.progress = 1.0
        job.completed_at = datetime.now()
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.progress = 0.0

# API Endpoints
@app.post("/api/transcribe", response_model=TranscriptionJob)
async def create_transcription(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """Create a new transcription job"""
    job_id = generate_job_id()
    
    job = TranscriptionJob(
        id=job_id,
        status="pending",
        progress=0.0,
        created_at=datetime.now()
    )
    
    transcription_jobs[job_id] = job
    
    # Start background processing
    background_tasks.add_task(process_transcription_job, job_id, request)
    
    return job

@app.post("/api/transcribe/file", response_model=TranscriptionJob)
async def transcribe_file(
    file: UploadFile = File(...),
    language: str = "en",
    model: str = "base",
    timestamps: bool = True,
    speakers: bool = False,
    profanity_filter: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Transcribe uploaded audio file"""
    # Validate file type
    allowed_types = ["audio/wav", "audio/mp3", "audio/flac", "audio/m4a", "audio/x-m4a"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Read file content
    audio_content = await file.read()
    
    # Convert to base64
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    
    # Create transcription request
    request = TranscriptionRequest(
        audio_data=audio_base64,
        language=language,
        model=model,
        format=file.filename.split('.')[-1] if file.filename else "wav",
        timestamps=timestamps,
        speakers=speakers,
        profanity_filter=profanity_filter
    )
    
    return await create_transcription(request, background_tasks)

@app.get("/api/transcribe/{job_id}", response_model=TranscriptionJob)
async def get_transcription_job(job_id: str):
    """Get transcription job status and result"""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    return transcription_jobs[job_id]

@app.get("/api/transcribe/{job_id}/result", response_model=TranscriptionResult)
async def get_transcription_result(job_id: str):
    """Get only the transcription result"""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    job = transcription_jobs[job_id]
    
    if not job.result:
        raise HTTPException(status_code=400, detail="Transcription not completed yet")
    
    return job.result

@app.get("/api/transcribe/{job_id}/text")
async def get_transcription_text(job_id: str):
    """Get only the transcribed text"""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    job = transcription_jobs[job_id]
    
    if not job.result:
        raise HTTPException(status_code=400, detail="Transcription not completed yet")
    
    return {"text": job.result.text}

@app.delete("/api/transcribe/{job_id}")
async def delete_transcription_job(job_id: str):
    """Delete transcription job"""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Transcription job not found")
    
    del transcription_jobs[job_id]
    return {"message": "Transcription job deleted successfully"}

@app.get("/api/jobs", response_model=List[TranscriptionJob])
async def list_transcription_jobs(status: Optional[str] = None, limit: int = 50):
    """List transcription jobs with optional status filter"""
    jobs = list(transcription_jobs.values())
    
    if status:
        jobs = [job for job in jobs if job.status == status]
    
    return sorted(jobs, key=lambda x: x.created_at, reverse=True)[:limit]

@app.get("/api/languages", response_model=List[Language])
async def get_supported_languages():
    """Get list of supported languages"""
    return supported_languages

@app.get("/api/models", response_model=List[Model])
async def get_supported_models():
    """Get list of available transcription models"""
    return supported_models

@app.get("/api/stats")
async def get_transcription_stats():
    """Get transcription service statistics"""
    total_jobs = len(transcription_jobs)
    completed_jobs = len([j for j in transcription_jobs.values() if j.status == "completed"])
    failed_jobs = len([j for j in transcription_jobs.values() if j.status == "failed"])
    processing_jobs = len([j for j in transcription_jobs.values() if j.status == "processing"])
    
    # Calculate average confidence for completed jobs
    completed_results = [j.result for j in transcription_jobs.values() if j.result]
    avg_confidence = sum(r.confidence for r in completed_results) / len(completed_results) if completed_results else 0
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "processing_jobs": processing_jobs,
        "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
        "average_confidence": avg_confidence,
        "supported_languages": len(supported_languages),
        "available_models": len(supported_models),
        "total_audio_duration": sum(r.duration for r in completed_results if r.duration)
    }

@app.post("/api/transcribe/batch", response_model=List[TranscriptionJob])
async def batch_transcribe(
    requests: List[TranscriptionRequest],
    background_tasks: BackgroundTasks
):
    """Create multiple transcription jobs"""
    jobs = []
    
    for request in requests:
        job = await create_transcription(request, background_tasks)
        jobs.append(job)
    
    return jobs

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "active_jobs": len([j for j in transcription_jobs.values() if j.status == "processing"]),
        "service_version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "Voice-to-Text Transcription API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
