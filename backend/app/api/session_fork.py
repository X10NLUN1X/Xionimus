"""
Session Fork API
Handles context overflow by creating intelligent session forks with summarized context
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime, timezone
import json

from ..core.auth import get_current_user, User
from ..core.database import get_database
from sqlalchemy.orm import Session
from ..models.session_models import Session as SessionModel, Message
from ..core.ai_manager import AIManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Context limits (tokens)
CONTEXT_WARNING_THRESHOLD = 0.8  # Warn at 80%
CONTEXT_LIMIT_GPT4 = 128000
CONTEXT_LIMIT_CLAUDE = 200000
CONTEXT_LIMIT_DEFAULT = 8000

class ContextStatus(BaseModel):
    """Current context status for a session"""
    session_id: str
    total_messages: int
    estimated_tokens: int
    context_limit: int
    usage_percentage: float
    should_fork: bool
    warning_message: Optional[str] = None


class ForkSessionRequest(BaseModel):
    """Request to fork a session"""
    session_id: str
    include_last_n_messages: Optional[int] = 10  # Include last N messages in detail


class ForkSessionResponse(BaseModel):
    """Response after forking a session"""
    success: bool
    new_session_id: str
    new_session_name: str
    summary: str
    message: str


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation: ~4 chars per token for English
    This is a simplified approximation
    """
    return len(text) // 4


def calculate_context_usage(messages: List[Message], model: str = "gpt-4o") -> ContextStatus:
    """
    Calculate current context usage for a session
    """
    total_tokens = 0
    for msg in messages:
        total_tokens += estimate_tokens(msg.content)
    
    # Determine context limit based on model
    if "gpt-4" in model.lower() or "gpt-5" in model.lower():
        context_limit = CONTEXT_LIMIT_GPT4
    elif "claude" in model.lower():
        context_limit = CONTEXT_LIMIT_CLAUDE
    else:
        context_limit = CONTEXT_LIMIT_DEFAULT
    
    usage_percentage = (total_tokens / context_limit) * 100
    should_fork = usage_percentage >= (CONTEXT_WARNING_THRESHOLD * 100)
    
    warning_message = None
    if should_fork:
        warning_message = f"⚠️ Context-Auslastung bei {usage_percentage:.1f}%. Ein Fork wird empfohlen, um die Performance zu erhalten."
    
    return ContextStatus(
        session_id=messages[0].session_id if messages else "",
        total_messages=len(messages),
        estimated_tokens=total_tokens,
        context_limit=context_limit,
        usage_percentage=usage_percentage,
        should_fork=should_fork,
        warning_message=warning_message
    )


@router.get("/context-status/{session_id}", response_model=ContextStatus)
async def get_context_status(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get current context status for a session
    Returns warning if fork is recommended
    """
    try:
        # Get session
        session = db.query(SessionModel).filter(
            Session.id == session_id,
            Session.user_id == current_user.user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all messages
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            return ContextStatus(
                session_id=session_id,
                total_messages=0,
                estimated_tokens=0,
                context_limit=CONTEXT_LIMIT_GPT4,
                usage_percentage=0.0,
                should_fork=False
            )
        
        # Get the model from most recent message
        recent_model = messages[-1].model if messages[-1].model else "gpt-4o"
        
        status = calculate_context_usage(messages, recent_model)
        
        logger.info(f"Context status for {session_id}: {status.usage_percentage:.1f}% ({status.estimated_tokens}/{status.context_limit} tokens)")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get context status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fork", response_model=ForkSessionResponse)
async def fork_session(
    request: ForkSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Fork a session with intelligent context summarization
    
    Process:
    1. Get all messages from current session
    2. Create AI summary of conversation (preserving user intent)
    3. Create new session with summary as first message
    4. Include last N messages in full detail
    5. Return new session ID
    """
    try:
        # Get original session
        original_session = db.query(SessionModel).filter(
            Session.id == request.session_id,
            Session.user_id == current_user.user_id
        ).first()
        
        if not original_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all messages
        messages = db.query(Message).filter(
            Message.session_id == request.session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(status_code=400, detail="Cannot fork empty session")
        
        logger.info(f"🔀 Forking session {request.session_id} with {len(messages)} messages")
        
        # Create conversation text for summarization
        conversation_text = ""
        for msg in messages[:-request.include_last_n_messages]:  # All except last N
            role = "User" if msg.role == "user" else "Assistant"
            conversation_text += f"{role}: {msg.content[:500]}...\n\n"
        
        # Generate summary using AI
        summary_prompt = f"""Erstelle eine kompakte, präzise Zusammenfassung dieser Konversation.

WICHTIG:
- Fokussiere auf die USER-INTENTION und ZIELE
- Bewahre ALLE wichtigen technischen Details und Entscheidungen
- Liste konkrete Anforderungen und bereits implementierte Features
- Halte die Zusammenfassung unter 1000 Tokens
- Format: Strukturiert mit Bullet Points

KONVERSATION:
{conversation_text}

ZUSAMMENFASSUNG:"""

        ai_manager = AIManager()
        summary_response = await ai_manager.generate_response(
            prompt=summary_prompt,
            model="gpt-4o-mini",  # Use cheaper model for summarization
            stream=False
        )
        
        summary = summary_response.get("content", "Fehler bei der Zusammenfassung")
        
        logger.info(f"✅ Generated summary: {len(summary)} chars")
        
        # Create new session
        new_session_id = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        new_session = SessionModel(
            id=new_session_id,
            name=f"Fork: {original_session.name or 'Continued Conversation'}",
            user_id=current_user.user_id,
            workspace_id=original_session.workspace_id,
            active_project=original_session.active_project,
            active_project_branch=original_session.active_project_branch,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        db.add(new_session)
        
        # Add summary as first message
        summary_message = Message(
            id=f"msg_{datetime.now(timezone.utc).timestamp()}",
            session_id=new_session_id,
            role="system",
            content=f"📋 **Zusammenfassung der vorherigen Session:**\n\n{summary}\n\n---\n\n**Konversation wird hier fortgesetzt...**",
            timestamp=datetime.now(timezone.utc).isoformat(),
            model="system"
        )
        db.add(summary_message)
        
        # Copy last N messages in full detail
        for msg in messages[-request.include_last_n_messages:]:
            copied_message = Message(
                id=f"msg_{datetime.now(timezone.utc).timestamp()}_{msg.id}",
                session_id=new_session_id,
                role=msg.role,
                content=msg.content,
                timestamp=datetime.now(timezone.utc).isoformat(),
                model=msg.model
            )
            db.add(copied_message)
        
        db.commit()
        
        logger.info(f"✅ Created forked session: {new_session_id}")
        
        return ForkSessionResponse(
            success=True,
            new_session_id=new_session_id,
            new_session_name=new_session.name,
            summary=summary,
            message=f"✅ Session erfolgreich geforkt! Die letzten {request.include_last_n_messages} Nachrichten wurden übernommen."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fork session: {e}")
        raise HTTPException(status_code=500, detail=f"Fork failed: {str(e)}")


@router.get("/fork-preview/{session_id}")
async def preview_fork(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Preview what will be included in a fork
    Shows estimated summary size and last N messages
    """
    try:
        session = db.query(SessionModel).filter(
            Session.id == session_id,
            Session.user_id == current_user.user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages to fork")
        
        # Calculate sizes
        total_chars = sum(len(msg.content) for msg in messages)
        last_10_chars = sum(len(msg.content) for msg in messages[-10:])
        to_summarize_chars = total_chars - last_10_chars
        
        return {
            "session_id": session_id,
            "session_name": session.name,
            "total_messages": len(messages),
            "messages_to_summarize": len(messages) - 10,
            "messages_to_keep_full": 10,
            "estimated_summary_reduction": f"{(to_summarize_chars / total_chars * 100):.1f}%",
            "preview": {
                "first_message": messages[0].content[:200] + "..." if len(messages[0].content) > 200 else messages[0].content,
                "last_message": messages[-1].content[:200] + "..." if len(messages[-1].content) > 200 else messages[-1].content
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview fork: {e}")
        raise HTTPException(status_code=500, detail=str(e))
