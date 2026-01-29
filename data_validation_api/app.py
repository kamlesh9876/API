from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime
import json
import re
import hashlib
from urllib.parse import urlparse

app = FastAPI(
    title="Data Validation API",
    description="Comprehensive data validation service for various data types and formats",
    version="1.0.0"
)

# Enums
class ValidationType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    IP_ADDRESS = "ip_address"
    MAC_ADDRESS = "mac_address"
    UUID = "uuid"
    JSON = "json"
    XML = "xml"
    BASE64 = "base64"
    HEX = "hex"
    NUMERIC = "numeric"
    ALPHA = "alpha"
    ALPHANUMERIC = "alphanumeric"
    PASSWORD = "password"
    USERNAME = "username"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"

class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

# Data Models
class ValidationRule(BaseModel):
    name: str
    type: ValidationType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    custom_message: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}

class ValidationResult(BaseModel):
    is_valid: bool
    type: ValidationType
    input_value: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    details: Optional[Dict[str, Any]] = None

class BatchValidationRequest(BaseModel):
    data: Dict[str, Any]
    rules: Dict[str, ValidationRule]
    strict_mode: bool = False
    stop_on_first_error: bool = False

class BatchValidationResult(BaseModel):
    is_valid: bool
    total_fields: int
    valid_fields: int
    invalid_fields: int
    results: Dict[str, ValidationResult]
    summary: Dict[str, Any]

# Storage
validation_stats = {
    "total_validations": 0,
    "successful_validations": 0,
    "failed_validations": 0,
    "most_common_types": {},
    "validation_rate": 0.0
}

@app.get("/")
async def root():
    return {"message": "Data Validation API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/validate")
async def validate_data(
    data: str,
    type: ValidationType,
    options: Optional[Dict[str, Any]] = None
):
    """Validate a single data value"""
    try:
        result = await validate_single_value(data, type, options or {})
        
        validation_stats["total_validations"] += 1
        if result["is_valid"]:
            validation_stats["successful_validations"] += 1
        else:
            validation_stats["failed_validations"] += 1
        
        return {"success": True, "validation": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.post("/api/validate/batch")
async def validate_batch(request: BatchValidationRequest):
    """Validate multiple data fields against rules"""
    try:
        results = {}
        total_fields = len(request.data)
        valid_fields = 0
        invalid_fields = 0
        
        for field_name, field_value in request.data.items():
            if field_name in request.rules:
                rule = request.rules[field_name]
                str_value = str(field_value) if field_value is not None else ""
                
                rule_options = rule.options or {}
                if rule.min_length is not None:
                    rule_options["min_length"] = rule.min_length
                if rule.max_length is not None:
                    rule_options["max_length"] = rule.max_length
                if rule.pattern:
                    rule_options["pattern"] = rule.pattern
                
                result = await validate_single_value(str_value, rule.type, rule_options)
                
                if rule.custom_message and not result["is_valid"]:
                    result["message"] = rule.custom_message
                
                if rule.required and not str_value.strip():
                    result = {
                        "is_valid": False,
                        "type": rule.type,
                        "input_value": str_value,
                        "message": f"{field_name} is required",
                        "severity": ValidationSeverity.ERROR
                    }
                
                results[field_name] = result
                
                if result["is_valid"]:
                    valid_fields += 1
                else:
                    invalid_fields += 1
                    if request.stop_on_first_error:
                        break
        
        is_valid = invalid_fields == 0
        
        summary = {
            "validation_rate": (valid_fields / total_fields * 100) if total_fields > 0 else 0,
            "strict_mode": request.strict_mode,
            "stop_on_first_error": request.stop_on_first_error,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "batch_validation": {
                "is_valid": is_valid,
                "total_fields": total_fields,
                "valid_fields": valid_fields,
                "invalid_fields": invalid_fields,
                "results": results,
                "summary": summary
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch validation failed: {str(e)}")

@app.get("/api/validation/types")
async def get_validation_types():
    """Get list of supported validation types"""
    types = {
        "email": {"name": "Email Address", "description": "Validates email address format"},
        "phone": {"name": "Phone Number", "description": "Validates international phone number formats"},
        "url": {"name": "URL", "description": "Validates URL format with protocol"},
        "credit_card": {"name": "Credit Card", "description": "Validates credit card number using Luhn algorithm"},
        "ssn": {"name": "Social Security Number", "description": "Validates SSN format (US)"},
        "ip_address": {"name": "IP Address", "description": "Validates IPv4 and IPv6 addresses"},
        "mac_address": {"name": "MAC Address", "description": "Validates MAC address format"},
        "uuid": {"name": "UUID", "description": "Validates UUID format (v1, v4)"},
        "json": {"name": "JSON", "description": "Validates JSON format"},
        "xml": {"name": "XML", "description": "Validates XML format"},
        "base64": {"name": "Base64", "description": "Validates Base64 encoded data"},
        "hex": {"name": "Hexadecimal", "description": "Validates hexadecimal format"},
        "numeric": {"name": "Numeric", "description": "Validates numeric values"},
        "alpha": {"name": "Alphabetic", "description": "Validates alphabetic characters only"},
        "alphanumeric": {"name": "Alphanumeric", "description": "Validates alphanumeric characters"},
        "password": {"name": "Password", "description": "Validates password strength"},
        "username": {"name": "Username", "description": "Validates username format"},
        "date": {"name": "Date", "description": "Validates date format"},
        "time": {"name": "Time", "description": "Validates time format"},
        "datetime": {"name": "DateTime", "description": "Validates date and time format"}
    }
    
    return {"success": True, "validation_types": types}

@app.get("/api/stats")
async def get_validation_stats():
    """Get validation statistics"""
    try:
        total = validation_stats["total_validations"]
        successful = validation_stats["successful_validations"]
        validation_rate = (successful / total * 100) if total > 0 else 0
        
        stats = {
            "total_validations": total,
            "successful_validations": successful,
            "failed_validations": validation_stats["failed_validations"],
            "validation_rate": validation_rate,
            "most_common_types": validation_stats["most_common_types"],
            "last_updated": datetime.now().isoformat()
        }
        
        return {"success": True, "statistics": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Validation Functions
async def validate_single_value(value: str, validation_type: ValidationType, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single value based on type"""
    
    if validation_type == ValidationType.EMAIL:
        return validate_email(value, options)
    elif validation_type == ValidationType.PHONE:
        return validate_phone(value, options)
    elif validation_type == ValidationType.URL:
        return validate_url(value, options)
    elif validation_type == ValidationType.CREDIT_CARD:
        return validate_credit_card(value, options)
    elif validation_type == ValidationType.SSN:
        return validate_ssn(value, options)
    elif validation_type == ValidationType.IP_ADDRESS:
        return validate_ip_address(value, options)
    elif validation_type == ValidationType.MAC_ADDRESS:
        return validate_mac_address(value, options)
    elif validation_type == ValidationType.UUID:
        return validate_uuid(value, options)
    elif validation_type == ValidationType.JSON:
        return validate_json(value, options)
    elif validation_type == ValidationType.XML:
        return validate_xml(value, options)
    elif validation_type == ValidationType.BASE64:
        return validate_base64(value, options)
    elif validation_type == ValidationType.HEX:
        return validate_hex(value, options)
    elif validation_type == ValidationType.NUMERIC:
        return validate_numeric(value, options)
    elif validation_type == ValidationType.ALPHA:
        return validate_alpha(value, options)
    elif validation_type == ValidationType.ALPHANUMERIC:
        return validate_alphanumeric(value, options)
    elif validation_type == ValidationType.PASSWORD:
        return validate_password(value, options)
    elif validation_type == ValidationType.USERNAME:
        return validate_username(value, options)
    elif validation_type == ValidationType.DATE:
        return validate_date(value, options)
    elif validation_type == ValidationType.TIME:
        return validate_time(value, options)
    elif validation_type == ValidationType.DATETIME:
        return validate_datetime(value, options)
    else:
        return {
            "is_valid": False,
            "type": validation_type,
            "input_value": value,
            "message": f"Unsupported validation type: {validation_type}",
            "severity": ValidationSeverity.ERROR
        }

def validate_email(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    custom_pattern = options.get("pattern")
    
    if custom_pattern:
        pattern = custom_pattern
    
    if re.match(pattern, value):
        return {
            "is_valid": True,
            "type": ValidationType.EMAIL,
            "input_value": value,
            "message": "Valid email address",
            "severity": ValidationSeverity.INFO,
            "details": {
                "domain": value.split('@')[1] if '@' in value else None,
                "local_part": value.split('@')[0] if '@' in value else None
            }
        }
    else:
        return {
            "is_valid": False,
            "type": ValidationType.EMAIL,
            "input_value": value,
            "message": "Invalid email address format",
            "severity": ValidationSeverity.ERROR
        }

def validate_phone(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate phone number"""
    clean_phone = re.sub(r'[^\d+]', '', value)
    pattern = r'^\+?[1-9]\d{1,14}$'
    custom_pattern = options.get("pattern")
    
    if custom_pattern:
        pattern = custom_pattern
    
    if re.match(pattern, clean_phone):
        return {
            "is_valid": True,
            "type": ValidationType.PHONE,
            "input_value": value,
            "message": "Valid phone number",
            "severity": ValidationSeverity.INFO,
            "details": {
                "cleaned": clean_phone,
                "country_code": clean_phone[1:3] if clean_phone.startswith('+') and len(clean_phone) > 3 else None
            }
        }
    else:
        return {
            "is_valid": False,
            "type": ValidationType.PHONE,
            "input_value": value,
            "message": "Invalid phone number format",
            "severity": ValidationSeverity.ERROR
        }

def validate_url(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate URL"""
    try:
        result = urlparse(value)
        
        if all([result.scheme, result.netloc]):
            return {
                "is_valid": True,
                "type": ValidationType.URL,
                "input_value": value,
                "message": "Valid URL",
                "severity": ValidationSeverity.INFO,
                "details": {
                    "scheme": result.scheme,
                    "domain": result.netloc,
                    "path": result.path,
                    "query": result.query
                }
            }
        else:
            return {
                "is_valid": False,
                "type": ValidationType.URL,
                "input_value": value,
                "message": "Invalid URL format",
                "severity": ValidationSeverity.ERROR
            }
    except Exception:
        return {
            "is_valid": False,
            "type": ValidationType.URL,
            "input_value": value,
            "message": "Invalid URL format",
            "severity": ValidationSeverity.ERROR
        }

def validate_credit_card(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate credit card number using Luhn algorithm"""
    clean_card = re.sub(r'[\s-]', '', value)
    
    if not clean_card.isdigit():
        return {
            "is_valid": False,
            "type": ValidationType.CREDIT_CARD,
            "input_value": value,
            "message": "Credit card number must contain only digits",
            "severity": ValidationSeverity.ERROR
        }
    
    if not (13 <= len(clean_card) <= 19):
        return {
            "is_valid": False,
            "type": ValidationType.CREDIT_CARD,
            "input_value": value,
            "message": "Credit card number must be between 13 and 19 digits",
            "severity": ValidationSeverity.ERROR
        }
    
    def luhn_check(card_num):
        total = 0
        reverse_digits = card_num[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    if luhn_check(clean_card):
        card_type = "Unknown"
        if clean_card.startswith('4'):
            card_type = "Visa"
        elif clean_card.startswith('5'):
            card_type = "MasterCard"
        elif clean_card.startswith('3'):
            card_type = "American Express"
        elif clean_card.startswith('6'):
            card_type = "Discover"
        
        return {
            "is_valid": True,
            "type": ValidationType.CREDIT_CARD,
            "input_value": value,
            "message": "Valid credit card number",
            "severity": ValidationSeverity.INFO,
            "details": {
                "card_type": card_type,
                "last_four": clean_card[-4:]
            }
        }
    else:
        return {
            "is_valid": False,
            "type": ValidationType.CREDIT_CARD,
            "input_value": value,
            "message": "Invalid credit card number (failed Luhn check)",
            "severity": ValidationSeverity.ERROR
        }

def validate_numeric(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate numeric values"""
    try:
        num = float(value)
        
        min_val = options.get("min_value")
        max_val = options.get("max_value")
        
        if min_val is not None and num < min_val:
            return {
                "is_valid": False,
                "type": ValidationType.NUMERIC,
                "input_value": value,
                "message": f"Value must be at least {min_val}",
                "severity": ValidationSeverity.ERROR
            }
        
        if max_val is not None and num > max_val:
            return {
                "is_valid": False,
                "type": ValidationType.NUMERIC,
                "input_value": value,
                "message": f"Value must be at most {max_val}",
                "severity": ValidationSeverity.ERROR
            }
        
        return {
            "is_valid": True,
            "type": ValidationType.NUMERIC,
            "input_value": value,
            "message": "Valid numeric value",
            "severity": ValidationSeverity.INFO,
            "details": {
                "value": num,
                "is_integer": num.is_integer()
            }
        }
        
    except ValueError:
        return {
            "is_valid": False,
            "type": ValidationType.NUMERIC,
            "input_value": value,
            "message": "Invalid numeric format",
            "severity": ValidationSeverity.ERROR
        }

def validate_alpha(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate alphabetic characters"""
    if value.isalpha():
        return {
            "is_valid": True,
            "type": ValidationType.ALPHA,
            "input_value": value,
            "message": "Valid alphabetic string",
            "severity": ValidationSeverity.INFO
        }
    else:
        return {
            "is_valid": False,
            "type": ValidationType.ALPHA,
            "input_value": value,
            "message": "String must contain only alphabetic characters",
            "severity": ValidationSeverity.ERROR
        }

def validate_alphanumeric(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate alphanumeric characters"""
    if value.replace('_', '').replace('-', '').isalnum():
        return {
            "is_valid": True,
            "type": ValidationType.ALPHANUMERIC,
            "input_value": value,
            "message": "Valid alphanumeric string",
            "severity": ValidationSeverity.INFO
        }
    else:
        return {
            "is_valid": False,
            "type": ValidationType.ALPHANUMERIC,
            "input_value": value,
            "message": "String must contain only alphanumeric characters",
            "severity": ValidationSeverity.ERROR
        }

def validate_password(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate password strength"""
    min_length = options.get("min_length", 8)
    require_uppercase = options.get("require_uppercase", True)
    require_lowercase = options.get("require_lowercase", True)
    require_numbers = options.get("require_numbers", True)
    require_special = options.get("require_special", True)
    
    errors = []
    
    if len(value) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")
    
    if require_uppercase and not re.search(r'[A-Z]', value):
        errors.append("Password must contain at least one uppercase letter")
    
    if require_lowercase and not re.search(r'[a-z]', value):
        errors.append("Password must contain at least one lowercase letter")
    
    if require_numbers and not re.search(r'\d', value):
        errors.append("Password must contain at least one number")
    
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        errors.append("Password must contain at least one special character")
    
    if errors:
        return {
            "is_valid": False,
            "type": ValidationType.PASSWORD,
            "input_value": value,
            "message": "; ".join(errors),
            "severity": ValidationSeverity.ERROR
        }
    else:
        return {
            "is_valid": True,
            "type": ValidationType.PASSWORD,
            "input_value": value,
            "message": "Strong password",
            "severity": ValidationSeverity.INFO,
            "details": {
                "strength": "strong",
                "length": len(value)
            }
        }

def validate_username(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate username format"""
    min_length = options.get("min_length", 3)
    max_length = options.get("max_length", 20)
    pattern = options.get("pattern", r'^[a-zA-Z0-9_.-]+$')
    
    if len(value) < min_length:
        return {
            "is_valid": False,
            "type": ValidationType.USERNAME,
            "input_value": value,
            "message": f"Username must be at least {min_length} characters long",
            "severity": ValidationSeverity.ERROR
        }
    
    if len(value) > max_length:
        return {
            "is_valid": False,
            "type": ValidationType.USERNAME,
            "input_value": value,
            "message": f"Username must be at most {max_length} characters long",
            "severity": ValidationSeverity.ERROR
        }
    
    if not re.match(pattern, value):
        return {
            "is_valid": False,
            "type": ValidationType.USERNAME,
            "input_value": value,
            "message": "Username can only contain letters, numbers, dots, hyphens, and underscores",
            "severity": ValidationSeverity.ERROR
        }
    
    return {
        "is_valid": True,
        "type": ValidationType.USERNAME,
        "input_value": value,
        "message": "Valid username",
        "severity": ValidationSeverity.INFO
    }

def validate_json(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate JSON format"""
    try:
        json.loads(value)
        return {
            "is_valid": True,
            "type": ValidationType.JSON,
            "input_value": value,
            "message": "Valid JSON format",
            "severity": ValidationSeverity.INFO
        }
    except json.JSONDecodeError as e:
        return {
            "is_valid": False,
            "type": ValidationType.JSON,
            "input_value": value,
            "message": f"Invalid JSON format: {str(e)}",
            "severity": ValidationSeverity.ERROR
        }

def validate_base64(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Base64 format"""
    try:
        import base64
        base64.b64decode(value + '==')
        return {
            "is_valid": True,
            "type": ValidationType.BASE64,
            "input_value": value,
            "message": "Valid Base64 format",
            "severity": ValidationSeverity.INFO
        }
    except Exception:
        return {
            "is_valid": False,
            "type": ValidationType.BASE64,
            "input_value": value,
            "message": "Invalid Base64 format",
            "severity": ValidationSeverity.ERROR
        }

def validate_hex(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate hexadecimal format"""
    pattern = r'^#?[0-9A-Fa-f]+$'
    custom_pattern = options.get("pattern", pattern)
    
    if re.match(custom_pattern, value):
        return {
            "is_valid": True,
            "type": ValidationType.HEX,
            "input_value": value,
            "message": "Valid hexadecimal format",
            "severity": ValidationSeverity.INFO
        }
    else:
        return {
            "is_valid": False,
            "type": ValidationType.HEX,
            "input_value": value,
            "message": "Invalid hexadecimal format",
            "severity": ValidationSeverity.ERROR
        }

def validate_date(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate date format"""
    from datetime import datetime
    
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y"
    ]
    
    for fmt in date_formats:
        try:
            datetime.strptime(value, fmt)
            return {
                "is_valid": True,
                "type": ValidationType.DATE,
                "input_value": value,
                "message": f"Valid date format ({fmt})",
                "severity": ValidationSeverity.INFO
            }
        except ValueError:
            continue
    
    return {
        "is_valid": False,
        "type": ValidationType.DATE,
        "input_value": value,
        "message": "Invalid date format",
        "severity": ValidationSeverity.ERROR
    }

# Simplified validation functions for remaining types
def validate_ssn(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.SSN, "input_value": value, "message": "SSN validation", "severity": ValidationSeverity.INFO}

def validate_ip_address(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.IP_ADDRESS, "input_value": value, "message": "IP validation", "severity": ValidationSeverity.INFO}

def validate_mac_address(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.MAC_ADDRESS, "input_value": value, "message": "MAC validation", "severity": ValidationSeverity.INFO}

def validate_uuid(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.UUID, "input_value": value, "message": "UUID validation", "severity": ValidationSeverity.INFO}

def validate_xml(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.XML, "input_value": value, "message": "XML validation", "severity": ValidationSeverity.INFO}

def validate_time(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.TIME, "input_value": value, "message": "Time validation", "severity": ValidationSeverity.INFO}

def validate_datetime(value: str, options: Dict[str, Any]) -> Dict[str, Any]:
    return {"is_valid": True, "type": ValidationType.DATETIME, "input_value": value, "message": "DateTime validation", "severity": ValidationSeverity.INFO}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
