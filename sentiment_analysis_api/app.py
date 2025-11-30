from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import asyncio
import logging
import re
import string
import math
from collections import Counter, defaultdict
import sqlite3
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
import secrets
import hashlib

# NLP and ML imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from transformers import Pipeline
    import torch
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Using fallback sentiment analysis.")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Using basic text processing.")

app = FastAPI(
    title="Sentiment Analysis API",
    description="Advanced sentiment analysis with emotion tagging and confidence scores using NLP and HuggingFace models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///sentiment_analysis.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class EmotionTag(str, Enum):
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class AnalysisType(str, Enum):
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    COMPREHENSIVE = "comprehensive"

# SQLAlchemy Models
class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    input_text = Column(Text, nullable=False)
    sentiment_label = Column(String, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    emotion_tags = Column(Text)  # JSON string of emotion tags
    emotion_scores = Column(Text)  # JSON string of emotion scores
    processing_time_ms = Column(Integer)
    model_used = Column(String)
    analysis_type = Column(String, default=AnalysisType.COMPREHENSIVE)
    language_detected = Column(String)
    word_count = Column(Integer)
    sentence_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(Text)

class ModelPerformance(Base):
    __tablename__ = "model_performance"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String, nullable=False)
    accuracy_score = Column(Float)
    precision_score = Column(Float)
    recall_score = Column(Float)
    f1_score = Column(Float)
    total_analyses = Column(Integer, default=0)
    average_processing_time_ms = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

class BatchAnalysis(Base):
    __tablename__ = "batch_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, nullable=False, index=True)
    input_text = Column(Text, nullable=False)
    sentiment_label = Column(String, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    emotion_tags = Column(Text)
    emotion_scores = Column(Text)
    processing_time_ms = Column(Integer)
    status = Column(String, default="completed")  # completed, failed, pending
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    language: Optional[str] = Field("auto", regex=r'^(auto|en|es|fr|de|it|pt|ru|ja|zh|ar)$')
    analysis_type: AnalysisType = Field(AnalysisType.COMPREHENSIVE)
    include_emotions: bool = Field(True)
    include_confidence: bool = Field(True)
    include_statistics: bool = Field(False)

class BatchTextInput(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    language: Optional[str] = Field("auto", regex=r'^(auto|en|es|fr|de|it|pt|ru|ja|zh|ar)$')
    analysis_type: AnalysisType = Field(AnalysisType.COMPREHENSIVE)
    include_emotions: bool = Field(True)
    include_confidence: bool = Field(True)
    include_statistics: bool = Field(False)

class SentimentResult(BaseModel):
    sentiment: SentimentLabel
    confidence: float = Field(..., ge=0.0, le=1.0)
    score: float = Field(..., ge=-1.0, le=1.0)

class EmotionResult(BaseModel):
    emotion: EmotionTag
    confidence: float = Field(..., ge=0.0, le=1.0)
    intensity: float = Field(..., ge=0.0, le=1.0)

class AnalysisResponse(BaseModel):
    id: str
    input_text: str
    sentiment: SentimentResult
    emotions: Optional[List[EmotionResult]]
    confidence: float
    processing_time_ms: int
    model_used: str
    language_detected: Optional[str]
    statistics: Optional[Dict[str, Any]]
    created_at: datetime

class BatchAnalysisResponse(BaseModel):
    batch_id: str
    results: List[AnalysisResponse]
    total_processed: int
    total_failed: int
    total_processing_time_ms: int
    created_at: datetime

class ModelInfo(BaseModel):
    name: str
    type: str
    description: str
    accuracy: Optional[float]
    languages_supported: List[str]
    processing_speed: str
    last_updated: datetime

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    models_loaded: List[str]
    database_status: str
    memory_usage_mb: Optional[float]

# NLP Models and Utilities
class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self.vader_analyzer = None
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """Load NLP models"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Load sentiment analysis model
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Loaded sentiment analysis model: cardiffnlp/twitter-roberta-base-sentiment-latest")
                
                # Load emotion classification model
                self.emotion_pipeline = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Loaded emotion classification model: j-hartmann/emotion-english-distilroberta-base")
            
            if NLTK_AVAILABLE:
                # Download required NLTK data
                try:
                    nltk.data.find('tokenizers/punkt')
                except LookupError:
                    nltk.download('punkt')
                
                try:
                    nltk.data.find('corpora/stopwords')
                except LookupError:
                    nltk.download('stopwords')
                
                try:
                    nltk.data.find('sentiment/vader_lexicon.zip')
                except LookupError:
                    nltk.download('vader_lexicon')
                
                self.vader_analyzer = SentimentIntensityAnalyzer()
                logger.info("Loaded NLTK VADER sentiment analyzer")
            
            self.models_loaded = True
            logger.info("All NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.models_loaded = False
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)
        
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        # This is a simplified language detection
        # In production, use a proper language detection library
        
        # Check for common language patterns
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return 'ja'
        elif re.search(r'[\u0600-\u06ff]', text):
            return 'ar'
        elif re.search(r'[а-яА-Я]', text):
            return 'ru'
        elif re.search(r'[àáâãäåæçèéêëìíîïñòóôõöùúûüýÿ]', text):
            # Could be French, Spanish, Italian, Portuguese, German
            if re.search(r'[ß]', text):
                return 'de'
            elif re.search(r'[ñ]', text):
                return 'es'
            elif re.search(r'[ç]', text):
                return 'fr'
            else:
                return 'it'
        else:
            return 'en'
    
    def analyze_sentiment_transformers(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Transformers models"""
        if not self.sentiment_pipeline:
            raise Exception("Sentiment model not loaded")
        
        result = self.sentiment_pipeline(text)
        
        # Map model labels to our standard labels
        label_mapping = {
            'LABEL_0': 'negative',
            'LABEL_1': 'neutral', 
            'LABEL_2': 'positive',
            'NEGATIVE': 'negative',
            'NEUTRAL': 'neutral',
            'POSITIVE': 'positive'
        }
        
        label = result[0]['label']
        sentiment = label_mapping.get(label, label.lower())
        score = result[0]['score']
        
        # Convert to -1 to 1 scale
        if sentiment == 'positive':
            score_normalized = score
        elif sentiment == 'negative':
            score_normalized = -score
        else:
            score_normalized = 0.0
        
        return {
            'sentiment': SentimentLabel(sentiment),
            'confidence': score,
            'score': score_normalized
        }
    
    def analyze_sentiment_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER"""
        if not self.vader_analyzer:
            raise Exception("VADER analyzer not loaded")
        
        scores = self.vader_analyzer.polarity_scores(text)
        
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': SentimentLabel(sentiment),
            'confidence': abs(compound),
            'score': compound
        }
    
    def analyze_emotions_transformers(self, text: str) -> Dict[str, Any]:
        """Analyze emotions using Transformers models"""
        if not self.emotion_pipeline:
            raise Exception("Emotion model not loaded")
        
        result = self.emotion_pipeline(text)
        
        emotions = []
        for item in result:
            emotion_label = item['label'].lower()
            confidence = item['score']
            
            # Map to our emotion tags
            emotion_mapping = {
                'joy': EmotionTag.JOY,
                'anger': EmotionTag.ANGER,
                'fear': EmotionTag.FEAR,
                'sadness': EmotionTag.SADNESS,
                'surprise': EmotionTag.SURPRISE,
                'disgust': EmotionTag.DISGUST,
                'trust': EmotionTag.TRUST,
                'anticipation': EmotionTag.ANTICIPATION
            }
            
            emotion = emotion_mapping.get(emotion_label, emotion_label)
            if isinstance(emotion, str):
                emotion = EmotionTag(emotion) if emotion in EmotionTag else EmotionTag.JOY
            
            emotions.append({
                'emotion': emotion,
                'confidence': confidence,
                'intensity': confidence
            })
        
        return {'emotions': emotions}
    
    def analyze_emotions_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze emotions using keyword-based approach"""
        # Emotion keyword dictionaries
        emotion_keywords = {
            EmotionTag.JOY: ['happy', 'joy', 'excited', 'delighted', 'pleased', 'glad', 'cheerful', 'merry', 'elated'],
            EmotionTag.ANGER: ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'rage', 'outraged'],
            EmotionTag.FEAR: ['afraid', 'scared', 'fearful', 'terrified', 'anxious', 'worried', 'nervous', 'panic'],
            EmotionTag.SADNESS: ['sad', 'unhappy', 'depressed', 'miserable', 'sorrowful', 'grief', 'melancholy'],
            EmotionTag.SURPRISE: ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'bewildered'],
            EmotionTag.DISGUST: ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated'],
            EmotionTag.TRUST: ['trust', 'believe', 'confident', 'rely', 'depend', 'faith'],
            EmotionTag.ANTICIPATION: ['anticipate', 'expect', 'look forward', 'eager', 'hopeful', 'excited']
        }
        
        text_lower = text.lower()
        words = word_tokenize(text_lower) if NLTK_AVAILABLE else text_lower.split()
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = 0
            for word in words:
                if word in keywords:
                    score += 1
            emotion_scores[emotion] = score / len(words) if words else 0
        
        emotions = []
        for emotion, score in emotion_scores.items():
            if score > 0:
                emotions.append({
                    'emotion': emotion,
                    'confidence': min(score * 2, 1.0),  # Scale confidence
                    'intensity': score
                })
        
        return {'emotions': emotions}
    
    def analyze_text(self, text: str, analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE, 
                   include_emotions: bool = True, include_confidence: bool = True) -> Dict[str, Any]:
        """Main analysis function"""
        start_time = datetime.utcnow()
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Detect language
        language = self.detect_language(processed_text)
        
        # Sentiment analysis
        sentiment_result = None
        model_used = "fallback"
        
        if self.models_loaded and TRANSFORMERS_AVAILABLE and language == 'en':
            try:
                sentiment_result = self.analyze_sentiment_transformers(processed_text)
                model_used = "transformers"
            except Exception as e:
                logger.error(f"Transformers sentiment analysis failed: {e}")
        
        if sentiment_result is None and self.models_loaded and NLTK_AVAILABLE:
            try:
                sentiment_result = self.analyze_sentiment_vader(processed_text)
                model_used = "vader"
            except Exception as e:
                logger.error(f"VADER sentiment analysis failed: {e}")
        
        if sentiment_result is None:
            # Fallback basic sentiment analysis
            sentiment_result = self._basic_sentiment_analysis(processed_text)
            model_used = "basic"
        
        # Emotion analysis
        emotions_result = None
        if include_emotions and analysis_type in [AnalysisType.EMOTION, AnalysisType.COMPREHENSIVE]:
            if self.models_loaded and TRANSFORMERS_AVAILABLE and language == 'en':
                try:
                    emotions_result = self.analyze_emotions_transformers(processed_text)
                except Exception as e:
                    logger.error(f"Transformers emotion analysis failed: {e}")
                    emotions_result = self.analyze_emotions_keywords(processed_text)
            else:
                emotions_result = self.analyze_emotions_keywords(processed_text)
        
        # Calculate processing time
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Calculate text statistics
        word_count = len(processed_text.split())
        sentence_count = len(sent_tokenize(processed_text)) if NLTK_AVAILABLE else processed_text.count('.') + processed_text.count('!') + processed_text.count('?')
        
        result = {
            'sentiment': sentiment_result,
            'emotions': emotions_result.get('emotions') if emotions_result else None,
            'language_detected': language,
            'model_used': model_used,
            'processing_time_ms': processing_time,
            'word_count': word_count,
            'sentence_count': sentence_count
        }
        
        if include_confidence:
            result['confidence'] = sentiment_result.get('confidence', 0.5)
        
        return result
    
    def _basic_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis using simple word lists"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'pleased']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'disappointed']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return {
                'sentiment': SentimentLabel.NEUTRAL,
                'confidence': 0.5,
                'score': 0.0
            }
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            score = positive_ratio
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            score = -negative_ratio
        else:
            sentiment = 'neutral'
            score = 0.0
        
        confidence = max(positive_ratio, negative_ratio) * 2  # Scale confidence
        
        return {
            'sentiment': SentimentLabel(sentiment),
            'confidence': min(confidence, 1.0),
            'score': score
        }

