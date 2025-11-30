# URL Shortener API (Bitly Clone)

A comprehensive URL shortening service built with FastAPI, featuring analytics, custom slugs, and detailed click tracking.

## 🚀 Features

- **URL Shortening**: Create short URLs from long URLs
- **Custom Slugs**: Use custom aliases for URLs
- **Click Tracking**: Track every click with detailed analytics
- **Analytics Dashboard**: Comprehensive analytics including:
  - Geographic data (country, city)
  - Device and browser breakdown
  - Time-based analytics (hourly, daily)
  - Referrer tracking
  - Unique vs total clicks
- **URL Management**: Update, deactivate, or delete URLs
- **Expiration Dates**: Set expiration for URLs
- **Password Protection**: Optional password protection for URLs
- **Global Statistics**: Overview of all URLs and performance

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: In-memory (for demo) - Ready for MongoDB integration
- **Analytics**: Real-time click tracking and processing
- **Security**: Input validation, CORS protection

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

The API will be available at `http://localhost:8003`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

## 🔗 API Endpoints

### URL Management

#### Create Short URL
```http
POST /shorten
Content-Type: application/json

{
  "original_url": "https://www.example.com/very/long/url/path",
  "custom_slug": "my-link",
  "expires_at": "2024-12-31T23:59:59",
  "password": "optional-password"
}
```

#### Redirect to Original URL
```http
GET /{slug}
```
*Automatically redirects to the original URL and tracks the click*

#### Get URL Information
```http
GET /url/{slug}
```

#### Update URL
```http
PUT /url/{slug}
Content-Type: application/json

{
  "original_url": "https://updated-url.com",
  "expires_at": "2024-12-31T23:59:59",
  "is_active": true
}
```

#### Delete URL
```http
DELETE /url/{slug}
```

#### List All URLs
```http
GET /urls?limit=50&offset=0
```

### Analytics

#### Get URL Analytics
```http
GET /analytics/{slug}
```

#### Global Statistics
```http
GET /stats
```

### System

#### Health Check
```http
GET /health
```

## 📊 Analytics Features

### Geographic Analytics
- **Country breakdown**: Top countries by clicks
- **City breakdown**: Top cities by clicks
- **IP-based location**: Mock GeoIP service (replace with real service in production)

### Device & Browser Analytics
- **Device types**: Desktop, Mobile, Tablet
- **Browser detection**: Chrome, Firefox, Safari, Edge, Opera
- **OS detection**: Windows, macOS, Linux, Android, iOS

### Time-Based Analytics
- **Hourly clicks**: Click distribution by hour
- **Daily clicks**: Click trends over time
- **Recent clicks**: Last 50 clicks with full details

### Engagement Metrics
- **Total clicks**: Overall click count
- **Unique clicks**: Unique visitors by IP
- **Clicks today/week/month**: Time-based performance
- **Referrer tracking**: Traffic sources

## 🧪 Testing Examples

### Create a short URL
```bash
curl -X POST http://localhost:8003/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.google.com/search?q=fastapi",
    "custom_slug": "fastapi-search"
  }'
```

### Test redirection
```bash
curl -L http://localhost:8003/fastapi-search
```

### Get analytics
```bash
curl http://localhost:8003/analytics/fastapi-search
```

### List all URLs
```bash
curl http://localhost:8003/urls
```

### Get global stats
```bash
curl http://localhost:8003/stats
```

## 📊 Data Models

### URL Entry
```json
{
  "id": 1,
  "original_url": "https://example.com",
  "slug": "abc123",
  "custom_slug": "my-link",
  "created_at": "2024-01-01T12:00:00",
  "expires_at": "2024-12-31T23:59:59",
  "click_count": 42,
  "is_active": true,
  "password": "optional-password"
}
```

### Click Analytics
```json
{
  "timestamp": "2024-01-01T12:30:00",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "referrer": "https://google.com",
  "country": "United States",
  "city": "New York",
  "device_type": "desktop",
  "browser_type": "chrome",
  "os": "Windows"
}
```

### Analytics Response
```json
{
  "short_url": "http://localhost:8003/abc123",
  "total_clicks": 150,
  "unique_clicks": 120,
  "clicks_today": 5,
  "clicks_this_week": 25,
  "clicks_this_month": 85,
  "top_countries": [
    {"country": "United States", "clicks": 75},
    {"country": "United Kingdom", "clicks": 30}
  ],
  "device_breakdown": {
    "desktop": 90,
    "mobile": 50,
    "tablet": 10
  },
  "browser_breakdown": {
    "chrome": 80,
    "firefox": 35,
    "safari": 25,
    "edge": 10
  }
}
```

## 🔧 Configuration

### Environment Variables
Create `.env` file for production:

```bash
# Database Configuration
MONGODB_URI=mongodb://localhost:27017/url_shortener
REDIS_URL=redis://localhost:6379

# GeoIP Service
MAXMIND_API_KEY=your-maxmind-api-key
IPINFO_API_KEY=your-ipinfo-api-key

# Base URL
BASE_URL=https://your-domain.com

# Security
SECRET_KEY=your-secret-key

# Analytics Retention
ANALYTICS_RETENTION_DAYS=365
```

### Custom Slug Rules
- Minimum 3 characters
- Maximum 50 characters
- Alphanumeric characters only
- Case insensitive
- First come, first served

### URL Validation
- Valid URL format required
- HTTP/HTTPS protocols only
- Maximum URL length: 2048 characters

## 🗄️ Database Integration

The API is designed to work with MongoDB. Replace in-memory storage with:

```python
from pymongo import MongoClient

# Database setup
client = MongoClient(MONGODB_URI)
db = client.url_shortener

# Collections
urls_collection = db.urls
clicks_collection = db.clicks
analytics_collection = db.analytics
```

## 🚀 Production Deployment

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8003

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  url-shortener:
    build: .
    ports:
      - "8003:8003"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/url_shortener
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:5.0
    ports:
      - "27017:27017"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Cloud Deployment
Deploy on:
- **AWS Lambda** + API Gateway
- **Google Cloud Functions**
- **Azure Functions**
- **Heroku**
- **DigitalOcean App Platform**
- **Railway**
- **Render**

## 📈 Performance Considerations

### Caching
- Redis for frequently accessed URLs
- Analytics aggregation caching
- CDN for static assets

### Rate Limiting
- Implement rate limiting for URL creation
- IP-based click tracking limits
- API endpoint throttling

### Scalability
- Horizontal scaling with load balancers
- Database sharding for high traffic
- Analytics data archiving

## 🔍 Advanced Features

### QR Code Generation
```python
import qrcode
from io import BytesIO
import base64

def generate_qr_code(url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    return base64.b64encode(buffer.getvalue()).decode()
```

### Bulk URL Creation
```python
@app.post("/bulk-shorten")
async def bulk_shorten(urls: List[URLCreate]):
    results = []
    for url_data in urls:
        result = await create_short_url(url_data, request)
        results.append(result)
    return results
```

### Custom Domains
```python
@app.get("/{custom_domain}/{slug}")
async def custom_domain_redirect(custom_domain: str, slug: str):
    # Handle custom domain redirects
    pass
```

## 🛡️ Security Features

### Input Validation
- URL format validation
- Custom slug sanitization
- Rate limiting protection

### Click Fraud Detection
- IP-based click pattern analysis
- User agent validation
- Time-based click thresholds

### Privacy Compliance
- GDPR compliance options
- IP anonymization
- Data retention policies

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the code comments for implementation details

---

**Built with ❤️ using FastAPI**
