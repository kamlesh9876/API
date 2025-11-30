# Fitness Tracker API

A comprehensive fitness tracking API with calorie tracking, workout logging, progress analytics, and personalized goal suggestions. Built with FastAPI and SQLite for efficient data management.

## 🚀 Features

- **User Management**: Profile management with personal metrics and goals
- **Workout Tracking**: Log exercises, sets, reps, duration, and calories burned
- **Nutrition Tracking**: Track calories, macronutrients, and meal types
- **Weight Monitoring**: Log weight changes and track progress
- **BMI Calculation**: Automatic BMI calculation with health recommendations
- **Calorie Planning**: BMR and TDEE calculations with personalized targets
- **Progress Analytics**: Comprehensive analytics for workouts and nutrition
- **Goal Suggestions**: AI-powered personalized fitness goals
- **Exercise Database**: Track various exercises with detailed metrics
- **Time-based Analytics**: Weekly, monthly, and yearly progress reports
- **Health Insights**: Personalized recommendations based on user data

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (lightweight, file-based)
- **Data Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Health Tracking**: Scientific calculations and formulas

## 📋 Prerequisites

- Python 3.7+
- pip package manager
- No external database required (SQLite included)

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8010`

3. **Database**: SQLite database (`fitness_tracker.db`) will be created automatically

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8010/docs`
- ReDoc: `http://localhost:8010/redoc`

## 🏃‍♂️ API Endpoints

### User Management

#### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "height": 175.5,
  "weight": 70.0,
  "activity_level": "moderate",
  "goal": "maintain"
}
```

#### Get User
```http
GET /users/{user_id}
```

#### Update User
```http
PUT /users/{user_id}
Content-Type: application/json

{
  "weight": 68.5,
  "activity_level": "active"
}
```

### Workout Tracking

#### Create Workout
```http
POST /workouts
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Morning Strength Training",
  "type": "strength",
  "duration_minutes": 45,
  "calories_burned": 250,
  "intensity": "moderate",
  "date": "2024-01-15",
  "exercises": [
    {
      "workout_id": "workout_123",
      "name": "Bench Press",
      "sets": 3,
      "reps": 10,
      "weight": 60.0,
      "notes": "Good form"
    },
    {
      "workout_id": "workout_123",
      "name": "Squats",
      "sets": 4,
      "reps": 12,
      "weight": 80.0
    }
  ]
}
```

#### Get Workouts
```http
GET /workouts?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31&workout_type=strength&limit=20
```

**Response Example**:
```json
[
  {
    "id": "workout_123",
    "user_id": "user_123",
    "name": "Morning Strength Training",
    "type": "strength",
    "duration_minutes": 45,
    "calories_burned": 250,
    "intensity": "moderate",
    "notes": "Great workout!",
    "date": "2024-01-15",
    "exercises": [
      {
        "id": "ex_123",
        "workout_id": "workout_123",
        "name": "Bench Press",
        "sets": 3,
        "reps": 10,
        "weight": 60.0,
        "notes": "Good form"
      }
    ],
    "created_at": "2024-01-15T08:00:00"
  }
]
```

#### Get Specific Workout
```http
GET /workouts/{workout_id}
```

#### Delete Workout
```http
DELETE /workouts/{workout_id}
```

### Nutrition Tracking

#### Create Food Entry
```http
POST /food-entries
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Grilled Chicken Salad",
  "calories": 350,
  "protein": 35.0,
  "carbs": 15.0,
  "fat": 12.0,
  "fiber": 8.0,
  "sugar": 5.0,
  "sodium": 600,
  "serving_size": "1 bowl",
  "quantity": 1,
  "meal_type": "lunch",
  "date": "2024-01-15"
}
```

#### Get Food Entries
```http
GET /food-entries?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31&meal_type=lunch&limit=50
```

#### Delete Food Entry
```http
DELETE /food-entries/{entry_id}
```

### Weight Tracking

#### Create Weight Log
```http
POST /weight-logs
Content-Type: application/json

{
  "user_id": "user_123",
  "weight": 68.5,
  "date": "2024-01-15",
  "notes": "Morning weight after workout"
}
```

#### Get Weight Logs
```http
GET /weight-logs?user_id=user_123&start_date=2024-01-01&end_date=2024-01-31&limit=50
```

### Goals

#### Create Goal
```http
POST /goals
Content-Type: application/json

