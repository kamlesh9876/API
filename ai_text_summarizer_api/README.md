# AI Text Summarizer API

A comprehensive AI-powered text summarization API with automatic language detection, multiple summarization modes, keyword extraction, and advanced NLP capabilities. Built with Transformers and FastAPI for intelligent text processing.

## 🚀 Features

- **AI-Powered Summarization**: Advanced transformer models for high-quality summaries
- **Multiple Summary Types**: Abstractive, extractive, bullet points, headlines, key points
- **Language Detection**: Automatic detection of 12+ languages
- **Keyword Extraction**: Extract keywords, key phrases, named entities, and topics
- **Bullet Point Mode**: Convert text to structured bullet points
- **Text Statistics**: Comprehensive text analysis and readability scores
- **Batch Processing**: Summarize multiple texts simultaneously
- **File Upload**: Support for text file summarization
- **Multiple Models**: BART, T5, and multilingual models
- **Confidence Scoring**: Quality assessment for generated summaries
- **GPU Support**: CUDA acceleration for faster processing

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **AI Models**: Transformers (BART, T5, mBART)
- **NLP Libraries**: NLTK, spaCy, scikit-learn
- **Language Detection**: langdetect, XLM-RoBERTa
- **Machine Learning**: PyTorch, NumPy
- **Text Processing**: TF-IDF, tokenization, POS tagging

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- 8GB+ RAM for AI models (16GB+ recommended)
- GPU support optional (CUDA compatible)
- Internet connection for model downloads

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download spaCy model**:
```bash
python -m spacy download en_core_web_sm
```

3. **Download NLTK data** (automatic on first run):
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

4. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8014`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8014/docs`
- ReDoc: `http://localhost:8014/redoc`

## 📝 API Endpoints

### Main Summarization

#### Summarize Text
```http
POST /summarize
Content-Type: application/json

{
  "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents: any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term artificial intelligence is often used to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem-solving. AI applications include advanced web search engines, recommendation systems, understanding human speech, self-driving cars, competing at the highest level in strategic games, and creative content generation.",
  "summary_type": "abstractive",
  "summary_length": "medium",
  "extract_keywords": true,
  "keyword_count": 10,
  "include_statistics": true
}
```

**Response Example**:
```json
{
  "id": "summary_123",
  "original_text": "Artificial intelligence (AI) is intelligence demonstrated by machines...",
  "summary": "Artificial intelligence is machine intelligence that mimics human cognitive functions like learning and problem-solving. AI applications include web search, recommendation systems, speech understanding, self-driving cars, strategic games, and content generation.",
  "summary_type": "abstractive",
  "language_detected": "en",
  "keywords": {
    "keywords": ["intelligence", "machines", "artificial", "human", "learning", "problem-solving", "applications", "search", "recommendation", "systems"],
    "key_phrases": ["artificial intelligence", "machine intelligence", "cognitive functions", "web search engines", "recommendation systems"],
    "entities": ["AI", "machines", "humans", "animals"],
    "topics": ["technology", "computing", "automation"]
  },
  "statistics": {
    "word_count": 85,
    "sentence_count": 4,
    "paragraph_count": 1,
    "avg_sentence_length": 21.25,
    "avg_word_length": 5.2,
    "readability_score": 45.8,
    "language_detected": "en"
  },
  "processing_time": 2.45,
  "model_used": "facebook/bart-large-cnn",
  "confidence_score": 0.87,
  "created_at": "2024-01-15T12:00:00"
}
```

#### Summarize File
```http
POST /summarize/file
Content-Type: multipart/form-data

file: [text file]
summary_type: bullet_points
summary_length: short
extract_keywords: true
```

#### Batch Summarization
```http
POST /summarize/batch
Content-Type: application/json

{
  "texts": [
    "First text to summarize...",
    "Second text to summarize...",
    "Third text to summarize..."
  ],
  "summary_type": "abstractive",
  "summary_length": "medium",
  "extract_keywords": true
}
```

**Response Example**:
```json
{
  "batch_id": "batch_123",
  "results": [
    {
      "id": "summary_1",
      "original_text": "First text...",
      "summary": "Summary of first text...",
      "summary_type": "abstractive",
      "language_detected": "en",
      "processing_time": 1.2,
      "model_used": "facebook/bart-large-cnn",
      "confidence_score": 0.85
    }
  ],
  "total_processing_time": 3.8,
  "success_count": 3,
  "error_count": 0
}
```

### Specialized Endpoints

#### Extract Keywords
```http
POST /extract-keywords
Content-Type: application/json

{
  "text": "Your text here for keyword extraction...",
  "keyword_count": 15,
  "language": "auto"
}
```

