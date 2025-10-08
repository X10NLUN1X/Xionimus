"""
API Key Models for secure storage
"""
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime, timezone
from ..core.database import Base


class UserApiKey(Base):
    """User API Keys - Encrypted storage"""
    __tablename__ = "user_api_keys"
    
    # Composite primary key: user_id + provider
    user_id = Column(String, primary_key=True, index=True)
    provider = Column(String, primary_key=True, index=True)  # anthropic, openai, perplexity, github
    
    # Encrypted API key
    encrypted_key = Column(String, nullable=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat(), onupdate=lambda: datetime.now(timezone.utc).isoformat())
    last_used_at = Column(String, nullable=True)
    
    # Connection test status (optional)
    last_test_status = Column(String, nullable=True)  # success, failed, not_tested
    last_test_at = Column(String, nullable=True)