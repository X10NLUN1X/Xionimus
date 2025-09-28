from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from core.ai_orchestrator import orchestrator
from core.database import get_database
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    agent: str = "code"
    model: str = "gpt-4o-mini"
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    agent: str
    model: str
    session_id: str
    message_id: str
    timestamp: datetime
    usage: Optional[Dict[str, Any]] = None

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    db = Depends(get_database)
) -> ChatResponse:
    """Send message to AI agent and get response"""
    try:
        # Check if AI services are available
        services = orchestrator.get_available_services()
        if not any(services.values()):
            raise HTTPException(
                status_code=400,
                detail="No AI services configured. Please add API keys."
            )
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate AI response
        ai_response = await orchestrator.generate_response(
            agent_type=request.agent,
            message=request.message,
            model=request.model,
            context=request.context
        )
        
        # Create response
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Save to database
        chat_data = {
            "session_id": session_id,
            "message_id": message_id,
            "user_message": request.message,
            "ai_response": ai_response["content"],
            "agent": request.agent,
            "model": ai_response["model"],
            "timestamp": timestamp,
            "usage": ai_response.get("usage")
        }
        
        await db.chat_messages.insert_one(chat_data)
        
        return ChatResponse(
            response=ai_response["content"],
            agent=request.agent,
            model=ai_response["model"],
            session_id=session_id,
            message_id=message_id,
            timestamp=timestamp,
            usage=ai_response.get("usage")
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db = Depends(get_database)
) -> List[Dict[str, Any]]:
    """Get chat history for a session"""
    try:
        cursor = db.chat_messages.find(
            {"session_id": session_id}
        ).sort("timestamp", 1)
        
        messages = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for message in messages:
            message["_id"] = str(message["_id"])
        
        return messages
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))