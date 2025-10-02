"""
Edit Agent - Autonomous Code Editing
Automatically edits existing code files based on bug fixes, improvements, or user requests
"""
import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import aiofiles
import asyncio

from .ai_manager import AIManager

logger = logging.getLogger(__name__)


class EditAgent:
    """
    Agent for editing existing code files
    Can work autonomously based on code review feedback or user-directed edits
    """
    
    WORKSPACE_ROOT = "/app/xionimus-ai"
    
    def __init__(self):
        self.ai_manager = AIManager()
        
    async def autonomous_edit(
        self, 
        code_review_feedback: Dict[str, Any],
        workspace_path: str = None
    ) -> Dict[str, Any]:
        """
        Autonomously edit files based on code review feedback
        
        Args:
            code_review_feedback: Feedback from code review agents
            workspace_path: Optional custom workspace path
            
        Returns:
            Dict with edit results and statistics
        """
        workspace = workspace_path or self.WORKSPACE_ROOT
        
        logger.info("🔧 Edit Agent: Starting autonomous edit process")
        
        # Extract issues that need fixing from code review
        issues_to_fix = self._extract_fixable_issues(code_review_feedback)
        
        if not issues_to_fix:
            logger.info("✅ No issues requiring code edits found")
            return {
                "status": "success",
                "message": "No edits needed",
                "files_edited": [],
                "edits_applied": 0
            }
        
        # Process each issue and generate edits
        edit_results = []
        for issue in issues_to_fix:
            try:
                result = await self._fix_issue(issue, workspace)
                if result:
                    edit_results.append(result)
            except Exception as e:
                logger.error(f"❌ Error fixing issue in {issue.get('file', 'unknown')}: {e}")
                edit_results.append({
                    "file": issue.get('file', 'unknown'),
                    "status": "error",
                    "error": str(e)
                })
        
        # Summarize results
        success_count = sum(1 for r in edit_results if r.get('status') == 'success')
        files_edited = [r['file'] for r in edit_results if r.get('status') == 'success']
        
        logger.info(f"✅ Edit Agent: Completed {success_count}/{len(edit_results)} edits")
        
        return {
            "status": "success" if success_count > 0 else "partial",
            "message": f"Applied {success_count} edits across {len(files_edited)} files",
            "files_edited": files_edited,
            "edits_applied": success_count,
            "edit_details": edit_results
        }
    
    async def user_directed_edit(
        self,
        file_path: str,
        edit_instructions: str,
        workspace_path: str = None
    ) -> Dict[str, Any]:
        """
        Edit a specific file based on user instructions
        
        Args:
            file_path: Path to file to edit (relative to workspace)
            edit_instructions: Natural language instructions for edits
            workspace_path: Optional custom workspace path
            
        Returns:
            Dict with edit result
        """
        workspace = workspace_path or self.WORKSPACE_ROOT
        full_path = os.path.join(workspace, file_path)
        
        logger.info(f"🔧 Edit Agent: User-directed edit for {file_path}")
        
        if not os.path.exists(full_path):
            logger.error(f"❌ File not found: {full_path}")
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
                "file": file_path
            }
        
        # Read current file content with retry logic for Windows
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                    current_content = await f.read()
                break  # Success, exit retry loop
            except (PermissionError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ File read attempt {attempt + 1} failed: {e}. Retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"❌ Error reading file {full_path} after {max_retries} attempts: {e}")
                    return {
                        "status": "error",
                        "message": f"Error reading file after {max_retries} attempts: {str(e)}",
                        "file": file_path
                    }
            except Exception as e:
                logger.error(f"❌ Unexpected error reading file {full_path}: {e}")
                return {
                    "status": "error",
                    "message": f"Error reading file: {str(e)}",
                    "file": file_path
                }
        
        # Generate edit using AI
        try:
            edited_content = await self._generate_edit(
                file_path=file_path,
                current_content=current_content,
                instructions=edit_instructions
            )
            
            if not edited_content:
                return {
                    "status": "error",
                    "message": "Failed to generate edit",
                    "file": file_path
                }
            
            # Write edited content back with retry logic for Windows
            max_retries = 3
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                try:
                    # Use atomic write pattern: write to temp, then move
                    import tempfile
                    temp_file = f"{full_path}.tmp.{os.getpid()}"
                    
                    try:
                        # Write to temp file first
                        async with aiofiles.open(temp_file, 'w', encoding='utf-8') as f:
                            await f.write(edited_content)
                        
                        # Atomic move (or copy+delete on Windows)
                        if os.name == 'nt':
                            # Windows: copy then delete
                            import shutil
                            shutil.copy2(temp_file, full_path)
                            os.remove(temp_file)
                        else:
                            # Unix: atomic rename
                            os.rename(temp_file, full_path)
                        
                        break  # Success, exit retry loop
                        
                    finally:
                        # Cleanup temp file if it still exists
                        if os.path.exists(temp_file):
                            try:
                                os.remove(temp_file)
                            except Exception:
                                pass
                                
                except (PermissionError, OSError) as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ File write attempt {attempt + 1} failed: {e}. Retrying...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"❌ Error writing file {full_path} after {max_retries} attempts: {e}")
                        return {
                            "status": "error",
                            "message": f"Error writing file after {max_retries} attempts: {str(e)}",
                            "file": file_path
                        }
            
            logger.info(f"✅ Successfully edited {file_path}")
            
            return {
                "status": "success",
                "message": f"Successfully edited {file_path}",
                "file": file_path,
                "changes": self._summarize_changes(current_content, edited_content)
            }
            
        except Exception as e:
            logger.error(f"❌ Error editing file {full_path}: {e}")
            return {
                "status": "error",
                "message": f"Error editing file: {str(e)}",
                "file": file_path
            }
    
    async def batch_edit(
        self,
        edit_requests: List[Dict[str, str]],
        workspace_path: str = None
    ) -> Dict[str, Any]:
        """
        Edit multiple files in batch
        
        Args:
            edit_requests: List of dicts with 'file' and 'instructions' keys
            workspace_path: Optional custom workspace path
            
        Returns:
            Dict with batch edit results
        """
        logger.info(f"🔧 Edit Agent: Batch editing {len(edit_requests)} files")
        
        results = []
        for request in edit_requests:
            result = await self.user_directed_edit(
                file_path=request['file'],
                edit_instructions=request['instructions'],
                workspace_path=workspace_path
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        
        return {
            "status": "success" if success_count > 0 else "error",
            "message": f"Completed {success_count}/{len(edit_requests)} edits",
            "results": results,
            "success_count": success_count,
            "total_requests": len(edit_requests)
        }
    
    def _extract_fixable_issues(self, code_review_feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract issues from code review that can be automatically fixed"""
        fixable_issues = []
        
        # Parse different types of code review feedback
        if isinstance(code_review_feedback, dict):
            # Debug agent feedback
            if 'debug_analysis' in code_review_feedback:
                debug_data = code_review_feedback['debug_analysis']
                if isinstance(debug_data, dict) and 'issues' in debug_data:
                    for issue in debug_data['issues']:
                        if issue.get('severity') in ['high', 'critical'] and issue.get('file'):
                            fixable_issues.append({
                                'file': issue['file'],
                                'line': issue.get('line'),
                                'issue': issue.get('description', ''),
                                'suggestion': issue.get('fix_suggestion', ''),
                                'type': 'bug'
                            })
            
            # Enhancement agent feedback
            if 'enhancements' in code_review_feedback:
                enhancements = code_review_feedback['enhancements']
                if isinstance(enhancements, list):
                    for enhancement in enhancements:
                        if enhancement.get('auto_fixable') and enhancement.get('file'):
                            fixable_issues.append({
                                'file': enhancement['file'],
                                'line': enhancement.get('line'),
                                'issue': enhancement.get('description', ''),
                                'suggestion': enhancement.get('suggestion', ''),
                                'type': 'enhancement'
                            })
        
        logger.info(f"📋 Extracted {len(fixable_issues)} fixable issues from code review")
        return fixable_issues
    
    async def _fix_issue(self, issue: Dict[str, Any], workspace: str) -> Optional[Dict[str, Any]]:
        """Fix a single issue"""
        file_path = issue['file']
        full_path = os.path.join(workspace, file_path)
        
        if not os.path.exists(full_path):
            logger.warning(f"⚠️ File not found: {full_path}")
            return None
        
        # Read current content
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            current_content = await f.read()
        
        # Generate fix instructions
        fix_instructions = f"""
Issue Type: {issue['type']}
Problem: {issue['issue']}
Suggested Fix: {issue.get('suggestion', 'Apply best practices to fix this issue')}
Line: {issue.get('line', 'unknown')}

Please fix this issue while preserving all other functionality.
"""
        
        # Generate edited content
        edited_content = await self._generate_edit(
            file_path=file_path,
            current_content=current_content,
            instructions=fix_instructions
        )
        
        if not edited_content or edited_content == current_content:
            logger.warning(f"⚠️ No changes generated for {file_path}")
            return None
        
        # Write back
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(edited_content)
        
        logger.info(f"✅ Fixed {issue['type']} in {file_path}")
        
        return {
            "status": "success",
            "file": file_path,
            "issue_type": issue['type'],
            "changes": self._summarize_changes(current_content, edited_content)
        }
    
    async def _generate_edit(
        self,
        file_path: str,
        current_content: str,
        instructions: str
    ) -> Optional[str]:
        """
        Use AI to generate edited version of file
        Uses Claude (Anthropic) as per project requirements
        """
        
        # Determine file type
        file_ext = Path(file_path).suffix
        language = self._get_language_from_extension(file_ext)
        
        # Create prompt for AI
        system_prompt = f"""You are an expert code editor. Your task is to edit existing code files precisely and carefully.

CRITICAL RULES:
1. Maintain all existing functionality unless specifically asked to change it
2. Preserve code style and formatting
3. Only make changes relevant to the instructions
4. Return ONLY the complete edited file content, no explanations
5. Do not add comments explaining changes unless requested
6. Ensure syntax is correct for {language}
7. Preserve all imports, dependencies, and structure
"""

        user_prompt = f"""Edit this {language} file: {file_path}

CURRENT CONTENT:
```{language}
{current_content}
```

EDIT INSTRUCTIONS:
{instructions}

Return the COMPLETE edited file content (no explanations, no markdown, just the code):"""

        try:
            # Use Claude for editing (as per project requirements)
            messages = [{"role": "user", "content": user_prompt}]
            
            response = await self.ai_manager.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-5-20250514",
                messages=messages,
                system_message=system_prompt,
                stream=False,
                api_keys=None
            )
            
            edited_content = response.get('content', '').strip()
            
            # Clean up if AI wrapped in code blocks
            if edited_content.startswith('```'):
                # Remove code block markers
                lines = edited_content.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].startswith('```'):
                    lines = lines[:-1]
                edited_content = '\n'.join(lines)
            
            return edited_content
            
        except Exception as e:
            logger.error(f"❌ AI generation error for {file_path}: {e}")
            return None
    
    def _get_language_from_extension(self, ext: str) -> str:
        """Get language name from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sh': 'bash',
            '.sql': 'sql'
        }
        return ext_map.get(ext.lower(), 'text')
    
    def _summarize_changes(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Summarize changes between old and new content"""
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        # Simple diff statistics
        lines_added = len(new_lines) - len(old_lines)
        
        return {
            "old_lines": len(old_lines),
            "new_lines": len(new_lines),
            "lines_changed": abs(lines_added),
            "size_change": len(new_content) - len(old_content)
        }
    
    async def analyze_and_suggest_edits(
        self,
        workspace_path: str = None
    ) -> Dict[str, Any]:
        """
        Analyze workspace and suggest potential edits
        Returns suggestions without applying them
        """
        workspace = workspace_path or self.WORKSPACE_ROOT
        
        logger.info("🔍 Edit Agent: Analyzing workspace for potential edits")
        
        # Find all code files
        code_files = self._find_code_files(workspace)
        
        suggestions = []
        for file_path in code_files[:10]:  # Limit to first 10 files
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # Quick analysis for common issues
                file_suggestions = self._quick_analyze_file(file_path, content)
                if file_suggestions:
                    suggestions.extend(file_suggestions)
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not analyze {file_path}: {e}")
        
        return {
            "status": "success",
            "suggestions": suggestions,
            "files_analyzed": len(code_files)
        }
    
    def _find_code_files(self, workspace: str) -> List[str]:
        """Find all code files in workspace"""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css'}
        code_files = []
        
        try:
            for root, dirs, files in os.walk(workspace):
                # Skip node_modules, .git, etc.
                dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'venv']]
                
                for file in files:
                    if Path(file).suffix in code_extensions:
                        code_files.append(os.path.join(root, file))
        except Exception as e:
            logger.error(f"❌ Error finding code files: {e}")
        
        return code_files
    
    def _quick_analyze_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Quick static analysis for common issues"""
        suggestions = []
        rel_path = file_path.replace(self.WORKSPACE_ROOT + '/', '')
        
        # Python-specific checks
        if file_path.endswith('.py'):
            # Check for print statements (should use logging)
            if 'print(' in content and 'logger' not in content:
                suggestions.append({
                    "file": rel_path,
                    "issue": "Using print() instead of logging",
                    "severity": "low",
                    "suggestion": "Replace print() with proper logging"
                })
            
            # Check for bare except clauses
            if re.search(r'except\s*:', content):
                suggestions.append({
                    "file": rel_path,
                    "issue": "Bare except clause found",
                    "severity": "medium",
                    "suggestion": "Specify exception types"
                })
        
        # JavaScript/TypeScript checks
        if file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            # Check for console.log
            if 'console.log' in content:
                suggestions.append({
                    "file": rel_path,
                    "issue": "console.log statements found",
                    "severity": "low",
                    "suggestion": "Remove or replace with proper logging"
                })
        
        return suggestions


# Global instance
edit_agent = EditAgent()
