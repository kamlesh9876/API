from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid
import os
import tempfile
import subprocess
import json
import re
import ast
import tree_sitter
from tree_sitter import Language, Parser
import requests
from pathlib import Path
import logging

app = FastAPI(title="AI Code Explainer API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    TYPESCRIPT = "typescript"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"

class AnalysisType(str, Enum):
    EXPLAIN = "explain"
    DEBUG = "debug"
    OPTIMIZE = "optimize"
    DOCUMENT = "document"
    REFACTOR = "refactor"
    SECURITY = "security"

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Pydantic models
class CodeIssue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    severity: SeverityLevel
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)

class CodeExplanation(BaseModel):
    overview: str
    purpose: str
    key_components: List[str]
    algorithms_used: List[str]
    data_structures: List[str]
    complexity_analysis: Optional[str] = None
    dependencies: List[str]
    potential_improvements: List[str]

class CodeSuggestion(BaseModel):
    type: str
    description: str
    before_code: Optional[str] = None
    after_code: Optional[str] = None
    reasoning: str
    impact: str

class SecurityVulnerability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    severity: SeverityLevel
    description: str
    location: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: str
    references: List[str] = []

class CodeAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    language: ProgrammingLanguage
    file_name: str
    analysis_type: AnalysisType
    timestamp: datetime = Field(default_factory=datetime.now)
    explanation: Optional[CodeExplanation] = None
    issues: List[CodeIssue] = []
    suggestions: List[CodeSuggestion] = []
    security_vulnerabilities: List[SecurityVulnerability] = []
    metrics: Dict[str, Any] = {}
    processing_time: float
    model_used: str

class AnalysisRequest(BaseModel):
    code: str
    language: ProgrammingLanguage
    analysis_types: List[AnalysisType] = [AnalysisType.EXPLAIN]
    context: Optional[str] = None
    focus_areas: Optional[List[str]] = None

# Tree-sitter language parsers (mock implementation)
# In production, you would download actual tree-sitter language libraries
LANGUAGE_PARSERS = {
    ProgrammingLanguage.PYTHON: "python",
    ProgrammingLanguage.JAVASCRIPT: "javascript",
    ProgrammingLanguage.JAVA: "java"
}

# Local LLM configuration (mock implementation)
class LocalLLMService:
    """Mock Local LLM Service for demonstration"""
    
    def __init__(self):
        self.model_name = "llama-2-7b-chat"
        self.base_url = "http://localhost:8080"  # Local LLM server
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response from local LLM"""
        # Mock implementation - in production, this would call actual LLM
        try:
            # Simulate LLM API call
            response = self._mock_llm_response(prompt)
            return response
        except Exception as e:
            logger.error(f"LLM service error: {e}")
            return self._fallback_response(prompt)
    
    def _mock_llm_response(self, prompt: str) -> str:
        """Mock LLM response for demonstration"""
        if "explain" in prompt.lower():
            return """
This code implements a web server using FastAPI framework. It defines REST endpoints for managing user data,
including CRUD operations (Create, Read, Update, Delete). The code uses Pydantic models for data validation
and SQLAlchemy for database interactions. Key components include:

1. FastAPI application instance
2. Pydantic models for request/response validation
3. Database session management
4. Error handling middleware
5. API route definitions

The code follows RESTful principles and includes proper error handling and data validation.
"""
        elif "debug" in prompt.lower():
            return """
Potential issues found:
1. Missing error handling for database operations
2. No input validation for user-provided data
3. Potential SQL injection vulnerabilities
4. Missing authentication/authorization
5. No rate limiting implemented

Suggestions:
- Add try-catch blocks for database operations
- Implement proper input validation
- Use parameterized queries
- Add authentication middleware
- Implement rate limiting
"""
        elif "security" in prompt.lower():
            return """
Security vulnerabilities identified:
1. SQL Injection risk in database queries
2. Missing authentication on sensitive endpoints
3. No input sanitization
4. Potential XSS in response data
5. Missing CORS configuration

