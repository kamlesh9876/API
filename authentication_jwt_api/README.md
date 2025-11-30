# Authentication & JWT API

A comprehensive authentication and authorization API built with FastAPI, providing secure user management with JWT tokens, OTP verification, and password reset functionality.

## 🚀 Features

- **User Registration**: Create new user accounts with email verification
- **Email Verification**: OTP-based email verification system
- **User Login**: Secure authentication with JWT tokens
- **Token Management**: Access and refresh token system
- **Password Reset**: Secure password reset via email
- **Role-Based Access**: Admin, moderator, and user roles
- **User Management**: Admin endpoints for user management
- **Security Features**: Password hashing, token expiration, CORS protection

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Security**: SHA-256 password hashing
- **Server**: Uvicorn

## 📋 Prerequisites

- Python 3.7+
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

The API will be available at `http://localhost:8002`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## 🔐 API Endpoints

### Authentication Endpoints

#### User Registration
```http
POST /register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "role": "user"
}
```

#### Send OTP Verification
```http
POST /send-otp
Content-Type: application/json

{
  "email": "john@example.com"
}
```

#### Verify OTP
```http
POST /verify-otp
Content-Type: application/json

{
  "email": "john@example.com",
  "otp": "123456"
}
```

#### User Login
```http
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Refresh Token
```http
POST /refresh-token
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Logout
```http
POST /logout
Authorization: Bearer <access_token>
```

### Password Management

#### Request Password Reset
```http
POST /password-reset-request
Content-Type: application/json

{
  "email": "john@example.com"
}
```

#### Confirm Password Reset
```http
POST /password-reset-confirm
Content-Type: application/json

{
  "email": "john@example.com",
  "reset_token": "abc123def456...",
  "new_password": "newsecurepassword123"
}
```

#### Change Password (Authenticated)
```http
POST /change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

### User Management

#### Get Current User
```http
GET /me
Authorization: Bearer <access_token>
```

#### Get All Users (Admin Only)
```http
GET /admin/users
Authorization: Bearer <admin_access_token>
```

#### Deactivate User (Admin Only)
```http
POST /admin/deactivate-user/{user_id}
Authorization: Bearer <admin_access_token>
```

## 📊 Data Models

### User
- `id`: Unique identifier
- `username`: Unique username
- `email`: Email address (must be verified)
- `full_name`: Optional full name
- `role`: User role (user, admin, moderator)
- `is_verified`: Email verification status
- `is_active`: Account status
- `created_at`: Registration timestamp
- `last_login`: Last login timestamp

### Token Response
- `access_token`: JWT access token (30 min expiry)
- `refresh_token`: JWT refresh token (7 days expiry)
- `token_type`: "bearer"
- `expires_in`: Token expiry in seconds

### OTP
- 6-digit numeric code
- 5-minute expiry
- Single-use verification

## 🔧 Configuration

### Security Settings
Update these variables in `app.py` for production:

```python
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
OTP_EXPIRE_MINUTES = 5
```

### CORS Configuration
For production, restrict allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🧪 Testing Examples

### Register a new user
```bash
curl -X POST http://localhost:8002/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Send OTP
```bash
curl -X POST http://localhost:8002/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Verify OTP (using the OTP from console)
```bash
curl -X POST http://localhost:8002/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp": "123456"
  }'
```

### Login
```bash
curl -X POST http://localhost:8002/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### Access protected endpoint
```bash
curl -X GET http://localhost:8002/me \
  -H "Authorization: Bearer <your_access_token>"
```

## 🏗️ Production Considerations

### Database
Replace in-memory storage with:
- PostgreSQL with SQLAlchemy
- MongoDB with Motor
- Firebase Firestore

### Email Service
Integrate with:
- SendGrid
- AWS SES
- Mailgun
- SMTP

### Rate Limiting
Add rate limiting for:
- Registration attempts
- Login attempts
- OTP requests
- Password reset requests

### Security Enhancements
- Implement CAPTCHA for registration
- Add 2FA support
- IP-based blocking
- Audit logging

## 🐳 Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
```

Build and run:
```bash
docker build -t auth-api .
docker run -p 8002:8002 auth-api
```

## 📝 Default Admin Account

For testing, a default admin account is available:
- **Email**: admin@example.com
- **Password**: admin123
- **Role**: admin

## 🔍 Sample Workflows

### Complete User Registration Flow
1. `POST /register` - Create account
2. `POST /send-otp` - Request verification
3. `POST /verify-otp` - Verify email
4. `POST /login` - Authenticate
5. Use `access_token` for protected endpoints

### Password Reset Flow
1. `POST /password-reset-request` - Request reset
2. Receive reset token via email
3. `POST /password-reset-confirm` - Confirm reset
4. Login with new password

## 🚨 Security Notes

- **SECRET_KEY**: Must be changed in production
- **HTTPS**: Always use HTTPS in production
- **Token Storage**: Store refresh tokens securely
- **Password Policy**: Implement strong password requirements
- **Rate Limiting**: Prevent brute force attacks
- **Logging**: Monitor authentication attempts

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code comments for implementation details

---

**Built with ❤️ using FastAPI**
