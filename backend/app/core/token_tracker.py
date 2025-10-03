"""
Token Usage Tracker
Tracks token consumption across sessions and provides recommendations
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import tempfile

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("⚠️ Tiktoken not installed. Using approximate counting (4 chars = 1 token).")
    print("   Install with: pip install tiktoken")
    logging.info("ℹ️ tiktoken not available - using character-based estimation (4 chars = 1 token)")

logger = logging.getLogger(__name__)


class TokenUsageTracker:
    """Track token usage and provide fork/summary recommendations"""
    
    def __init__(self):
        # Use XDG_RUNTIME_DIR if available, otherwise create in system temp with proper permissions
        if os.environ.get('XDG_RUNTIME_DIR'):
            storage_dir = Path(os.environ['XDG_RUNTIME_DIR'])
        else:
            storage_dir = Path(tempfile.gettempdir()) / 'xionimus'
            storage_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        self.storage_file = storage_dir / "xionimus_token_usage.json"
        self.load_usage()
        
        # Limits and thresholds
        self.SOFT_LIMIT = 50000  # Start showing warnings
        self.HARD_LIMIT = 100000  # Recommend fork/summary
        self.CRITICAL_LIMIT = 150000  # Strong recommendation
        
        # Initialize tiktoken encoders for precise token counting
        self._encoders = {}
        if TIKTOKEN_AVAILABLE:
            try:
                # Initialize commonly used encoders
                self._encoders['gpt-4'] = tiktoken.encoding_for_model("gpt-4")
                self._encoders['gpt-3.5-turbo'] = tiktoken.encoding_for_model("gpt-3.5-turbo")
                self._encoders['claude'] = tiktoken.get_encoding("cl100k_base")  # Claude uses similar tokenization
                logger.info("✅ Initialized tiktoken encoders for precise token counting")
            except Exception as e:
                logger.warning(f"Failed to initialize tiktoken encoders: {e}")
                self._encoders = {}
        
    def load_usage(self):
        """Load usage data from storage"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.current_session = data.get('current_session', {
                        'session_id': None,
                        'total_tokens': 0,
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'messages_count': 0,
                        'started_at': datetime.now(timezone.utc).isoformat()
                    })
                    self.total_usage = data.get('total_usage', {
                        'all_time_tokens': 0,
                        'sessions_count': 0
                    })
            else:
                self.reset_session()
                self.total_usage = {
                    'all_time_tokens': 0,
                    'sessions_count': 0
                }
        except Exception as e:
            logger.error(f"Failed to load token usage: {e}")
            self.reset_session()
            self.total_usage = {'all_time_tokens': 0, 'sessions_count': 0}
    
    def save_usage(self):
        """Save usage data to storage"""
        try:
            data = {
                'current_session': self.current_session,
                'total_usage': self.total_usage,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save token usage: {e}")
    
    def reset_session(self):
        """Reset current session counters"""
        self.current_session = {
            'session_id': None,
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'messages_count': 0,
            'started_at': datetime.now(timezone.utc).isoformat()
        }
    
    def track_usage(
        self, 
        session_id: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0
    ):
        """Track token usage for a request"""
        
        # Auto-calculate total if not provided
        if total_tokens == 0 and (prompt_tokens > 0 or completion_tokens > 0):
            total_tokens = prompt_tokens + completion_tokens
        
        # Ensure non-negative tokens
        total_tokens = max(0, total_tokens)
        prompt_tokens = max(0, prompt_tokens)
        completion_tokens = max(0, completion_tokens)
        
        # Check and reset if session changed (BEFORE any operations)
        if self.current_session.get('session_id') != session_id:
            if self.current_session.get('session_id'):
                # Save old session to total before reset
                old_total = self.current_session['total_tokens']
                old_session = self.current_session['session_id']
                self.total_usage['all_time_tokens'] += old_total
                self.total_usage['sessions_count'] += 1
                logger.info(f"📊 Session completed: {old_session} with {old_total} tokens")
            
            # Reset completely BEFORE setting new session
            self.reset_session()
            self.current_session['session_id'] = session_id
            logger.info(f"📊 New session started: {session_id}")
        
        # Update counters (now correctly starts from 0 for new sessions)
        self.current_session['total_tokens'] += total_tokens
        self.current_session['prompt_tokens'] += prompt_tokens
        self.current_session['completion_tokens'] += completion_tokens
        self.current_session['messages_count'] += 1
        
        self.save_usage()
        
        logger.info(f"📊 Token usage: +{total_tokens} (session total: {self.current_session['total_tokens']})")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        current_tokens = self.current_session['total_tokens']
        
        # Calculate percentage of limits
        soft_percentage = (current_tokens / self.SOFT_LIMIT) * 100
        hard_percentage = (current_tokens / self.HARD_LIMIT) * 100
        
        # Determine recommendation level
        recommendation = self._get_recommendation(current_tokens)
        
        return {
            'current_session': {
                'session_id': self.current_session.get('session_id'),
                'total_tokens': current_tokens,
                'prompt_tokens': self.current_session['prompt_tokens'],
                'completion_tokens': self.current_session['completion_tokens'],
                'messages_count': self.current_session['messages_count'],
                'started_at': self.current_session.get('started_at')
            },
            'limits': {
                'soft_limit': self.SOFT_LIMIT,
                'hard_limit': self.HARD_LIMIT,
                'critical_limit': self.CRITICAL_LIMIT
            },
            'percentages': {
                'soft_limit_percentage': round(soft_percentage, 1),
                'hard_limit_percentage': round(hard_percentage, 1)
            },
            'recommendation': recommendation,
            'total_usage': self.total_usage
        }
    
    def _get_recommendation(self, tokens: int) -> Dict[str, Any]:
        """Get recommendation based on token usage"""
        
        # Safety check for edge cases
        tokens = max(0, int(tokens))
        
        if tokens < self.SOFT_LIMIT:
            return {
                'level': 'ok',
                'message': 'Token usage is healthy',
                'action': None,
                'color': 'green'
            }
        elif tokens < self.HARD_LIMIT:
            return {
                'level': 'warning',
                'message': f'Consider forking or creating summary soon ({tokens}/{self.HARD_LIMIT} tokens)',
                'action': 'fork_soon',
                'color': 'yellow',
                'details': 'Approaching context limit. Fork conversation to start fresh while preserving history.'
            }
        elif tokens < self.CRITICAL_LIMIT:
            return {
                'level': 'high',
                'message': f'Recommended: Fork or summarize now ({tokens}/{self.CRITICAL_LIMIT} tokens)',
                'action': 'fork_now',
                'color': 'orange',
                'details': 'High token usage detected. Fork conversation to maintain performance and reduce costs.'
            }
        else:
            return {
                'level': 'critical',
                'message': f'Critical: Fork immediately! ({tokens} tokens)',
                'action': 'fork_critical',
                'color': 'red',
                'details': 'Critical token usage! Fork now to avoid performance degradation and high costs.'
            }
    
    def should_recommend_fork(self) -> bool:
        """Check if fork should be recommended"""
        return self.current_session['total_tokens'] >= self.HARD_LIMIT
    
    def estimate_tokens(self, text: str, model: str = "gpt-4") -> int:
        """
        Precisely count tokens for text using tiktoken
        
        Args:
            text: Text to count tokens for
            model: Model name to determine correct encoding (gpt-4, gpt-3.5-turbo, claude)
        
        Returns:
            Precise token count
        """
        if not text:
            return 0
        
        if not TIKTOKEN_AVAILABLE or not self._encoders:
            # Fallback to character-based estimation
            logger.debug("Using character-based token estimation (tiktoken not available)")
            return len(text) // 4
        
        try:
            # Determine which encoder to use
            encoder_key = 'gpt-4'  # Default
            
            if 'gpt-3.5' in model.lower() or 'turbo' in model.lower():
                encoder_key = 'gpt-3.5-turbo'
            elif 'claude' in model.lower() or 'anthropic' in model.lower():
                encoder_key = 'claude'
            elif 'gpt-4' in model.lower() or 'gpt-5' in model.lower():
                encoder_key = 'gpt-4'
            
            # Get encoder
            encoder = self._encoders.get(encoder_key)
            if not encoder:
                # Try to get encoder for this model
                try:
                    encoder = tiktoken.encoding_for_model(model)
                    self._encoders[model] = encoder
                except Exception:
                    # Fall back to default encoder
                    encoder = self._encoders.get('gpt-4')
            
            if encoder:
                # Precise token count
                tokens = len(encoder.encode(text))
                logger.debug(f"Precise token count for {len(text)} chars: {tokens} tokens (model: {encoder_key})")
                return tokens
            else:
                # Fallback
                return len(text) // 4
                
        except Exception as e:
            logger.warning(f"Token counting error: {e}, falling back to estimation")
            return len(text) // 4


# Global instance
token_tracker = TokenUsageTracker()
