"""
Advanced Rate Limiting System
Provides granular rate limiting with user-based quotas and endpoint-specific limits
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone
import asyncio
import logging
from fastapi import HTTPException, Request, status
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class RateLimit:
    """Rate limit configuration"""
    def __init__(self, requests: int, window: int, description: str = ""):
        self.requests = requests  # Number of requests allowed
        self.window = window      # Time window in seconds
        self.description = description

class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = datetime.now(timezone.utc)
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, return True if allowed"""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_refill).total_seconds()
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

class SlidingWindowCounter:
    """Sliding window counter for rate limiting"""
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed and record it"""
        now = datetime.now(timezone.utc)
        
        # Remove old requests outside the window
        cutoff = now - timedelta(seconds=self.window_size)
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        # Add current request
        self.requests.append(now)
        
        return True  # Will be checked against limits elsewhere

class AdvancedRateLimiter:
    """Advanced rate limiting with multiple algorithms and user-based quotas"""
    
    # Default rate limits per endpoint pattern
    DEFAULT_LIMITS = {
        # Authentication endpoints - more lenient
        "/api/auth/login": RateLimit(5, 60, "Login attempts per minute"),
        "/api/auth/register": RateLimit(3, 300, "Registration attempts per 5 minutes"),
        
        # Chat endpoints - moderate limits
        "/api/chat/": RateLimit(30, 60, "Chat requests per minute"),
        "/api/chat/*": RateLimit(30, 60, "Chat operations per minute"),
        
        # File operations - stricter limits
        "/api/files/*": RateLimit(20, 60, "File operations per minute"),
        "/api/workspace/*": RateLimit(15, 60, "Workspace operations per minute"),
        
        # GitHub integration - very strict
        "/api/github/*": RateLimit(10, 300, "GitHub operations per 5 minutes"),
        
        # Admin operations - strict
        "/api/admin/*": RateLimit(5, 60, "Admin operations per minute"),
        
        # General API - default limits
        "/api/*": RateLimit(100, 60, "General API requests per minute"),
    }
    
    # User-based quotas (per hour)
    USER_QUOTAS = {
        "user": {"requests": 1000, "ai_calls": 50},
        "premium": {"requests": 5000, "ai_calls": 200},
        "admin": {"requests": 10000, "ai_calls": 1000},
    }
    
    def __init__(self):
        self.user_buckets: Dict[str, Dict[str, TokenBucket]] = defaultdict(dict)
        self.ip_counters: Dict[str, Dict[str, SlidingWindowCounter]] = defaultdict(dict)
        self.user_quotas: Dict[str, Dict[str, int]] = defaultdict(lambda: {"requests": 0, "ai_calls": 0})
        self.quota_reset_time: Dict[str, datetime] = {}
        
    def get_client_id(self, request: Request, user_id: Optional[str] = None) -> str:
        """Get client identifier (user_id or IP)"""
        if user_id:
            return f"user:{user_id}"
        
        # Get real IP address (handle proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def match_endpoint_pattern(self, path: str) -> Optional[RateLimit]:
        """Find matching rate limit for endpoint"""
        # Exact match first
        if path in self.DEFAULT_LIMITS:
            return self.DEFAULT_LIMITS[path]
        
        # Pattern matching (most specific first)
        patterns = sorted(self.DEFAULT_LIMITS.keys(), key=len, reverse=True)
        for pattern in patterns:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if path.startswith(prefix):
                    return self.DEFAULT_LIMITS[pattern]
        
        return None
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_id: Optional[str] = None, 
        user_role: str = "user",
        is_ai_call: bool = False
    ) -> bool:
        """
        Check if request is allowed based on rate limits and quotas
        Returns True if allowed, False if rate limited
        """
        client_id = self.get_client_id(request, user_id)
        endpoint = request.url.path
        
        try:
            # 1. Check endpoint-specific rate limits
            rate_limit = self.match_endpoint_pattern(endpoint)
            if rate_limit:
                if not await self._check_endpoint_limit(client_id, endpoint, rate_limit):
                    logger.warning(f"Rate limit exceeded for {client_id} on {endpoint}: {rate_limit.description}")
                    return False
            
            # 2. Check user quotas (if authenticated)
            if user_id:
                if not await self._check_user_quota(user_id, user_role, is_ai_call):
                    logger.warning(f"User quota exceeded for {user_id} (role: {user_role})")
                    return False
            
            # 3. Record successful request
            await self._record_request(client_id, endpoint, user_id, is_ai_call)
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request if rate limiter has issues
            return True
    
    async def _check_endpoint_limit(self, client_id: str, endpoint: str, rate_limit: RateLimit) -> bool:
        """Check endpoint-specific rate limit using token bucket"""
        bucket_key = f"{client_id}:{endpoint}"
        
        if bucket_key not in self.user_buckets[client_id]:
            # Create new token bucket
            self.user_buckets[client_id][bucket_key] = TokenBucket(
                capacity=rate_limit.requests,
                refill_rate=rate_limit.requests / rate_limit.window
            )
        
        bucket = self.user_buckets[client_id][bucket_key]
        return bucket.consume(1)
    
    async def _check_user_quota(self, user_id: str, user_role: str, is_ai_call: bool) -> bool:
        """Check hourly user quota"""
        now = datetime.now(timezone.utc)
        
        # Reset quota if hour has passed
        if user_id not in self.quota_reset_time or now - self.quota_reset_time[user_id] >= timedelta(hours=1):
            self.user_quotas[user_id] = {"requests": 0, "ai_calls": 0}
            self.quota_reset_time[user_id] = now
        
        quotas = self.USER_QUOTAS.get(user_role, self.USER_QUOTAS["user"])
        current = self.user_quotas[user_id]
        
        # Check request quota
        if current["requests"] >= quotas["requests"]:
            return False
        
        # Check AI call quota
        if is_ai_call and current["ai_calls"] >= quotas["ai_calls"]:
            return False
        
        return True
    
    async def _record_request(self, client_id: str, endpoint: str, user_id: Optional[str], is_ai_call: bool):
        """Record successful request for monitoring"""
        if user_id:
            self.user_quotas[user_id]["requests"] += 1
            if is_ai_call:
                self.user_quotas[user_id]["ai_calls"] += 1
    
    def get_quota_status(self, user_id: str, user_role: str) -> Dict[str, any]:
        """Get current quota status for user"""
        quotas = self.USER_QUOTAS.get(user_role, self.USER_QUOTAS["user"])
        current = self.user_quotas.get(user_id, {"requests": 0, "ai_calls": 0})
        
        return {
            "requests": {
                "used": current["requests"],
                "limit": quotas["requests"],
                "remaining": quotas["requests"] - current["requests"]
            },
            "ai_calls": {
                "used": current["ai_calls"],
                "limit": quotas["ai_calls"],
                "remaining": quotas["ai_calls"] - current["ai_calls"]
            },
            "reset_in_seconds": 3600 - (datetime.now(timezone.utc) - self.quota_reset_time.get(user_id, datetime.now(timezone.utc))).seconds
        }

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

class RateLimitExceeded(HTTPException):
    """Rate limit exceeded exception"""
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)}
        )
