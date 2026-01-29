# Data Validation API

A comprehensive data validation service providing validation for various data types and formats. Built with FastAPI, this service offers single and batch validation, file validation, schema validation, and extensive customization options.

## 🚀 Features

### Validation Types
- **Email**: Validate email address formats with domain checking
- **Phone**: Validate international phone number formats
- **URL**: Validate URL formats with protocol and domain validation
- **Credit Card**: Validate credit card numbers using Luhn algorithm
- **SSN**: Validate Social Security Number formats
- **IP Address**: Validate IPv4 and IPv6 addresses
- **MAC Address**: Validate MAC address formats
- **UUID**: Validate UUID formats (v1, v4)
- **JSON**: Validate JSON format and structure
- **XML**: Validate XML format
- **Base64**: Validate Base64 encoded data
- **Hexadecimal**: Validate hexadecimal formats
- **Numeric**: Validate numeric values with range checking
- **Alphabetic**: Validate alphabetic characters only
- **Alphanumeric**: Validate alphanumeric characters
- **Password**: Validate password strength requirements
- **Username**: Validate username formats
- **Date**: Validate various date formats
- **Time**: Validate time formats
- **DateTime**: Validate date and time formats

### Advanced Features
- **Batch Validation**: Validate multiple fields simultaneously
- **File Validation**: Validate uploaded file contents
- **Schema Validation**: Validate data against JSON schemas
- **Custom Rules**: Create custom validation rules
- **Error Messages**: Customizable error messages
- **Severity Levels**: Error, warning, and info severity levels
- **Validation Statistics**: Track validation performance

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Data Validation**: Pydantic models with custom validators
- **Regex Patterns**: Comprehensive regex validation
- **File Handling**: UploadFile support for file validation
- **Async Support**: Full async/await implementation

## 📋 API Endpoints

### Single Validation

#### Validate Single Data
```http
POST /api/validate?data=user@example.com&type=email
```

```http
POST /api/validate
Content-Type: application/json

{
  "data": "user@example.com",
  "type": "email",
  "options": {
    "pattern": "custom_pattern",
    "allow_subdomains": true
  }
}
```

### Batch Validation

#### Validate Multiple Fields
```http
POST /api/validate/batch
Content-Type: application/json

{
  "data": {
    "email": "user@example.com",
    "phone": "+1-555-123-4567",
    "password": "SecurePass123!",
    "age": 25
  },
  "rules": {
    "email": {
      "name": "email",
      "type": "email",
      "required": true,
      "custom_message": "Please enter a valid email address"
    },
    "phone": {
      "name": "phone",
      "type": "phone",
      "required": false
    },
    "password": {
      "name": "password",
      "type": "password",
      "required": true,
      "options": {
        "min_length": 8,
        "require_uppercase": true,
        "require_numbers": true,
        "require_special": true
      }
    },
    "age": {
      "name": "age",
      "type": "numeric",
      "required": true,
      "options": {
        "min_value": 18,
        "max_value": 120
      }
    }
  },
  "strict_mode": false,
  "stop_on_first_error": false
}
```

### File Validation

#### Validate Uploaded File
```http
POST /api/validate/file
Content-Type: multipart/form-data

file: [JSON File]
file_type: json
validation_rules: {"name": {"type": "string", "required": true}}
max_file_size: 1048576
allowed_extensions: json,csv
scan_for_malware: false
```

### Schema Validation

#### Validate Against Schema
```http
POST /api/validate/schema
Content-Type: application/json

{
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  },
  "schema": {
    "type": "object",
    "required": ["name", "email"],
    "properties": {
      "name": {
        "type": "string",
        "minLength": 2,
        "maxLength": 50
      },
      "email": {
        "type": "string",
        "format": "email"
      },
      "age": {
        "type": "integer",
        "minimum": 0,
        "maximum": 150
      }
    }
  },
  "strict_mode": true
}
```

### Utility Endpoints

#### Get Validation Types
```http
GET /api/validation/types
```

#### Get Validation Statistics
```http
GET /api/stats
```

## 📊 Data Models

### ValidationRule
```python
class ValidationRule(BaseModel):
    name: str
    type: ValidationType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    custom_message: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}
```

### ValidationResult
```python
class ValidationResult(BaseModel):
    is_valid: bool
    type: ValidationType
    input_value: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    details: Optional[Dict[str, Any]] = None
```

### BatchValidationRequest
```python
class BatchValidationRequest(BaseModel):
    data: Dict[str, Any]
    rules: Dict[str, ValidationRule]
    strict_mode: bool = False
    stop_on_first_error: bool = False
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn pydantic python-multipart

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
MAX_VALIDATION_SIZE=10MB
BATCH_VALIDATION_LIMIT=100
FILE_VALIDATION_ENABLED=true
SCHEMA_VALIDATION_ENABLED=true
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json

# Single validation
response = requests.post(
    "http://localhost:8000/api/validate",
    params={
        "data": "user@example.com",
        "type": "email"
    }
)

validation_result = response.json()
print(f"Validation result: {validation_result['validation']}")

# Batch validation
batch_data = {
    "data": {
        "email": "user@example.com",
        "phone": "+1-555-123-4567",
        "password": "SecurePass123!",
        "age": 25
    },
    "rules": {
        "email": {
            "name": "email",
            "type": "email",
            "required": True
        },
        "password": {
            "name": "password",
            "type": "password",
            "required": True,
            "options": {
                "min_length": 8,
                "require_uppercase": True,
                "require_numbers": True,
                "require_special": True
            }
        },
        "age": {
            "name": "age",
            "type": "numeric",
            "required": True,
            "options": {
                "min_value": 18,
                "max_value": 120
            }
        }
    }
}

batch_response = requests.post(
    "http://localhost:8000/api/validate/batch",
    json=batch_data
)

batch_result = batch_response.json()
print(f"Batch validation: {batch_result['batch_validation']}")

# File validation
with open('data.json', 'rb') as f:
    files = {'file': f}
    data = {
        'file_type': 'json',
        'validation_rules': json.dumps({
            "name": {"type": "string", "required": True},
            "email": {"type": "email", "required": True}
        }),
        'max_file_size': 1048576
    }
    
    file_response = requests.post(
        "http://localhost:8000/api/validate/file",
        files=files,
        data=data
    )
    
    print(f"File validation: {file_response.json()}")

# Schema validation
schema_data = {
    "data": {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    },
    "schema": {
        "type": "object",
        "required": ["name", "email"],
        "properties": {
            "name": {"type": "string", "minLength": 2},
            "email": {"type": "string"},
            "age": {"type": "integer", "minimum": 0}
        }
    }
}

schema_response = requests.post(
    "http://localhost:8000/api/validate/schema",
    json=schema_data
)

print(f"Schema validation: {schema_response.json()}")
```

### JavaScript Client
```javascript
// Single validation
fetch('http://localhost:8000/api/validate?data=user@example.com&type=email')
.then(response => response.json())
.then(data => {
    console.log('Validation result:', data.validation);
})
.catch(error => console.error('Error:', error));

// Batch validation
const batchData = {
    data: {
        email: 'user@example.com',
        phone: '+1-555-123-4567',
        password: 'SecurePass123!',
        age: 25
    },
    rules: {
        email: {
            name: 'email',
            type: 'email',
            required: true
        },
        password: {
            name: 'password',
            type: 'password',
            required: true,
            options: {
                min_length: 8,
                require_uppercase: true,
                require_numbers: true,
                require_special: true
            }
        },
        age: {
            name: 'age',
            type: 'numeric',
            required: true,
            options: {
                min_value: 18,
                max_value: 120
            }
        }
    }
};

fetch('http://localhost:8000/api/validate/batch', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(batchData)
})
.then(response => response.json())
.then(data => {
    console.log('Batch validation:', data.batch_validation);
    
    // Display results
    Object.entries(data.batch_validation.results).forEach(([field, result]) => {
        console.log(`${field}: ${result.is_valid ? '✓' : '✗'} ${result.message}`);
    });
})
.catch(error => console.error('Error:', error));

// File validation
const formData = new FormData();
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

if (file) {
    formData.append('file', file);
    formData.append('file_type', 'json');
    formData.append('validation_rules', JSON.stringify({
        name: {type: "string", required: true},
        email: {type: "email", required: true}
    }));
    
    fetch('http://localhost:8000/api/validate/file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('File validation:', data.file_validation);
    })
    .catch(error => console.error('Error:', error));
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Validation Limits
MAX_VALIDATION_SIZE=10MB
BATCH_VALIDATION_LIMIT=100
MAX_RULES_PER_BATCH=50

# File Validation
FILE_VALIDATION_ENABLED=true
MAX_FILE_SIZE=50MB
ALLOWED_FILE_TYPES=json,xml,csv,txt
MALWARE_SCAN_ENABLED=false

# Schema Validation
SCHEMA_VALIDATION_ENABLED=true
MAX_SCHEMA_DEPTH=10
MAX_SCHEMA_PROPERTIES=100

# Performance
VALIDATION_TIMEOUT=30
CONCURRENT_VALIDATIONS=10
CACHE_VALIDATION_RESULTS=true
CACHE_TTL=300

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
RATE_LIMIT_PER_MINUTE=100
INPUT_SANITIZATION=true

# Logging
LOG_LEVEL=INFO
LOG_VALIDATION_ERRORS=true
AUDIT_LOG_ENABLED=true
```

### Validation Types and Options

#### Email Validation
- **pattern**: Custom regex pattern
- **allow_subdomains**: Allow subdomain emails
- **check_mx**: Check MX records (advanced)

#### Phone Validation
- **pattern**: Custom regex pattern
- **country_codes**: Allowed country codes
- **format**: Output format (E164, NATIONAL, INTERNATIONAL)

#### Password Validation
- **min_length**: Minimum password length
- **max_length**: Maximum password length
- **require_uppercase**: Require uppercase letters
- **require_lowercase**: Require lowercase letters
- **require_numbers**: Require numbers
- **require_special**: Require special characters
- **forbidden_patterns**: Forbidden password patterns

#### Numeric Validation
- **min_value**: Minimum allowed value
- **max_value**: Maximum allowed value
- **allow_decimal**: Allow decimal numbers
- **precision**: Decimal precision

#### Date Validation
- **formats**: Allowed date formats
- **min_date**: Minimum allowed date
- **max_date**: Maximum allowed date
- **timezone**: Timezone validation

## 📈 Use Cases

### Form Validation
- **User Registration**: Validate signup forms
- **Contact Forms**: Validate contact information
- **Survey Forms**: Validate survey responses
- **Application Forms**: Validate complex application data

### Data Processing
- **Data Import**: Validate imported data files
- **Data Migration**: Validate migrated data
- **Data Cleaning**: Identify invalid data
- **Data Quality**: Assess data quality metrics

### API Integration
- **Request Validation**: Validate API request data
- **Response Validation**: Validate API responses
- **Webhook Validation**: Validate webhook payloads
- **Integration Testing**: Validate integration data

### Security
- **Input Sanitization**: Validate user inputs
- **Data Leakage Prevention**: Validate sensitive data
- **Compliance**: Ensure data format compliance
- **Audit Trail**: Track validation attempts

## 🛡️ Security Features

### Input Security
- **Input Sanitization**: Clean and sanitize inputs
- **SQL Injection Prevention**: Validate database inputs
- **XSS Prevention**: Validate web inputs
- **File Upload Security**: Secure file validation

### Data Protection
- **Sensitive Data Handling**: Handle sensitive validation data
- **Audit Logging**: Track all validation attempts
- **Rate Limiting**: Prevent abuse
- **Access Control**: Control validation access

## 📊 Monitoring

### Validation Metrics
- **Validation Rate**: Success/failure rates
- **Common Errors**: Most frequent validation errors
- **Performance**: Validation processing times
- **Usage Statistics**: API usage metrics

### Quality Metrics
- **Data Quality Score**: Overall data quality assessment
- **Error Patterns**: Identify common error patterns
- **Validation Trends**: Track validation trends over time
- **Compliance Metrics**: Measure compliance rates

## 🔗 Related APIs

- **User Management API**: For user data validation
- **File Storage API**: For file validation and storage
- **Analytics API**: For validation analytics
- **Security API**: For security validation rules

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This API provides comprehensive validation capabilities. For production use, consider:
- **Performance Optimization**: Cache frequently used validation rules
- **Custom Validators**: Implement domain-specific validators
- **Integration**: Integrate with existing validation frameworks
- **Monitoring**: Set up comprehensive monitoring and alerting
