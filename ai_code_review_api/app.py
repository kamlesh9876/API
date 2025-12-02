from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import json
import uuid
import re
import ast
from datetime import datetime, timedelta
import hashlib

app = FastAPI(title="AI Code Review API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class CodeFile(BaseModel):
    filename: str
    language: str
    content: str
    path: str = ""

class Issue(BaseModel):
    id: str
    type: str  # "error", "warning", "info", "suggestion"
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "security", "performance", "style", "logic", "best_practices"
    title: str
    description: str
    line_number: int
    column_number: Optional[int] = None
    code_snippet: str
    suggestion: Optional[str] = None
    rule_id: str
    confidence: float  # 0.0 to 1.0

class CodeMetrics(BaseModel):
    complexity: int
    lines_of_code: int
    comment_lines: int
    blank_lines: int
    maintainability_index: float
    technical_debt: str
    duplication_percentage: float
    test_coverage: Optional[float] = None

class SecurityVulnerability(BaseModel):
    id: str
    type: str  # "sql_injection", "xss", "csrf", "path_traversal", "insecure_deserialization"
    severity: str
    description: str
    line_number: int
    code_snippet: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None

class CodeReview(BaseModel):
    id: str
    repository_url: Optional[str] = None
    files: List[CodeFile]
    overall_score: float  # 0.0 to 100.0
    issues: List[Issue]
    security_vulnerabilities: List[SecurityVulnerability]
    metrics: Dict[str, CodeMetrics]
    summary: str
    recommendations: List[str]
    review_time: datetime
    processing_time: float

class ReviewRequest(BaseModel):
    files: List[CodeFile]
    review_type: str = "comprehensive"  # "security", "performance", "style", "comprehensive"
    language: Optional[str] = None
    custom_rules: Optional[List[Dict[str, Any]]] = None
    exclude_patterns: Optional[List[str]] = None

class ReviewJob(BaseModel):
    id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    request: ReviewRequest
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[CodeReview] = None
    error_message: Optional[str] = None

# In-memory storage
review_jobs: Dict[str, ReviewJob] = {}
code_patterns: Dict[str, Dict] = {
    "python": {
        "security_patterns": [
            {
                "pattern": r"execute\s*\(",
                "type": "sql_injection",
                "severity": "critical",
                "description": "Potential SQL injection vulnerability"
            },
            {
                "pattern": r"eval\s*\(",
                "type": "code_injection",
                "severity": "critical", 
                "description": "Use of eval() function can lead to code injection"
            },
            {
                "pattern": r"pickle\.loads?\s*\(",
                "type": "insecure_deserialization",
                "severity": "high",
                "description": "Insecure deserialization with pickle"
            }
        ],
        "performance_patterns": [
            {
                "pattern": r"for\s+\w+\s+in\s+range\(len\(",
                "type": "inefficient_loop",
                "severity": "medium",
                "description": "Use enumerate() instead of range(len())"
            },
            {
                "pattern": r"\.append\(.*\)\s*for\s+.*\s+in\s+.*\]",
                "type": "list_comprehension",
                "severity": "low",
                "description": "Consider using list comprehension"
            }
        ],
        "style_patterns": [
            {
                "pattern": r"def\s+\w+\([^)]*\):\s*$",
                "type": "missing_docstring",
                "severity": "low",
                "description": "Function should have a docstring"
            },
            {
                "pattern": r"[A-Z_]{2,}\s*=",
                "type": "constant_naming",
                "severity": "low",
                "description": "Constants should be in UPPER_CASE"
            }
        ]
    },
    "javascript": {
        "security_patterns": [
            {
                "pattern": r"innerHTML\s*=",
                "type": "xss",
                "severity": "high",
                "description": "Direct innerHTML assignment can lead to XSS"
            },
            {
                "pattern": r"eval\s*\(",
                "type": "code_injection",
                "severity": "critical",
                "description": "Use of eval() function"
            }
        ],
        "performance_patterns": [
            {
                "pattern": r"for\s*\(\s*var\s+\w+\s*=\s*0\s*;",
                "type": "var_keyword",
                "severity": "medium",
                "description": "Use let/const instead of var"
            }
        ]
    },
    "java": {
        "security_patterns": [
            {
                "pattern": r"Statement\.execute\s*\(",
                "type": "sql_injection",
                "severity": "critical",
                "description": "Potential SQL injection vulnerability"
            }
        ],
        "performance_patterns": [
            {
                "pattern": r"String\s+\w+\s*=\s*.*\s*\+",
                "type": "string_concatenation",
                "severity": "medium",
                "description": "Use StringBuilder for string concatenation"
            }
        ]
    }
}

# Utility functions
def generate_issue_id() -> str:
    """Generate unique issue ID"""
    return f"issue_{uuid.uuid4().hex[:8]}"

def generate_review_id() -> str:
    """Generate unique review ID"""
    return f"review_{uuid.uuid4().hex[:8]}"

def calculate_complexity(code: str, language: str) -> int:
    """Calculate cyclomatic complexity"""
    try:
        if language == "python":
            tree = ast.parse(code)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            return complexity
        else:
            # Simplified complexity calculation for other languages
            control_keywords = ["if", "else", "while", "for", "switch", "case", "catch", "try"]
            complexity = 1
            for keyword in control_keywords:
                complexity += code.lower().count(keyword)
            return complexity
    except:
        return 1

def calculate_metrics(code: str, language: str) -> CodeMetrics:
    """Calculate code metrics"""
    lines = code.split('\n')
    total_lines = len(lines)
    
    # Count different types of lines
    comment_lines = 0
    blank_lines = 0
    code_lines = 0
    
    if language == "python":
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1
    else:
        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith(('//', '/*', '*', '#')):
                comment_lines += 1
            else:
                code_lines += 1
    
    complexity = calculate_complexity(code, language)
    
    # Calculate maintainability index (simplified)
    maintainability = max(0, 171 - 5.2 * math.log(complexity) - 0.23 * complexity - 16.2 * math.log(code_lines))
    
    # Calculate technical debt (simplified)
    tech_debt_hours = max(0, complexity * 2 + (code_lines / 100))
    
    return CodeMetrics(
        complexity=complexity,
        lines_of_code=code_lines,
        comment_lines=comment_lines,
        blank_lines=blank_lines,
        maintainability_index=maintainability,
        technical_debt=f"{tech_debt_hours:.1f}h",
        duplication_percentage=0.0,  # Would need more sophisticated analysis
        test_coverage=None
    )

def analyze_code_patterns(code: str, language: str) -> List[Issue]:
    """Analyze code for patterns and issues"""
    issues = []
    lines = code.split('\n')
    
    patterns = code_patterns.get(language, {})
    
    for category, pattern_list in patterns.items():
        for pattern_info in pattern_list:
            pattern = pattern_info["pattern"]
            issue_type = pattern_info["type"]
            severity = pattern_info["severity"]
            description = pattern_info["description"]
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract code snippet
                    snippet_start = max(0, line_num - 2)
                    snippet_end = min(len(lines), line_num + 2)
                    snippet = '\n'.join(lines[snippet_start:snippet_end])
                    
                    # Generate suggestion
                    suggestion = None
                    if issue_type == "inefficient_loop":
                        suggestion = "Use enumerate() for better performance and readability"
                    elif issue_type == "list_comprehension":
                        suggestion = "Consider using list comprehension for cleaner code"
                    elif issue_type == "missing_docstring":
                        suggestion = "Add a docstring to document the function"
                    elif issue_type == "string_concatenation":
                        suggestion = "Use StringBuilder for better performance"
                    elif issue_type == "var_keyword":
                        suggestion = "Use let/const for block-scoped variables"
                    
                    issue = Issue(
                        id=generate_issue_id(),
                        type="warning" if issue_type in ["style", "performance"] else "error",
                        severity=severity,
                        category=category.replace("_patterns", ""),
                        title=issue_type.replace("_", " ").title(),
                        description=description,
                        line_number=line_num,
                        code_snippet=snippet,
                        suggestion=suggestion,
                        rule_id=f"{language}_{issue_type}",
                        confidence=0.8
                    )
                    issues.append(issue)
    
    return issues

def analyze_security_vulnerabilities(code: str, language: str) -> List[SecurityVulnerability]:
    """Analyze code for security vulnerabilities"""
    vulnerabilities = []
    lines = code.split('\n')
    
    security_patterns = code_patterns.get(language, {}).get("security_patterns", [])
    
    for pattern_info in security_patterns:
        pattern = pattern_info["pattern"]
        vuln_type = pattern_info["type"]
        severity = pattern_info["severity"]
        description = pattern_info["description"]
        
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                snippet_start = max(0, line_num - 1)
                snippet_end = min(len(lines), line_num + 1)
                snippet = '\n'.join(lines[snippet_start:snippet_end])
                
                # Map to CWE IDs
                cwe_mapping = {
                    "sql_injection": "CWE-89",
                    "xss": "CWE-79",
                    "code_injection": "CWE-94",
                    "insecure_deserialization": "CWE-502"
                }
                
                # CVSS scores (simplified)
                cvss_mapping = {
                    "critical": 9.0,
                    "high": 7.5,
                    "medium": 5.5,
                    "low": 3.0
                }
                
                vulnerability = SecurityVulnerability(
                    id=generate_issue_id(),
                    type=vuln_type,
                    severity=severity,
                    description=description,
                    line_number=line_num,
                    code_snippet=snippet,
                    cwe_id=cwe_mapping.get(vuln_type),
                    cvss_score=cvss_mapping.get(severity)
                )
                vulnerabilities.append(vulnerability)
    
    return vulnerabilities

async def perform_code_review(job_id: str):
    """Perform comprehensive code review"""
    job = review_jobs[job_id]
    
    try:
        job.status = "processing"
        job.progress = 0.1
        
        all_issues = []
        all_vulnerabilities = []
        all_metrics = {}
        total_files = len(job.request.files)
        
        for i, file in enumerate(job.request.files):
            # Update progress
            job.progress = 0.1 + (i / total_files) * 0.8
            
            # Analyze patterns
            issues = analyze_code_patterns(file.content, file.language)
            all_issues.extend(issues)
            
            # Security analysis
            vulnerabilities = analyze_security_vulnerabilities(file.content, file.language)
            all_vulnerabilities.extend(vulnerabilities)
            
            # Calculate metrics
            metrics = calculate_metrics(file.content, file.language)
            all_metrics[file.filename] = metrics
            
            await asyncio.sleep(0.1)  # Simulate processing time
        
        # Calculate overall score
        critical_issues = len([i for i in all_issues if i.severity == "critical"])
        high_issues = len([i for i in all_issues if i.severity == "high"])
        medium_issues = len([i for i in all_issues if i.severity == "medium"])
        low_issues = len([i for i in all_issues if i.severity == "low"])
        
        critical_vulns = len([v for v in all_vulnerabilities if v.severity == "critical"])
        high_vulns = len([v for v in all_vulnerabilities if v.severity == "high"])
        
        # Score calculation (0-100)
        score = 100.0
        score -= critical_issues * 20
        score -= high_issues * 10
        score -= medium_issues * 5
        score -= low_issues * 2
        score -= critical_vulns * 25
        score -= high_vulns * 15
        score = max(0, score)
        
        # Generate summary
        summary_parts = []
        if critical_issues > 0 or critical_vulns > 0:
            summary_parts.append(f"Found {critical_issues + critical_vulns} critical issues requiring immediate attention")
        if high_issues > 0 or high_vulns > 0:
            summary_parts.append(f"Found {high_issues + high_vulns} high-priority issues")
        if score >= 80:
            summary_parts.append("Overall code quality is good")
        elif score >= 60:
            summary_parts.append("Code quality needs improvement")
        else:
            summary_parts.append("Code quality requires significant improvement")
        
        summary = ". ".join(summary_parts) + "."
        
        # Generate recommendations
        recommendations = []
        if critical_vulns > 0:
            recommendations.append("Address all critical security vulnerabilities immediately")
        if critical_issues > 0:
            recommendations.append("Fix critical issues before deploying to production")
        if high_issues > 5:
            recommendations.append("Consider refactoring to reduce complexity")
        if any(m.complexity > 10 for m in all_metrics.values()):
            recommendations.append("Reduce function complexity for better maintainability")
        if any(m.maintainability_index < 60 for m in all_metrics.values()):
            recommendations.append("Improve code documentation and structure")
        
        # Create review result
        review = CodeReview(
            id=generate_review_id(),
            files=job.request.files,
            overall_score=score,
            issues=all_issues,
            security_vulnerabilities=all_vulnerabilities,
            metrics=all_metrics,
            summary=summary,
            recommendations=recommendations,
            review_time=datetime.now(),
            processing_time=0.0  # Would calculate actual processing time
        )
        
        job.result = review
        job.status = "completed"
        job.progress = 1.0
        job.completed_at = datetime.now()
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.progress = 0.0

# API Endpoints
@app.post("/api/review", response_model=ReviewJob)
async def create_review_job(request: ReviewRequest, background_tasks: BackgroundTasks):
    """Create a new code review job"""
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    
    job = ReviewJob(
        id=job_id,
        status="pending",
        progress=0.0,
        request=request,
        created_at=datetime.now()
    )
    
    review_jobs[job_id] = job
    
    # Start review process
    background_tasks.add_task(perform_code_review, job_id)
    
    return job

@app.get("/api/review/{job_id}", response_model=ReviewJob)
async def get_review_job(job_id: str):
    """Get review job status"""
    if job_id not in review_jobs:
        raise HTTPException(status_code=404, detail="Review job not found")
    return review_jobs[job_id]

@app.get("/api/review/{job_id}/result", response_model=CodeReview)
async def get_review_result(job_id: str):
    """Get review result"""
    if job_id not in review_jobs:
        raise HTTPException(status_code=404, detail="Review job not found")
    
    job = review_jobs[job_id]
    
    if not job.result:
        raise HTTPException(status_code=400, detail="Review not completed yet")
    
    return job.result

@app.get("/api/review/{job_id}/summary")
async def get_review_summary(job_id: str):
    """Get review summary only"""
    if job_id not in review_jobs:
        raise HTTPException(status_code=404, detail="Review job not found")
    
    job = review_jobs[job_id]
    
    if not job.result:
        raise HTTPException(status_code=400, detail="Review not completed yet")
    
    result = job.result
    
    return {
        "overall_score": result.overall_score,
        "summary": result.summary,
        "total_issues": len(result.issues),
        "critical_issues": len([i for i in result.issues if i.severity == "critical"]),
        "security_vulnerabilities": len(result.security_vulnerabilities),
        "recommendations": result.recommendations
    }

@app.get("/api/jobs", response_model=List[ReviewJob])
async def list_review_jobs(status: Optional[str] = None, limit: int = 50):
    """List review jobs"""
    jobs = list(review_jobs.values())
    
    if status:
        jobs = [job for job in jobs if job.status == status]
    
    return sorted(jobs, key=lambda x: x.created_at, reverse=True)[:limit]

@app.get("/api/patterns/{language}")
async def get_code_patterns(language: str):
    """Get code patterns for a specific language"""
    patterns = code_patterns.get(language.lower(), {})
    return {"language": language, "patterns": patterns}

@app.get("/api/stats")
async def get_review_stats():
    """Get review statistics"""
    total_jobs = len(review_jobs)
    completed_jobs = len([j for j in review_jobs.values() if j.status == "completed"])
    failed_jobs = len([j for j in review_jobs.values() if j.status == "failed"])
    
    # Calculate average score
    completed_results = [j.result for j in review_jobs.values() if j.result]
    avg_score = sum(r.overall_score for r in completed_results) / len(completed_results) if completed_results else 0
    
    # Issue statistics
    all_issues = []
    all_vulnerabilities = []
    for result in completed_results:
        all_issues.extend(result.issues)
        all_vulnerabilities.extend(result.security_vulnerabilities)
    
    return {
        "total_reviews": total_jobs,
        "completed_reviews": completed_jobs,
        "failed_reviews": failed_jobs,
        "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
        "average_score": avg_score,
        "total_issues_found": len(all_issues),
        "total_vulnerabilities_found": len(all_vulnerabilities),
        "supported_languages": list(code_patterns.keys()),
        "issue_categories": ["security", "performance", "style", "logic", "best_practices"]
    }

@app.delete("/api/review/{job_id}")
async def delete_review_job(job_id: str):
    """Delete review job"""
    if job_id not in review_jobs:
        raise HTTPException(status_code=404, detail="Review job not found")
    
    del review_jobs[job_id]
    return {"message": "Review job deleted successfully"}

@app.get("/")
async def root():
    return {"message": "AI Code Review API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    import math
    uvicorn.run(app, host="0.0.0.0", port=8000)
