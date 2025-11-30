# Sentiment Analysis API

An advanced sentiment analysis API with emotion tagging and confidence scores using NLP and HuggingFace models. Features multiple model support, batch processing, and comprehensive text analytics.

## 🚀 Features

- **Sentiment Analysis**: Positive/negative/neutral classification with confidence scores
- **Emotion Tagging**: 8 emotion categories (joy, anger, fear, sadness, surprise, disgust, trust, anticipation)
- **Multiple NLP Models**: Transformers, VADER, and keyword-based fallbacks
- **Confidence Scores**: Detailed confidence metrics for all predictions
- **Batch Processing**: Analyze multiple texts simultaneously
- **Language Detection**: Automatic language identification
- **Text Statistics**: Comprehensive text analytics and readability metrics
- **Model Information**: Detailed model performance and capabilities
- **Analysis History**: Track and retrieve previous analyses
- **Health Monitoring**: System health and performance metrics

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **NLP Models**: HuggingFace Transformers (RoBERTa, DistilRoBERTa)
- **Sentiment Analysis**: VADER, rule-based, and keyword-based methods
- **Text Processing**: NLTK for tokenization and preprocessing
- **Database**: SQLAlchemy with SQLite
- **ML Framework**: PyTorch for model inference
- **Performance**: Async processing and background tasks

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- Internet connection (for model downloads)
- At least 2GB RAM for model loading

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download NLTK data** (if using NLTK):
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')
```

3. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8021`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8021/docs`
- ReDoc: `http://localhost:8021/redoc`

## 📝 API Endpoints

### Text Analysis

#### Analyze Single Text
```http
POST /analyze
Content-Type: application/json

{
  "text": "I absolutely love this product! It's amazing and works perfectly.",
  "language": "auto",
  "analysis_type": "comprehensive",
  "include_emotions": true,
  "include_confidence": true,
  "include_statistics": false
}
```

**Response Example**:
```json
{
  "id": "analysis_123",
  "input_text": "I absolutely love this product! It's amazing and works perfectly.",
  "sentiment": {
    "sentiment": "positive",
    "confidence": 0.95,
    "score": 0.89
  },
  "emotions": [
    {
      "emotion": "joy",
      "confidence": 0.92,
      "intensity": 0.88
    },
    {
      "emotion": "trust",
      "confidence": 0.75,
      "intensity": 0.70
    }
  ],
  "confidence": 0.95,
  "processing_time_ms": 125,
  "model_used": "transformers",
  "language_detected": "en",
  "statistics": null,
  "created_at": "2024-01-15T12:00:00"
}
```

#### Analyze Multiple Texts (Batch)
```http
POST /analyze/batch
Content-Type: application/json

{
  "texts": [
    "This is terrible! I hate it.",
    "It's okay, nothing special.",
    "Fantastic product! Highly recommended!"
  ],
  "language": "auto",
  "analysis_type": "comprehensive",
  "include_emotions": true,
  "include_confidence": true,
  "include_statistics": true
}
```

**Response Example**:
```json
{
  "batch_id": "batch_123",
  "results": [
    {
      "id": "analysis_124",
      "input_text": "This is terrible! I hate it.",
      "sentiment": {
        "sentiment": "negative",
        "confidence": 0.91,
        "score": -0.85
      },
      "emotions": [
        {
          "emotion": "anger",
          "confidence": 0.88,
          "intensity": 0.82
        },
        {
          "emotion": "disgust",
          "confidence": 0.65,
          "intensity": 0.60
        }
      ],
      "confidence": 0.91,
      "processing_time_ms": 98,
      "model_used": "transformers",
      "language_detected": "en",
      "statistics": {
        "char_count": 24,
        "char_count_no_spaces": 20,
        "word_count": 6,
        "sentence_count": 2,
        "avg_word_length": 3.33,
        "avg_sentence_length": 3.0,
        "complex_word_ratio": 0.0
      },
      "created_at": "2024-01-15T12:00:01"
    }
  ],
  "total_processed": 3,
  "total_failed": 0,
  "total_processing_time_ms": 345,
  "created_at": "2024-01-15T12:00:01"
}
```

### Model Information

#### Get Available Models
```http
GET /models
```