Recommendations:
- Use parameterized queries or ORM
- Implement JWT authentication
- Sanitize all user inputs
- Escape output data
- Configure CORS properly
"""
        else:
            return "Analysis completed successfully with comprehensive insights."
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is unavailable"""
        return "Analysis completed using rule-based approach. For more detailed analysis, please configure a local LLM service."

# HuggingFace model service (mock implementation)
class HuggingFaceService:
    """Mock HuggingFace service for code analysis"""
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models"
        self.models = {
            "code-analysis": "microsoft/CodeBERT-base",
            "vulnerability": "deepset/roberta-base-squad2"
        }
    
    async def analyze_code(self, code: str, task: str) -> Dict[str, Any]:
        """Analyze code using HuggingFace models"""
        # Mock implementation
        return {
            "analysis": "Code analyzed using HuggingFace models",
            "confidence": 0.85,
            "issues": [],
            "suggestions": []
        }

# Code analysis service
class CodeAnalyzer:
    def __init__(self):
        self.llm_service = LocalLLMService()
        self.hf_service = HuggingFaceService()
    
    async def analyze_code(self, request: AnalysisRequest) -> CodeAnalysisResult:
        """Analyze code based on request"""
        import time
        start_time = time.time()
        
        result = CodeAnalysisResult(
            language=request.language,
            file_name="uploaded_code",
            analysis_type=request.analysis_types[0] if request.analysis_types else AnalysisType.EXPLAIN,
            model_used="local_llm"
        )
        
        # Perform different types of analysis
        for analysis_type in request.analysis_types:
            if analysis_type == AnalysisType.EXPLAIN:
                result.explanation = await self._explain_code(request.code, request.language)
            elif analysis_type == AnalysisType.DEBUG:
                result.issues = await self._debug_code(request.code, request.language)
            elif analysis_type == AnalysisType.OPTIMIZE:
                result.suggestions = await self._optimize_code(request.code, request.language)
            elif analysis_type == AnalysisType.SECURITY:
                result.security_vulnerabilities = await self._analyze_security(request.code, request.language)
            elif analysis_type == AnalysisType.DOCUMENT:
                result.explanation = await self._generate_documentation(request.code, request.language)
            elif analysis_type == AnalysisType.REFACTOR:
                result.suggestions = await self._suggest_refactoring(request.code, request.language)
        
        # Calculate metrics
        result.metrics = self._calculate_metrics(request.code, request.language)
        
        processing_time = time.time() - start_time
        result.processing_time = processing_time
        
        return result
    
    async def _explain_code(self, code: str, language: ProgrammingLanguage) -> CodeExplanation:
        """Explain what the code does"""
        prompt = f"""
Please explain the following {language.value} code:

{code}

Provide:
1. Overview of what the code does
2. Main purpose and functionality
3. Key components and their roles
4. Algorithms used (if any)
5. Data structures used
6. Dependencies and imports
7. Potential areas for improvement
"""
        
        response = await self.llm_service.generate_response(prompt)
        
        # Parse response into structured format (simplified)
        return CodeExplanation(
            overview="This code implements web application functionality",
            purpose="To provide API endpoints for data management",
            key_components=["FastAPI app", "Database models", "API routes"],
            algorithms_used=["REST API design", "CRUD operations"],
            data_structures=["Dictionaries", "Lists", "Database models"],
            complexity_analysis="Time complexity: O(n) for most operations",
            dependencies=["fastapi", "pydantic", "sqlalchemy"],
            potential_improvements=["Add caching", "Implement pagination", "Add tests"]
        )
    
    async def _debug_code(self, code: str, language: ProgrammingLanguage) -> List[CodeIssue]:
        """Find potential bugs and issues"""
        issues = []
        
        # Static analysis for common issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for common issues
            if 'print(' in line and language == ProgrammingLanguage.PYTHON:
                issues.append(CodeIssue(
                    type="debug_statement",
                    severity=SeverityLevel.LOW,
                    message="Debug print statement found in production code",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Remove or replace with proper logging",
                    confidence=0.9
                ))
            
            if 'TODO:' in line_stripped or 'FIXME:' in line_stripped:
                issues.append(CodeIssue(
                    type="incomplete_code",
                    severity=SeverityLevel.MEDIUM,
                    message="TODO/FIXME comment indicates incomplete implementation",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Complete the implementation or remove the comment",
                    confidence=0.8
                ))
            
            if 'except:' in line_stripped and 'except Exception' not in line_stripped:
                issues.append(CodeIssue(
                    type="bare_except",
                    severity=SeverityLevel.HIGH,
                    message="Bare except clause catches all exceptions",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Specify the exception types you want to catch",
                    confidence=0.95
                ))
            
            if 'eval(' in line_stripped:
                issues.append(CodeIssue(
                    type="security_risk",
                    severity=SeverityLevel.CRITICAL,
                    message="Use of eval() function poses security risk",
                    line_number=i,
                    code_snippet=line.strip(),
                    suggestion="Avoid eval() or use safer alternatives",
                    confidence=1.0
                ))
        
        # Use LLM for deeper analysis
        prompt = f"""
Analyze the following {language.value} code for bugs and issues:

{code}

Identify:
1. Logic errors
2. Performance issues
3. Code smells
4. Potential runtime errors
5. Best practice violations
"""
        
        llm_response = await self.llm_service.generate_response(prompt)
        
        # Parse LLM response for additional issues (simplified)
        if "SQL injection" in llm_response:
            issues.append(CodeIssue(
                type="sql_injection",
                severity=SeverityLevel.CRITICAL,
                message="Potential SQL injection vulnerability",
                suggestion="Use parameterized queries or ORM",
                confidence=0.8
            ))
        
        return issues
    
    async def _optimize_code(self, code: str, language: ProgrammingLanguage) -> List[CodeSuggestion]:
        """Provide optimization suggestions"""
        suggestions = []
        
        # Static analysis for optimization opportunities
        if language == ProgrammingLanguage.PYTHON:
            # Check for inefficient loops
            if 'for i in range(len(' in code:
                suggestions.append(CodeSuggestion(
                    type="performance",
                    description="Use enumerate() instead of range(len())",
                    before_code="for i in range(len(items)):",
                    after_code="for i, item in enumerate(items):",
                    reasoning="More Pythonic and readable",
                    impact="Minor performance improvement, better readability"
                ))
            
            # Check for list comprehension opportunities
            if 'result = []' in code and 'for item in' in code:
                suggestions.append(CodeSuggestion(
                    type="performance",
                    description="Consider using list comprehension",
                    before_code="result = []\nfor item in items:\n    result.append(item * 2)",
                    after_code="result = [item * 2 for item in items]",
                    reasoning="List comprehensions are more efficient",
                    impact="Performance improvement and cleaner code"
                ))
        
        # Use LLM for optimization suggestions
        prompt = f"""
Analyze the following {language.value} code and provide optimization suggestions:

{code}

Focus on:
1. Performance improvements
2. Code readability
3. Best practices
4. Memory usage
5. Algorithm efficiency
"""
        
        llm_response = await self.llm_service.generate_response(prompt)
        
        # Parse LLM response for suggestions (simplified)
        if "cache" in llm_response.lower():
            suggestions.append(CodeSuggestion(
                type="performance",
                description="Implement caching for frequently accessed data",
                reasoning="Caching can significantly improve performance",
                impact="Major performance improvement for repeated operations"
            ))
        
        return suggestions
    
    async def _analyze_security(self, code: str, language: ProgrammingLanguage) -> List[SecurityVulnerability]:
        """Analyze code for security vulnerabilities"""
        vulnerabilities = []
        
        # Static security analysis
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for common security issues
            if 'password' in line.lower() and '=' in line:
                vulnerabilities.append(SecurityVulnerability(
                    type="hardcoded_credential",
                    severity=SeverityLevel.HIGH,
                    description="Hardcoded password or credential detected",
                    location=f"Line {i}",
                    cwe_id="CWE-798",
                    remediation="Use environment variables or secure credential storage",
                    references=["https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication"]
                ))
            
            if 'exec(' in line_stripped or 'eval(' in line_stripped:
                vulnerabilities.append(SecurityVulnerability(
                    type="code_injection",
                    severity=SeverityLevel.CRITICAL,
                    description="Use of dynamic code execution functions",
                    location=f"Line {i}",
                    cwe_id="CWE-94",
                    remediation="Avoid dynamic code execution or validate inputs strictly",
                    references=["https://owasp.org/www-project-top-ten/2017/A1_2017-Injection"]
                ))
            
            if 'sql' in line.lower() and '+' in line and language == ProgrammingLanguage.PYTHON:
                vulnerabilities.append(SecurityVulnerability(
                    type="sql_injection",
                    severity=SeverityLevel.CRITICAL,
                    description="Potential SQL injection vulnerability",
                    location=f"Line {i}",
                    cwe_id="CWE-89",
                    remediation="Use parameterized queries or ORM",
                    references=["https://owasp.org/www-project-top-ten/2017/A1_2017-Injection"]
                ))
        
        # Use LLM for security analysis
        prompt = f"""
Perform a comprehensive security analysis of the following {language.value} code:

{code}

Identify:
1. Input validation issues
2. Authentication/authorization flaws
3. Data exposure risks
4. Injection vulnerabilities
5. Cryptographic weaknesses
6. Configuration security issues
"""
        
        llm_response = await self.llm_service.generate_response(prompt)
        
        # Parse LLM response for vulnerabilities (simplified)
        if "xss" in llm_response.lower():
            vulnerabilities.append(SecurityVulnerability(
                type="xss",
                severity=SeverityLevel.HIGH,
                description="Potential Cross-Site Scripting vulnerability",
                location="Multiple locations",
                cwe_id="CWE-79",
                remediation="Sanitize user input and escape output",
                references=["https://owasp.org/www-project-top-ten/2017/A7_2017-Cross_Site_Scripting"]
            ))
        
        return vulnerabilities
    
    async def _generate_documentation(self, code: str, language: ProgrammingLanguage) -> CodeExplanation:
        """Generate documentation for the code"""
        prompt = f"""
Generate comprehensive documentation for the following {language.value} code:

{code}

Include:
1. Function/class descriptions
2. Parameter documentation
3. Return value descriptions
4. Usage examples
5. Dependencies and requirements
"""
        
        response = await self.llm_service.generate_response(prompt)
        
        return CodeExplanation(
            overview="Auto-generated documentation",
            purpose="To provide comprehensive code documentation",
            key_components=["Functions", "Classes", "Modules"],
            algorithms_used=["Various algorithms as implemented"],
            data_structures=["Data structures used in code"],
            dependencies=["List of dependencies"],
            potential_improvements=["Documentation improvements"]
        )
    
    async def _suggest_refactoring(self, code: str, language: ProgrammingLanguage) -> List[CodeSuggestion]:
        """Suggest refactoring improvements"""
        suggestions = []
        
        # Static analysis for refactoring opportunities
        lines = code.split('\n')
        
        # Check for long functions (simplified)
        function_count = 0
        for line in lines:
            if 'def ' in line or 'function ' in line:
                function_count += 1
        
        if function_count == 0 and len(lines) > 50:
            suggestions.append(CodeSuggestion(
                type="refactoring",
                description="Consider breaking down large code into functions",
                reasoning="Improves readability and maintainability",
                impact="Better code organization and reusability"
            ))
        
        # Check for code duplication (simplified)
        if lines.count(lines[0]) > 1:
            suggestions.append(CodeSuggestion(
                type="refactoring",
                description="Extract duplicated code into functions",
                reasoning="Follows DRY principle",
                impact="Reduced code duplication, easier maintenance"
            ))
        
        # Use LLM for refactoring suggestions
        prompt = f"""
Analyze the following {language.value} code and suggest refactoring improvements:

{code}

Focus on:
1. Code organization
2. Design patterns
3. Code duplication
4. Complexity reduction
5. Maintainability improvements
"""
        
        llm_response = await self.llm_service.generate_response(prompt)
        
        # Parse LLM response for suggestions (simplified)
        if "extract" in llm_response.lower():
            suggestions.append(CodeSuggestion(
                type="refactoring",
                description="Extract common functionality into helper functions",
                reasoning="Improves code reusability and reduces duplication",
                impact="Better maintainability and reduced code size"
            ))
        
        return suggestions
    
    def _calculate_metrics(self, code: str, language: ProgrammingLanguage) -> Dict[str, Any]:
        """Calculate code metrics"""
        lines = code.split('\n')
        
        # Basic metrics
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')])
        
        # Language-specific metrics
        if language == ProgrammingLanguage.PYTHON:
            functions = len(re.findall(r'def\s+\w+', code))
            classes = len(re.findall(r'class\s+\w+', code))
            imports = len(re.findall(r'import\s+\w+|from\s+\w+\s+import', code))
        elif language == ProgrammingLanguage.JAVASCRIPT:
            functions = len(re.findall(r'function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=', code))
            classes = len(re.findall(r'class\s+\w+', code))
            imports = len(re.findall(r'import.*from|require\(', code))
        else:
            functions = 0
            classes = 0
            imports = 0
        
        # Complexity metrics (simplified)
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(code, language)
        
        return {
            "total_lines": total_lines,
            "non_empty_lines": non_empty_lines,
            "comment_lines": comment_lines,
            "comment_ratio": comment_lines / non_empty_lines if non_empty_lines > 0 else 0,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "cyclomatic_complexity": cyclomatic_complexity,
            "maintainability_index": self._calculate_maintainability_index(
                total_lines, functions, cyclomatic_complexity
            )
        }
    
    def _calculate_cyclomatic_complexity(self, code: str, language: ProgrammingLanguage) -> int:
        """Calculate cyclomatic complexity (simplified)"""
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = {
            ProgrammingLanguage.PYTHON: ['if', 'elif', 'for', 'while', 'except', 'with'],
            ProgrammingLanguage.JAVASCRIPT: ['if', 'for', 'while', 'catch', 'switch'],
            ProgrammingLanguage.JAVA: ['if', 'for', 'while', 'catch', 'switch', 'case']
        }
        
        keywords = decision_keywords.get(language, [])
        for keyword in keywords:
            complexity += len(re.findall(r'\b' + keyword + r'\b', code))
        
        return complexity
    
    def _calculate_maintainability_index(self, lines: int, functions: int, complexity: int) -> float:
        """Calculate maintainability index (simplified)"""
        if functions == 0:
            return 100.0
        
        # Simplified maintainability index calculation
        mi = 100 - (complexity * 0.1) - (lines * 0.01) + (functions * 0.5)
        return max(0.0, min(100.0, mi))

