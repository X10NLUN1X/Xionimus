"""
Session Management with Context Tracking & Intelligent Fork
Handles session summaries, context warnings, and smart session continuation
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import logging

from ..core.database import get_database
from ..core.auth import get_current_user
from ..core.ai_manager import AIManager
from ..core.token_tracker import token_tracker
from ..models.user_models import User
from ..models.session_models import Session, Message

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== MODELS ====================

class SessionSummaryRequest(BaseModel):
    session_id: str
    api_keys: Optional[Dict[str, str]] = None


class ContinueWithOptionRequest(BaseModel):
    session_id: str
    option_action: str
    api_keys: Optional[Dict[str, str]] = None


class SessionSummaryResponse(BaseModel):
    session_id: str
    new_session_id: str
    summary: str
    context_transfer: str
    next_steps: List[Dict[str, str]]  # 3 options with title + description
    old_session_tokens: int
    timestamp: str


class ContextWarningResponse(BaseModel):
    warning: bool
    current_tokens: int
    limit: int
    percentage: float
    message: str
    can_continue: bool
    recommendation: str


# ==================== ENDPOINTS ====================

@router.get("/context-status/{session_id}")
async def get_context_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Check context status for a session
    Returns warning if context limit is approaching
    """
    try:
        db = get_database()
        # Get session messages
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        # Calculate total tokens for this session
        import json
        total_tokens = 0
        for msg in messages:
            # Get usage if available
            if hasattr(msg, 'usage') and msg.usage:
                usage_data = msg.usage
                # Parse if it's a JSON string
                if isinstance(usage_data, str):
                    try:
                        usage_data = json.loads(usage_data)
                    except:
                        usage_data = {}
                if isinstance(usage_data, dict):
                    total_tokens += usage_data.get('total_tokens', 0)
        
        # If no usage data, estimate from content
        if total_tokens == 0:
            for msg in messages:
                estimated = token_tracker.estimate_tokens(msg.content)
                total_tokens += estimated
        
        # Context limits (adjust based on model)
        # GPT-4: 128k tokens
        # Claude: 200k tokens
        # Using conservative 100k limit
        CONTEXT_LIMIT = 100000
        SOFT_LIMIT = int(CONTEXT_LIMIT * 0.75)  # 75%
        HARD_LIMIT = int(CONTEXT_LIMIT * 0.90)  # 90%
        
        percentage = (total_tokens / CONTEXT_LIMIT) * 100
        
        # Determine warning level
        warning = total_tokens >= SOFT_LIMIT
        can_continue = total_tokens < HARD_LIMIT
        
        if total_tokens >= HARD_LIMIT:
            message = "⚠️ Context-Limit fast erreicht! Bitte Session zusammenfassen."
            recommendation = "critical"
        elif total_tokens >= SOFT_LIMIT:
            message = "⚠️ Context wird bald voll. Zusammenfassung empfohlen."
            recommendation = "warning"
        else:
            message = "✅ Context-Nutzung normal"
            recommendation = "ok"
        
        return ContextWarningResponse(
            warning=warning,
            current_tokens=total_tokens,
            limit=CONTEXT_LIMIT,
            percentage=round(percentage, 1),
            message=message,
            can_continue=can_continue,
            recommendation=recommendation
        )
        
    except Exception as e:
        logger.error(f"Context status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/summarize-and-fork", response_model=SessionSummaryResponse)
