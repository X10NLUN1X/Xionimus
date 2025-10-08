"""
Monitoring API Endpoints
Provides access to error monitoring, metrics, and system health
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.error_monitoring import error_monitor
from app.core.auth import get_current_user
from app.models.user_models import User

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/errors/summary")
async def get_error_summary(
    minutes: int = Query(default=60, ge=1, le=1440, description="Time window in minutes"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get error summary for the specified time window
    
    Requires authentication. Admin users get full access.
    """
    summary = error_monitor.get_error_summary(minutes=minutes)
    
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "data": summary
    }


@router.get("/errors/details")
async def get_error_details(
    limit: int = Query(default=50, ge=1, le=500, description="Maximum number of errors"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    error_type: Optional[str] = Query(default=None, description="Filter by error type"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed error records with optional filters
    
    Requires authentication.
    """
    errors = error_monitor.get_error_details(
        limit=limit,
        severity=severity,
        error_type=error_type
    )
    
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "count": len(errors),
        "data": errors
    }


@router.post("/errors/export")
async def export_error_report(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export comprehensive error report to file
    
    Requires authentication. Admin only.
    """
    # Check if user is admin
    if not current_user.role == 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    filepath = f"/tmp/error_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report = error_monitor.export_error_report(filepath)
    
    return {
        "status": "success",
        "message": f"Error report exported to {filepath}",
        "summary": report.get('summary_1h', {})
    }


@router.delete("/errors/cleanup")
async def cleanup_old_errors(
    days: int = Query(default=7, ge=1, le=90, description="Keep errors newer than N days"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clean up old error records
    
    Requires authentication. Admin only.
    """
    # Check if user is admin
    if not current_user.role == 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cleared_count = error_monitor.clear_old_errors(days=days)
    
    return {
        "status": "success",
        "message": f"Cleared {cleared_count} old error records",
        "days": days
    }


@router.get("/health/detailed")
async def get_detailed_health(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed system health including recent errors
    
    Requires authentication.
    """
    # Get error summary for last hour
    error_summary = error_monitor.get_error_summary(minutes=60)
    
    # Determine overall health status
    total_errors = error_summary.get('total_errors', 0)
    critical_errors = error_summary.get('by_severity', {}).get('critical', 0)
    
    if critical_errors > 0:
        health_status = "critical"
    elif total_errors > 50:
        health_status = "degraded"
    elif total_errors > 10:
        health_status = "warning"
    else:
        health_status = "healthy"
    
    return {
        "status": health_status,
        "timestamp": datetime.utcnow().isoformat(),
        "error_summary": error_summary,
        "recommendations": _get_health_recommendations(health_status, error_summary)
    }


def _get_health_recommendations(status: str, summary: Dict[str, Any]) -> list:
    """Generate health recommendations based on status"""
    recommendations = []
    
    if status == "critical":
        recommendations.append("🚨 Critical errors detected. Immediate action required.")
        recommendations.append("Check error details and logs immediately.")
    
    if status == "degraded":
        recommendations.append("⚠️ High error rate detected. Investigation recommended.")
    
    most_common = summary.get('most_common_error')
    if most_common:
        recommendations.append(f"Most common error: {most_common}")
    
    by_endpoint = summary.get('by_endpoint', {})
    if by_endpoint:
        problematic_endpoint = max(by_endpoint.items(), key=lambda x: x[1])
        recommendations.append(f"Endpoint with most errors: {problematic_endpoint[0]} ({problematic_endpoint[1]} errors)")
    
    return recommendations
