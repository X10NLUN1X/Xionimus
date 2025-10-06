"""
API Version Information Endpoint

Provides version information and migration guidance.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional
from app.core.versioning import APIVersion, DeprecationInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class VersionInfo(BaseModel):
    """API Version Information"""
    current_version: str
    deprecated_versions: list[str]
    sunset_date: str
    migration_guide_url: str


class VersionStatsResponse(BaseModel):
    """API Version Usage Statistics"""
    total_requests: int
    by_version: Dict[str, int]
    migration_progress: Dict[str, float]


@router.get("/version", response_model=VersionInfo, tags=["meta"], dependencies=[])
async def get_version_info():
    """
    Get API version information
    
    Returns information about current and deprecated API versions,
    including sunset dates and migration guidance.
    """
    return VersionInfo(
        current_version=APIVersion.CURRENT,
        deprecated_versions=[APIVersion.DEPRECATED_UNVERSIONED],
        sunset_date=DeprecationInfo.SUNSET_DATE.strftime("%Y-%m-%d"),
        migration_guide_url="/docs#/v1"
    )


@router.get("/version/stats", response_model=VersionStatsResponse, tags=["meta"])
async def get_version_stats(request: Request):
    """
    Get API version usage statistics
    
    Requires admin access. Returns statistics about API version usage
    for tracking migration progress.
    """
    # Get middleware instance
    versioning_middleware = None
    for middleware in request.app.user_middleware:
        if hasattr(middleware, 'cls'):
            if middleware.cls.__name__ == "APIVersioningMiddleware":
                versioning_middleware = middleware
                break
    
    if versioning_middleware:
        # In production, you'd store middleware instance reference
        # For now, return mock data
        return VersionStatsResponse(
            total_requests=0,
            by_version={"v1": 0, "unversioned": 0},
            migration_progress={"v1_percentage": 0.0, "unversioned_percentage": 0.0}
        )
    
    return VersionStatsResponse(
        total_requests=0,
        by_version={"v1": 0, "unversioned": 0},
        migration_progress={"v1_percentage": 0.0, "unversioned_percentage": 0.0}
    )


@router.get("/migration-guide", tags=["meta"])
async def get_migration_guide():
    """
    Get API migration guide
    
    Returns comprehensive guide for migrating from legacy /api/*
    endpoints to versioned /api/v1/* endpoints.
    """
    return {
        "title": "API Migration Guide",
        "overview": "Migrate from legacy /api/* to versioned /api/v1/* endpoints",
        "timeline": {
            "announcement": "2025-01-06",
            "sunset_date": DeprecationInfo.SUNSET_DATE.strftime("%Y-%m-%d"),
            "migration_window_days": (DeprecationInfo.SUNSET_DATE - datetime.now()).days
        },
        "changes": {
            "url_pattern": {
                "old": "/api/{endpoint}",
                "new": "/api/v1/{endpoint}",
                "example": {
                    "old": "/api/auth/login",
                    "new": "/api/v1/auth/login"
                }
            },
            "headers": {
                "response_headers": {
                    "API-Version": "v1 (new versioned endpoints)",
                    "Deprecation": "true (on legacy endpoints)",
                    "Sunset": f"{DeprecationInfo.get_sunset_header()} (on legacy endpoints)",
                    "Link": "Points to successor version (on legacy endpoints)"
                }
            }
        },
        "migration_steps": [
            {
                "step": 1,
                "action": "Audit API calls",
                "description": "Identify all /api/* calls in your application"
            },
            {
                "step": 2,
                "action": "Update base URL",
                "description": "Change API_BASE_URL from '/api' to '/api/v1'"
            },
            {
                "step": 3,
                "action": "Test thoroughly",
                "description": "Verify all endpoints work with new URLs"
            },
            {
                "step": 4,
                "action": "Deploy",
                "description": "Roll out changes to production"
            },
            {
                "step": 5,
                "action": "Monitor",
                "description": "Check logs for remaining legacy API usage"
            }
        ],
        "code_examples": {
            "javascript": {
                "before": "const API_BASE = '/api';\nfetch(`${API_BASE}/auth/login`, {...})",
                "after": "const API_BASE = '/api/v1';\nfetch(`${API_BASE}/auth/login`, {...})"
            },
            "python": {
                "before": "BASE_URL = 'http://localhost:8001/api'\nrequests.post(f'{BASE_URL}/auth/login', ...)",
                "after": "BASE_URL = 'http://localhost:8001/api/v1'\nrequests.post(f'{BASE_URL}/auth/login', ...)"
            },
            "react": {
                "before": "// .env\nREACT_APP_API_URL=http://localhost:8001/api",
                "after": "// .env\nREACT_APP_API_URL=http://localhost:8001/api/v1"
            }
        },
        "faq": [
            {
                "question": "Will my app break if I don't migrate?",
                "answer": f"No, legacy endpoints will continue to work until {DeprecationInfo.SUNSET_DATE.strftime('%Y-%m-%d')}. However, they will return deprecation headers."
            },
            {
                "question": "What happens after sunset date?",
                "answer": "Legacy /api/* endpoints will be removed and return 410 Gone status."
            },
            {
                "question": "Can I use both versions during migration?",
                "answer": "Yes! Both versions are fully supported during the migration window."
            },
            {
                "question": "Are there any breaking changes in v1?",
                "answer": "No, v1 is functionally identical to legacy endpoints. Only the URL pattern changed."
            }
        ],
        "support": {
            "documentation": "/docs",
            "changelog": "/api/v1/version",
            "contact": "See README.md for support information"
        }
    }
