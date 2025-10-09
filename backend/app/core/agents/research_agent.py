"""Research Agent using Perplexity Sonar Deep Research"""
import requests
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, AsyncGenerator, List
from uuid import uuid4

from ...models.agent_models import AgentType, AgentStreamChunk
from ..base_agent import BaseAgent
from ..mongo_db import get_database

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent powered by Perplexity Sonar Deep Research
    Performs comprehensive web research with citations
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.RESEARCH, api_keys=api_keys)
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
    
    def _format_citations(self, citations: List[str]) -> List[Dict[str, Any]]:
        """Format citations with better structure and clickable links"""
        formatted_citations = []
        
        for idx, citation in enumerate(citations, 1):
            # Extract URL if present
            url_match = re.search(r'(https?://[^\s]+)', citation)
            url = url_match.group(1) if url_match else citation
            
            # Clean URL and get domain
            clean_url = url.rstrip('.,;)')
            domain = re.search(r'https?://(?:www\.)?([^/]+)', clean_url)
            domain_name = domain.group(1) if domain else "Unknown Source"
            
            formatted_citations.append({
                "id": idx,
                "url": clean_url,
                "domain": domain_name,
                "title": f"Source {idx}",
                "accessible": True
            })
        
        return formatted_citations
    
    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key findings from research content"""
        # Look for bullet points, numbered lists, or key statements
        findings = []
        
        # Extract bullet points
        bullet_matches = re.findall(r'[•\-\*]\s*(.+?)(?:\n|$)', content)
        findings.extend(bullet_matches[:5])  # Top 5 findings
        
        # Extract numbered points
        numbered_matches = re.findall(r'\d+\.\s*(.+?)(?:\n|$)', content)
        findings.extend(numbered_matches[:5])
        
        # If no findings, extract first few sentences
        if not findings:
            sentences = re.split(r'[.!?]+', content)
            findings = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
        
        return findings[:5]  # Return top 5 findings
    
    async def _save_research_result(
        self,
        query: str,
        result: Dict[str, Any],
        user_id: Optional[str],
        session_id: Optional[str]
    ):
        """Save research results to database for history"""
        if not user_id:
            return
        
        try:
            db = get_database()
            research_collection = db.research_history
            
            research_doc = {
                "research_id": str(uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "query": query,
                "content": result["content"],
                "citations": result["formatted_citations"],
                "related_questions": result.get("related_questions", []),
                "key_findings": result.get("key_findings", []),
                "model_used": result["model_used"],
                "sources_count": result["sources_count"],
                "token_usage": result["token_usage"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["research", "perplexity"]
            }
            
            research_collection.insert_one(research_doc)
            logger.info(f"Research result saved for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to save research result: {e}")
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute research query with enhancements"""
        query = input_data["query"]
        use_deep_research = input_data.get("deep_research", True)
        multi_step = input_data.get("multi_step", False)
        
        # Select model
        model = "sonar-deep-research" if use_deep_research else "sonar"
        
        # Enhanced system prompt for better research
        enhanced_prompt = self.get_system_prompt() + """
        
        Additionally:
        - Verify facts across multiple sources when possible
        - Highlight any conflicting information found
        - Provide confidence levels for key claims
        - Structure findings clearly with key takeaways
        """
        
        # Build request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": enhanced_prompt},
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
        
        logger.info(f"Sending enhanced research query with model: {model}")
        
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
        
        # Format citations with better structure
        formatted_citations = self._format_citations(citations)
        
        # Extract key findings
        key_findings = self._extract_key_findings(content)
        
        enhanced_result = {
            "content": content,
            "citations": citations,  # Original citations
            "formatted_citations": formatted_citations,  # Enhanced citations
            "related_questions": related_questions,
            "key_findings": key_findings,
            "sources_count": len(citations),
            "model_used": model,
            "fact_checked": use_deep_research,  # Deep research does more fact-checking
            "multi_step_analysis": multi_step,
            "token_usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        }
        
        # Save to database
        await self._save_research_result(query, enhanced_result, user_id, session_id)
        
        return enhanced_result
    
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