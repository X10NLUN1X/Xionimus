import uuid
import asyncio
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent, AgentTask, AgentStatus
from .code_agent import CodeAgent
from .research_agent import ResearchAgent
from .writing_agent import WritingAgent
from .data_agent import DataAgent
from .qa_agent import QAAgent
from .github_agent import GitHubAgent
from .file_agent import FileAgent
from .session_agent import SessionAgent
from .language_detector import LanguageDetector
import logging
import asyncio
from datetime import datetime, timezone

class AgentManager:
    """Manages all agents and task routing"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_tasks: Dict[str, AgentTask] = {}
        self.task_lock = asyncio.Lock()
        self.language_detector = LanguageDetector()
        self.logger = logging.getLogger("agent_manager")
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        agents = [
            CodeAgent(),          # Claude - for coding tasks
            ResearchAgent(),      # Perplexity - for research and current information
            WritingAgent(),       # Claude - for documentation and content creation
            DataAgent(),          # Claude - for data analysis and visualization
            QAAgent(),           # Perplexity - for testing best practices
            GitHubAgent(),       # Perplexity - for GitHub operations and version control
            FileAgent(),         # Claude - for file management and organization
            SessionAgent(),      # Claude - for session management and forking
        ]
        
        for agent in agents:
            self.agents[agent.name] = agent
            self.logger.info(f"Initialized agent: {agent.name} (AI: {agent.ai_model})")
    
    async def process_request(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user request and route to appropriate agent"""
        if context is None:
            context = {}
        
        # Detect language
        language_info = self.language_detector.detect_language(user_message)
        context['language'] = language_info['language']
        context['language_confidence'] = language_info['confidence']
        
        # Determine if this requires an agent or direct AI response
        requires_agent = self._requires_agent_processing(user_message, context)
        
        if not requires_agent:
            return {
                "requires_agent": False,
                "language_info": language_info,
                "system_message": self.language_detector.get_system_message_for_language(language_info['language']),
                "enhanced_prompt": user_message
            }
        
        # Find best agent for the task
        best_agent = self._select_best_agent(user_message, context)
        
        if not best_agent:
            return {
                "requires_agent": False,
                "language_info": language_info,
                "system_message": self.language_detector.get_system_message_for_language(language_info['language']),
                "enhanced_prompt": user_message,
                "agent_recommendation": "No specialized agent found, using general AI response"
            }
        
        # Create and execute task
        task = AgentTask(
            id=str(uuid.uuid4()),
            agent_type=best_agent.name,
            description=user_message,
            input_data=context
        )
        
        async with self.task_lock:
            self.active_tasks[task.id] = task
        
        # Execute task asynchronously
        try:
            completed_task = await best_agent.execute_task(task)
            return {
                "requires_agent": True,
                "agent_used": best_agent.name,
                "task_id": task.id,
                "result": completed_task.result,
                "status": completed_task.status,
                "language_info": language_info,
                "steps": completed_task.steps
            }
        except Exception as e:
            self.logger.error(f"Agent execution error: {e}")
            return {
                "requires_agent": True,
                "agent_used": best_agent.name,
                "task_id": task.id,
                "error": str(e),
                "status": "error",
                "language_info": language_info
            }
    
    def _requires_agent_processing(self, message: str, context: Dict[str, Any]) -> bool:
        """Determine if the message requires specialized agent processing"""
        # Keywords that suggest agent processing is needed
        agent_keywords = [
            # Code-related
            'generate code', 'write code', 'create function', 'debug', 'fix code', 'analyze code',
            'review code', 'optimize', 'refactor', 'implement', 'algorithm',
            # Research-related
            'research', 'find information', 'compare', 'analyze market', 'trend analysis',
            'competitive analysis', 'gather data', 'investigate',
            # Complex task indicators
            'step by step', 'detailed analysis', 'comprehensive', 'thorough',
            'create project', 'build application', 'develop system'
        ]
        
        message_lower = message.lower()
        
        # Check for agent keywords
        for keyword in agent_keywords:
            if keyword in message_lower:
                return True
        
        # Check for complex task patterns
        if len(message.split()) > 15:  # Long, detailed requests
            return True
        
        # Check for multiple requirements
        if len([s for s in message.split('.') if s.strip()]) > 2:
            return True
        
        # Check context indicators
        if context.get('project_type') or context.get('file_extension'):
            return True
        
        return False
    
    def _select_best_agent(self, message: str, context: Dict[str, Any]) -> Optional[BaseAgent]:
        """Select the best agent for handling the message"""
        agent_scores = {}
        
        for agent_name, agent in self.agents.items():
            confidence = agent.can_handle_task(message, context)
            if confidence > 0:
                agent_scores[agent_name] = confidence
        
        if not agent_scores:
            return None
        
        # Return agent with highest confidence
        best_agent_name = max(agent_scores, key=agent_scores.get)
        
        # Only use agent if confidence is above threshold
        if agent_scores[best_agent_name] >= 0.3:
            return self.agents[best_agent_name]
        
        return None
    
    def get_agent_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.active_tasks:
            return None
        
        task = self.active_tasks[task_id]
        return {
            "task_id": task.id,
            "agent_type": task.agent_type,
            "status": task.status,
            "progress": task.progress,
            "current_step": task.current_step,
            "steps": task.steps,
            "result": task.result,
            "error_message": task.error_message
        }
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of all available agents"""
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.get_capabilities_description()
            }
            for agent in self.agents.values()
        ]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = AgentStatus.ERROR
            task.error_message = "Task cancelled by user"
            return True
        return False
    
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        current_time = datetime.now(timezone.utc)
        tasks_to_remove = []
        
        for task_id, task in self.active_tasks.items():
            # Calculate age (simplified - would need proper timestamp tracking)
            if task.status in [AgentStatus.COMPLETED, AgentStatus.ERROR] and len(self.active_tasks) > 100:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove[:50]:  # Remove oldest 50 tasks if too many
            del self.active_tasks[task_id]
        
        self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")