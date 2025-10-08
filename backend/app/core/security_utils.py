"""
Security utilities for safe logging and data handling
"""
import re
from typing import Any, Dict

def mask_api_key(key: str) -> str:
    """
    Mask API key for safe logging
    
    Examples:
        'sk-proj-abc123def456' -> '********...f456'
        'sk-ant-api03-xyz789' -> '********...z789'
    """
    if not key or len(key) < 8:
        return "****"
    
    return f"{'*' * 8}...{key[-4:]}"


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively mask sensitive data in dictionaries
    
    Masks fields like: api_key, secret, password, token, authorization
    """
    sensitive_patterns = [
        'api_key', 'apikey', 'secret', 'password', 
        'token', 'authorization', 'auth', 'credential'
    ]
    
    masked = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if key matches sensitive pattern
        is_sensitive = any(pattern in key_lower for pattern in sensitive_patterns)
        
        if is_sensitive and isinstance(value, str):
            masked[key] = mask_api_key(value)
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_data(value)
        elif isinstance(value, list):
            masked[key] = [
                mask_sensitive_data(item) if isinstance(item, dict) else item 
                for item in value
            ]
        else:
            masked[key] = value
    
    return masked


def sanitize_log_message(message: str) -> str:
    """
    Remove potential API keys from log messages using regex
    
    Patterns:
        - sk-proj-... (OpenAI)
        - sk-ant-... (Anthropic)
        - pplx-... (Perplexity)
    """
    # Pattern for common API key formats
    patterns = [
        r'sk-proj-[A-Za-z0-9_-]+',
        r'sk-ant-api\d+-[A-Za-z0-9_-]+',
        r'sk-[A-Za-z0-9]{48}',
        r'pplx-[A-Za-z0-9]+',
    ]
    
    sanitized = message
    for pattern in patterns:
        sanitized = re.sub(pattern, '********[REDACTED]', sanitized)
    
    return sanitized
