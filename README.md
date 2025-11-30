# Project: My API Collection (FastAPI example)
# The document below contains the full code for a minimal but production-ready FastAPI project.
# Copy each section into the corresponding file path in your repository.

### FILE: README.md
```
# My API Collection - FastAPI Example

A minimal FastAPI-based API repository ready for GitHub. Includes health and code-explain endpoints, tests, Docker support, and a clear structure for extension.
```

### FILE: .gitignore
```
__pycache__/
.env
.venv/
*.pyc
.DS_Store
instance/
.envrc

# Docker
docker-compose.override.yml

# VSCode
.vscode/
```

### FILE: requirements.txt
```
fastapi==0.95.2
uvicorn[standard]==0.22.0
pydantic==1.10.11
python-multipart==0.0.6
pytest==7.4.0
httpx==0.24.0
```

### FILE: Dockerfile
```
FROM python:3.11-slim
WORKDIR /app

# system deps for some libraries (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### FILE: app/main.py
```
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.explain import router as explain_router

app = FastAPI(
    title="My API Collection",
    description="Example FastAPI project for portfolio and learning",
    version="0.1.0",
)

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(explain_router, prefix="/api/v1")


@app.get('/')
async def root():
    return {"message": "Welcome to My API Collection", "version": "0.1.0"}
```

### FILE: app/api/v1/health.py
```
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

@router.get('/health', response_model=HealthResponse, tags=['Health'])
async def health():
    return HealthResponse(status='ok', message='API is running successfully', timestamp=datetime.utcnow().isoformat() + 'Z')
```

### FILE: app/models.py
```
from pydantic import BaseModel
from typing import Optional, List

class ExplainRequest(BaseModel):
    language: str
    code: str
    detail_level: Optional[str] = 'short'  # 'short' or 'detailed'

class ExplainResponse(BaseModel):
    language: str
    explanation: str
    tips: Optional[List[str]] = []
```

### FILE: app/services/explainer.py
```
# Simple explainer service for Python code using builtin ast
import ast
from typing import Tuple, List


def explain_python_code(code: str, detail: str = 'short') -> Tuple[str, List[str]]:
    """
    Very simple rule-based explanation for Python code.
    Returns (explanation_text, tips_list)
    """
    tips = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return (f"Unable to parse Python code: {e}", ["Check for syntax errors"]) 

    # Provide a very short explanation by inspecting top-level nodes
    descriptions = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            desc = f"Function `{node.name}` with parameters ({', '.join(args)})"
            # check for return in body
            has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
            desc += "; returns a value" if has_return else "; no explicit return"
            descriptions.append(desc)
            if not ast.get_docstring(node):
                tips.append(f"Add a docstring to function `{node.name}`")
        elif isinstance(node, ast.ClassDef):
            descriptions.append(f"Class `{node.name}` defined")
            if not ast.get_docstring(node):
                tips.append(f"Add a docstring to class `{node.name}`")
        elif isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            descriptions.append(f"Assignment to {', '.join(targets)}")

    if not descriptions:
        descriptions.append("No top-level functions, classes, or assignments detected.")

    if detail == 'short':
        explanation = ' | '.join(descriptions)
    else:
        # Detailed: give AST dump summary (shortened)
        explanation = 'Detailed view: ' + ' | '.join(descriptions)
        explanation += ' -- parsed AST nodes: ' + ','.join([type(n).__name__ for n in ast.walk(tree)][:10])

    # generic tips
    if 'def ' in code and 'type(' not in code:
        tips.append('Consider adding type hints for function parameters and returns')

    return (explanation, tips)
```

### FILE: app/api/v1/explain.py
```
from fastapi import APIRouter, HTTPException
from app.models import ExplainRequest, ExplainResponse
from app.services.explainer import explain_python_code

router = APIRouter()

@router.post('/explain', response_model=ExplainResponse, tags=['Explain'])
async def explain(req: ExplainRequest):
    lang = req.language.lower().strip()
    if lang not in ('python', 'py'):
        raise HTTPException(status_code=400, detail='Only Python is supported in this demo')

    explanation, tips = explain_python_code(req.code, req.detail_level)

    return ExplainResponse(language='python', explanation=explanation, tips=tips)
```

### FILE: tests/test_health.py
```
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    body = r.json()
    assert body['status'] == 'ok'
    assert 'timestamp' in body
```

### FILE: tests/test_explain.py
```
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_explain_simple_function():
    payload = {
        "language": "python",
        "code": "def add(a, b):\n    return a + b",
        "detail_level": "short"
    }
    r = client.post('/api/v1/explain', json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body['language'] == 'python'
    assert 'Function `add`' in body['explanation']
```

### FILE: run_local.sh
```
#!/usr/bin/env bash
uvicorn app.main:app --reload --port 8000
```

### NOTES
```
- This is a starter template focused on clarity and portability.
- Extend services/explainer.py to add support for other languages (JS/Java) using external parsers.
- Add authentication, rate-limiting, caching (Redis), logging, metrics, and CI for production.
