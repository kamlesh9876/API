# Cache Management API

A comprehensive cache management service providing intelligent caching strategies, multiple backends, and advanced cache operations. Built with FastAPI, this service offers high-performance caching with configurable eviction policies and real-time monitoring.

## 🚀 Features

### Cache Operations
- **Set/Get/Delete**: Basic cache operations with TTL support
- **Batch Operations**: Efficient bulk cache operations
- **Pattern Matching**: Wildcard pattern-based key operations
- **TTL Management**: Automatic expiration with configurable TTL
- **Metadata Support**: Attach metadata to cache items

### Cache Strategies
- **LRU**: Least Recently Used eviction
- **LFU**: Least Frequently Used eviction
- **FIFO**: First In First Out eviction
- **TTL**: Time-based expiration
- **Write-Through**: Synchronous writes to backend
- **Write-Behind**: Asynchronous writes to backend

### Advanced Features
- **Multiple Backends**: Memory, Redis, Memcached, Database, File
- **Cache Warming**: Pre-populate cache with important data
- **Cache Invalidation**: Tag-based and pattern-based invalidation
- **Cache Export**: Export cache data for backup/analysis
- **Real-time Statistics**: Comprehensive cache performance metrics
- **Memory Management**: Intelligent memory usage and cleanup

### Monitoring & Analytics
- **Hit/Miss Rates**: Track cache efficiency
- **Memory Usage**: Monitor memory consumption
- **Eviction Statistics**: Track cache evictions
- **Access Patterns**: Analyze cache access patterns
- **Performance Metrics**: Response time and throughput

## 🛠️ Technology Stack

- **Framework**: FastAPI with Python
- **Async Support**: Full async/await implementation
- **Data Models**: Pydantic models with validation
- **Background Tasks**: Asyncio for TTL cleanup
- **Memory Management**: Efficient memory usage tracking

## 📋 API Endpoints

### Basic Cache Operations

#### Set Cache Value
```http
POST /api/cache/set
Content-Type: application/json

{
  "key": "user:123",
  "value": {"name": "John Doe", "email": "john@example.com"},
  "data_type": "json",
  "ttl": 3600,
  "backend": "memory",
  "strategy": "lru",
  "metadata": {
    "tags": ["user", "profile"],
    "source": "database"
  }
}
```

#### Get Cache Value
```http
GET /api/cache/get/user:123?backend=memory
```

#### Delete Cache Value
```http
DELETE /api/cache/delete/user:123
```

#### Clear Cache
```http
POST /api/cache/clear?pattern=user:*&backend=memory
```

### Batch Operations

#### Set Multiple Values
```http
POST /api/cache/set-batch
Content-Type: application/json

[
  {
    "key": "user:123",
    "value": {"name": "John"},
    "data_type": "json",
    "ttl": 3600
  },
  {
    "key": "user:456",
    "value": {"name": "Jane"},
    "data_type": "json",
    "ttl": 3600
  }
]
```

#### Get Multiple Values
```http
POST /api/cache/get-batch
Content-Type: application/json

["user:123", "user:456", "user:789"]
```

### Cache Management

#### List Cache Keys
```http
GET /api/cache/keys?pattern=user:*&limit=100&offset=0
```

#### Get Cache Statistics
```http
GET /api/cache/stats?backend=memory
```

#### Update Cache Configuration
```http
POST /api/cache/config
Content-Type: application/json

{
  "backend": "memory",
  "strategy": "lru",
  "max_memory": 104857600,
  "max_items": 10000,
  "default_ttl": 3600,
  "cleanup_interval": 300,
  "compression_enabled": false,
  "encryption_enabled": false
}
```

#### Get Cache Configuration
```http
GET /api/cache/config
```

### Advanced Operations

#### Warm Cache
```http
POST /api/cache/warm
Content-Type: application/json

{
  "config:app": {"version": "1.0.0", "features": ["auth", "api"]},
  "stats:daily": {"users": 1000, "requests": 50000},
  "cache:hot": {"items": ["popular", "trending", "featured"]}
}
```

#### Invalidate Cache
```http
POST /api/cache/invalidate
Content-Type: application/json

{
  "tags": ["user", "profile"],
  "pattern": "temp:*"
}
```

#### Export Cache
```http
GET /api/cache/export?format=json
```

## 📊 Data Models

### CacheRequest
```python
class CacheRequest(BaseModel):
    key: str
    value: Any
    data_type: DataType = DataType.STRING
    ttl: Optional[int] = None
    backend: Optional[CacheBackend] = CacheBackend.MEMORY
    strategy: Optional[CacheStrategy] = CacheStrategy.LRU
    metadata: Optional[Dict[str, Any]] = {}
```

### CacheItem
```python
class CacheItem(BaseModel):
    key: str
    value: Any
    data_type: DataType
    ttl: Optional[int] = None
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size: int = 0
    metadata: Optional[Dict[str, Any]] = {}
```

