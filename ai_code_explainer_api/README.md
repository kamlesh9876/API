# AI Code Explainer API

A comprehensive AI-powered code analysis API that explains code, finds bugs, suggests optimizations, and identifies security vulnerabilities. Supports multiple programming languages with local LLM and HuggingFace model integration.

## 🚀 Features

- **Code Explanation**: Natural language explanations of what code does
- **Bug Detection**: Identify potential bugs and runtime issues
- **Performance Optimization**: Suggest code improvements and optimizations
- **Security Analysis**: Detect security vulnerabilities and compliance issues
- **Documentation Generation**: Auto-generate comprehensive code documentation
- **Refactoring Suggestions**: Recommend code structure improvements
- **Multi-language Support**: Python, JavaScript, Java, TypeScript, C++, Go, Rust
- **Local LLM Integration**: Support for local LLaMA models
- **HuggingFace Models**: Integration with CodeBERT and other code models
- **File Upload**: Analyze code files directly
- **Code Metrics**: Calculate cyclomatic complexity, maintainability index
- **Batch Analysis**: Analyze multiple files simultaneously
- **Real-time Analysis**: Fast response times with caching

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **AI Models**: Local LLaMA, HuggingFace Transformers
- **Code Parsing**: Tree-sitter for syntax analysis
- **Machine Learning**: PyTorch, Transformers library
- **File Processing**: Async file handling
- **API Documentation**: Auto-generated OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.8+
- pip package manager
- (Optional) Local LLM server (LLaMA)
- (Optional) HuggingFace API token
- 8GB+ RAM for local models

## 🚀 Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download Tree-sitter language parsers** (optional):
```bash
# Install tree-sitter CLI
npm install -g tree-sitter

# Download language grammars
tree-sitter build-wasm
```

3. **Set up local LLM** (optional):
```bash
# Install Ollama for local LLaMA
curl -fsSL https://ollama.ai/install.sh | sh

# Download LLaMA model
ollama pull llama2
ollama serve
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the server**:
```bash
python app.py
```

The API will be available at `http://localhost:8011`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8011/docs`
- ReDoc: `http://localhost:8011/redoc`

## 🔍 API Endpoints

### Main Analysis Endpoint

#### Analyze Code
```http
POST /analyze
Content-Type: application/json

{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "language": "python",
  "analysis_types": ["explain", "debug", "optimize", "security"],
  "context": "This is a recursive Fibonacci implementation",
  "focus_areas": ["performance", "security"]
}
```

**Response Example**:
```json
{
  "id": "analysis_123",
  "language": "python",
  "file_name": "uploaded_code",
  "analysis_type": "explain",
  "timestamp": "2024-01-15T12:00:00",
  "explanation": {
    "overview": "This code implements the Fibonacci sequence using recursion",
    "purpose": "Calculate Fibonacci numbers",
    "key_components": ["recursive function", "base cases", "recursive calls"],
    "algorithms_used": ["recursive algorithm"],
    "data_structures": ["call stack"],
    "complexity_analysis": "Time: O(2^n), Space: O(n)",
    "dependencies": [],
    "potential_improvements": ["Use memoization", "Iterative approach"]
  },
  "issues": [
    {
      "id": "issue_123",
      "type": "performance",
      "severity": "high",
      "message": "Exponential time complexity due to repeated calculations",
      "line_number": 4,
      "code_snippet": "return fibonacci(n-1) + fibonacci(n-2)",
      "suggestion": "Use memoization or iterative approach",
      "confidence": 0.95
    }
  ],
  "suggestions": [
    {
      "type": "performance",
      "description": "Implement memoization to improve performance",
      "before_code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
      "after_code": "def fibonacci(n, memo={}):\n    if n in memo:\n        return memo[n]\n    if n <= 1:\n        return n\n    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)\n    return memo[n]",
      "reasoning": "Memoization eliminates redundant calculations",
      "impact": "Time complexity reduced from O(2^n) to O(n)"
    }
  ],
  "security_vulnerabilities": [],
  "metrics": {
    "total_lines": 4,
    "non_empty_lines": 4,
    "comment_lines": 0,
    "comment_ratio": 0.0,
    "functions": 1,
    "classes": 0,
    "imports": 0,
    "cyclomatic_complexity": 3,
    "maintainability_index": 85.5
  },
  "processing_time": 0.245,
  "model_used": "local_llm"
}
```

#### Analyze File Upload
```http
POST /analyze/file
Content-Type: multipart/form-data

file: [code file]
language: python
analysis_types: explain,debug,optimize
```

### Specialized Endpoints

#### Explain Code
```http
POST /explain
Content-Type: application/x-www-form-urlencoded

code=def hello_world(): print("Hello, World!")
&language=python
&context=Simple greeting function
```

**Response Example**:
```json
{
  "overview": "This function prints a greeting message",
  "purpose": "Display 'Hello, World!' to the console",
  "key_components": ["function definition", "print statement"],
  "algorithms_used": [],
  "data_structures": [],
  "complexity_analysis": "Time: O(1), Space: O(1)",
  "dependencies": [],
  "potential_improvements": ["Add docstring", "Return value instead of printing"]
}
```

#### Debug Code
```http
POST /debug
Content-Type: application/x-www-form-urlencoded

code=for i in range(10): print(i)
&language=python
```

**Response Example**:
```json
{
  "issues": [
    {
      "id": "issue_456",
      "type": "style",
      "severity": "low",
      "message": "Consider using enumerate for better readability",
      "line_number": 1,
      "suggestion": "for i, value in enumerate(range(10)): print(i, value)",
      "confidence": 0.8
    }
  ],
  "metrics": {
    "total_lines": 1,
    "cyclomatic_complexity": 2,
    "maintainability_index": 90.0
  },
  "processing_time": 0.123
}
```

#### Optimize Code
```http
POST /optimize
Content-Type: application/x-www-form-urlencoded

code=result = []
for item in items:
    result.append(item * 2)
&language=python
```

**Response Example**:
```json
{
  "suggestions": [
    {
      "type": "performance",
      "description": "Use list comprehension for better performance",
      "before_code": "result = []\nfor item in items:\n    result.append(item * 2)",
      "after_code": "result = [item * 2 for item in items]",
      "reasoning": "List comprehensions are more efficient and Pythonic",
      "impact": "Performance improvement and cleaner code"
    }
  ],
  "metrics": {
    "total_lines": 3,
    "maintainability_index": 88.0
  },
  "processing_time": 0.156
}
```

#### Security Analysis
```http
POST /security
Content-Type: application/x-www-form-urlencoded

code=cursor.execute("SELECT * FROM users WHERE id = " + user_id)
&language=python
```

**Response Example**:
```json
{
  "vulnerabilities": [
    {
      "id": "vuln_789",
      "type": "sql_injection",
      "severity": "critical",
      "description": "SQL injection vulnerability through string concatenation",
      "location": "Line 1",
      "cwe_id": "CWE-89",
      "cvss_score": 9.8,
      "remediation": "Use parameterized queries or ORM",
      "references": [
        "https://owasp.org/www-project-top-ten/2017/A1_2017-Injection"
      ]
    }
  ],
  "severity_summary": {
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "processing_time": 0.289
}
```

#### Generate Documentation
```http
POST /document
Content-Type: application/x-www-form-urlencoded

code=def calculate_area(length, width): return length * width
&language=python
```

#### Refactoring Suggestions
```http
POST /refactor
Content-Type: application/x-www-form-urlencoded

code=def process_data(data):
    # Process step 1
    result1 = data * 2
    # Process step 2
    result2 = result1 + 10
    # Process step 3
    result3 = result2 / 5
    return result3
&language=python
```

### Utility Endpoints

#### Get Supported Languages
```http
GET /languages
```

**Response Example**:
```json
{
  "languages": [
    {"code": "python", "name": "Python", "supported": true},
    {"code": "javascript", "name": "Javascript", "supported": true},
    {"code": "java", "name": "Java", "supported": true},
    {"code": "typescript", "name": "Typescript", "supported": true},
    {"code": "cpp", "name": "Cpp", "supported": true},
    {"code": "csharp", "name": "Csharp", "supported": true},
    {"code": "go", "name": "Go", "supported": true},
    {"code": "rust", "name": "Rust", "supported": true}
  ]
}
```

#### Get Analysis Types
```http
GET /analysis-types
```

#### Model Status
```http
GET /models/status
```

**Response Example**:
```json
{
  "local_llm": {
    "status": "configured",
    "model": "llama-2-7b-chat",
    "endpoint": "http://localhost:8080",
    "available": true
  },
  "huggingface": {
    "status": "configured",
    "models": ["microsoft/CodeBERT-base", "deepset/roberta-base-squad2"],
    "available": true
  },
  "tree_sitter": {
    "status": "configured",
    "languages": ["python", "javascript", "java"],
    "available": true
  }
}
```

## 📊 Data Models

### CodeAnalysisResult
```json
{
  "id": "analysis_123",
  "language": "python",
  "file_name": "example.py",
  "analysis_type": "explain",
  "timestamp": "2024-01-15T12:00:00",
  "explanation": {...},
  "issues": [...],
  "suggestions": [...],
  "security_vulnerabilities": [...],
  "metrics": {...},
  "processing_time": 0.245,
  "model_used": "local_llm"
}
```

