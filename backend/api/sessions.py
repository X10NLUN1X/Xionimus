from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from core.database import get_database
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CreateSessionRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    message_count: int

@router.post("/", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db = Depends(get_database)
) -> SessionResponse:
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        session_data = {
            "session_id": session_id,
            "name": request.name or f"Session {timestamp.strftime('%Y-%m-%d %H:%M')}",
            "description": request.description,
            "created_at": timestamp,
            "updated_at": timestamp,
            "message_count": 0
        }
        
        await db.chat_sessions.insert_one(session_data)
        
        return SessionResponse(
            session_id=session_id,
            name=session_data["name"],
            description=session_data["description"],
            created_at=timestamp,
            message_count=0
        )
        
    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    db = Depends(get_database)
) -> List[SessionResponse]:
    """List all chat sessions"""
    try:
        cursor = db.chat_sessions.find().sort("updated_at", -1)
        sessions = await cursor.to_list(length=100)
        
        result = []
        for session in sessions:
            # Count messages for this session
            message_count = await db.chat_messages.count_documents(
                {"session_id": session["session_id"]}
            )
            
            result.append(SessionResponse(
                session_id=session["session_id"],
                name=session["name"],
                description=session.get("description"),
                created_at=session["created_at"],
                message_count=message_count
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db = Depends(get_database)
) -> Dict[str, str]:
    """Delete a chat session and all its messages"""
    try:
        # Delete session
        session_result = await db.chat_sessions.delete_one({"session_id": session_id})
        if session_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete all messages in session
        await db.chat_messages.delete_many({"session_id": session_id})
        
        return {"status": "deleted", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))