**Response Example**:
```json
[
  {
    "name": "Twitter RoBERTa Sentiment",
    "type": "transformers",
    "description": "RoBERTa-based sentiment analysis model trained on Twitter data",
    "accuracy": 0.85,
    "languages_supported": ["en"],
    "processing_speed": "medium",
    "last_updated": "2024-01-15T12:00:00"
  },
  {
    "name": "DistilRoBERTa Emotion",
    "type": "transformers",
    "description": "DistilRoBERTa-based emotion classification model",
    "accuracy": 0.82,
    "languages_supported": ["en"],
    "processing_speed": "fast",
    "last_updated": "2024-01-15T12:00:00"
  }
]
```

### Statistics and History

#### Get Analysis Statistics
```http
GET /statistics?days=30
```

**Response Example**:
```json
{
  "period_days": 30,
  "total_analyses": 1250,
  "sentiment_distribution": {
    "positive": 580,
    "negative": 320,
    "neutral": 350
  },
  "average_processing_time_ms": 145.67,
  "model_usage": {
    "transformers": 850,
    "vader": 300,
    "basic": 100
  },
  "language_distribution": {
    "en": 1100,
    "es": 75,
    "fr": 50,
    "de": 25
  },
  "generated_at": "2024-01-15T12:00:00"
}
```

#### Get Analysis History
```http
GET /history?skip=0&limit=50&sentiment_filter=positive&model_filter=transformers
```

#### Clear History
```http
DELETE /history?days=30
```

### Utility Endpoints

#### Get Supported Emotions
```http
GET /emotions
```

**Response Example**:
```json
{
  "emotions": [
    {
      "name": "joy",
      "description": "Feeling of great pleasure and happiness"
    },
    {
      "name": "anger",
      "description": "Strong feeling of annoyance, displeasure, or hostility"
    },
    {
      "name": "fear",
      "description": "An unpleasant emotion caused by threat or danger"
    }
  ]
}
```

#### Get Supported Languages
```http
GET /languages
```

#### Health Check
```http
GET /health
```

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00",
  "version": "1.0.0",
  "models_loaded": [
    "sentiment_transformers",
    "emotion_transformers",
    "vader",
    "basic"
  ],
  "database_status": "healthy",
  "memory_usage_mb": 512.45
}
```

## 🧪 Testing Examples

### Basic Sentiment Analysis
```bash
# Analyze positive text
curl -X POST "http://localhost:8021/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this amazing product! It works perfectly and exceeded my expectations.",
    "analysis_type": "comprehensive",
    "include_emotions": true,
    "include_confidence": true
  }'

# Analyze negative text
curl -X POST "http://localhost:8021/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is terrible! I hate it and want my money back.",
    "analysis_type": "comprehensive",
    "include_emotions": true,
    "include_confidence": true
  }'

# Analyze neutral text
curl -X POST "http://localhost:8021/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The product is functional and does what it says.",
    "analysis_type": "comprehensive",
    "include_emotions": true,
    "include_confidence": true
  }'
```

### Batch Analysis
```bash
# Analyze multiple texts
curl -X POST "http://localhost:8021/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great service and amazing staff!",
      "Poor quality and bad customer service.",
      "Average experience, nothing special."
    ],
    "analysis_type": "comprehensive",
    "include_emotions": true,
    "include_statistics": true
  }'
```

### Model Information
```bash
# Get available models
curl -X GET "http://localhost:8021/models"

# Get system health
curl -X GET "http://localhost:8021/health"