{
  "user_id": "user_123",
  "type": "weight_loss",
  "target_value": 65.0,
  "current_value": 70.0,
  "unit": "kg",
  "target_date": "2024-06-01",
  "is_active": true
}
```

#### Get Goals
```http
GET /goals?user_id=user_123&active_only=true
```

### Analytics

#### Calculate BMI
```http
GET /analytics/bmi?user_id=user_123
```

**Response Example**:
```json
{
  "bmi": 22.2,
  "category": "Normal weight",
  "status": "Maintain your healthy weight with balanced diet and regular exercise",
  "recommendations": [
    "Continue regular physical activity (150+ minutes per week)",
    "Maintain balanced macronutrient intake",
    "Focus on consistency in diet and exercise",
    "Consider setting fitness performance goals"
  ]
}
```

#### Calculate Calorie Needs
```http
GET /analytics/calories?user_id=user_123
```

**Response Example**:
```json
{
  "bmr": 1650,
  "tdee": 2555,
  "goal_calories": 2055,
  "protein_grams": 128.4,
  "carbs_grams": 231.9,
  "fat_grams": 68.5
}
```

#### Get Progress Analytics
```http
GET /analytics/progress?user_id=user_123&period=week
```

**Response Example**:
```json
{
  "period": "week",
  "start_date": "2024-01-08",
  "end_date": "2024-01-15",
  "total_workouts": 4,
  "total_duration": 180,
  "total_calories_burned": 1200,
  "total_calories_consumed": 14350,
  "net_calories": 13150,
  "weight_change": -0.3,
  "workout_frequency": 4.0,
  "avg_workout_duration": 45.0,
  "top_exercises": [
    {
      "name": "Bench Press",
      "count": 4,
      "total_sets": 12
    },
    {
      "name": "Squats",
      "count": 4,
      "total_sets": 16
    }
  ],
  "nutrition_breakdown": {
    "protein": 514.0,
    "carbs": 771.6,
    "fat": 514.0
  }
}
```

#### Get Goal Suggestions
```http
GET /suggestions/goals?user_id=user_123
```

**Response Example**:
```json
[
  {
    "type": "weight_loss",
    "title": "Weight Loss Journey",
    "description": "Lose weight safely through diet and exercise",
    "target_value": 63.0,
    "unit": "kg",
    "estimated_timeline": "3-4 months",
    "difficulty": "Moderate",
    "action_steps": [
      "Create 500-calorie daily deficit",
      "Exercise 300+ minutes per week",
      "Track calories and macros",
      "Focus on whole foods"
    ]
  },
  {
    "type": "cardio_endurance",
    "title": "Improve Cardio Endurance",
    "description": "Build cardiovascular fitness through regular cardio exercise",
    "target_value": 150,
    "unit": "minutes/week",
    "estimated_timeline": "8-12 weeks",
    "difficulty": "Moderate",
    "action_steps": [
      "Start with 20-30 minute sessions, 3x per week",
      "Gradually increase duration and intensity",
      "Mix running, cycling, and swimming",
      "Include interval training once per week"
    ]
  }
]
```

## 📊 Data Models

### User
```json
{
  "id": "user_123",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "height": 175.5,
  "weight": 70.0,
  "activity_level": "moderate",
  "goal": "maintain",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-15T12:00:00"
}
```

### Workout
```json
{
  "id": "workout_123",
  "user_id": "user_123",
  "name": "Morning Strength Training",
  "type": "strength",
  "duration_minutes": 45,
  "calories_burned": 250,
  "intensity": "moderate",
  "notes": "Great workout!",
  "date": "2024-01-15",
  "exercises": [...],
  "created_at": "2024-01-15T08:00:00"
}
```

### Food Entry
```json
{
  "id": "food_123",
  "user_id": "user_123",
  "name": "Grilled Chicken Salad",
  "calories": 350,
  "protein": 35.0,
  "carbs": 15.0,
  "fat": 12.0,
  "fiber": 8.0,
  "sugar": 5.0,
  "sodium": 600,
  "serving_size": "1 bowl",
  "quantity": 1,
  "meal_type": "lunch",
  "date": "2024-01-15",
  "created_at": "2024-01-15T12:30:00"
}
```

## 🧪 Testing Examples

### Create User and Track Progress
```bash
# Create user
curl -X POST "http://localhost:8010/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fitness_user",
    "email": "user@example.com",
    "first_name": "Alex",
    "last_name": "Smith",
    "date_of_birth": "1992-05-20",
    "gender": "female",
    "height": 165.0,
    "weight": 65.0,
    "activity_level": "moderate",
    "goal": "lose_weight"
  }'

# Log workout
curl -X POST "http://localhost:8010/workouts" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "name": "Evening Run",
    "type": "cardio",
    "duration_minutes": 30,
    "calories_burned": 300,
    "intensity": "moderate",
    "date": "2024-01-15"
  }'

# Log meal
curl -X POST "http://localhost:8010/food-entries" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "name": "Oatmeal with Berries",
    "calories": 280,
    "protein": 8.0,
    "carbs": 45.0,
    "fat": 6.0,
    "fiber": 10.0,
    "meal_type": "breakfast",
    "date": "2024-01-15"
  }'

# Get analytics
curl "http://localhost:8010/analytics/progress?user_id=user_123&period=week"

# Get BMI
curl "http://localhost:8010/analytics/bmi?user_id=user_123"

# Get calorie needs
curl "http://localhost:8010/analytics/calories?user_id=user_123"
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Database Configuration
DATABASE_URL=fitness_tracker.db
DATABASE_BACKUP_ENABLED=true
DATABASE_BACKUP_INTERVAL=3600  # seconds

