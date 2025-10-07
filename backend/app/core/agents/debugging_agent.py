"""Debugging Agent using Claude Opus 4.1"""
import logging
from typing import Dict, Any, Optional, AsyncGenerator

from ...models.agent_models import AgentType, AgentStreamChunk
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DebuggingAgent(BaseAgent):
    """
    Debugging Agent powered by Claude Opus 4.1
    Analyzes errors and provides debugging solutions
    """
    
    def __init__(self):
        super().__init__(AgentType.DEBUGGING)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate debugging input"""
        super()._validate_input(input_data)
        
        if "error" not in input_data and "code" not in input_data:
            raise ValueError("Either error or code must be provided")
    
    def get_system_prompt(self) -> str:
        """Get debugging agent system prompt"""
        return """You are an expert debugging assistant with deep knowledge of:
        - Root cause analysis
        - Error trace interpretation
        - Edge case identification
        - Multi-language debugging
        - System-level debugging
        
        Provide thorough debugging analysis that includes:
        1. Root cause identification
        2. Step-by-step explanation
        3. Concrete fix suggestions
        4. Prevention strategies
        5. Related issues to check
        
        Be precise, methodical, and consider edge cases."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute debugging analysis"""
        error = input_data.get("error", "")
        code = input_data.get("code", "")
        stack_trace = input_data.get("stack_trace", "")
        context = input_data.get("context", "")
        
        # Build debugging prompt
        prompt = "Please help debug the following issue:\n\n"
        
        if error:
            prompt += f"**Error Message:**\n{error}\n\n"
        
        if stack_trace:
            prompt += f"**Stack Trace:**\n```\n{stack_trace}\n```\n\n"
        
        if code:
            prompt += f"**Code:**\n```\n{code}\n```\n\n"
        
        if context:
            prompt += f"**Context:**\n{context}\n\n"
        
        prompt += """
Provide a comprehensive debugging analysis:
1. **Root Cause**: What is causing the error?
2. **Explanation**: Why is this happening?
3. **Fix**: How to fix it (with code if applicable)
4. **Prevention**: How to prevent similar issues
5. **Related Checks**: Other potential issues to verify

Be specific and thorough."""
        
        # Call Claude Opus 4.1 API
        response = self.client.messages.create(
            model=self.model,  # claude-opus-4-20250514
            max_tokens=options.get("max_tokens", 3000),
            temperature=options.get("temperature", 0.2),
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        return {
            "analysis": content,
            "error_provided": bool(error),
            "code_provided": bool(code),
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }