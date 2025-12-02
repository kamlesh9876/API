# AI Code Review API

An intelligent code review system that analyzes source code for security vulnerabilities, performance issues, style violations, and best practices using AI-powered pattern recognition.

## Features

- **Multi-Language Support**: Python, JavaScript, Java, and more
- **Security Analysis**: Detect SQL injection, XSS, code injection, and other vulnerabilities
- **Performance Analysis**: Identify inefficient code patterns and optimization opportunities
- **Style Checking**: Enforce coding standards and best practices
- **Code Metrics**: Calculate complexity, maintainability index, and technical debt
- **CWE Mapping**: Map vulnerabilities to Common Weakness Enumeration (CWE) IDs
- **CVSS Scoring**: Provide Common Vulnerability Scoring System (CVSS) scores
- **Batch Processing**: Analyze multiple files simultaneously
- **Progress Tracking**: Real-time progress updates for large codebases
- **Customizable Rules**: Support for custom review patterns

## API Endpoints

### Code Review

#### Create Review Job
```http
POST /api/review
Content-Type: application/json

{
  "files": [
    {
      "filename": "app.py",
      "language": "python",
      "content": "def hello_world():\n    print('Hello, World!')",
      "path": "/src/app.py"
    }
  ],
  "review_type": "comprehensive",
  "language": "python",
  "exclude_patterns": ["*_test.py", "migrations/"]
}
```

#### Get Review Job Status
```http
GET /api/review/{job_id}
```

#### Get Review Result
```http
GET /api/review/{job_id}/result
```

#### Get Review Summary
```http
GET /api/review/{job_id}/summary
```

#### List Review Jobs
```http
GET /api/jobs?status=completed&limit=50
```

#### Delete Review Job
```http
DELETE /api/review/{job_id}
```

### Patterns & Rules

#### Get Code Patterns
```http
GET /api/patterns/{language}
```

### Statistics
```http
GET /api/stats
```

## Data Models

### Code File
```json
{
  "filename": "app.py",
  "language": "python",
  "content": "def hello_world():\n    print('Hello, World!')",
  "path": "/src/app.py"
}
```

### Issue
```json
{
  "id": "issue_123",
  "type": "warning",
  "severity": "medium",
  "category": "performance",
  "title": "Inefficient Loop",
  "description": "Use enumerate() instead of range(len())",
  "line_number": 15,
  "column_number": 5,
  "code_snippet": "for i in range(len(items)):\n    print(items[i])",
  "suggestion": "Use enumerate() for better performance and readability",
  "rule_id": "python_inefficient_loop",
  "confidence": 0.8
}
```

### Security Vulnerability
```json
{
  "id": "vuln_123",
  "type": "sql_injection",
  "severity": "critical",
  "description": "Potential SQL injection vulnerability",
  "line_number": 42,
  "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
  "cwe_id": "CWE-89",
  "cvss_score": 9.0
}
```

### Code Metrics
```json
{
  "complexity": 8,
  "lines_of_code": 150,
  "comment_lines": 25,
  "blank_lines": 15,
  "maintainability_index": 75.2,
  "technical_debt": "16.0h",
  "duplication_percentage": 0.0,
  "test_coverage": 85.5
}
```

### Code Review Result
```json
{
  "id": "review_123",
  "files": [...],
  "overall_score": 82.5,
  "issues": [...],
  "security_vulnerabilities": [...],
  "metrics": {
    "app.py": {...}
  },
  "summary": "Found 2 critical issues requiring immediate attention. Overall code quality is good.",
  "recommendations": [
    "Address all critical security vulnerabilities immediately",
    "Consider refactoring to reduce complexity"
  ],
  "review_time": "2024-01-01T12:00:00",
  "processing_time": 2.5
}
```

## Supported Languages

### Python
- **Security**: SQL injection, code injection, insecure deserialization
- **Performance**: Inefficient loops, list comprehensions, string operations
- **Style**: Missing docstrings, naming conventions, PEP 8 violations

### JavaScript
- **Security**: XSS, code injection, prototype pollution
- **Performance**: Var keyword usage, inefficient DOM operations
- **Style**: Missing semicolons, function declarations vs expressions

### Java
- **Security**: SQL injection, path traversal, insecure crypto
- **Performance**: String concatenation, object creation in loops
- **Style**: Naming conventions, code organization

## Issue Categories

### 1. Security
- **Critical**: SQL injection, XSS, code injection, insecure deserialization
- **High**: Authentication bypass, sensitive data exposure
- **Medium**: Weak cryptography, insufficient logging
- **Low**: Information disclosure, improper error handling

### 2. Performance
- **Critical**: Memory leaks, infinite loops
- **High**: Inefficient algorithms, N+1 queries
- **Medium**: Redundant computations, inefficient data structures
- **Low**: Minor optimizations, code style improvements

### 3. Style
- **Critical**: Inconsistent formatting (affects readability)
- **High**: Missing documentation, poor naming
- **Medium**: Code organization violations
- **Low**: Minor style issues, whitespace problems

### 4. Logic
- **Critical**: Unreachable code, logic errors
- **High**: Potential null pointer exceptions
- **Medium**: Missing error handling, edge cases
- **Low**: Redundant conditions, inefficient logic

### 5. Best Practices
- **Critical**: Security best practices violations
- **High**: Design pattern violations
- **Medium**: SOLID principle violations
- **Low**: Minor improvements suggestions

## Security Vulnerabilities Detected

### SQL Injection (CWE-89)
- **Pattern**: Dynamic SQL query construction
- **Severity**: Critical
- **CVSS Score**: 9.0
- **Detection**: String concatenation in SQL queries

### Cross-Site Scripting (CWE-79)
- **Pattern**: Direct innerHTML assignment
- **Severity**: High
- **CVSS Score**: 7.5
- **Detection**: HTML injection patterns

### Code Injection (CWE-94)
- **Pattern**: Use of eval(), exec()
- **Severity**: Critical
- **CVSS Score**: 9.0
- **Detection**: Dynamic code execution

### Insecure Deserialization (CWE-502)
- **Pattern**: Pickle, JSON deserialization
- **Severity**: High
- **CVSS Score**: 8.0
- **Detection**: Unsafe deserialization methods

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
import asyncio

# Create code review job
review_data = {
    "files": [
        {
            "filename": "app.py",
            "language": "python",
            "content": """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

def process_data(items):
    for i in range(len(items)):
        print(items[i])
    return items
"""
        }
    ],
    "review_type": "comprehensive"
}

response = requests.post("http://localhost:8000/api/review", json=review_data)
job = response.json()
print(f"Review job created: {job['id']}")

# Check progress
while True:
    response = requests.get(f"http://localhost:8000/api/review/{job['id']}")
    current_job = response.json()
    print(f"Progress: {current_job['progress']:.1%}")
    
    if current_job["status"] == "completed":
        result = requests.get(f"http://localhost:8000/api/review/{job['id']}/result").json()
        print(f"Overall Score: {result['overall_score']}")
        print(f"Issues Found: {len(result['issues'])}")
        print(f"Security Vulnerabilities: {len(result['security_vulnerabilities'])}")
        
        for issue in result['issues']:
            print(f"- {issue['title']}: {issue['description']}")
        
        break
    elif current_job["status"] == "failed":
        print(f"Review failed: {current_job['error_message']}")
        break
    
    asyncio.sleep(1)
```

### JavaScript Client
```javascript
// Create review job
const reviewData = {
  files: [{
    filename: 'app.js',
    language: 'javascript',
    content: `
function getUserInput() {
    const input = document.getElementById('userInput').value;
    document.getElementById('output').innerHTML = input;
}

function processData(items) {
    for (var i = 0; i < items.length; i++) {
        console.log(items[i]);
    }
    return items;
}
    `
  }],
  review_type: 'comprehensive'
};

const response = await fetch('http://localhost:8000/api/review', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(reviewData)
});

const job = await response.json();
console.log('Review job created:', job.id);

// Get results
const resultResponse = await fetch(`http://localhost:8000/api/review/${job.id}/result`);
const result = await resultResponse.json();

console.log('Overall Score:', result.overall_score);
console.log('Issues:', result.issues.map(i => i.title));
console.log('Security Vulnerabilities:', result.security_vulnerabilities.map(v => v.type));
```

## Configuration

### Environment Variables
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Review Settings
MAX_FILE_SIZE=10485760
MAX_FILES_PER_REVIEW=50
REVIEW_TIMEOUT=300

# AI Model Settings
USE_EXTERNAL_AI=false
OPENAI_API_KEY=your-openai-key
CONFIDENCE_THRESHOLD=0.7

# Storage
DATABASE_URL=sqlite:///./code_reviews.db
RESULTS_RETENTION_DAYS=30

# Performance
MAX_CONCURRENT_REVIEWS=5
ENABLE_CACHING=true
```

## Use Cases

- **CI/CD Integration**: Automated code review in build pipelines
- **Pull Request Analysis**: Pre-commit code quality checks
- **Security Audits**: Comprehensive security vulnerability scanning
- **Code Quality Monitoring**: Track code quality over time
- **Educational Tools**: Help developers learn best practices
- **Compliance**: Ensure code meets organizational standards

## Advanced Features

### Custom Rules
Create custom review patterns:
```json
{
  "custom_patterns": [
    {
      "pattern": "TODO|FIXME|HACK",
      "type": "technical_debt",
      "severity": "medium",
      "description": "Technical debt markers found"
    }
  ]
}
```

### Integration Examples

#### GitHub Actions
```yaml
name: Code Review
on: [push, pull_request]
jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run Code Review
      run: |
        curl -X POST http://localhost:8000/api/review \
          -H "Content-Type: application/json" \
          -d @code-review.json
```

#### Git Hooks
```bash
#!/bin/sh
# Pre-commit hook
python3 - << EOF
import requests
import json

# Read staged files
files = []
for file in $(git diff --cached --name-only):
    if [[ $file == *.py ]]; then
        content=$(git show :$file)
        files.append({
            "filename": file,
            "language": "python",
            "content": content
        })

if files:
    response = requests.post("http://localhost:8000/api/review", 
                           json={"files": files})
    job = response.json()
    
    # Wait for completion and check score
    # Fail commit if score is too low
EOF
```

## Production Considerations

- **Scalability**: Horizontal scaling with load balancers
- **Database Integration**: PostgreSQL for persistent storage
- **Caching**: Redis for frequent pattern matches
- **Queue System**: RabbitMQ for job processing
- **Monitoring**: Metrics and health checks
- **Security**: API authentication and rate limiting
- **Performance**: Optimized pattern matching algorithms

## Metrics and Analytics

### Code Quality Trends
- Track quality scores over time
- Monitor issue resolution rates
- Analyze vulnerability trends

### Team Performance
- Developer-specific metrics
- Team-wide quality comparisons
- Improvement tracking

### Project Health
- Technical debt accumulation
- Security posture assessment
- Maintainability trends
