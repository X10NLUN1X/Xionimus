"""
Context Manager für Xionimus AI
Verwaltet 200k Token Context-Fenster intelligent
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ContextManager:
    """Intelligentes Context-Management mit 200k Token Support"""
    
    # Maximale Token-Limits pro Modell
    MODEL_LIMITS = {
        'gpt-5': 200000,
        'o1': 200000,
        'o3': 200000,
        'claude-sonnet-4-5-20250514': 200000,
        'claude-3-opus': 200000,
        'claude-3-sonnet': 200000,
        'gpt-4o': 128000,
        'gpt-4.1': 128000,
        'sonar-pro': 127072,
        'sonar': 127072,
        'sonar-deep-research': 127072,
        'default': 8000
    }
    
    def __init__(self):
        """Initialize context manager"""
        # Try to load tiktoken for accurate counting (optional dependency)
        self.encoder = None
        try:
            import tiktoken
            self.encoder = tiktoken.encoding_for_model("gpt-4")
            logger.info("✅ Tiktoken encoder loaded for accurate token counting")
        except ImportError:
            logger.warning("⚠️ Tiktoken not installed. Using approximate counting (4 chars = 1 token).")
            logger.info("💡 Install tiktoken for accurate token counting: pip install tiktoken")
        except Exception as e:
            logger.warning(f"⚠️ Tiktoken error: {e}. Using approximate counting.")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        Uses tiktoken if available, otherwise approximates (4 chars = 1 token)
        """
        if self.encoder:
            try:
                return len(self.encoder.encode(text))
            except Exception as e:
                logger.warning(f"Tiktoken encoding failed: {e}, using approximation")
        
        # Fallback: approximate counting
        return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count total tokens in message list"""
        total = 0
        for msg in messages:
            # Add tokens for role (usually ~4 tokens)
            total += 4
            # Add content tokens
            total += self.count_tokens(msg.get('content', ''))
        
        # Add overhead for message formatting (~3 tokens per message)
        total += len(messages) * 3
        
        return total
    
    def get_model_limit(self, model: str) -> int:
        """Get token limit for specific model"""
        model_lower = model.lower()
        
        # Check for exact match
        if model_lower in self.MODEL_LIMITS:
            return self.MODEL_LIMITS[model_lower]
        
        # Check for partial match (e.g., 'gpt-5-turbo' matches 'gpt-5')
        for key, limit in self.MODEL_LIMITS.items():
            if key in model_lower:
                return limit
        
        return self.MODEL_LIMITS['default']
    
    def trim_context(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        reserve_tokens: int = 4000
    ) -> tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Trim context to fit within model limits
        Keeps system message and recent messages, removes middle messages
        
        Returns: (trimmed_messages, stats)
        """
        max_tokens = self.get_model_limit(model)
        target_tokens = max_tokens - reserve_tokens
        
        current_tokens = self.count_messages_tokens(messages)
        
        # If we're within limit, return as-is
        if current_tokens <= target_tokens:
            return messages, {
                'trimmed': False,
                'original_messages': len(messages),
                'original_tokens': current_tokens,
                'final_tokens': current_tokens,
                'model_limit': max_tokens,
                'reserved_for_response': reserve_tokens
            }
        
        # Need to trim
        logger.info(f"⚠️ Context trimming needed: {current_tokens} > {target_tokens} tokens")
        
        # Strategy: Keep system message (if any) + recent messages
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        non_system = [msg for msg in messages if msg.get('role') != 'system']
        
        # Start with system messages
        trimmed = system_messages.copy()
        tokens_used = self.count_messages_tokens(trimmed)
        
        # Add messages from the end (most recent)
        for msg in reversed(non_system):
            msg_tokens = self.count_tokens(msg.get('content', '')) + 7  # +7 for message overhead
            if tokens_used + msg_tokens <= target_tokens:
                trimmed.insert(len(system_messages), msg)
                tokens_used += msg_tokens
            else:
                break
        
        # Ensure chronological order (except system at start)
        if len(system_messages) > 0:
            trimmed = system_messages + trimmed[len(system_messages):]
        
        final_tokens = self.count_messages_tokens(trimmed)
        
        logger.info(f"✂️ Context trimmed: {len(messages)} → {len(trimmed)} messages, {current_tokens} → {final_tokens} tokens")
        
        return trimmed, {
            'trimmed': True,
            'original_messages': len(messages),
            'final_messages': len(trimmed),
            'removed_messages': len(messages) - len(trimmed),
            'original_tokens': current_tokens,
            'final_tokens': final_tokens,
            'model_limit': max_tokens,
            'reserved_for_response': reserve_tokens
        }
    
    def get_context_stats(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """Get detailed context statistics"""
        total_tokens = self.count_messages_tokens(messages)
        model_limit = self.get_model_limit(model)
        usage_percent = (total_tokens / model_limit) * 100
        
        return {
            'total_messages': len(messages),
            'total_tokens': total_tokens,
            'model': model,
            'model_limit': model_limit,
            'usage_percent': round(usage_percent, 2),
            'tokens_remaining': model_limit - total_tokens,
            'is_near_limit': usage_percent > 80,
            'breakdown': {
                'system': len([m for m in messages if m.get('role') == 'system']),
                'user': len([m for m in messages if m.get('role') == 'user']),
                'assistant': len([m for m in messages if m.get('role') == 'assistant'])
            }
        }

# Global instance
context_manager = ContextManager()