**Response Example**:
```json
{
  "keywords": ["artificial", "intelligence", "machines", "learning", "systems"],
  "key_phrases": ["artificial intelligence", "machine learning", "recommendation systems"],
  "entities": ["AI", "machines", "humans"],
  "topics": ["technology", "computing", "automation"]
}
```

#### Detect Language
```http
POST /detect-language
Content-Type: application/json

{
  "text": "Bonjour, comment allez-vous aujourd'hui?"
}
```

**Response Example**:
```json
{
  "detected_language": "fr",
  "confidence": 0.92,
  "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"]
}
```

#### Analyze Text Statistics
```http
POST /analyze-text
Content-Type: application/json

{
  "text": "Your text here for analysis...",
  "language": "auto"
}
```

**Response Example**:
```json
{
  "word_count": 150,
  "sentence_count": 8,
  "paragraph_count": 3,
  "avg_sentence_length": 18.75,
  "avg_word_length": 4.8,
  "readability_score": 52.3,
  "language_detected": "en"
}
```

### Utility Endpoints

#### Model Status
```http
GET /models/status
```

**Response Example**:
```json
{
  "models": {
    "en": {
      "loaded": true,
      "device": "cuda:0",
      "status": "ready"
    },
    "multilingual": {
      "loaded": true,
      "device": "cuda:0",
      "status": "ready"
    }
  },
  "device": "cuda:0",
  "language_detector": true,
  "nlp_models": ["en"],
  "total_models_loaded": 4
}
```

#### Summary Types
```http
GET /summary-types
```

#### Supported Languages
```http
GET /languages
```

## 📊 Summary Types

### 1. Abstractive Summarization
- **Description**: Generate new sentences that capture the essence
- **Best for**: Creating human-like summaries
- **Models used**: BART, T5
- **Quality**: High coherence and readability

### 2. Extractive Summarization
- **Description**: Extract important sentences from original text
- **Best for**: Fact-based summaries, quotes
- **Method**: TF-IDF sentence scoring
- **Quality**: Preserves original wording

### 3. Bullet Points
- **Description**: Format summary as structured bullet points
- **Best for**: Presentations, quick overviews
- **Format**: • Point 1\n• Point 2\n• Point 3
- **Use case**: Executive summaries

### 4. Headline
- **Description**: Generate a single sentence headline
- **Best for**: Titles, social media posts
- **Length**: 10-20 words
- **Use case**: News headlines

### 5. Key Points
- **Description**: Extract only the most important points
- **Best for**: Decision-making summaries
- **Focus**: Critical information only
- **Use case**: Business reports

## 🌍 Supported Languages

| Language | Code | Native Support | Model |
|----------|------|----------------|-------|
| English | en | ✅ | BART, T5 |
| Spanish | es | ✅ | mBART |
| French | fr | ✅ | mBART |
| German | de | ✅ | mBART |
| Italian | it | ✅ | mBART |
| Portuguese | pt | ✅ | mBART |
| Russian | ru | ✅ | mBART |
| Chinese | zh | ✅ | mBART |
| Japanese | ja | ✅ | mBART |
| Korean | ko | ✅ | mBART |
| Arabic | ar | ✅ | mBART |
| Hindi | hi | ✅ | mBART |

## 📈 Summary Length Options

### Short (~50 words)
- **Use case**: Quick summaries, social media
- **Processing time**: Fast
- **Best for**: News headlines, notifications

### Medium (~150 words)
- **Use case**: General summaries, reports
- **Processing time**: Medium
- **Best for**: Articles, documents

### Long (~300 words)
- **Use case**: Detailed summaries, research
- **Processing time**: Slower
- **Best for**: Academic papers, long documents

### Custom
- **Use case**: Specific requirements
- **Range**: 10-1000 words
- **Flexibility**: Full control

## 🧪 Testing Examples

### Basic Summarization
```bash
# Simple text summarization
curl -X POST "http://localhost:8014/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, human activities have been the main driver of climate change since the 1950s. The burning of fossil fuels releases greenhouse gases that trap heat in the atmosphere, causing global warming. This leads to rising sea levels, extreme weather events, and disruptions to ecosystems. Addressing climate change requires reducing emissions, transitioning to renewable energy, and adapting to unavoidable impacts.",
    "summary_type": "abstractive",
    "summary_length": "medium",
    "extract_keywords": true
  }'
```

### Bullet Point Summarization
```bash
# Bullet point format
curl -X POST "http://localhost:8014/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The benefits of regular exercise include improved cardiovascular health, stronger muscles and bones, better mental health, and increased longevity. Exercise helps control weight, reduces risk of chronic diseases, improves mood through endorphin release, and enhances cognitive function. It also boosts energy levels, improves sleep quality, and strengthens the immune system. Different types of exercise offer various benefits: aerobic exercise improves heart health, strength training builds muscle, flexibility exercises enhance range of motion, and balance exercises reduce fall risk.",
    "summary_type": "bullet_points",
    "summary_length": "medium"
  }'
```