# API Configuration
HOST=0.0.0.0
PORT=8010
DEBUG=false

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/fitness_api.log
LOG_ROTATION=daily

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Data Retention
DATA_RETENTION_DAYS=365
CLEANUP_INTERVAL=86400  # seconds
```

### Database Schema
The SQLite database includes the following tables:

- **users**: User profiles and personal information
- **workouts**: Workout sessions with duration and calories
- **exercises**: Individual exercises within workouts
- **food_entries**: Nutrition tracking with macros
- **weight_logs**: Weight tracking over time
- **goals**: Personal fitness goals

### Advanced Configuration
```python
# Custom settings
FITNESS_CONFIG = {
    "bmi_categories": {
        "underweight": {"min": 0, "max": 18.5},
        "normal": {"min": 18.5, "max": 25},
        "overweight": {"min": 25, "max": 30},
        "obese": {"min": 30, "max": 100}
    },
    "activity_multipliers": {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    },
    "macro_ratios": {
        "lose_weight": {"protein": 0.3, "carbs": 0.4, "fat": 0.3},
        "maintain": {"protein": 0.25, "carbs": 0.45, "fat": 0.3},
        "gain_muscle": {"protein": 0.4, "carbs": 0.4, "fat": 0.2}
    }
}
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8010

# Create data directory for SQLite database
RUN mkdir -p /app/data

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  fitness-api:
    build: .
    ports:
      - "8010:8010"
    environment:
      - DATABASE_URL=/app/data/fitness_tracker.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - fitness-api
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fitness-tracker-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fitness-tracker-api
  template:
    metadata:
      labels:
        app: fitness-tracker-api
    spec:
      containers:
      - name: api
        image: fitness-tracker-api:latest
        ports:
        - containerPort: 8010
        env:
        - name: DATABASE_URL
          value: "/app/data/fitness_tracker.db"
        volumeMounts:
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: fitness-data-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fitness-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## 📈 Advanced Features

### Workout Plans
```python
class WorkoutPlan(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    duration_weeks: int
    difficulty: str
    workouts: List[Dict[str, Any]]
    rest_days: List[int]

@app.post("/workout-plans")
async def create_workout_plan(plan: WorkoutPlan):
    """Create personalized workout plan"""
    pass
```

### Nutrition Plans
```python
class NutritionPlan(BaseModel):
    id: str
    user_id: str
    name: str
    daily_calories: float
    macro_targets: Dict[str, float]
    meal_templates: List[Dict[str, Any]]

@app.post("/nutrition-plans")
async def create_nutrition_plan(plan: NutritionPlan):
    """Create personalized nutrition plan"""
    pass
```

### Achievement System
```python
class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    criteria: Dict[str, Any]
    points: int

@app.get("/achievements")
async def get_user_achievements(user_id: str):
    """Get user achievements and progress"""
    pass
```

### Social Features
```python
class WorkoutShare(BaseModel):
    workout_id: str
    shared_with: List[str]
    message: Optional[str] = None

@app.post("/workouts/{workout_id}/share")
async def share_workout(workout_id: str, share: WorkoutShare):
    """Share workout with friends"""
    pass
```

## 🛡️ Security Features

### Authentication
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(credentials: str = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Data Privacy
```python
# GDPR compliance features
@app.delete("/users/{user_id}/data")
async def delete_user_data(user_id: str):
    """Delete all user data (GDPR right to be forgotten)"""
    pass

@app.get("/users/{user_id}/data-export")
async def export_user_data(user_id: str):
    """Export user data in JSON format"""
    pass
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
workouts_logged = Counter('fitness_workouts_logged_total', 'Total workouts logged')
calories_tracked = Counter('fitness_calories_tracked_total', 'Total calories tracked')
active_users = Gauge('fitness_active_users', 'Active users')
api_response_time = Histogram('fitness_api_response_seconds', 'API response time')
```

### Health Monitoring
```python
@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check with database status"""
    try:
        # Test database connection
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": user_count,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
```

## 🔮 Future Enhancements

### Planned Features
- **Workout Videos**: Integration with exercise video libraries
- **Meal Planning**: Automated meal plan generation
- **Social Features**: Friend system and workout sharing
- **Wearable Integration**: Connect with fitness trackers
- **AI Coach**: Personalized AI-powered coaching
- **Challenges**: Fitness challenges and competitions
- **Progress Photos**: Visual progress tracking
- **Heart Rate Zones**: Advanced cardio analytics
- **Sleep Tracking**: Integration with sleep data
- **Hydration Tracking**: Water intake monitoring

### AI Integration
- **Exercise Recognition**: AI-powered exercise detection
- **Nutrition Analysis**: Food photo recognition
- **Personalized Recommendations**: ML-based suggestions
- **Injury Prevention**: Risk assessment and prevention
- **Performance Prediction**: Future performance forecasting

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review SQLite documentation for database management
- Consult health professionals for medical advice

---

**Built with ❤️ using FastAPI and SQLite**
