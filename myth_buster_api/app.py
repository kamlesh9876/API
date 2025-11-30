from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Myth Buster API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Myth(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    is_true: bool
    category: str
    evidence: List[str]
    sources: List[str]

class MythCreate(BaseModel):
    title: str
    description: str
    is_true: bool
    category: str
    evidence: List[str]
    sources: List[str]

class MythUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_true: Optional[bool] = None
    category: Optional[str] = None
    evidence: Optional[List[str]] = None
    sources: Optional[List[str]] = None

# In-memory database (for demo purposes)
myths_db = [
    {
        "id": 1,
        "title": "Lightning never strikes the same place twice",
        "description": "The belief that lightning cannot strike the same location multiple times",
        "is_true": False,
        "category": "Nature",
        "evidence": [
            "The Empire State Building is struck by lightning an average of 25 times per year",
            "Lightning tends to strike tall objects and high points repeatedly"
        ],
        "sources": [
            "National Weather Service",
            "Scientific American"
        ]
    },
    {
        "id": 2,
        "title": "Humans only use 10% of their brain",
        "description": "The myth that humans only utilize a small fraction of their brain capacity",
        "is_true": False,
        "category": "Biology",
        "evidence": [
            "Brain imaging shows activity throughout the entire brain",
            "Even during sleep, most brain areas remain active",
            "Damage to small brain areas can have significant consequences"
        ],
        "sources": [
            "Neuroscience journal studies",
            "Harvard Medical School"
        ]
    },
    {
        "id": 3,
        "title": "Goldfish have a 3-second memory",
        "description": "The belief that goldfish can only remember things for 3 seconds",
        "is_true": False,
        "category": "Animals",
        "evidence": [
            "Studies show goldfish can remember things for at least 5 months",
            "Goldfish can be trained to respond to colors and sounds",
            "They can recognize their owners and remember feeding times"
        ],
        "sources": [
            "Plymouth University research",
            "Animal behavior studies"
        ]
    }
]

next_id = 4

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Myth Buster API", "version": "1.0.0"}

@app.get("/myths", response_model=List[Myth])
async def get_myths(category: Optional[str] = None, is_true: Optional[bool] = None):
    """Get all myths with optional filtering"""
    filtered_myths = myths_db.copy()
    
    if category:
        filtered_myths = [myth for myth in filtered_myths if myth["category"].lower() == category.lower()]
    
    if is_true is not None:
        filtered_myths = [myth for myth in filtered_myths if myth["is_true"] == is_true]
    
    return filtered_myths

@app.get("/myths/{myth_id}", response_model=Myth)
async def get_myth(myth_id: int):
    """Get a specific myth by ID"""
    for myth in myths_db:
        if myth["id"] == myth_id:
            return myth
    raise HTTPException(status_code=404, detail="Myth not found")

@app.post("/myths", response_model=Myth)
async def create_myth(myth: MythCreate):
    """Create a new myth"""
    global next_id
    new_myth = {
        "id": next_id,
        **myth.dict()
    }
    myths_db.append(new_myth)
    next_id += 1
    return new_myth

@app.put("/myths/{myth_id}", response_model=Myth)
async def update_myth(myth_id: int, myth_update: MythUpdate):
    """Update an existing myth"""
    for i, myth in enumerate(myths_db):
        if myth["id"] == myth_id:
            update_data = myth_update.dict(exclude_unset=True)
            myths_db[i].update(update_data)
            return myths_db[i]
    raise HTTPException(status_code=404, detail="Myth not found")

@app.delete("/myths/{myth_id}")
async def delete_myth(myth_id: int):
    """Delete a myth"""
    for i, myth in enumerate(myths_db):
        if myth["id"] == myth_id:
            del myths_db[i]
            return {"message": f"Myth with ID {myth_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Myth not found")

@app.get("/categories")
async def get_categories():
    """Get all available categories"""
    categories = list(set(myth["category"] for myth in myths_db))
    return {"categories": sorted(categories)}

@app.get("/myths/search")
async def search_myths(q: str):
    """Search myths by title or description"""
    query = q.lower()
    results = []
    for myth in myths_db:
        if (query in myth["title"].lower() or 
            query in myth["description"].lower() or
            query in myth["category"].lower()):
            results.append(myth)
    return results

@app.get("/stats")
async def get_stats():
    """Get statistics about myths"""
    total_myths = len(myths_db)
    true_myths = len([m for m in myths_db if m["is_true"]])
    false_myths = total_myths - true_myths
    categories = list(set(myth["category"] for myth in myths_db))
    
    return {
        "total_myths": total_myths,
        "true_myths": true_myths,
        "false_myths": false_myths,
        "categories_count": len(categories),
        "categories": sorted(categories)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