### CodeIssue
```json
{
  "id": "issue_123",
  "type": "performance",
  "severity": "high",
  "message": "Inefficient algorithm detected",
  "line_number": 15,
  "column_number": 8,
  "code_snippet": "for item in large_list:",
  "suggestion": "Use generator expression instead",
  "confidence": 0.9
}
```

### SecurityVulnerability
```json
{
  "id": "vuln_123",
  "type": "sql_injection",
  "severity": "critical",
  "description": "SQL injection vulnerability",
  "location": "Line 10",
  "cwe_id": "CWE-89",
  "cvss_score": 9.8,
  "remediation": "Use parameterized queries",
  "references": ["https://owasp.org/"]
}
```

## 🧪 Testing Examples

### Python Code Analysis
```bash
# Analyze Python code
curl -X POST "http://localhost:8011/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[0]\n    left = [x for x in arr[1:] if x <= pivot]\n    right = [x for x in arr[1:] if x > pivot]\n    return quicksort(left) + [pivot] + quicksort(right)",
    "language": "python",
    "analysis_types": ["explain", "optimize", "debug"]
  }'
```

### JavaScript Code Analysis
```bash
# Analyze JavaScript code
curl -X POST "http://localhost:8011/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "function debounce(func, delay) {\n    let timeoutId;\n    return function(...args) {\n        clearTimeout(timeoutId);\n        timeoutId = setTimeout(() => func.apply(this, args), delay);\n    };\n}",
    "language": "javascript",
    "analysis_types": ["explain", "document"]
  }'
```

### File Upload Analysis
```bash
# Upload and analyze file
curl -X POST "http://localhost:8011/analyze/file" \
  -F "file=@example.py" \
  -F "language=python" \
  -F "analysis_types=explain,debug,security"
```

### Security Analysis
```bash
# Security vulnerability check
curl -X POST "http://localhost:8011/security" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'code=eval(user_input)&language=python'
```

## 🔧 Configuration

### Environment Variables
Create `.env` file:

```bash
# Local LLM Configuration
LOCAL_LLM_URL=http://localhost:8080
LOCAL_LLM_MODEL=llama2
LOCAL_LLM_TIMEOUT=30

# HuggingFace Configuration
HUGGINGFACE_API_KEY=hf_your_huggingface_token
HUGGINGFACE_MODEL=microsoft/CodeBERT-base
HUGGINGFACE_TIMEOUT=60

# Tree-sitter Configuration
TREE_SITTER_LIB_PATH=/usr/local/lib
TREE_SITTER_GRAMMAR_PATH=./grammars

# API Configuration
HOST=0.0.0.0
PORT=8011
DEBUG=false
MAX_FILE_SIZE=10485760  # 10MB
MAX_CODE_LENGTH=1000000  # 1M characters

# Caching Configuration
ENABLE_CACHE=true
CACHE_TTL=3600
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_ANALYSIS=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ai_code_explainer.log
LOG_ANALYSIS_REQUESTS=true

# Performance
MAX_CONCURRENT_ANALYSES=5
ANALYSIS_TIMEOUT=120
ENABLE_ASYNC_PROCESSING=true

# Security
ENABLE_INPUT_SANITIZATION=true
MAX_CODE_COMPLEXITY=100
BLOCKED_PATTERNS=system,exec,eval

# Model Configuration
DEFAULT_ANALYSIS_TYPES=explain,debug
CONFIDENCE_THRESHOLD=0.7
ENABLE_FALLBACK_RESPONSES=true
```

### Local LLM Setup

#### Using Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Download models
ollama pull llama2
ollama pull codellama

# Test the model
ollama run llama2 "Explain this Python code: def hello(): print('Hello')"
```

#### Using Llama.cpp
```bash
# Clone and build Llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Download model
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

# Start server
./main -m llama-2-7b-chat.Q4_K_M.gguf --host 0.0.0.0 --port 8080
```

### HuggingFace Setup
```python
# Configure HuggingFace API
from transformers import AutoTokenizer, AutoModelForCodeGeneration

tokenizer = AutoTokenizer.from_pretrained("microsoft/CodeBERT-base")
model = AutoModelForCodeGeneration.from_pretrained("microsoft/CodeBERT-base")
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install tree-sitter CLI
RUN npm install -g tree-sitter

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download language grammars
RUN tree-sitter build-wasm
RUN git clone https://github.com/tree-sitter/tree-sitter-python
RUN git clone https://github.com/tree-sitter/tree-sitter-javascript
RUN git clone https://github.com/tree-sitter/tree-sitter-java

COPY . .
EXPOSE 8011

