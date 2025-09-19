import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
from openai import AsyncOpenAI

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Specialized in web research, information gathering, and fact-checking using Perplexity AI",
            capabilities=[
                AgentCapability.WEB_RESEARCH
            ]
        )
        self.ai_model = "perplexity"
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        research_keywords = [
            'research', 'find', 'search', 'information', 'data', 'facts', 'analyze',
            'investigate', 'study', 'explore', 'gather', 'collect', 'compare',
            'market research', 'competitive analysis', 'trends', 'statistics',
            'what is', 'how to', 'explain', 'summarize', 'overview', 'latest',
            'current', 'news', 'developments', 'industry', 'market', 'report'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in research_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for question-like queries
        if any(description_lower.startswith(q) for q in ['what', 'how', 'why', 'when', 'where', 'who']):
            confidence += 0.3
        if '?' in task_description:
            confidence += 0.2
            
        # Boost for research-specific terms
        if any(term in description_lower for term in ['latest', 'current', 'trends', 'market', 'industry']):
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute research tasks using Perplexity AI"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing Perplexity research")
            
            # Get Perplexity client
            api_key = os.environ.get('PERPLEXITY_API_KEY')
            if not api_key:
                raise Exception("Perplexity API key not configured")
            
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            
            await self.update_progress(task, 0.3, "Analyzing research requirements")
            
            # Determine research type and create enhanced prompt
            task_type = self._identify_research_type(task.description)
            enhanced_prompt = self._create_research_prompt(task.description, task_type, task.input_data.get('language', 'english'))
            
            await self.update_progress(task, 0.5, "Conducting research with Perplexity")
            
            # Make API call to Perplexity
            response = await client.chat.completions.create(
                model="llama-3.1-sonar-huge-128k-online",
                messages=[
                    {"role": "system", "content": "You are a professional research assistant. Provide comprehensive, accurate, and well-sourced information."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more factual responses
                stream=False
            )
            
            await self.update_progress(task, 0.8, "Processing research results")
            
            content = response.choices[0].message.content
            sources = getattr(response, 'search_results', [])
            
            # Structure the research result
            task.result = {
                "type": task_type,
                "research_content": content,
                "sources": sources,
                "summary": self._extract_summary(content),
                "key_points": self._extract_key_points(content),
                "confidence": 0.9,
                "ai_model_used": "perplexity",
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Research completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Research failed: {str(e)}"
            self.logger.error(f"Research agent error: {e}")
            
        return task
    
    def _identify_research_type(self, description: str) -> str:
        """Identify the type of research task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return "comparative_research"
        elif any(word in description_lower for word in ['trend', 'trending', 'popular', 'growth', 'latest']):
            return "trend_analysis"
        elif any(word in description_lower for word in ['market', 'competitor', 'industry', 'business']):
            return "market_research"
        elif any(word in description_lower for word in ['what is', 'define', 'explain', 'meaning']):
            return "factual_research"
        elif any(word in description_lower for word in ['news', 'current', 'recent', 'today']):
            return "news_research"
        else:
            return "general_research"
    
    def _create_research_prompt(self, description: str, research_type: str, language: str) -> str:
        """Create an enhanced prompt for better research results"""
        language_instructions = {
            'german': "Bitte antworte auf Deutsch und verwende deutsche Quellen wo möglich.",
            'english': "Please respond in English and prioritize English sources.",
            'spanish': "Por favor responde en español y usa fuentes en español cuando sea posible.",
            'french': "Veuillez répondre en français et utiliser des sources françaises si possible.",
            'italian': "Si prega di rispondere in italiano e utilizzare fonti italiane quando possibile."
        }
        
        lang_instruction = language_instructions.get(language, language_instructions['english'])
        
        base_prompt = f"{description}\n\n{lang_instruction}\n\n"
        
        if research_type == "comparative_research":
            base_prompt += "Please provide a detailed comparison with pros and cons, and include recent data and sources."
        elif research_type == "trend_analysis":
            base_prompt += "Focus on current trends, recent developments, and future predictions with supporting data."
        elif research_type == "market_research":
            base_prompt += "Include market size, key players, growth trends, and competitive landscape analysis."
        elif research_type == "factual_research":
            base_prompt += "Provide accurate, well-sourced factual information with multiple authoritative sources."
        elif research_type == "news_research":
            base_prompt += "Focus on the most recent news and developments, including dates and sources."
        else:
            base_prompt += "Provide comprehensive information with multiple authoritative sources and current data."
        
        return base_prompt
    
    def _extract_summary(self, content: str) -> str:
        """Extract a brief summary from the research content"""
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines[:5]:  # Take first 5 lines as summary
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines)[:300] + "..." if len(' '.join(summary_lines)) > 300 else ' '.join(summary_lines)
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from the research content"""
        key_points = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                key_points.append(line[1:].strip())
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                key_points.append(line[2:].strip())
        
        return key_points[:10]  # Return max 10 key points