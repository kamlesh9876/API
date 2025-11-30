# Movie Recommendation API

A comprehensive movie recommendation API with search functionality, cosine similarity-based recommendations, genre-based filtering, and TMDB integration for trending movies. Built with Python ML libraries and FastAPI for intelligent movie discovery.

## 🚀 Features

- **Movie Search**: Search movies by title with detailed information
- **Similar Movies**: Find similar movies using cosine similarity algorithms
- **Genre-based Recommendations**: Get recommendations based on movie genres
- **Trending Movies**: Real-time trending movies via TMDB API
- **Personalized Recommendations**: ML-powered recommendations based on user preferences
- **Popular Movies**: Discover popular and top-rated movies
- **User Preferences**: Track user ratings, favorites, and watchlist
- **Advanced ML**: TF-IDF vectorization and similarity calculations
- **Comprehensive Data**: Movie details, cast, crew, keywords, and production info
- **Caching System**: Intelligent caching for improved performance
- **TMDB Integration**: Full integration with The Movie Database API

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Machine Learning**: Scikit-learn, NumPy
- **Text Processing**: TF-IDF Vectorization
- **Similarity Algorithm**: Cosine Similarity
- **External API**: TMDB (The Movie Database)
- **Database**: SQLite with caching layers
- **Data Processing**: Pandas-like operations with NumPy

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- TMDB API key (free from themoviedb.org)
- 4GB+ RAM for ML operations

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Get TMDB API Key**:
   - Visit [TMDB](https://www.themoviedb.org/signup)
   - Create an account and get your API key
   - Set environment variable:
   ```bash
   export TMDB_API_KEY=your_tmdb_api_key
   ```

3. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8013`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8013/docs`
- ReDoc: `http://localhost:8013/redoc`

## 🎬 API Endpoints

### Movie Search

#### Search Movies
```http
GET /movies/search?query=inception&page=1
```

**Response Example**:
```json
{
  "movies": [
    {
      "id": 1,
      "tmdb_id": 27205,
      "title": "Inception",
      "overview": "A thief who steals corporate secrets...",
      "genres": ["Action", "Adventure", "Sci-Fi"],
      "release_date": "2010-07-16",
      "runtime": 148,
      "vote_average": 8.4,
      "vote_count": 35000,
      "popularity": 85.5,
      "poster_path": "/qyJN0tlPq43aN5Fz7g2yvr4Lj5E.jpg",
      "backdrop_path": "/s3TBrRGB1iav7gCNKN3iMH4JyJo.jpg",
      "original_language": "en",
      "budget": 160000000,
      "revenue": 836800000,
      "tagline": "Your mind is the scene of the crime.",
      "keywords": ["dream", "thief", "subconscious", "reality"],
      "cast": [
        {"name": "Leonardo DiCaprio", "character": "Cobb"},
        {"name": "Marion Cotillard", "character": "Mal"}
      ],
      "crew": [
        {"name": "Christopher Nolan", "job": "Director"},
        {"name": "Hans Zimmer", "job": "Music"}
      ],
      "production_companies": ["Warner Bros.", "Legendary Entertainment"],
      "production_countries": ["United States", "United Kingdom"],
      "spoken_languages": ["English", "Japanese", "French"],
      "status": "Released",
      "adult": false,
      "video": false
    }
  ],
  "total_results": 1,
  "total_pages": 1,
  "current_page": 1
}
```

#### Get Movie Details
```http
GET /movies/27205
```

### Recommendations

#### Similar Movies (Cosine Similarity)
```http
GET /recommendations/similar/27205?limit=10
```

**Response Example**:
```json
{
  "movie_id": 27205,
  "type": "similar",
  "recommendations": [
    {
      "movie_id": 157336,
      "title": "Interstellar",
      "score": 0.85,
      "reason": "Similar content and themes",
      "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
      "release_date": "2014-11-07",
      "vote_average": 8.2
    },
    {
      "movie_id": 99861,
      "title": "Fight Club",
      "score": 0.78,
      "reason": "Similar content and themes",
      "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
      "release_date": "1999-10-15",
      "vote_average": 8.4
    }
  ],
  "total_count": 10,
  "generated_at": "2024-01-15T12:00:00"
}
```

#### Genre-based Recommendations
```http
GET /recommendations/genre/action?limit=10
```

#### Trending Movies (TMDB)
```http
GET /recommendations/trending?time_window=day&limit=10
```

**Response Example**:
```json
{
  "type": "trending",
  "recommendations": [
    {
      "movie_id": 96657,
      "title": "Oppenheimer",
      "score": 0.95,
      "reason": "Trending day",
      "poster_path": "/8Gxv8gWSFCXCexIXKoFDt6T6aDq.jpg",
      "release_date": "2023-07-21",
      "vote_average": 8.3
    },
    {
      "movie_id": 346698,
      "title": "Barbie",
      "score": 0.92,
      "reason": "Trending day",
      "poster_path": "/iuQjJ8rKvXLnMi0aou9XtOL3yPu.jpg",
      "release_date": "2023-07-21",
      "vote_average": 7.0
    }
  ],
  "total_count": 10
}
```

#### Popular Movies
```http
GET /recommendations/popular?limit=10
```

#### Top Rated Movies
```http
GET /recommendations/top-rated?limit=10
```

### User Preferences

#### Create User Preference
```http
POST /users/user123/preferences
Content-Type: application/json

{
  "movie_id": 27205,
  "rating": 4.5,
  "favorite": true,
  "watchlist": false,
  "watched": true
}
```

#### Get User Preferences
```http
GET /users/user123/preferences
```

#### Personalized Recommendations
```http
GET /users/user123/recommendations/personalized?limit=10
```

**Response Example**:
```json
{
  "user_id": "user123",
  "type": "personalized",
  "recommendations": [
    {
      "movie_id": 157336,
      "title": "Interstellar",
      "score": 0.92,
      "reason": "Based on your viewing history and preferences",
      "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
      "release_date": "2014-11-07",
      "vote_average": 8.2
    }
  ],
  "total_count": 10
}
```

### Utility Endpoints

#### Get Genres
```http
GET /genres
```

**Response Example**:
```json
{
  "genres": [
    {"id": 28, "name": "Action"},
    {"id": 12, "name": "Adventure"},
    {"id": 16, "name": "Animation"},
    {"id": 35, "name": "Comedy"},
    {"id": 80, "name": "Crime"},
    {"id": 99, "name": "Documentary"},
    {"id": 18, "name": "Drama"},
    {"id": 10751, "name": "Family"},
    {"id": 14, "name": "Fantasy"},
    {"id": 36, "name": "History"}
  ]
}
```

## 📊 Data Models

### Movie
```json
{
  "id": 1,
  "tmdb_id": 27205,
  "title": "Inception",
  "overview": "A thief who steals corporate secrets...",
  "genres": ["Action", "Adventure", "Sci-Fi"],
  "release_date": "2010-07-16",
  "runtime": 148,
  "vote_average": 8.4,
  "vote_count": 35000,
  "popularity": 85.5,
  "poster_path": "/qyJN0tlPq43aN5Fz7g2yvr4Lj5E.jpg",
  "backdrop_path": "/s3TBrRGB1iav7gCNKN3iMH4JyJo.jpg",
  "original_language": "en",
  "budget": 160000000,
  "revenue": 836800000,
  "tagline": "Your mind is the scene of the crime.",
  "keywords": ["dream", "thief", "subconscious", "reality"],
  "cast": [
    {"name": "Leonardo DiCaprio", "character": "Cobb"},
    {"name": "Marion Cotillard", "character": "Mal"}
  ],
  "crew": [
    {"name": "Christopher Nolan", "job": "Director"},
    {"name": "Hans Zimmer", "job": "Music"}
  ],
  "production_companies": ["Warner Bros.", "Legendary Entertainment"],
  "production_countries": ["United States", "United Kingdom"],
  "spoken_languages": ["English", "Japanese", "French"],
  "status": "Released",
  "adult": false,
  "video": false
}
```

### UserPreference
```json
{
  "id": "pref_123",
  "user_id": "user123",
  "movie_id": 27205,
  "rating": 4.5,
  "favorite": true,
  "watchlist": false,
  "watched": true,
  "created_at": "2024-01-15T12:00:00"
}
```

### Recommendation
```json
{
  "movie_id": 157336,
  "title": "Interstellar",
  "score": 0.85,
  "reason": "Similar content and themes",
  "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
  "release_date": "2014-11-07",
  "vote_average": 8.2
}
```

## 🧪 Testing Examples

### Search and Recommendation Workflow
```bash
# Search for movies
curl "http://localhost:8013/movies/search?query=inception&page=1"

# Get movie details
curl "http://localhost:8013/movies/27205"

# Get similar movies
curl "http://localhost:8013/recommendations/similar/27205?limit=5"

# Get genre recommendations
curl "http://localhost:8013/recommendations/genre/sci-fi?limit=5"

# Get trending movies
curl "http://localhost:8013/recommendations/trending?time_window=day&limit=5"

# Create user preference
curl -X POST "http://localhost:8013/users/user123/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 27205,
    "rating": 4.5,
    "favorite": true,
    "watched": true
  }'

# Get personalized recommendations
curl "http://localhost:8013/users/user123/recommendations/personalized?limit=5"
```

### Advanced ML Testing
```bash
# Test similarity algorithm
curl "http://localhost:8013/recommendations/similar/157336?limit=10"

# Test genre-based filtering
curl "http://localhost:8013/recommendations/genre/action?limit=10"

# Test trending with different time windows
curl "http://localhost:8013/recommendations/trending?time_window=week&limit=10"
curl "http://localhost:8013/recommendations/trending?time_window=month&limit=10"
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# TMDB API Configuration
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p/w500

# API Configuration
HOST=0.0.0.0
PORT=8013
DEBUG=false

# Database Configuration
DATABASE_URL=movie_recommendation.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30

# ML Configuration
TFIDF_MAX_FEATURES=5000
TFIDF_NGRAM_RANGE_MIN=1
TFIDF_NGRAM_RANGE_MAX=2
SIMILARITY_THRESHOLD=0.1
MAX_RECOMMENDATIONS=50

# Caching Configuration
ENABLE_CACHE=true
CACHE_TTL=3600
RECOMMENDATION_CACHE_TTL=1800
TRENDING_CACHE_TTL=900

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_SEARCH=20
RATE_LIMIT_RECOMMENDATIONS=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/movie_api.log
LOG_ML_OPERATIONS=true
LOG_CACHE_HITS=true

# Performance
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
ML_MODEL_TIMEOUT=60

# Security
ENABLE_HTTPS=false
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
API_KEY_HEADER=X-API-Key
ENABLE_AUTHENTICATION=false

# Feature Weights
TITLE_WEIGHT=1.0
OVERVIEW_WEIGHT=0.8
GENRE_WEIGHT=0.6
KEYWORD_WEIGHT=0.4
CAST_WEIGHT=0.3
NUMERICAL_FEATURES_WEIGHT=0.3
```

## 🤖 Machine Learning Details

### Feature Extraction
The API uses advanced NLP and ML techniques for movie recommendations:

#### TF-IDF Vectorization
```python
# Text features combined for each movie
features = [
    movie.title,                    # Movie title (weight: 1.0)
    movie.overview,                 # Plot description (weight: 0.8)
    " ".join(movie.genres),         # Genres (weight: 0.6)
    " ".join(movie.keywords),       # Keywords (weight: 0.4)
    " ".join(cast_names),           # Cast members (weight: 0.3)
    " ".join(production_companies)  # Production companies (weight: 0.3)
]
```

#### Numerical Features
```python
numerical_features = [
    vote_average,    # IMDb-style rating
    popularity,      # TMDB popularity score
    vote_count,      # Number of votes
    runtime,         # Movie duration
    genre_count,     # Number of genres
    keyword_count,   # Number of keywords
    cast_count       # Number of cast members
]
```

### Similarity Calculation
```python
# Cosine similarity calculation
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(movie_vector, feature_matrix):
    similarities = cosine_similarity(movie_vector, feature_matrix)[0]
    return similarities.argsort()[::-1][1:top_k+1]  # Exclude self
```

### Recommendation Algorithms

#### 1. Content-Based Similarity
- **Input**: Movie TMDB ID
- **Process**: TF-IDF + Cosine Similarity
- **Output**: Movies with similar content/themes
- **Use Case**: "Movies like Inception"

#### 2. Genre-Based Filtering
- **Input**: Genre name
- **Process**: Filter by genre + popularity ranking
- **Output**: Popular movies in the genre
- **Use Case**: "Action movie recommendations"

#### 3. Collaborative Filtering (Personalized)
- **Input**: User preferences/ratings
- **Process**: User's liked movies → similar movies
- **Output**: Personalized recommendations
- **Use Case**: "Recommended for you"

#### 4. Trend-Based Recommendations
- **Input**: Time window (day/week/month)
- **Process**: TMDB trending API
- **Output**: Currently popular movies
- **Use Case**: "What's trending now"

## 📊 Database Schema

### SQLite Tables
```sql
-- Movies table
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    overview TEXT,
    genres TEXT,  -- JSON array
    release_date DATE,
    runtime INTEGER,
    vote_average REAL,
    vote_count INTEGER,
    popularity REAL,
    poster_path TEXT,
    backdrop_path TEXT,
    keywords TEXT,  -- JSON array
    cast TEXT,  -- JSON array
    crew TEXT,  -- JSON array
    -- ... other fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences table
CREATE TABLE user_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    movie_id INTEGER,
    rating REAL CHECK(rating >= 0.5 AND rating <= 5.0),
    favorite BOOLEAN DEFAULT 0,
    watchlist BOOLEAN DEFAULT 0,
    watched BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies (id)
);

-- Recommendations cache table
CREATE TABLE recommendations_cache (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    movie_id INTEGER,
    recommendation_type TEXT,
    recommendations TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
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

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs data

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords')"

EXPOSE 8013

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8013"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  movie-api:
    build: .
    ports:
      - "8013:8013"
    environment:
      - TMDB_API_KEY=${TMDB_API_KEY}
      - DATABASE_URL=/app/data/movie_recommendation.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8013/health"]
      interval: 30s
      timeout: 10s
      retries: 3

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
  name: movie-recommendation-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: movie-recommendation-api
  template:
    metadata:
      labels:
        app: movie-recommendation-api
    spec:
      containers:
      - name: api
        image: movie-recommendation-api:latest
        ports:
        - containerPort: 8013
        env:
        - name: TMDB_API_KEY
          valueFrom:
            secretKeyRef:
              name: tmdb-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8013
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8013
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: movie-recommendation-service
spec:
  selector:
    app: movie-recommendation-api
  ports:
  - port: 8013
    targetPort: 8013
  type: LoadBalancer
```

## 📈 Advanced Features

### Hybrid Recommendation System
```python
class HybridRecommendationEngine:
    def __init__(self):
        self.content_based = ContentBasedEngine()
        self.collaborative = CollaborativeEngine()
        self.popularity_based = PopularityEngine()
    
    def get_hybrid_recommendations(self, user_id, movie_id, weights=None):
        """Combine multiple recommendation strategies"""
        content_recs = self.content_based.get_similar_movies(movie_id)
        collab_recs = self.collaborative.get_user_recommendations(user_id)
        popular_recs = self.popularity_based.get_trending_movies()
        
        # Combine with weights
        final_recs = self.combine_recommendations(
            content_recs, collab_recs, popular_recs, weights
        )
        
        return final_recs
```

### Real-time Learning
```python
class OnlineLearningEngine:
    def update_user_profile(self, user_id, movie_id, rating):
        """Update user profile in real-time"""
        # Incremental learning
        user_vector = self.get_user_vector(user_id)
        movie_vector = self.get_movie_vector(movie_id)
        
        # Update using gradient descent
        self.update_weights(user_vector, movie_vector, rating)
```

### A/B Testing Framework
```python
@app.get("/recommendations/ab-test/{user_id}")
async def ab_test_recommendations(user_id: str):
    """A/B testing different recommendation algorithms"""
    algorithm = select_algorithm_for_user(user_id)
    
    if algorithm == "content_based":
        return await get_content_based_recommendations(user_id)
    elif algorithm == "collaborative":
        return await get_collaborative_recommendations(user_id)
    else:
        return await get_hybrid_recommendations(user_id)
```

### Advanced Analytics
```python
@app.get("/analytics/user-behavior/{user_id}")
async def get_user_analytics(user_id: str):
    """Analyze user viewing patterns and preferences"""
    return {
        "favorite_genres": get_favorite_genres(user_id),
        "viewing_patterns": get_viewing_patterns(user_id),
        "rating_distribution": get_rating_distribution(user_id),
        "discovery_sources": get_discovery_sources(user_id)
    }
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
recommendation_requests = Counter('movie_recommendation_requests_total', 'Total recommendation requests')
ml_processing_time = Histogram('movie_ml_processing_seconds', 'ML processing time')
cache_hit_rate = Gauge('movie_cache_hit_rate', 'Cache hit rate')
active_users = Gauge('movie_active_users', 'Active users')
```

### Model Performance
```python
@app.get("/analytics/model-performance")
async def get_model_performance():
    """Get ML model performance metrics"""
    return {
        "accuracy": calculate_recommendation_accuracy(),
        "precision": calculate_precision(),
        "recall": calculate_recall(),
        "f1_score": calculate_f1_score(),
        "user_satisfaction": get_user_satisfaction_scores()
    }
```

### Health Monitoring
```python
@app.get("/health/detailed")
async def detailed_health():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "tmdb_api": await check_tmdb_health(),
            "database": await check_database_health(),
            "ml_models": check_ml_models_health(),
            "cache": await check_cache_health()
        },
        "metrics": {
            "total_recommendations": recommendation_requests._value._value,
            "cache_hit_rate": cache_hit_rate._value._value,
            "active_users": active_users._value._value
        }
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Deep Learning Models**: Neural collaborative filtering
- **Image Recognition**: Visual similarity based on posters
- **Audio Analysis**: Soundtrack-based recommendations
- **Social Features**: Friend recommendations and sharing
- **Watch Parties**: Group viewing recommendations
- **Seasonal Content**: Holiday and event-based recommendations
- **Mood Detection**: Emotion-based movie suggestions
- **Multi-language Support**: Recommendations in different languages
- **Content Filtering**: Parental controls and content warnings
- **Integration**: Netflix, Hulu, Disney+ integration

### Advanced ML Features
- **Matrix Factorization**: SVD, NMF for collaborative filtering
- **Neural Networks**: Deep learning for better recommendations
- **Reinforcement Learning**: Adaptive recommendation systems
- **Ensemble Methods**: Combine multiple ML models
- **Knowledge Graphs**: Movie relationship mapping
- **Time-aware Recommendations**: Temporal preference modeling
- **Cold Start Solutions**: New user/item problem
- **Explainable AI**: Recommendation reasoning

### Analytics & Insights
- **User Journey Tracking**: Complete viewing history analysis
- **Content Performance**: Movie success prediction
- **Trend Analysis**: Emerging genre detection
- **Demographic Insights**: Age/gender preference analysis
- **Geographic Patterns**: Regional preference differences
- **Competitive Analysis**: Market trend monitoring
- **ROI Analysis**: Content investment recommendations

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review TMDB API documentation
- Consult Scikit-learn documentation for ML concepts
- Check NumPy documentation for data operations

---

**Built with ❤️ using FastAPI, Scikit-learn, and TMDB API**
