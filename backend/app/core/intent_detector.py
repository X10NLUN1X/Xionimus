"""
Intent Detector - Detects code review intents in chat messages
"""
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class IntentDetector:
    """Detects user intentions for automated code review"""
    
    # Patterns for code review intents (German & English)
    CODE_REVIEW_PATTERNS = [
        # German
        r'\b(review|überprüf|analysier|verbessere|optimiere|refactor).*(code|backend|frontend|projekt|repository|repo)\b',
        r'\b(code|backend|frontend|projekt|repository|repo).*(review|überprüf|analysier|verbessere|optimiere|refactor)\b',
        r'\b(finde|suche).*(fehler|bugs|probleme)\b',
        r'\b(automatisch|auto).*(fix|beheb|korrigier)\b',
        r'\breview.*(mein|den|das).*(code|backend|frontend)\b',
        
        # English  
        r'\b(review|analyze|check|improve|optimize|refactor).*(code|backend|frontend|project|repository|repo)\b',
        r'\b(code|backend|frontend|project|repository|repo).*(review|analyze|check|improve|optimize|refactor)\b',
        r'\b(find|detect).*(bugs|errors|issues|problems)\b',
        r'\b(auto|automatic|automatically).*(fix|repair|correct)\b',
        r'\breview.*(my|the).*(code|backend|frontend)\b',
    ]
    
    # Patterns for scope detection
    BACKEND_PATTERNS = [r'\bbackend\b', r'\bapi\b', r'\bserver\b', r'\bpython\b']
    FRONTEND_PATTERNS = [r'\bfrontend\b', r'\bui\b', r'\breact\b', r'\btypescript\b']
    FULL_PATTERNS = [r'\ball\b', r'\bfull\b', r'\bentire\b', r'\bgesamte\b', r'\bkomplett\b']
    
    def detect_code_review_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Detect if message is a code review request
        
        Returns:
            Dict with intent details if detected, None otherwise
        """
        message_lower = message.lower()
        
        # Check if any review pattern matches
        is_review_intent = any(
            re.search(pattern, message_lower, re.IGNORECASE)
            for pattern in self.CODE_REVIEW_PATTERNS
        )
        
        if not is_review_intent:
            return None
        
        logger.info(f"🎯 Code review intent detected: {message[:100]}...")
        
        # Detect scope
        scope = self._detect_scope(message_lower)
        
        # Detect language
        language = 'de' if self._is_german(message) else 'en'
        
        return {
            'type': 'code_review',
            'scope': scope,
            'language': language,
            'original_message': message
        }
    
    def _detect_scope(self, message_lower: str) -> str:
        """Detect review scope from message"""
        
        # Check for full review
        if any(re.search(pattern, message_lower) for pattern in self.FULL_PATTERNS):
            return 'full'
        
        # Check for backend
        if any(re.search(pattern, message_lower) for pattern in self.BACKEND_PATTERNS):
            return 'backend'
        
        # Check for frontend
        if any(re.search(pattern, message_lower) for pattern in self.FRONTEND_PATTERNS):
            return 'frontend'
        
        # Default to full
        return 'full'
    
    def _is_german(self, message: str) -> bool:
        """Simple German language detection"""
        german_words = ['code', 'review', 'überprüf', 'analysier', 'verbessere', 
                       'optimiere', 'backend', 'frontend', 'projekt', 'fehler']
        message_lower = message.lower()
        german_count = sum(1 for word in german_words if word in message_lower)
        return german_count >= 2


# Global intent detector instance
intent_detector = IntentDetector()
