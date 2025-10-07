"""Research Agent using Perplexity Sonar Deep Research"""
import requests
import logging
from typing import Dict, Any, Optional, AsyncGenerator

from ...models.agent_models import AgentType, AgentStreamChunk
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent powered by Perplexity Sonar Deep Research
    Performs comprehensive web research with citations
    """
    
    def __init__(self):
        super().__init__(AgentType.RESEARCH)
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate research query input"""
        super()._validate_input(input_data)
        
        if "query" not in input_data:
            raise ValueError("Research query is required")
        
        query = input_data["query"]
        if not isinstance(query, str) or len(query.strip()) < 10:
            raise ValueError("Query must be at least 10 characters")
    
    def get_system_prompt(self) -> str:
        """Get research agent system prompt"""
        return """You are an expert research assistant. Provide comprehensive, 
        well-researched answers with proper citations. Focus on accuracy and 
        include diverse perspectives when relevant."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute research query"""
        query = input_data["query"]
        use_deep_research = input_data.get("deep_research", True)
        
        # Select model
        model = "sonar-deep-research" if use_deep_research else "sonar"
        
        # Build request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": query}
            ],
            "max_tokens": options.get("max_tokens", 2000),
            "temperature": options.get("temperature", 0.2),
            "return_citations": True,
            "return_related_questions": True
        }
        
        # Add search recency if specified
        if "search_recency" in options:
            payload["search_recency"] = options["search_recency"]
        
        logger.info(f"Sending research query with model: {model}")
        
        # Make API request
        response = requests.post(
            self.base_url,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract response data
        content = result["choices"][0]["message"]["content"]
        citations = result.get("citations", [])
        related_questions = result.get("related_questions", [])
        usage = result.get("usage", {})
        
        return {
            "content": content,
            "citations": citations,
            "related_questions": related_questions,
            "sources_count": len(citations),
            "model_used": model,
            "token_usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        }
    
    async def _execute_streaming_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> AsyncGenerator[AgentStreamChunk, None]:
        """Execute research with streaming (simulated progress updates)"""
        
        # Send initial status
        yield AgentStreamChunk(
            execution_id=execution_id,
            agent_type=self.agent_type,
            chunk_type="status",
            data={"message": "Starting research query analysis..."}
        )
        
        # For now, execute normally and return as chunks
        # In production, could use streaming API if available
        result = await self._execute_internal(
            input_data, execution_id, session_id, user_id, options
        )
        
        # Send progress updates
        yield AgentStreamChunk(
            execution_id=execution_id,
            agent_type=self.agent_type,
            chunk_type="metadata",
            data={
                "sources_found": result["sources_count"],
                "model": result["model_used"]
            }
        )
        
        # Send content
        yield AgentStreamChunk(
            execution_id=execution_id,
            agent_type=self.agent_type,
            chunk_type="content",
            data={
                "content": result["content"],
                "citations": result["citations"],
                "related_questions": result["related_questions"]
            }
        )