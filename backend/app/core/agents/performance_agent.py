"""Performance Agent using OpenAI GPT"""
import logging
from typing import Dict, Any, Optional

from ...models.agent_models import AgentType
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """
    Performance Agent powered by OpenAI GPT
    Analyzes code for performance optimization opportunities
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.PERFORMANCE, api_keys=api_keys)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate performance analysis input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data:
            raise ValueError("Code is required for performance analysis")
    
    def get_system_prompt(self) -> str:
        """Get performance agent system prompt"""
        return """You are an expert performance engineer. Analyze code for 
        performance optimization opportunities including:
        - Algorithm complexity
        - Data structure efficiency
        - Memory usage
        - I/O operations
        - Caching opportunities
        - Parallel processing potential
        
        Provide specific, actionable optimization recommendations."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze code for performance"""
        code = input_data["code"]
        language = input_data.get("language", "unknown")
        context = input_data.get("context", "")
        performance_goals = input_data.get("performance_goals", "")
        
        # Build performance analysis prompt
        prompt = f"""Analyze the following {language} code for performance optimization:

```{language}
{code}
```

"""
        if context:
            prompt += f"Context: {context}\n\n"
        
        if performance_goals:
            prompt += f"Performance Goals: {performance_goals}\n\n"
        
        prompt += """
Provide a comprehensive performance analysis:
1. **Time Complexity**: Current algorithm complexity
2. **Memory Usage**: Memory consumption patterns
3. **Bottlenecks**: Performance bottlenecks identified
4. **Optimizations**: Specific optimization opportunities with:
   - Current approach
   - Optimized approach
   - Expected improvement
5. **Best Practices**: Performance best practices to follow
6. **Rating**: Overall performance score (1-10)

Be specific with code examples where helpful."""
        
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
            "performance_analysis": content,
            "language": language,
            "code_length": len(code),
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }