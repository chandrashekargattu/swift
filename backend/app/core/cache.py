"""Redis caching implementation."""
import json
import logging
from typing import Optional, Any, Union, Callable
from functools import wraps
import hashlib
import pickle
from datetime import timedelta

import redis
from redis.exceptions import RedisError
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager."""
    
    def __init__(self, redis_url: str = None, decode_responses: bool = True):
        """Initialize Redis connection."""
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        self.decode_responses = decode_responses
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=self.decode_responses
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except RedisError:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                # Try to deserialize JSON first
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # If JSON fails, try pickle
                    try:
                        return pickle.loads(value.encode('latin-1') if isinstance(value, str) else value)
                    except:
                        return value
            return None
        except RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache."""
        if not self.is_connected():
            return False
        
        try:
            # Convert timedelta to seconds
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            # Try to serialize as JSON first
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                # If JSON fails, use pickle
                serialized_value = pickle.dumps(value)
            
            if ttl:
                return bool(self.redis_client.setex(key, ttl, serialized_value))
            else:
                return bool(self.redis_client.set(key, serialized_value))
        except RedisError as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except RedisError as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.is_connected():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Redis clear pattern error: {e}")
            return 0
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter."""
        if not self.is_connected():
            return None
        
        try:
            return self.redis_client.incr(key, amount)
        except RedisError as e:
            logger.error(f"Redis incr error: {e}")
            return None
    
    def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration on a key."""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            return bool(self.redis_client.expire(key, ttl))
        except RedisError as e:
            logger.error(f"Redis expire error: {e}")
            return False
    
    def ttl(self, key: str) -> Optional[int]:
        """Get time to live for a key."""
        if not self.is_connected():
            return None
        
        try:
            ttl = self.redis_client.ttl(key)
            return ttl if ttl >= 0 else None
        except RedisError as e:
            logger.error(f"Redis ttl error: {e}")
            return None


# Singleton instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_key_wrapper(func: Callable) -> Callable:
    """Generate cache key for function calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a unique key based on function name and arguments
        key_parts = [func.__module__, func.__name__]
        
        # Add positional arguments
        for arg in args:
            if hasattr(arg, '__dict__'):
                # For objects, use their dict representation
                key_parts.append(str(sorted(arg.__dict__.items())))
            else:
                key_parts.append(str(arg))
        
        # Add keyword arguments
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        # Create hash of the key parts
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"cache:{func.__name__}:{key_hash}"
    
    return wrapper


def cached(ttl: Union[int, timedelta] = 300, key_prefix: str = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds or timedelta
        key_prefix: Optional prefix for cache keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            cache_key = cache_key_wrapper(func)(*args, **kwargs)
            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Call the function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            cache_key = cache_key_wrapper(func)(*args, **kwargs)
            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for key: {cache_key}")
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator to invalidate cache matching pattern after function execution.
    
    Args:
        pattern: Redis key pattern to invalidate
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            cache = get_cache_manager()
            cleared = cache.clear_pattern(pattern)
            logger.debug(f"Invalidated {cleared} cache keys matching pattern: {pattern}")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache = get_cache_manager()
            cleared = cache.clear_pattern(pattern)
            logger.debug(f"Invalidated {cleared} cache keys matching pattern: {pattern}")
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Import asyncio at the end to avoid circular imports
import asyncio
