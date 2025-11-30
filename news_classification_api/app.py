from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import re
import math
from collections import Counter
import json

app = FastAPI(title="News Classification / Fake News API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class NewsInput(BaseModel):
    text: str
    title: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None

class ClassificationResult(BaseModel):
    text: str
    prediction: str  # "real" or "fake"
    confidence: float  # 0.0 to 1.0
    probabilities: Dict[str, float]
    features: Dict[str, Any]
    processing_time: float
    timestamp: datetime

class BatchClassification(BaseModel):
    results: List[ClassificationResult]
    total_processed: int
    real_count: int
    fake_count: int
    average_confidence: float

class FeatureAnalysis(BaseModel):
    sentiment_score: float
    readability_score: float
    sensational_words: List[str]
    clickbait_indicators: List[str]
    source_credibility: Optional[float]
    fact_check_urls: List[str]

class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: Dict[str, Dict[str, int]]
    total_samples: int

# Fake news detection features
class FakeNewsDetector:
    def __init__(self):
        # Sensational words that often indicate fake news
        self.sensational_words = [
            "shocking", "unbelievable", "miracle", "breakthrough", "conspiracy",
            "cover-up", "secret", "revealed", "exposed", "hidden", "scandal",
            "outrageous", "incredible", "amazing", "stunning", "mind-blowing",
            "you won't believe", "what they don't want you to know", "the truth about"
        ]
        
        # Clickbait phrases
        self.clickbait_phrases = [
            "you won't believe", "shocking results", "doctors hate this",
            "one weird trick", "this will change everything", "never seen before",
            "breaking news", "exclusive", "urgent", "must read"
        ]
        
        # Credible news sources (simplified list)
        self.credible_sources = [
            "reuters", "associated press", "ap news", "bbc", "npr", "pbs",
            "the new york times", "wall street journal", "washington post",
            "the guardian", "financial times", "bloomberg", "cnn", "nbc news"
        ]
        
        # Fake news indicators
        self.fake_indicators = [
            "clickbait", "sensationalism", "emotional language", "unverified claims",
            "anonymous sources", "lack of quotes", "vague references", "all caps"
        ]
        
        # Real news indicators
        self.real_indicators = [
            "factual reporting", "named sources", "quotes", "statistics",
            "balanced perspective", "multiple sources", "expert opinions",
            "official statements", "data driven"
        ]

    def extract_features(self, text: str, title: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """Extract features for fake news detection"""
        features = {}
        
        # Text preprocessing
        text_lower = text.lower()
        title_lower = title.lower() if title else ""
        
        # Basic text features
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len(re.split(r'[.!?]+', text))
        features['avg_sentence_length'] = features['word_count'] / max(features['sentence_count'], 1)
        
        # Capitalization features
        features['capital_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features['exclamation_count'] = text.count('!') + title_lower.count('!')
        features['question_count'] = text.count('?') + title_lower.count('?')
        
        # Punctuation features
        features['punctuation_ratio'] = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
        
        # Sensational words
        sensational_found = []
        for word in self.sensational_words:
            if word in text_lower or word in title_lower:
                sensational_found.append(word)
        features['sensational_word_count'] = len(sensational_found)
        features['sensational_words'] = sensational_found
        
        # Clickbait detection
        clickbait_found = []
        for phrase in self.clickbait_phrases:
            if phrase in text_lower or phrase in title_lower:
                clickbait_found.append(phrase)
        features['clickbait_count'] = len(clickbait_found)
        features['clickbait_phrases'] = clickbait_found
        
        # Source credibility
        source_credibility = 0.5  # neutral
        if source:
            source_lower = source.lower()
            if any(cred_source in source_lower for cred_source in self.credible_sources):
                source_credibility = 0.9
            elif any(indicator in source_lower for indicator in ['blog', 'forum', 'social media', 'anonymous']):
                source_credibility = 0.2
        features['source_credibility'] = source_credibility
        
        # Quote detection (real news often has quotes)
        quote_count = text.count('"') + text.count("'")
        features['quote_count'] = quote_count
        
        # Number detection (real news often has statistics)
        number_count = len(re.findall(r'\d+', text))
        features['number_count'] = number_count
        
        # URL detection (fake news often has suspicious URLs)
        url_count = len(re.findall(r'http[s]?://\S+', text))
        features['url_count'] = url_count
        
        # Readability score (simplified Flesch-Kincaid)
        avg_sentence_length = features['avg_sentence_length']
        syllable_count = sum(len(re.findall(r'[aeiouAEIOU]+', word)) for word in text.split())
        avg_syllables_per_word = syllable_count / max(features['word_count'], 1)
        features['readability_score'] = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Sentiment analysis (simplified)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disgusting', 'worst']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words > 0:
            features['sentiment_score'] = (positive_count - negative_count) / total_sentiment_words
        else:
            features['sentiment_score'] = 0.0
        
        # Title vs content consistency
        if title:
            title_words = set(title_lower.split())
            content_words = set(text_lower.split())
            overlap = len(title_words.intersection(content_words))
            features['title_content_overlap'] = overlap / max(len(title_words), 1)
        else:
            features['title_content_overlap'] = 0.0
        
        return features

    def predict(self, text: str, title: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """Predict if news is real or fake"""
        import time
        start_time = time.time()
        
        features = self.extract_features(text, title, source)
        
        # Simplified scoring algorithm (in production, use trained ML model)
        fake_score = 0.0
        real_score = 0.0
        
        # Sensationalism penalty
        fake_score += features['sensational_word_count'] * 0.1
        fake_score += features['clickbait_count'] * 0.15
        
        # Punctuation and capitalization penalties
        fake_score += features['exclamation_count'] * 0.05
        fake_score += features['capital_ratio'] * 0.3
        
        # Source credibility
        if features['source_credibility'] > 0.7:
            real_score += 0.3
        elif features['source_credibility'] < 0.3:
            fake_score += 0.3
        
        # Quote and number bonuses (real news indicators)
        real_score += features['quote_count'] * 0.02
        real_score += features['number_count'] * 0.01
        
        # Text length (very short articles might be fake)
        if features['word_count'] < 50:
            fake_score += 0.2
        elif features['word_count'] > 300:
            real_score += 0.1
        
        # Readability (very simple or very complex might be fake)
        if features['readability_score'] < 30 or features['readability_score'] > 90:
            fake_score += 0.1
        
        # Title-content consistency
        if features['title_content_overlap'] < 0.2:
            fake_score += 0.15
        
        # Normalize scores
        total_score = fake_score + real_score + 0.1  # Add small constant to avoid division by zero
        
        fake_probability = fake_score / total_score
        real_probability = real_score / total_score
        
        # Normalize to ensure they sum to 1
        sum_prob = fake_probability + real_probability
        fake_probability /= sum_prob
        real_probability /= sum_prob
        
        # Make prediction
        prediction = "fake" if fake_probability > real_probability else "real"
        confidence = max(fake_probability, real_probability)
        
        processing_time = time.time() - start_time
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": {"fake": fake_probability, "real": real_probability},
            "features": features,
            "processing_time": processing_time
        }

# Initialize detector
detector = FakeNewsDetector()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to News Classification / Fake News API", "version": "1.0.0"}

@app.post("/classify", response_model=ClassificationResult)
async def classify_news(news_input: NewsInput):
    """Classify a single news article as real or fake"""
    result = detector.predict(
        text=news_input.text,
        title=news_input.title,
        source=news_input.source
    )
    
    return ClassificationResult(
        text=news_input.text[:200] + "..." if len(news_input.text) > 200 else news_input.text,
        prediction=result["prediction"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
        features=result["features"],
        processing_time=result["processing_time"],
        timestamp=datetime.now()
    )

@app.post("/classify-batch", response_model=BatchClassification)
async def classify_batch(news_articles: List[NewsInput]):
    """Classify multiple news articles"""
    results = []
    real_count = 0
    fake_count = 0
    total_confidence = 0.0
    
    for article in news_articles:
        result = detector.predict(
            text=article.text,
            title=article.title,
            source=article.source
        )
        
        classification_result = ClassificationResult(
            text=article.text[:200] + "..." if len(article.text) > 200 else article.text,
            prediction=result["prediction"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            features=result["features"],
            processing_time=result["processing_time"],
            timestamp=datetime.now()
        )
        
        results.append(classification_result)
        
        if result["prediction"] == "real":
            real_count += 1
        else:
            fake_count += 1
        
        total_confidence += result["confidence"]
    
    average_confidence = total_confidence / len(news_articles) if news_articles else 0.0
    
    return BatchClassification(
        results=results,
        total_processed=len(news_articles),
        real_count=real_count,
        fake_count=fake_count,
        average_confidence=average_confidence
    )

@app.post("/analyze-features", response_model=FeatureAnalysis)
async def analyze_features(news_input: NewsInput):
    """Analyze text features without classification"""
    features = detector.extract_features(
        text=news_input.text,
        title=news_input.title,
        source=news_input.source
    )
    
    # Find fact-check URLs (mock implementation)
    fact_check_urls = []
    if "covid" in news_input.text.lower() or "coronavirus" in news_input.text.lower():
        fact_check_urls.append("https://www.snopes.com/fact-check/coronavirus/")
    if "politics" in news_input.text.lower():
        fact_check_urls.append("https://www.politifact.com/")
    
    return FeatureAnalysis(
        sentiment_score=features.get('sentiment_score', 0.0),
        readability_score=features.get('readability_score', 0.0),
        sensational_words=features.get('sensational_words', []),
        clickbait_indicators=features.get('clickbait_phrases', []),
        source_credibility=features.get('source_credibility', None),
        fact_check_urls=fact_check_urls
    )

@app.get("/model-metrics", response_model=ModelMetrics)
async def get_model_metrics():
    """Get model performance metrics (mock data for demo)"""
    return ModelMetrics(
        accuracy=0.85,
        precision=0.83,
        recall=0.87,
        f1_score=0.85,
        confusion_matrix={
            "predicted_real": {"actual_real": 850, "actual_fake": 150},
            "predicted_fake": {"actual_real": 130, "actual_fake": 870}
        },
        total_samples=2000
    )

@app.get("/feature-explanation")
async def get_feature_explanation():
    """Get explanation of features used in classification"""
    return {
        "text_features": {
            "text_length": "Total number of characters in the article",
            "word_count": "Number of words in the article",
            "sentence_count": "Number of sentences in the article",
            "avg_sentence_length": "Average words per sentence"
        },
        "style_features": {
            "capital_ratio": "Ratio of uppercase letters to total characters",
            "exclamation_count": "Number of exclamation marks",
            "question_count": "Number of question marks",
            "punctuation_ratio": "Ratio of punctuation to total characters"
        },
        "content_features": {
            "sensational_word_count": "Count of sensational/emotional words",
            "clickbait_count": "Count of clickbait phrases",
            "quote_count": "Number of quotation marks (indicates sources)",
            "number_count": "Count of numbers (indicates data/statistics)"
        },
        "credibility_features": {
            "source_credibility": "Trustworthiness score of the source (0-1)",
            "url_count": "Number of URLs in the article",
            "title_content_overlap": "Similarity between title and content"
        },
        "readability_features": {
            "readability_score": "Flesch-Kincaid readability score",
            "sentiment_score": "Sentiment analysis score (-1 to 1)"
        }
    }

@app.get("/sensational-words")
async def get_sensational_words():
    """Get list of sensational words used in detection"""
    return {
        "sensational_words": detector.sensational_words,
        "clickbait_phrases": detector.clickbait_phrases,
        "credible_sources": detector.credible_sources
    }

@app.post("/test-classification")
async def test_classification():
    """Test the classifier with sample articles"""
    test_articles = [
        {
            "title": "BREAKING: Scientists Discover Miracle Cure for All Diseases",
            "text": "SHOCKING breakthrough reveals that doctors have been hiding the secret to eternal youth! You won't believe what they don't want you to know. This one weird trick will change everything!",
            "source": "conspiracyblog.com"
        },
        {
            "title": "Federal Reserve Raises Interest Rates by 0.25 Percentage Points",
            "text": "The Federal Reserve announced today a quarter-point increase in the federal funds rate, bringing it to a range of 5.25% to 5.5%. The decision was unanimous among committee members. 'We are committed to bringing inflation down to 2%,' said Fed Chair Jerome Powell in a press conference.",
            "source": "Reuters"
        }
    ]
    
    results = []
    for article in test_articles:
        result = detector.predict(
            text=article["text"],
            title=article["title"],
            source=article["source"]
        )
        results.append({
            "title": article["title"],
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "source": article["source"]
        })
    
    return {"test_results": results}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "model_loaded": True,
        "features_count": len(detector.sensational_words) + len(detector.clickbait_phrases)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
