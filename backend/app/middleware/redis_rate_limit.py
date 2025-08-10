"""Redis-based rate limiting middleware."""
import time
from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis
from redis.exceptions import RedisError
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-based rate limiting middleware for distributed systems."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
        exclude_paths: Optional[list] = None,
        redis_url: str = None,
        db: int = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/redoc"]
        
        # Redis connection
        self.redis_url = redis_url or settings.REDIS_URL
        self.db = db or settings.REDIS_RATE_LIMIT_DB
        self.redis_client = None
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                db=self.db,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis for rate limiting (db={self.db})")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}")
            self.redis_client = None
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get a unique identifier for the client."""
        # Try to get authenticated user ID from request
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    def _check_rate_limit_redis(self, identifier: str, endpoint: str) -> Tuple[bool, Optional[int]]:
        """Check rate limit using Redis."""
        if not self.redis_client:
            # Fall back to allowing requests if Redis is down
            return True, None
        
        current_time = int(time.time())
        minute_window = current_time // 60
        hour_window = current_time // 3600
        
        # Keys for different windows
        minute_key = f"rate_limit:minute:{minute_window}:{identifier}:{endpoint}"
        hour_key = f"rate_limit:hour:{hour_window}:{identifier}:{endpoint}"
        burst_key = f"rate_limit:burst:{identifier}:{endpoint}"
        
        try:
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Check burst limit
            pipe.get(burst_key)
            
            # Check minute limit
            pipe.get(minute_key)
            
            # Check hour limit
            pipe.get(hour_key)
            
            results = pipe.execute()
            
            burst_count = int(results[0] or 0)
            minute_count = int(results[1] or 0)
            hour_count = int(results[2] or 0)
            
            # Check limits
            if burst_count >= self.burst_size:
                return False, 1  # Retry after 1 second
            
            if minute_count >= self.requests_per_minute:
                retry_after = 60 - (current_time % 60) + 1
                return False, retry_after
            
            if hour_count >= self.requests_per_hour:
                retry_after = 3600 - (current_time % 3600) + 1
                return False, retry_after
            
            # Increment counters
            pipe = self.redis_client.pipeline()
            
            # Increment burst counter
            pipe.incr(burst_key)
            pipe.expire(burst_key, 1)  # 1 second expiry
            
            # Increment minute counter
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)  # 60 seconds expiry
            
            # Increment hour counter
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)  # 3600 seconds expiry
            
            pipe.execute()
            
            return True, None
            
        except RedisError as e:
            logger.error(f"Redis rate limit error: {e}")
            # Allow request if Redis fails
            return True, None
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client identifier and endpoint
        identifier = self._get_client_identifier(request)
        endpoint = f"{request.method}:{request.url.path}"
        
        # Check rate limit
        allowed, retry_after = self._check_rate_limit_redis(identifier, endpoint)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier} on {endpoint}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        if self.redis_client:
            try:
                current_time = int(time.time())
                minute_window = current_time // 60
                hour_window = current_time // 3600
                
                minute_key = f"rate_limit:minute:{minute_window}:{identifier}:{endpoint}"
                hour_key = f"rate_limit:hour:{hour_window}:{identifier}:{endpoint}"
                
                minute_count = int(self.redis_client.get(minute_key) or 0)
                hour_count = int(self.redis_client.get(hour_key) or 0)
                
                response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
                response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
                response.headers["X-RateLimit-Remaining-Minute"] = str(
                    max(0, self.requests_per_minute - minute_count)
                )
                response.headers["X-RateLimit-Remaining-Hour"] = str(
                    max(0, self.requests_per_hour - hour_count)
                )
            except RedisError:
                pass
        
        return response


class RedisSlidingWindowRateLimiter:
    """
    Redis-based sliding window rate limiter for more accurate rate limiting.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int,
        window_seconds: int
    ):
        self.redis_client = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Check if request is allowed using sliding window algorithm.
        
        Returns:
            Tuple of (is_allowed, requests_in_window)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        try:
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry
            pipe.expire(key, self.window_seconds + 1)
            
            results = pipe.execute()
            
            # Get count before adding current request
            count = results[1]
            
            if count >= self.max_requests:
                # Remove the just-added entry
                self.redis_client.zrem(key, str(now))
                return False, count
            
            return True, count + 1
            
        except RedisError as e:
            logger.error(f"Redis sliding window error: {e}")
            # Allow request if Redis fails
            return True, 0
    
    def reset(self, key: str):
        """Reset rate limit for a key."""
        try:
            self.redis_client.delete(key)
        except RedisError as e:
            logger.error(f"Redis reset error: {e}")
