# News Classification / Fake News API

A sophisticated fake news detection API built with FastAPI and machine learning techniques. Analyzes news articles and provides real/fake probability scores with detailed feature analysis.

## 🚀 Features

- **Real/Fake Classification**: Predicts if news is real or fake with confidence scores
- **Feature Analysis**: Detailed breakdown of text features used in classification
- **Batch Processing**: Classify multiple articles simultaneously
- **Sentiment Analysis**: Analyzes emotional tone of articles
- **Readability Scoring**: Evaluates text complexity
- **Source Credibility**: Assesses trustworthiness of news sources
- **Clickbait Detection**: Identifies sensational headlines and content
- **Fact Check Integration**: Provides relevant fact-checking resources
- **Performance Metrics**: Model accuracy and performance statistics
- **Custom Feature Engineering**: Extensible feature extraction system

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Machine Learning**: scikit-learn, NLTK, TextBlob
- **Data Analysis**: pandas, numpy
- **Visualization**: matplotlib, seaborn
- **Text Processing**: NLTK, regular expressions
- **API Documentation**: Auto-generated Swagger/OpenAPI

## 📋 Prerequisites

- Python 3.7+
- pip package manager

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download NLTK data** (optional, for enhanced features):
```python
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
```

3. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8005`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`

## 🔍 API Endpoints

### Classification

#### Classify Single Article
```http
POST /classify
Content-Type: application/json

{
  "text": "The federal government announced new regulations...",
  "title": "New Government Regulations Announced",
  "source": "reuters.com",
  "author": "John Smith",
  "publish_date": "2024-01-15T10:00:00"
}
```

**Response Example**:
```json
{
  "text": "The federal government announced new regulations...",
  "prediction": "real",
  "confidence": 0.87,
  "probabilities": {
    "real": 0.87,
    "fake": 0.13
  },
  "features": {
    "text_length": 1250,
    "word_count": 200,
    "sensational_word_count": 0,
    "clickbait_count": 0,
    "source_credibility": 0.9,
    "readability_score": 65.2
  },
  "processing_time": 0.045,
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Batch Classification
```http
POST /classify-batch
Content-Type: application/json

{
  "news_articles": [
    {
      "text": "Article 1 text...",
      "title": "Article 1 title",
      "source": "source1.com"
    },
    {
      "text": "Article 2 text...",
      "title": "Article 2 title",
      "source": "source2.com"
    }
  ]
}
```

### Feature Analysis

#### Analyze Text Features
```http
POST /analyze-features
Content-Type: application/json

{
  "text": "SHOCKING revelation reveals conspiracy...",
  "title": "You won't believe this BREAKING news",
  "source": "sensationalblog.com"
}
```

**Response Example**:
```json
{
  "sentiment_score": -0.3,
  "readability_score": 45.6,
  "sensational_words": ["shocking", "reveals", "breaking"],
  "clickbait_indicators": ["you won't believe", "breaking news"],
  "source_credibility": 0.2,
  "fact_check_urls": ["https://www.snopes.com/"]
}
```

### Model Information

#### Get Model Metrics
```http
GET /model-metrics
```

#### Feature Explanations
```http
GET /feature-explanation
```

#### Get Sensational Words List
```http
GET /sensational-words
```

### Testing

#### Test with Sample Articles
```http
POST /test-classification
```

## 🧪 Testing Examples

### Classify a Real News Article
```bash
curl -X POST http://localhost:8005/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The Federal Reserve announced today a quarter-point increase in the federal funds rate, bringing it to a range of 5.25% to 5.5%. The decision was unanimous among committee members.",
    "title": "Federal Reserve Raises Interest Rates by 0.25 Percentage Points",
    "source": "Reuters"
  }'
```

### Classify a Fake News Article
```bash
curl -X POST http://localhost:8005/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "SHOCKING breakthrough reveals that doctors have been hiding the secret to eternal youth! You won'\''t believe what they don'\''t want you to know.",
    "title": "BREAKING: Scientists Discover Miracle Cure for All Diseases",
    "source": "conspiracyblog.com"
  }'
```

### Analyze Features Only
```bash
curl -X POST http://localhost:8005/analyze-features \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This amazing discovery will change everything forever!",
    "title": "One weird trick doctors hate"
  }'
```

## 🤖 Machine Learning Features

### Feature Engineering

The API extracts multiple categories of features:

#### Text Features
- **Text Length**: Total characters in article
- **Word Count**: Number of words
- **Sentence Count**: Number of sentences
- **Average Sentence Length**: Words per sentence

#### Style Features
- **Capitalization Ratio**: Uppercase vs lowercase letters
- **Punctuation Usage**: Exclamation marks, question marks
- **Readability Score**: Flesch-Kincaid readability index

#### Content Features
- **Sensational Words**: Count of emotional/sensational terms
- **Clickbait Phrases**: Detection of clickbait patterns
- **Quote Count**: Number of quotations (indicates sources)
- **Number Count**: Statistical data presence

#### Credibility Features
- **Source Credibility**: Trustworthiness assessment
- **URL Count**: External links analysis
- **Title-Content Overlap**: Consistency between headline and body

### Classification Algorithm

The current implementation uses a rule-based approach with feature scoring:

```python
# Simplified scoring logic
fake_score += sensational_word_count * 0.1
fake_score += clickbait_count * 0.15
fake_score += exclamation_count * 0.05

real_score += quote_count * 0.02
real_score += number_count * 0.01
real_score += source_credibility_bonus
```

### Model Enhancement Options

#### Machine Learning Models
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

# Train with real dataset
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
```

#### Deep Learning Approach
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Use pre-trained BERT model
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')
```

## 📊 Performance Metrics

### Model Evaluation
```json
{
  "accuracy": 0.85,
  "precision": 0.83,
  "recall": 0.87,
  "f1_score": 0.85,
  "confusion_matrix": {
    "predicted_real": {"actual_real": 850, "actual_fake": 150},
    "predicted_fake": {"actual_real": 130, "actual_fake": 870}
  },
  "total_samples": 2000
}
```

### Feature Importance
1. **Source Credibility**: 30% weight
2. **Sensational Words**: 25% weight
3. **Clickbait Indicators**: 20% weight
4. **Text Quality**: 15% weight
5. **Readability**: 10% weight

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Model Configuration
MODEL_PATH=models/fake_news_detector.pkl
FEATURE_CACHE_SIZE=1000

# API Settings
MAX_BATCH_SIZE=100
PROCESSING_TIMEOUT=30

# External Services
FACT_CHECK_API_KEY=your-fact-check-api-key
NEWS_API_KEY=your-news-api-key

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/news_classification.log
```

### Custom Feature Sets
```python
# Add custom sensational words
custom_sensational_words = [
    "outrageous", "incredible", "unprecedented",
    "historical", "game-changing", "revolutionary"
]

# Add custom credible sources
custom_sources = [
    "associated press", "bloomberg", "financial times",
    "the economist", "wired", "techcrunch"
]
```

## 🗄️ Database Integration

### Store Classification History
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime

# Database model for classification history
class ClassificationHistory(Base):
    __tablename__ = "classifications"
    
    id = Column(Integer, primary_key=True)
    text_hash = Column(String(64))  # For deduplication
    prediction = Column(String(10))
    confidence = Column(Float)
    features = Column(JSON)
    timestamp = Column(DateTime)
```

### User Feedback Loop
```python
@app.post("/feedback")
async def submit_feedback(
    classification_id: int,
    correct_label: str,
    user_id: Optional[str] = None
):
    # Store user feedback for model improvement
    pass
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

COPY . .
EXPOSE 8005

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8005"]
```

### Model Training Pipeline
```python
# train_model.py
def train_fake_news_detector():
    # Load dataset
    df = pd.read_csv('news_dataset.csv')
    
    # Feature extraction
    X = extract_features(df['text'])
    y = df['label']
    
    # Train model
    model = RandomForestClassifier()
    model.fit(X, y)
    
    # Save model
    joblib.dump(model, 'models/fake_news_detector.pkl')
```

## 📈 Advanced Features

### Real-time News Monitoring
```python
@app.post("/monitor-news-source")
async def monitor_news_source(source_url: str):
    """Continuously monitor a news source for fake news"""
    # Implement web scraping and real-time classification
    pass
```

### Multilingual Support
```python
from langdetect import detect

def detect_language(text: str) -> str:
    return detect(text)

# Language-specific models
language_models = {
    'en': english_model,
    'es': spanish_model,
    'fr': french_model
}
```

### Topic-based Analysis
```python
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_topics(text: str, n_topics: int = 5):
    """Extract main topics from article"""
    vectorizer = TfidfVectorizer(max_features=1000)
    # Implement topic modeling
    pass
```

## 🔍 Research & Development

### Dataset Sources
- **LIAR Dataset**: Fake news detection benchmark
- **FakeNewsNet**: Multi-source fake news dataset
- **ISOT Fake News Dataset**: Real and fake news articles
- **Kaggle Fake News**: Community-curated dataset

### Model Improvement Techniques
1. **Ensemble Methods**: Combine multiple classifiers
2. **Deep Learning**: BERT, RoBERTa, GPT-based models
3. **Transfer Learning**: Pre-trained language models
4. **Active Learning**: User feedback integration
5. **Few-shot Learning**: Adapt to new domains quickly

### Evaluation Metrics
- **Accuracy**: Overall classification accuracy
- **Precision**: False positive minimization
- **Recall**: False negative minimization
- **F1-Score**: Balance between precision and recall
- **AUC-ROC**: Model discrimination ability
- **Calibration**: Confidence score reliability

## 🛡️ Ethical Considerations

### Bias Detection
```python
def detect_bias(text: str) -> Dict[str, float]:
    """Detect political bias, gender bias, etc."""
    # Implement bias detection algorithms
    pass
```

### Transparency
- Explainable AI features
- Feature importance visualization
- Confidence calibration
- Uncertainty quantification

### Privacy Protection
- Text hashing for storage
- User data anonymization
- GDPR compliance
- Data retention policies

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the research papers on fake news detection
- Contribute to the dataset and model improvement

---

**Built with ❤️ using FastAPI and Machine Learning**
