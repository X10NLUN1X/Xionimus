"""Agent Orchestrator - Manages multi-agent system"""
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.agent_models import (
    AgentType,
    AgentExecution,
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentInteraction,
    AgentMetrics,
    AgentStatus
)
from .agents import (
    ResearchAgent,
    CodeReviewAgent,
    TestingAgent,
    DocumentationAgent,
    DebuggingAgent,
    SecurityAgent,
    PerformanceAgent,
    ForkAgent
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates multiple agents and manages their interactions
    Handles agent lifecycle, collaboration, and coordination
    """
    
    def __init__(self, mongodb_client=None):
        """
        Initialize agent orchestrator
        
        Args:
            mongodb_client: MongoDB client for storing execution history
        """
        self.mongodb = mongodb_client
        
        # Initialize all agents
        self.agents: Dict[AgentType, Any] = {
            AgentType.RESEARCH: ResearchAgent(),
            AgentType.CODE_REVIEW: CodeReviewAgent(),
            AgentType.TESTING: TestingAgent(),
            AgentType.DOCUMENTATION: DocumentationAgent(),
            AgentType.DEBUGGING: DebuggingAgent(),
            AgentType.SECURITY: SecurityAgent(),
            AgentType.PERFORMANCE: PerformanceAgent(),
            AgentType.FORK: ForkAgent()
        }
        
        logger.info(f"Initialized agent orchestrator with {len(self.agents)} agents")
    
    async def execute_agent(
        self,
        request: AgentExecutionRequest
    ) -> AgentExecutionResult:
        """
        Execute a single agent
        
        Args:
            request: Agent execution request
            
        Returns:
            AgentExecutionResult with execution details
        """
        execution_id = str(uuid.uuid4())
        agent_type = request.agent_type
        
        logger.info(f"Executing {agent_type.value} agent: {execution_id}")
        
        # Get agent instance
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Create execution record
        execution = AgentExecution(
            execution_id=execution_id,
            agent_type=agent_type,
            status=AgentStatus.PENDING,
            input_data=request.input_data,
            session_id=request.session_id,
            user_id=request.user_id,
            parent_execution_id=request.parent_execution_id,
            options=request.options,
            provider=agent.provider,
            model=agent.model
        )
        
        # Store initial execution record
        if self.mongodb:
            await self._store_execution(execution)
        
        try:
            # Execute agent
            execution.status = AgentStatus.RUNNING
            if self.mongodb:
                await self._update_execution(execution)
            
            result = await agent.execute(
                input_data=request.input_data,
                execution_id=execution_id,
                session_id=request.session_id,
                user_id=request.user_id,
                options=request.options
            )
            
            # Update execution record with results
            execution.status = result.status
            execution.output_data = result.output_data
            execution.error_message = result.error_message
            execution.completed_at = result.completed_at
            execution.duration_seconds = result.duration_seconds
            execution.token_usage = result.token_usage
            
            if self.mongodb:
                await self._update_execution(execution)
            
            logger.info(f"Completed {agent_type.value} execution: {execution_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent execution failed: {execution_id}", exc_info=True)
            
            execution.status = AgentStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            if self.mongodb:
                await self._update_execution(execution)
            
            raise
    
    async def execute_collaborative(
        self,
        primary_request: AgentExecutionRequest,
        collaboration_strategy: str = "sequential"
    ) -> Dict[str, Any]:
        """
        Execute multiple agents in a collaborative workflow
        
        Args:
            primary_request: Primary agent execution request
            collaboration_strategy: "sequential", "parallel", or "conditional"
            
        Returns:
            Dictionary with results from all agents
        """
        results = {}
        primary_result = None
        
        try:
            # Execute primary agent
            primary_result = await self.execute_agent(primary_request)
            results[primary_request.agent_type.value] = primary_result
            
            # Determine if collaboration is needed
            if collaboration_strategy == "sequential":
                # Execute agents in sequence based on primary result
                collaborative_agents = self._determine_collaborative_agents(
                    primary_request.agent_type,
                    primary_result
                )
                
                for agent_type in collaborative_agents:
                    # Create request for collaborative agent
                    collab_request = AgentExecutionRequest(
                        agent_type=agent_type,
                        input_data=self._prepare_collaborative_input(
                            primary_result,
                            agent_type
                        ),
                        session_id=primary_request.session_id,
                        user_id=primary_request.user_id,
                        parent_execution_id=primary_result.execution_id
                    )
                    
                    # Execute collaborative agent
                    collab_result = await self.execute_agent(collab_request)
                    results[agent_type.value] = collab_result
                    
                    # Record interaction
                    if self.mongodb:
                        await self._record_interaction(
                            source_execution_id=primary_result.execution_id,
                            source_agent_type=primary_request.agent_type,
                            target_execution_id=collab_result.execution_id,
                            target_agent_type=agent_type,
                            interaction_type="spawn",
                            message={
                                "reason": "Collaborative workflow",
                                "strategy": collaboration_strategy
                            },
                            session_id=primary_request.session_id,
                            user_id=primary_request.user_id
                        )
            
            return {
                "success": True,
                "primary_agent": primary_request.agent_type.value,
                "strategy": collaboration_strategy,
                "results": results,
                "total_agents": len(results)
            }
            
        except Exception as e:
            logger.error(f"Collaborative execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "results": results
            }
    
    def _determine_collaborative_agents(
        self,
        primary_agent: AgentType,
        primary_result: AgentExecutionResult
    ) -> List[AgentType]:
        """Determine which agents should collaborate based on primary result"""
        collaborative_agents = []
        
        # Define collaboration rules
        if primary_agent == AgentType.DEBUGGING:
            # After debugging, might want code review
            if primary_result.status == AgentStatus.COMPLETED:
                collaborative_agents.append(AgentType.CODE_REVIEW)
        
        elif primary_agent == AgentType.CODE_REVIEW:
            # After code review, might want security check
            collaborative_agents.append(AgentType.SECURITY)
        
        elif primary_agent == AgentType.RESEARCH:
            # Research might lead to documentation
            collaborative_agents.append(AgentType.DOCUMENTATION)
        
        return collaborative_agents
    
    def _prepare_collaborative_input(
        self,
        primary_result: AgentExecutionResult,
        target_agent: AgentType
    ) -> Dict[str, Any]:
        """Prepare input for collaborative agent based on primary result"""
        output_data = primary_result.output_data or {}
        
        if target_agent == AgentType.CODE_REVIEW:
            # Extract code from debugging result
            return {
                "code": output_data.get("fixed_code", output_data.get("code", "")),
                "context": f"Code from {primary_result.agent_type.value} agent"
            }
        
        elif target_agent == AgentType.SECURITY:
            # Pass code for security analysis
            return {
                "code": output_data.get("code", output_data.get("review", "")),
                "context": f"Analysis from {primary_result.agent_type.value} agent"
            }
        
        elif target_agent == AgentType.DOCUMENTATION:
            # Create documentation from research
            return {
                "topic": output_data.get("content", "")[:500],
                "doc_type": "guide"
            }
        
        return {"context": str(output_data)}
    
    async def get_agent_health(self) -> Dict[str, Any]:
        """
        Check health status of all agents
        
        Returns:
            Dictionary with health status for each agent
        """
        health_status = {}
        
        for agent_type, agent in self.agents.items():
            try:
                status = await agent.health_check()
                health_status[agent_type.value] = status
            except Exception as e:
                health_status[agent_type.value] = {
                    "agent_type": agent_type.value,
                    "is_healthy": False,
                    "error": str(e)
                }
        
        overall_healthy = all(
            status.get("is_healthy", False)
            for status in health_status.values()
        )
        
        return {
            "overall_healthy": overall_healthy,
            "agents": health_status,
            "total_agents": len(health_status),
            "healthy_agents": sum(
                1 for s in health_status.values() if s.get("is_healthy", False)
            )
        }
    
    async def get_agent_metrics(
        self,
        agent_type: Optional[AgentType] = None,
        time_range_hours: int = 24
    ) -> Dict[str, AgentMetrics]:
        """
        Get metrics for agents
        
        Args:
            agent_type: Specific agent type or None for all
            time_range_hours: Time range for metrics
            
        Returns:
            Dictionary of agent metrics
        """
        if not self.mongodb:
            return {}
        
        # This would query MongoDB for execution history
        # Simplified version for now
        metrics = {}
        
        agent_types = [agent_type] if agent_type else list(AgentType)
        
        for at in agent_types:
            metrics[at.value] = AgentMetrics(
                agent_type=at,
                total_executions=0,
                successful_executions=0,
                failed_executions=0
            )
        
        return metrics
    
    async def _store_execution(self, execution: AgentExecution):
        """Store execution record in MongoDB"""
        if not self.mongodb:
            return
        
        try:
            db = self.mongodb["xionimus_ai"]
            collection = db["agent_executions"]
            await collection.insert_one(execution.dict())
        except Exception as e:
            logger.error(f"Failed to store execution: {str(e)}")
    
    async def _update_execution(self, execution: AgentExecution):
        """Update execution record in MongoDB"""
        if not self.mongodb:
            return
        
        try:
            db = self.mongodb["xionimus_ai"]
            collection = db["agent_executions"]
            await collection.update_one(
                {"execution_id": execution.execution_id},
                {"$set": execution.dict()}
            )
        except Exception as e:
            logger.error(f"Failed to update execution: {str(e)}")
    
    async def _record_interaction(
        self,
        source_execution_id: str,
        source_agent_type: AgentType,
        target_execution_id: str,
        target_agent_type: AgentType,
        interaction_type: str,
        message: Dict[str, Any],
        session_id: Optional[str],
        user_id: Optional[str]
    ):
        """Record agent interaction in MongoDB"""
        if not self.mongodb:
            return
        
        try:
            interaction = AgentInteraction(
                source_execution_id=source_execution_id,
                source_agent_type=source_agent_type,
                target_execution_id=target_execution_id,
                target_agent_type=target_agent_type,
                interaction_type=interaction_type,
                message=message,
                session_id=session_id,
                user_id=user_id
            )
            
            db = self.mongodb["xionimus_ai"]
            collection = db["agent_interactions"]
            await collection.insert_one(interaction.dict())
        except Exception as e:
            logger.error(f"Failed to record interaction: {str(e)}")
