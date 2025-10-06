"""
Claude Smart Router - Phase 2
Intelligently routes between Claude Sonnet 4.5 and Opus 4.1 based on task complexity
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ClaudeRouter:
    """Smart routing between Claude models based on complexity"""
    
    # Keywords that indicate complex tasks requiring Opus 4.1
    COMPLEX_KEYWORDS = [
        # Code-related complexity
        "refactor", "architect", "design pattern", "optimize", "algorithm",
        "debug complex", "system design", "scalability", "performance",
        "multi-threaded", "concurrent", "distributed", "microservices",
        
        # Analysis complexity
        "comprehensive analysis", "deep dive", "thorough review", "detailed analysis",
        "root cause", "systematic", "investigate thoroughly",
        
        # Problem-solving complexity  
        "solve complex", "difficult problem", "challenging issue", "stuck",
        "not working", "broken", "failing", "error", "exception",
        
        # Research complexity
        "research", "compare multiple", "evaluate options", "pros and cons",
        "best practices", "industry standards",
        
        # Strategic thinking
        "strategy", "roadmap", "planning", "architecture decision",
        "technical debt", "migration plan"
    ]
    
    # Keywords that indicate code generation (needs Opus for better quality)
    CODE_GENERATION_KEYWORDS = [
        "create", "build", "implement", "generate", "write code",
        "develop", "construct", "make a", "add feature"
    ]
    
    def should_use_opus(self, messages: List[Dict[str, str]]) -> bool:
        """
        Determine if task requires Claude Opus 4.1 instead of Sonnet 4.5
        
        Args:
            messages: List of conversation messages
            
        Returns:
            True if Opus should be used, False for Sonnet
        """
        # Get the last user message (current request)
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "").lower()
                break
        
        if not last_user_message:
            return False
        
        # Check message length - very long messages often indicate complex tasks
        if len(last_user_message) > 1000:
            logger.info("🎯 Claude Router: Long message detected (>1000 chars) → Opus 4.1")
            return True
        
        # Check for complex keywords
        complex_matches = sum(1 for keyword in self.COMPLEX_KEYWORDS if keyword in last_user_message)
        if complex_matches >= 2:
            logger.info(f"🎯 Claude Router: Multiple complexity indicators ({complex_matches}) → Opus 4.1")
            return True
        
        # Check for code generation with error indicators
        has_code_gen = any(keyword in last_user_message for keyword in self.CODE_GENERATION_KEYWORDS)
        has_error = any(word in last_user_message for word in ["error", "bug", "broken", "not working", "failing"])
        
        if has_code_gen and has_error:
            logger.info("🎯 Claude Router: Code generation + error → Opus 4.1")
            return True
        
        # Check conversation history - if Sonnet struggled, escalate to Opus
        if len(messages) > 10:  # Long conversation might indicate difficulty
            recent_messages = messages[-10:]
            user_messages = [m for m in recent_messages if m.get("role") == "user"]
            
            # If user keeps asking follow-ups, might need Opus
            if len(user_messages) >= 5:
                logger.info("🎯 Claude Router: Long conversation (>5 user messages in last 10) → Opus 4.1")
                return True
        
        # Check for multi-file or multi-step requests
        multi_indicators = ["multiple files", "several files", "all files", "step by step", 
                          "first", "then", "next", "finally", "phase", "stage"]
        multi_matches = sum(1 for indicator in multi_indicators if indicator in last_user_message)
        
        if multi_matches >= 2:
            logger.info(f"🎯 Claude Router: Multi-step task detected → Opus 4.1")
            return True
        
        # Default to Sonnet 4.5 for standard tasks
        logger.info("✅ Claude Router: Standard task → Sonnet 4.5")
        return False
    
    def get_recommended_model(self, messages: List[Dict[str, str]], current_model: str) -> str:
        """
        Get recommended Claude model based on task complexity
        
        Args:
            messages: Conversation messages
            current_model: Currently selected model
            
        Returns:
            Recommended model name
        """
        # Only route if using Claude
        if "claude" not in current_model.lower():
            return current_model
        
        # If already using Opus, keep it
        if "opus" in current_model.lower():
            logger.info("✅ Already using Opus 4.1, maintaining selection")
            return current_model
        
        # Check if should upgrade to Opus
        if self.should_use_opus(messages):
            logger.info("🚀 Upgrading from Sonnet 4.5 to Opus 4.1 for complex task")
            return "claude-opus-4-1"
        
        # Keep Sonnet for standard tasks
        return current_model
    
    def get_fallback_model(self, failed_model: str) -> str:
        """
        Get fallback model if current model fails
        
        Args:
            failed_model: Model that failed
            
        Returns:
            Fallback model name
        """
        if "sonnet" in failed_model.lower():
            logger.info("⚠️ Sonnet 4.5 failed, falling back to Opus 4.1")
            return "claude-opus-4-1"
        
        if "opus" in failed_model.lower():
            logger.info("⚠️ Opus 4.1 failed, falling back to GPT-4o")
            return "gpt-4o"  # Ultimate fallback to OpenAI
        
        return failed_model

# Global router instance
claude_router = ClaudeRouter()
