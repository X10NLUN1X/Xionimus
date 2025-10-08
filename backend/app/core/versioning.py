"""
API Versioning System

Provides backward-compatible API versioning with deprecation warnings.
Supports gradual migration from /api/* to /api/v1/*
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIVersion:
    """API Version constants"""
    V1 = "v1"
    CURRENT = V1  # Current recommended version
    DEPRECATED_UNVERSIONED = "unversioned"  # Legacy /api/* without version


class DeprecationInfo:
    """Information about deprecated API endpoints"""
    
    # Deprecation sunset date (when old API will be removed)
    SUNSET_DATE = datetime(2025, 12, 31)  # End of 2025
    
    # Deprecation warning message
    WARNING_MESSAGE = (
        "This API endpoint is deprecated. "
        f"Please migrate to /api/{APIVersion.CURRENT}/* before {SUNSET_DATE.strftime('%Y-%m-%d')}. "
        "See documentation: /docs"
    )
    
    @classmethod
    def get_sunset_header(cls) -> str:
        """Returns sunset date in HTTP date format"""
        return cls.SUNSET_DATE.strftime("%a, %d %b %Y %H:%M:%S GMT")


class APIVersioningMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API versioning with backward compatibility
    
    Features:
    - Redirects /api/* to /api/v1/* internally (backward compatibility)
    - Adds deprecation headers for unversioned endpoints
    - Logs usage statistics for migration tracking
    """
    
    def __init__(self, app, enable_redirect: bool = True, log_usage: bool = True):
        """
        Args:
            app: FastAPI application
            enable_redirect: Enable automatic redirect from /api/* to /api/v1/*
            log_usage: Log API version usage for tracking
        """
        super().__init__(app)
        self.enable_redirect = enable_redirect
        self.log_usage = log_usage
        self.usage_stats = {
            "v1": 0,
            "unversioned": 0,
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle API versioning for each request"""
        
        path = request.url.path
        
        # Skip non-API paths
        if not path.startswith("/api/"):
            return await call_next(request)
        
        # Check if path is versioned
        is_versioned = self._is_versioned_path(path)
        
        if not is_versioned and self.enable_redirect:
            # Unversioned path like /api/auth/login
            # Redirect internally to /api/v1/auth/login
            new_path = self._get_versioned_path(path)
            
            # Log usage
            if self.log_usage:
                self.usage_stats["unversioned"] += 1
                if self.usage_stats["unversioned"] % 100 == 1:  # Log every 100 requests
                    logger.warning(
                        f"📊 Unversioned API usage: {self.usage_stats['unversioned']} requests "
                        f"(v1: {self.usage_stats['v1']})"
                    )
            
            # Modify request path for internal routing
            request.scope["path"] = new_path
            
            # Process request
            response = await call_next(request)
            
            # Add deprecation headers
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = DeprecationInfo.get_sunset_header()
            response.headers["Link"] = f'</api/{APIVersion.CURRENT}{path[4:]}>; rel="successor-version"'
            response.headers["Warning"] = f'299 - "{DeprecationInfo.WARNING_MESSAGE}"'
            
            return response
        
        elif is_versioned:
            # Versioned path like /api/v1/auth/login
            if self.log_usage:
                version = self._extract_version(path)
                if version in self.usage_stats:
                    self.usage_stats[version] += 1
            
            # Process normally
            response = await call_next(request)
            
            # Add version header
            response.headers["API-Version"] = APIVersion.CURRENT
            
            return response
        
        else:
            # Versioned path but redirect disabled
            return await call_next(request)
    
    def _is_versioned_path(self, path: str) -> bool:
        """Check if path includes version number"""
        # Check for /api/v1/, /api/v2/, etc.
        parts = path.split("/")
        return len(parts) > 2 and parts[2].startswith("v") and parts[2][1:].isdigit()
    
    def _extract_version(self, path: str) -> str:
        """Extract version from path like /api/v1/..."""
        parts = path.split("/")
        if len(parts) > 2 and parts[2].startswith("v"):
            return parts[2]
        return "unknown"
    
    def _get_versioned_path(self, path: str) -> str:
        """
        Convert unversioned path to versioned path
        
        Example:
            /api/auth/login -> /api/v1/auth/login
        """
        # Remove /api prefix
        without_prefix = path[4:]  # Remove '/api'
        
        # Add version
        return f"/api/{APIVersion.CURRENT}{without_prefix}"
    
    def get_stats(self) -> dict:
        """Get API version usage statistics"""
        total = sum(self.usage_stats.values())
        
        return {
            "total_requests": total,
            "by_version": self.usage_stats.copy(),
            "migration_progress": {
                "v1_percentage": round(self.usage_stats["v1"] / total * 100, 2) if total > 0 else 0,
                "unversioned_percentage": round(self.usage_stats["unversioned"] / total * 100, 2) if total > 0 else 0,
            }
        }


def create_versioned_prefix(version: str = APIVersion.CURRENT) -> str:
    """
    Helper function to create versioned API prefix
    
    Args:
        version: API version (default: current)
        
    Returns:
        str: Versioned prefix like "/api/v1"
    """
    return f"/api/{version}"


# Helper for gradual migration
def supports_both_versions(router_prefix: str) -> list:
    """
    Returns list of prefixes for backward compatibility
    
    Example:
        prefixes = supports_both_versions("/auth")
        # Returns: ["/api/v1/auth", "/api/auth"]
    """
    return [
        f"/api/{APIVersion.CURRENT}{router_prefix}",
        f"/api{router_prefix}",  # Legacy support
    ]
