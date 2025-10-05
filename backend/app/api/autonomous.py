"""
Autonomous AI API Endpoints
Handles rollback, action history, and autonomous control
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timezone

from ..core.state_manager import StateManager
from ..core.auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()


class RollbackResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    action_type: Optional[str] = None
    restored_files: Optional[List[str]] = None


@router.post("/rollback/action/{session_id}", response_model=RollbackResponse)
async def rollback_last_action(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Rollback the last autonomous action in a session
    Restores the previous state of the last modified file
    """
    try:
        logger.info(f"🔄 Rollback last action for session: {session_id}")
        
        state_manager = StateManager(session_id)
        result = await state_manager.rollback_last_action()
        state_manager.close()
        
        return RollbackResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Rollback action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback/session/{session_id}", response_model=RollbackResponse)
async def rollback_entire_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Rollback entire session - restore all checkpoints
    Restores the session to its initial state before any autonomous actions
    """
    try:
        logger.info(f"🔄 Rollback entire session: {session_id}")
        
        state_manager = StateManager(session_id)
        result = await state_manager.rollback_session()
        state_manager.close()
        
        return RollbackResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Rollback session failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_action_history(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Get action history for a session
    Returns list of all autonomous actions with results
    """
    try:
        logger.info(f"📋 Get action history for session: {session_id}")
        
        state_manager = StateManager(session_id)
        history = await state_manager.get_action_history(limit=limit)
        state_manager.close()
        
        return {
            "success": True,
            "session_id": session_id,
            "count": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"❌ Get action history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checkpoints/{session_id}")
async def get_checkpoint_count(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get number of checkpoints available for rollback
    """
    try:
        state_manager = StateManager(session_id)
        count = await state_manager.get_checkpoint_count()
        state_manager.close()
        
        return {
            "success": True,
            "session_id": session_id,
            "checkpoint_count": count,
            "can_rollback": count > 0
        }
        
    except Exception as e:
        logger.error(f"❌ Get checkpoint count failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
