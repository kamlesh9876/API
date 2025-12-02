from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import re
import asyncio
from datetime import datetime
import hashlib

app = FastAPI(title="AI Content Moderation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ContentAnalysis(BaseModel):
    content: str
    content_type: str  # "text", "comment", "post", "message"
    language: str = "en"
    user_id: Optional[str] = None
    context: Optional[Dict] = None

class ModerationResult(BaseModel):
    is_approved: bool
    confidence: float
    risk_level: str  # "low", "medium", "high", "critical"
    flagged_categories: List[str]
    filtered_content: Optional[str] = None
    analysis_details: Dict
    timestamp: datetime

class ModerationRule(BaseModel):
    id: str
    name: str
    pattern: str
    category: str
    severity: str  # "low", "medium", "high", "critical"
    is_active: bool = True
    action: str  # "flag", "filter", "block"

# In-memory rule storage
moderation_rules = [
    ModerationRule(
        id="profanity_1",
        name="Basic Profanity",
        pattern=r"\b(bad|evil|hate|kill|stupid|idiot)\b",
        category="profanity",
        severity="medium",
        action="filter"
    ),
    ModerationRule(
        id="spam_1",
        name="Spam Patterns",
        pattern=r"(buy now|click here|free money|winner|congratulations)",
        category="spam",
        severity="low",
        action="flag"
    ),
    ModerationRule(
        id="hate_speech_1",
        name="Hate Speech Detection",
        pattern=r"\b(racist|sexist|homophobic|discrimination)\b",
        category="hate_speech",
        severity="critical",
        action="block"
    ),
    ModerationRule(
        id="personal_info_1",
        name="Personal Information",
        pattern=r"\b\d{3}-\d{3}-\d{4}\b|\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b",
        category="personal_info",
        severity="high",
        action="filter"
    ),
    ModerationRule(
        id="violence_1",
        name="Violent Content",
        pattern=r"\b(weapon|bomb|terror|attack|violence|threat)\b",
        category="violence",
        severity="high",
        action="block"
    )
]

# Content analysis functions
def analyze_toxicity(content: str) -> float:
    """Simulate AI toxicity analysis (0.0 to 1.0)"""
    toxic_words = ["hate", "kill", "stupid", "idiot", "evil", "bad"]
    words = content.lower().split()
    toxic_count = sum(1 for word in words if word in toxic_words)
    return min(toxic_count / max(len(words), 1), 1.0)

def analyze_spam(content: str) -> float:
    """Simulate spam detection (0.0 to 1.0)"""
    spam_indicators = ["buy", "free", "money", "winner", "click", "now", "congratulations"]
    spam_count = sum(1 for word in spam_indicators if word in content.lower())
    return min(spam_count / max(len(content.split()), 1), 1.0)

def analyze_sentiment(content: str) -> str:
    """Simple sentiment analysis"""
    positive_words = ["good", "great", "awesome", "love", "happy", "excellent"]
    negative_words = ["bad", "terrible", "hate", "awful", "horrible", "sad"]
    
    words = content.lower().split()
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    return "neutral"

def filter_content(content: str, rules: List[ModerationRule]) -> str:
    """Apply content filtering based on rules"""
    filtered = content
    for rule in rules:
        if rule.action == "filter" and rule.is_active:
            filtered = re.sub(rule.pattern, "***", filtered, flags=re.IGNORECASE)
    return filtered

def calculate_risk_level(flagged_categories: List[str], toxicity: float, spam: float) -> str:
    """Calculate overall risk level"""
    critical_categories = ["hate_speech", "violence"]
    high_categories = ["personal_info", "profanity"]
    
    if any(cat in flagged_categories for cat in critical_categories):
        return "critical"
    elif any(cat in flagged_categories for cat in high_categories) or toxicity > 0.7:
        return "high"
    elif toxicity > 0.3 or spam > 0.5:
        return "medium"
    else:
        return "low"

# API Endpoints
@app.post("/api/moderate", response_model=ModerationResult)
async def moderate_content(analysis: ContentAnalysis):
    """Analyze and moderate content"""
    
    # Apply rule-based filtering
    flagged_categories = []
    matched_rules = []
    
    for rule in moderation_rules:
        if rule.is_active and re.search(rule.pattern, analysis.content, re.IGNORECASE):
            flagged_categories.append(rule.category)
            matched_rules.append(rule)
    
    # AI-based analysis
    toxicity_score = analyze_toxicity(analysis.content)
    spam_score = analyze_spam(analysis.content)
    sentiment = analyze_sentiment(analysis.content)
    
    # Calculate risk level
    risk_level = calculate_risk_level(flagged_categories, toxicity_score, spam_score)
    
    # Determine approval
    is_approved = risk_level in ["low", "medium"]
    confidence = max(toxicity_score, spam_score)
    
    # Apply filtering if needed
    filtered_content = None
    if any(rule.action == "filter" for rule in matched_rules):
        filter_rules = [rule for rule in matched_rules if rule.action == "filter"]
        filtered_content = filter_content(analysis.content, filter_rules)
    
    # Analysis details
    analysis_details = {
        "toxicity_score": toxicity_score,
        "spam_score": spam_score,
        "sentiment": sentiment,
        "matched_rules": [rule.name for rule in matched_rules],
        "word_count": len(analysis.content.split()),
        "character_count": len(analysis.content)
    }
    
    return ModerationResult(
        is_approved=is_approved,
        confidence=confidence,
        risk_level=risk_level,
        flagged_categories=flagged_categories,
        filtered_content=filtered_content,
        analysis_details=analysis_details,
        timestamp=datetime.now()
    )

@app.post("/api/batch-moderate", response_model=List[ModerationResult])
async def batch_moderate_content(contents: List[ContentAnalysis]):
    """Moderate multiple content items"""
    results = []
    for content in contents:
        result = await moderate_content(content)
        results.append(result)
    return results

@app.get("/api/rules", response_model=List[ModerationRule])
async def get_moderation_rules():
    """Get all moderation rules"""
    return moderation_rules

@app.post("/api/rules", response_model=ModerationRule)
async def create_moderation_rule(rule: ModerationRule):
    """Create a new moderation rule"""
    moderation_rules.append(rule)
    return rule

@app.put("/api/rules/{rule_id}")
async def update_moderation_rule(rule_id: str, rule: ModerationRule):
    """Update a moderation rule"""
    for i, existing_rule in enumerate(moderation_rules):
        if existing_rule.id == rule_id:
            moderation_rules[i] = rule
            return {"message": "Rule updated successfully"}
    raise HTTPException(status_code=404, detail="Rule not found")

@app.delete("/api/rules/{rule_id}")
async def delete_moderation_rule(rule_id: str):
    """Delete a moderation rule"""
    global moderation_rules
    moderation_rules = [rule for rule in moderation_rules if rule.id != rule_id]
    return {"message": "Rule deleted successfully"}

@app.get("/api/stats")
async def get_moderation_stats():
    """Get moderation statistics"""
    return {
        "total_rules": len(moderation_rules),
        "active_rules": len([rule for rule in moderation_rules if rule.is_active]),
        "categories": list(set(rule.category for rule in moderation_rules)),
        "severity_distribution": {
            severity: len([rule for rule in moderation_rules if rule.severity == severity])
            for severity in ["low", "medium", "high", "critical"]
        }
    }

@app.post("/api/analyze-text")
async def analyze_text_only(text: str):
    """Quick text analysis without moderation"""
    return {
        "toxicity": analyze_toxicity(text),
        "spam": analyze_spam(text),
        "sentiment": analyze_sentiment(text),
        "word_count": len(text.split()),
        "character_count": len(text)
    }

@app.get("/")
async def root():
    return {"message": "AI Content Moderation API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
