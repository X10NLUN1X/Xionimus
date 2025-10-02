from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
from pathlib import Path
import os
import logging
import secrets

logger = logging.getLogger(__name__)

# Determine .env file path - works on both Windows and Linux
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Go up to backend/ directory
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"

class Settings(BaseSettings):
    # Database
    MONGO_URL: str = "mongodb://localhost:27017/xionimus_ai"
    
    # AI API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # Application
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    @field_validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY and ensure it's set"""
        if not v or v == "":
            if os.getenv('ENVIRONMENT', 'development') == 'production':
                raise ValueError("❌ CRITICAL: SECRET_KEY must be set in production environment!")
            
            # In development, generate temporary key with clear warning
            temp_key = secrets.token_hex(32)
            logger.critical("🔴 SECRET_KEY not set! Using temporary key for this session.")
            logger.warning("⚠️  For production, set SECRET_KEY in .env file!")
            logger.warning("⚠️  Generate one with: openssl rand -hex 32")
            return temp_key
        
        # Validate key length
        if len(v) < 32:
            logger.warning(f"⚠️  SECRET_KEY is too short ({len(v)} chars). Recommended: 64+ chars")
        
        return v
    
    # File Upload Constants
    MAX_FILE_SIZE: int = 250 * 1024 * 1024  # 250MB
    UPLOAD_DIR: str = "uploads"
    WORKSPACE_DIR: str = "workspace"
    
    # Rate Limiting Constants
    DEFAULT_RATE_LIMIT: str = "100/minute"
    CHAT_RATE_LIMIT: str = "30/minute"
    AUTH_RATE_LIMIT: str = "5/minute"
    CODE_REVIEW_RATE_LIMIT: str = "10/minute"
    
    # Retry Logic Constants
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_MIN_WAIT_SECONDS: int = 2
    RETRY_MAX_WAIT_SECONDS: int = 10
    
    # Database Constants
    DEFAULT_SESSION_LIMIT: int = 50
    DEFAULT_MESSAGE_LIMIT: int = 100
    
    # Code Review Constants
    MAX_FILES_TO_REVIEW: int = 10
    LOCK_TIMEOUT_SECONDS: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env without errors

settings = Settings()

# Setup logging based on environment
import os
if os.getenv("ENABLE_JSON_LOGGING", "false").lower() == "true":
    from .structured_logging import setup_structured_logging
    setup_structured_logging(enable_json=True)
    logger.info("✅ Structured JSON logging enabled")
