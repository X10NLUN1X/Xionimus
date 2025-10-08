"""Debugging Agent using Claude Opus 4.1"""
import logging
import re
from typing import Dict, Any, Optional, AsyncGenerator, List, Tuple
from datetime import datetime, timezone

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
    
    def _parse_stack_trace(self, stack_trace: str) -> Dict[str, Any]:
        """Parse stack trace to extract key information"""
        lines = stack_trace.split('\n')
        
        # Find error message
        error_line = None
        for line in lines:
            if 'Error:' in line or 'Exception:' in line:
                error_line = line.strip()
                break
        
        # Find file and line number
        file_info = []
        file_pattern = r'File "([^"]+)", line (\d+)'
        for match in re.finditer(file_pattern, stack_trace):
            file_info.append({
                "file": match.group(1),
                "line": int(match.group(2))
            })
        
        # Find function calls
        function_calls = re.findall(r'in (\w+)', stack_trace)
        
        return {
            "error_message": error_line,
            "affected_files": file_info,
            "function_calls": function_calls,
            "stack_depth": len(function_calls)
        }
    
    def _generate_test_case_prompt(self, error: str, code: str) -> str:
        """Generate prompt for test case generation"""
        return f"""
Based on this error: {error}

And this code:
```
{code}
```

Generate unit test cases that would catch this bug, including:
1. Test case that reproduces the bug
2. Test case for the fix
3. Edge case tests
4. Input validation tests
"""
    
    def _create_fix_diff(self, original_code: str, suggested_fix: str) -> str:
        """Create a diff-style representation of the fix"""
        # Simple diff representation
        return f"""
--- Original Code
+++ Fixed Code

{suggested_fix}
"""
    
    def get_system_prompt(self) -> str:
        """Get debugging agent system prompt"""
        return """You are an expert debugging assistant with deep knowledge of:
        - Root cause analysis
        - Error trace interpretation
        - Edge case identification
        - Multi-language debugging
        - System-level debugging
        - Test-driven debugging
        
        Provide thorough debugging analysis that includes:
        1. Root cause identification with stack trace analysis
        2. Step-by-step explanation
        3. Concrete fix suggestions with code examples
        4. Prevention strategies
        5. Test cases to verify the fix
        6. Related issues to check
        
        Be precise, methodical, and consider edge cases. Always provide working code examples."""
    
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
1. **Root Cause**: What is causing the error? (with stack trace analysis)
2. **Explanation**: Why is this happening? (step-by-step)
3. **Fix**: How to fix it with working code example
4. **Code Diff**: Show before/after code clearly
5. **Test Cases**: Unit tests to verify the fix
6. **Prevention**: How to prevent similar issues
7. **Related Checks**: Other potential issues to verify

Be specific, thorough, and provide executable code examples."""
        
        # Parse stack trace if provided
        stack_info = {}
        if stack_trace:
            stack_info = self._parse_stack_trace(stack_trace)
        
        # Call Claude Opus 4.1 API
        response = self.client.messages.create(
            model=self.model,  # claude-opus-4-20250514
            max_tokens=options.get("max_tokens", 4000),
            temperature=options.get("temperature", 0.2),
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        # Extract code blocks from response for fix suggestions
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        
        # Generate test cases if code is provided
        test_cases = []
        if code and error:
            try:
                test_prompt = self._generate_test_case_prompt(error, code)
                test_response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": test_prompt}
                    ]
                )
                test_cases_text = test_response.content[0].text
                test_code_blocks = re.findall(r'```[\w]*\n(.*?)```', test_cases_text, re.DOTALL)
                test_cases = test_code_blocks if test_code_blocks else []
            except Exception as e:
                logger.warning(f"Failed to generate test cases: {e}")
        
        return {
            "analysis": content,
            "error_provided": bool(error),
            "code_provided": bool(code),
            "stack_trace_provided": bool(stack_trace),
            "stack_trace_info": stack_info,
            "suggested_fixes": code_blocks[:3] if code_blocks else [],
            "test_cases": test_cases,
            "test_cases_count": len(test_cases),
            "model_used": self.model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "high" if "critical" in error.lower() or "fatal" in error.lower() else "medium",
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }