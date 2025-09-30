"""
Rate Limiter - Request Rate Limiting
Protects APIs from abuse
"""
import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store: {identifier: [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Limits per endpoint
        self.limits = {
            '/api/chat': {'requests': 60, 'window': 60},  # 60 requests per minute
            '/api/testing/run': {'requests': 10, 'window': 60},  # 10 tests per minute
            '/api/bulk/write': {'requests': 20, 'window': 60},  # 20 bulk operations per minute
            'default': {'requests': 100, 'window': 60}  # 100 requests per minute
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
