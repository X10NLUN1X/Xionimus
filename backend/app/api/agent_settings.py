"""
Agent Settings API
Manage autonomous agent settings and configuration
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from ..core.database import get_db_session
from ..core.auth import get_current_user, User
from ..models.agent_models import AgentSettings, AgentConnection, AgentActivity

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentSettingsUpdate(BaseModel):
    """Model for updating agent settings"""
    watch_directories: Optional[List[str]] = None
    claude_api_key: Optional[str] = None
    sonnet_enabled: Optional[bool] = None
    opus_enabled: Optional[bool] = None
    auto_analysis_enabled: Optional[bool] = None
    suggestions_enabled: Optional[bool] = None
    notification_level: Optional[str] = None


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    connected: bool
    agent_count: int
    last_activity: Optional[str] = None


@router.get("/settings")
async def get_agent_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get current user's agent settings"""
    settings = db.query(AgentSettings).filter(
        AgentSettings.user_id == current_user.user_id
    ).first()
    
    if not settings:
        # Create default settings
        settings = AgentSettings(
            user_id=current_user.user_id,
            watch_directories=[],
            auto_analysis_enabled=True,
            suggestions_enabled=True,
            notification_level="all"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings.to_dict()


@router.put("/settings")
async def update_agent_settings(
    settings_update: AgentSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update agent settings"""
    settings = db.query(AgentSettings).filter(
        AgentSettings.user_id == current_user.user_id
    ).first()
    
    if not settings:
        settings = AgentSettings(user_id=current_user.user_id)
        db.add(settings)
    
    # Update fields if provided
    if settings_update.watch_directories is not None:
        settings.watch_directories = settings_update.watch_directories
    if settings_update.claude_api_key is not None:
        # TODO: Encrypt API key before storing
        settings.claude_api_key = settings_update.claude_api_key
    if settings_update.sonnet_enabled is not None:
        settings.sonnet_enabled = int(settings_update.sonnet_enabled)
    if settings_update.opus_enabled is not None:
        settings.opus_enabled = int(settings_update.opus_enabled)
    if settings_update.auto_analysis_enabled is not None:
        settings.auto_analysis_enabled = int(settings_update.auto_analysis_enabled)
    if settings_update.suggestions_enabled is not None:
        settings.suggestions_enabled = int(settings_update.suggestions_enabled)
    if settings_update.notification_level is not None:
        settings.notification_level = settings_update.notification_level
    
    db.commit()
    db.refresh(settings)
    
    return settings.to_dict()


@router.get("/status")
async def get_agent_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent connection status for current user"""
    # Get latest connection
    connection = db.query(AgentConnection).filter(
        AgentConnection.agent_id.like(f"%{current_user.user_id}%")
    ).order_by(AgentConnection.connected_at.desc()).first()
    
    # Get latest activity
    activity = db.query(AgentActivity).filter(
        AgentActivity.agent_id.like(f"%{current_user.user_id}%")
    ).order_by(AgentActivity.timestamp.desc()).first()
    
    is_connected = connection and connection.status == "connected" if connection else False
    
    return {
        "connected": is_connected,
        "agent_count": 1 if is_connected else 0,
        "last_activity": activity.timestamp.isoformat() if activity else None,
        "last_connection": connection.connected_at.isoformat() if connection else None
    }


@router.get("/activity")
async def get_agent_activity(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent agent activity"""
    activities = db.query(AgentActivity).filter(
        AgentActivity.agent_id.like(f"%{current_user.user_id}%")
    ).order_by(AgentActivity.timestamp.desc()).limit(limit).all()
    
    return {
        "activities": [activity.to_dict() for activity in activities],
        "count": len(activities)
    }


@router.get("/connections")
async def get_agent_connections(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent connection history"""
    connections = db.query(AgentConnection).filter(
        AgentConnection.agent_id.like(f"%{current_user.user_id}%")
    ).order_by(AgentConnection.connected_at.desc()).limit(limit).all()
    
    return {
        "connections": [conn.to_dict() for conn in connections],
        "count": len(connections)
    }
