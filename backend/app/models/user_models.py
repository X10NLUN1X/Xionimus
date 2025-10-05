"""User and File models for SQLite"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from datetime import datetime, timezone
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    last_login = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    github_token = Column(Text, nullable=True)  # GitHub Personal Access Token
    github_username = Column(String, nullable=True)  # Connected GitHub username

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(String, primary_key=True)  # file_id
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    uploaded_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    user_id = Column(String, nullable=True)
    file_metadata = Column("metadata", Text, default="{}")