async def summarize_and_fork_session(
    request: SessionSummaryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Summarize current session and create new session with context
    
    Process:
    1. Load all messages from current session
    2. AI summarizes: Code, Progress, Goals, Approaches
    3. Create new session with summary as context
    4. Generate 3 simple next-step options
    5. Return summary + options to user
    """
    try:
        db = get_database()
        session_id = request.session_id
        
        # 1. Load session messages
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="Session nicht gefunden")
        
        # Get old session token count
        import json
        old_session_tokens = 0
        for msg in messages:
            if hasattr(msg, 'usage') and msg.usage:
                usage_data = msg.usage
                # Parse if it's a JSON string
                if isinstance(usage_data, str):
                    try:
                        usage_data = json.loads(usage_data)
                    except:
                        usage_data = {}
                if isinstance(usage_data, dict):
                    old_session_tokens += usage_data.get('total_tokens', 0)
        
        # 2. Build conversation context
        conversation_text = ""
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            conversation_text += f"\n\n{role}: {msg.content[:2000]}"  # Limit each message to 2k chars
        
        # Truncate if too long
        if len(conversation_text) > 50000:
            conversation_text = conversation_text[:50000] + "\n\n[... Konversation wurde gekürzt ...]"
        
        # 3. Generate summary with AI
        ai_manager = AIManager()
        
        summary_prompt = f"""Du bist ein intelligenter Assistent. Analysiere diese Chat-Session und erstelle eine präzise Zusammenfassung.

**Bisherige Konversation:**
{conversation_text}

**Deine Aufgabe:**
Erstelle eine strukturierte Zusammenfassung mit folgenden Punkten:

1. **🎯 Hauptziel**: Was will der User erreichen?
2. **💻 Code-Status**: Welcher Code wurde erstellt? Welche Dateien gibt es?
3. **📊 Aktueller Fortschritt**: Was funktioniert bereits?
4. **🔧 Offene Punkte**: Was fehlt noch oder muss verbessert werden?
5. **🛠️ Wichtige Ansätze**: Welche technischen Entscheidungen wurden getroffen?

**Format:**
Sei präzise, technisch korrekt aber verständlich. Keine Wiederholungen. Max 500 Wörter.
"""
        
        # Use Claude Sonnet for summary (good at analysis)
        summary_response = await ai_manager.generate_response(
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            messages=[{"role": "user", "content": summary_prompt}],
            stream=False,
            api_keys=request.api_keys or {}
        )
        
        summary = summary_response.get("content", "Zusammenfassung konnte nicht erstellt werden.")
        
        # 4. Generate next steps options
        options_prompt = f"""Basierend auf dieser Session-Zusammenfassung, schlage 3 konkrete nächste Schritte vor:

{summary}

**Deine Aufgabe:**
Generiere exakt 3 Optionen im folgenden JSON-Format:

[
  {{
    "title": "Kurzer, klarer Titel (max 8 Wörter)",
    "description": "Was genau passiert (max 20 Wörter)",
    "action": "Technische Beschreibung was gemacht wird"
  }},
  {{
    "title": "...",
    "description": "...",
    "action": "..."
  }},
  {{
    "title": "...",
    "description": "...",
    "action": "..."
  }}
]

**Anforderungen:**
- Optionen sollen für Laien verständlich sein
- Konkret und umsetzbar
- Sortiert nach Priorität (wichtigste zuerst)
- Keine technischen Fachbegriffe im Title/Description
- Action kann technisch sein

Gib NUR das JSON aus, keine weiteren Erklärungen!"""
        
        options_response = await ai_manager.generate_response(
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            messages=[{"role": "user", "content": options_prompt}],
            stream=False,
            api_keys=request.api_keys or {}
        )
        
        options_text = options_response.get("content", "[]")
        
        # Parse JSON from response
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', options_text, re.DOTALL)
        if json_match:
            options_text = json_match.group(1)
        
        try:
            next_steps = json.loads(options_text)
            if not isinstance(next_steps, list) or len(next_steps) != 3:
                raise ValueError("Invalid options format")
        except Exception as e:
            logger.error(f"Failed to parse options JSON: {e}")
            # Fallback options
            next_steps = [
                {
                    "title": "Weiter am Code arbeiten",
                    "description": "Bestehenden Code verbessern und erweitern",
                    "action": "Continue with code improvements"
                },
                {
                    "title": "Neue Funktionen hinzufügen",
                    "description": "Zusätzliche Features implementieren",
                    "action": "Add new features"
                },
                {
                    "title": "Tests und Debugging",
                    "description": "Code testen und Fehler beheben",
                    "action": "Test and debug"
                }
            ]
        
        # 5. Create new session
        new_session_id = f"session_{uuid.uuid4().hex[:16]}"
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.isoformat()
        
        new_session = Session(
            id=new_session_id,
            name=f"Fortsetzung: {messages[0].content[:30]}...",
            user_id=current_user.user_id,
            created_at=timestamp_str,
            updated_at=timestamp_str
        )
        db.add(new_session)
        
        # 6. Add context transfer message to new session
        context_transfer = f"""📋 **Session-Fortsetzung**

Dies ist eine neue Session, die auf der vorherigen aufbaut.

{summary}

---

**🎯 Wie möchtest du fortfahren?**

Wähle eine der folgenden Optionen oder beschreibe, was du als nächstes machen möchtest:"""
        
        context_message = Message(
            id=str(uuid.uuid4()),
            session_id=new_session_id,
            role="assistant",
            content=context_transfer,
            provider="system",
            model="context-transfer",
            timestamp=timestamp_str
        )
        db.add(context_message)
        
        db.commit()
        
        # 7. Reset token tracker for new session
        token_tracker.reset_session()
        
        logger.info(f"✅ Session forked: {session_id} → {new_session_id}")
        
        return SessionSummaryResponse(
            session_id=session_id,
            new_session_id=new_session_id,
            summary=summary,
            context_transfer=context_transfer,
            next_steps=next_steps,
            old_session_tokens=old_session_tokens,
            timestamp=timestamp_str
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session fork error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue-with-option")
async def continue_with_option(
    request: ContinueWithOptionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    User selects one of the 3 options
    This endpoint processes the selection and starts working on it
    """
    try:
        db = get_database()
        session_id = request.session_id
        option_action = request.option_action
        
        # Get session context
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="Session nicht gefunden")
        
        # Get the context transfer message
        context_msg = messages[0] if messages else None
        
        # Create user message for selected option
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.isoformat()
        
        user_message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=f"Ich möchte: {option_action}",
            timestamp=timestamp_str
        )
        db.add(user_message)
        db.commit()
        
        return {
            "status": "option_selected",
            "session_id": session_id,
            "action": option_action,
            "message": "Option ausgewählt. Der Assistant wird jetzt darauf reagieren."
        }
        
    except Exception as e:
        logger.error(f"Option selection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
