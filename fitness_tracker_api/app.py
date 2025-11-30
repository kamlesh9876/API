from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from enum import Enum
import uuid
import sqlite3
from sqlite3 import Connection
import json
from decimal import Decimal
import math

app = FastAPI(title="Fitness Tracker API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "fitness_tracker.db"

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
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            date_of_birth DATE,
            gender TEXT CHECK(gender IN ('male', 'female', 'other')),
            height REAL,  -- in cm
            weight REAL,  -- in kg
            activity_level TEXT CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
            goal TEXT CHECK(goal IN ('lose_weight', 'maintain', 'gain_muscle', 'improve_endurance')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Workouts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('cardio', 'strength', 'flexibility', 'sports', 'other')),
            duration_minutes INTEGER NOT NULL,
            calories_burned REAL,
            intensity TEXT CHECK(intensity IN ('low', 'moderate', 'high')),
            notes TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Exercises table (for workout details)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id TEXT PRIMARY KEY,
            workout_id TEXT NOT NULL,
            name TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,  -- in kg
            duration_seconds INTEGER,
            distance_meters REAL,
            notes TEXT,
            FOREIGN KEY (workout_id) REFERENCES workouts (id)
        )
    ''')
    
    # Food entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_entries (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL DEFAULT 0,  -- in grams
            carbs REAL DEFAULT 0,    -- in grams
            fat REAL DEFAULT 0,     -- in grams
            fiber REAL DEFAULT 0,   -- in grams
            sugar REAL DEFAULT 0,   -- in grams
            sodium REAL DEFAULT 0,  -- in mg
            serving_size TEXT,
            quantity REAL DEFAULT 1,
            meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Weight logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            weight REAL NOT NULL,  -- in kg
            date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT CHECK(type IN ('weight_loss', 'weight_gain', 'muscle_gain', 'endurance', 'strength', 'custom')),
            target_value REAL,
            current_value REAL DEFAULT 0,
            unit TEXT,
            target_date DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Enums
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class GoalType(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"
    IMPROVE_ENDURANCE = "improve_endurance"

class WorkoutType(str, Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    SPORTS = "sports"
    OTHER = "other"

class Intensity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

# Pydantic models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None  # cm
    weight: Optional[float] = None  # kg
    activity_level: Optional[ActivityLevel] = None
    goal: Optional[GoalType] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workout_id: str
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None  # kg
    duration_seconds: Optional[int] = None
    distance_meters: Optional[float] = None
    notes: Optional[str] = None

class Workout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    type: WorkoutType
    duration_minutes: int
    calories_burned: Optional[float] = None
    intensity: Optional[Intensity] = None
    notes: Optional[str] = None
    date: date
    exercises: List[Exercise] = []
    created_at: datetime = Field(default_factory=datetime.now)

class FoodEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    calories: float
    protein: float = 0  # grams
    carbs: float = 0    # grams
    fat: float = 0     # grams
    fiber: float = 0   # grams
    sugar: float = 0   # grams
    sodium: float = 0  # mg
    serving_size: Optional[str] = None
    quantity: float = 1
    meal_type: MealType
    date: date
    created_at: datetime = Field(default_factory=datetime.now)

class WeightLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    weight: float  # kg
    date: date
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: str
    target_value: float
    current_value: float = 0
    unit: str
    target_date: Optional[date] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class BMICalculation(BaseModel):
    bmi: float
    category: str
    status: str
    recommendations: List[str]

class CalorieCalculation(BaseModel):
    bmr: float  # Basal Metabolic Rate
    tdee: float  # Total Daily Energy Expenditure
    goal_calories: float  # Calories for goal
    protein_grams: float
    carbs_grams: float
    fat_grams: float

class ProgressAnalytics(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_workouts: int
    total_duration: int  # minutes
    total_calories_burned: float
    total_calories_consumed: float
    net_calories: float
    weight_change: Optional[float] = None  # kg
    workout_frequency: float  # workouts per week
    avg_workout_duration: float  # minutes
    top_exercises: List[Dict[str, Any]]
    nutrition_breakdown: Dict[str, float]

class GoalSuggestion(BaseModel):
    type: str
    title: str
    description: str
    target_value: float
    unit: str
    estimated_timeline: str
    difficulty: str
    action_steps: List[str]

# Helper functions
def calculate_bmi(weight_kg: float, height_cm: float) -> BMICalculation:
    """Calculate BMI and provide recommendations"""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
        status = "Consider gaining weight through balanced nutrition and strength training"
        recommendations = [
            "Increase calorie intake with nutrient-dense foods",
            "Focus on strength training to build muscle mass",
            "Consult with a nutritionist for personalized meal plans",
            "Ensure adequate protein intake (1.6-2.2g per kg body weight)"
        ]
    elif bmi < 25:
        category = "Normal weight"
        status = "Maintain your healthy weight with balanced diet and regular exercise"
        recommendations = [
            "Continue regular physical activity (150+ minutes per week)",
            "Maintain balanced macronutrient intake",
            "Focus on consistency in diet and exercise",
            "Consider setting fitness performance goals"
        ]
    elif bmi < 30:
        category = "Overweight"
        status = "Consider gradual weight loss through diet and exercise"
        recommendations = [
            "Create moderate calorie deficit (500 calories/day)",
            "Increase physical activity to 300+ minutes per week",
            "Focus on whole foods and reduce processed foods",
            "Consider tracking calories and macronutrients"
        ]
    else:
        category = "Obese"
        status = "Consult with healthcare provider for comprehensive weight management plan"
        recommendations = [
            "Seek professional medical guidance",
            "Start with gentle exercise and gradually increase intensity",
            "Focus on sustainable dietary changes",
            "Consider working with registered dietitian"
        ]
    
    return BMICalculation(
        bmi=round(bmi, 1),
        category=category,
        status=status,
        recommendations=recommendations
    )

def calculate_calories(user: User) -> CalorieCalculation:
    """Calculate daily calorie needs based on user profile"""
    if not user.weight or not user.height or not user.date_of_birth or not user.gender:
        raise HTTPException(status_code=400, detail="Missing required user data for calorie calculation")
    
    age = (date.today() - user.date_of_birth).days // 365
    
    # Calculate BMR using Mifflin-St Jeor Equation
    if user.gender == Gender.MALE:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHT: 1.375,
        ActivityLevel.MODERATE: 1.55,
        ActivityLevel.ACTIVE: 1.725,
        ActivityLevel.VERY_ACTIVE: 1.9
    }
    
    tdee = bmr * activity_multipliers.get(user.activity_level or ActivityLevel.MODERATE, 1.55)
    
    # Adjust based on goals
    if user.goal == GoalType.LOSE_WEIGHT:
        goal_calories = tdee - 500  # 500 calorie deficit
    elif user.goal == GoalType.GAIN_MUSCLE:
        goal_calories = tdee + 300  # 300 calorie surplus
    else:
        goal_calories = tdee  # Maintenance
    
    # Macronutrient distribution (40% protein, 40% carbs, 20% fat for muscle gain)
    if user.goal == GoalType.GAIN_MUSCLE:
        protein_calories = goal_calories * 0.4
        carb_calories = goal_calories * 0.4
        fat_calories = goal_calories * 0.2
    else:
        protein_calories = goal_calories * 0.25
        carb_calories = goal_calories * 0.45
        fat_calories = goal_calories * 0.3
    
    protein_grams = protein_calories / 4
    carbs_grams = carb_calories / 4
    fat_grams = fat_calories / 9
    
    return CalorieCalculation(
        bmr=round(bmr, 0),
        tdee=round(tdee, 0),
        goal_calories=round(goal_calories, 0),
        protein_grams=round(protein_grams, 1),
        carbs_grams=round(carbs_grams, 1),
        fat_grams=round(fat_grams, 1)
    )

def generate_goal_suggestions(user: User) -> List[GoalSuggestion]:
    """Generate personalized goal suggestions based on user profile"""
    suggestions = []
    
    if user.weight and user.height:
        bmi_calc = calculate_bmi(user.weight, user.height)
        
        if bmi_calc.category == "Overweight":
            suggestions.append(GoSuggestion(
                type="weight_loss",
                title="Weight Loss Journey",
                description="Lose weight safely through diet and exercise",
                target_value=user.weight * 0.9,  # 10% weight loss
                unit="kg",
                estimated_timeline="3-4 months",
                difficulty="Moderate",
                action_steps=[
                    "Create 500-calorie daily deficit",
                    "Exercise 300+ minutes per week",
                    "Track calories and macros",
                    "Focus on whole foods"
                ]
            ))
        elif bmi_calc.category == "Underweight":
            suggestions.append(GoSuggestion(
                type="weight_gain",
                title="Healthy Weight Gain",
                description="Gain weight through balanced nutrition and strength training",
                target_value=user.weight * 1.1,  # 10% weight gain
                unit="kg",
                estimated_timeline="2-3 months",
                difficulty="Moderate",
                action_steps=[
                    "Create 300-500 calorie surplus",
                    "Strength training 3x per week",
                    "Focus on protein-rich foods",
                    "Ensure adequate rest and recovery"
                ]
            ))
    
    # Fitness goals
    suggestions.append(GoSuggestion(
        type="cardio_endurance",
        title="Improve Cardio Endurance",
        description="Build cardiovascular fitness through regular cardio exercise",
        target_value=150,  # minutes per week
        unit="minutes/week",
        estimated_timeline="8-12 weeks",
        difficulty="Moderate",
        action_steps=[
            "Start with 20-30 minute sessions, 3x per week",
            "Gradually increase duration and intensity",
            "Mix running, cycling, and swimming",
            "Include interval training once per week"
        ]
    ))
    
    suggestions.append(GoSuggestion(
        type="strength_training",
        title="Build Strength",
        description="Increase muscle strength through resistance training",
        target_value=3,  # sessions per week
        unit="sessions/week",
        estimated_timeline="6-8 weeks",
        difficulty="Moderate",
        action_steps=[
            "Full-body workouts 3x per week",
            "Focus on compound exercises",
            "Progressive overload principle",
            "Allow adequate recovery time"
        ]
    ))
    
    # Nutrition goals
    suggestions.append(GoSuggestion(
        type="protein_intake",
        title="Optimize Protein Intake",
        description="Ensure adequate protein for muscle maintenance and growth",
        target_value=user.weight * 1.6 if user.weight else 80,  # 1.6g per kg
        unit="grams/day",
        estimated_timeline="Immediate",
        difficulty="Easy",
        action_steps=[
            "Include protein in each meal",
            "Consider protein supplements if needed",
            "Track daily protein intake",
            "Focus on high-quality protein sources"
        ]
    ))
    
    return suggestions

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Fitness Tracker API", "version": "1.0.0"}

# Users
@app.post("/users", response_model=User)
async def create_user(user: User, db: Connection = Depends(get_db)):
    """Create a new user"""
    cursor = db.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (id, username, email, first_name, last_name, date_of_birth, 
                             gender, height, weight, activity_level, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user.id, user.username, user.email, user.first_name, user.last_name,
              user.date_of_birth, user.gender.value if user.gender else None,
              user.height, user.weight, 
              user.activity_level.value if user.activity_level else None,
              user.goal.value if user.goal else None))
        db.commit()
        return user
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, db: Connection = Depends(get_db)):
    """Get user by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        date_of_birth=row["date_of_birth"],
        gender=row["gender"],
        height=row["height"],
        weight=row["weight"],
        activity_level=row["activity_level"],
        goal=row["goal"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: Dict[str, Any], db: Connection = Depends(get_db)):
    """Update user information"""
    cursor = db.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build update query dynamically
    update_fields = []
    update_values = []
    
    for field, value in user_update.items():
        if field in ["username", "email", "first_name", "last_name", "date_of_birth", 
                    "gender", "height", "weight", "activity_level", "goal"]:
            update_fields.append(f"{field} = ?")
            update_values.append(value)
    
    if update_fields:
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now())
        update_values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        db.commit()
    
    # Return updated user
    return await get_user(user_id, db)

# Workouts
@app.post("/workouts", response_model=Workout)
async def create_workout(workout: Workout, db: Connection = Depends(get_db)):
    """Create a new workout"""
    cursor = db.cursor()
    
    # Insert workout
    cursor.execute('''
        INSERT INTO workouts (id, user_id, name, type, duration_minutes, 
                             calories_burned, intensity, notes, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (workout.id, workout.user_id, workout.name, workout.type.value,
          workout.duration_minutes, workout.calories_burned,
          workout.intensity.value if workout.intensity else None,
          workout.notes, workout.date))
    
    # Insert exercises
    for exercise in workout.exercises:
        cursor.execute('''
            INSERT INTO exercises (id, workout_id, name, sets, reps, weight, 
                                  duration_seconds, distance_meters, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (exercise.id, exercise.workout_id, exercise.name, exercise.sets,
              exercise.reps, exercise.weight, exercise.duration_seconds,
              exercise.distance_meters, exercise.notes))
    
    db.commit()
    return workout

@app.get("/workouts", response_model=List[Workout])
async def get_workouts(
    user_id: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    workout_type: Optional[WorkoutType] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Connection = Depends(get_db)
):
    """Get user's workouts with filtering"""
    cursor = db.cursor()
    
    query = "SELECT * FROM workouts WHERE user_id = ?"
    params = [user_id]
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    if workout_type:
        query += " AND type = ?"
        params.append(workout_type.value)
    
    query += " ORDER BY date DESC, created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    workouts = []
    for row in rows:
        # Get exercises for this workout
        cursor.execute("SELECT * FROM exercises WHERE workout_id = ?", (row["id"],))
        exercise_rows = cursor.fetchall()
        
        exercises = []
        for ex_row in exercise_rows:
            exercises.append(Exercise(
                id=ex_row["id"],
                workout_id=ex_row["workout_id"],
                name=ex_row["name"],
                sets=ex_row["sets"],
                reps=ex_row["reps"],
                weight=ex_row["weight"],
                duration_seconds=ex_row["duration_seconds"],
                distance_meters=ex_row["distance_meters"],
                notes=ex_row["notes"]
            ))
        
        workouts.append(Workout(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            type=row["type"],
            duration_minutes=row["duration_minutes"],
            calories_burned=row["calories_burned"],
            intensity=row["intensity"],
            notes=row["notes"],
            date=row["date"],
            exercises=exercises,
            created_at=row["created_at"]
        ))
    
    return workouts

@app.get("/workouts/{workout_id}", response_model=Workout)
async def get_workout(workout_id: str, db: Connection = Depends(get_db)):
    """Get workout by ID"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Get exercises
    cursor.execute("SELECT * FROM exercises WHERE workout_id = ?", (workout_id,))
    exercise_rows = cursor.fetchall()
    
    exercises = []
    for ex_row in exercise_rows:
        exercises.append(Exercise(
            id=ex_row["id"],
            workout_id=ex_row["workout_id"],
            name=ex_row["name"],
            sets=ex_row["sets"],
            reps=ex_row["reps"],
            weight=ex_row["weight"],
            duration_seconds=ex_row["duration_seconds"],
            distance_meters=ex_row["distance_meters"],
            notes=ex_row["notes"]
        ))
    
    return Workout(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        type=row["type"],
        duration_minutes=row["duration_minutes"],
        calories_burned=row["calories_burned"],
        intensity=row["intensity"],
        notes=row["notes"],
        date=row["date"],
        exercises=exercises,
        created_at=row["created_at"]
    )

@app.delete("/workouts/{workout_id}")
async def delete_workout(workout_id: str, db: Connection = Depends(get_db)):
    """Delete a workout"""
    cursor = db.cursor()
    
    # Delete exercises first
    cursor.execute("DELETE FROM exercises WHERE workout_id = ?", (workout_id,))
    
    # Delete workout
    cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db.commit()
    return {"message": "Workout deleted successfully"}

# Food Entries
@app.post("/food-entries", response_model=FoodEntry)
async def create_food_entry(food_entry: FoodEntry, db: Connection = Depends(get_db)):
    """Create a new food entry"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO food_entries (id, user_id, name, calories, protein, carbs, fat,
                                  fiber, sugar, sodium, serving_size, quantity, meal_type, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (food_entry.id, food_entry.user_id, food_entry.name, food_entry.calories,
          food_entry.protein, food_entry.carbs, food_entry.fat, food_entry.fiber,
          food_entry.sugar, food_entry.sodium, food_entry.serving_size,
          food_entry.quantity, food_entry.meal_type.value, food_entry.date))
    
    db.commit()
    return food_entry

@app.get("/food-entries", response_model=List[FoodEntry])
async def get_food_entries(
    user_id: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    meal_type: Optional[MealType] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Connection = Depends(get_db)
):
    """Get user's food entries with filtering"""
    cursor = db.cursor()
    
    query = "SELECT * FROM food_entries WHERE user_id = ?"
    params = [user_id]
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    if meal_type:
        query += " AND meal_type = ?"
        params.append(meal_type.value)
    
    query += " ORDER BY date DESC, created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    food_entries = []
    for row in rows:
        food_entries.append(FoodEntry(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            calories=row["calories"],
            protein=row["protein"],
            carbs=row["carbs"],
            fat=row["fat"],
            fiber=row["fiber"],
            sugar=row["sugar"],
            sodium=row["sodium"],
            serving_size=row["serving_size"],
            quantity=row["quantity"],
            meal_type=row["meal_type"],
            date=row["date"],
            created_at=row["created_at"]
        ))
    
    return food_entries

@app.delete("/food-entries/{entry_id}")
async def delete_food_entry(entry_id: str, db: Connection = Depends(get_db)):
    """Delete a food entry"""
    cursor = db.cursor()
    cursor.execute("DELETE FROM food_entries WHERE id = ?", (entry_id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Food entry not found")
    
    db.commit()
    return {"message": "Food entry deleted successfully"}

# Weight Logs
@app.post("/weight-logs", response_model=WeightLog)
async def create_weight_log(weight_log: WeightLog, db: Connection = Depends(get_db)):
    """Create a new weight log entry"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO weight_logs (id, user_id, weight, date, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (weight_log.id, weight_log.user_id, weight_log.weight, weight_log.date, weight_log.notes))
    
    db.commit()
    return weight_log

@app.get("/weight-logs", response_model=List[WeightLog])
async def get_weight_logs(
    user_id: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Connection = Depends(get_db)
):
    """Get user's weight logs"""
    cursor = db.cursor()
    
    query = "SELECT * FROM weight_logs WHERE user_id = ?"
    params = [user_id]
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    query += " ORDER BY date DESC, created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    weight_logs = []
    for row in rows:
        weight_logs.append(WeightLog(
            id=row["id"],
            user_id=row["user_id"],
            weight=row["weight"],
            date=row["date"],
            notes=row["notes"],
            created_at=row["created_at"]
        ))
    
    return weight_logs

# Goals
@app.post("/goals", response_model=Goal)
async def create_goal(goal: Goal, db: Connection = Depends(get_db)):
    """Create a new goal"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO goals (id, user_id, type, target_value, current_value, unit, target_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (goal.id, goal.user_id, goal.type, goal.target_value, goal.current_value,
          goal.unit, goal.target_date, goal.is_active))
    
    db.commit()
    return goal

@app.get("/goals", response_model=List[Goal])
async def get_goals(user_id: str = Query(...), active_only: bool = Query(False), db: Connection = Depends(get_db)):
    """Get user's goals"""
    cursor = db.cursor()
    
    query = "SELECT * FROM goals WHERE user_id = ?"
    params = [user_id]
    
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    goals = []
    for row in rows:
        goals.append(Goal(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            target_value=row["target_value"],
            current_value=row["current_value"],
            unit=row["unit"],
            target_date=row["target_date"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        ))
    
    return goals

# Analytics
@app.get("/analytics/bmi", response_model=BMICalculation)
async def calculate_bmi_endpoint(user_id: str, db: Connection = Depends(get_db)):
    """Calculate BMI for user"""
    cursor = db.cursor()
    cursor.execute("SELECT weight, height FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row or not row["weight"] or not row["height"]:
        raise HTTPException(status_code=400, detail="User weight and height required for BMI calculation")
    
    return calculate_bmi(row["weight"], row["height"])

@app.get("/analytics/calories", response_model=CalorieCalculation)
async def calculate_calories_endpoint(user_id: str, db: Connection = Depends(get_db)):
    """Calculate daily calorie needs for user"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        date_of_birth=row["date_of_birth"],
        gender=row["gender"],
        weight=row["weight"],
        height=row["height"],
        activity_level=row["activity_level"],
        goal=row["goal"]
    )
    
    return calculate_calories(user)

@app.get("/analytics/progress", response_model=ProgressAnalytics)
async def get_progress_analytics(
    user_id: str = Query(...),
    period: str = Query("week", regex="^(week|month|year)$"),
    db: Connection = Depends(get_db)
):
    """Get progress analytics for a time period"""
    cursor = db.cursor()
    
    # Calculate date range
    end_date = date.today()
    if period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    else:  # year
        start_date = end_date - timedelta(days=365)
    
    # Get workouts
    cursor.execute('''
        SELECT COUNT(*) as total_workouts, 
               SUM(duration_minutes) as total_duration,
               SUM(calories_burned) as total_calories_burned
        FROM workouts 
        WHERE user_id = ? AND date BETWEEN ? AND ?
    ''', (user_id, start_date, end_date))
    
    workout_stats = cursor.fetchone()
    
    # Get food entries
    cursor.execute('''
        SELECT SUM(calories) as total_calories,
               SUM(protein) as total_protein,
               SUM(carbs) as total_carbs,
               SUM(fat) as total_fat
        FROM food_entries 
        WHERE user_id = ? AND date BETWEEN ? AND ?
    ''', (user_id, start_date, end_date))
    
    nutrition_stats = cursor.fetchone()
    
    # Get weight change
    cursor.execute('''
        SELECT weight FROM weight_logs 
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
    ''', (user_id, start_date, end_date))
    
    weight_logs = cursor.fetchall()
    weight_change = None
    if len(weight_logs) >= 2:
        weight_change = weight_logs[-1]["weight"] - weight_logs[0]["weight"]
    
    # Calculate workout frequency
    days_in_period = (end_date - start_date).days + 1
    workout_frequency = (workout_stats["total_workouts"] / days_in_period) * 7 if workout_stats["total_workouts"] > 0 else 0
    
    avg_workout_duration = workout_stats["total_duration"] / workout_stats["total_workouts"] if workout_stats["total_workouts"] > 0 else 0
    
    # Get top exercises
    cursor.execute('''
        SELECT e.name, COUNT(*) as count, SUM(e.sets) as total_sets
        FROM exercises e
        JOIN workouts w ON e.workout_id = w.id
        WHERE w.user_id = ? AND w.date BETWEEN ? AND ?
        GROUP BY e.name
        ORDER BY count DESC
        LIMIT 5
    ''', (user_id, start_date, end_date))
    
    top_exercises = []
    for row in cursor.fetchall():
        top_exercises.append({
            "name": row["name"],
            "count": row["count"],
            "total_sets": row["total_sets"]
        })
    
    # Nutrition breakdown
    total_calories = nutrition_stats["total_calories"] or 0
    nutrition_breakdown = {
        "protein": (nutrition_stats["total_protein"] or 0) * 4,  # 4 calories per gram
        "carbs": (nutrition_stats["total_carbs"] or 0) * 4,      # 4 calories per gram
        "fat": (nutrition_stats["total_fat"] or 0) * 9          # 9 calories per gram
    }
    
    return ProgressAnalytics(
        period=period,
        start_date=start_date,
        end_date=end_date,
        total_workouts=workout_stats["total_workouts"] or 0,
        total_duration=workout_stats["total_duration"] or 0,
        total_calories_burned=workout_stats["total_calories_burned"] or 0,
        total_calories_consumed=total_calories,
        net_calories=total_calories - (workout_stats["total_calories_burned"] or 0),
        weight_change=weight_change,
        workout_frequency=round(workout_frequency, 1),
        avg_workout_duration=round(avg_workout_duration, 1),
        top_exercises=top_exercises,
        nutrition_breakdown=nutrition_breakdown
    )

@app.get("/suggestions/goals", response_model=List[GoalSuggestion])
async def get_goal_suggestions(user_id: str, db: Connection = Depends(get_db)):
    """Get personalized goal suggestions for user"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        date_of_birth=row["date_of_birth"],
        gender=row["gender"],
        weight=row["weight"],
        height=row["height"],
        activity_level=row["activity_level"],
        goal=row["goal"]
    )
    
    return generate_goal_suggestions(user)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": "SQLite"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)
