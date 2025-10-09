"""Base Agent class for all specialized agents"""
import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from ..models.agent_models import (
    AgentType,
    AgentStatus,
    AgentProvider,
    AgentExecution,
    AgentExecutionResult,
    AgentStreamChunk
)
from .api_config import get_agent_config

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    Provides common functionality for execution, error handling, and logging.
    """
    
    def __init__(self, agent_type: AgentType):
        """
        Initialize base agent
        
        Args:
            agent_type: Type of agent (research, code_review, etc.)
        """
        self.agent_type = agent_type
        self.config = get_agent_config(agent_type.value)
        self.provider = AgentProvider(self.config["provider"])
        self.model = self.config["model"]
        self.timeout = self.config["timeout"]
        
        # Initialize API clients based on provider
        self._init_clients()
        
        logger.info(f"Initialized {agent_type.value} agent with {self.provider.value} provider")
    
    def _init_clients(self):
        """Initialize API clients based on provider"""
        try:
            if self.provider == AgentProvider.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=api_key)
                    logger.info(f"✅ {self.agent_type.value}: OpenAI client initialized")
                else:
                    self.client = None
                    logger.warning(f"⚠️ {self.agent_type.value}: OPENAI_API_KEY not set - agent will run in degraded mode")
                
            elif self.provider == AgentProvider.CLAUDE:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    from anthropic import Anthropic
                    self.client = Anthropic(api_key=api_key)
                    logger.info(f"✅ {self.agent_type.value}: Anthropic client initialized")
                else:
                    self.client = None
                    logger.warning(f"⚠️ {self.agent_type.value}: ANTHROPIC_API_KEY not set - agent will run in degraded mode")
                
            elif self.provider == AgentProvider.PERPLEXITY:
                import requests
                self.client = None  # Will use requests directly
                self.api_key = os.getenv("PERPLEXITY_API_KEY")
                if self.api_key:
                    logger.info(f"✅ {self.agent_type.value}: Perplexity API key found")
                else:
                    logger.warning(f"⚠️ {self.agent_type.value}: PERPLEXITY_API_KEY not set - agent will run in degraded mode")
                
            elif self.provider == AgentProvider.GITHUB:
                from github import Github
                github_token = os.getenv("GITHUB_TOKEN")
                self.client = Github(github_token) if github_token else None
                if github_token:
                    logger.info(f"✅ {self.agent_type.value}: GitHub client initialized")
                else:
                    logger.warning(f"⚠️ {self.agent_type.value}: GITHUB_TOKEN not set - agent will run in degraded mode")
        except Exception as e:
            logger.error(f"❌ {self.agent_type.value}: Failed to initialize client: {e}")
            self.client = None
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AgentExecutionResult:
        """
        Execute agent with input data and return results
        
        Args:
            input_data: Input data for the agent
            execution_id: Unique execution ID
            session_id: Optional session ID for context
            user_id: Optional user ID
            options: Optional execution options
            
        Returns:
            AgentExecutionResult with execution details
        """
        start_time = time.time()
        started_at = datetime.utcnow()
        
        logger.info(f"Starting {self.agent_type.value} execution {execution_id}")
        
        try:
            # Validate input
            self._validate_input(input_data)
            
            # Execute agent-specific logic
            output_data = await self._execute_internal(
                input_data=input_data,
                execution_id=execution_id,
                session_id=session_id,
                user_id=user_id,
                options=options or {}
            )
            
            # Calculate duration
            duration = time.time() - start_time
            completed_at = datetime.utcnow()
            
            # Build result
            result = AgentExecutionResult(
                execution_id=execution_id,
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                output_data=output_data,
                provider=self.provider,
                model=self.model,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                token_usage=output_data.get("token_usage") if output_data else None,
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "options": options
                }
            )
            
            logger.info(
                f"Completed {self.agent_type.value} execution {execution_id} "
                f"in {duration:.2f}s"
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Failed {self.agent_type.value} execution {execution_id}: {str(e)}",
                exc_info=True
            )
            
            return AgentExecutionResult(
                execution_id=execution_id,
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                error_message=str(e),
                provider=self.provider,
                model=self.model,
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=duration,
                metadata={
                    "session_id": session_id,
                    "user_id": user_id,
                    "options": options,
                    "error_type": type(e).__name__
                }
            )
    
    async def execute_streaming(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[AgentStreamChunk, None]:
        """
        Execute agent with streaming output
        
        Args:
            input_data: Input data for the agent
            execution_id: Unique execution ID
            session_id: Optional session ID
            user_id: Optional user ID
            options: Optional execution options
            
        Yields:
            AgentStreamChunk objects with incremental updates
        """
        sequence = 0
        
        try:
            # Send initial status
            yield AgentStreamChunk(
                execution_id=execution_id,
                agent_type=self.agent_type,
                chunk_type="status",
                data={"status": "started", "message": f"Starting {self.agent_type.value} agent"},
                sequence_number=sequence
            )
            sequence += 1
            
            # Validate input
            self._validate_input(input_data)
            
            # Execute with streaming
            async for chunk in self._execute_streaming_internal(
                input_data=input_data,
                execution_id=execution_id,
                session_id=session_id,
                user_id=user_id,
                options=options or {}
            ):
                chunk.sequence_number = sequence
                yield chunk
                sequence += 1
            
            # Send completion status
            yield AgentStreamChunk(
                execution_id=execution_id,
                agent_type=self.agent_type,
                chunk_type="complete",
                data={"status": "completed", "message": "Execution completed successfully"},
                sequence_number=sequence
            )
            
        except Exception as e:
            logger.error(f"Streaming execution failed: {str(e)}", exc_info=True)
            
            yield AgentStreamChunk(
                execution_id=execution_id,
                agent_type=self.agent_type,
                chunk_type="error",
                data={
                    "status": "failed",
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                sequence_number=sequence
            )
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """
        Validate input data for the agent
        Override in subclasses for specific validation
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValueError: If input is invalid
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
    
    @abstractmethod
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Internal execution logic - must be implemented by subclasses
        
        Args:
            input_data: Validated input data
            execution_id: Execution ID
            session_id: Session ID
            user_id: User ID
            options: Execution options
            
        Returns:
            Output data dictionary
        """
        pass
    
    async def _execute_streaming_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> AsyncGenerator[AgentStreamChunk, None]:
        """
        Internal streaming execution logic
        Override in subclasses to support streaming
        
        Default implementation: falls back to non-streaming execution
        """
        # Default: execute normally and return as single chunk
        result = await self._execute_internal(
            input_data, execution_id, session_id, user_id, options
        )
        
        yield AgentStreamChunk(
            execution_id=execution_id,
            agent_type=self.agent_type,
            chunk_type="content",
            data=result,
            sequence_number=0
        )
    
    def get_system_prompt(self) -> str:
        """
        Get system prompt for the agent
        Override in subclasses for specific prompts
        
        Returns:
            System prompt string
        """
        return f"You are a helpful {self.agent_type.value} assistant."
    
    async def fast_health_check(self) -> Dict[str, Any]:
        """
        Fast health check without external API calls
        Checks only internal configuration for quick health status
        
        Returns:
            Health status dictionary
        """
        try:
            # Check basic configuration
            is_healthy = True
            errors = []
            
            # Get API key based on provider
            api_key_configured = False
            if hasattr(self, 'api_key'):
                api_key_configured = bool(self.api_key and self.api_key != "")
            elif hasattr(self, 'client') and self.client:
                api_key_configured = True
            
            if not api_key_configured:
                is_healthy = False
                errors.append("API key not configured")
            
            # Verify provider and model set
            if not self.provider or not self.model:
                is_healthy = False
                errors.append("Provider or model not configured")
            
            return {
                "agent_type": self.agent_type.value,
                "provider": self.provider.value if self.provider else None,
                "model": self.model,
                "status": "healthy" if is_healthy else "degraded",
                "api_key_configured": api_key_configured,
                "errors": errors,
                "response_time_ms": 0
            }
            
        except Exception as e:
            return {
                "agent_type": self.agent_type.value,
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": 0
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the agent with actual API call
        Note: This can take 5-10s depending on API response time
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            
            # Perform simple test based on provider
            if self.provider == AgentProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                is_healthy = True
                
            elif self.provider == AgentProvider.CLAUDE:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "test"}]
                )
                is_healthy = True
                
            elif self.provider == AgentProvider.PERPLEXITY:
                import requests
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 5
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                is_healthy = response.status_code == 200
                
            elif self.provider == AgentProvider.GITHUB:
                user = self.client.get_user()
                is_healthy = user.login is not None
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                "agent_type": self.agent_type.value,
                "is_healthy": is_healthy,
                "provider": self.provider.value,
                "model": self.model,
                "response_time_ms": response_time,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "agent_type": self.agent_type.value,
                "is_healthy": False,
                "provider": self.provider.value,
                "model": self.model,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
