"""
Health Check & Monitoring Endpoints
Kubernetes-ready liveness and readiness probes
"""

from fastapi import APIRouter, Response, status
from typing import Dict, Any
import time
import sys
import psutil
from datetime import datetime

from app.core.database import get_database_health
from app.core.redis_client import get_redis_health
from app.core.mongo_db import get_mongo_health

router = APIRouter()


@router.get("/health/live", tags=["Health"])
async def liveness_probe() -> Dict[str, Any]:
    """
    Kubernetes liveness probe
    Returns 200 if the application is running
    
    This endpoint should respond quickly and only check if the application is alive.
    It should NOT check external dependencies.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - getattr(sys, 'start_time', time.time()))
    }


@router.get("/health/ready", tags=["Health"])
async def readiness_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes readiness probe
    Returns 200 if the application is ready to receive traffic
    
    Checks:
    - Database connectivity
    - Redis connectivity
    - MongoDB connectivity
    """
    checks = {}
    all_ready = True
    
    # Check PostgreSQL
    try:
        db_health = await get_database_health()
        checks["database"] = {
            "status": "ready" if db_health else "not_ready",
            "healthy": db_health
        }
        if not db_health:
            all_ready = False
    except Exception as e:
        checks["database"] = {
            "status": "error",
            "healthy": False,
            "error": str(e)
        }
        all_ready = False
    
    # Check Redis
    try:
        redis_health = await get_redis_health()
        checks["redis"] = {
            "status": "ready" if redis_health else "not_ready",
            "healthy": redis_health
        }
        if not redis_health:
            all_ready = False
    except Exception as e:
        checks["redis"] = {
            "status": "error",
            "healthy": False,
            "error": str(e)
        }
        all_ready = False
    
    # Check MongoDB (optional - don't fail readiness if not available)
    try:
        mongo_health = await get_mongo_health()
        checks["mongodb"] = {
            "status": "ready" if mongo_health else "not_ready",
            "healthy": mongo_health,
            "optional": True
        }
    except Exception as e:
        checks["mongodb"] = {
            "status": "error",
            "healthy": False,
            "error": str(e),
            "optional": True
        }
    
    # Set response status
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/health/startup", tags=["Health"])
async def startup_probe(response: Response) -> Dict[str, Any]:
    """
    Kubernetes startup probe
    Returns 200 when the application has finished starting up
    
    Similar to readiness probe but more lenient on timeouts
    """
    # For now, same as readiness
    return await readiness_probe(response)


@router.get("/health/metrics", tags=["Health"])
async def health_metrics() -> Dict[str, Any]:
    """
    Detailed health metrics for monitoring
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - getattr(sys, 'start_time', time.time())),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            },
            "platform": sys.platform,
            "python_version": sys.version
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }