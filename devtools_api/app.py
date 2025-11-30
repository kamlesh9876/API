from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid
import hashlib
import base64
import re
import secrets
import string
import logging
import json
from urllib.parse import quote, unquote
import binascii
import time

app = FastAPI(
    title="DevTools API - Ultimate Developer Helper",
    description="A comprehensive API with multiple developer tools including Base64 encoding/decoding, hash generation, password strength checking, and UUID generation",
    version="1.0.0"
)

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
class HashAlgorithm(str, Enum):
    MD5 = "md5"
    SHA1 = "sha1"
    SHA224 = "sha224"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA3_224 = "sha3_224"
    SHA3_256 = "sha3_256"
    SHA3_384 = "sha3_384"
    SHA3_512 = "sha3_512"

class UUIDVersion(str, Enum):
    V1 = "1"
    V3 = "3"
    V4 = "4"
    V5 = "5"

class PasswordStrength(str, Enum):
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

# Pydantic Models
class Base64Request(BaseModel):
    text: str = Field(..., description="Text to encode/decode")
    encoding: str = Field("utf-8", description="Text encoding")

class Base64Response(BaseModel):
    input_text: str
    output_text: str
    operation: str
    encoding: str
    timestamp: datetime

class HashRequest(BaseModel):
    text: str = Field(..., description="Text to hash")
    algorithm: HashAlgorithm = Field(HashAlgorithm.SHA256, description="Hash algorithm")
    encoding: str = Field("utf-8", description="Text encoding")
    output_format: str = Field("hex", description="Output format: hex or base64")

class HashResponse(BaseModel):
    input_text: str
    algorithm: str
    hash_value: str
    output_format: str
    encoding: str
    timestamp: datetime

class PasswordStrengthRequest(BaseModel):
    password: str = Field(..., min_length=1, description="Password to check")
    username: Optional[str] = Field(None, description="Username to check against")
    email: Optional[str] = Field(None, description="Email to check against")
    common_passwords: Optional[bool] = Field(True, description="Check against common passwords")

class PasswordStrengthResponse(BaseModel):
    password: str
    strength: PasswordStrength
    score: int  # 0-100
    length: int
    feedback: List[str]
    suggestions: List[str]
    time_to_crack: str
    entropy: float
    timestamp: datetime

class UUIDRequest(BaseModel):
    version: UUIDVersion = Field(UUIDVersion.V4, description="UUID version")
    namespace: Optional[str] = Field(None, description="Namespace for UUID v3/v5")
    name: Optional[str] = Field(None, description="Name for UUID v3/v5")
    count: int = Field(1, ge=1, le=100, description="Number of UUIDs to generate")

class UUIDResponse(BaseModel):
    uuids: List[str]
    version: str
    count: int
    timestamp: datetime

class BulkHashRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=50, description="List of texts to hash")
    algorithm: HashAlgorithm = Field(HashAlgorithm.SHA256, description="Hash algorithm")
    encoding: str = Field("utf-8", description="Text encoding")
    output_format: str = Field("hex", description="Output format: hex or base64")

class BulkHashResponse(BaseModel):
    results: List[Dict[str, Any]]
    algorithm: str
    count: int
    timestamp: datetime

class TextAnalyzerRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    include_stats: bool = Field(True, description="Include detailed statistics")

class TextAnalyzerResponse(BaseModel):
    text_length: int
    word_count: int
    character_count: int
    line_count: int
    paragraph_count: int
    unique_words: int
    readability_score: Optional[float]
    language: Optional[str]
    timestamp: datetime

# Utility Functions
def calculate_entropy(password: str) -> float:
    """Calculate password entropy"""
    charset_size = 0
    
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)
    
    if charset_size == 0:
        return 0.0
    
    import math
    entropy = len(password) * math.log2(charset_size)
    return entropy

def estimate_crack_time(entropy: float) -> str:
    """Estimate time to crack password based on entropy"""
    # Assuming 10^9 guesses per second
    guesses_per_second = 10**9
    total_combinations = 2 ** entropy
    seconds_to_crack = total_combinations / (2 * guesses_per_second)  # Average case
    
    if seconds_to_crack < 1:
        return "Less than a second"
    elif seconds_to_crack < 60:
        return f"{int(seconds_to_crack)} seconds"
    elif seconds_to_crack < 3600:
        return f"{int(seconds_to_crack / 60)} minutes"
    elif seconds_to_crack < 86400:
        return f"{int(seconds_to_crack / 3600)} hours"
    elif seconds_to_crack < 2592000:
        return f"{int(seconds_to_crack / 86400)} days"
    elif seconds_to_crack < 31536000:
        return f"{int(seconds_to_crack / 2592000)} months"
    elif seconds_to_crack < 3153600000:
        return f"{int(seconds_to_crack / 31536000)} years"
    else:
        return "Centuries"

def check_common_passwords(password: str) -> bool:
    """Check if password is in common passwords list"""
    # Top 100 most common passwords (simplified list)
    common_passwords = {
        "password", "123456", "123456789", "12345678", "12345", "1234567",
        "password1", "1234567890", "qwerty", "abc123", "111111", "123123",
        "admin", "letmein", "welcome", "monkey", "1234", "dragon", "master",
        "hello", "freedom", "whatever", "qazwsx", "trustno1", "123qwe",
        "1q2w3e4r", "zxcvbnm", "iloveyou", "sunshine", "princess",
        "football", "baseball", "shadow", "superman", "azerty", "computer"
    }
    
    return password.lower() in common_passwords

def check_password_patterns(password: str, username: Optional[str] = None, email: Optional[str] = None) -> List[str]:
    """Check for common password patterns"""
    patterns = []
    
    # Check for sequential characters
    if re.search(r'(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
        patterns.append("Contains sequential characters")
    
    # Check for repeated characters
    if re.search(r'(.)\1{2,}', password):
        patterns.append("Contains repeated characters")
    
    # Check for keyboard patterns
    if re.search(r'(?:qwerty|asdf|zxcv|1234|2345|3456|4567|5678|6789|7890)', password.lower()):
        patterns.append("Contains keyboard patterns")
    
    # Check if password contains username
    if username and username.lower() in password.lower():
        patterns.append("Contains username")
    
    # Check if password contains email parts
    if email:
        email_parts = email.split('@')[0].lower()
        if email_parts in password.lower():
            patterns.append("Contains email parts")
    
    return patterns

def calculate_password_strength(password: str, username: Optional[str] = None, email: Optional[str] = None) -> tuple:
    """Calculate password strength"""
    score = 0
    feedback = []
    suggestions = []
    
    # Length check
    length = len(password)
    if length >= 8:
        score += 20
    else:
        feedback.append("Password is too short")
        suggestions.append("Use at least 8 characters")
    
    if length >= 12:
        score += 10
    if length >= 16:
        score += 10
    
    # Character variety
    if any(c.islower() for c in password):
        score += 10
    else:
        feedback.append("No lowercase letters")
        suggestions.append("Add lowercase letters")
    
    if any(c.isupper() for c in password):
        score += 10
    else:
        feedback.append("No uppercase letters")
        suggestions.append("Add uppercase letters")
    
    if any(c.isdigit() for c in password):
        score += 10
    else:
        feedback.append("No numbers")
        suggestions.append("Add numbers")
    
    if any(c in string.punctuation for c in password):
        score += 15
    else:
        feedback.append("No special characters")
        suggestions.append("Add special characters")
    
    # Pattern checks
    patterns = check_password_patterns(password, username, email)
    if patterns:
        feedback.extend(patterns)
        score -= 10
    
    # Common password check
    if check_common_passwords(password):
        feedback.append("Password is too common")
        suggestions.append("Choose a more unique password")
        score -= 30
    
    # Entropy bonus
    entropy = calculate_entropy(password)
    if entropy >= 50:
        score += 15
    elif entropy >= 30:
        score += 10
    elif entropy >= 20:
        score += 5
    
    # Determine strength
    if score >= 80:
        strength = PasswordStrength.VERY_STRONG
    elif score >= 65:
        strength = PasswordStrength.STRONG
    elif score >= 50:
        strength = PasswordStrength.GOOD
    elif score >= 35:
        strength = PasswordStrength.FAIR
    elif score >= 20:
        strength = PasswordStrength.WEAK
    else:
        strength = PasswordStrength.VERY_WEAK
    
    return strength, score, feedback, suggestions, entropy

def analyze_text(text: str) -> Dict[str, Any]:
    """Analyze text statistics"""
    lines = text.splitlines()
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    words = text.split()
    characters = list(text)
    unique_words = set(word.lower().strip(string.punctuation) for word in words)
    
    # Simple language detection (very basic)
    language = "unknown"
    if text.strip():
        # Check for common English words
        english_words = {"the", "and", "is", "in", "to", "of", "a", "that", "it", "with", "for", "as", "on", "be", "at", "by", "this", "have", "from", "or"}
        text_lower = text.lower()
        english_matches = sum(1 for word in english_words if word in text_lower)
        
        if english_matches >= 3:
            language = "english"
        # Add more language detection as needed
    
    # Simple readability score (simplified Flesch Reading Ease)
    if len(words) > 0 and len(sentences := text.split('. ')) > 0:
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables = sum(_count_syllables(word) for word in words) / len(words)
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        readability_score = max(0, min(100, readability_score))
    else:
        readability_score = None
    
    return {
        "text_length": len(text),
        "word_count": len(words),
        "character_count": len(characters),
        "line_count": len(lines),
        "paragraph_count": len(paragraphs),
        "unique_words": len(unique_words),
        "readability_score": readability_score,
        "language": language
    }

def _count_syllables(word: str) -> int:
    """Count syllables in a word (simplified)"""
    word = word.lower().strip(string.punctuation)
    if not word:
        return 0
    
    vowels = "aeiouy"
    syllable_count = 0
    prev_char_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_was_vowel:
            syllable_count += 1
        prev_char_was_vowel = is_vowel
    
    # Adjust for silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to DevTools API - Ultimate Developer Helper",
        "version": "1.0.0",
        "available_tools": [
            "Base64 Encode/Decode",
            "Hash Generator",
            "Password Strength Checker",
            "UUID Generator",
            "Text Analyzer"
        ]
    }

# Base64 Tools
@app.post("/base64/encode", response_model=Base64Response)
async def base64_encode(request: Base64Request):
    """Encode text to Base64"""
    try:
        encoded_bytes = base64.b64encode(request.text.encode(request.encoding))
        encoded_text = encoded_bytes.decode('ascii')
        
        return Base64Response(
            input_text=request.text,
            output_text=encoded_text,
            operation="encode",
            encoding=request.encoding,
            timestamp=datetime.utcnow()
        )
    except UnicodeEncodeError as e:
        raise HTTPException(status_code=400, detail=f"Encoding error: {str(e)}")
    except Exception as e:
        logger.error(f"Base64 encode error: {e}")
        raise HTTPException(status_code=500, detail="Encoding failed")

@app.post("/base64/decode", response_model=Base64Response)
async def base64_decode(request: Base64Request):
    """Decode Base64 to text"""
    try:
        decoded_bytes = base64.b64decode(request.text.encode('ascii'))
        decoded_text = decoded_bytes.decode(request.encoding)
        
        return Base64Response(
            input_text=request.text,
            output_text=decoded_text,
            operation="decode",
            encoding=request.encoding,
            timestamp=datetime.utcnow()
        )
    except binascii.Error as e:
        raise HTTPException(status_code=400, detail=f"Invalid Base64: {str(e)}")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Decoding error: {str(e)}")
    except Exception as e:
        logger.error(f"Base64 decode error: {e}")
        raise HTTPException(status_code=500, detail="Decoding failed")

@app.post("/base64/url-encode")
async def url_encode(text: str = Body(..., embed=True)):
    """URL encode text"""
    try:
        encoded = quote(text, safe='')
        return {
            "input_text": text,
            "output_text": encoded,
            "operation": "url_encode",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"URL encode error: {e}")
        raise HTTPException(status_code=500, detail="URL encoding failed")

@app.post("/base64/url-decode")
async def url_decode(text: str = Body(..., embed=True)):
    """URL decode text"""
    try:
        decoded = unquote(text)
        return {
            "input_text": text,
            "output_text": decoded,
            "operation": "url_decode",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"URL decode error: {e}")
        raise HTTPException(status_code=500, detail="URL decoding failed")

# Hash Tools
@app.post("/hash/generate", response_model=HashResponse)
async def generate_hash(request: HashRequest):
    """Generate hash of text"""
    try:
        text_bytes = request.text.encode(request.encoding)
        
        if request.algorithm == HashAlgorithm.MD5:
            hash_obj = hashlib.md5(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA1:
            hash_obj = hashlib.sha1(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA224:
            hash_obj = hashlib.sha224(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA256:
            hash_obj = hashlib.sha256(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA384:
            hash_obj = hashlib.sha384(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA512:
            hash_obj = hashlib.sha512(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA3_224:
            hash_obj = hashlib.sha3_224(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA3_256:
            hash_obj = hashlib.sha3_256(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA3_384:
            hash_obj = hashlib.sha3_384(text_bytes)
        elif request.algorithm == HashAlgorithm.SHA3_512:
            hash_obj = hashlib.sha3_512(text_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported hash algorithm")
        
        hash_bytes = hash_obj.digest()
        
        if request.output_format == "base64":
            hash_value = base64.b64encode(hash_bytes).decode('ascii')
        else:  # hex
            hash_value = hash_bytes.hex()
        
        return HashResponse(
            input_text=request.text,
            algorithm=request.algorithm.value,
            hash_value=hash_value,
            output_format=request.output_format,
            encoding=request.encoding,
            timestamp=datetime.utcnow()
        )
    except UnicodeEncodeError as e:
        raise HTTPException(status_code=400, detail=f"Encoding error: {str(e)}")
    except Exception as e:
        logger.error(f"Hash generation error: {e}")
        raise HTTPException(status_code=500, detail="Hash generation failed")

@app.post("/hash/bulk", response_model=BulkHashResponse)
async def bulk_generate_hash(request: BulkHashRequest):
    """Generate hash for multiple texts"""
    try:
        results = []
        
        for text in request.texts:
            text_bytes = text.encode(request.encoding)
            
            if request.algorithm == HashAlgorithm.MD5:
                hash_obj = hashlib.md5(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA1:
                hash_obj = hashlib.sha1(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA224:
                hash_obj = hashlib.sha224(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA256:
                hash_obj = hashlib.sha256(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA384:
                hash_obj = hashlib.sha384(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA512:
                hash_obj = hashlib.sha512(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA3_224:
                hash_obj = hashlib.sha3_224(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA3_256:
                hash_obj = hashlib.sha3_256(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA3_384:
                hash_obj = hashlib.sha3_384(text_bytes)
            elif request.algorithm == HashAlgorithm.SHA3_512:
                hash_obj = hashlib.sha3_512(text_bytes)
            else:
                raise HTTPException(status_code=400, detail="Unsupported hash algorithm")
            
            hash_bytes = hash_obj.digest()
            
            if request.output_format == "base64":
                hash_value = base64.b64encode(hash_bytes).decode('ascii')
            else:  # hex
                hash_value = hash_bytes.hex()
            
            results.append({
                "input_text": text,
                "hash_value": hash_value
            })
        
        return BulkHashResponse(
            results=results,
            algorithm=request.algorithm.value,
            count=len(results),
            timestamp=datetime.utcnow()
        )
    except UnicodeEncodeError as e:
        raise HTTPException(status_code=400, detail=f"Encoding error: {str(e)}")
    except Exception as e:
        logger.error(f"Bulk hash generation error: {e}")
        raise HTTPException(status_code=500, detail="Bulk hash generation failed")

@app.get("/hash/compare")
async def compare_hashes(
    text1: str = Query(..., description="First text"),
    text2: str = Query(..., description="Second text"),
    algorithm: HashAlgorithm = Query(HashAlgorithm.SHA256, description="Hash algorithm")
):
    """Compare hashes of two texts"""
    try:
        hash1_request = HashRequest(text=text1, algorithm=algorithm)
        hash2_request = HashRequest(text=text2, algorithm=algorithm)
        
        hash1_response = await generate_hash(hash1_request)
        hash2_response = await generate_hash(hash2_request)
        
        return {
            "text1": text1,
            "text2": text2,
            "algorithm": algorithm.value,
            "hash1": hash1_response.hash_value,
            "hash2": hash2_response.hash_value,
            "match": hash1_response.hash_value == hash2_response.hash_value,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Hash comparison error: {e}")
        raise HTTPException(status_code=500, detail="Hash comparison failed")

# Password Tools
@app.post("/password/strength", response_model=PasswordStrengthResponse)
async def check_password_strength(request: PasswordStrengthRequest):
    """Check password strength"""
    try:
        strength, score, feedback, suggestions, entropy = calculate_password_strength(
            request.password, request.username, request.email
        )
        
        time_to_crack = estimate_crack_time(entropy)
        
        return PasswordStrengthResponse(
            password=request.password,
            strength=strength,
            score=score,
            length=len(request.password),
            feedback=feedback,
            suggestions=suggestions,
            time_to_crack=time_to_crack,
            entropy=entropy,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Password strength check error: {e}")
        raise HTTPException(status_code=500, detail="Password strength check failed")

@app.post("/password/generate")
async def generate_password(
    length: int = Query(16, ge=8, le=128, description="Password length"),
    include_uppercase: bool = Query(True, description="Include uppercase letters"),
    include_lowercase: bool = Query(True, description="Include lowercase letters"),
    include_numbers: bool = Query(True, description="Include numbers"),
    include_symbols: bool = Query(True, description="Include symbols"),
    exclude_similar: bool = Query(True, description="Exclude similar characters (0O, 1lI)"),
    count: int = Query(1, ge=1, le=10, description="Number of passwords to generate")
):
    """Generate secure passwords"""
    try:
        passwords = []
        
        charset = ""
        if include_lowercase:
            charset += string.ascii_lowercase
        if include_uppercase:
            charset += string.ascii_uppercase
        if include_numbers:
            charset += string.digits
        if include_symbols:
            charset += string.punctuation
        
        if exclude_similar:
            similar_chars = "0O1lI"
            charset = ''.join(c for c in charset if c not in similar_chars)
        
        if not charset:
            raise HTTPException(status_code=400, detail="At least one character type must be selected")
        
        for _ in range(count):
            password = ''.join(secrets.choice(charset) for _ in range(length))
            passwords.append(password)
        
        return {
            "passwords": passwords,
            "length": length,
            "character_set": charset,
            "count": len(passwords),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Password generation error: {e}")
        raise HTTPException(status_code=500, detail="Password generation failed")

@app.post("/password/entropy")
async def calculate_password_entropy(password: str = Body(..., embed=True)):
    """Calculate password entropy"""
    try:
        entropy = calculate_entropy(password)
        crack_time = estimate_crack_time(entropy)
        
        return {
            "password": password,
            "entropy": entropy,
            "time_to_crack": crack_time,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Entropy calculation error: {e}")
        raise HTTPException(status_code=500, detail="Entropy calculation failed")

# UUID Tools
@app.post("/uuid/generate", response_model=UUIDResponse)
async def generate_uuid(request: UUIDRequest):
    """Generate UUIDs"""
    try:
        uuids = []
        
        for _ in range(request.count):
            if request.version == UUIDVersion.V1:
                generated_uuid = str(uuid.uuid1())
            elif request.version == UUIDVersion.V3:
                if not request.namespace or not request.name:
                    raise HTTPException(status_code=400, detail="Namespace and name required for UUID v3")
                generated_uuid = str(uuid.uuid3(uuid.UUID(request.namespace), request.name))
            elif request.version == UUIDVersion.V4:
                generated_uuid = str(uuid.uuid4())
            elif request.version == UUIDVersion.V5:
                if not request.namespace or not request.name:
                    raise HTTPException(status_code=400, detail="Namespace and name required for UUID v5")
                generated_uuid = str(uuid.uuid5(uuid.UUID(request.namespace), request.name))
            else:
                raise HTTPException(status_code=400, detail="Unsupported UUID version")
            
            uuids.append(generated_uuid)
        
        return UUIDResponse(
            uuids=uuids,
            version=request.version.value,
            count=len(uuids),
            timestamp=datetime.utcnow()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID namespace: {str(e)}")
    except Exception as e:
        logger.error(f"UUID generation error: {e}")
        raise HTTPException(status_code=500, detail="UUID generation failed")

@app.get("/uuid/parse")
async def parse_uuid(uuid_string: str = Query(..., description="UUID string to parse")):
    """Parse UUID and get information"""
    try:
        parsed_uuid = uuid.UUID(uuid_string)
        
        return {
            "uuid": str(parsed_uuid),
            "version": parsed_uuid.version,
            "variant": parsed_uuid.variant,
            "hex": parsed_uuid.hex,
            "int": parsed_uuid.int,
            "urn": parsed_uuid.urn,
            "bytes": parsed_uuid.bytes.hex(),
            "timestamp": datetime.utcnow()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {str(e)}")
    except Exception as e:
        logger.error(f"UUID parsing error: {e}")
        raise HTTPException(status_code=500, detail="UUID parsing failed")

@app.get("/uuid/validate")
async def validate_uuid(uuid_string: str = Query(..., description="UUID string to validate")):
    """Validate UUID format"""
    try:
        parsed_uuid = uuid.UUID(uuid_string)
        return {
            "uuid": uuid_string,
            "is_valid": True,
            "version": parsed_uuid.version,
            "timestamp": datetime.utcnow()
        }
    except ValueError:
        return {
            "uuid": uuid_string,
            "is_valid": False,
            "error": "Invalid UUID format",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"UUID validation error: {e}")
        raise HTTPException(status_code=500, detail="UUID validation failed")

# Text Analysis Tools
@app.post("/text/analyze", response_model=TextAnalyzerResponse)
async def analyze_text_endpoint(request: TextAnalyzerRequest):
    """Analyze text statistics"""
    try:
        analysis = analyze_text(request.text)
        
        return TextAnalyzerResponse(
            text_length=analysis["text_length"],
            word_count=analysis["word_count"],
            character_count=analysis["character_count"],
            line_count=analysis["line_count"],
            paragraph_count=analysis["paragraph_count"],
            unique_words=analysis["unique_words"],
            readability_score=analysis["readability_score"],
            language=analysis["language"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        raise HTTPException(status_code=500, detail="Text analysis failed")

@app.post("/text/extract")
async def extract_info(text: str = Body(..., embed=True)):
    """Extract information from text"""
    try:
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        # Extract phone numbers (simple pattern)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', text)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', text)
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "emails": emails,
            "urls": urls,
            "phone_numbers": phones,
            "numbers": numbers,
            "hashtags": hashtags,
            "mentions": mentions,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        raise HTTPException(status_code=500, detail="Text extraction failed")

# Utility Endpoints
@app.get("/tools/info")
async def get_tools_info():
    """Get information about available tools"""
    return {
        "tools": [
            {
                "name": "Base64",
                "description": "Encode and decode Base64 text",
                "endpoints": [
                    {"path": "/base64/encode", "method": "POST", "description": "Encode text to Base64"},
                    {"path": "/base64/decode", "method": "POST", "description": "Decode Base64 to text"},
                    {"path": "/base64/url-encode", "method": "POST", "description": "URL encode text"},
                    {"path": "/base64/url-decode", "method": "POST", "description": "URL decode text"}
                ]
            },
            {
                "name": "Hash Generator",
                "description": "Generate various hash types",
                "algorithms": ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_224", "sha3_256", "sha3_384", "sha3_512"],
                "endpoints": [
                    {"path": "/hash/generate", "method": "POST", "description": "Generate hash"},
                    {"path": "/hash/bulk", "method": "POST", "description": "Bulk hash generation"},
                    {"path": "/hash/compare", "method": "GET", "description": "Compare hashes"}
                ]
            },
            {
                "name": "Password Tools",
                "description": "Password strength checking and generation",
                "endpoints": [
                    {"path": "/password/strength", "method": "POST", "description": "Check password strength"},
                    {"path": "/password/generate", "method": "POST", "description": "Generate secure passwords"},
                    {"path": "/password/entropy", "method": "POST", "description": "Calculate password entropy"}
                ]
            },
            {
                "name": "UUID Generator",
                "description": "Generate and parse UUIDs",
                "versions": ["1", "3", "4", "5"],
                "endpoints": [
                    {"path": "/uuid/generate", "method": "POST", "description": "Generate UUIDs"},
                    {"path": "/uuid/parse", "method": "GET", "description": "Parse UUID"},
                    {"path": "/uuid/validate", "method": "GET", "description": "Validate UUID"}
                ]
            },
            {
                "name": "Text Analyzer",
                "description": "Analyze text statistics and extract information",
                "endpoints": [
                    {"path": "/text/analyze", "method": "POST", "description": "Analyze text"},
                    {"path": "/text/extract", "method": "POST", "description": "Extract information"}
                ]
            }
        ],
        "timestamp": datetime.utcnow()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "tools_count": 5,
        "endpoints_count": 15
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
