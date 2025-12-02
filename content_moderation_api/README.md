# AI Content Moderation API

An intelligent content moderation system that uses AI and rule-based filtering to detect and handle inappropriate content across multiple categories.

## Features

- **Multi-Category Detection**: Profanity, spam, hate speech, personal info, violence
- **AI-Powered Analysis**: Toxicity scoring, spam detection, sentiment analysis
- **Rule-Based Filtering**: Customizable moderation rules with regex patterns
- **Batch Processing**: Moderate multiple content items simultaneously
- **Content Filtering**: Automatic content replacement with asterisks
- **Risk Assessment**: Four-level risk classification (low, medium, high, critical)
- **Real-time Analysis**: Fast content processing for live applications

## API Endpoints

### Content Moderation

#### Moderate Single Content
```http
POST /api/moderate
Content-Type: application/json

{
  "content": "Your text content here",
  "content_type": "text|comment|post|message",
  "language": "en",
  "user_id": "user123",
  "context": {"platform": "social_media"}
}
```

#### Batch Moderation
```http
POST /api/batch-moderate
Content-Type: application/json

[
  {
    "content": "First content item",
    "content_type": "comment"
  },
  {
    "content": "Second content item", 
    "content_type": "post"
  }
]
```

#### Quick Text Analysis
```http
POST /api/analyze-text
Content-Type: application/json

"Your text here"
```

### Rule Management

#### Get All Rules
```http
GET /api/rules
```

#### Create Rule
```http
POST /api/rules
Content-Type: application/json

{
  "id": "custom_rule_1",
  "name": "Custom Rule",
  "pattern": "\\b(banned_word)\\b",
  "category": "custom",
  "severity": "medium",
  "action": "filter"
}
```

#### Update Rule
```http
PUT /api/rules/{rule_id}
Content-Type: application/json

{
  "id": "rule_id",
  "name": "Updated Rule",
  "pattern": "\\b(new_pattern)\\b",
  "category": "custom",
  "severity": "high",
  "action": "block"
}
```

#### Delete Rule
```http
DELETE /api/rules/{rule_id}
```

### Statistics
```http
GET /api/stats
```

## Response Models

### Moderation Result
```json
{
  "is_approved": true,
  "confidence": 0.85,
  "risk_level": "low|medium|high|critical",
  "flagged_categories": ["profanity", "spam"],
  "filtered_content": "Filtered text with ***",
  "analysis_details": {
    "toxicity_score": 0.3,
    "spam_score": 0.1,
    "sentiment": "neutral",
    "matched_rules": ["Basic Profanity"],
    "word_count": 25,
    "character_count": 120
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## Moderation Categories

### 1. Profanity
- Detects offensive language and swear words
- Action: Filter with asterisks
- Severity: Medium

### 2. Spam
- Identifies promotional and spam content
- Action: Flag for review
- Severity: Low

### 3. Hate Speech
- Detects discriminatory and hateful content
- Action: Block immediately
- Severity: Critical

### 4. Personal Information
- Identifies phone numbers, credit cards, etc.
- Action: Filter sensitive data
- Severity: High

### 5. Violence
- Detects violent threats and harmful content
- Action: Block immediately
- Severity: High

## Risk Levels

- **Low**: Content is safe, minimal concerns
- **Medium**: Some issues but generally acceptable
- **High**: Significant concerns, review needed
- **Critical**: Immediate action required

## Installation

```bash
pip install fastapi uvicorn
```

## Usage

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Example Usage

### Python Client
```python
import requests

# Moderate content
response = requests.post("http://localhost:8000/api/moderate", json={
    "content": "This is a test message",
    "content_type": "comment"
})

result = response.json()
print(f"Approved: {result['is_approved']}")
print(f"Risk Level: {result['risk_level']}")
```

### JavaScript Client
```javascript
const response = await fetch('http://localhost:8000/api/moderate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    content: 'Your content here',
    content_type: 'comment'
  })
});

const result = await response.json();
console.log('Approved:', result.is_approved);
console.log('Risk Level:', result.risk_level);
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# AI Model Configuration
TOXICITY_THRESHOLD=0.5
SPAM_THRESHOLD=0.7

# Database (for persistence)
DATABASE_URL=sqlite:///./moderation.db
```

## Use Cases

- **Social Media Platforms**: Real-time comment and post moderation
- **Chat Applications**: Message filtering in live conversations
- **E-commerce**: Review and product comment moderation
- **Gaming Platforms**: Chat and username filtering
- **Educational Platforms**: Student content moderation
- **Dating Apps**: Profile and message content filtering

## Advanced Features

### Custom Rule Creation
Create sophisticated moderation rules using regular expressions:
- Pattern matching for specific words or phrases
- Context-aware filtering
- Multi-language support
- Custom severity levels

### Batch Processing
Efficiently process large volumes of content:
- Bulk moderation for content imports
- Historical content analysis
- Scheduled content reviews

### Analytics Integration
- Detailed moderation metrics
- Trend analysis of content violations
- User behavior patterns
- Platform health monitoring

## Production Considerations

- **Database Integration**: Store moderation history and user statistics
- **Machine Learning**: Replace rule-based system with trained models
- **Scalability**: Implement caching and load balancing
- **Multi-language**: Support for international content
- **Custom Thresholds**: Platform-specific risk tolerances
- **Appeals Process**: Human review workflow integration
