"""
Sub-Agent API - Emergent-Style Specialized Agents
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..core.sub_agents import sub_agent_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class IntegrationRequest(BaseModel):
    integration_name: str
    constraints: Optional[str] = None

class TroubleshootRequest(BaseModel):
    error_message: str
    component: str  # "backend", "frontend", "database", etc.
    recent_actions: Optional[str] = None

@router.post("/integration")
async def get_integration_playbook(request: IntegrationRequest) -> Dict[str, Any]:
    """
    Get integration playbook from Integration Expert
    """
    try:
        logger.info(f"📚 Integration request: {request.integration_name}")
        
        playbook = sub_agent_manager.call_integration_expert(request.integration_name)
        
        return {
            "status": "success",
            "integration": request.integration_name,
            "playbook": playbook,
            "constraints": request.constraints
        }
        
    except Exception as e:
        logger.error(f"Integration expert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration/list")
async def list_integrations():
    """List available integrations"""
    integrations = sub_agent_manager.integration_expert.list_available_integrations()
    return {
        "total": len(integrations),
        "integrations": integrations
    }

@router.get("/integration/search")
async def search_integrations(query: str):
    """Search for integrations"""
    results = sub_agent_manager.integration_expert.search_integrations(query)
    return {
        "query": query,
        "results": results
    }

@router.post("/troubleshoot")
async def troubleshoot_issue(request: TroubleshootRequest) -> Dict[str, Any]:
    """
    Troubleshoot issue using Troubleshooting Agent
    """
    try:
        logger.info(f"🔍 Troubleshoot request: {request.component}")
        
        analysis = sub_agent_manager.call_troubleshooting_agent(
            error=request.error_message,
            component=request.component
        )
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Troubleshooting agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_agents():
    """List all available sub-agents"""
    agents = sub_agent_manager.list_available_agents()
    return {
        "total": len(agents),
        "agents": agents
    }