# Initialize analyzer
analyzer = CodeAnalyzer()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to AI Code Explainer API", "version": "1.0.0"}

@app.post("/analyze", response_model=CodeAnalysisResult)
async def analyze_code(request: AnalysisRequest):
    """Analyze code using AI models"""
    try:
        result = await analyzer.analyze_code(request)
        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/file", response_model=CodeAnalysisResult)
async def analyze_file(
    file: UploadFile = File(...),
    language: ProgrammingLanguage = Form(...),
    analysis_types: str = Form("explain")  # Comma-separated list
):
    """Analyze uploaded code file"""
    try:
        # Read file content
        content = await file.read()
        code = content.decode('utf-8')
        
        # Parse analysis types
        types = [AnalysisType(t.strip()) for t in analysis_types.split(',') if t.strip()]
        
        # Create analysis request
        request = AnalysisRequest(
            code=code,
            language=language,
            analysis_types=types
        )
        
        result = await analyzer.analyze_code(request)
        result.file_name = file.filename
        
        return result
        
    except Exception as e:
        logger.error(f"File analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.post("/explain")
async def explain_code(
    code: str = Form(...),
    language: ProgrammingLanguage = Form(...),
    context: Optional[str] = Form(None)
):
    """Get code explanation"""
    request = AnalysisRequest(
        code=code,
        language=language,
        analysis_types=[AnalysisType.EXPLAIN],
        context=context
    )
    
    result = await analyzer.analyze_code(request)
    return result.explanation

@app.post("/debug")
async def debug_code(
    code: str = Form(...),
    language: ProgrammingLanguage = Form(...)
):
    """Debug code and find issues"""
    request = AnalysisRequest(
        code=code,
        language=language,
        analysis_types=[AnalysisType.DEBUG]
    )
    
    result = await analyzer.analyze_code(request)
    return {
        "issues": result.issues,
        "metrics": result.metrics,
        "processing_time": result.processing_time
    }

@app.post("/optimize")
async def optimize_code(
    code: str = Form(...),
    language: ProgrammingLanguage = Form(...)
):
    """Get optimization suggestions"""
    request = AnalysisRequest(
        code=code,
        language=language,
        analysis_types=[AnalysisType.OPTIMIZE]
    )
    
    result = await analyzer.analyze_code(request)
    return {
        "suggestions": result.suggestions,
        "metrics": result.metrics,
        "processing_time": result.processing_time
    }

@app.post("/security")
async def analyze_security(
    code: str = Form(...),
    language: ProgrammingLanguage = Form(...)
):
    """Analyze code for security vulnerabilities"""
    request = AnalysisRequest(
        code=code,
        language=language,
        analysis_types=[AnalysisType.SECURITY]
    )
    
    result = await analyzer.analyze_code(request)
    return {
        "vulnerabilities": result.security_vulnerabilities,
        "severity_summary": {
            "critical": len([v for v in result.security_vulnerabilities if v.severity == SeverityLevel.CRITICAL]),
            "high": len([v for v in result.security_vulnerabilities if v.severity == SeverityLevel.HIGH]),
            "medium": len([v for v in result.security_vulnerabilities if v.severity == SeverityLevel.MEDIUM]),
            "low": len([v for v in result.security_vulnerabilities if v.severity == SeverityLevel.LOW])
        },
        "processing_time": result.processing_time
    }

@app.post("/document")
async def generate_documentation(
    code: str = Form(...),
    language: ProgrammingLanguage = Form(...)
):
    """Generate documentation for code"""
    request = AnalysisRequest(
        code=code,
        language=language,
        analysis_types=[AnalysisType.DOCUMENT]
    )
    
    result = await analyzer.analyze_code(request)
    return result.explanation

@app.post("/refactor")
async def suggest_refactoring(
    code: str = Form(...),
    language: ProgrammingLanguage = Form(...)
):
    """Suggest refactoring improvements"""
    request = AnalysisRequest(
        code=code,
        language=language,
        analysis_types=[AnalysisType.REFACTOR]
    )
    
    result = await analyzer.analyze_code(request)
    return {
        "suggestions": result.suggestions,
        "metrics": result.metrics,
        "processing_time": result.processing_time
    }

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": [
            {
                "code": lang.value,
                "name": lang.value.title(),
                "supported": True
            }
            for lang in ProgrammingLanguage
        ]
    }