### File Upload Summarization
```bash
# Summarize text file
curl -X POST "http://localhost:8014/summarize/file" \
  -F "file=@document.txt" \
  -F "summary_type=abstractive" \
  -F "summary_length=short" \
  -F "extract_keywords=true"
```

### Batch Processing
```bash
# Multiple texts
curl -X POST "http://localhost:8014/summarize/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "First article about technology...",
      "Second article about science...",
      "Third article about business..."
    ],
    "summary_type": "abstractive",
    "extract_keywords": true
  }'
```

### Language Detection
```bash
# Detect language
curl -X POST "http://localhost:8014/detect-language" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bonjour, comment allez-vous? Je voudrais commander un café, s'il vous plaît."
  }'
```

### Keyword Extraction
```bash
# Extract keywords only
curl -X POST "http://localhost:8014/extract-keywords" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves. The process of learning begins with observations or data, such as examples, direct experience, or instruction, to look for patterns in data and make better decisions in the future.",
    "keyword_count": 15
  }'
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8014
DEBUG=false
RELOAD=false

# Model Configuration
DEFAULT_MODEL=facebook/bart-large-cnn
MULTILINGUAL_MODEL=facebook/mbart-large-50-many-to-many-mmt
SMALL_MODEL=t5-small
BASE_MODEL=t5-base

# Device Configuration
DEVICE=auto  # auto, cpu, cuda
MAX_MEMORY_GB=8
ENABLE_GPU=true

# Processing Limits
MAX_TEXT_LENGTH=50000
MAX_BATCH_SIZE=10
MAX_FILE_SIZE_MB=10
REQUEST_TIMEOUT=300

# Model Paths
MODEL_CACHE_DIR=./models
DOWNLOAD_MODELS=true
OFFLINE_MODE=false

# Language Detection
LANGUAGE_DETECTOR=papluca/xlm-roberta-base-language-detection
CONFIDENCE_THRESHOLD=0.7

# NLP Configuration
SPACY_MODEL=en_core_web_sm
NLTK_DATA_PATH=./nltk_data
ENABLE_POS_TAGGING=true
ENABLE_NER=true

# Performance
ENABLE_BATCH_PROCESSING=true
MAX_CONCURRENT_REQUESTS=5
ENABLE_CACHING=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/summarizer.log
LOG_MODEL_PERFORMANCE=true
LOG_REQUESTS=true

# Security
ENABLE_AUTHENTICATION=false
API_KEY_HEADER=X-API-Key
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Advanced Features
ENABLE_FINE_TUNING=false
FINE_TUNING_DATA_PATH=./training_data
ENABLE_MODEL_VERSIONING=true
MODEL_BACKUP_COUNT=3

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8015
HEALTH_CHECK_INTERVAL=30
PROMETHEUS_ENABLED=true
```

## 🤖 AI Model Details

### BART (Bidirectional and Auto-Regressive Transformers)
- **Purpose**: Abstractive summarization
- **Strengths**: High-quality, coherent summaries
- **Languages**: English primary
- **Model Size**: ~400MB
- **Performance**: State-of-the-art for summarization

### T5 (Text-to-Text Transfer Transformer)
- **Purpose**: Text-to-text tasks
- **Strengths**: Versatile, good for various tasks
- **Languages**: English primary
- **Model Size**: ~220MB (small), ~770MB (base)
- **Performance**: Good balance of speed and quality

### mBART (Multilingual BART)
- **Purpose**: Multilingual translation and summarization
- **Strengths**: Supports 50+ languages
- **Languages**: Multilingual
- **Model Size**: ~1GB
- **Performance**: Best for non-English text

### XLM-RoBERTa (Language Detection)
- **Purpose**: Language identification
- **Strengths**: High accuracy language detection
- **Languages**: 100+ languages
- **Model Size**: ~1GB
- **Performance**: State-of-the-art language detection

## 📊 Algorithm Details

### Abstractive Summarization Process
```python
# 1. Tokenization
tokens = tokenizer.encode(text, max_length=1024, truncation=True)

# 2. Model Inference
summary_ids = model.generate(
    tokens,
    max_length=max_len,
    min_length=min_len,
    num_beams=4,
    early_stopping=True
)

# 3. Decoding
summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
```

### Extractive Summarization Process
```python
# 1. Sentence Tokenization
sentences = sent_tokenize(text)

# 2. TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(sentences)

# 3. Sentence Scoring
scores = np.array(tfidf_matrix.sum(axis=1)).flatten()

# 4. Top Sentence Selection
top_sentences = sentences[scores.argsort()[-k:]]
```

### Keyword Extraction Process
```python
# 1. Tokenization and Cleaning
words = word_tokenize(text.lower())
words = [w for w in words if w.isalpha() and w not in stopwords]

# 2. TF-IDF Scoring
word_freq = Counter(words)
tfidf_scores = {word: freq/len(words) * log(len(words)/freq) 
                for word, freq in word_freq.items()}

# 3. Top Keywords Selection
top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download models and data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs models

# Download AI models on startup
CMD ["bash", "-c", "python -c 'from app import AISummarizerService; AISummarizerService()' && uvicorn app:app --host 0.0.0.0 --port 8014"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  summarizer-api:
    build: .
    ports:
      - "8014:8014"
    environment:
      - DEVICE=cpu  # Use CPU for smaller instances
      - MAX_MEMORY_GB=4
      - ENABLE_GPU=false
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8014/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-summarizer-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-summarizer-api
  template:
    metadata:
      labels:
        app: ai-summarizer-api
    spec:
      containers:
      - name: api
        image: ai-summarizer-api:latest
        ports:
        - containerPort: 8014
        env:
        - name: DEVICE
          value: "cpu"
        - name: MAX_MEMORY_GB
          value: "4"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8014
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8014
          initialDelaySeconds: 30
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-summarizer-service
spec:
  selector:
    app: ai-summarizer-api
  ports:
  - port: 8014
    targetPort: 8014
  type: LoadBalancer
```

## 📈 Performance Optimization

### GPU Acceleration
```python
# Enable CUDA for faster processing
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Batch processing for multiple texts
def batch_summarize(texts, batch_size=4):
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # Process batch together
        yield process_batch(batch)
```

### Caching Strategy
```python
# Redis caching for repeated requests
@lru_cache(maxsize=1000)
def cached_summarize(text_hash, summary_type, length):
    # Check cache first
    cached_result = redis.get(f"summary:{text_hash}")
    if cached_result:
        return json.loads(cached_result)
    
    # Generate and cache result
    result = generate_summary(text, summary_type, length)
    redis.setex(f"summary:{text_hash}", 3600, json.dumps(result))
    return result
```

### Model Optimization
```python
# Quantization for smaller model size
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Half-precision for faster inference
model.half()
inputs = inputs.half()
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
summary_requests = Counter('summary_requests_total', 'Total summary requests')
processing_time = Histogram('summary_processing_seconds', 'Summary processing time')
model_load_time = Histogram('model_load_seconds', 'Model loading time')
active_models = Gauge('active_models_count', 'Number of loaded models')
gpu_memory_usage = Gauge('gpu_memory_usage_bytes', 'GPU memory usage')
```

### Quality Metrics
```python
def calculate_rouge_scores(reference, candidate):
    """Calculate ROUGE scores for summary quality"""
    from rouge_score import rouge_scorer
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, candidate)
    return scores

def calculate_bertscore(reference, candidate):
    """Calculate BERTScore for semantic similarity"""
    from bert_score import score
    P, R, F1 = score([candidate], [reference], lang="en")
    return {"precision": P.mean(), "recall": R.mean(), "f1": F1.mean()}
```

### Health Monitoring
```python
@app.get("/health/detailed")
async def detailed_health():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "models": {
            "loaded": len(ai_service.models),
            "device": str(ai_service.device),
            "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        },
        "performance": {
            "avg_processing_time": processing_time.observe(),
            "cache_hit_rate": calculate_cache_hit_rate(),
            "active_requests": get_active_request_count()
        }
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Custom Model Training**: Fine-tune models on domain-specific data
- **Real-time Summarization**: Streaming text summarization
- **Multi-document Summarization**: Summarize multiple related documents
- **Dialogue Summarization**: Specialized for conversations
- **Code Summarization**: Summarize code and documentation
- **Audio Transcription**: Summarize audio content
- **Video Summarization**: Extract and summarize video content
- **Cross-lingual Summarization**: Summarize in different language

### Advanced AI Features
- **GPT Integration**: Use GPT models for higher quality summaries
- **Reinforcement Learning**: Improve summary quality through feedback
- **Few-shot Learning**: Adapt to new domains with minimal data
- **Ensemble Methods**: Combine multiple models for better results
- **Explainable AI**: Provide reasoning for summary decisions
- **Style Transfer**: Summarize in different writing styles

### Integration Opportunities
- **CMS Integration**: WordPress, Drupal content summarization
- **Email Integration**: Automatic email summarization
- **Social Media**: Social media post summarization
- **News Aggregation**: News article summarization
- **Research Tools**: Academic paper summarization
- **Legal Documents**: Contract and legal text summarization

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review Transformers documentation for model details
- Consult NLTK and spaCy documentation for NLP concepts
- Check PyTorch documentation for GPU optimization

---

**Built with ❤️ using Transformers, FastAPI, and Advanced NLP**
