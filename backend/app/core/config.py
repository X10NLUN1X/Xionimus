from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os
import logging
import secrets

logger = logging.getLogger(__name__)

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
    
    # File Upload
    MAX_FILE_SIZE: int = 250 * 1024 * 1024  # 250MB
    UPLOAD_DIR: str = "uploads"
    WORKSPACE_DIR: str = "workspace"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Setup logging based on environment
import os
if os.getenv("ENABLE_JSON_LOGGING", "false").lower() == "true":
    from .structured_logging import setup_structured_logging
    setup_structured_logging(enable_json=True)
    logger.info("✅ Structured JSON logging enabled")
