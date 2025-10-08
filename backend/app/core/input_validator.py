"""
Input Validation Utilities
Centralized input validation to prevent injection attacks and ensure data integrity
"""

import re
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, validator


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_session_id(session_id: str) -> str:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        Validated session ID
        
    Raises:
        HTTPException: If session ID is invalid
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    # Session ID should be alphanumeric with optional hyphens/underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format. Only alphanumeric characters, hyphens, and underscores allowed"
        )
    
    if len(session_id) > 100:
        raise HTTPException(status_code=400, detail="Session ID too long (max 100 characters)")
    
    return session_id


def validate_filename(filename: str) -> str:
    """
    Validate filename to prevent path traversal attacks
    
    Args:
        filename: Filename to validate
        
    Returns:
        Validated filename
        
    Raises:
        HTTPException: If filename is invalid
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename: path traversal detected")
    
    # Check for null bytes
    if '\0' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename: null byte detected")
    
    # Validate length
    if len(filename) > 255:
        raise HTTPException(status_code=400, detail="Filename too long (max 255 characters)")
    
    return filename


def validate_command(command: str, allowed_commands: Optional[List[str]] = None) -> str:
    """
    Validate command to prevent command injection
    
    Args:
        command: Command to validate
        allowed_commands: Optional list of allowed commands
        
    Returns:
        Validated command
        
    Raises:
        HTTPException: If command is invalid
    """
    if not command:
        raise HTTPException(status_code=400, detail="Command is required")
    
    # Check for command injection patterns
    dangerous_patterns = [';', '&&', '||', '|', '$', '`', '\n', '\r']
    for pattern in dangerous_patterns:
        if pattern in command:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid command: dangerous pattern '{pattern}' detected"
            )
    
    # If allowed commands specified, check whitelist
    if allowed_commands:
        command_name = command.split()[0]
        if command_name not in allowed_commands:
            raise HTTPException(
                status_code=400,
                detail=f"Command '{command_name}' not allowed"
            )
    
    return command


def validate_code(code: str, language: str, max_length: int = 100000) -> str:
    """
    Validate code submission
    
    Args:
        code: Code to validate
        language: Programming language
        max_length: Maximum code length
        
    Returns:
        Validated code
        
    Raises:
        HTTPException: If code is invalid
    """
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    if len(code) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Code too long (max {max_length} characters)"
        )
    
    # Language-specific validation
    supported_languages = ['python', 'javascript', 'bash', 'cpp', 'c', 'csharp', 'perl']
    if language not in supported_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{language}'. Supported: {', '.join(supported_languages)}"
        )
    
    return code


def validate_url(url: str) -> str:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        HTTPException: If URL is invalid
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if not url_pattern.match(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    return url


def sanitize_log_message(message: str, max_length: int = 1000) -> str:
    """
    Sanitize log message to prevent log injection
    
    Args:
        message: Log message to sanitize
        max_length: Maximum message length
        
    Returns:
        Sanitized message
    """
    if not message:
        return ""
    
    # Remove newlines and carriage returns to prevent log injection
    sanitized = message.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized


def validate_pagination(page: int = 1, page_size: int = 20, max_page_size: int = 100) -> Dict[str, int]:
    """
    Validate pagination parameters
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Dict with validated page and page_size
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    
    if page_size < 1:
        raise HTTPException(status_code=400, detail="Page size must be >= 1")
    
    if page_size > max_page_size:
        raise HTTPException(
            status_code=400,
            detail=f"Page size too large (max {max_page_size})"
        )
    
    return {"page": page, "page_size": page_size}


class SafeRequest(BaseModel):
    """Base model for safe API requests with common validation"""
    
    class Config:
        # Prevent extra fields
        extra = "forbid"
        # Validate on assignment
        validate_assignment = True