# Get statistics
curl -X GET "http://localhost:8021/statistics?days=7"
```

## 📊 Database Schema

### Analyses Table
- **id**: Primary key (UUID)
- **input_text**: Original input text
- **sentiment_label**: Sentiment classification (positive/negative/neutral)
- **sentiment_score**: Normalized sentiment score (-1 to 1)
- **confidence_score**: Confidence in prediction (0 to 1)
- **emotion_tags**: JSON string of emotion predictions
- **emotion_scores**: JSON string of emotion confidence scores
- **processing_time_ms**: Processing time in milliseconds
- **model_used**: Model used for analysis
- **analysis_type**: Type of analysis performed
- **language_detected**: Detected language code
- **word_count**: Number of words in input
- **sentence_count**: Number of sentences in input
- **created_at**: Analysis timestamp
- **ip_address**: Client IP address
- **user_agent**: Client user agent

### Model Performance Table
- **id**: Primary key (UUID)
- **model_name**: Name of the model
- **accuracy_score**: Model accuracy metric
- **precision_score**: Model precision metric
- **recall_score**: Model recall metric
- **f1_score**: Model F1 score
- **total_analyses**: Total analyses using this model
- **average_processing_time_ms**: Average processing time
- **last_updated**: Last update timestamp

### Batch Analyses Table
- **id**: Primary key (UUID)
- **batch_id**: Batch identifier for grouping
- **input_text**: Original input text
- **sentiment_label**: Sentiment classification
- **sentiment_score**: Normalized sentiment score
- **confidence_score**: Confidence in prediction
- **emotion_tags**: JSON string of emotion predictions
- **emotion_scores**: JSON string of emotion scores
- **processing_time_ms**: Processing time in milliseconds
- **status**: Processing status (completed/failed/pending)
- **error_message**: Error message if failed
- **created_at**: Analysis timestamp

## 🤖 NLP Models

### Transformers Models

#### Twitter RoBERTa Sentiment
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Type**: Transformer-based sentiment analysis
- **Training Data**: Twitter posts
- **Accuracy**: ~85%
- **Languages**: English
- **Processing Speed**: Medium
- **Features**: Context-aware sentiment analysis

#### DistilRoBERTa Emotion
- **Model**: `j-hartmann/emotion-english-distilroberta-base`
- **Type**: Transformer-based emotion classification
- **Training Data**: Labeled emotion datasets
- **Accuracy**: ~82%
- **Languages**: English
- **Processing Speed**: Fast
- **Features**: Multi-emotion classification

### Traditional Models

#### VADER Sentiment
- **Type**: Rule-based sentiment analysis
- **Algorithm**: Valence Aware Dictionary and sEntiment Reasoner
- **Accuracy**: ~75%
- **Languages**: English
- **Processing Speed**: Very Fast
- **Features**: Social media text optimized

#### Basic Sentiment
- **Type**: Keyword-based sentiment analysis
- **Algorithm**: Simple word matching
- **Accuracy**: ~60%
- **Languages**: Multiple (basic support)
- **Processing Speed**: Very Fast
- **Features**: Fallback method

## 🎯 Emotion Categories

### Primary Emotions
1. **Joy**: Feeling of great pleasure and happiness
2. **Anger**: Strong feeling of annoyance, displeasure, or hostility
3. **Fear**: An unpleasant emotion caused by threat or danger
4. **Sadness**: Emotional pain associated with feelings of disadvantage or loss

### Secondary Emotions
5. **Surprise**: Brief emotional state from unexpected events
6. **Disgust**: Emotional response of revulsion to offensive content
7. **Trust**: Firm belief in reliability or truth
8. **Anticipation**: Pleasurable expectation about future events

### Emotion Scoring
- **Confidence**: Model confidence in emotion prediction (0-1)
- **Intensity**: Strength of emotion in text (0-1)
- **Multiple Emotions**: Text can have multiple emotions with different intensities

## 📈 Analysis Types

### Sentiment Analysis Only
- **Output**: Sentiment label, confidence, score
- **Processing**: Fastest
- **Models**: Sentiment-specific models
- **Use Case**: Quick sentiment classification

### Emotion Analysis Only
- **Output**: Emotion tags, confidence, intensity
- **Processing**: Medium speed
- **Models**: Emotion-specific models
- **Use Case**: Emotional content analysis

### Comprehensive Analysis
- **Output**: Sentiment + emotions + statistics
- **Processing**: Slower but complete
- **Models**: Multiple models
- **Use Case**: Full text analysis

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8021
DEBUG=false
RELOAD=false

# Database Configuration
DATABASE_URL=sqlite:///sentiment_analysis.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30
DATABASE_ECHO=false
ENABLE_DATABASE_BACKUP=true
BACKUP_INTERVAL_HOURS=6
BACKUP_RETENTION_DAYS=30

# Model Configuration
DEFAULT_SENTIMENT_MODEL=transformers
DEFAULT_EMOTION_MODEL=transformers
ENABLE_TRANSFORMERS=true
ENABLE_NLTK=true
ENABLE_FALLBACK_MODELS=true
MODEL_CACHE_DIR=./models
MAX_MODEL_MEMORY_MB=2048
MODEL_TIMEOUT_SECONDS=60

# Transformers Configuration
TRANSFORMERS_CACHE_DIR=./cache/transformers
SENTIMENT_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
EMOTION_MODEL_NAME=j-hartmann/emotion-english-distilroberta-base
MODEL_DEVICE=auto  # auto, cpu, cuda
ENABLE_MODEL_QUANTIZATION=false
MODEL_QUANTIZATION_BITS=8

# NLTK Configuration
NLTK_DATA_PATH=./nltk_data
ENABLE_NLTK_DOWNLOAD=true
NLTK_CORPORA=punkt,stopwords,vader_lexicon
ENABLE_ADVANCED_TOKENIZATION=true
ENABLE_SENTENCE_TOKENIZATION=true

# Processing Configuration
MAX_TEXT_LENGTH=10000
MIN_TEXT_LENGTH=1
MAX_BATCH_SIZE=100
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_ANALYSES=10
PROCESSING_TIMEOUT_SECONDS=30

# Language Detection
ENABLE_LANGUAGE_DETECTION=true
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,fr,de,it,pt,ru,ja,zh,ar
ENABLE_MULTI_LANGUAGE_SUPPORT=false

# Text Preprocessing
ENABLE_TEXT_CLEANING=true
REMOVE_URLS=true
REMOVE_EMAILS=true
REMOVE_EXCESSIVE_PUNCTUATION=true
NORMALIZE_WHITESPACE=true
ENABLE_LOWERCASE_CONVERSION=false

# Confidence and Scoring
MIN_CONFIDENCE_THRESHOLD=0.1
ENABLE_CONFIDENCE_CALIBRATION=true
CONFIDENCE_CALIBRATION_METHOD=temperature_scaling
ENABLE_ENSEMBLE_METHODS=false
ENSEMBLE_WEIGHTS=transformers=0.7,vader=0.3

# Caching Configuration
ENABLE_RESULT_CACHING=true
CACHE_TTL_SECONDS=3600
CACHE_STORAGE=memory
CACHE_MAX_SIZE=10000
ENABLE_MODEL_OUTPUT_CACHING=true
MODEL_CACHE_TTL_SECONDS=7200

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/sentiment_analysis.log
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_MODEL_PERFORMANCE=true
LOG_PROCESSING_TIMES=true
LOG_ERRORS=true

# Performance Monitoring
ENABLE_PERFORMANCE_MONITORING=true
MONITOR_MEMORY_USAGE=true
MONITOR_PROCESSING_TIMES=true
ENABLE_PROFILING=false
PROFILE_SAMPLE_RATE=0.1
ENABLE_METRICS_COLLECTION=true

# Security Configuration
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
ENABLE_IP_WHITELIST=false
IP_WHITELIST=127.0.0.1,::1
ENABLE_INPUT_VALIDATION=true
MAX_REQUEST_SIZE_MB=10

# CORS Configuration
ENABLE_CORS=true
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
CORS_MAX_AGE=3600

# Development Configuration
TEST_MODE=false
ENABLE_PROFILING=false
DEBUG_RESPONSES=false
ENABLE_SWAGGER_UI=true
ENABLE_REDOC=true
ENABLE_API_DOCS_AUTH=false
ENABLE_TEST_ENDPOINTS=false

# Production Configuration
ENABLE_HEALTH_CHECK=true
HEALTH_CHECK_INTERVAL_SECONDS=30
ENABLE_GRACEFUL_SHUTDOWN=true
SHUTDOWN_TIMEOUT_SECONDS=30
ENABLE_RESTART_ON_FAILURE=false

# Backup and Recovery
ENABLE_AUTO_BACKUP=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_STORAGE=local
BACKUP_ENCRYPTION=false
BACKUP_COMPRESSION=true
BACKUP_RETENTION_COPIES=30
ENABLE_POINT_IN_TIME_RECOVERY=false

# Advanced Features
ENABLE_ENSEMBLE_MODELS=false
ENABLE_CUSTOM_MODELS=false
CUSTOM_MODEL_PATH=./custom_models
ENABLE_MODEL_VERSIONING=false
MODEL_VERSION_STORAGE=database
ENABLE_A_B_TESTING=false
ENABLE_FEATURE_FLAGS=false

# Integration Configuration
ENABLE_EXTERNAL_INTEGRATIONS=false
EXTERNAL_API_TIMEOUT=10
ENABLE_WEBHOOKS=false
WEBHOOK_SECRET=your-webhook-secret
ENABLE_CALLBACKS=false

# Monitoring and Alerting
ENABLE_MONITORING_DASHBOARD=false
DASHBOARD_PORT=8022
ENABLE_ALERTS=false
ALERT_THRESHOLD_PROCESSING_TIME=5000
ALERT_THRESHOLD_ERROR_RATE=0.05
ENABLE_EMAIL_ALERTS=false

# Experimental Features
ENABLE_EXPERIMENTAL_MODELS=false
EXPERIMENTAL_MODELS=gpt_sentiment,bert_emotion
ENABLE_RESEARCH_MODE=false
ENABLE_ADVANCED_ANALYTICS=false
ENABLE_PREDICTIVE_ANALYTICS=false
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs models cache

# Set permissions
RUN chmod +x logs models cache

EXPOSE 8021

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8021"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  sentiment-api:
    build: .
    ports:
      - "8021:8021"
    environment:
      - DATABASE_URL=sqlite:///data/sentiment_analysis.db
      - LOG_LEVEL=INFO
      - ENABLE_TRANSFORMERS=true
      - MODEL_DEVICE=cpu
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./models:/app/models
      - ./cache:/app/cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8021/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

volumes:
  data_data:
  logs_data:
  models_data:
  cache_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentiment-analysis-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sentiment-analysis-api
  template:
    metadata:
      labels:
        app: sentiment-analysis-api
    spec:
      containers:
      - name: api
        image: sentiment-analysis-api:latest
        ports:
        - containerPort: 8021
        env:
        - name: DATABASE_URL
          value: sqlite:///data/sentiment_analysis.db
        - name: MODEL_DEVICE
          value: cpu
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: models
          mountPath: /app/models
        - name: cache
          mountPath: /app/cache
        livenessProbe:
          httpGet:
            path: /health
            port: 8021
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8021
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data-pvc
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: cache
        persistentVolumeClaim:
          claimName: cache-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: sentiment-analysis-service
spec:
  selector:
    app: sentiment-analysis-api
  ports:
  - port: 8021
    targetPort: 8021
  type: LoadBalancer
```

