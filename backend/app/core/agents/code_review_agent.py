"""Code Review Agent using Claude Sonnet 4"""
import logging
import re
from typing import Dict, Any, Optional, AsyncGenerator, List
from datetime import datetime, timezone

from ...models.agent_models import AgentType, AgentStreamChunk
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CodeReviewAgent(BaseAgent):
    """
    Code Review Agent powered by Claude Sonnet 4
    Reviews code for quality, bugs, and best practices
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.CODE_REVIEW, api_keys=api_keys)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate code review input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data:
            raise ValueError("Code is required for review")
        
        if not input_data["code"].strip():
            raise ValueError("Code cannot be empty")
    
    def _calculate_complexity_score(self, code: str) -> int:
        """Calculate approximate cyclomatic complexity"""
        # Count decision points
        complexity = 1  # Base complexity
        
        # Decision keywords
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', '&&', '||', '?']
        
        for keyword in decision_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', code, re.IGNORECASE))
        
        return min(complexity, 100)  # Cap at 100
    
    def _extract_security_issues(self, review_text: str) -> List[str]:
        """Extract security vulnerabilities from review"""
        security_keywords = [
            'security', 'vulnerability', 'SQL injection', 'XSS', 'CSRF',
            'authentication', 'authorization', 'sensitive data', 'encryption',
            'password', 'token', 'injection', 'sanitize', 'validate'
        ]
        
        issues = []
        lines = review_text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in security_keywords):
                issues.append(line.strip())
        
        return issues[:10]  # Return top 10 security concerns
    
    def _extract_quality_score(self, review_text: str) -> int:
        """Extract quality score from review text"""
        # Look for rating patterns
        score_patterns = [
            r'rating[:\s]*(\d+)[/\s]*10',
            r'score[:\s]*(\d+)[/\s]*10',
            r'quality[:\s]*(\d+)[/\s]*10',
            r'(\d+)[/\s]*10\s*(?:rating|score|quality)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, review_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Default score based on content analysis
        negative_indicators = ['bug', 'issue', 'problem', 'error', 'vulnerable', 'poor']
        positive_indicators = ['good', 'well', 'excellent', 'clean', 'efficient', 'solid']
        
        negative_count = sum(review_text.lower().count(word) for word in negative_indicators)
        positive_count = sum(review_text.lower().count(word) for word in positive_indicators)
        
        if negative_count > positive_count * 2:
            return 4
        elif negative_count > positive_count:
            return 6
        elif positive_count > negative_count:
            return 8
        else:
            return 7
    
    def get_system_prompt(self) -> str:
        """Get code review agent system prompt"""
        return """You are an expert code reviewer with deep knowledge of software 
        engineering best practices, design patterns, and common pitfalls. Provide 
        thorough, constructive code reviews that focus on:
        - Code quality and maintainability
        - Potential bugs and edge cases
        - Performance optimization opportunities
        - Security vulnerabilities (SQL injection, XSS, CSRF, etc.)
        - Best practices and design patterns
        - Complexity analysis
        
        Format your review with clear sections and actionable suggestions.
        Always provide a quality rating (1-10) at the end."""
    
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
3. **Performance**: Optimization opportunities with specific suggestions
4. **Security**: Vulnerabilities (SQL injection, XSS, CSRF, input validation, etc.)
5. **Best Practices**: Suggestions for improvement with examples
6. **Complexity**: Code complexity analysis
7. **Rating**: Overall code quality score (1-10) with justification

Be specific and provide examples where helpful. For security issues, be explicit about the risk level."""
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=options.get("max_tokens", 3000),
            temperature=options.get("temperature", 0.3),
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        # Calculate complexity
        complexity = self._calculate_complexity_score(code)
        
        # Extract security issues
        security_issues = self._extract_security_issues(content)
        
        # Extract quality score
        quality_score = self._extract_quality_score(content)
        
        # Performance analysis
        performance_concerns = []
        perf_keywords = ['loop', 'nested', 'O(n', 'inefficient', 'slow', 'optimize', 'cache']
        for line in content.split('\n'):
            if any(keyword in line.lower() for keyword in perf_keywords):
                performance_concerns.append(line.strip())
        
        return {
            "review": content,
            "language": language,
            "code_length": len(code),
            "quality_score": quality_score,
            "complexity_score": complexity,
            "security_issues": security_issues,
            "security_issues_count": len(security_issues),
            "performance_concerns": performance_concerns[:5],
            "lines_of_code": len(code.split('\n')),
            "model_used": self.model,
            "report_generated": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }