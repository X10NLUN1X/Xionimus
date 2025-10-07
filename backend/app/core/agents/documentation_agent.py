"""Documentation Agent using Claude Sonnet 4"""
import logging
from typing import Dict, Any, Optional

from ...models.agent_models import AgentType
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    """
    Documentation Agent powered by Claude Sonnet 4
    Generates comprehensive documentation
    """
    
    def __init__(self):
        super().__init__(AgentType.DOCUMENTATION)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate documentation input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data and "topic" not in input_data:
            raise ValueError("Either code or topic must be provided")
    
    def get_system_prompt(self) -> str:
        """Get documentation agent system prompt"""
        return """You are an expert technical writer. Create clear, comprehensive 
        documentation that is:
        - Well-structured with proper headings
        - Easy to understand for target audience
        - Complete with examples and use cases
        - Following documentation best practices
        
        Use markdown formatting for readability."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate documentation"""
        code = input_data.get("code", "")
        topic = input_data.get("topic", "")
        doc_type = input_data.get("doc_type", "api")  # api, tutorial, guide, reference
        language = input_data.get("language", "python")
        
        # Build documentation prompt
        prompt = f"""Generate {doc_type} documentation for:

"""
        if code:
            prompt += f"**Code:**\n```{language}\n{code}\n```\n\n"
        
        if topic:
            prompt += f"**Topic:**\n{topic}\n\n"
        
        prompt += f"""
Create comprehensive {doc_type} documentation including:
1. **Overview**: Purpose and functionality
2. **Usage**: How to use with examples
3. **Parameters/Arguments**: Detailed descriptions
4. **Return Values**: What is returned
5. **Examples**: Practical use cases
6. **Notes**: Important considerations

Use markdown formatting and be thorough."""
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=options.get("max_tokens", 2500),
            temperature=options.get("temperature", 0.4),
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        return {
            "documentation": content,
            "doc_type": doc_type,
            "language": language,
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }