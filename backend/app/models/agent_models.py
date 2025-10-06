"""
Agent Models
Database models for autonomous agent tracking
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AgentConnection(Base):
    """Track agent connections"""
    __tablename__ = "agent_connections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), index=True, nullable=False)
    connected_at = Column(DateTime, default=datetime.now, nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="connected")  # connected, disconnected
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "disconnected_at": self.disconnected_at.isoformat() if self.disconnected_at else None,
            "status": self.status
        }


class AgentActivity(Base):
    """Track agent file monitoring activity"""
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(100), index=True, nullable=False)
    activity_type = Column(String(50), nullable=False)  # file_event, analysis, suggestion
    file_path = Column(Text, nullable=True)
    event_type = Column(String(20), nullable=True)  # created, modified, deleted
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional data
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "activity_type": self.activity_type,
            "file_path": self.file_path,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }


class AgentSettings(Base):
    """User-specific agent settings"""
    __tablename__ = "agent_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    watch_directories = Column(JSON, nullable=True)  # List of directories to watch
    claude_api_key = Column(Text, nullable=True)  # Encrypted Claude API key
    sonnet_enabled = Column(Integer, default=1)  # Use Claude Sonnet 4.5
    opus_enabled = Column(Integer, default=1)  # Use Claude Opus 4.1
    auto_analysis_enabled = Column(Integer, default=1)
    suggestions_enabled = Column(Integer, default=1)
    notification_level = Column(String(20), default="all")  # all, errors, none
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "watch_directories": self.watch_directories,
            "sonnet_enabled": bool(self.sonnet_enabled),
            "opus_enabled": bool(self.opus_enabled),
            "auto_analysis_enabled": bool(self.auto_analysis_enabled),
            "suggestions_enabled": bool(self.suggestions_enabled),
            "notification_level": self.notification_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
