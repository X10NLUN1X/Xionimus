from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os
import logging

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
    SECRET_KEY: str = os.getenv("SECRET_KEY", None) or os.getenv("JWT_SECRET_KEY", None)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Security validation
        if not self.SECRET_KEY:
            from secrets import token_urlsafe
            logger.warning("🔴 SECRET_KEY not set! Generating random key for this session.")
            logger.warning("⚠️  Set SECRET_KEY in .env for production!")
            self.SECRET_KEY = token_urlsafe(32)
        elif self.SECRET_KEY == "xionimus-secret-key-change-in-production":
            raise ValueError(
                "🔴 SECURITY ERROR: Default SECRET_KEY detected!\n"
                "You MUST change SECRET_KEY in production.\n"
                "Generate a secure key: openssl rand -hex 32\n"
                "Add to .env: SECRET_KEY=your_generated_key"
            )
    
    # File Upload
    MAX_FILE_SIZE: int = 250 * 1024 * 1024  # 250MB
    UPLOAD_DIR: str = "uploads"
    WORKSPACE_DIR: str = "workspace"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()