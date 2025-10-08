"""Agent execution and interaction models for MongoDB"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import uuid


class AgentType(str, Enum):
    """Available agent types"""
    RESEARCH = "research"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEBUGGING = "debugging"
    SECURITY = "security"
    PERFORMANCE = "performance"
    FORK = "fork"


class AgentStatus(str, Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentProvider(str, Enum):
    """API provider for agents"""
    PERPLEXITY = "perplexity"
    OPENAI = "openai"
    CLAUDE = "claude"
    GITHUB = "github"


class AgentExecutionRequest(BaseModel):
    """Request model for agent execution"""
    agent_type: AgentType
    input_data: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    parent_execution_id: Optional[str] = None  # For collaborative agents
    options: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "research",
                "input_data": {
                    "query": "What are the latest trends in AI?",
                    "depth": "comprehensive"
                },
                "session_id": "session_123",
                "user_id": "user_456",
                "options": {
                    "include_citations": True,
                    "max_sources": 10
                }
            }
        }


class AgentExecutionResult(BaseModel):
    """Result model for agent execution"""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType
    status: AgentStatus
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    provider: AgentProvider
    model: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec_789",
                "agent_type": "research",
                "status": "completed",
                "output_data": {
                    "content": "Research findings...",
                    "citations": ["source1", "source2"],
                    "related_questions": ["Question 1", "Question 2"]
                },
                "provider": "perplexity",
                "model": "sonar-deep-research",
                "started_at": "2025-01-01T12:00:00Z",
                "completed_at": "2025-01-01T12:03:45Z",
                "duration_seconds": 225.5,
                "token_usage": {
                    "input_tokens": 100,
                    "output_tokens": 500
                }
            }
        }


class AgentExecution(BaseModel):
    """Complete agent execution record for database storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    agent_type: AgentType
    status: AgentStatus
    
    # Request data
    input_data: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    parent_execution_id: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    
    # Result data
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    
    # Provider info
    provider: AgentProvider
    model: Optional[str] = None
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Usage stats
    token_usage: Optional[Dict[str, int]] = None
    api_calls_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Collaborative execution
    child_executions: List[str] = Field(default_factory=list)  # IDs of spawned agents
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "mongo_id_123",
                "execution_id": "exec_789",
                "agent_type": "code_review",
                "status": "completed",
                "input_data": {
                    "code": "def example(): pass",
                    "language": "python"
                },
                "session_id": "session_123",
                "user_id": "user_456",
                "output_data": {
                    "issues": [],
                    "suggestions": ["Add docstring"],
                    "score": 8.5
                },
                "provider": "claude",
                "model": "claude-sonnet-4-20250514",
                "started_at": "2025-01-01T12:00:00Z",
                "completed_at": "2025-01-01T12:00:05Z",
                "duration_seconds": 5.2
            }
        }


class AgentInteraction(BaseModel):
    """Records interaction between agents for collaborative workflows"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Source and target agents
    source_execution_id: str
    source_agent_type: AgentType
    target_execution_id: Optional[str] = None  # Set when target agent starts
    target_agent_type: AgentType
    
    # Interaction data
    interaction_type: str  # "spawn", "query", "result_share", "error_report"
    message: Dict[str, Any]
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Session context
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "interaction_123",
                "source_execution_id": "exec_789",
                "source_agent_type": "debugging",
                "target_execution_id": "exec_790",
                "target_agent_type": "code_review",
                "interaction_type": "spawn",
                "message": {
                    "reason": "Need code review before applying fix",
                    "context": {"code": "fixed_code_here"}
                },
                "created_at": "2025-01-01T12:00:00Z",
                "session_id": "session_123"
            }
        }


class AgentStreamChunk(BaseModel):
    """Streaming chunk for real-time agent updates"""
    execution_id: str
    agent_type: AgentType
    chunk_type: str  # "status", "content", "metadata", "error", "complete"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec_789",
                "agent_type": "research",
                "chunk_type": "content",
                "data": {
                    "partial_content": "Research findings so far...",
                    "sources_found": 5
                },
                "timestamp": "2025-01-01T12:00:30Z",
                "sequence_number": 15
            }
        }


class AgentHealthStatus(BaseModel):
    """Health status for agent system"""
    agent_type: AgentType
    is_healthy: bool
    provider: AgentProvider
    model: Optional[str] = None
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    success_rate_24h: Optional[float] = None  # Percentage
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "research",
                "is_healthy": True,
                "provider": "perplexity",
                "model": "sonar-deep-research",
                "last_check": "2025-01-01T12:00:00Z",
                "response_time_ms": 2500.0,
                "success_rate_24h": 98.5
            }
        }


class AgentMetrics(BaseModel):
    """Aggregated metrics for an agent"""
    agent_type: AgentType
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration_seconds: Optional[float] = None
    total_tokens_used: int = 0
    last_execution: Optional[datetime] = None
    success_rate: Optional[float] = None  # Percentage
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "code_review",
                "total_executions": 150,
                "successful_executions": 147,
                "failed_executions": 3,
                "average_duration_seconds": 5.8,
                "total_tokens_used": 75000,
                "last_execution": "2025-01-01T11:55:00Z",
                "success_rate": 98.0
            }
        }
