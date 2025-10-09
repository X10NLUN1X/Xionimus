"""Multi-Agent System API endpoints"""
import logging
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Depends, Request
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
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/multi-agents", tags=["multi-agents"])

# Global orchestrator instance (without API keys for /types endpoint)
_orchestrator = None


def get_orchestrator(api_keys: Optional[Dict[str, str]] = None):
    """
    Get or create agent orchestrator instance
    
    Args:
        api_keys: Optional dictionary of API keys for agent initialization
        
    Returns:
        AgentOrchestrator instance
    """
    global _orchestrator
    
    # If API keys are provided, always create a new orchestrator
    if api_keys:
        logger.info("Creating orchestrator with dynamic API keys")
        return AgentOrchestrator(mongodb_client=None, api_keys=api_keys)
    
    # Otherwise, use global singleton (for endpoints like /types)
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(mongodb_client=None)
        logger.info("Agent orchestrator initialized without persistence (singleton)")
    
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
        # Pass API keys to orchestrator if provided
        orchestrator = get_orchestrator(api_keys=request.api_keys)
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
        # Pass API keys to orchestrator if provided
        orchestrator = get_orchestrator(api_keys=request.api_keys)
        agent = orchestrator._get_or_create_agent(request.agent_type)
        
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
async def get_agents_health(full_check: bool = False):
    """
    Get health status of all agents
    
    Args:
        full_check: If True, performs full health check with API calls (slower)
                   If False, performs fast configuration check only (default)
    
    Returns:
        Health status for all agents
    """
    try:
        orchestrator = get_orchestrator()
        
        if full_check:
            health_status = await orchestrator.get_agent_health()
        else:
            # Fast health check without API calls
            agent_health = {}
            for agent_type, agent in orchestrator.agents.items():
                agent_health[agent_type.value] = await agent.fast_health_check()
            
            health_status = {
                "status": "healthy",
                "total_agents": len(orchestrator.agents),
                "agents": agent_health
            }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{agent_type}")
async def get_agent_health(agent_type: AgentType, full_check: bool = False):
    """
    Get health status of a specific agent
    
    Args:
        agent_type: Type of agent to check
        full_check: If True, performs full health check with API call (slower)
        
    Returns:
        Health status for the specified agent
    """
    try:
        orchestrator = get_orchestrator()
        agent = orchestrator.agents.get(agent_type)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_type}")
        
        if full_check:
            health = await agent.health_check()
        else:
            health = await agent.fast_health_check()
            
        return health
        
    except Exception as e:
        logger.error(f"Health check failed for {agent_type}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", dependencies=[])
async def get_agent_types(request: Request):
    """
    Get list of available agent types with their configurations
    PUBLIC ENDPOINT - No authentication required
    
    Returns:
        List of agent types and their details
    """
    try:
        orchestrator = get_orchestrator()
        
        agent_info = []
        for agent_type, agent in orchestrator.agents.items():
            try:
                agent_info.append({
                    "type": agent_type.value,
                    "provider": agent.provider.value,
                    "model": agent.model,
                    "timeout": agent.timeout,
                    "description": agent.get_system_prompt()[:100] + "..."
                })
            except Exception as agent_error:
                logger.warning(f"Could not get info for agent {agent_type.value}: {agent_error}")
                # Add basic info even if agent is not fully initialized
                agent_info.append({
                    "type": agent_type.value,
                    "provider": "unknown",
                    "model": "unknown",
                    "timeout": 60,
                    "description": f"Agent {agent_type.value} (not fully configured)"
                })
        
        return {
            "total_agents": len(agent_info),
            "agents": agent_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent types: {str(e)}", exc_info=True)
        # Return fallback static agent list if orchestrator fails
        logger.warning("⚠️ Returning fallback agent list due to orchestrator error")
        fallback_agents = [
            {
                "type": "research",
                "provider": "perplexity",
                "model": "sonar-pro",
                "timeout": 60,
                "description": "Research agent for information gathering (offline)"
            },
            {
                "type": "code_review",
                "provider": "claude",
                "model": "claude-3-5-sonnet-20241022",
                "timeout": 120,
                "description": "Code review agent for quality analysis (offline)"
            },
            {
                "type": "testing",
                "provider": "openai",
                "model": "gpt-4o",
                "timeout": 90,
                "description": "Testing agent for test generation (offline)"
            }
        ]
        return {
            "total_agents": len(fallback_agents),
            "agents": fallback_agents,
            "fallback": True,
            "error": str(e)
        }


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
