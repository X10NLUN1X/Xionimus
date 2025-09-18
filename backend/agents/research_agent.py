import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Specialized in web research, information gathering, and fact-checking",
            capabilities=[
                AgentCapability.WEB_RESEARCH
            ]
        )
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        research_keywords = [
            'research', 'find', 'search', 'information', 'data', 'facts', 'analyze',
            'investigate', 'study', 'explore', 'gather', 'collect', 'compare',
            'market research', 'competitive analysis', 'trends', 'statistics',
            'what is', 'how to', 'explain', 'summarize', 'overview'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in research_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for question-like queries
        if any(description_lower.startswith(q) for q in ['what', 'how', 'why', 'when', 'where']):
            confidence += 0.3
        if '?' in task_description:
            confidence += 0.2
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute research tasks"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Understanding research requirements")
            
            task_type = self._identify_research_type(task.description)
            
            if task_type == "factual":
                await self._handle_factual_research(task)
            elif task_type == "comparative":
                await self._handle_comparative_research(task)
            elif task_type == "trend":
                await self._handle_trend_analysis(task)
            elif task_type == "market":
                await self._handle_market_research(task)
            else:
                await self._handle_general_research(task)
                
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Research completed")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = str(e)
            self.logger.error(f"Research agent error: {e}")
            
        return task
    
    def _identify_research_type(self, description: str) -> str:
        """Identify the type of research task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return "comparative"
        elif any(word in description_lower for word in ['trend', 'trending', 'popular', 'growth']):
            return "trend"
        elif any(word in description_lower for word in ['market', 'competitor', 'industry', 'business']):
            return "market"
        elif any(word in description_lower for word in ['what is', 'define', 'explain', 'meaning']):
            return "factual"
        else:
            return "general"
    
    async def _handle_factual_research(self, task: AgentTask):
        """Handle factual research queries"""
        await self.update_progress(task, 0.3, "Searching for factual information")
        await self.update_progress(task, 0.6, "Verifying information accuracy")
        await self.update_progress(task, 0.8, "Compiling research findings")
        
        # This would integrate with Perplexity or other research APIs
        task.result = {
            "type": "factual_research",
            "summary": "Research summary would be generated here",
            "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
            "sources": ["Source 1", "Source 2", "Source 3"],
            "confidence": 0.9,
            "last_updated": "Recent information timestamp"
        }
    
    async def _handle_comparative_research(self, task: AgentTask):
        """Handle comparative research"""
        await self.update_progress(task, 0.3, "Identifying comparison subjects")
        await self.update_progress(task, 0.6, "Gathering comparative data")
        await self.update_progress(task, 0.8, "Analyzing differences and similarities")
        
        task.result = {
            "type": "comparative_research",
            "comparison_table": {},
            "key_differences": ["Difference 1", "Difference 2"],
            "similarities": ["Similarity 1", "Similarity 2"],
            "recommendation": "Based on comparison, recommendation would be here",
            "sources": []
        }
    
    async def _handle_trend_analysis(self, task: AgentTask):
        """Handle trend analysis research"""
        await self.update_progress(task, 0.3, "Identifying trend indicators")
        await self.update_progress(task, 0.6, "Analyzing trend data")
        await self.update_progress(task, 0.8, "Forecasting trend direction")
        
        task.result = {
            "type": "trend_analysis",
            "current_trends": ["Trend 1", "Trend 2"],
            "emerging_trends": ["Emerging trend 1"],
            "trend_direction": "upward/downward/stable",
            "forecast": "Future trend predictions",
            "impact_analysis": "Analysis of trend impacts"
        }
    
    async def _handle_market_research(self, task: AgentTask):
        """Handle market research"""
        await self.update_progress(task, 0.3, "Analyzing market landscape")
        await self.update_progress(task, 0.6, "Researching competitors")
        await self.update_progress(task, 0.8, "Compiling market insights")
        
        task.result = {
            "type": "market_research",
            "market_size": "Market size information",
            "key_players": ["Player 1", "Player 2"],
            "market_trends": ["Trend 1", "Trend 2"],
            "opportunities": ["Opportunity 1", "Opportunity 2"],
            "threats": ["Threat 1", "Threat 2"],
            "recommendations": "Strategic recommendations"
        }
    
    async def _handle_general_research(self, task: AgentTask):
        """Handle general research tasks"""
        await self.update_progress(task, 0.3, "Conducting comprehensive research")
        await self.update_progress(task, 0.6, "Analyzing information sources")
        await self.update_progress(task, 0.8, "Synthesizing research results")
        
        task.result = {
            "type": "general_research",
            "summary": "Comprehensive research summary",
            "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
            "detailed_findings": "Detailed research findings",
            "sources": ["Source 1", "Source 2", "Source 3"],
            "related_topics": ["Related topic 1", "Related topic 2"]
        }