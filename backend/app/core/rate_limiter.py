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
    
    def is_allowed(
        self, 
        identifier: str,
        endpoint: str
    ) -> tuple[bool, Optional[Dict[str, any]]]:
        """
        Check if request is allowed
        Returns (allowed, info)
        """
        now = time.time()
        
        # Get limit for endpoint
        limit_config = self.limits.get(endpoint, self.limits['default'])
        max_requests = limit_config['requests']
        window_seconds = limit_config['window']
        
        # Clean old requests
        cutoff_time = now - window_seconds
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]
        
        # Count recent requests
        recent_requests = len(self.requests[identifier])
        
        # Check if limit exceeded
        if recent_requests >= max_requests:
            reset_time = self.requests[identifier][0] + window_seconds
            retry_after = int(reset_time - now)
            
            logger.warning(
                f"⚠️ Rate limit exceeded for {identifier} on {endpoint}: "
                f"{recent_requests}/{max_requests}"
            )
            
            return False, {
                'allowed': False,
                'limit': max_requests,
                'remaining': 0,
                'reset': int(reset_time),
                'retry_after': retry_after
            }
        
        # Add current request
        self.requests[identifier].append(now)
        
        remaining = max_requests - (recent_requests + 1)
        reset_time = now + window_seconds
        
        return True, {
            'allowed': True,
            'limit': max_requests,
            'remaining': remaining,
            'reset': int(reset_time)
        }
    
    def get_usage_stats(self, identifier: str) -> Dict[str, any]:
        """
        Get usage statistics for identifier
        """
        now = time.time()
        
        # Count requests in last minute
        last_minute = now - 60
        recent_requests = sum(
            1 for req_time in self.requests[identifier]
            if req_time > last_minute
        )
        
        # Count requests in last hour
        last_hour = now - 3600
        hourly_requests = sum(
            1 for req_time in self.requests[identifier]
            if req_time > last_hour
        )
        
        return {
            'identifier': identifier,
            'requests_last_minute': recent_requests,
            'requests_last_hour': hourly_requests,
            'total_tracked': len(self.requests[identifier]),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_user(self, identifier: str) -> Dict[str, any]:
        """
        Reset rate limit for user (admin function)
        """
        if identifier in self.requests:
            count = len(self.requests[identifier])
            del self.requests[identifier]
            logger.info(f"✅ Reset rate limit for {identifier} ({count} requests cleared)")
            
            return {
                'success': True,
                'identifier': identifier,
                'requests_cleared': count
            }
        
        return {
            'success': False,
            'error': 'No requests found for identifier'
        }
    
    def get_all_stats(self) -> Dict[str, any]:
        """
        Get statistics for all users
        """
        now = time.time()
        last_minute = now - 60
        
        stats = []
        for identifier, requests in self.requests.items():
            recent = sum(1 for req_time in requests if req_time > last_minute)
            stats.append({
                'identifier': identifier,
                'recent_requests': recent,
                'total_tracked': len(requests)
            })
        
        # Sort by recent requests
        stats.sort(key=lambda x: x['recent_requests'], reverse=True)
        
        return {
            'total_identifiers': len(self.requests),
            'limits': self.limits,
            'top_users': stats[:10],
            'timestamp': datetime.now().isoformat()
        }


# Global instance
rate_limiter = RateLimiter()
