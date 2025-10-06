# ⚠️ DEPRECATED: This file is no longer used
# Rate limiting middleware is currently disabled
# Kept for reference only - will be removed in future version
# Last known usage: Commented out in main.py


"""
Rate Limiting for API Protection
Prevents DoS, brute force, and API abuse
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# Create rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global default
    storage_uri="memory://"  # Use in-memory storage (upgrade to Redis for production)
)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add rate limit headers
        if hasattr(request.state, "view_rate_limit"):
            limit = request.state.view_rate_limit
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(
                getattr(request.state, "view_rate_limit_remaining", 0)
            )
            response.headers["X-RateLimit-Reset"] = str(
                getattr(request.state, "view_rate_limit_reset", 0)
            )
        
        return response

# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    # Authentication - strict limits to prevent brute force
    "auth_login": "5/minute",           # Max 5 login attempts per minute
    "auth_register": "3/hour",          # Max 3 registrations per hour
    
    # AI endpoints - prevent cost explosion
    "chat": "20/minute",                # Max 20 AI chats per minute
    "chat_stream": "10/minute",         # Max 10 streaming sessions per minute
    
    # File operations - prevent abuse
    "file_upload": "10/minute",         # Max 10 uploads per minute
    "file_download": "50/minute",       # More generous for downloads
    
    # GitHub operations
    "github_push": "5/minute",          # Max 5 pushes per minute
    
    # Read operations - more generous
    "read_operations": "100/minute",    # General reads
    
    # Admin/testing - very strict
    "admin": "10/minute",
}

def get_rate_limit(operation: str) -> str:
    """Get rate limit string for operation type"""
    return RATE_LIMITS.get(operation, "60/minute")

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded"""
    logger.warning(
        f"Rate limit exceeded: {request.client.host} on {request.url.path}"
    )
    
    return Response(
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down.",
                "retry_after": exc.detail
            }
        },
        status_code=429,
        headers={
            "Retry-After": str(exc.detail),
            "X-RateLimit-Limit": str(exc.detail)
        }
    )