## 📈 Advanced Features

### Ensemble Methods
```python
# Combine multiple models for better accuracy
def ensemble_sentiment_analysis(text: str, models: List[str]) -> Dict[str, Any]:
    """Combine predictions from multiple models"""
    predictions = []
    
    for model_name in models:
        try:
            if model_name == "transformers":
                pred = analyzer.analyze_sentiment_transformers(text)
            elif model_name == "vader":
                pred = analyzer.analyze_sentiment_vader(text)
            elif model_name == "basic":
                pred = analyzer._basic_sentiment_analysis(text)
            
            predictions.append(pred)
        except Exception as e:
            logger.error(f"Model {model_name} failed: {e}")
    
    # Weighted average of predictions
    if predictions:
        avg_score = sum(p['score'] for p in predictions) / len(predictions)
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        
        # Determine final sentiment
        if avg_score > 0.1:
            sentiment = 'positive'
        elif avg_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': SentimentLabel(sentiment),
            'confidence': avg_confidence,
            'score': avg_score
        }
    
    return analyzer._basic_sentiment_analysis(text)
```

### Advanced Text Preprocessing
```python
def advanced_text_preprocessing(text: str) -> str:
    """Advanced text preprocessing for better analysis"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove hashtags and mentions
    text = re.sub(r'#[\w]+', '', text)
    text = re.sub(r'@[\w]+', '', text)
    
    # Normalize repeated characters
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    # Handle contractions
    contractions = {
        "won't": "will not",
        "can't": "cannot",
        "n't": " not",
        "'ve": " have",
        "'ll": " will",
        "'re": " are",
        "'d": " would"
    }
    
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
    
    return text.strip()
```

