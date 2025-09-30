"""
Rate Limiting Middleware
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

from ..core.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in ['/api/health', '/docs', '/openapi.json', '/redoc']:
            return await call_next(request)
        
        # Get identifier (IP address or user ID if authenticated)
        identifier = request.client.host if request.client else 'unknown'
        
        # Check rate limit
        allowed, info = rate_limiter.is_allowed(
            identifier=identifier,
            endpoint=request.url.path
        )
        
        if not allowed:
            logger.warning(
                f"⚠️ Rate limit exceeded: {identifier} -> {request.url.path}"
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'Rate limit exceeded',
                    'message': f"Too many requests. Retry after {info['retry_after']} seconds",
                    'limit': info['limit'],
                    'reset': info['reset'],
                    'retry_after': info['retry_after']
                },
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': str(info['remaining']),
                    'X-RateLimit-Reset': str(info['reset']),
                    'Retry-After': str(info['retry_after'])
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        if info:
            response.headers['X-RateLimit-Limit'] = str(info['limit'])
            response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
            response.headers['X-RateLimit-Reset'] = str(info['reset'])
        
        return response
