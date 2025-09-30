"""Session and message models for SQLite"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    name = Column(String, default="New Chat")  # Changed from 'title' to 'name'
    workspace_id = Column(String, nullable=True)  # Added workspace_id
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())  # Changed to String
    updated_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat(), onupdate=lambda: datetime.now(timezone.utc).isoformat())  # Changed to String
    metadata = Column(Text, default="{}")  # Added metadata
    
    # Relationship
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)  # Changed from Integer to String
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(String, nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())  # Changed from created_at to timestamp, and to String
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)
    usage = Column(Text, nullable=True)  # Changed to Text for JSON storage
    parent_message_id = Column(String, nullable=True)  # Added parent_message_id
    
    # Relationship
    session = relationship("Session", back_populates="messages")
