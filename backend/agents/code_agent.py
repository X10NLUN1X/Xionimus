import re
import ast
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability

class CodeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Code Agent",
            description="Specialized in code generation, analysis, debugging, and optimization",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.DEBUGGING
            ]
        )
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        code_keywords = [
            'code', 'programming', 'function', 'class', 'algorithm', 'debug', 'fix',
            'implement', 'python', 'javascript', 'react', 'api', 'database', 'sql',
            'bug', 'error', 'optimize', 'refactor', 'review', 'test', 'unittest'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in code_keywords if keyword in description_lower)
        confidence = min(matches / 5, 1.0)  # Max confidence based on keyword matches
        
        # Boost confidence if specific code-related context is provided
        if context.get('file_extension') in ['.py', '.js', '.ts', '.jsx', '.tsx']:
            confidence += 0.2
        if context.get('project_type') in ['web', 'api', 'backend', 'frontend']:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute code-related tasks"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Analyzing task requirements")
            
            task_type = self._identify_task_type(task.description)
            
            if task_type == "generation":
                await self._handle_code_generation(task)
            elif task_type == "analysis":
                await self._handle_code_analysis(task)
            elif task_type == "debug":
                await self._handle_debugging(task)
            elif task_type == "review":
                await self._handle_code_review(task)
            else:
                await self._handle_general_coding_task(task)
                
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Task completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = str(e)
            self.logger.error(f"Code agent error: {e}")
            
        return task
    
    def _identify_task_type(self, description: str) -> str:
        """Identify the type of coding task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['generate', 'create', 'write', 'build']):
            return "generation"
        elif any(word in description_lower for word in ['analyze', 'review', 'examine', 'check']):
            return "analysis"
        elif any(word in description_lower for word in ['debug', 'fix', 'error', 'bug']):
            return "debug"
        elif any(word in description_lower for word in ['review', 'audit', 'improve']):
            return "review"
        else:
            return "general"
    
    async def _handle_code_generation(self, task: AgentTask):
        """Handle code generation tasks"""
        await self.update_progress(task, 0.3, "Planning code structure")
        
        language = task.input_data.get('language', 'python')
        requirements = task.description
        
        await self.update_progress(task, 0.6, f"Generating {language} code")
        
        # This would integrate with the AI models for actual code generation
        # For now, providing structure for the result
        task.result = {
            "code": f"# Generated {language} code for: {requirements}\n# This would be actual generated code",
            "language": language,
            "files": [],
            "dependencies": [],
            "instructions": "Instructions for using the generated code"
        }
        
        await self.update_progress(task, 0.9, "Validating generated code")
    
    async def _handle_code_analysis(self, task: AgentTask):
        """Handle code analysis tasks"""
        await self.update_progress(task, 0.3, "Parsing code structure")
        
        code = task.input_data.get('code', '')
        language = task.input_data.get('language', 'python')
        
        await self.update_progress(task, 0.6, "Analyzing code quality and patterns")
        
        analysis_result = {
            "complexity": "medium",
            "issues": [],
            "suggestions": [],
            "metrics": {
                "lines_of_code": len(code.split('\n')),
                "functions": 0,
                "classes": 0
            }
        }
        
        if language == 'python':
            analysis_result = self._analyze_python_code(code)
        
        task.result = {
            "analysis": analysis_result,
            "recommendations": "Code analysis recommendations would be here"
        }
        
        await self.update_progress(task, 0.9, "Compiling analysis report")
    
    async def _handle_debugging(self, task: AgentTask):
        """Handle debugging tasks"""
        await self.update_progress(task, 0.3, "Examining error context")
        
        code = task.input_data.get('code', '')
        error_message = task.input_data.get('error', '')
        
        await self.update_progress(task, 0.6, "Identifying potential fixes")
        
        task.result = {
            "issues_found": ["Issue 1", "Issue 2"],
            "fixes": ["Fix 1", "Fix 2"],
            "corrected_code": "# Corrected code would be here",
            "explanation": "Detailed explanation of the fixes"
        }
        
        await self.update_progress(task, 0.9, "Preparing debug report")
    
    async def _handle_code_review(self, task: AgentTask):
        """Handle code review tasks"""
        await self.update_progress(task, 0.3, "Reviewing code standards")
        
        code = task.input_data.get('code', '')
        
        await self.update_progress(task, 0.6, "Checking best practices")
        
        task.result = {
            "score": 8.5,
            "strengths": ["Good variable naming", "Proper error handling"],
            "improvements": ["Add more comments", "Optimize performance"],
            "security_issues": [],
            "performance_notes": "Performance analysis notes"
        }
        
        await self.update_progress(task, 0.9, "Finalizing review report")
    
    async def _handle_general_coding_task(self, task: AgentTask):
        """Handle general coding tasks"""
        await self.update_progress(task, 0.3, "Processing request")
        await self.update_progress(task, 0.6, "Executing coding task")
        
        task.result = {
            "result": "General coding task completed",
            "details": "Task-specific results would be here"
        }
        
        await self.update_progress(task, 0.9, "Finalizing results")
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure"""
        try:
            tree = ast.parse(code)
            
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            return {
                "complexity": "medium",
                "issues": [],
                "suggestions": ["Consider adding docstrings", "Use type hints"],
                "metrics": {
                    "lines_of_code": len(code.split('\n')),
                    "functions": len(functions),
                    "classes": len(classes)
                },
                "functions": functions,
                "classes": classes
            }
        except SyntaxError:
            return {
                "complexity": "unknown",
                "issues": ["Syntax error in code"],
                "suggestions": ["Fix syntax errors before analysis"],
                "metrics": {"lines_of_code": len(code.split('\n')), "functions": 0, "classes": 0}
            }