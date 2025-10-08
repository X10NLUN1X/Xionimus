"""
Rate Limiting Management API
Provides endpoints for monitoring and managing rate limits
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..core.rate_limiter import rate_limiter
from ..core.auth import get_current_user, get_current_admin_user, User

router = APIRouter()

class QuotaStatus(BaseModel):
    """User quota status response"""
    requests: Dict[str, int]
    ai_calls: Dict[str, int] 
    reset_in_seconds: int
    user_role: str

class RateLimitInfo(BaseModel):
    """Rate limit information"""
    endpoint: str
    limit: int
    window_seconds: int
    description: str

@router.get("/quota", response_model=QuotaStatus)
async def get_user_quota(current_user: User = Depends(get_current_user)):
    """Get current user's quota status"""
    quota_status = rate_limiter.get_quota_status(current_user.user_id, current_user.role)
    
    return QuotaStatus(
        requests=quota_status["requests"],
        ai_calls=quota_status["ai_calls"],
        reset_in_seconds=quota_status["reset_in_seconds"],
        user_role=current_user.role
    )

@router.get("/limits")
async def get_rate_limits():
    """Get all configured rate limits (public endpoint)"""
    limits = []
    
    for endpoint, limit_config in rate_limiter.DEFAULT_LIMITS.items():
        limits.append(RateLimitInfo(
            endpoint=endpoint,
            limit=limit_config.requests,
            window_seconds=limit_config.window,
            description=limit_config.description
        ))
    
    return {
        "rate_limits": limits,
        "user_quotas": rate_limiter.USER_QUOTAS
    }

@router.get("/stats")
async def get_rate_limit_stats(admin_user: User = Depends(get_current_admin_user)):
    """Get rate limiting statistics (admin only)"""
    
    # Count active users and buckets
    active_users = len([uid for uid in rate_limiter.user_quotas.keys() if rate_limiter.user_quotas[uid]["requests"] > 0])
    active_buckets = sum(len(buckets) for buckets in rate_limiter.user_buckets.values())
    
    # Top users by request count
    top_users = []
    for user_id, quota in rate_limiter.user_quotas.items():
        if quota["requests"] > 0:
            top_users.append({
                "user_id": user_id,
                "requests": quota["requests"],
                "ai_calls": quota["ai_calls"]
            })
    
    top_users.sort(key=lambda x: x["requests"], reverse=True)
    
    return {
        "summary": {
            "active_users": active_users,
            "active_buckets": active_buckets,
            "total_quotas_tracked": len(rate_limiter.user_quotas)
        },
        "top_users": top_users[:10],
        "quotas_by_role": rate_limiter.USER_QUOTAS
    }

@router.post("/reset/{user_id}")
async def reset_user_rate_limits(
    user_id: str,
    admin_user: User = Depends(get_current_admin_user)
):
    """Reset rate limits for a specific user (admin only)"""
    
    # Clear user quotas
    if user_id in rate_limiter.user_quotas:
        old_quotas = rate_limiter.user_quotas[user_id].copy()
        rate_limiter.user_quotas[user_id] = {"requests": 0, "ai_calls": 0}
        
        # Clear user buckets
        user_key = f"user:{user_id}"
        if user_key in rate_limiter.user_buckets:
            bucket_count = len(rate_limiter.user_buckets[user_key])
            del rate_limiter.user_buckets[user_key]
        else:
            bucket_count = 0
        
        # Reset quota timer
        if user_id in rate_limiter.quota_reset_time:
            del rate_limiter.quota_reset_time[user_id]
        
        return {
            "success": True,
            "user_id": user_id,
            "cleared_quotas": old_quotas,
            "cleared_buckets": bucket_count,
            "reset_by": admin_user.username
        }
    
    return {
        "success": False,
        "error": "User not found in rate limit system",
        "user_id": user_id
    }

@router.get("/health")
async def rate_limiter_health():
    """Health check for rate limiting system"""
    try:
        # Test basic functionality
        from datetime import datetime
        test_time = datetime.now()
        
        stats = {
            "status": "healthy",
            "timestamp": test_time.isoformat(),
            "active_users": len(rate_limiter.user_quotas),
            "active_buckets": sum(len(buckets) for buckets in rate_limiter.user_buckets.values()),
            "memory_usage": {
                "user_quotas_count": len(rate_limiter.user_quotas),
                "user_buckets_count": len(rate_limiter.user_buckets),
                "quota_timers_count": len(rate_limiter.quota_reset_time)
            }
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Rate limiter health check failed: {str(e)}"
        )