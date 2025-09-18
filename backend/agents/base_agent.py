from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum
import logging

class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"

class AgentCapability(str, Enum):
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    WEB_RESEARCH = "web_research"
    DATA_ANALYSIS = "data_analysis"
    API_INTEGRATION = "api_integration"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    WRITING = "writing"
    DESIGN = "design"
    DEBUGGING = "debugging"

class AgentTask(BaseModel):
    id: str
    agent_type: str
    description: str
    input_data: Dict[str, Any]
    status: AgentStatus = AgentStatus.IDLE
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    steps: List[str] = []
    current_step: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, name: str, description: str, capabilities: List[AgentCapability]):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute the given task and return updated task with results"""
        pass
    
    @abstractmethod
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Return confidence score (0-1) for handling this task"""
        pass
    
    async def update_progress(self, task: AgentTask, progress: float, step: str):
        """Update task progress and current step"""
        task.progress = progress
        task.current_step = step
        task.steps.append(step)
        self.logger.info(f"Task {task.id}: {step} ({progress:.0%})")
    
    def get_capabilities_description(self) -> str:
        """Return human-readable description of capabilities"""
        return ", ".join([cap.value.replace("_", " ").title() for cap in self.capabilities])