# Create directories
RUN mkdir -p logs uploads

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8011"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  ai-code-explainer:
    build: .
    ports:
      - "8011:8011"
    environment:
      - LOCAL_LLM_URL=http://ollama:11434
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - ollama
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  ollama_data:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-code-explainer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-code-explainer
  template:
    metadata:
      labels:
        app: ai-code-explainer
    spec:
      containers:
      - name: api
        image: ai-code-explainer:latest
        ports:
        - containerPort: 8011
        env:
        - name: LOCAL_LLM_URL
          value: "http://ollama-service:11434"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8011
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8011
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-code-explainer-service
spec:
  selector:
    app: ai-code-explainer
  ports:
  - port: 8011
    targetPort: 8011
  type: LoadBalancer
```

## 📈 Advanced Features

### Custom Model Integration
```python
class CustomModelService:
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)
    
    async def analyze_code(self, code: str, language: str) -> Dict:
        """Custom model analysis logic"""
        # Implement custom analysis logic
        pass

# Register custom model
analyzer.register_model("custom", CustomModelService("path/to/model"))
```

### Batch Processing
```python
@app.post("/analyze/batch")
async def analyze_batch(files: List[UploadFile]):
    """Analyze multiple files simultaneously"""
    results = []
    for file in files:
        result = await analyze_file(file)
        results.append(result)
    return results
```

### Code Comparison
```python
@app.post("/compare")
async def compare_code(
    code1: str = Form(...),
    code2: str = Form(...),
    language: ProgrammingLanguage = Form(...)
):
    """Compare two code snippets"""
    # Implement comparison logic
    pass
```

### Real-time Streaming
```python
from fastapi.responses import StreamingResponse

@app.post("/analyze/stream")
async def analyze_stream(request: AnalysisRequest):
    """Stream analysis results in real-time"""
    async def generate():
        # Stream analysis progress
        yield "data: Starting analysis...\n\n"
        # ... analysis logic
        yield "data: Analysis complete\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

## 🛡️ Security Features

### Input Validation
```python
def validate_code(code: str, language: str) -> bool:
    """Validate code input for security"""
    # Check for malicious patterns
    blocked_patterns = [
        r'import\s+os',
        r'system\s*\(',
        r'exec\s*\(',
        r'eval\s*\('
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, code):
            return False
    
    return True
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_code(request: Request, analysis_request: AnalysisRequest):
    """Rate-limited analysis endpoint"""
    pass
```

### Content Security
```python
def sanitize_code(code: str) -> str:
    """Sanitize code for safe processing"""
    # Remove potentially dangerous content
    # Implement sanitization logic
    return code
```

## 🔍 Monitoring & Analytics

### Performance Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
analysis_requests = Counter('ai_analysis_requests_total', 'Total analysis requests')
analysis_duration = Histogram('ai_analysis_duration_seconds', 'Analysis duration')
active_analyses = Gauge('ai_active_analyses', 'Currently active analyses')
model_usage = Counter('ai_model_usage_total', 'Model usage', ['model_type'])
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
            "local_llm": await check_llm_health(),
            "huggingface": await check_hf_health(),
            "tree_sitter": check_tree_sitter_health()
        },
        "metrics": {
            "total_analyses": analysis_requests._value._value,
            "active_analyses": active_analyses._value._value,
            "avg_duration": analysis_duration.observe()
        }
    }
```

## 🔮 Future Enhancements

### Planned Features
- **Multi-file Project Analysis**: Analyze entire codebases
- **Code Generation**: Generate code from natural language descriptions
- **Test Generation**: Auto-generate unit tests
- **Code Translation**: Convert code between programming languages
- **Integration IDE**: VS Code and JetBrains plugins
- **Collaborative Analysis**: Team-based code review features
- **Custom Rules**: Define custom analysis rules and patterns
- **Performance Profiling**: Detailed performance analysis
- **Code Quality Scoring**: Overall code quality metrics
- **Learning Mode**: Improve models based on user feedback

### AI Integration
- **Fine-tuned Models**: Custom models for specific domains
- **Ensemble Methods**: Multiple model consensus
- **Active Learning**: Improve models with user interactions
- **Context Awareness**: Better understanding of project context
- **Semantic Analysis**: Deeper code understanding
- **Pattern Recognition**: Identify design patterns automatically

### Advanced Analytics
- **Code Evolution**: Track code changes over time
- **Team Metrics**: Team coding patterns and insights
- **Technical Debt**: Quantify and track technical debt
- **Code Smells**: Advanced code smell detection
- **Architecture Analysis**: System-level architectural insights
- **Dependency Analysis**: Complex dependency mapping

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review model documentation for LLM setup
- Consult Tree-sitter documentation for language parsing
- Check HuggingFace for model integration

---

**Built with ❤️ using FastAPI and AI Models**
