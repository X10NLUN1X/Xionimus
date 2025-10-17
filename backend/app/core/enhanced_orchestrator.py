"""
Enhanced Multi-Agent Orchestrator
Coordinates multiple AI agents with message broker and task queue

Location: /backend/app/core/enhanced_orchestrator.py
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

from .message_broker import (
    get_message_broker,
    MessageBroker,
    Message,
    MessageType,
    MessagePriority
)
from .task_queue import (
    get_task_queue,
    TaskQueue,
    Task,
    TaskStatus,
    TaskPriority
)
from .ai_manager import AIManager

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """How tasks should be executed"""
    SEQUENTIAL = "sequential"  # One at a time, in order
    PARALLEL = "parallel"      # All at once where possible
    SMART = "smart"           # Orchestrator decides based on dependencies


class AgentType(Enum):
    """Agent types in the system"""
    STRATEGIST = "strategist"      # High-level planning
    ARCHITECT = "architect"        # System architecture
    ENGINEER = "engineer"          # Code implementation
    UI_UX = "ui_ux"               # UI/UX design
    TESTER = "tester"             # Testing
    DEBUGGER = "debugger"         # Debugging & optimization
    DOCUMENTER = "documenter"     # Documentation
    ANALYST = "analyst"           # Analysis & interpretation
    OPERATOR = "operator"         # Execution & deployment
    LIAISON = "liaison"           # User interaction
    VALIDATOR = "validator"       # Quality assurance


@dataclass
class ExecutionContext:
    """
    Shared context for all agents in an execution
    """
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_id: str = ""
    user_request: str = ""
    research_data: Optional[str] = None
    
    # Shared artifacts
    architecture: Optional[Dict[str, Any]] = None
    code_base: Dict[str, str] = field(default_factory=dict)  # filename -> code
    test_results: Optional[Dict[str, Any]] = None
    documentation: Optional[str] = None
    
    # Custom artifacts
    artifacts: Dict[str, Any] = field(default_factory=dict)
    
    # Timeline
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, agent_type: str, event_type: str, data: Dict[str, Any]):
        """Add event to timeline"""
        self.events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_type,
            "event_type": event_type,
            "data": data
        })
    
    def set_artifact(self, key: str, value: Any, agent: str):
        """Set shared artifact"""
        self.artifacts[key] = value
        self.add_event(agent, "artifact_created", {"key": key})
    
    def get_artifact(self, key: str) -> Any:
        """Get shared artifact"""
        return self.artifacts.get(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "execution_id": self.execution_id,
            "user_request": self.user_request,
            "started_at": self.started_at.isoformat(),
            "artifacts": list(self.artifacts.keys()),
            "events_count": len(self.events),
            "metadata": self.metadata
        }


@dataclass
class ExecutionPlan:
    """
    Plan for agent execution
    """
    plan_id: str = field(default_factory=lambda: str(uuid4()))
    tasks: List[Task] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SMART
    estimated_duration: Optional[float] = None
    estimated_cost: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plan_id": self.plan_id,
            "execution_mode": self.execution_mode.value,
            "total_tasks": len(self.tasks),
            "tasks": [t.to_dict() for t in self.tasks],
            "estimated_duration": self.estimated_duration,
            "estimated_cost": self.estimated_cost
        }


@dataclass
class OrchestratorResult:
    """
    Final result from orchestrator
    """
    execution_id: str
    status: str  # "success", "partial", "failed"
    completed_tasks: int
    failed_tasks: int
    total_tasks: int
    
    # Results by agent
    agent_results: Dict[str, Any] = field(default_factory=dict)
    
    # Consolidated output
    code: Optional[str] = None
    documentation: Optional[str] = None
    summary: Optional[str] = None
    
    # Metadata
    execution_time: Optional[float] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    
    # Context
    context: Optional[ExecutionContext] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "execution_id": self.execution_id,
            "status": self.status,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_tasks": self.total_tasks,
            "agent_results": self.agent_results,
            "code": self.code,
            "documentation": self.documentation,
            "summary": self.summary,
            "execution_time": self.execution_time,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "context": self.context.to_dict() if self.context else None
        }


class EnhancedOrchestrator:
    """
    Enhanced orchestrator with message broker and task queue
    """
    
    def __init__(self, ai_manager: AIManager):
        self.ai_manager = ai_manager
        self.message_broker: MessageBroker = get_message_broker()
        self.task_queue: TaskQueue = get_task_queue()
        
        # Agent registry (agent_type -> agent_instance)
        self.agents: Dict[str, Any] = {}
        
        # Active executions
        self.active_executions: Dict[str, ExecutionContext] = {}
        
        logger.info("🎭 Enhanced Orchestrator initialized")
    
    async def plan(
        self,
        user_request: str,
        user_id: str = "",
        session_id: str = "",
        research_data: Optional[str] = None,
        mode: ExecutionMode = ExecutionMode.SMART
    ) -> ExecutionPlan:
        """
        Plan agent execution based on user request
        Returns execution plan with tasks
        """
        logger.info(f"📋 Planning execution for: {user_request[:100]}...")
        
        # Create execution context
        context = ExecutionContext(
            user_id=user_id,
            session_id=session_id,
            user_request=user_request,
            research_data=research_data
        )
        
        # Analyze request to determine required agents
        required_agents = await self._analyze_request(user_request)
        
        # Create tasks with dependencies
        tasks = await self._create_tasks(required_agents, context)
        
        # Estimate duration and cost
        estimated_duration = sum(self._estimate_task_duration(t) for t in tasks)
        estimated_cost = sum(self._estimate_task_cost(t) for t in tasks)
        
        plan = ExecutionPlan(
            tasks=tasks,
            execution_mode=mode,
            estimated_duration=estimated_duration,
            estimated_cost=estimated_cost
        )
        
        logger.info(
            f"✅ Plan created: {len(tasks)} tasks, "
            f"est. {estimated_duration:.1f}s, ${estimated_cost:.4f}"
        )
        
        return plan
    
    async def execute(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        api_keys: Dict[str, str],
        stream: bool = False
    ) -> OrchestratorResult:
        """
        Execute the plan
        """
        logger.info(
            f"🚀 Starting execution {context.execution_id} "
            f"with {len(plan.tasks)} tasks"
        )
        
        # Store context
        self.active_executions[context.execution_id] = context
        
        start_time = datetime.now(timezone.utc)
        
        # Enqueue all tasks
        for task in plan.tasks:
            task.execution_id = context.execution_id
            await self.task_queue.enqueue(task)
        
        # Execute based on mode
        if plan.execution_mode == ExecutionMode.PARALLEL:
            await self._execute_parallel(plan, context, api_keys)
        elif plan.execution_mode == ExecutionMode.SEQUENTIAL:
            await self._execute_sequential(plan, context, api_keys)
        else:  # SMART
            await self._execute_smart(plan, context, api_keys)
        
        # Collect results
        result = await self._collect_results(plan, context, start_time)
        
        # Cleanup
        self.active_executions.pop(context.execution_id, None)
        
        logger.info(
            f"✅ Execution completed: {result.completed_tasks}/{result.total_tasks} tasks"
        )
        
        return result
    
    async def execute_with_streaming(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        api_keys: Dict[str, str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute with real-time progress streaming
        Yields progress updates as tasks execute
        """
        logger.info(f"📡 Starting streaming execution {context.execution_id}")
        
        # Store context
        self.active_executions[context.execution_id] = context
        
        start_time = datetime.now(timezone.utc)
        
        # Enqueue tasks
        for task in plan.tasks:
            task.execution_id = context.execution_id
            await self.task_queue.enqueue(task)
            
            # Yield task enqueued event
            yield {
                "type": "task_enqueued",
                "task_id": task.task_id,
                "agent_type": task.agent_type,
                "description": task.description
            }
        
        # Execute with progress updates
        async for update in self._execute_with_updates(plan, context, api_keys):
            yield update
        
        # Final result
        result = await self._collect_results(plan, context, start_time)
        
        yield {
            "type": "execution_complete",
            "result": result.to_dict()
        }
        
        # Cleanup
        self.active_executions.pop(context.execution_id, None)
    
    async def _analyze_request(self, user_request: str) -> List[AgentType]:
        """
        Analyze request to determine which agents are needed
        """
        request_lower = user_request.lower()
        agents = []
        
        # Core agents - always included for coding requests
        if any(word in request_lower for word in ["code", "implement", "create", "build", "develop"]):
            agents.extend([
                AgentType.STRATEGIST,   # Plan approach
                AgentType.ARCHITECT,    # Design architecture
                AgentType.ENGINEER      # Implement code
            ])
        
        # UI/UX for frontend requests
        if any(word in request_lower for word in ["ui", "interface", "frontend", "design", "website", "app"]):
            agents.append(AgentType.UI_UX)
        
        # Testing for quality requests
        if any(word in request_lower for word in ["test", "testing", "quality", "qa"]):
            agents.append(AgentType.TESTER)
        
        # Debugging for fix/optimize requests
        if any(word in request_lower for word in ["debug", "fix", "bug", "error", "optimize", "improve"]):
            agents.append(AgentType.DEBUGGER)
        
        # Documentation for docs requests
        if any(word in request_lower for word in ["document", "readme", "docs", "explain"]):
            agents.append(AgentType.DOCUMENTER)
        
        # Analysis for analysis requests
        if any(word in request_lower for word in ["analyze", "analyze", "metrics", "performance"]):
            agents.append(AgentType.ANALYST)
        
        # If no agents selected, use basic set
        if not agents:
            agents = [AgentType.LIAISON]
        
        logger.info(f"📊 Required agents: {[a.value for a in agents]}")
        return agents
    
    async def _create_tasks(
        self,
        agents: List[AgentType],
        context: ExecutionContext
    ) -> List[Task]:
        """
        Create tasks with proper dependencies
        """
        tasks = []
        task_map = {}  # agent_type -> task_id
        
        # Define agent priority and dependencies
        agent_order = [
            (AgentType.STRATEGIST, TaskPriority.CRITICAL, []),
            (AgentType.ARCHITECT, TaskPriority.HIGH, [AgentType.STRATEGIST]),
            (AgentType.ENGINEER, TaskPriority.HIGH, [AgentType.ARCHITECT]),
            (AgentType.UI_UX, TaskPriority.NORMAL, [AgentType.ARCHITECT]),
            (AgentType.TESTER, TaskPriority.NORMAL, [AgentType.ENGINEER]),
            (AgentType.DEBUGGER, TaskPriority.NORMAL, [AgentType.ENGINEER]),
            (AgentType.ANALYST, TaskPriority.NORMAL, [AgentType.ENGINEER]),
            (AgentType.DOCUMENTER, TaskPriority.LOW, [AgentType.ENGINEER]),
            (AgentType.VALIDATOR, TaskPriority.HIGH, [AgentType.ENGINEER, AgentType.TESTER]),
            (AgentType.LIAISON, TaskPriority.CRITICAL, [AgentType.VALIDATOR])
        ]
        
        for agent_type, priority, deps in agent_order:
            if agent_type not in agents:
                continue
            
            # Get dependency task IDs
            dep_ids = [
                task_map[dep]
                for dep in deps
                if dep in task_map
            ]
            
            task = Task(
                agent_type=agent_type.value,
                description=self._get_task_description(agent_type),
                priority=priority,
                dependencies=dep_ids,
                input_data={"context": context.to_dict()},
                execution_id=context.execution_id
            )
            
            tasks.append(task)
            task_map[agent_type] = task.task_id
        
        return tasks
    
    def _get_task_description(self, agent_type: AgentType) -> str:
        """Get description for agent task"""
        descriptions = {
            AgentType.STRATEGIST: "Analyze requirements and create execution strategy",
            AgentType.ARCHITECT: "Design system architecture and structure",
            AgentType.ENGINEER: "Implement code based on architecture",
            AgentType.UI_UX: "Design user interface and experience",
            AgentType.TESTER: "Create and run tests",
            AgentType.DEBUGGER: "Debug and optimize code",
            AgentType.DOCUMENTER: "Generate documentation",
            AgentType.ANALYST: "Analyze results and metrics",
            AgentType.OPERATOR: "Execute deployments",
            AgentType.LIAISON: "Format output for user",
            AgentType.VALIDATOR: "Validate all outputs"
        }
        return descriptions.get(agent_type, f"Execute {agent_type.value} task")
    
    def _estimate_task_duration(self, task: Task) -> float:
        """Estimate task duration in seconds"""
        # Simple heuristic - adjust based on agent type
        durations = {
            "strategist": 10.0,
            "architect": 15.0,
            "engineer": 30.0,
            "ui_ux": 20.0,
            "tester": 15.0,
            "debugger": 20.0,
            "documenter": 10.0,
            "analyst": 10.0,
            "operator": 5.0,
            "liaison": 5.0,
            "validator": 10.0
        }
        return durations.get(task.agent_type, 10.0)
    
    def _estimate_task_cost(self, task: Task) -> float:
        """Estimate task cost in USD"""
        # Simple cost estimation based on model usage
        # Adjust based on actual model pricing
        return 0.01  # $0.01 per task as baseline
    
    async def _execute_parallel(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        api_keys: Dict[str, str]
    ):
        """Execute tasks in parallel where possible"""
        logger.info("⚡ Executing in parallel mode")
        
        tasks = []
        for task in plan.tasks:
            tasks.append(self._execute_task(task, context, api_keys))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_sequential(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        api_keys: Dict[str, str]
    ):
        """Execute tasks sequentially"""
        logger.info("➡️ Executing in sequential mode")
        
        for task in plan.tasks:
            await self._execute_task(task, context, api_keys)
    
    async def _execute_smart(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        api_keys: Dict[str, str]
    ):
        """Execute tasks smartly based on dependencies"""
        logger.info("🧠 Executing in smart mode")
        
        # Keep processing until all tasks done
        while True:
            # Get ready tasks
            ready_tasks = self.task_queue.get_ready_tasks()
            
            if not ready_tasks:
                # Check if we're done
                running = self.task_queue.get_running_tasks()
                if not running:
                    break
                
                # Wait for running tasks
                await asyncio.sleep(0.5)
                continue
            
            # Execute ready tasks in parallel
            tasks = [
                self._execute_task(
                    await self.task_queue.dequeue(timeout=0.1),
                    context,
                    api_keys
                )
                for _ in range(len(ready_tasks))
            ]
            
            await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
    
    async def _execute_with_updates(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        api_keys: Dict[str, str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute with real-time updates"""
        
        # Smart execution with progress updates
        while True:
            # Get queue status
            stats = self.task_queue.get_statistics()
            
            yield {
                "type": "queue_status",
                "stats": stats
            }
            
            # Get ready tasks
            task = await self.task_queue.dequeue(timeout=0.5)
            
            if task is None:
                # Check if we're done
                if stats["running"] == 0 and stats["ready"] == 0 and stats["pending"] == 0:
                    break
                continue
            
            # Task started
            yield {
                "type": "task_started",
                "task_id": task.task_id,
                "agent_type": task.agent_type
            }
            
            # Execute
            try:
                await self._execute_task(task, context, api_keys)
                
                yield {
                    "type": "task_completed",
                    "task_id": task.task_id,
                    "agent_type": task.agent_type
                }
            except Exception as e:
                yield {
                    "type": "task_failed",
                    "task_id": task.task_id,
                    "agent_type": task.agent_type,
                    "error": str(e)
                }
    
    async def _execute_task(
        self,
        task: Task,
        context: ExecutionContext,
        api_keys: Dict[str, str]
    ):
        """Execute a single task"""
        if task is None:
            return
        
        logger.info(f"🤖 Executing: {task.agent_type}")
        
        try:
            # Select model for agent
            provider, model = self._select_agent_model(task.agent_type)
            
            # Generate prompt
            prompt = self._generate_agent_prompt(task, context)
            
            # Execute with AI manager
            response = await self.ai_manager.generate_response(
                provider=provider,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                api_keys=api_keys
            )
            
            result = response.get("content", "")
            
            # Mark completed
            await self.task_queue.mark_completed(task.task_id, result)
            
            # Add to context
            context.agent_results[task.agent_type] = result
            context.add_event(task.agent_type, "completed", {"result_length": len(result)})
            
        except Exception as e:
            logger.error(f"❌ Task failed: {task.agent_type} - {e}")
            await self.task_queue.mark_failed(task.task_id, str(e))
    
    def _select_agent_model(self, agent_type: str) -> tuple[str, str]:
        """Select best model for agent type"""
        # Use same logic as existing multi_agent_orchestrator
        model_mapping = {
            "strategist": ("anthropic", "claude-opus-4-1-20250805"),
            "architect": ("anthropic", "claude-opus-4-1-20250805"),
            "engineer": ("anthropic", "claude-sonnet-4-5-20250929"),
            "ui_ux": ("openai", "gpt-4o"),
            "tester": ("anthropic", "claude-sonnet-4-5-20250929"),
            "debugger": ("anthropic", "claude-opus-4-1-20250805"),
            "documenter": ("openai", "gpt-4o"),
            "analyst": ("anthropic", "claude-sonnet-4-5-20250929"),
            "operator": ("openai", "gpt-4o"),
            "liaison": ("openai", "gpt-4o"),
            "validator": ("anthropic", "claude-opus-4-1-20250805")
        }
        return model_mapping.get(agent_type, ("anthropic", "claude-sonnet-4-5-20250929"))
    
    def _generate_agent_prompt(self, task: Task, context: ExecutionContext) -> str:
        """Generate prompt for agent"""
        base = f"""User Request: {context.user_request}

Research Data: {context.research_data[:1000] if context.research_data else 'None'}

Previous Results: {len(context.agent_results)} agents completed

Your Task: {task.description}

Provide a detailed, high-quality response."""
        
        return base
    
    async def _collect_results(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext,
        start_time: datetime
    ) -> OrchestratorResult:
        """Collect and aggregate results"""
        
        completed = self.task_queue.get_completed_tasks()
        failed = self.task_queue.get_failed_tasks()
        
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Determine status
        if len(failed) == 0:
            status = "success"
        elif len(completed) > 0:
            status = "partial"
        else:
            status = "failed"
        
        result = OrchestratorResult(
            execution_id=context.execution_id,
            status=status,
            completed_tasks=len(completed),
            failed_tasks=len(failed),
            total_tasks=len(plan.tasks),
            agent_results=context.agent_results,
            execution_time=execution_time,
            context=context
        )
        
        return result


# Global orchestrator instance
_orchestrator: Optional[EnhancedOrchestrator] = None


def get_enhanced_orchestrator(ai_manager: AIManager) -> EnhancedOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EnhancedOrchestrator(ai_manager)
    return _orchestrator
