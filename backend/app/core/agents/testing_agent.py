"""Testing Agent using OpenAI GPT"""
import logging
from typing import Dict, Any, Optional

from ...models.agent_models import AgentType
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TestingAgent(BaseAgent):
    """
    Testing Agent powered by OpenAI GPT
    Generates unit tests and test strategies
    """
    
    def __init__(self):
        super().__init__(AgentType.TESTING)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate testing input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data and "specification" not in input_data:
            raise ValueError("Either code or specification must be provided")
    
    def get_system_prompt(self) -> str:
        """Get testing agent system prompt"""
        return """You are an expert test engineer. Generate comprehensive, 
        well-structured unit tests that cover:
        - Happy path scenarios
        - Edge cases and boundary conditions
        - Error handling
        - Integration points
        
        Follow testing best practices and use appropriate testing frameworks."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate tests"""
        code = input_data.get("code", "")
        specification = input_data.get("specification", "")
        language = input_data.get("language", "python")
        test_framework = input_data.get("test_framework", "pytest")
        
        # Build test generation prompt
        prompt = f"""Generate comprehensive unit tests for the following:

"""
        if code:
            prompt += f"**Code to Test:**\n```{language}\n{code}\n```\n\n"
        
        if specification:
            prompt += f"**Specification:**\n{specification}\n\n"
        
        prompt += f"""
Generate tests using {test_framework} that cover:
1. **Happy path**: Normal use cases
2. **Edge cases**: Boundary conditions
3. **Error handling**: Invalid inputs and exceptions
4. **Integration**: Dependencies and side effects

Provide complete, runnable test code with clear test names and docstrings."""
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=options.get("temperature", 0.3),
            max_tokens=options.get("max_tokens", 2000)
        )
        
        content = response.choices[0].message.content
        
        return {
            "tests": content,
            "language": language,
            "test_framework": test_framework,
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }