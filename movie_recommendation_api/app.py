from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import sqlite3
from sqlite3 import Connection
import json
import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import pickle
import os
from collections import defaultdict
import re

app = FastAPI(title="Movie Recommendation API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "movie_recommendation.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Movies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tmdb_id INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            overview TEXT,
            genres TEXT,  -- JSON array
            release_date DATE,
            runtime INTEGER,  -- in minutes
            vote_average REAL,
            vote_count INTEGER,
            popularity REAL,
            poster_path TEXT,
            backdrop_path TEXT,
            original_language TEXT,
            budget INTEGER,
            revenue INTEGER,
            tagline TEXT,
            keywords TEXT,  -- JSON array
            cast TEXT,  -- JSON array of top cast
            crew TEXT,  -- JSON array of key crew
            production_companies TEXT,  -- JSON array
            production_countries TEXT,  -- JSON array
            spoken_languages TEXT,  -- JSON array
            status TEXT,  -- Released, Post Production, etc.
            adult BOOLEAN DEFAULT 0,
            video BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            movie_id INTEGER,
            rating REAL CHECK(rating >= 0.5 AND rating <= 5.0),
            favorite BOOLEAN DEFAULT 0,
            watchlist BOOLEAN DEFAULT 0,
            watched BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
    ''')
    
    # Recommendations cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations_cache (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            movie_id INTEGER,
            recommendation_type TEXT,  -- similar, genre_based, trending, personalized
            recommendations TEXT,  -- JSON array of movie IDs with scores
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # Trending movies cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trending_cache (
            id TEXT PRIMARY KEY,
            trending_type TEXT,  -- day, week, month
            movies TEXT,  -- JSON array
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_tmdb_id ON movies(tmdb_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_genres ON movies(genres)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_movie_id ON user_preferences(movie_id)')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# TMDB API Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "your_tmdb_api_key")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Enums
class RecommendationType(str, Enum):
    SIMILAR = "similar"
    GENRE_BASED = "genre_based"
    TRENDING = "trending"
    PERSONALIZED = "personalized"
    POPULAR = "popular"
    TOP_RATED = "top_rated"

class TrendingType(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

# Pydantic models
class Movie(BaseModel):
    id: Optional[int] = None
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    genres: List[str] = []
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    original_language: Optional[str] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    tagline: Optional[str] = None
    keywords: List[str] = []
    cast: List[Dict[str, Any]] = []
    crew: List[Dict[str, Any]] = []
    production_companies: List[str] = []
    production_countries: List[str] = []
    spoken_languages: List[str] = []
    status: Optional[str] = None
    adult: bool = False
    video: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserPreference(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    movie_id: int
    rating: Optional[float] = Field(None, ge=0.5, le=5.0)
    favorite: bool = False
    watchlist: bool = False
    watched: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class Recommendation(BaseModel):
    movie_id: int
    title: str
    score: float
    reason: str
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None

class RecommendationResponse(BaseModel):
    user_id: Optional[str] = None
    movie_id: Optional[int] = None
    type: RecommendationType
    recommendations: List[Recommendation]
    total_count: int
    generated_at: datetime = Field(default_factory=datetime.now)

class SearchResult(BaseModel):
    movies: List[Movie]
    total_results: int
    total_pages: int
    current_page: int

class TrendingMovie(BaseModel):
    id: int
    title: str
    popularity: float
    vote_average: Optional[float] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None

# TMDB API Service
class TMDBService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = TMDB_BASE_URL
        self.image_base_url = TMDB_IMAGE_BASE_URL
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make request to TMDB API"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        params['language'] = 'en-US'
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"TMDB API error: {str(e)}")
    
    def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """Search movies by title"""
        return self._make_request("/search/movie", {
            "query": query,
            "page": page,
            "include_adult": False
        })
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get detailed movie information"""
        movie = self._make_request(f"/movie/{movie_id}")
        credits = self._make_request(f"/movie/{movie_id}/credits")
        keywords = self._make_request(f"/movie/{movie_id}/keywords")
        
        # Combine all information
        movie.update({
            "cast": credits.get("cast", [])[:10],  # Top 10 cast members
            "crew": credits.get("crew", [])[:5],   # Top 5 crew members
            "keywords": [kw["name"] for kw in keywords.get("keywords", [])]
        })
        
        return movie
    
    def get_similar_movies(self, movie_id: int, page: int = 1) -> Dict[str, Any]:
        """Get similar movies from TMDB"""
        return self._make_request(f"/movie/{movie_id}/similar", {"page": page})
    
    def get_trending_movies(self, time_window: str = "day", page: int = 1) -> Dict[str, Any]:
        """Get trending movies"""
        return self._make_request("/trending/movie/{}".format(time_window), {"page": page})
    
    def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get popular movies"""
        return self._make_request("/movie/popular", {"page": page})
    
    def get_top_rated_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get top rated movies"""
        return self._make_request("/movie/top_rated", {"page": page})
    
    def get_movies_by_genre(self, genre_id: int, page: int = 1) -> Dict[str, Any]:
        """Get movies by genre"""
        return self._make_request("/discover/movie", {
            "with_genres": genre_id,
            "page": page,
            "sort_by": "popularity.desc"
        })
    
    def get_genres(self) -> Dict[str, Any]:
        """Get all genres"""
        return self._make_request("/genre/movie/list")

# Initialize TMDB service
tmdb_service = TMDBService(TMDB_API_KEY)

# Movie Recommendation Engine
class MovieRecommendationEngine:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.feature_matrix = None
        self.movie_indices = {}
        self.scaler = MinMaxScaler()
    
    def build_feature_matrix(self, movies: List[Movie]) -> np.ndarray:
        """Build feature matrix for similarity calculations"""
        # Combine text features
        text_features = []
        for movie in movies:
            features = []
            features.append(movie.title or "")
            features.append(movie.overview or "")
            features.append(" ".join(movie.genres))
            features.append(" ".join(movie.keywords))
            features.append(" ".join([actor.get("name", "") for actor in movie.cast[:5]]))
            features.append(" ".join(movie.production_companies))
            text_features.append(" ".join(features))
        
        # Create TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(text_features)
        
        # Add numerical features
        numerical_features = []
        for movie in movies:
            features = [
                movie.vote_average or 0,
                movie.popularity or 0,
                movie.vote_count or 0,
                movie.runtime or 0,
                len(movie.genres),
                len(movie.keywords),
                len(movie.cast)
            ]
            numerical_features.append(features)
        
        numerical_features = np.array(numerical_features)
        numerical_features = self.scaler.fit_transform(numerical_features)
        
        # Combine features
        combined_features = np.hstack([
            tfidf_matrix.toarray(),
            numerical_features * 0.3  # Weight numerical features less
        ])
        
        self.feature_matrix = combined_features
        self.movie_indices = {movie.tmdb_id: idx for idx, movie in enumerate(movies)}
        
        return combined_features
    
    def calculate_similarity(self, movie_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
        """Calculate similarity-based recommendations"""
        if movie_id not in self.movie_indices:
            return []
        
        movie_idx = self.movie_indices[movie_id]
        movie_vector = self.feature_matrix[movie_idx].reshape(1, -1)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(movie_vector, self.feature_matrix)[0]
        
        # Get top similar movies (excluding the movie itself)
        similar_indices = similarities.argsort()[::-1][1:top_k+1]
        
        recommendations = []
        for idx in similar_indices:
            similarity_score = similarities[idx]
            if similarity_score > 0.1:  # Threshold for similarity
                recommendations.append({
                    "movie_index": idx,
                    "similarity_score": similarity_score
                })
        
        return recommendations
    
    def get_genre_based_recommendations(self, genres: List[str], movies: List[Movie], top_k: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations based on genres"""
        genre_movies = []
        for movie in movies:
            if any(genre.lower() in [g.lower() for g in movie.genres] for genre in genres):
                genre_movies.append(movie)
        
        # Sort by popularity and rating
        genre_movies.sort(key=lambda x: (x.popularity or 0) * (x.vote_average or 0), reverse=True)
        
        recommendations = []
        for movie in genre_movies[:top_k]:
            score = (movie.popularity or 0) * (movie.vote_average or 0) / 100
            recommendations.append({
                "movie": movie,
                "score": min(score, 1.0)
            })
        
        return recommendations
    
    def get_personalized_recommendations(self, user_preferences: List[UserPreference], movies: List[Movie], top_k: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user preferences"""
        # Get user's liked movies
        liked_movies = []
        for pref in user_preferences:
            if pref.rating and pref.rating >= 4.0:
                liked_movies.append(pref.movie_id)
        
        if not liked_movies:
            return []
        
        # Find similar movies to user's liked movies
        movie_scores = defaultdict(float)
        
        for liked_movie_id in liked_movies:
            similar_movies = self.calculate_similarity(liked_movie_id, top_k * 2)
            for sim in similar_movies:
                movie_scores[sim["movie_index"]] += sim["similarity_score"]
        
        # Sort by score and get top recommendations
        sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        recommendations = []
        for movie_idx, score in sorted_movies:
            recommendations.append({
                "movie_index": movie_idx,
                "score": score / len(liked_movies)  # Normalize by number of liked movies
            })
        
        return recommendations

# Initialize recommendation engine
recommendation_engine = MovieRecommendationEngine()

# Database operations
def get_movies_from_db(db: Connection, limit: int = None) -> List[Movie]:
    """Get movies from database"""
    cursor = db.cursor()
    query = "SELECT * FROM movies ORDER BY popularity DESC"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    movies = []
    for row in rows:
        movies.append(Movie(
            id=row["id"],
            tmdb_id=row["tmdb_id"],
            title=row["title"],
            overview=row["overview"],
            genres=json.loads(row["genres"]) if row["genres"] else [],
            release_date=row["release_date"],
            runtime=row["runtime"],
            vote_average=row["vote_average"],
            vote_count=row["vote_count"],
            popularity=row["popularity"],
            poster_path=row["poster_path"],
            backdrop_path=row["backdrop_path"],
            original_language=row["original_language"],
            budget=row["budget"],
            revenue=row["revenue"],
            tagline=row["tagline"],
            keywords=json.loads(row["keywords"]) if row["keywords"] else [],
            cast=json.loads(row["cast"]) if row["cast"] else [],
            crew=json.loads(row["crew"]) if row["crew"] else [],
            production_companies=json.loads(row["production_companies"]) if row["production_companies"] else [],
            production_countries=json.loads(row["production_countries"]) if row["production_countries"] else [],
            spoken_languages=json.loads(row["spoken_languages"]) if row["spoken_languages"] else [],
            status=row["status"],
            adult=bool(row["adult"]),
            video=bool(row["video"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        ))
    
    return movies

def save_movie_to_db(db: Connection, movie_data: Dict[str, Any]) -> int:
    """Save movie to database"""
    cursor = db.cursor()
    
    # Convert lists to JSON
    json_fields = ['genres', 'keywords', 'cast', 'crew', 'production_companies', 'production_countries', 'spoken_languages']
    for field in json_fields:
        if field in movie_data and isinstance(movie_data[field], list):
            movie_data[field] = json.dumps(movie_data[field])
    
    cursor.execute('''
        INSERT OR REPLACE INTO movies (
            tmdb_id, title, overview, genres, release_date, runtime, vote_average,
            vote_count, popularity, poster_path, backdrop_path, original_language,
            budget, revenue, tagline, keywords, cast, crew, production_companies,
            production_countries, spoken_languages, status, adult, video
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        movie_data.get("id"),
        movie_data.get("title"),
        movie_data.get("overview"),
        movie_data.get("genres"),
        movie_data.get("release_date"),
        movie_data.get("runtime"),
        movie_data.get("vote_average"),
        movie_data.get("vote_count"),
        movie_data.get("popularity"),
        movie_data.get("poster_path"),
        movie_data.get("backdrop_path"),
        movie_data.get("original_language"),
        movie_data.get("budget"),
        movie_data.get("revenue"),
        movie_data.get("tagline"),
        movie_data.get("keywords"),
        movie_data.get("cast"),
        movie_data.get("crew"),
        movie_data.get("production_companies"),
        movie_data.get("production_countries"),
        movie_data.get("spoken_languages"),
        movie_data.get("status"),
        movie_data.get("adult", False),
        movie_data.get("video", False)
    ))
    
    movie_id = cursor.lastrowid
    db.commit()
    return movie_id

def get_user_preferences(db: Connection, user_id: str) -> List[UserPreference]:
    """Get user preferences from database"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    
    preferences = []
    for row in rows:
        preferences.append(UserPreference(
            id=row["id"],
            user_id=row["user_id"],
            movie_id=row["movie_id"],
            rating=row["rating"],
            favorite=bool(row["favorite"]),
            watchlist=bool(row["watchlist"]),
            watched=bool(row["watched"]),
            created_at=row["created_at"]
        ))
    
    return preferences

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Movie Recommendation API", "version": "1.0.0"}

# Movie Search
@app.get("/movies/search", response_model=SearchResult)
async def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    db: Connection = Depends(get_db)
):
    """Search movies by title"""
    try:
        # Search TMDB API
        tmdb_results = tmdb_service.search_movies(query, page)
        
        # Save movies to database
        movies = []
        for movie_data in tmdb_results.get("results", []):
            try:
                # Get detailed movie information
                detailed_movie = tmdb_service.get_movie_details(movie_data["id"])
                save_movie_to_db(db, detailed_movie)
                
                movie = Movie(
                    tmdb_id=detailed_movie["id"],
                    title=detailed_movie["title"],
                    overview=detailed_movie.get("overview"),
                    genres=[genre["name"] for genre in detailed_movie.get("genres", [])],
                    release_date=detailed_movie.get("release_date"),
                    runtime=detailed_movie.get("runtime"),
                    vote_average=detailed_movie.get("vote_average"),
                    vote_count=detailed_movie.get("vote_count"),
                    popularity=detailed_movie.get("popularity"),
                    poster_path=detailed_movie.get("poster_path"),
                    backdrop_path=detailed_movie.get("backdrop_path"),
                    original_language=detailed_movie.get("original_language"),
                    budget=detailed_movie.get("budget"),
                    revenue=detailed_movie.get("revenue"),
                    tagline=detailed_movie.get("tagline"),
                    keywords=detailed_movie.get("keywords", []),
                    cast=detailed_movie.get("cast", []),
                    crew=detailed_movie.get("crew", []),
                    production_companies=[company["name"] for company in detailed_movie.get("production_companies", [])],
                    production_countries=[country["name"] for country in detailed_movie.get("production_countries", [])],
                    spoken_languages=[lang["english_name"] for lang in detailed_movie.get("spoken_languages", [])],
                    status=detailed_movie.get("status"),
                    adult=detailed_movie.get("adult", False),
                    video=detailed_movie.get("video", False)
                )
                movies.append(movie)
            except Exception as e:
                print(f"Error saving movie {movie_data['id']}: {e}")
                continue
        
        return SearchResult(
            movies=movies,
            total_results=tmdb_results.get("total_results", 0),
            total_pages=tmdb_results.get("total_pages", 0),
            current_page=tmdb_results.get("page", page)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Movie Details
@app.get("/movies/{movie_id}", response_model=Movie)
async def get_movie_details(movie_id: int, db: Connection = Depends(get_db)):
    """Get detailed movie information"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM movies WHERE tmdb_id = ?", (movie_id,))
    row = cursor.fetchone()
    
    if row:
        # Return from database
        return Movie(
            id=row["id"],
            tmdb_id=row["tmdb_id"],
            title=row["title"],
            overview=row["overview"],
            genres=json.loads(row["genres"]) if row["genres"] else [],
            release_date=row["release_date"],
            runtime=row["runtime"],
            vote_average=row["vote_average"],
            vote_count=row["vote_count"],
            popularity=row["popularity"],
            poster_path=row["poster_path"],
            backdrop_path=row["backdrop_path"],
            original_language=row["original_language"],
            budget=row["budget"],
            revenue=row["revenue"],
            tagline=row["tagline"],
            keywords=json.loads(row["keywords"]) if row["keywords"] else [],
            cast=json.loads(row["cast"]) if row["cast"] else [],
            crew=json.loads(row["crew"]) if row["crew"] else [],
            production_companies=json.loads(row["production_companies"]) if row["production_companies"] else [],
            production_countries=json.loads(row["production_countries"]) if row["production_countries"] else [],
            spoken_languages=json.loads(row["spoken_languages"]) if row["spoken_languages"] else [],
            status=row["status"],
            adult=bool(row["adult"]),
            video=bool(row["video"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
    else:
        # Fetch from TMDB and save to database
        try:
            movie_data = tmdb_service.get_movie_details(movie_id)
            save_movie_to_db(db, movie_data)
            
            return Movie(
                tmdb_id=movie_data["id"],
                title=movie_data["title"],
                overview=movie_data.get("overview"),
                genres=[genre["name"] for genre in movie_data.get("genres", [])],
                release_date=movie_data.get("release_date"),
                runtime=movie_data.get("runtime"),
                vote_average=movie_data.get("vote_average"),
                vote_count=movie_data.get("vote_count"),
                popularity=movie_data.get("popularity"),
                poster_path=movie_data.get("poster_path"),
                backdrop_path=movie_data.get("backdrop_path"),
                original_language=movie_data.get("original_language"),
                budget=movie_data.get("budget"),
                revenue=movie_data.get("revenue"),
                tagline=movie_data.get("tagline"),
                keywords=movie_data.get("keywords", []),
                cast=movie_data.get("cast", []),
                crew=movie_data.get("crew", []),
                production_companies=[company["name"] for company in movie_data.get("production_companies", [])],
                production_countries=[country["name"] for country in movie_data.get("production_countries", [])],
                spoken_languages=[lang["english_name"] for lang in movie_data.get("spoken_languages", [])],
                status=movie_data.get("status"),
                adult=movie_data.get("adult", False),
                video=movie_data.get("video", False)
            )
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Movie not found: {str(e)}")

# Recommendations
@app.get("/recommendations/similar/{movie_id}", response_model=RecommendationResponse)
async def get_similar_movies(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Connection = Depends(get_db)
):
    """Get similar movies using cosine similarity"""
    try:
        # Get movies from database
        movies = get_movies_from_db(db)
        
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found in database")
        
        # Build feature matrix if not already built
        if recommendation_engine.feature_matrix is None:
            recommendation_engine.build_feature_matrix(movies)
        
        # Calculate similarities
        similar_movies = recommendation_engine.calculate_similarity(movie_id, limit)
        
        recommendations = []
        for sim in similar_movies:
            movie_idx = sim["movie_index"]
            if movie_idx < len(movies):
                movie = movies[movie_idx]
                recommendations.append(Recommendation(
                    movie_id=movie.tmdb_id,
                    title=movie.title,
                    score=sim["similarity_score"],
                    reason="Similar content and themes",
                    poster_path=movie.poster_path,
                    release_date=movie.release_date,
                    vote_average=movie.vote_average
                ))
        
        return RecommendationResponse(
            movie_id=movie_id,
            type=RecommendationType.SIMILAR,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get similar movies: {str(e)}")

@app.get("/recommendations/genre/{genre}", response_model=RecommendationResponse)
async def get_genre_recommendations(
    genre: str,
    limit: int = Query(10, ge=1, le=50),
    db: Connection = Depends(get_db)
):
    """Get genre-based recommendations"""
    try:
        movies = get_movies_from_db(db)
        
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found in database")
        
        # Get genre-based recommendations
        genre_recs = recommendation_engine.get_genre_based_recommendations([genre], movies, limit)
        
        recommendations = []
        for rec in genre_recs:
            movie = rec["movie"]
            recommendations.append(Recommendation(
                movie_id=movie.tmdb_id,
                title=movie.title,
                score=rec["score"],
                reason=f"Popular in {genre} genre",
                poster_path=movie.poster_path,
                release_date=movie.release_date,
                vote_average=movie.vote_average
            ))
        
        return RecommendationResponse(
            type=RecommendationType.GENRE_BASED,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get genre recommendations: {str(e)}")

@app.get("/recommendations/trending", response_model=RecommendationResponse)
async def get_trending_movies(
    time_window: TrendingType = TrendingType.DAY,
    limit: int = Query(10, ge=1, le=50),
    db: Connection = Depends(get_db)
):
    """Get trending movies from TMDB"""
    try:
        # Get trending movies from TMDB
        trending_data = tmdb_service.get_trending_movies(time_window.value)
        
        recommendations = []
        for movie_data in trending_data.get("results", [])[:limit]:
            # Save to database
            try:
                detailed_movie = tmdb_service.get_movie_details(movie_data["id"])
                save_movie_to_db(db, detailed_movie)
            except:
                pass  # Continue even if saving fails
            
            recommendations.append(Recommendation(
                movie_id=movie_data["id"],
                title=movie_data["title"],
                score=movie_data.get("popularity", 0) / 100,  # Normalize popularity
                reason=f"Trending {time_window.value}",
                poster_path=movie_data.get("poster_path"),
                release_date=movie_data.get("release_date"),
                vote_average=movie_data.get("vote_average")
            ))
        
        return RecommendationResponse(
            type=RecommendationType.TRENDING,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending movies: {str(e)}")

@app.get("/recommendations/popular", response_model=RecommendationResponse)
async def get_popular_movies(
    limit: int = Query(10, ge=1, le=50),
    db: Connection = Depends(get_db)
):
    """Get popular movies"""
    try:
        popular_data = tmdb_service.get_popular_movies()
        
        recommendations = []
        for movie_data in popular_data.get("results", [])[:limit]:
            # Save to database
            try:
                detailed_movie = tmdb_service.get_movie_details(movie_data["id"])
                save_movie_to_db(db, detailed_movie)
            except:
                pass
            
            recommendations.append(Recommendation(
                movie_id=movie_data["id"],
                title=movie_data["title"],
                score=movie_data.get("popularity", 0) / 100,
                reason="Popular among viewers",
                poster_path=movie_data.get("poster_path"),
                release_date=movie_data.get("release_date"),
                vote_average=movie_data.get("vote_average")
            ))
        
        return RecommendationResponse(
            type=RecommendationType.POPULAR,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular movies: {str(e)}")

@app.get("/recommendations/top-rated", response_model=RecommendationResponse)
async def get_top_rated_movies(
    limit: int = Query(10, ge=1, le=50),
    db: Connection = Depends(get_db)
):
    """Get top rated movies"""
    try:
        top_rated_data = tmdb_service.get_top_rated_movies()
        
        recommendations = []
        for movie_data in top_rated_data.get("results", [])[:limit]:
            # Save to database
            try:
                detailed_movie = tmdb_service.get_movie_details(movie_data["id"])
                save_movie_to_db(db, detailed_movie)
            except:
                pass
            
            recommendations.append(Recommendation(
                movie_id=movie_data["id"],
                title=movie_data["title"],
                score=movie_data.get("vote_average", 0) / 10,  # Normalize rating
                reason="Highly rated by critics and users",
                poster_path=movie_data.get("poster_path"),
                release_date=movie_data.get("release_date"),
                vote_average=movie_data.get("vote_average")
            ))
        
        return RecommendationResponse(
            type=RecommendationType.TOP_RATED,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top rated movies: {str(e)}")

# User Preferences
@app.post("/users/{user_id}/preferences", response_model=UserPreference)
async def create_user_preference(
    user_id: str,
    preference: UserPreference,
    db: Connection = Depends(get_db)
):
    """Create or update user preference"""
    cursor = db.cursor()
    
    # Check if preference already exists
    cursor.execute(
        "SELECT id FROM user_preferences WHERE user_id = ? AND movie_id = ?",
        (user_id, preference.movie_id)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing preference
        cursor.execute('''
            UPDATE user_preferences 
            SET rating = ?, favorite = ?, watchlist = ?, watched = ?
            WHERE user_id = ? AND movie_id = ?
        ''', (
            preference.rating,
            preference.favorite,
            preference.watchlist,
            preference.watched,
            user_id,
            preference.movie_id
        ))
        
        preference_id = existing["id"]
    else:
        # Create new preference
        cursor.execute('''
            INSERT INTO user_preferences (id, user_id, movie_id, rating, favorite, watchlist, watched)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            preference.id,
            user_id,
            preference.movie_id,
            preference.rating,
            preference.favorite,
            preference.watchlist,
            preference.watched
        ))
        
        preference_id = preference.id
    
    db.commit()
    preference.id = preference_id
    preference.user_id = user_id
    
    return preference

@app.get("/users/{user_id}/preferences", response_model=List[UserPreference])
async def get_user_preferences(user_id: str, db: Connection = Depends(get_db)):
    """Get all user preferences"""
    return get_user_preferences(db, user_id)

@app.get("/users/{user_id}/recommendations/personalized", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Connection = Depends(get_db)
):
    """Get personalized recommendations based on user preferences"""
    try:
        # Get user preferences
        user_prefs = get_user_preferences(db, user_id)
        
        if not user_prefs:
            raise HTTPException(status_code=404, detail="No user preferences found")
        
        # Get movies from database
        movies = get_movies_from_db(db)
        
        if not movies:
            raise HTTPException(status_code=404, detail="No movies found in database")
        
        # Build feature matrix if not already built
        if recommendation_engine.feature_matrix is None:
            recommendation_engine.build_feature_matrix(movies)
        
        # Get personalized recommendations
        personalized_recs = recommendation_engine.get_personalized_recommendations(user_prefs, movies, limit)
        
        recommendations = []
        for rec in personalized_recs:
            movie_idx = rec["movie_index"]
            if movie_idx < len(movies):
                movie = movies[movie_idx]
                recommendations.append(Recommendation(
                    movie_id=movie.tmdb_id,
                    title=movie.title,
                    score=rec["score"],
                    reason="Based on your viewing history and preferences",
                    poster_path=movie.poster_path,
                    release_date=movie.release_date,
                    vote_average=movie.vote_average
                ))
        
        return RecommendationResponse(
            user_id=user_id,
            type=RecommendationType.PERSONALIZED,
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get personalized recommendations: {str(e)}")

# Utility endpoints
@app.get("/genres")
async def get_genres():
    """Get all available genres"""
    try:
        genres_data = tmdb_service.get_genres()
        return {"genres": genres_data.get("genres", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get genres: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "tmdb_api": "connected" if TMDB_API_KEY != "your_tmdb_api_key" else "not_configured"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8013)
