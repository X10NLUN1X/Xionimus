"""Multi-Agent System API endpoints"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json

from ..models.agent_models import (
    AgentType,
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentHealthStatus
)
from ..core.agent_orchestrator import AgentOrchestrator
from ..core.database import get_mongo_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/multi-agents", tags=["multi-agents"])

# Global orchestrator instance
_orchestrator = None


def get_orchestrator():
    """Get or create agent orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        try:
            mongo_client = get_mongo_client()
            _orchestrator = AgentOrchestrator(mongodb_client=mongo_client)
        except Exception as e:
            logger.warning(f"MongoDB not available, using orchestrator without persistence: {e}")
            _orchestrator = AgentOrchestrator(mongodb_client=None)
    return _orchestrator


@router.post("/execute", response_model=AgentExecutionResult)
async def execute_agent(request: AgentExecutionRequest):
    """
    Execute a single agent
    
    Args:
        request: Agent execution request with type and input data
        
    Returns:
        AgentExecutionResult with execution details and output
    """
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.execute_agent(request)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/execute/stream")
async def execute_agent_streaming(request: AgentExecutionRequest):
    """
    Execute agent with streaming updates (Server-Sent Events)
    
    Args:
        request: Agent execution request
        
    Returns:
        EventSourceResponse with streaming updates
    """
    try:
        orchestrator = get_orchestrator()
        agent = orchestrator.agents.get(request.agent_type)
        
        if not agent:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")
        
        async def event_generator():
            """Generate SSE events from agent stream"""
            try:
                import uuid
                execution_id = str(uuid.uuid4())
                
                async for chunk in agent.execute_streaming(
                    input_data=request.input_data,
                    execution_id=execution_id,
                    session_id=request.session_id,
                    user_id=request.user_id,
                    options=request.options
                ):
                    # Convert chunk to SSE format
                    data = {
                        "execution_id": chunk.execution_id,
                        "agent_type": chunk.agent_type.value,
                        "chunk_type": chunk.chunk_type,
                        "data": chunk.data,
                        "timestamp": chunk.timestamp.isoformat(),
                        "sequence_number": chunk.sequence_number
                    }
                    
                    yield {
                        "event": "agent_update",
                        "data": json.dumps(data)
                    }
                    
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}", exc_info=True)
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)})
                }
        
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        logger.error(f"Streaming setup failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_agents_health():
    """
    Get health status of all agents
    
    Returns:
        Health status for all agents
    """
    try:
        orchestrator = get_orchestrator()
        health_status = await orchestrator.get_agent_health()
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{agent_type}")
async def get_agent_health(agent_type: AgentType):
    """
    Get health status of a specific agent
    
    Args:
        agent_type: Type of agent to check
        
    Returns:
        Health status for the specified agent
    """
    try:
        orchestrator = get_orchestrator()
        agent = orchestrator.agents.get(agent_type)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_type}")
        
        health = await agent.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Health check failed for {agent_type}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_agent_types():
    """
    Get list of available agent types with their configurations
    
    Returns:
        List of agent types and their details
    """
    try:
        orchestrator = get_orchestrator()
        
        agent_info = []
        for agent_type, agent in orchestrator.agents.items():
            agent_info.append({
                "type": agent_type.value,
                "provider": agent.provider.value,
                "model": agent.model,
                "timeout": agent.timeout,
                "description": agent.get_system_prompt()[:100] + "..."
            })
        
        return {
            "total_agents": len(agent_info),
            "agents": agent_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent types: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collaborative")
async def execute_collaborative_agents(
    primary_request: AgentExecutionRequest,
    strategy: str = "sequential"
):
    """
    Execute multiple agents in a collaborative workflow
    
    Args:
        primary_request: Primary agent execution request
        strategy: Collaboration strategy (sequential, parallel, conditional)
        
    Returns:
        Results from all agents in the workflow
    """
    try:
        if strategy not in ["sequential", "parallel", "conditional"]:
            raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy}")
        
        orchestrator = get_orchestrator()
        result = await orchestrator.execute_collaborative(
            primary_request=primary_request,
            collaboration_strategy=strategy
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Collaborative execution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_agent_metrics(
    agent_type: Optional[AgentType] = None,
    time_range_hours: int = 24
):
    """
    Get metrics for agents
    
    Args:
        agent_type: Specific agent type or None for all
        time_range_hours: Time range for metrics (default 24 hours)
        
    Returns:
        Agent metrics and statistics
    """
    try:
        orchestrator = get_orchestrator()
        metrics = await orchestrator.get_agent_metrics(
            agent_type=agent_type,
            time_range_hours=time_range_hours
        )
        
        return {
            "time_range_hours": time_range_hours,
            "agent_type": agent_type.value if agent_type else "all",
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
