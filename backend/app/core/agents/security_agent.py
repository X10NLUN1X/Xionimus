"""Security Agent using OpenAI GPT"""
import logging
from typing import Dict, Any, Optional

from ...models.agent_models import AgentType
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """
    Security Agent powered by OpenAI GPT
    Analyzes code for security vulnerabilities
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.SECURITY, api_keys=api_keys)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate security analysis input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data:
            raise ValueError("Code is required for security analysis")
    
    def get_system_prompt(self) -> str:
        """Get security agent system prompt"""
        return """You are an expert security analyst. Identify security 
        vulnerabilities in code including:
        - Injection attacks (SQL, XSS, Command)
        - Authentication/Authorization flaws
        - Data exposure risks
        - Cryptographic issues
        - Input validation problems
        - Dependency vulnerabilities
        
        Provide severity ratings and remediation guidance."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze code for security issues"""
        code = input_data["code"]
        language = input_data.get("language", "unknown")
        context = input_data.get("context", "")
        
        # Build security analysis prompt
        prompt = f"""Perform a security audit of the following {language} code:

```{language}
{code}
```

"""
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += """
Analyze for security vulnerabilities:
1. **Injection Vulnerabilities**: SQL, XSS, Command injection
2. **Authentication/Authorization**: Access control issues
3. **Data Exposure**: Sensitive data handling
4. **Cryptography**: Weak crypto or improper use
5. **Input Validation**: Missing or weak validation
6. **Dependencies**: Known vulnerable dependencies

For each issue found:
- **Severity**: Critical/High/Medium/Low
- **Description**: What the vulnerability is
- **Impact**: Potential consequences
- **Remediation**: How to fix it

Provide an overall security score (1-10) and prioritized recommendations."""
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=options.get("temperature", 0.2),
            max_tokens=options.get("max_tokens", 2500)
        )
        
        content = response.choices[0].message.content
        
        return {
            "security_analysis": content,
            "language": language,
            "code_length": len(code),
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }