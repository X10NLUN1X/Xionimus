from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    MONGO_URL: str = "mongodb://localhost:27017/emergent_next"
    
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
    SECRET_KEY: str = "emergent-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    # File Upload
    MAX_FILE_SIZE: int = 250 * 1024 * 1024  # 250MB
    UPLOAD_DIR: str = "uploads"
    WORKSPACE_DIR: str = "workspace"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()