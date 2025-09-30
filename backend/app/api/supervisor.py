"""
Supervisor API - Service Management & Monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..core.supervisor_manager import supervisor_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class ServiceActionRequest(BaseModel):
    service: str
    action: str  # "start", "stop", "restart"

class LogRequest(BaseModel):
    service: str
    log_type: str = "out"  # "out" or "err"
    lines: int = 50
    grep_pattern: Optional[str] = None

@router.get("/status")
async def get_status(service: Optional[str] = None):
    """
    Get service status
    """
    try:
        result = supervisor_manager.get_service_status(service)
        return result
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action")
async def service_action(request: ServiceActionRequest) -> Dict[str, Any]:
    """
    Perform action on service (start/stop/restart)
    """
    try:
        if request.action == "restart":
            result = supervisor_manager.restart_service(request.service)
        elif request.action == "start":
            result = supervisor_manager.start_service(request.service)
        elif request.action == "stop":
            result = supervisor_manager.stop_service(request.service)
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use: start, stop, restart")
        
        return result
        
    except Exception as e:
        logger.error(f"Service action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs")
async def get_logs(request: LogRequest) -> Dict[str, Any]:
    """
    Get service logs
    """
    try:
        result = supervisor_manager.get_service_logs(
            service=request.service,
            log_type=request.log_type,
            lines=request.lines,
            grep_pattern=request.grep_pattern
        )
        return result
        
    except Exception as e:
        logger.error(f"Logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health():
    """
    Get comprehensive health status
    """
    try:
        health_data = supervisor_manager.get_all_services_health()
        report = supervisor_manager.generate_health_report(health_data)
        
        return {
            'health_data': health_data,
            'report': report
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
async def list_services():
    """
    List all available services
    """
    return {
        'services': supervisor_manager.SERVICES
    }
