"""
Smart Context Management for Xionimus AI
Intelligently manages conversation context to stay within token limits
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ContextManager:
    """Manage conversation context intelligently"""
    
    # Token limits for different models (approximate)
    MODEL_LIMITS = {
        'gpt-4o': 128000,
        'gpt-4.1': 128000,
        'gpt-5': 200000,
        'o1': 200000,
        'o3': 200000,
        'claude-sonnet-4-5-20250929': 200000,
        'claude-3-opus': 200000,
        'claude-3-sonnet': 200000,
        'sonar-pro': 127072,
        'sonar': 127072,
        'default': 8000
    }
    
    # Approximate tokens per character
    CHARS_PER_TOKEN = 4
    
    def __init__(self, model: str = 'gpt-4o'):
        """
        Initialize context manager
        
        Args:
            model: AI model name
        """
        self.model = model
        self.max_tokens = self._get_model_limit(model)
        # Reserve 25% for response
        self.context_budget = int(self.max_tokens * 0.75)
        
        logger.info(f"Context Manager initialized for {model} (budget: {self.context_budget} tokens)")
    
    def _get_model_limit(self, model: str) -> int:
        """Get token limit for model"""
        model_lower = model.lower()
        
        for key, limit in self.MODEL_LIMITS.items():
            if key in model_lower:
                return limit
        
        return self.MODEL_LIMITS['default']
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text"""
        return len(text) // self.CHARS_PER_TOKEN
    
    def calculate_message_priority(self, message: Dict[str, Any], index: int, total: int) -> float:
        """
        Calculate priority score for a message
        Higher score = more important to keep
        
        Args:
            message: Message dict
            index: Position in conversation
            total: Total messages
            
        Returns:
            Priority score (0-1)
        """
        priority = 0.5  # Base priority
        
        # Recent messages are more important
        recency = index / max(total, 1)
        priority += recency * 0.3
        
        # First message (often contains important context) is important
        if index <= 1:
            priority += 0.2
        
        # User messages slightly more important than assistant
        if message.get('role') == 'user':
            priority += 0.1
        
        # Shorter messages are less important (often acknowledgments)
        content_length = len(message.get('content', ''))
        if content_length < 50:
            priority -= 0.1
        elif content_length > 500:
            priority += 0.1
        
        # System messages are important
        if message.get('role') == 'system':
            priority += 0.3
        
        return max(0.0, min(1.0, priority))
    
    def prune_messages(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Intelligently prune messages to fit within token budget
        
        Args:
            messages: List of messages
            target_tokens: Target token count (uses context_budget if None)
            
        Returns:
            Pruned message list
        """
        if not messages:
            return messages
        
        target = target_tokens or self.context_budget
        
        # Calculate current token usage
        current_tokens = sum(self.estimate_tokens(m.get('content', '')) for m in messages)
        
        if current_tokens <= target:
            logger.info(f"No pruning needed: {current_tokens}/{target} tokens")
            return messages
        
        logger.info(f"Pruning messages: {current_tokens} -> {target} tokens")
        
        # Calculate priorities
        message_priorities = []
        for i, msg in enumerate(messages):
            priority = self.calculate_message_priority(msg, i, len(messages))
            tokens = self.estimate_tokens(msg.get('content', ''))
            message_priorities.append({
                'index': i,
                'message': msg,
                'priority': priority,
                'tokens': tokens
            })
        
        # Sort by priority (descending)
        message_priorities.sort(key=lambda x: x['priority'], reverse=True)
        
        # Select messages to keep
        kept_messages = []
        total_tokens = 0
        
        # Always keep first message (system/initial context)
        if message_priorities:
            first_msg = message_priorities[0]
            if first_msg['index'] == 0:
                kept_messages.append(first_msg)
                total_tokens += first_msg['tokens']
                message_priorities = message_priorities[1:]
        
        # Add messages by priority until budget exhausted
        for item in message_priorities:
            if total_tokens + item['tokens'] <= target:
                kept_messages.append(item)
                total_tokens += item['tokens']
        
        # Sort back to chronological order
        kept_messages.sort(key=lambda x: x['index'])
        
        # Extract just the messages
        result = [item['message'] for item in kept_messages]
        
        # Add truncation notice if messages were removed
        removed_count = len(messages) - len(result)
        if removed_count > 0:
            logger.info(f"Pruned {removed_count} messages, kept {len(result)}")
            
            # Add a system message indicating truncation
            if result and result[0].get('role') != 'system':
                result.insert(0, {
                    'role': 'system',
                    'content': f'[Note: {removed_count} less relevant messages from this conversation were omitted to stay within context limits]'
                })
        
        return result
    
    def summarize_old_messages(
        self,
        messages: List[Dict[str, Any]],
        keep_recent: int = 10
    ) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Create a summary of old messages and keep only recent ones
        
        Args:
            messages: Full message list
            keep_recent: Number of recent messages to keep
            
        Returns:
            Tuple of (summary string, recent messages)
        """
        if len(messages) <= keep_recent:
            return None, messages
        
        old_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]
        
        # Create summary
        summary_parts = [
            f"Previous conversation summary ({len(old_messages)} messages):\n"
        ]
        
        for msg in old_messages[::2]:  # Sample every other message
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # First 100 chars
            summary_parts.append(f"- {role}: {content}...")
        
        summary = "\n".join(summary_parts)
        
        return summary, recent_messages
    
    def optimize_context(
        self,
        messages: List[Dict[str, Any]],
        rag_context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Optimize full conversation context
        
        Args:
            messages: Conversation messages
            rag_context: Optional RAG context to include
            system_prompt: Optional system prompt
            
        Returns:
            Optimized message list
        """
        # Calculate token budget allocation
        rag_tokens = self.estimate_tokens(rag_context) if rag_context else 0
        system_tokens = self.estimate_tokens(system_prompt) if system_prompt else 0
        
        # Available tokens for conversation
        available_for_messages = self.context_budget - rag_tokens - system_tokens
        
        if available_for_messages < 1000:
            logger.warning(f"Very limited context budget: {available_for_messages} tokens")
        
        # Prune messages to fit
        pruned_messages = self.prune_messages(messages, available_for_messages)
        
        # Construct final message list
        final_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            final_messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add RAG context if provided
        if rag_context:
            final_messages.append({
                'role': 'system',
                'content': f"=== Relevant Context ===\n{rag_context}"
            })
        
        # Add pruned conversation
        final_messages.extend(pruned_messages)
        
        total_tokens = sum(self.estimate_tokens(m.get('content', '')) for m in final_messages)
        logger.info(f"Optimized context: {total_tokens}/{self.context_budget} tokens ({len(final_messages)} messages)")
        
        return final_messages
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        return {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'context_budget': self.context_budget,
            'response_budget': self.max_tokens - self.context_budget
        }
