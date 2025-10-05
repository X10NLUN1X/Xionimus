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
        """Validate SECRET_KEY and ensure it's set - AUTO-CREATE if missing"""
        
        # Check if .env file exists - AUTO-CREATE if missing
        if not ENV_FILE.exists():
            print("=" * 70)
            print("🔧 AUTO-FIX: .env file not found - creating automatically...")
            print("=" * 70)
            
            try:
                # Generate new SECRET_KEY
                new_secret_key = secrets.token_hex(32)
                
                # Copy from .env.example if it exists, otherwise create minimal .env
                if ENV_EXAMPLE.exists():
                    import shutil
                    shutil.copy(ENV_EXAMPLE, ENV_FILE)
                    print(f"✅ Copied template from {ENV_EXAMPLE}")
                    
                    # Replace placeholder SECRET_KEY
                    env_content = ENV_FILE.read_text()
                    env_content = env_content.replace(
                        'SECRET_KEY=your-secret-key-here-must-be-64-chars-long',
                        f'SECRET_KEY={new_secret_key}'
                    )
                    ENV_FILE.write_text(env_content)
                else:
                    # Create minimal .env file
                    minimal_env = f"""# Auto-generated .env file
SECRET_KEY={new_secret_key}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
DEBUG=true
HOST=0.0.0.0
PORT=8001
MONGO_URL=mongodb://localhost:27017/xionimus_ai
"""
                    ENV_FILE.write_text(minimal_env)
                    print(f"✅ Created minimal .env file")
                
                print(f"✅ SECRET_KEY automatically generated")
                print(f"📁 Location: {ENV_FILE}")
                print("=" * 70)
                logger.info(f"✅ Auto-created .env file with SECRET_KEY at {ENV_FILE}")
                
                # Return the new key
                return new_secret_key
                
            except Exception as e:
                print(f"❌ Failed to auto-create .env: {e}")
                print("⚠️  Using temporary key for this session")
                logger.error(f"Failed to auto-create .env: {e}")
        
        if not v or v == "":
            if os.getenv('ENVIRONMENT', 'development') == 'production':
                raise ValueError("❌ CRITICAL: SECRET_KEY must be set in production environment!")
            
            # In development, generate temporary key with clear warning
            temp_key = secrets.token_hex(32)
            print("=" * 70)
            print("🔴 SECRET_KEY not set in .env! Using temporary key.")
            print("⚠️  WARNING: Tokens will be invalid after restart!")
            print("=" * 70)
            print(f"📁 .env file location: {ENV_FILE}")
            print("🔑 Add this line to .env:")
            print(f"   SECRET_KEY={secrets.token_hex(32)}")
            print("=" * 70)
            logger.warning("⚠️ SECRET_KEY not set - using temporary key")
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
        env_file = str(ENV_FILE)  # Use absolute path - works on Windows and Linux
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env without errors

settings = Settings()

# Log .env file status on startup
if ENV_FILE.exists():
    logger.info(f"✅ .env file loaded from: {ENV_FILE}")
else:
    logger.warning(f"⚠️  .env file not found at: {ENV_FILE}")
    logger.warning(f"📝 Template available at: {ENV_EXAMPLE}")

# Setup logging based on environment
import os
if os.getenv("ENABLE_JSON_LOGGING", "false").lower() == "true":
    from .structured_logging import setup_structured_logging
    setup_structured_logging(enable_json=True)
    logger.info("✅ Structured JSON logging enabled")