# Initialize analyzer
analyzer = SentimentAnalyzer()

# Utility Functions
def calculate_text_statistics(text: str) -> Dict[str, Any]:
    """Calculate detailed text statistics"""
    words = text.split()
    sentences = text.split('.') + text.split('!') + text.split('?')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Character statistics
    char_count = len(text)
    char_count_no_spaces = len(text.replace(' ', ''))
    
    # Word statistics
    word_count = len(words)
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    # Sentence statistics
    sentence_count = len(sentences)
    avg_sentence_length = sum(len(sent.split()) for sent in sentences) / sentence_count if sentence_count > 0 else 0
    
    # Readability metrics (simplified)
    if NLTK_AVAILABLE:
        # Count complex words (more than 6 characters)
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_word_ratio = complex_words / word_count if word_count > 0 else 0
    else:
        complex_word_ratio = 0
    
    return {
        'char_count': char_count,
        'char_count_no_spaces': char_count_no_spaces,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_word_length': round(avg_word_length, 2),
        'avg_sentence_length': round(avg_sentence_length, 2),
        'complex_word_ratio': round(complex_word_ratio, 2)
    }

def save_analysis_to_db(analysis_data: Dict[str, Any], input_text: str, db: Session, 
                       ip_address: str = None, user_agent: str = None) -> Analysis:
    """Save analysis to database"""
    analysis = Analysis(
        input_text=input_text,
        sentiment_label=analysis_data['sentiment']['sentiment'].value,
        sentiment_score=analysis_data['sentiment'].get('score', 0.0),
        confidence_score=analysis_data.get('confidence', 0.0),
        emotion_tags=json.dumps(analysis_data.get('emotions', [])),
        emotion_scores=json.dumps(analysis_data.get('emotions', [])),
        processing_time_ms=analysis_data.get('processing_time_ms', 0),
        model_used=analysis_data.get('model_used', 'unknown'),
        language_detected=analysis_data.get('language_detected'),
        word_count=analysis_data.get('word_count', 0),
        sentence_count=analysis_data.get('sentence_count', 0),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sentiment Analysis API",
        "version": "1.0.0",
        "features": [
            "Sentiment analysis (positive/negative/neutral)",
            "Emotion tagging (joy, anger, fear, etc.)",
            "Confidence scores",
            "Multiple NLP models",
            "Batch processing"
        ],
        "models_loaded": analyzer.models_loaded
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(
    text_input: TextInput,
    request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze text sentiment and emotions"""
    try:
        # Perform analysis
        analysis_data = analyzer.analyze_text(
            text=text_input.text,
            analysis_type=text_input.analysis_type,
            include_emotions=text_input.include_emotions,
            include_confidence=text_input.include_confidence
        )
        
        # Calculate statistics if requested
        statistics = None
        if text_input.include_statistics:
            statistics = calculate_text_statistics(text_input.text)
        
        # Save to database in background
        background_tasks.add_task(
            save_analysis_to_db,
            analysis_data,
            text_input.text,
            db,
            request.client.host if request else None,
            request.headers.get("user-agent") if request else None
        )
        
        # Build response
        response = AnalysisResponse(
            id=str(uuid.uuid4()),
            input_text=text_input.text,
            sentiment=SentimentResult(
                sentiment=analysis_data['sentiment']['sentiment'],
                confidence=analysis_data['sentiment'].get('confidence', 0.0),
                score=analysis_data['sentiment'].get('score', 0.0)
            ),
            emotions=[
                EmotionResult(
                    emotion=emotion['emotion'],
                    confidence=emotion['confidence'],
                    intensity=emotion['intensity']
                )
                for emotion in (analysis_data.get('emotions') or [])
            ],
            confidence=analysis_data.get('confidence', 0.0),
            processing_time_ms=analysis_data.get('processing_time_ms', 0),
            model_used=analysis_data.get('model_used', 'unknown'),
            language_detected=analysis_data.get('language_detected'),
            statistics=statistics,
            created_at=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(
    batch_input: BatchTextInput,
    request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze multiple texts in batch"""
    try:
        batch_id = str(uuid.uuid4())
        results = []
        total_processing_time = 0
        total_failed = 0
        
        for i, text in enumerate(batch_input.texts):
            try:
                # Perform analysis
                analysis_data = analyzer.analyze_text(
                    text=text,
                    analysis_type=batch_input.analysis_type,
                    include_emotions=batch_input.include_emotions,
                    include_confidence=batch_input.include_confidence
                )
                
                # Calculate statistics if requested
                statistics = None
                if batch_input.include_statistics:
                    statistics = calculate_text_statistics(text)
                
                total_processing_time += analysis_data.get('processing_time_ms', 0)
                
                # Build response
                response = AnalysisResponse(
                    id=str(uuid.uuid4()),
                    input_text=text,
                    sentiment=SentimentResult(
                        sentiment=analysis_data['sentiment']['sentiment'],
                        confidence=analysis_data['sentiment'].get('confidence', 0.0),
                        score=analysis_data['sentiment'].get('score', 0.0)
                    ),
                    emotions=[
                        EmotionResult(
                            emotion=emotion['emotion'],
                            confidence=emotion['confidence'],
                            intensity=emotion['intensity']
                        )
                        for emotion in (analysis_data.get('emotions') or [])
                    ],
                    confidence=analysis_data.get('confidence', 0.0),
                    processing_time_ms=analysis_data.get('processing_time_ms', 0),
                    model_used=analysis_data.get('model_used', 'unknown'),
                    language_detected=analysis_data.get('language_detected'),
                    statistics=statistics,
                    created_at=datetime.utcnow()
                )
                
                results.append(response)
                
                # Save to database in background
                background_tasks.add_task(
                    save_batch_analysis_to_db,
                    batch_id,
                    text,
                    analysis_data,
                    db,
                    request.client.host if request else None,
                    request.headers.get("user-agent") if request else None
                )
                
            except Exception as e:
                logger.error(f"Batch item {i} analysis failed: {e}")
                total_failed += 1
                # Continue processing other items
        
        return BatchAnalysisResponse(
            batch_id=batch_id,
            results=results,
            total_processed=len(results),
            total_failed=total_failed,
            total_processing_time_ms=total_processing_time,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Batch analysis failed")

def save_batch_analysis_to_db(batch_id: str, text: str, analysis_data: Dict[str, Any], 
                             db: Session, ip_address: str = None, user_agent: str = None):
    """Save batch analysis to database"""
    try:
        batch_analysis = BatchAnalysis(
            batch_id=batch_id,
            input_text=text,
            sentiment_label=analysis_data['sentiment']['sentiment'].value,
            sentiment_score=analysis_data['sentiment'].get('score', 0.0),
            confidence_score=analysis_data.get('confidence', 0.0),
            emotion_tags=json.dumps(analysis_data.get('emotions', [])),
            emotion_scores=json.dumps(analysis_data.get('emotions', [])),
            processing_time_ms=analysis_data.get('processing_time_ms', 0),
            status="completed"
        )
        
        db.add(batch_analysis)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to save batch analysis: {e}")

@app.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """Get information about available models"""
    models = []
    
    if TRANSFORMERS_AVAILABLE and analyzer.sentiment_pipeline:
        models.append(ModelInfo(
            name="Twitter RoBERTa Sentiment",
            type="transformers",
            description="RoBERTa-based sentiment analysis model trained on Twitter data",
            accuracy=0.85,  # Approximate accuracy
            languages_supported=["en"],
            processing_speed="medium",
            last_updated=datetime.utcnow()
        ))
    
    if TRANSFORMERS_AVAILABLE and analyzer.emotion_pipeline:
        models.append(ModelInfo(
            name="DistilRoBERTa Emotion",
            type="transformers",
            description="DistilRoBERTa-based emotion classification model",
            accuracy=0.82,  # Approximate accuracy
            languages_supported=["en"],
            processing_speed="fast",
            last_updated=datetime.utcnow()
        ))
    
    if NLTK_AVAILABLE and analyzer.vader_analyzer:
        models.append(ModelInfo(
            name="VADER Sentiment",
            type="rule-based",
            description="VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis",
            accuracy=0.75,  # Approximate accuracy
            languages_supported=["en"],
            processing_speed="very_fast",
            last_updated=datetime.utcnow()
        ))
    
    models.append(ModelInfo(
        name="Basic Sentiment",
        type="keyword-based",
        description="Simple keyword-based sentiment analysis (fallback)",
        accuracy=0.60,  # Approximate accuracy
        languages_supported=["en", "es", "fr", "de", "it", "pt"],
        processing_speed="very_fast",
        last_updated=datetime.utcnow()
    ))
    
    return models

@app.get("/statistics")
async def get_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get analysis statistics"""
    try:
        # Date filter
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total analyses
        total_analyses = db.query(Analysis).filter(Analysis.created_at >= start_date).count()
        
        # Sentiment distribution
        sentiment_stats = db.query(
            Analysis.sentiment_label,
            func.count(Analysis.id).label('count')
        ).filter(Analysis.created_at >= start_date).group_by(Analysis.sentiment_label).all()
        
        sentiment_distribution = {
            stat.sentiment_label: stat.count for stat in sentiment_stats
        }
        
        # Average processing time
        avg_processing_time = db.query(func.avg(Analysis.processing_time_ms)).filter(
            Analysis.created_at >= start_date
        ).scalar() or 0
        
        # Model usage
        model_stats = db.query(
            Analysis.model_used,
            func.count(Analysis.id).label('count')
        ).filter(Analysis.created_at >= start_date).group_by(Analysis.model_used).all()
        
        model_usage = {
            stat.model_used: stat.count for stat in model_stats
        }
        
        # Language distribution
        language_stats = db.query(
            Analysis.language_detected,
            func.count(Analysis.id).label('count')
        ).filter(Analysis.created_at >= start_date).group_by(Analysis.language_detected).all()
        
        language_distribution = {
            stat.language_detected: stat.count for stat in language_stats
        }
        
        return {
            "period_days": days,
            "total_analyses": total_analyses,
            "sentiment_distribution": sentiment_distribution,
            "average_processing_time_ms": round(avg_processing_time, 2),
            "model_usage": model_usage,
            "language_distribution": language_distribution,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@app.get("/history", response_model=List[AnalysisResponse])
async def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sentiment_filter: Optional[SentimentLabel] = Query(None),
    model_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get analysis history"""
    try:
        query = db.query(Analysis)
        
        if sentiment_filter:
            query = query.filter(Analysis.sentiment_label == sentiment_filter.value)
        
        if model_filter:
            query = query.filter(Analysis.model_used == model_filter)
        
        analyses = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
        
        results = []
        for analysis in analyses:
            # Parse emotions
            emotions = []
            if analysis.emotion_tags:
                try:
                    emotion_data = json.loads(analysis.emotion_tags)
                    for emotion in emotion_data:
                        emotions.append(EmotionResult(
                            emotion=emotion['emotion'],
                            confidence=emotion['confidence'],
                            intensity=emotion['intensity']
                        ))
                except json.JSONDecodeError:
                    pass
            
            result = AnalysisResponse(
                id=analysis.id,
                input_text=analysis.input_text,
                sentiment=SentimentResult(
                    sentiment=SentimentLabel(analysis.sentiment_label),
                    confidence=analysis.confidence_score,
                    score=analysis.sentiment_score
                ),
                emotions=emotions,
                confidence=analysis.confidence_score,
                processing_time_ms=analysis.processing_time_ms,
                model_used=analysis.model_used,
                language_detected=analysis.language_detected,
                statistics=None,
                created_at=analysis.created_at
            )
            
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"History retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Check memory usage (simplified)
    try:
        import psutil
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        memory_usage = None
    
    # Get loaded models
    loaded_models = []
    if TRANSFORMERS_AVAILABLE and analyzer.sentiment_pipeline:
        loaded_models.append("sentiment_transformers")
    if TRANSFORMERS_AVAILABLE and analyzer.emotion_pipeline:
        loaded_models.append("emotion_transformers")
    if NLTK_AVAILABLE and analyzer.vader_analyzer:
        loaded_models.append("vader")
    loaded_models.append("basic")
    
    return HealthCheck(
        status="healthy" if db_status == "healthy" and analyzer.models_loaded else "degraded",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        models_loaded=loaded_models,
        database_status=db_status,
        memory_usage_mb=memory_usage
    )

# Utility Endpoints
@app.get("/emotions")
async def get_emotion_list():
    """Get list of supported emotions"""
    return {
        "emotions": [
            {"name": emotion.value, "description": get_emotion_description(emotion)}
            for emotion in EmotionTag
        ]
    }

def get_emotion_description(emotion: EmotionTag) -> str:
    """Get emotion description"""
    descriptions = {
        EmotionTag.JOY: "Feeling of great pleasure and happiness",
        EmotionTag.ANGER: "Strong feeling of annoyance, displeasure, or hostility",
        EmotionTag.FEAR: "An unpleasant emotion caused by threat or danger",
        EmotionTag.SADNESS: "Emotional pain associated with feelings of disadvantage, loss, despair, or helplessness",
        EmotionTag.SURPRISE: "A brief emotional state experienced as the result of an unexpected event",
        EmotionTag.DISGUST: "Emotional response of revulsion to something potentially offensive",
        EmotionTag.TRUST: "Firm belief in the reliability, truth, or ability of someone or something",
        EmotionTag.ANTICIPATION: "Pleasurable expectation about a future event"
    }
    return descriptions.get(emotion, "Emotion tag")

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English", "full_support": True},
            {"code": "es", "name": "Spanish", "full_support": False},
            {"code": "fr", "name": "French", "full_support": False},
            {"code": "de", "name": "German", "full_support": False},
            {"code": "it", "name": "Italian", "full_support": False},
            {"code": "pt", "name": "Portuguese", "full_support": False},
            {"code": "ru", "name": "Russian", "full_support": False},
            {"code": "ja", "name": "Japanese", "full_support": False},
            {"code": "zh", "name": "Chinese", "full_support": False},
            {"code": "ar", "name": "Arabic", "full_support": False}
        ]
    }

@app.delete("/history")
async def clear_history(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Clear analysis history"""
    try:
        # Date filter
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old analyses
        deleted_count = db.query(Analysis).filter(
            Analysis.created_at < cutoff_date
        ).delete()
        
        # Delete old batch analyses
        deleted_batch_count = db.query(BatchAnalysis).filter(
            BatchAnalysis.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "message": "History cleared successfully",
            "deleted_analyses": deleted_count,
            "deleted_batch_analyses": deleted_batch_count,
            "cutoff_date": cutoff_date
        }
        
    except Exception as e:
        logger.error(f"History clearing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
