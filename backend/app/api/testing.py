"""
Testing API - Automated testing endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..core.testing_agent import testing_agent

logger = logging.getLogger(__name__)
router = APIRouter()

class TestRequest(BaseModel):
    test_type: str  # "backend", "frontend", "all"
    endpoints: Optional[list] = None

@router.post("/run")
async def run_tests(request: TestRequest) -> Dict[str, Any]:
    """
    Run automated tests
    """
    try:
        logger.info(f"🧪 Starting tests: {request.test_type}")
        
        backend_results = None
        frontend_results = None
        
        if request.test_type in ["backend", "all"]:
            backend_results = await testing_agent.run_backend_test_suite()
        
        if request.test_type in ["frontend", "all"]:
            frontend_results = await testing_agent.run_frontend_test_suite()
        
        # Generate report
        report = ""
        if backend_results and frontend_results:
            report = testing_agent.generate_test_report(backend_results, frontend_results)
        elif backend_results:
            report = f"# Backend Test Report\n\n{backend_results['passed']}/{backend_results['total_tests']} passed"
        elif frontend_results:
            report = f"# Frontend Test Report\n\n{frontend_results['passed']}/{frontend_results['total_tests']} passed"
        
        return {
            "status": "completed",
            "backend": backend_results,
            "frontend": frontend_results,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Testing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_test_status():
    """Get testing agent status"""
    return {
        "status": "ready",
        "backend_url": testing_agent.backend_url,
        "frontend_url": testing_agent.frontend_url,
        "recent_tests": len(testing_agent.test_results)
    }
