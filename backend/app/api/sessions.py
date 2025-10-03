"""
Session Management API with SQLite Backend
Handles chat sessions, messages, and workspace organization
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import logging

from ..core.database import get_database
from ..core.auth_middleware import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateSessionRequest(BaseModel):
    name: Optional[str] = None
    workspace_id: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    name: Optional[str] = None
    workspace_id: Optional[str] = None


class AddMessageRequest(BaseModel):
    session_id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    parent_message_id: Optional[str] = None


class UpdateMessageRequest(BaseModel):
    content: str


class SessionResponse(BaseModel):
    id: str
    name: str
    workspace_id: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    timestamp: str
    provider: Optional[str] = None
    model: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    parent_message_id: Optional[str] = None


# ==================== SESSION ENDPOINTS ====================

@router.post("/", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Create a new chat session (user-specific if authenticated)"""
    try:
        db = get_database()
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        
        # Import models
        from ..models.session_models import Session
        
        # Create new session with user_id
        new_session = Session(
            id=session_id,
            name=request.name or "New Chat",
            workspace_id=request.workspace_id,
            user_id=user_id  # Associate with authenticated user
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        logger.info(f"✅ Session created: {session_id} for user: {user_id or 'anonymous'}")
        
        return SessionResponse(
            id=new_session.id,
            name=new_session.name,
            workspace_id=new_session.workspace_id,
            created_at=new_session.created_at,
            updated_at=new_session.updated_at,
            message_count=0
        )
        
    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    workspace_id: Optional[str] = None, 
    limit: int = 100,
    user_id: Optional[str] = Depends(get_current_user_optional)
):
    """List sessions for authenticated user only
    
    Returns only sessions belonging to the authenticated user
    """
    try:
        from ..models.session_models import Session, Message
        from sqlalchemy import func
        
        db = get_database()
        
        # Query sessions with user filter
        query = db.query(
            Session.id,
            Session.name,
            Session.workspace_id,
            Session.created_at,
            Session.updated_at,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message, Session.id == Message.session_id)
        
        # Filter by user_id (critical for security)
        if user_id:
            # Show sessions that belong to user OR have no user_id (legacy migration)
            query = query.filter((Session.user_id == user_id) | (Session.user_id == None))
            logger.info(f"📋 Listing sessions for user: {user_id} (including legacy sessions)")
        else:
            # If no user_id, only show sessions without user_id (legacy)
            query = query.filter(Session.user_id == None)
            logger.warning("⚠️ Unauthenticated session list request - showing legacy sessions only")
        
        # Optional workspace filter
        if workspace_id:
            query = query.filter(Session.workspace_id == workspace_id)
        
        sessions = query.group_by(Session.id).order_by(Session.updated_at.desc()).limit(limit).all()
        
        return [SessionResponse(
            id=s.id,
            name=s.name,
            workspace_id=s.workspace_id,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=s.message_count
        ) for s in sessions]
        
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, user_id: Optional[str] = Depends(get_current_user_optional)):
    """Get a specific session (user must own it)"""
    try:
        from ..models.session_models import Session, Message
        from sqlalchemy import func
        
        db = get_database()
        
        # Query session with message count
        result = db.query(
            Session.id,
            Session.name,
            Session.workspace_id,
            Session.created_at,
            Session.updated_at,
            Session.user_id,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message, Session.id == Message.session_id)\
         .filter(Session.id == session_id)\
         .group_by(Session.id)\
         .first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Security: Check if session belongs to user
        if user_id and result.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return SessionResponse(
            id=result.id,
            name=result.name,
            workspace_id=result.workspace_id,
            created_at=result.created_at,
            updated_at=result.updated_at,
            message_count=result.message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update session metadata (rename, change workspace)"""
    try:
        db = get_database()
        
        # Check if session exists
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update
        db.update_session(
            session_id=session_id,
            name=request.name,
            workspace_id=request.workspace_id
        )
        
        # Return updated session
        updated_session = db.get_session(session_id)
        return SessionResponse(**updated_session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Delete a session and all its messages
    
    Optional authentication: If authenticated, validates ownership
    """
    # Note: user_id available for future ownership validation
    try:
        db = get_database()
        
        # Check if session exists
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        db.delete_session(session_id)
        
        return {"status": "deleted", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MESSAGE ENDPOINTS ====================

@router.post("/sessions/messages", response_model=MessageResponse)
async def add_message(request: AddMessageRequest):
    """Add a message to a session"""
    try:
        db = get_database()
        
        # Import models
        from ..models.session_models import Session, Message
        import json
        
        # Check if session exists
        session = db.query(Session).filter(Session.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        message_id = f"msg_{uuid.uuid4().hex[:16]}"
        
        # Create new message
        new_message = Message(
            id=message_id,
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            provider=request.provider,
            model=request.model,
            usage=json.dumps(request.usage) if request.usage else None,
            parent_message_id=request.parent_message_id
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return MessageResponse(
            id=new_message.id,
            session_id=new_message.session_id,
            role=new_message.role,
            content=new_message.content,
            timestamp=new_message.timestamp,
            provider=new_message.provider,
            model=new_message.model,
            usage=json.loads(new_message.usage) if new_message.usage else None,
            parent_message_id=new_message.parent_message_id
        )
        
    except Exception as e:
        logger.error(f"Add message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, limit: Optional[int] = None):
    """Get all messages for a session"""
    try:
        db = get_database()
        
        # Check if session exists
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.get_messages(session_id, limit=limit)
        return [MessageResponse(**m) for m in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/messages/{message_id}", response_model=MessageResponse)
async def update_message(message_id: str, request: UpdateMessageRequest):
    """Update a message (for edit functionality)"""
    try:
        db = get_database()
        
        db.update_message(message_id, request.content)
        
        # Get updated message (need to find session_id first)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT session_id FROM messages WHERE id = ?", (message_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Message not found")
            
            session_id = row['session_id']
            messages = db.get_messages(session_id)
            updated_msg = next((m for m in messages if m['id'] == message_id), None)
            
            if not updated_msg:
                raise HTTPException(status_code=404, detail="Message not found")
            
            return MessageResponse(**updated_msg)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str):
    """Delete a specific message"""
    try:
        db = get_database()
        db.delete_message(message_id)
        
        return {"status": "deleted", "message_id": message_id}
        
    except Exception as e:
        logger.error(f"Delete message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/branch")
async def branch_conversation(
    session_id: str,
    from_message_id: str,
    new_session_name: Optional[str] = None
):
    """
    Branch conversation from a specific message
    Creates a new session with messages up to the branch point
    """
    try:
        db = get_database()
        
        # Get original session
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages up to branch point
        messages = db.get_messages(session_id)
        branch_index = next(
            (i for i, m in enumerate(messages) if m['id'] == from_message_id),
            None
        )
        
        if branch_index is None:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Create new session
        new_session_id = f"session_{uuid.uuid4().hex[:16]}"
        db.create_session(
            session_id=new_session_id,
            name=new_session_name or f"{session['name']} (Branch)",
            workspace_id=session.get('workspace_id')
        )
        
        # Copy messages up to branch point
        for msg in messages[:branch_index + 1]:
            new_msg_id = f"msg_{uuid.uuid4().hex[:16]}"
            db.add_message(
                message_id=new_msg_id,
                session_id=new_session_id,
                role=msg['role'],
                content=msg['content'],
                provider=msg.get('provider'),
                model=msg.get('model'),
                usage=msg.get('usage')
            )
        
        return {
            "status": "branched",
            "new_session_id": new_session_id,
            "message_count": branch_index + 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Branch conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILITY ENDPOINTS ====================

@router.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        db = get_database()
        return db.get_db_stats()
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vacuum")
async def vacuum_database():
    """Optimize database (run after many deletions)"""
    try:
        db = get_database()
        db.vacuum()
        return {"status": "vacuumed"}
    except Exception as e:
        logger.error(f"Vacuum error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
