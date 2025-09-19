import re
import ast
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
import anthropic

class CodeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Code Agent",
            description="Specialized in code generation, analysis, debugging, and optimization using Claude AI",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.DEBUGGING
            ]
        )
        self.ai_model = "claude"
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        code_keywords = [
            'code', 'programming', 'function', 'class', 'algorithm', 'debug', 'fix',
            'implement', 'python', 'javascript', 'react', 'api', 'database', 'sql',
            'bug', 'error', 'optimize', 'refactor', 'review', 'test', 'unittest',
            'create', 'build', 'develop', 'write', 'generate', 'component', 'module',
            'backend', 'frontend', 'fullstack', 'web development', 'app', 'application'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in code_keywords if keyword in description_lower)
        confidence = min(matches / 4, 1.0)
        
        # Boost confidence if specific code-related context is provided
        if context.get('file_extension') in ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css']:
            confidence += 0.3
        if context.get('project_type') in ['web', 'api', 'backend', 'frontend']:
            confidence += 0.2
        
        # Boost for code-specific verbs
        if any(verb in description_lower for verb in ['erstelle', 'generiere', 'schreibe', 'create', 'generate', 'write', 'build']):
            confidence += 0.2
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute code-related tasks using Claude AI"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing Claude for coding task")
            
            # Get Claude client
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise Exception("Anthropic API key not configured")
            
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Detect language for system message
            language = task.input_data.get('language', 'english')
            system_message = self._get_system_message(language)
            
            await self.update_progress(task, 0.3, "Analyzing coding requirements")
            
            task_type = self._identify_task_type(task.description)
            enhanced_prompt = self._create_coding_prompt(task.description, task_type, task.input_data)
            
            await self.update_progress(task, 0.6, f"Executing {task_type} with Claude")
            
            # Make API call to Claude
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                system=system_message,
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ]
            )
            
            await self.update_progress(task, 0.8, "Processing coding results")
            
            # Structure the code result
            content = response.content[0].text
            result = self._process_code_response(content, task_type, task.input_data)
            task.result = result
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Coding task completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Coding task failed: {str(e)}"
            self.logger.error(f"Code agent error: {e}")
            
        return task
    
    def _get_system_message(self, language: str) -> str:
        """Get system message in appropriate language"""
        messages = {
            'german': "Du bist ein erfahrener Software-Entwickler und Code-Experte. Du hilfst bei Code-Generierung, -Analyse, Debugging und Optimierung. Antworte präzise und mit gut kommentierten Code-Beispielen.",
            'english': "You are an experienced software developer and code expert. You help with code generation, analysis, debugging, and optimization. Respond precisely with well-commented code examples.",
            'spanish': "Eres un desarrollador de software experimentado y experto en código. Ayudas con generación de código, análisis, depuración y optimización. Responde con precisión y ejemplos de código bien comentados.",
            'french': "Vous êtes un développeur logiciel expérimenté et expert en code. Vous aidez avec la génération de code, l'analyse, le débogage et l'optimisation. Répondez avec précision et des exemples de code bien commentés.",
            'italian': "Sei uno sviluppatore software esperto e specialista del codice. Aiuti con generazione, analisi, debug e ottimizzazione del codice. Rispondi con precisione e esempi di codice ben commentati."
        }
        return messages.get(language, messages['english'])
    
    def _identify_task_type(self, description: str) -> str:
        """Identify the type of coding task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['generate', 'create', 'write', 'build', 'erstelle', 'generiere', 'schreibe']):
            return "code_generation"
        elif any(word in description_lower for word in ['analyze', 'review', 'examine', 'check', 'analysiere', 'überprüfe']):
            return "code_analysis"
        elif any(word in description_lower for word in ['debug', 'fix', 'error', 'bug', 'fehler', 'repariere']):
            return "debugging"
        elif any(word in description_lower for word in ['optimize', 'improve', 'refactor', 'optimiere', 'verbessere']):
            return "optimization"
        elif any(word in description_lower for word in ['test', 'testing', 'unittest', 'teste']):
            return "testing"
        else:
            return "general_coding"
    
    def _create_coding_prompt(self, description: str, task_type: str, input_data: Dict[str, Any]) -> str:
        """Create an enhanced prompt for coding tasks"""
        language = input_data.get('programming_language', input_data.get('language', 'python'))
        project_context = input_data.get('project_type', '')
        
        base_prompt = f"{description}\n\n"
        
        if task_type == "code_generation":
            base_prompt += f"""
Please generate clean, well-commented {language} code that follows best practices.
Include:
- Proper error handling
- Clear variable names
- Helpful comments
- Type hints (if applicable)
- Example usage (if appropriate)
"""
        elif task_type == "code_analysis":
            base_prompt += f"""
Please analyze the provided {language} code and provide:
- Code quality assessment
- Potential improvements
- Security considerations
- Performance optimizations
- Best practice recommendations
"""
        elif task_type == "debugging":
            base_prompt += f"""
Please help debug this {language} code:
- Identify the issues
- Explain why they occur
- Provide fixed code
- Suggest prevention strategies
"""
        elif task_type == "optimization":
            base_prompt += f"""
Please optimize this {language} code for:
- Better performance
- Improved readability
- Reduced complexity
- Memory efficiency
"""
        elif task_type == "testing":
            base_prompt += f"""
Please create comprehensive tests for this {language} code:
- Unit tests
- Edge cases
- Error conditions
- Integration tests (if applicable)
"""
        
        if project_context:
            base_prompt += f"\nProject context: {project_context}"
        
        return base_prompt
    
    def _process_code_response(self, response: str, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the AI response into structured format"""
        # Extract code blocks from response
        code_blocks = self._extract_code_blocks(response)
        language = input_data.get('programming_language', input_data.get('language', 'python'))
        
        result = {
            "type": task_type,
            "response_content": response,
            "code_blocks": code_blocks,
            "main_code": code_blocks[0] if code_blocks else "",
            "language": language,
            "ai_model_used": "claude",
            "explanation": self._extract_explanation(response),
            "files_generated": []
        }
        
        # Add task-specific fields
        if task_type == "code_generation":
            result.update({
                "dependencies": self._extract_dependencies(response),
                "usage_instructions": self._extract_usage_instructions(response)
            })
        elif task_type == "code_analysis":
            result.update({
                "issues_found": self._extract_issues(response),
                "recommendations": self._extract_recommendations(response),
                "quality_score": self._estimate_quality_score(response)
            })
        elif task_type == "debugging":
            result.update({
                "bugs_identified": self._extract_bugs(response),
                "fixes_applied": self._extract_fixes(response)
            })
        
        return result
    
    def _extract_code_blocks(self, response: str) -> List[str]:
        """Extract code blocks from the response"""
        import re
        code_pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        return matches
    
    def _extract_explanation(self, response: str) -> str:
        """Extract explanation text from response"""
        # Remove code blocks to get explanation
        import re
        without_code = re.sub(r'```(?:\w+)?\n.*?\n```', '', response, flags=re.DOTALL)
        return without_code.strip()[:500] + "..." if len(without_code.strip()) > 500 else without_code.strip()
    
    def _extract_dependencies(self, response: str) -> List[str]:
        """Extract dependencies from response"""
        dependencies = []
        lines = response.lower().split('\n')
        
        for line in lines:
            if 'import' in line or 'pip install' in line or 'yarn add' in line or 'npm install' in line:
                dependencies.append(line.strip())
        
        return dependencies[:10]  # Limit to 10 dependencies
    
    def _extract_usage_instructions(self, response: str) -> str:
        """Extract usage instructions from response"""
        lines = response.split('\n')
        instructions = []
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['usage', 'how to use', 'example', 'run']):
                # Take next few lines as instructions
                instructions.extend(lines[i:i+5])
                break
        
        return '\n'.join(instructions)
    
    def _extract_issues(self, response: str) -> List[str]:
        """Extract identified issues from analysis"""
        issues = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['issue', 'problem', 'error', 'warning']):
                issues.append(line.strip())
        
        return issues[:10]
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from analysis"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                recommendations.append(line.strip())
        
        return recommendations[:10]
    
    def _estimate_quality_score(self, response: str) -> float:
        """Estimate code quality score based on response"""
        positive_indicators = ['good', 'well', 'clean', 'proper', 'efficient']
        negative_indicators = ['poor', 'bad', 'issue', 'problem', 'error']
        
        response_lower = response.lower()
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        base_score = 7.0  # Base score
        score = base_score + (positive_count * 0.5) - (negative_count * 0.8)
        
        return max(1.0, min(10.0, score))
    
    def _extract_bugs(self, response: str) -> List[str]:
        """Extract identified bugs from debugging response"""
        bugs = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['bug', 'error', 'issue', 'problem', 'wrong']):
                bugs.append(line.strip())
        
        return bugs[:10]
    
    def _extract_fixes(self, response: str) -> List[str]:
        """Extract applied fixes from debugging response"""
        fixes = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['fix', 'fixed', 'corrected', 'resolved', 'solution']):
                fixes.append(line.strip())
        
        return fixes[:10]