from typing import Dict, Any, Optional, List
import logging
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Different types of AI tasks that require different models"""
    GENERAL_CONVERSATION = "general_conversation"
    CODE_ANALYSIS = "code_analysis"
    COMPLEX_REASONING = "complex_reasoning"
    RESEARCH_WEB = "research_web"
    CREATIVE_WRITING = "creative_writing"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    DEBUGGING = "debugging"
    SYSTEM_ANALYSIS = "system_analysis"

@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    provider: str
    model: str
    temperature: float = 0.7
    max_completion_tokens: int = 2000  # Updated parameter name for consistency
    system_message: str = "You are a helpful AI assistant."

class IntelligentAgentManager:
    """Intelligent agent manager that assigns optimal AI models for different tasks"""
    
    def __init__(self):
        # Import hybrid router for cost optimization
        from .hybrid_model_router import HybridModelRouter
        self.hybrid_router = HybridModelRouter()
        
        # AI Model assignments based on strengths
        self.agent_assignments = {
            TaskType.GENERAL_CONVERSATION: AgentConfig(
                provider="openai",
                model="gpt-4o-mini",  # ChatGPT-4o-mini - Cost-effective primary user chatbot
                temperature=0.8,
                system_message="You are ChatGPT, a helpful AI assistant. Be engaging, ask clarifying questions, and understand user needs before delegating technical tasks."
            ),
            TaskType.CODE_ANALYSIS: AgentConfig(
                provider="anthropic",
                model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 - Background only for coding tasks
                temperature=0.3,
                system_message="You are an expert code analyst working in the background. Provide detailed, accurate code analysis and suggestions. You are supporting ChatGPT, the primary user-facing assistant."
            ),
            TaskType.COMPLEX_REASONING: AgentConfig(
                provider="anthropic", 
                model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 for Coding
                temperature=0.5,
                system_message="You are an expert in complex reasoning and analysis. Think step by step and provide detailed explanations."
            ),
            TaskType.RESEARCH_WEB: AgentConfig(
                provider="perplexity",
                model="sonar-pro",  # Updated to current model
                temperature=0.6,
                system_message="You are a research assistant with access to real-time web information. Provide accurate, up-to-date information."
            ),
            TaskType.CREATIVE_WRITING: AgentConfig(
                provider="openai",
                model="gpt-4o",  # Changed from gpt-5 due to reasoning content issues
                temperature=0.9,
                system_message="You are a creative writing assistant. Be imaginative, engaging, and help with creative projects."
            ),
            TaskType.TECHNICAL_DOCUMENTATION: AgentConfig(
                provider="openai",
                model="gpt-4o-mini",  # 🎯 Hybrid: GPT-4o-mini for most docs (96% cheaper!)
                temperature=0.4,
                system_message="You are a technical documentation expert. Write clear, comprehensive, and well-structured documentation."
            ),
            TaskType.DEBUGGING: AgentConfig(
                provider="anthropic",
                model="claude-opus-4-1-20250805",  # Claude Opus 4.1 for Debugging
                temperature=0.3,
                system_message="You are a debugging expert with deep analytical capabilities. Help identify and fix issues systematically with thorough root cause analysis."
            ),
            TaskType.SYSTEM_ANALYSIS: AgentConfig(
                provider="anthropic",
                model="claude-opus-4-1-20250805",  # Claude Opus 4.1 for System Analysis
                temperature=0.4,
                system_message="You are a systems analyst with advanced reasoning. Provide thorough analysis of systems, architectures, and processes."
            )
        }
        
        # Fallback configurations
        self.fallback_order = {
            "openai": ["anthropic", "perplexity"],
            "anthropic": ["openai", "perplexity"], 
            "perplexity": ["openai", "anthropic"]
        }

    def detect_task_type(self, message: str, context: List[Dict[str, str]] = None) -> TaskType:
        """Intelligently detect the task type based on message content"""
        message_lower = message.lower()
        
        # Keywords for different task types
        code_keywords = ['code', 'function', 'bug', 'error', 'debug', 'programming', 'script', 'api', 'class', 'method']
        reasoning_keywords = ['analyze', 'explain', 'why', 'how', 'compare', 'evaluate', 'assess', 'reasoning']
        research_keywords = [
            'search', 'find', 'research', 'latest', 'current', 'news', 'information', 'data',
            'internet', 'web', 'online', 'suche', 'suchen', 'recherche', 'aktuell', 
            'neueste', 'nachrichten', 'informationen', 'lookup', 'browse', 'what is',
            'when did', 'who is', 'where is', 'tell me about', 'info about'
        ]
        creative_keywords = ['write', 'create', 'story', 'poem', 'creative', 'imagine', 'design']
        documentation_keywords = ['document', 'documentation', 'guide', 'manual', 'instructions', 'readme']
        debugging_keywords = ['fix', 'broken', 'error', 'issue', 'problem', 'troubleshoot', 'debug']
        system_keywords = ['system', 'architecture', 'design', 'structure', 'analysis', 'review']
        
        # Score each task type
        scores = {
            TaskType.CODE_ANALYSIS: sum(1 for keyword in code_keywords if keyword in message_lower),
            TaskType.COMPLEX_REASONING: sum(1 for keyword in reasoning_keywords if keyword in message_lower),
            TaskType.RESEARCH_WEB: sum(1 for keyword in research_keywords if keyword in message_lower),
            TaskType.CREATIVE_WRITING: sum(1 for keyword in creative_keywords if keyword in message_lower),
            TaskType.TECHNICAL_DOCUMENTATION: sum(1 for keyword in documentation_keywords if keyword in message_lower),
            TaskType.DEBUGGING: sum(1 for keyword in debugging_keywords if keyword in message_lower),
            TaskType.SYSTEM_ANALYSIS: sum(1 for keyword in system_keywords if keyword in message_lower)
        }
        
        # Find the highest scoring task type
        max_score = max(scores.values())
        if max_score > 0:
            for task_type, score in scores.items():
                if score == max_score:
                    return task_type
        
        # Default to general conversation
        return TaskType.GENERAL_CONVERSATION

    def get_optimal_agent(self, task_type: TaskType, available_providers: Dict[str, bool]) -> AgentConfig:
        """Get the optimal agent configuration for a task type"""
        
        preferred_config = self.agent_assignments[task_type]
        
        # Check if preferred provider is available
        if available_providers.get(preferred_config.provider, False):
            logger.info(f"🎯 Using optimal agent: {preferred_config.provider}/{preferred_config.model} for {task_type.value}")
            return preferred_config
        
        # Try fallback providers
        for fallback_provider in self.fallback_order.get(preferred_config.provider, []):
            if available_providers.get(fallback_provider, False):
                # Find a suitable config for this provider
                fallback_configs = [
                    config for config in self.agent_assignments.values() 
                    if config.provider == fallback_provider
                ]
                
                if fallback_configs:
                    fallback_config = fallback_configs[0]
                    logger.info(f"🔄 Using fallback agent: {fallback_config.provider}/{fallback_config.model} for {task_type.value}")
                    return fallback_config
        
        # If no providers available, return preferred anyway (will error appropriately)
        logger.warning(f"⚠️ No providers available for {task_type.value}, returning preferred config")
        return preferred_config

    def get_agent_recommendation(self, message: str, available_providers: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get agent recommendation for a message with Hybrid Routing
        Uses cost-optimized models for appropriate tasks
        """
        from .hybrid_model_router import TaskCategory
        
        task_type = self.detect_task_type(message)
        
        # 🎯 HYBRID ROUTING: Use cost-optimized models for docs and tests
        if task_type == TaskType.TECHNICAL_DOCUMENTATION:
            # Use hybrid router for documentation
            model_config = self.hybrid_router.get_model_for_documentation(message)
            return {
                "task_type": task_type.value,
                "recommended_provider": model_config["provider"],
                "recommended_model": model_config["model"],
                "reasoning": f"📊 Hybrid Routing: {model_config['reason']} (${model_config['cost_per_1m']}/1M, {model_config['quality']}% quality)",
                "temperature": 0.4,
                "max_completion_tokens": 2000,
                "system_message": "You are a technical documentation expert. Write clear, comprehensive, and well-structured documentation.",
                "hybrid_routing": True,
                "cost_savings": model_config.get("cost_per_1m", 0)
            }
        
        # For other tasks, use standard agent config
        agent_config = self.get_optimal_agent(task_type, available_providers)
        
        return {
            "task_type": task_type.value,
            "recommended_provider": agent_config.provider,
            "recommended_model": agent_config.model,
            "reasoning": f"Task detected as {task_type.value}, optimal model is {agent_config.model}",
            "temperature": agent_config.temperature,
            "max_completion_tokens": agent_config.max_completion_tokens,  # Updated parameter name
            "system_message": agent_config.system_message,
            "hybrid_routing": False
        }

    def get_all_assignments(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent assignments for documentation"""
        return {
            task_type.value: {
                "provider": config.provider,
                "model": config.model,
                "temperature": config.temperature,
                "use_case": task_type.value.replace('_', ' ').title()
            }
            for task_type, config in self.agent_assignments.items()
        }

# Global instance
intelligent_agent_manager = IntelligentAgentManager()