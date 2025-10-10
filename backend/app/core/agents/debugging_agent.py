"""Debugging Agent - Enhanced Version with File System Access"""
import logging
import re
import os
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from pathlib import Path

from ...models.agent_models import AgentType, AgentStreamChunk
from ..base_agent import BaseAgent
from ..ai_manager import AIManager

logger = logging.getLogger(__name__)


class DebuggingAgent(BaseAgent):
    """
    Enhanced Debugging Agent with:
    - Proper API key handling
    - Local file system access
    - Auto-fix capability
    - Better error handling
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.DEBUGGING, api_keys=api_keys)
        self.ai_manager = AIManager()
        # Set up workspace paths
        self.backend_dir = Path(__file__).parent.parent.parent.parent
        self.workspace_dir = self.backend_dir / "workspace"
        self.project_root = self.backend_dir.parent
        
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate debugging input"""
        super()._validate_input(input_data)
        
        if "error" not in input_data and "code" not in input_data and "file_path" not in input_data:
            raise ValueError("Either error, code, or file_path must be provided")
    
    def _read_local_file(self, file_path: str) -> Optional[str]:
        """Read a file from local repository with multiple path resolution"""
        try:
            # Try multiple locations
            paths_to_try = [
                Path(file_path),  # Absolute or relative to CWD
                self.workspace_dir / file_path,  # Workspace relative
                self.backend_dir / file_path,  # Backend relative
                self.project_root / file_path,  # Project root relative
                Path.cwd() / file_path,  # Current dir relative
            ]
            
            for path in paths_to_try:
                if path.exists() and path.is_file():
                    logger.info(f"📁 Reading file from: {path}")
                    return path.read_text(encoding='utf-8')
                    
            logger.warning(f"⚠️ File not found in any location: {file_path}")
            return None
        except Exception as e:
            logger.error(f"❌ Error reading file {file_path}: {e}")
            return None
    
    def _write_local_file(self, file_path: str, content: str) -> bool:
        """Write fixed content back to local file with backup"""
        try:
            # Determine the correct path
            if Path(file_path).is_absolute():
                path = Path(file_path)
            else:
                # Try to find existing file first
                for base in [self.workspace_dir, self.backend_dir, self.project_root]:
                    test_path = base / file_path
                    if test_path.exists():
                        path = test_path
                        break
                else:
                    # Default to workspace if file doesn't exist
                    path = self.workspace_dir / file_path
            
            # Create backup if file exists
            if path.exists():
                backup_path = path.with_suffix(path.suffix + '.backup')
                backup_path.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
                logger.info(f"📋 Created backup: {backup_path}")
            
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write new content
            path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Fixed file written: {path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error writing file {file_path}: {e}")
            return False
    
    def _parse_stack_trace(self, stack_trace: str) -> Dict[str, Any]:
        """Enhanced stack trace parsing"""
        lines = stack_trace.split('\n')
        
        # Find error type and message
        error_type = None
        error_message = None
        for line in lines:
            if 'Error:' in line or 'Exception:' in line:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    error_type = parts[0].strip()
                    error_message = parts[1].strip()
                break
        
        # Find file and line information
        file_info = []
        file_pattern = r'File "([^"]+)", line (\d+)'
        for match in re.finditer(file_pattern, stack_trace):
            file_info.append({
                "file": match.group(1),
                "line": int(match.group(2))
            })
        
        # Find function calls
        function_calls = []
        func_pattern = r'in (\w+)'
        for match in re.finditer(func_pattern, stack_trace):
            function_calls.append(match.group(1))
        
        # Extract code snippets if present
        code_snippets = []
        for i, line in enumerate(lines):
            if line.strip().startswith('>'):
                code_snippets.append(line.strip())
        
        return {
            "error_type": error_type,
            "error_message": error_message,
            "affected_files": file_info,
            "function_calls": function_calls,
            "code_snippets": code_snippets,
            "stack_depth": len(function_calls)
        }
    
    def get_system_prompt(self) -> str:
        """Enhanced system prompt for debugging"""
        return """You are an expert debugging assistant specializing in:
        - Root cause analysis and error diagnosis
        - Stack trace interpretation
        - Edge case identification
        - Multi-language debugging (Python, JavaScript, TypeScript, etc.)
        - Performance optimization
        - Memory leak detection
        - Race condition analysis
        - File system operations and path resolution
        
        Provide comprehensive debugging analysis including:
        1. **Root Cause**: Precise identification of the error source
        2. **Explanation**: Clear step-by-step explanation of why the error occurs
        3. **Complete Fixed Code**: ALWAYS provide the ENTIRE fixed code, not snippets
        4. **Test Cases**: Comprehensive tests to verify the fix
        5. **Prevention**: Best practices to prevent similar issues
        6. **Performance Impact**: Any performance considerations
        7. **Related Issues**: Other potential problems to check
        
        CRITICAL INSTRUCTIONS:
        - Always provide COMPLETE fixed code wrapped in ```fixed_code``` tags
        - Include proper error handling in all fixes
        - Add comments explaining the changes
        - Consider edge cases and boundary conditions
        - Ensure backward compatibility when possible"""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute debugging with enhanced capabilities"""
        
        # Extract input parameters
        error = input_data.get("error", "")
        code = input_data.get("code", "")
        stack_trace = input_data.get("stack_trace", "")
        context = input_data.get("context", "")
        file_path = input_data.get("file_path", "")
        auto_fix = input_data.get("auto_fix", False)
        language = input_data.get("language", "python")
        
        # Read file if path provided and no code given
        file_content = None
        if file_path and not code:
            file_content = self._read_local_file(file_path)
            if file_content:
                code = file_content
                logger.info(f"📄 Loaded {len(file_content)} characters from {file_path}")
            else:
                return {
                    "success": False,
                    "error": f"Could not read file: {file_path}",
                    "file_path": file_path,
                    "suggestions": [
                        "Check if the file path is correct",
                        "Ensure the file exists",
                        "Verify file permissions"
                    ]
                }
        
        # Build comprehensive debugging prompt
        prompt_parts = ["I need help debugging an issue.\n"]
        
        if file_path:
            prompt_parts.append(f"**File:** `{file_path}`\n")
            prompt_parts.append(f"**Language:** {language}\n\n")
        
        if error:
            prompt_parts.append(f"**Error Message:**\n```\n{error}\n```\n\n")
        
        if stack_trace:
            prompt_parts.append(f"**Stack Trace:**\n```\n{stack_trace}\n```\n\n")
        
        if code:
            prompt_parts.append(f"**Code to Debug:**\n```{language}\n{code[:10000]}\n```\n\n")
            if len(code) > 10000:
                prompt_parts.append(f"(Code truncated, showing first 10000 characters of {len(code)} total)\n\n")
        
        if context:
            prompt_parts.append(f"**Additional Context:**\n{context}\n\n")
        
        prompt_parts.append("""
Please provide a comprehensive debugging analysis with:

1. **Root Cause Analysis**: What exactly is causing the error?
2. **Detailed Explanation**: Step-by-step explanation of the issue
3. **Complete Fixed Code**: The ENTIRE corrected code (wrap in ```fixed_code``` tags)
4. **Test Cases**: Unit tests to verify the fix (wrap in ```test``` tags)
5. **Prevention Strategies**: How to avoid this in the future
6. **Performance Considerations**: Any performance impacts
7. **Related Issues**: Other potential problems to check

IMPORTANT: Always provide the COMPLETE fixed code, not just the changes.""")
        
        prompt = "".join(prompt_parts)
        
        try:
            # Parse stack trace if provided
            stack_info = {}
            if stack_trace:
                stack_info = self._parse_stack_trace(stack_trace)
                logger.info(f"📊 Stack trace parsed: {stack_info.get('error_type', 'Unknown')}")
            
            # Validate API keys
            if not self.api_keys:
                logger.error("❌ No API keys provided to debugging agent")
                return {
                    "success": False,
                    "error": "No API keys configured",
                    "message": "Please configure API keys in Settings to use the debugging agent",
                    "required_keys": ["openai or anthropic"]
                }
            
            # Select best provider and model for debugging
            provider = None
            model = None
            
            if self.api_keys.get('anthropic'):
                provider = 'anthropic'
                model = 'claude-opus-4-1-20250805'  # Best for complex debugging
                logger.info("🤖 Using Claude Opus 4.1 (best for debugging)")
            elif self.api_keys.get('openai'):
                provider = 'openai'
                model = 'gpt-4o'  # Fallback option
                logger.info("🤖 Using GPT-4o as fallback")
            else:
                return {
                    "success": False,
                    "error": "No compatible API keys available",
                    "message": "Need either OpenAI or Anthropic API key",
                    "configured_keys": list(self.api_keys.keys())
                }
            
            # Prepare messages
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            # Call AI with error handling
            logger.info(f"🔍 Sending debugging request to {provider}/{model}")
            response = await self.ai_manager.generate_response(
                provider=provider,
                model=model,
                messages=messages,
                stream=False,
                api_keys=self.api_keys,
                max_tokens=options.get("max_tokens", 4000),
                temperature=options.get("temperature", 0.2)  # Low temperature for precision
            )
            
            content = response.get('content', '')
            
            if not content:
                logger.error("❌ Empty response from AI")
                return {
                    "success": False,
                    "error": "Empty response from AI model",
                    "provider": provider,
                    "model": model
                }
            
            # Extract fixed code
            fixed_code = None
            fixed_match = re.search(r'```fixed_code\n(.*?)```', content, re.DOTALL)
            if fixed_match:
                fixed_code = fixed_match.group(1)
            else:
                # Fallback: look for any code block after "fix" keywords
                for pattern in [r'```python\n(.*?)```', r'```javascript\n(.*?)```', r'```typescript\n(.*?)```', r'```\n(.*?)```']:
                    matches = re.findall(pattern, content, re.DOTALL)
                    for match in matches:
                        if len(match) > len(code) * 0.5:  # Likely the fixed version
                            fixed_code = match
                            break
                    if fixed_code:
                        break
            
            # Extract test cases
            test_cases = []
            test_pattern = r'```test\n(.*?)```'
            test_matches = re.findall(test_pattern, content, re.DOTALL)
            if test_matches:
                test_cases = test_matches
            else:
                # Look for test patterns in any code block
                all_code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
                for block in all_code_blocks:
                    if 'def test_' in block or 'describe(' in block or 'it(' in block or 'assert' in block:
                        test_cases.append(block)
            
            # Apply auto-fix if requested
            fix_applied = False
            backup_path = None
            if auto_fix and fixed_code and file_path:
                logger.info(f"🔧 Attempting auto-fix for {file_path}")
                fix_applied = self._write_local_file(file_path, fixed_code)
                if fix_applied:
                    backup_path = str(Path(file_path).with_suffix(Path(file_path).suffix + '.backup'))
                    logger.info(f"✅ Auto-fix applied! Backup saved to: {backup_path}")
            
            # Prepare response
            result = {
                "success": True,
                "analysis": content,
                "file_path": file_path,
                "error_provided": bool(error),
                "code_provided": bool(code or file_content),
                "stack_trace_provided": bool(stack_trace),
                "stack_trace_info": stack_info,
                "fixed_code": fixed_code,
                "has_fix": bool(fixed_code),
                "test_cases": test_cases,
                "test_cases_count": len(test_cases),
                "auto_fix_applied": fix_applied,
                "backup_path": backup_path,
                "model_used": f"{provider}/{model}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "severity": self._determine_severity(error, stack_trace),
                "token_usage": response.get('usage', {})
            }
            
            logger.info(f"✅ Debugging completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Debugging agent error: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Debugging agent failed: {str(e)}",
                "error_type": type(e).__name__,
                "file_path": file_path,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _determine_severity(self, error: str, stack_trace: str) -> str:
        """Determine error severity"""
        critical_keywords = ['fatal', 'critical', 'segfault', 'core dump', 'out of memory']
        high_keywords = ['error', 'exception', 'failed', 'undefined', 'null']
        
        combined_text = f"{error} {stack_trace}".lower()
        
        if any(keyword in combined_text for keyword in critical_keywords):
            return "critical"
        elif any(keyword in combined_text for keyword in high_keywords):
            return "high"
        else:
            return "medium"


# Export for external use
__all__ = ['DebuggingAgent']