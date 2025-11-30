# DevTools API - Ultimate Developer Helper

A comprehensive API with multiple developer tools including Base64 encoding/decoding, hash generation, password strength checking, UUID generation, and text analysis. Built with FastAPI for maximum performance and ease of use.

## 🚀 Features

- **Base64 Tools**: Encode/decode text, URL encoding/decoding
- **Hash Generator**: Support for MD5, SHA1, SHA256, SHA512, SHA3 variants
- **Password Strength Checker**: Comprehensive password analysis with entropy calculation
- **UUID Generator**: Generate UUIDs in versions 1, 3, 4, and 5
- **Text Analyzer**: Analyze text statistics and extract information
- **Bulk Operations**: Process multiple items at once
- **Security Features**: Secure password generation, common password detection
- **Performance Metrics**: Entropy calculation, crack time estimation

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Data Validation**: Pydantic models
- **Hashing**: Python hashlib library
- **Security**: Secrets module for secure random generation
- **Logging**: Comprehensive logging for debugging

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8018`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8018/docs`
- ReDoc: `http://localhost:8018/redoc`

## 📝 API Endpoints

### Base64 Tools

#### Encode to Base64
```http
POST /base64/encode
Content-Type: application/json

{
  "text": "Hello, World!",
  "encoding": "utf-8"
}
```

**Response Example**:
```json
{
  "input_text": "Hello, World!",
  "output_text": "SGVsbG8sIFdvcmxkIQ==",
  "operation": "encode",
  "encoding": "utf-8",
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Decode from Base64
```http
POST /base64/decode
Content-Type: application/json

{
  "text": "SGVsbG8sIFdvcmxkIQ==",
  "encoding": "utf-8"
}
```

#### URL Encode
```http
POST /base64/url-encode
Content-Type: application/json

{
  "text": "Hello World! How are you?"
}
```

#### URL Decode
```http
POST /base64/url-decode
Content-Type: application/json

{
  "text": "Hello%20World%21%20How%20are%20you%3F"
}
```

### Hash Generator

#### Generate Hash
```http
POST /hash/generate
Content-Type: application/json

{
  "text": "Hello, World!",
  "algorithm": "sha256",
  "encoding": "utf-8",
  "output_format": "hex"
}
```

**Response Example**:
```json
{
  "input_text": "Hello, World!",
  "algorithm": "sha256",
  "hash_value": "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f",
  "output_format": "hex",
  "encoding": "utf-8",
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Bulk Hash Generation
```http
POST /hash/bulk
Content-Type: application/json

{
  "texts": ["Hello", "World", "Test"],
  "algorithm": "sha256",
  "encoding": "utf-8",
  "output_format": "hex"
}
```

#### Compare Hashes
```http
GET /hash/compare?text1=Hello&text2=World&algorithm=sha256
```

**Response Example**:
```json
{
  "text1": "Hello",
  "text2": "World",
  "algorithm": "sha256",
  "hash1": "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969",
  "hash2": "486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7",
  "match": false,
  "timestamp": "2024-01-15T12:00:00"
}
```

### Password Tools

#### Check Password Strength
```http
POST /password/strength
Content-Type: application/json

{
  "password": "MySecurePassword123!",
  "username": "john_doe",
  "email": "john@example.com",
  "common_passwords": true
}
```

**Response Example**:
```json
{
  "password": "MySecurePassword123!",
  "strength": "strong",
  "score": 75,
  "length": 19,
  "feedback": [],
  "suggestions": [],
  "time_to_crack": "Centuries",
  "entropy": 95.2,
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Generate Secure Password
```http
POST /password/generate?length=16&include_uppercase=true&include_lowercase=true&include_numbers=true&include_symbols=true&exclude_similar=true&count=3
```

**Response Example**:
```json
{
  "passwords": [
    "K8$mB#n2@xP5!qR9",
    "Zt7&vW3#yL6*pH1$",
    "N4@jF8#qX2*mK5!b"
  ],
  "length": 16,
  "character_set": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
  "count": 3,
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Calculate Password Entropy
```http
POST /password/entropy
Content-Type: application/json

{
  "password": "MySecurePassword123!"
}
```

**Response Example**:
```json
{
  "password": "MySecurePassword123!",
  "entropy": 95.2,
  "time_to_crack": "Centuries",
  "timestamp": "2024-01-15T12:00:00"
}
```

### UUID Tools

#### Generate UUIDs
```http
POST /uuid/generate
Content-Type: application/json

{
  "version": "4",
  "count": 3
}
```

**Response Example**:
```json
{
  "uuids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ],
  "version": "4",
  "count": 3,
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Generate UUID v3/v5
```http
POST /uuid/generate
Content-Type: application/json

{
  "version": "5",
  "namespace": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "name": "example.com",
  "count": 1
}
```

#### Parse UUID
```http
GET /uuid/parse?uuid_string=550e8400-e29b-41d4-a716-446655440000
```

**Response Example**:
```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "version": 4,
  "variant": "RFC 4122",
  "hex": "550e8400e29b41d4a716446655440000",
  "int": 108413663389842876732445623816880619776,
  "urn": "urn:uuid:550e8400-e29b-41d4-a716-446655440000",
  "bytes": "550e8400e29b41d4a716446655440000",
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Validate UUID
```http
GET /uuid/validate?uuid_string=550e8400-e29b-41d4-a716-446655440000
```

**Response Example**:
```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "is_valid": true,
  "version": 4,
  "timestamp": "2024-01-15T12:00:00"
}
```

### Text Analyzer

#### Analyze Text
```http
POST /text/analyze
Content-Type: application/json

{
  "text": "Hello World! This is a test. How are you today?",
  "include_stats": true
}
```

**Response Example**:
```json
{
  "text_length": 42,
  "word_count": 9,
  "character_count": 42,
  "line_count": 1,
  "paragraph_count": 1,
  "unique_words": 9,
  "readability_score": 65.4,
  "language": "english",
  "timestamp": "2024-01-15T12:00:00"
}
```

#### Extract Information
```http
POST /text/extract
Content-Type: application/json

{
  "text": "Contact us at support@example.com or call 123-456-7890. Visit https://example.com for more info. #devtools @api"
}
```

**Response Example**:
```json
{
  "text": "Contact us at support@example.com or call 123-456-7890. Visit https://example.com for more info. #devtools @api",
  "emails": ["support@example.com"],
  "urls": ["https://example.com"],
  "phone_numbers": ["123-456-7890"],
  "numbers": ["123", "456", "7890"],
  "hashtags": ["#devtools"],
  "mentions": ["@api"],
  "timestamp": "2024-01-15T12:00:00"
}
```

## 🧪 Testing Examples

### Base64 Operations
```bash
# Encode text
curl -X POST "http://localhost:8018/base64/encode" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, World!",
    "encoding": "utf-8"
  }'

# Decode Base64
curl -X POST "http://localhost:8018/base64/decode" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "SGVsbG8sIFdvcmxkIQ==",
    "encoding": "utf-8"
  }'

# URL encode
curl -X POST "http://localhost:8018/base64/url-encode" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World! How are you?"}'
```

### Hash Operations
```bash
# Generate SHA256 hash
curl -X POST "http://localhost:8018/hash/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, World!",
    "algorithm": "sha256",
    "output_format": "hex"
  }'

# Bulk hash generation
curl -X POST "http://localhost:8018/hash/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello", "World", "Test"],
    "algorithm": "sha256"
  }'

# Compare hashes
curl -X GET "http://localhost:8018/hash/compare?text1=Hello&text2=World&algorithm=sha256"
```

### Password Operations
```bash
# Check password strength
curl -X POST "http://localhost:8018/password/strength" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MySecurePassword123!",
    "username": "john_doe",
    "email": "john@example.com"
  }'

# Generate passwords
curl -X POST "http://localhost:8018/password/generate?length=16&include_uppercase=true&include_lowercase=true&include_numbers=true&include_symbols=true&count=3"

# Calculate entropy
curl -X POST "http://localhost:8018/password/entropy" \
  -H "Content-Type: application/json" \
  -d '{"password": "MySecurePassword123!"}'
```

### UUID Operations
```bash
# Generate UUIDs
curl -X POST "http://localhost:8018/uuid/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "4",
    "count": 3
  }'

# Parse UUID
curl -X GET "http://localhost:8018/uuid/parse?uuid_string=550e8400-e29b-41d4-a716-446655440000"

# Validate UUID
curl -X GET "http://localhost:8018/uuid/validate?uuid_string=550e8400-e29b-41d4-a716-446655440000"
```

### Text Analysis
```bash
# Analyze text
curl -X POST "http://localhost:8018/text/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello World! This is a test. How are you today?",
    "include_stats": true
  }'

# Extract information
curl -X POST "http://localhost:8018/text/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact us at support@example.com or call 123-456-7890. Visit https://example.com for more info."
  }'
```

## 📊 Password Strength Scoring

### Strength Levels
| Score Range | Strength | Description |
|-------------|----------|-------------|
| 80-100 | Very Strong | Excellent password with high entropy |
| 65-79 | Strong | Good password with decent complexity |
| 50-64 | Good | Acceptable password with some complexity |
| 35-49 | Fair | Weak password with basic requirements |
| 20-34 | Weak | Poor password with major issues |
| 0-19 | Very Weak | Extremely weak password |

### Scoring Factors
- **Length**: +20 points for 8+ chars, +10 for 12+, +10 for 16+
- **Character Variety**: +10 for lowercase, +10 for uppercase, +10 for numbers, +15 for symbols
- **Patterns**: -10 points for common patterns (sequential, keyboard, repeated)
- **Common Passwords**: -30 points if found in common passwords list
- **Entropy**: Bonus points based on calculated entropy (20+, 30+, 50+)

### Entropy Calculation
```
Entropy = Length × log₂(Character Set Size)
```
- **Lowercase**: 26 characters
- **Uppercase**: 26 characters  
- **Numbers**: 10 characters
- **Symbols**: 32 characters (punctuation)

### Crack Time Estimation
Based on entropy and assuming 10⁹ guesses per second:
- **< 1 second**: Very weak passwords
- **Minutes to hours**: Weak to fair passwords
- **Days to months**: Good passwords
- **Years to centuries**: Strong to very strong passwords

## 🔐 Hash Algorithms

### Supported Algorithms
| Algorithm | Output Size | Use Case |
|-----------|-------------|----------|
| MD5 | 128 bits | Legacy checksums (not for security) |
| SHA1 | 160 bits | Legacy applications (not for security) |
| SHA224 | 224 bits | General purpose |
| SHA256 | 256 bits | Recommended for most uses |
| SHA384 | 384 bits | Higher security requirements |
| SHA512 | 512 bits | Maximum security |
| SHA3-224 | 224 bits | SHA3 family |
| SHA3-256 | 256 bits | SHA3 family (recommended) |
| SHA3-384 | 384 bits | SHA3 family |
| SHA3-512 | 512 bits | SHA3 family |

### Output Formats
- **Hex**: Standard hexadecimal format (e.g., `dffd6021bb2bd5b0af676290809ec3a5`)
- **Base64**: Base64 encoded format (e.g., `3/1iG7K9bCv9nYpCAns6lMR3dh8dwa0sobihiKYgZhv8=`)

## 🆔 UUID Versions

### Version 1 (Time-based)
- Based on timestamp and MAC address
- Sortable by generation time
- Potential privacy concerns (MAC address exposure)

### Version 3 (MD5-based)
- Deterministic: same namespace+name = same UUID
- Uses MD5 hash (not recommended for new applications)
- Requires namespace and name

### Version 4 (Random)
- Completely random (except for version bits)
- Most commonly used version
- No ordering guarantees

### Version 5 (SHA1-based)
- Deterministic: same namespace+name = same UUID
- Uses SHA1 hash (recommended over v3)
- Requires namespace and name

### Common Namespaces
- **DNS**: `6ba7b810-9dad-11d1-80b4-00c04fd430c8`
- **URL**: `6ba7b811-9dad-11d1-80b4-00c04fd430c8`
- **OID**: `6ba7b812-9dad-11d1-80b4-00c04fd430c8`
- **X500**: `6ba7b814-9dad-11d1-80b4-00c04fd430c8`

## 📝 Text Analysis Features

### Statistics Calculated
- **Text Length**: Total number of characters
- **Word Count**: Number of words separated by spaces
- **Character Count**: Individual character count
- **Line Count**: Number of lines in text
- **Paragraph Count**: Number of paragraphs (double newlines)
- **Unique Words**: Count of unique words (case-insensitive)
- **Readability Score**: Simplified Flesch Reading Ease (0-100)
- **Language Detection**: Basic language identification

### Information Extraction
- **Emails**: Email addresses using regex pattern
- **URLs**: HTTP/HTTPS URLs
- **Phone Numbers**: Simple phone number patterns
- **Numbers**: Numerical values
- **Hashtags**: Words starting with #
- **Mentions**: Words starting with @

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8018
DEBUG=false
RELOAD=false

# Security
SECRET_KEY=your-secret-key-here
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Password Configuration
MIN_PASSWORD_LENGTH=8
MAX_PASSWORD_LENGTH=128
ENABLE_COMMON_PASSWORD_CHECK=true
COMMON_PASSWORDS_FILE=./common_passwords.txt

# Hash Configuration
DEFAULT_HASH_ALGORITHM=sha256
DEFAULT_HASH_FORMAT=hex
ENABLE_BULK_HASHING=true
MAX_BULK_ITEMS=50

# UUID Configuration
DEFAULT_UUID_VERSION=4
MAX_UUID_GENERATION=100
ENABLE_UUID_VALIDATION=true

# Text Analysis
ENABLE_LANGUAGE_DETECTION=true
ENABLE_READABILITY_SCORE=true
MAX_TEXT_LENGTH=1000000
ENABLE_TEXT_EXTRACTION=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/devtools.log
LOG_ROTATION=daily
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600
ENABLE_COMPRESSION=true
COMPRESSION_LEVEL=6

# Monitoring
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=30
ENABLE_PERFORMANCE_MONITORING=true

# Development
TEST_MODE=false
ENABLE_PROFILING=false
DEBUG_RESPONSES=false
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs

# Set permissions
RUN chmod +x logs

EXPOSE 8018

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8018"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  devtools-api:
    build: .
    ports:
      - "8018:8018"
    environment:
      - SECRET_KEY=your-production-secret-key
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8018/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M

volumes:
  logs_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devtools-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: devtools-api
  template:
    metadata:
      labels:
        app: devtools-api
    spec:
      containers:
      - name: api
        image: devtools-api:latest
        ports:
        - containerPort: 8018
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: devtools-secrets
              key: secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8018
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8018
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: devtools-service
spec:
  selector:
    app: devtools-api
  ports:
  - port: 8018
    targetPort: 8018
  type: LoadBalancer
```

## 📈 Advanced Features

### Bulk Operations
```python
# Bulk hash generation example
@app.post("/hash/bulk")
async def bulk_generate_hash(request: BulkHashRequest):
    """Generate hash for multiple texts"""
    results = []
    for text in request.texts:
        # Generate hash for each text
        hash_result = await generate_hash_single(text, request.algorithm)
        results.append({
            "input_text": text,
            "hash_value": hash_result
        })
    return {"results": results}
```

### Advanced Password Analysis
```python
# Pattern detection
def detect_patterns(password: str) -> List[str]:
    """Detect common password patterns"""
    patterns = []
    
    # Sequential characters
    if re.search(r'(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
        patterns.append("Contains sequential characters")
    
    # Keyboard patterns
    if re.search(r'(?:qwerty|asdf|zxcv|1234|2345|3456|4567|5678|6789|7890)', password.lower()):
        patterns.append("Contains keyboard patterns")
    
    return patterns
```

### Real-time Validation
```python
# Real-time password strength feedback
@app.websocket("/ws/password-strength")
async def password_strength_websocket(websocket: WebSocket):
    """Real-time password strength checking"""
    await websocket.accept()
    
    while True:
        data = await websocket.receive_text()
        strength_result = await check_password_strength(
            PasswordStrengthRequest(password=data)
        )
        await websocket.send_json(strength_result.dict())
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
base64_operations = Counter('base64_operations_total', 'Total Base64 operations')
hash_operations = Counter('hash_operations_total', 'Total hash operations')
password_checks = Counter('password_checks_total', 'Total password strength checks')
uuid_generations = Counter('uuid_generations_total', 'Total UUID generations')
text_analyses = Counter('text_analyses_total', 'Total text analyses')

# Response times
base64_duration = Histogram('base64_duration_seconds', 'Base64 operation duration')
hash_duration = Histogram('hash_duration_seconds', 'Hash operation duration')
password_duration = Histogram('password_duration_seconds', 'Password check duration')
```

### Usage Analytics
```python
@app.get("/analytics/usage")
async def get_usage_analytics():
    """Get API usage statistics"""
    return {
        "base64_operations": base64_operations._value.get(),
        "hash_operations": hash_operations._value.get(),
        "password_checks": password_checks._value.get(),
        "uuid_generations": uuid_generations._value.get(),
        "text_analyses": text_analyses._value.get(),
        "popular_hash_algorithms": get_popular_algorithms(),
        "average_password_strength": get_avg_password_strength(),
        "most_common_uuid_versions": get_common_uuid_versions()
    }
```

## 🔮 Future Enhancements

### Planned Features
- **JWT Token Generator**: Generate and validate JWT tokens
- **QR Code Generator**: Generate QR codes for various data types
- **JSON Validator**: Validate and format JSON data
- **Regular Expression Tester**: Test and debug regex patterns
- **Color Palette Generator**: Generate color schemes
- **CSS Minifier**: Minify CSS code
- **JavaScript Minifier**: Minify JavaScript code
- **HTML Entity Encoder**: Encode/decode HTML entities
- **Timestamp Converter**: Convert between timestamp formats
- **Unit Converter**: Convert between different units

### Advanced Security Features
- **Password Breach Check**: Check against HaveIBeenPwned API
- **Advanced Pattern Detection**: Machine learning-based pattern detection
- **Password Policy Validation**: Custom password policy enforcement
- **Secure Random Generation**: Hardware random number generation

### Integration Opportunities
- **IDE Extensions**: VS Code, JetBrains IDE plugins
- **Browser Extensions**: Developer tools for browsers
- **Mobile Apps**: Native mobile applications
- **CLI Tools**: Command-line interface
- **Webhooks**: Integration with external services

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review FastAPI documentation for API development
- Consult Python documentation for standard library functions

---

**Built with ❤️ using FastAPI for ultimate developer productivity**
