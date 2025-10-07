"""Code Review Agent using Claude Sonnet 4"""
import logging
from typing import Dict, Any, Optional, AsyncGenerator

from ...models.agent_models import AgentType, AgentStreamChunk
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CodeReviewAgent(BaseAgent):
    """
    Code Review Agent powered by Claude Sonnet 4
    Reviews code for quality, bugs, and best practices
    """
    
    def __init__(self):
        super().__init__(AgentType.CODE_REVIEW)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate code review input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data:
            raise ValueError("Code is required for review")
        
        if not input_data["code"].strip():
            raise ValueError("Code cannot be empty")
    
    def get_system_prompt(self) -> str:
        """Get code review agent system prompt"""
        return """You are an expert code reviewer with deep knowledge of software 
        engineering best practices, design patterns, and common pitfalls. Provide 
        thorough, constructive code reviews that focus on:
        - Code quality and maintainability
        - Potential bugs and edge cases
        - Performance optimization opportunities
        - Security vulnerabilities
        - Best practices and design patterns
        
        Format your review with clear sections and actionable suggestions."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute code review"""
        code = input_data["code"]
        language = input_data.get("language", "unknown")
        context = input_data.get("context", "")
        
        # Build review prompt
        prompt = f"""Please review the following {language} code:

```{language}
{code}
```

"""
        if context:
            prompt += f"\nContext: {context}\n"
        
        prompt += """
Provide a comprehensive code review covering:
1. **Code Quality**: Overall structure, readability, maintainability
2. **Potential Issues**: Bugs, edge cases, error handling
3. **Performance**: Optimization opportunities
4. **Security**: Vulnerabilities or security concerns
5. **Best Practices**: Suggestions for improvement
6. **Rating**: Overall code quality score (1-10)

Be specific and provide examples where helpful."""
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=options.get("max_tokens", 2000),
            temperature=options.get("temperature", 0.3),
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        return {
            "review": content,
            "language": language,
            "code_length": len(code),
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }