import time
from typing import Dict, Tuple, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/redoc"]
        
        # Storage for request timestamps
        self.minute_buckets: Dict[str, deque] = defaultdict(lambda: deque(maxlen=requests_per_minute))
        self.hour_buckets: Dict[str, deque] = defaultdict(lambda: deque(maxlen=requests_per_hour))
        self.burst_buckets: Dict[str, int] = defaultdict(int)
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_buckets())
    
    async def _cleanup_buckets(self):
        """Periodically clean up old entries from buckets."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                current_time = time.time()
                
                # Clean minute buckets
                for key in list(self.minute_buckets.keys()):
                    self.minute_buckets[key] = deque(
                        (t for t in self.minute_buckets[key] if current_time - t < 60),
                        maxlen=self.requests_per_minute
                    )
                    if not self.minute_buckets[key]:
                        del self.minute_buckets[key]
                
                # Clean hour buckets
                for key in list(self.hour_buckets.keys()):
                    self.hour_buckets[key] = deque(
                        (t for t in self.hour_buckets[key] if current_time - t < 3600),
                        maxlen=self.requests_per_hour
                    )
                    if not self.hour_buckets[key]:
                        del self.hour_buckets[key]
                
                # Reset burst buckets
                self.burst_buckets.clear()
                
            except Exception as e:
                logger.error(f"Error in rate limit cleanup: {e}")
    
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
    
    def _check_rate_limit(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """Check if the client has exceeded rate limits."""
        current_time = time.time()
        
        # Check burst limit
        if self.burst_buckets[identifier] >= self.burst_size:
            return False, 1  # Retry after 1 second
        
        # Clean old entries from minute bucket
        minute_bucket = self.minute_buckets[identifier]
        minute_bucket = deque(
            (t for t in minute_bucket if current_time - t < 60),
            maxlen=self.requests_per_minute
        )
        self.minute_buckets[identifier] = minute_bucket
        
        # Check minute limit
        if len(minute_bucket) >= self.requests_per_minute:
            oldest_request = min(minute_bucket) if minute_bucket else current_time
            retry_after = int(60 - (current_time - oldest_request)) + 1
            return False, retry_after
        
        # Clean old entries from hour bucket
        hour_bucket = self.hour_buckets[identifier]
        hour_bucket = deque(
            (t for t in hour_bucket if current_time - t < 3600),
            maxlen=self.requests_per_hour
        )
        self.hour_buckets[identifier] = hour_bucket
        
        # Check hour limit
        if len(hour_bucket) >= self.requests_per_hour:
            oldest_request = min(hour_bucket) if hour_bucket else current_time
            retry_after = int(3600 - (current_time - oldest_request)) + 1
            return False, retry_after
        
        return True, None
    
    def _record_request(self, identifier: str):
        """Record a request for rate limiting."""
        current_time = time.time()
        self.minute_buckets[identifier].append(current_time)
        self.hour_buckets[identifier].append(current_time)
        self.burst_buckets[identifier] += 1
        
        # Reset burst counter after a short delay
        asyncio.create_task(self._reset_burst(identifier))
    
    async def _reset_burst(self, identifier: str):
        """Reset burst counter after a delay."""
        await asyncio.sleep(1)
        self.burst_buckets[identifier] = max(0, self.burst_buckets[identifier] - 1)
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client identifier
        identifier = self._get_client_identifier(request)
        
        # Check rate limit
        allowed, retry_after = self._check_rate_limit(identifier)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier} on {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Record the request
        self._record_request(identifier)
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(self.minute_buckets[identifier])
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(self.hour_buckets[identifier])
        )
        
        return response


class EndpointRateLimiter:
    """Rate limiter for specific endpoints."""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=requests_per_minute))
    
    async def __call__(self, request: Request):
        """Check rate limit for the endpoint."""
        # Get client identifier
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        identifier = f"{client_ip}:{request.url.path}"
        current_time = time.time()
        
        # Clean old entries
        request_times = self.requests[identifier]
        request_times = deque(
            (t for t in request_times if current_time - t < 60),
            maxlen=self.requests_per_minute
        )
        self.requests[identifier] = request_times
        
        # Check limit
        if len(request_times) >= self.requests_per_minute:
            oldest_request = min(request_times) if request_times else current_time
            retry_after = int(60 - (current_time - oldest_request)) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests for this endpoint",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Record request
        request_times.append(current_time)
