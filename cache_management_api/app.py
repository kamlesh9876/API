from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime, timedelta
import json
import hashlib
import time

app = FastAPI(
    title="Cache Management API",
    description="Advanced cache management service with multiple backends and intelligent caching strategies",
    version="1.0.0"
)

# Enums
class CacheBackend(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DATABASE = "database"
    FILE = "file"

class CacheStrategy(str, Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"

class DataType(str, Enum):
    STRING = "string"
    JSON = "json"
    BINARY = "binary"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DICTIONARY = "dictionary"

# Data Models
class CacheItem(BaseModel):
    key: str
    value: Any
    data_type: DataType
    ttl: Optional[int] = None  # Time to live in seconds
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size: int = 0
    metadata: Optional[Dict[str, Any]] = {}

class CacheRequest(BaseModel):
    key: str
    value: Any
    data_type: DataType = DataType.STRING
    ttl: Optional[int] = None
    backend: Optional[CacheBackend] = CacheBackend.MEMORY
    strategy: Optional[CacheStrategy] = CacheStrategy.LRU
    metadata: Optional[Dict[str, Any]] = {}

class CacheResponse(BaseModel):
    key: str
    value: Any
    data_type: DataType
    found: bool
    ttl: Optional[int] = None
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    size: int = 0
    metadata: Optional[Dict[str, Any]] = {}

class CacheStats(BaseModel):
    total_items: int
    total_memory_usage: int
    hit_rate: float
    miss_rate: float
    eviction_count: int
    backend: CacheBackend
    strategy: CacheStrategy

class CacheConfig(BaseModel):
    backend: CacheBackend = CacheBackend.MEMORY
    strategy: CacheStrategy = CacheStrategy.LRU
    max_memory: int = 100 * 1024 * 1024  # 100MB
    max_items: int = 10000
    default_ttl: int = 3600  # 1 hour
    cleanup_interval: int = 300  # 5 minutes
    compression_enabled: bool = False
    encryption_enabled: bool = False

# Storage (in production, use actual cache backends)
memory_cache = {}
cache_configs = {}
cache_stats = {}
cache_history = {}

# Initialize default cache config
default_config = CacheConfig()
cache_configs["default"] = default_config
cache_stats["default"] = {
    "hits": 0,
    "misses": 0,
    "evictions": 0,
    "total_items": 0,
    "total_memory_usage": 0
}

@app.get("/")
async def root():
    return {"message": "Cache Management API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Cache Operations
@app.post("/api/cache/set")
async def set_cache(request: CacheRequest):
    """Set a value in cache"""
    try:
        config_name = "default"
        config = cache_configs[config_name]
        stats = cache_stats[config_name]
        
        # Calculate value size
        value_str = json.dumps(request.value) if isinstance(request.value, (dict, list)) else str(request.value)
        size = len(value_str.encode('utf-8'))
        
        # Check memory limits
        if stats["total_memory_usage"] + size > config.max_memory:
            await evict_items(config_name, size)
        
        # Check item limits
        if stats["total_items"] >= config.max_items:
            await evict_items(config_name, size)
        
        # Create cache item
        cache_item = CacheItem(
            key=request.key,
            value=request.value,
            data_type=request.data_type,
            ttl=request.ttl or config.default_ttl,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            access_count=0,
            size=size,
            metadata=request.metadata or {}
        )
        
        # Store in cache
        memory_cache[request.key] = cache_item
        
        # Update statistics
        stats["total_items"] = len(memory_cache)
        stats["total_memory_usage"] = sum(item.size for item in memory_cache.values())
        
        # Schedule TTL cleanup if needed
        if cache_item.ttl:
            asyncio.create_task(schedule_ttl_cleanup(request.key, cache_item.ttl))
        
        return {
            "success": True,
            "message": "Value cached successfully",
            "key": request.key,
            "size": size,
            "ttl": cache_item.ttl,
            "backend": request.backend
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set cache: {str(e)}")

@app.get("/api/cache/get/{key}")
async def get_cache(key: str, backend: Optional[CacheBackend] = None):
    """Get a value from cache"""
    try:
        config_name = "default"
        stats = cache_stats[config_name]
        
        if key not in memory_cache:
            stats["misses"] += 1
            return {
                "success": True,
                "found": False,
                "message": "Key not found in cache",
                "key": key
            }
        
        cache_item = memory_cache[key]
        
        # Check TTL
        if cache_item.ttl:
            elapsed = (datetime.now() - cache_item.created_at).total_seconds()
            if elapsed > cache_item.ttl:
                del memory_cache[key]
                stats["misses"] += 1
                stats["total_items"] = len(memory_cache)
                return {
                    "success": True,
                    "found": False,
                    "message": "Key expired",
                    "key": key
                }
        
        # Update access statistics
        cache_item.accessed_at = datetime.now()
        cache_item.access_count += 1
        stats["hits"] += 1
        
        # Calculate remaining TTL
        remaining_ttl = None
        if cache_item.ttl:
            elapsed = (datetime.now() - cache_item.created_at).total_seconds()
            remaining_ttl = max(0, cache_item.ttl - elapsed)
        
        return {
            "success": True,
            "found": True,
            "cache_item": {
                "key": cache_item.key,
                "value": cache_item.value,
                "data_type": cache_item.data_type,
                "ttl": remaining_ttl,
                "created_at": cache_item.created_at.isoformat(),
                "accessed_at": cache_item.accessed_at.isoformat(),
                "access_count": cache_item.access_count,
                "size": cache_item.size,
                "metadata": cache_item.metadata
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache: {str(e)}")

@app.delete("/api/cache/delete/{key}")
async def delete_cache(key: str):
    """Delete a key from cache"""
    try:
        config_name = "default"
        stats = cache_stats[config_name]
        
        if key not in memory_cache:
            return {
                "success": True,
                "found": False,
                "message": "Key not found in cache",
                "key": key
            }
        
        del memory_cache[key]
        stats["total_items"] = len(memory_cache)
        stats["total_memory_usage"] = sum(item.size for item in memory_cache.values())
        
        return {
            "success": True,
            "found": True,
            "message": "Key deleted successfully",
            "key": key
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete cache: {str(e)}")

@app.post("/api/cache/clear")
async def clear_cache(pattern: Optional[str] = None, backend: Optional[CacheBackend] = None):
    """Clear cache with optional pattern matching"""
    try:
        config_name = "default"
        stats = cache_stats[config_name]
        
        keys_to_delete = []
        
        if pattern:
            # Pattern matching (simple wildcard support)
            import fnmatch
            for key in memory_cache.keys():
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)
        else:
            keys_to_delete = list(memory_cache.keys())
        
        deleted_count = len(keys_to_delete)
        
        for key in keys_to_delete:
            del memory_cache[key]
        
        stats["total_items"] = len(memory_cache)
        stats["total_memory_usage"] = sum(item.size for item in memory_cache.values())
        
        return {
            "success": True,
            "message": f"Cache cleared successfully",
            "deleted_count": deleted_count,
            "pattern": pattern
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

# Batch Operations
@app.post("/api/cache/set-batch")
async def set_batch_cache(items: List[CacheRequest]):
    """Set multiple values in cache"""
    try:
        results = []
        
        for item in items:
            try:
                result = await set_cache(item)
                results.append({
                    "key": item.key,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "key": item.key,
                    "success": False,
                    "error": str(e)
                })
        
        successful_count = len([r for r in results if r["success"]])
        
        return {
            "success": True,
            "message": f"Batch operation completed",
            "total_items": len(items),
            "successful_count": successful_count,
            "failed_count": len(items) - successful_count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch set failed: {str(e)}")

@app.post("/api/cache/get-batch")
async def get_batch_cache(keys: List[str]):
    """Get multiple values from cache"""
    try:
        results = []
        
        for key in keys:
            try:
                result = await get_cache(key)
                results.append({
                    "key": key,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "key": key,
                    "success": False,
                    "error": str(e)
                })
        
        found_count = len([r for r in results if r["success"] and r["result"]["found"]])
        
        return {
            "success": True,
            "message": f"Batch get completed",
            "total_keys": len(keys),
            "found_count": found_count,
            "not_found_count": len(keys) - found_count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch get failed: {str(e)}")

# Cache Management
@app.get("/api/cache/keys")
async def list_keys(
    pattern: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List cache keys with optional pattern matching"""
    try:
        keys = list(memory_cache.keys())
        
        if pattern:
            import fnmatch
            keys = [key for key in keys if fnmatch.fnmatch(key, pattern)]
        
        # Apply pagination
        total = len(keys)
        paginated_keys = keys[offset:offset + limit]
        
        # Add key details
        key_details = []
        for key in paginated_keys:
            if key in memory_cache:
                item = memory_cache[key]
                key_details.append({
                    "key": key,
                    "data_type": item.data_type,
                    "size": item.size,
                    "ttl": item.ttl,
                    "created_at": item.created_at.isoformat(),
                    "access_count": item.access_count,
                    "last_accessed": item.accessed_at.isoformat()
                })
        
        return {
            "success": True,
            "total_keys": total,
            "limit": limit,
            "offset": offset,
            "keys": key_details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list keys: {str(e)}")

@app.get("/api/cache/stats")
async def get_cache_stats(backend: Optional[CacheBackend] = None):
    """Get cache statistics"""
    try:
        config_name = "default"
        config = cache_configs[config_name]
        stats = cache_stats[config_name]
        
        # Calculate hit/miss rates
        total_requests = stats["hits"] + stats["misses"]
        hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        miss_rate = (stats["misses"] / total_requests * 100) if total_requests > 0 else 0
        
        cache_stats_obj = CacheStats(
            total_items=stats["total_items"],
            total_memory_usage=stats["total_memory_usage"],
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            eviction_count=stats["evictions"],
            backend=config.backend,
            strategy=config.strategy
        )
        
        return {
            "success": True,
            "statistics": cache_stats_obj.dict(),
            "config": config.dict(),
            "raw_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/api/cache/config")
async def update_cache_config(config: CacheConfig):
    """Update cache configuration"""
    try:
        config_name = "default"
        cache_configs[config_name] = config
        
        return {
            "success": True,
            "message": "Cache configuration updated",
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

@app.get("/api/cache/config")
async def get_cache_config():
    """Get current cache configuration"""
    try:
        config_name = "default"
        config = cache_configs[config_name]
        
        return {
            "success": True,
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")

# Advanced Operations
@app.post("/api/cache/warm")
async def warm_cache(data: Dict[str, Any]):
    """Warm cache with predefined data"""
    try:
        results = []
        
        for key, value in data.items():
            try:
                request = CacheRequest(
                    key=key,
                    value=value,
                    data_type=DataType.JSON if isinstance(value, (dict, list)) else DataType.STRING
                )
                result = await set_cache(request)
                results.append({
                    "key": key,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "key": key,
                    "success": False,
                    "error": str(e)
                })
        
        successful_count = len([r for r in results if r["success"]])
        
        return {
            "success": True,
            "message": f"Cache warming completed",
            "total_items": len(data),
            "successful_count": successful_count,
            "failed_count": len(data) - successful_count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache warming failed: {str(e)}")

@app.post("/api/cache/invalidate")
async def invalidate_cache(tags: Optional[List[str]] = None, pattern: Optional[str] = None):
    """Invalidate cache by tags or pattern"""
    try:
        keys_to_delete = []
        
        if tags:
            # Invalidate by metadata tags
            for key, item in memory_cache.items():
                if item.metadata and "tags" in item.metadata:
                    if any(tag in item.metadata["tags"] for tag in tags):
                        keys_to_delete.append(key)
        
        if pattern:
            # Invalidate by pattern
            import fnmatch
            for key in memory_cache.keys():
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)
        
        # Remove duplicates
        keys_to_delete = list(set(keys_to_delete))
        
        deleted_count = len(keys_to_delete)
        for key in keys_to_delete:
            del memory_cache[key]
        
        # Update stats
        config_name = "default"
        stats = cache_stats[config_name]
        stats["total_items"] = len(memory_cache)
        stats["total_memory_usage"] = sum(item.size for item in memory_cache.values())
        
        return {
            "success": True,
            "message": f"Cache invalidation completed",
            "deleted_count": deleted_count,
            "tags": tags,
            "pattern": pattern
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

@app.get("/api/cache/export")
async def export_cache(format: str = "json"):
    """Export cache data"""
    try:
        export_data = {}
        
        for key, item in memory_cache.items():
            export_data[key] = {
                "value": item.value,
                "data_type": item.data_type,
                "ttl": item.ttl,
                "created_at": item.created_at.isoformat(),
                "accessed_at": item.accessed_at.isoformat(),
                "access_count": item.access_count,
                "size": item.size,
                "metadata": item.metadata
            }
        
        if format.lower() == "json":
            return {
                "success": True,
                "format": "json",
                "data": export_data,
                "exported_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache export failed: {str(e)}")

# Utility Functions
async def evict_items(config_name: str, required_space: int):
    """Evict items based on cache strategy"""
    config = cache_configs[config_name]
    stats = cache_stats[config_name]
    
    if config.strategy == CacheStrategy.LRU:
        # Sort by last accessed time
        sorted_items = sorted(memory_cache.items(), key=lambda x: x[1].accessed_at)
    elif config.strategy == CacheStrategy.LFU:
        # Sort by access count
        sorted_items = sorted(memory_cache.items(), key=lambda x: x[1].access_count)
    elif config.strategy == CacheStrategy.FIFO:
        # Sort by creation time
        sorted_items = sorted(memory_cache.items(), key=lambda x: x[1].created_at)
    else:
        sorted_items = list(memory_cache.items())
    
    space_freed = 0
    evicted_count = 0
    
    for key, item in sorted_items:
        del memory_cache[key]
        space_freed += item.size
        evicted_count += 1
        stats["evictions"] += 1
        
        if space_freed >= required_space:
            break
    
    stats["total_items"] = len(memory_cache)
    stats["total_memory_usage"] = sum(item.size for item in memory_cache.values())

async def schedule_ttl_cleanup(key: str, ttl: int):
    """Schedule TTL cleanup for a key"""
    await asyncio.sleep(ttl)
    
    if key in memory_cache:
        item = memory_cache[key]
        elapsed = (datetime.now() - item.created_at).total_seconds()
        
        if elapsed >= ttl:
            del memory_cache[key]
            
            # Update stats
            config_name = "default"
            stats = cache_stats[config_name]
            stats["total_items"] = len(memory_cache)
            stats["total_memory_usage"] = sum(item.size for item in memory_cache.values())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