### Confidence Calibration
```python
def calibrate_confidence(raw_confidence: float, model_name: str) -> float:
    """Calibrate confidence scores based on model performance"""
    calibration_params = {
        "transformers": {"scale": 1.1, "offset": -0.05},
        "vader": {"scale": 0.9, "offset": 0.1},
        "basic": {"scale": 0.7, "offset": 0.15}
    }
    
    params = calibration_params.get(model_name, {"scale": 1.0, "offset": 0.0})
    
    calibrated = raw_confidence * params["scale"] + params["offset"]
    return max(0.0, min(1.0, calibrated))
```

## 🔍 Performance Optimization

### Model Caching
```python
from functools import lru_cache
import torch

class CachedSentimentAnalyzer:
    def __init__(self):
        self.cache_size = 1000
        self._setup_caching()
    
    def _setup_caching(self):
        """Setup model result caching"""
        self.sentiment_cache = {}
        self.emotion_cache = {}
    
    @lru_cache(maxsize=1000)
    def get_text_hash(self, text: str) -> str:
        """Get hash of text for caching"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def analyze_with_cache(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze with caching"""
        text_hash = self.get_text_hash(text)
        cache_key = f"{text_hash}_{analysis_type}"
        
        # Check cache
        if analysis_type == "sentiment" and cache_key in self.sentiment_cache:
            return self.sentiment_cache[cache_key]
        elif analysis_type == "emotion" and cache_key in self.emotion_cache:
            return self.emotion_cache[cache_key]
        
        # Perform analysis
        result = self.analyze_text(text, analysis_type)
        
        # Cache result
        if analysis_type == "sentiment":
            self.sentiment_cache[cache_key] = result
        elif analysis_type == "emotion":
            self.emotion_cache[cache_key] = result
        
        return result
```

