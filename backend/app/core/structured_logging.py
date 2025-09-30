"""
Structured Logging Configuration
Provides JSON-formatted logs with context for better monitoring and debugging
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "provider"):
            log_data["provider"] = record.provider
        if hasattr(record, "model"):
            log_data["model"] = record.model
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
            
        return json.dumps(log_data)


class StructuredLogger:
    """
    Wrapper for structured logging with extra context
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def info(self, message: str, **kwargs):
        """Log info with extra context"""
        extra = {k: v for k, v in kwargs.items()}
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning with extra context"""
        extra = {k: v for k, v in kwargs.items()}
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exc_info=False, **kwargs):
        """Log error with extra context"""
        extra = {k: v for k, v in kwargs.items()}
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def critical(self, message: str, exc_info=True, **kwargs):
        """Log critical with extra context"""
        extra = {k: v for k, v in kwargs.items()}
        self.logger.critical(message, exc_info=exc_info, extra=extra)


def setup_structured_logging(enable_json: bool = False):
    """
    Setup structured logging for the application
    
    Args:
        enable_json: If True, output JSON format. If False, use human-readable format
    """
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if enable_json:
        # JSON format for production/monitoring
        formatter = StructuredFormatter()
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance
    
    Usage:
        logger = get_structured_logger(__name__)
        logger.info("User logged in", user_id="123", provider="openai")
    """
    return StructuredLogger(name)
