import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
import anthropic

class WritingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Writing Agent",
            description="Specialized in documentation, content creation, and technical writing using Claude AI",
            capabilities=[
                AgentCapability.WRITING
            ]
        )
        self.ai_model = "claude"
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        writing_keywords = [
            'write', 'create', 'documentation', 'document', 'readme', 'guide',
            'tutorial', 'manual', 'content', 'article', 'blog', 'post',
            'description', 'summary', 'report', 'proposal', 'specification',
            'schreibe', 'erstelle', 'dokumentation', 'anleitung', 'beschreibung',
            'inhalt', 'artikel', 'bericht', 'zusammenfassung', 'specification',
            'api documentation', 'user guide', 'help text', 'instructions'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in writing_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for documentation-specific terms
        if any(term in description_lower for term in ['readme', 'documentation', 'guide', 'manual', 'tutorial']):
            confidence += 0.4
        
        # Boost for writing-specific verbs
        if any(verb in description_lower for verb in ['write', 'create', 'document', 'explain']):
            confidence += 0.2
            
        # Boost if file extension suggests documentation
        if context.get('file_extension') in ['.md', '.txt', '.rst', '.adoc']:
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute writing tasks using Claude AI"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing Claude for writing task")
            
            # Get Claude client
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise Exception("Anthropic API key not configured")
            
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Detect language for system message
            language = task.input_data.get('language', 'english')
            system_message = self._get_system_message(language)
            
            await self.update_progress(task, 0.3, "Analyzing writing requirements")
            
            task_type = self._identify_writing_type(task.description)
            enhanced_prompt = self._create_writing_prompt(task.description, task_type, task.input_data)
            
            await self.update_progress(task, 0.6, f"Creating {task_type} with Claude")
            
            # Make API call to Claude 3.5 Sonnet (correct model)
            response = await client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4000,
                temperature=0.7,
                system=system_message,
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ]
            )
            
            await self.update_progress(task, 0.8, "Processing writing results")
            
            # Structure the writing result
            content = response.content[0].text
            result = self._process_writing_response(content, task_type, task.input_data)
            task.result = result
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Writing task completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Writing task failed: {str(e)}"
            self.logger.error(f"Writing agent error: {e}")
            
        return task
    
    def _get_system_message(self, language: str) -> str:
        """Get system message in appropriate language"""
        messages = {
            'german': "Du bist ein professioneller technischer Redakteur und Content-Spezialist. Du erstellst klare, gut strukturierte Dokumentationen und Inhalte. Achte auf präzise Sprache und gute Lesbarkeit.",
            'english': "You are a professional technical writer and content specialist. You create clear, well-structured documentation and content. Focus on precise language and excellent readability.",
            'spanish': "Eres un redactor técnico profesional y especialista en contenido. Creas documentación y contenido claro y bien estructurado. Concéntrate en un lenguaje preciso y excelente legibilidad.",
            'french': "Vous êtes un rédacteur technique professionnel et spécialiste du contenu. Vous créez une documentation et un contenu clairs et bien structurés. Concentrez-vous sur un langage précis et une excellente lisibilité.",
            'italian': "Sei un redattore tecnico professionale e specialista dei contenuti. Crei documentazione e contenuti chiari e ben strutturati. Concentrati su un linguaggio preciso e un'eccellente leggibilità."
        }
        return messages.get(language, messages['english'])
    
    def _identify_writing_type(self, description: str) -> str:
        """Identify the type of writing task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['readme', 'readme.md']):
            return "readme"
        elif any(word in description_lower for word in ['api', 'documentation', 'api doc']):
            return "api_documentation"
        elif any(word in description_lower for word in ['tutorial', 'guide', 'how to', 'anleitung']):
            return "tutorial_guide"
        elif any(word in description_lower for word in ['manual', 'user guide', 'handbuch']):
            return "user_manual"
        elif any(word in description_lower for word in ['report', 'analysis', 'bericht', 'analyse']):
            return "report"
        elif any(word in description_lower for word in ['proposal', 'specification', 'spec']):
            return "specification"
        elif any(word in description_lower for word in ['blog', 'article', 'post', 'artikel']):
            return "blog_article"
        else:
            return "general_content"
    
    def _create_writing_prompt(self, description: str, writing_type: str, input_data: Dict[str, Any]) -> str:
        """Create an enhanced prompt for writing tasks"""
        language = input_data.get('language', 'english')
        project_context = input_data.get('project_type', '')
        target_audience = input_data.get('target_audience', 'general')
        
        base_prompt = f"{description}\n\n"
        
        if writing_type == "readme":
            base_prompt += """
Create a comprehensive README.md that includes:
- Project title and description
- Installation instructions
- Usage examples
- API documentation (if applicable)
- Contributing guidelines
- License information
- Contact information
"""
        elif writing_type == "api_documentation":
            base_prompt += """
Create detailed API documentation that includes:
- Overview of the API
- Authentication methods
- Endpoint descriptions
- Request/response examples
- Error codes and handling
- Rate limiting information
- SDK examples
"""
        elif writing_type == "tutorial_guide":
            base_prompt += """
Create a step-by-step tutorial that includes:
- Clear learning objectives
- Prerequisites
- Detailed steps with explanations
- Code examples and screenshots
- Common troubleshooting
- Next steps and resources
"""
        elif writing_type == "user_manual":
            base_prompt += """
Create a comprehensive user manual that includes:
- Getting started guide
- Feature explanations
- Step-by-step procedures
- Screenshots and examples
- FAQ section
- Troubleshooting guide
"""
        elif writing_type == "report":
            base_prompt += """
Create a professional report that includes:
- Executive summary
- Detailed analysis
- Data and statistics
- Conclusions and recommendations
- Appendices (if needed)
"""
        elif writing_type == "specification":
            base_prompt += """
Create a technical specification that includes:
- Overview and scope
- Technical requirements
- System architecture
- Implementation details
- Testing criteria
- Acceptance criteria
"""
        elif writing_type == "blog_article":
            base_prompt += """
Create an engaging blog article that includes:
- Compelling headline
- Introduction hook
- Well-structured content
- Practical examples
- Conclusion with key takeaways
- Call to action
"""
        
        if project_context:
            base_prompt += f"\nProject context: {project_context}"
        
        base_prompt += f"\nTarget audience: {target_audience}"
        base_prompt += f"\nPlease write in a clear, professional style appropriate for {target_audience}."
        
        return base_prompt
    
    def _process_writing_response(self, response: str, writing_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the AI response into structured format"""
        result = {
            "type": writing_type,
            "content": response,
            "word_count": len(response.split()),
            "language": input_data.get('language', 'english'),
            "ai_model_used": "claude",
            "sections": self._extract_sections(response),
            "format": "markdown" if "```" in response or "#" in response else "text"
        }
        
        # Add writing-type specific fields
        if writing_type == "readme":
            result.update({
                "filename": "README.md",
                "has_installation": "installation" in response.lower(),
                "has_usage": "usage" in response.lower(),
                "has_license": "license" in response.lower()
            })
        elif writing_type == "api_documentation":
            result.update({
                "endpoints_documented": self._count_endpoints(response),
                "has_examples": "example" in response.lower(),
                "has_authentication": "auth" in response.lower()
            })
        elif writing_type == "tutorial_guide":
            result.update({
                "steps_count": self._count_steps(response),
                "has_code_examples": "```" in response,
                "estimated_duration": self._estimate_tutorial_duration(response)
            })
        
        return result
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content"""
        import re
        # Look for markdown headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return headers[:10]  # Return first 10 headers
    
    def _count_endpoints(self, content: str) -> int:
        """Count API endpoints mentioned in documentation"""
        import re
        # Look for HTTP methods and endpoints
        endpoints = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+[/\w-]+', content, re.IGNORECASE)
        return len(endpoints)
    
    def _count_steps(self, content: str) -> int:
        """Count numbered steps in tutorial"""
        import re
        steps = re.findall(r'^\d+\.\s+', content, re.MULTILINE)
        return len(steps)
    
    def _estimate_tutorial_duration(self, content: str) -> str:
        """Estimate tutorial completion time based on content length"""
        word_count = len(content.split())
        code_blocks = content.count('```')
        
        # Rough estimation: 200 words per minute reading + extra time for code
        reading_time = word_count / 200
        coding_time = code_blocks * 5  # 5 minutes per code block
        
        total_minutes = reading_time + coding_time
        
        if total_minutes < 10:
            return "5-10 minutes"
        elif total_minutes < 30:
            return "15-30 minutes"
        elif total_minutes < 60:
            return "30-60 minutes"
        else:
            return "1+ hours"