### CacheConfig
```python
class CacheConfig(BaseModel):
    backend: CacheBackend = CacheBackend.MEMORY
    strategy: CacheStrategy = CacheStrategy.LRU
    max_memory: int = 100 * 1024 * 1024
    max_items: int = 10000
    default_ttl: int = 3600
    cleanup_interval: int = 300
    compression_enabled: bool = False
    encryption_enabled: bool = False
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Install optional backends
pip install redis memcached

# Run the API
python app.py
# or
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
```bash
# Create .env file
CACHE_BACKEND=memory
CACHE_STRATEGY=lru
CACHE_MAX_MEMORY=104857600
CACHE_MAX_ITEMS=10000
CACHE_DEFAULT_TTL=3600
REDIS_URL=redis://localhost:6379
MEMCACHED_URL=memcached://localhost:11211
```

## 📝 Usage Examples

### Python Client
```python
import requests
import json
import time

# Set a value in cache
cache_data = {
    "key": "user:123",
    "value": {
        "name": "John Doe",
        "email": "john@example.com",
        "last_login": "2024-01-15T10:30:00Z"
    },
    "data_type": "json",
    "ttl": 3600,
    "metadata": {
        "tags": ["user", "profile"],
        "source": "database"
    }
}

response = requests.post(
    "http://localhost:8000/api/cache/set",
    json=cache_data
)

print(f"Cache set: {response.json()}")

# Get value from cache
get_response = requests.get("http://localhost:8000/api/cache/get/user:123")
cache_result = get_response.json()

if cache_result["found"]:
    print(f"Cache hit: {cache_result['cache_item']['value']}")
else:
    print("Cache miss")

# Batch operations
batch_data = [
    {
        "key": "config:app",
        "value": {"version": "1.0.0", "debug": False},
        "data_type": "json"
    },
    {
        "key": "stats:daily",
        "value": {"users": 1000, "requests": 50000},
        "data_type": "json"
    }
]

batch_response = requests.post(
    "http://localhost:8000/api/cache/set-batch",
    json=batch_data
)

print(f"Batch set: {batch_response.json()}")

# Get multiple keys
get_batch_response = requests.post(
    "http://localhost:8000/api/cache/get-batch",
    json=["config:app", "stats:daily", "nonexistent"]
)

batch_result = get_batch_response.json()
print(f"Batch get: {batch_result}")

# Get cache statistics
stats_response = requests.get("http://localhost:8000/api/cache/stats")
stats = stats_response.json()
print(f"Cache stats: {stats['statistics']}")

# Warm cache with important data
warm_data = {
    "config:system": {"maintenance": False, "version": "2.1.0"},
    "cache:hot": {"popular_items": ["item1", "item2", "item3"]},
    "user:admin": {"role": "admin", "permissions": ["read", "write", "delete"]}
}

warm_response = requests.post(
    "http://localhost:8000/api/cache/warm",
    json=warm_data
)

print(f"Cache warming: {warm_response.json()}")

# List keys with pattern
keys_response = requests.get("http://localhost:8000/api/cache/keys?pattern=config:*")
keys = keys_response.json()
print(f"Config keys: {keys['keys']}")

# Invalidate cache by tags
invalidate_response = requests.post(
    "http://localhost:8000/api/cache/invalidate",
    json={"tags": ["user", "profile"]}
)

print(f"Cache invalidation: {invalidate_response.json()}")
```

### JavaScript Client
```javascript
// Set value in cache
const cacheData = {
    key: 'user:123',
    value: {
        name: 'John Doe',
        email: 'john@example.com',
        lastLogin: '2024-01-15T10:30:00Z'
    },
    data_type: 'json',
    ttl: 3600,
    metadata: {
        tags: ['user', 'profile'],
        source: 'database'
    }
};

fetch('http://localhost:8000/api/cache/set', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(cacheData)
})
.then(response => response.json())
.then(data => {
    console.log('Cache set:', data);
})
.catch(error => console.error('Error:', error));

// Get value from cache
fetch('http://localhost:8000/api/cache/get/user:123')
.then(response => response.json())
.then(data => {
    if (data.found) {
        console.log('Cache hit:', data.cache_item.value);
    } else {
        console.log('Cache miss');
    }
})
.catch(error => console.error('Error:', error));

// Batch operations
const batchData = [
    {
        key: 'config:app',
        value: { version: '1.0.0', debug: false },
        data_type: 'json'
    },
    {
        key: 'stats:daily',
        value: { users: 1000, requests: 50000 },
        data_type: 'json'
    }
];

fetch('http://localhost:8000/api/cache/set-batch', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(batchData)
})
.then(response => response.json())
.then(data => {
    console.log('Batch set:', data);
})
.catch(error => console.error('Error:', error));

// Get multiple keys
fetch('http://localhost:8000/api/cache/get-batch', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(['config:app', 'stats:daily', 'nonexistent'])
})
.then(response => response.json())
.then(data => {
    console.log('Batch get:', data);
    
    // Process results
    data.results.forEach(result => {
        if (result.success && result.result.found) {
            console.log(`${result.key}:`, result.result.cache_item.value);
        } else {
            console.log(`${result.key}: Not found`);
        }
    });
})
.catch(error => console.error('Error:', error));

// Get cache statistics
fetch('http://localhost:8000/api/cache/stats')
.then(response => response.json())
.then(data => {
    console.log('Cache statistics:', data.statistics);
    console.log(`Hit rate: ${data.statistics.hit_rate.toFixed(2)}%`);
    console.log(`Memory usage: ${(data.statistics.total_memory_usage / 1024 / 1024).toFixed(2)} MB`);
})
.catch(error => console.error('Error:', error));

// Warm cache
const warmData = {
    'config:system': { maintenance: false, version: '2.1.0' },
    'cache:hot': { popular_items: ['item1', 'item2', 'item3'] },
    'user:admin': { role: 'admin', permissions: ['read', 'write', 'delete'] }
};

fetch('http://localhost:8000/api/cache/warm', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(warmData)
})
.then(response => response.json())
.then(data => {
    console.log('Cache warming:', data);
})
.catch(error => console.error('Error:', error));
```

## 🔧 Configuration

### Environment Variables
```bash
# Cache Configuration
CACHE_BACKEND=memory
CACHE_STRATEGY=lru
CACHE_MAX_MEMORY=104857600
CACHE_MAX_ITEMS=10000
CACHE_DEFAULT_TTL=3600
CACHE_CLEANUP_INTERVAL=300

# Backend Configuration
REDIS_URL=redis://localhost:6379
REDIS_DB=0
REDIS_PASSWORD=
MEMCACHED_URL=memcached://localhost:11211
DATABASE_URL=sqlite:///./cache.db

# Performance
CACHE_COMPRESSION_ENABLED=false
CACHE_ENCRYPTION_ENABLED=false
CACHE_SERIALIZATION_FORMAT=json
CACHE_MAX_KEY_LENGTH=250

# Monitoring
CACHE_METRICS_ENABLED=true
CACHE_ACCESS_LOG_ENABLED=true
CACHE_PERFORMANCE_TRACKING=true

# Security
CACHE_AUTH_ENABLED=false
CACHE_API_KEY=your_cache_api_key
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Cache Backends
- **memory**: In-memory cache (default)
- **redis**: Redis cache server
- **memcached**: Memcached server
- **database**: Database-backed cache
- **file**: File-based cache storage

### Cache Strategies
- **lru**: Least Recently Used (default)
- **lfu**: Least Frequently Used
- **fifo**: First In First Out
- **ttl**: Time-based expiration
- **write_through**: Synchronous writes
- **write_behind**: Asynchronous writes

### Data Types
- **string**: String values
- **json**: JSON objects and arrays
- **binary**: Binary data
- **number**: Numeric values
- **boolean**: Boolean values
- **list**: List data structures
- **dictionary**: Dictionary objects

## 📈 Use Cases

### Application Caching
- **Database Query Results**: Cache frequent database queries
- **API Responses**: Cache external API responses
- **Computed Results**: Cache expensive computations
- **Session Data**: Cache user session information
- **Configuration Data**: Cache application configuration

### Performance Optimization
- **Reduce Database Load**: Minimize database queries
- **Improve Response Times**: Faster data retrieval
- **Scalability**: Handle increased traffic
- **Cost Reduction**: Reduce resource usage
- **User Experience**: Faster page loads

### Data Management
- **Temporary Storage**: Store temporary data
- **Rate Limiting**: Implement rate limiting
- **Feature Flags**: Cache feature flag states
- **Analytics Data**: Cache analytics results
- **Search Results**: Cache search results

## 🛡️ Security Features

### Data Protection
- **Encryption**: Optional data encryption
- **Access Control**: Restrict cache access
- **Data Sanitization**: Validate cached data
- **Secure Connections**: HTTPS/TLS support
- **API Authentication**: Optional API key protection

### Cache Security
- **Key Validation**: Validate cache keys
- **Size Limits**: Prevent cache overflow
- **Access Logging**: Track cache access
- **Rate Limiting**: Prevent abuse
- **Data Isolation**: Separate cache namespaces

## 📊 Monitoring

### Performance Metrics
- **Hit Rate**: Percentage of cache hits
- **Miss Rate**: Percentage of cache misses
- **Response Time**: Cache operation latency
- **Memory Usage**: Memory consumption
- **Eviction Rate**: Cache eviction frequency

### Cache Analytics
- **Access Patterns**: Analyze access patterns
- **Hot Keys**: Identify frequently accessed keys
- **Memory Distribution**: Memory usage by key type
- **TTL Distribution**: TTL setting analysis
- **Backend Performance**: Backend-specific metrics

## 🔗 Related APIs

- **Database API**: For database-backed caching
- **Storage API**: For file-based caching
- **Analytics API**: For cache performance analytics
- **Monitoring API**: For cache health monitoring
- **Configuration API**: For cache configuration management

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: This is a simulation API with in-memory caching. In production, integrate with actual cache backends like:
- **Redis**: For distributed caching
- **Memcached**: For high-performance caching
- **Database**: For persistent caching
- **File System**: For file-based caching
- **Cloud Services**: AWS ElastiCache, Azure Cache, etc.