### Batch Processing Optimization
```python
async def optimized_batch_analysis(texts: List[str]) -> List[Dict[str, Any]]:
    """Optimized batch processing with parallel execution"""
    # Group texts by language for model optimization
    language_groups = defaultdict(list)
    for i, text in enumerate(texts):
        lang = analyzer.detect_language(text)
        language_groups[lang].append((i, text))
    
    results = [None] * len(texts)
    
    # Process each language group
    for lang, text_group in language_groups.items():
        if lang == 'en' and analyzer.models_loaded:
            # Use Transformers for English
            group_texts = [text for _, text in text_group]
            batch_results = await process_with_transformers(group_texts)
            
            for (i, _), result in zip(text_group, batch_results):
                results[i] = result
        else:
            # Use fallback for other languages
            for i, text in text_group:
                results[i] = analyzer.analyze_text(text)
    
    return results
```

## 📊 Monitoring and Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
analysis_requests = Counter('analysis_requests_total', 'Total analysis requests', model='transformers|vader|basic')
processing_time = Histogram('processing_time_seconds', 'Processing time in seconds')
model_accuracy = Gauge('model_accuracy', 'Model accuracy', model='transformers|vader|basic')
memory_usage = Gauge('memory_usage_mb', 'Memory usage in MB')
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate')
```

### Model Performance Tracking
```python
def track_model_performance(model_name: str, prediction: Dict[str, Any], 
                          ground_truth: Optional[Dict[str, Any]] = None):
    """Track model performance metrics"""
    if ground_truth:
        # Calculate accuracy
        correct = prediction['sentiment'] == ground_truth['sentiment']
        
        # Update model performance in database
        db = SessionLocal()
        model_perf = db.query(ModelPerformance).filter(
            ModelPerformance.model_name == model_name
        ).first()
        
        if model_perf:
            # Update metrics
            total_analyses = model_perf.total_analyses + 1
            current_accuracy = model_perf.accuracy_score or 0.0
            
            # Calculate new accuracy
            new_accuracy = (current_accuracy * model_perf.total_analyses + (1 if correct else 0)) / total_analyses
            
            model_perf.total_analyses = total_analyses
            model_perf.accuracy_score = new_accuracy
            model_perf.last_updated = datetime.utcnow()
            
            db.commit()
        else:
            # Create new performance record
            model_perf = ModelPerformance(
                model_name=model_name,
                accuracy_score=1.0 if correct else 0.0,
                total_analyses=1,
                last_updated=datetime.utcnow()
            )
            db.add(model_perf)
            db.commit()
        
        db.close()
```

## 🔮 Future Enhancements

### Planned Features
- **Custom Model Training**: Train models on domain-specific data
- **Real-time Streaming**: WebSocket support for real-time analysis
- **Multi-language Models**: Better support for non-English languages
- **Aspect-based Sentiment**: Analyze sentiment for specific aspects
- **Emotion Intensity Scaling**: More granular emotion intensity levels
- **Text Generation**: Generate responses based on sentiment/emotion
- **Integration APIs**: Easy integration with popular platforms

### Advanced NLP Features
- **Named Entity Recognition**: Identify entities in text
- **Keyword Extraction**: Extract important keywords
- **Text Summarization**: Generate text summaries
- **Topic Modeling**: Identify topics in text
- **Semantic Similarity**: Compare text similarity
- **Language Translation**: Multi-language support

### Machine Learning Enhancements
- **Active Learning**: Improve models with user feedback
- **Transfer Learning**: Adapt models to specific domains
- **Ensemble Methods**: Combine multiple models
- **Model Explainability**: Explain model predictions
- **Bias Detection**: Detect and mitigate model bias
- **Continuous Learning**: Update models with new data

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review HuggingFace documentation for model details
- Consult FastAPI documentation for API development
- Check NLTK documentation for text processing

---

**Built with ❤️ using FastAPI, HuggingFace Transformers, and advanced NLP techniques**