@app.get("/analysis-types")
async def get_analysis_types():
    """Get list of available analysis types"""
    return {
        "analysis_types": [
            {
                "code": atype.value,
                "name": atype.value.replace('_', ' ').title(),
                "description": {
                    AnalysisType.EXPLAIN: "Explain what the code does and how it works",
                    AnalysisType.DEBUG: "Find bugs, issues, and potential problems",
                    AnalysisType.OPTIMIZE: "Suggest performance and efficiency improvements",
                    AnalysisType.DOCUMENT: "Generate comprehensive documentation",
                    AnalysisType.SECURITY: "Analyze for security vulnerabilities",
                    AnalysisType.REFACTOR: "Suggest code refactoring improvements"
                }.get(atype, "")
            }
            for atype in AnalysisType
        ]
    }

@app.get("/models/status")
async def get_model_status():
    """Get status of AI models"""
    return {
        "local_llm": {
            "status": "configured",
            "model": "llama-2-7b-chat",
            "endpoint": "http://localhost:8080",
            "available": True
        },
        "huggingface": {
            "status": "configured",
            "models": ["microsoft/CodeBERT-base", "deepset/roberta-base-squad2"],
            "available": True
        },
        "tree_sitter": {
            "status": "configured",
            "languages": list(LANGUAGE_PARSERS.keys()),
            "available": True
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "services": {
            "local_llm": "available",
            "huggingface": "available",
            "tree_sitter": "available"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
