from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import logging

from ..core.database import get_database
from ..core.ai_manager import AIManager
from ..core.intelligent_agents import intelligent_agent_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    provider: str = "openai"  # openai, anthropic, perplexity
    model: str = "gpt-5"      # Updated default to GPT-5
    session_id: Optional[str] = None
    stream: bool = False
    api_keys: Optional[Dict[str, str]] = None  # Dynamic API keys from frontend
    auto_agent_selection: bool = True  # Enable intelligent agent selection

class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str
    session_id: str
    message_id: str
    usage: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ChatSession(BaseModel):
    session_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message: Optional[str] = None

@router.post("/", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    """Generate AI chat completion with intelligent agent selection"""
    try:
        ai_manager = AIManager()
        
        # Convert Pydantic models to dict for AI manager
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Intelligent agent selection if enabled
        if request.auto_agent_selection and messages_dict:
            last_message = messages_dict[-1]['content']
            
            # Get provider status to know what's available
            available_providers = {}
            if request.api_keys:
                # Check what providers have API keys
                available_providers = {
                    provider: bool(api_key.strip()) 
                    for provider, api_key in request.api_keys.items()
                }
            else:
                # Use configured providers
                available_providers = ai_manager.get_provider_status()
            
            # Get intelligent recommendation
            recommendation = intelligent_agent_manager.get_agent_recommendation(
                last_message, available_providers
            )
            
            # Override provider/model if recommendation is different and available
            if available_providers.get(recommendation["recommended_provider"], False):
                original_provider = request.provider
                original_model = request.model
                
                request.provider = recommendation["recommended_provider"]
                request.model = recommendation["recommended_model"]
                
                logger.info(f"🤖 Intelligent agent selection: {original_provider}/{original_model} → {request.provider}/{request.model}")
                logger.info(f"💭 Reasoning: {recommendation['reasoning']}")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate response with classic AI manager
        response = await ai_manager.generate_response(
            provider=request.provider,
            model=request.model,
            messages=messages_dict,
            stream=request.stream,
            api_keys=request.api_keys
        )
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Save to database in background
        if db is not None:
            background_tasks.add_task(
                save_chat_message,
                db, session_id, messages_dict[-1], response, message_id, timestamp
            )
        
        # Add agent selection info to response
        if request.auto_agent_selection:
            response["agent_info"] = {
                "intelligent_selection": True,
                "task_type": recommendation.get("task_type") if 'recommendation' in locals() else "general",
                "reasoning": recommendation.get("reasoning") if 'recommendation' in locals() else "Standard selection"
            }
        
        return ChatResponse(
            content=response["content"],
            provider=response["provider"],
            model=response["model"],
            session_id=session_id,
            message_id=message_id,
            usage=response.get("usage"),
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_ai_providers():
    """Get available AI providers and their models"""
    ai_manager = AIManager()
    
    return {
        "providers": ai_manager.get_provider_status(),
        "models": ai_manager.get_available_models()
    }

@router.get("/sessions", response_model=List[ChatSession])
async def get_chat_sessions(
    db = Depends(get_database),
    limit: int = 50
):
    """Get user's chat sessions"""
    if db is None:
        return []
    
    try:
        cursor = db.chat_sessions.find().sort("updated_at", -1).limit(limit)
        sessions = await cursor.to_list(length=limit)
        
        result = []
        for session in sessions:
            # Get message count
            message_count = await db.chat_messages.count_documents(
                {"session_id": session["session_id"]}
            )
            
            # Get last message
            last_msg = await db.chat_messages.find_one(
                {"session_id": session["session_id"]},
                sort=[("timestamp", -1)]
            )
            
            result.append(ChatSession(
                session_id=session["session_id"],
                name=session.get("name", f"Session {session['session_id'][:8]}"),
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                message_count=message_count,
                last_message=last_msg["ai_response"][:100] + "..." if last_msg and len(last_msg["ai_response"]) > 100 else last_msg.get("ai_response") if last_msg else None
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        return []

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    db = Depends(get_database)
):
    """Get messages for a specific session"""
    if db is None:
        return []
    
    try:
        cursor = db.chat_messages.find(
            {"session_id": session_id}
        ).sort("timestamp", 1)
        
        messages = await cursor.to_list(length=None)
        
        # Convert to chat format
        result = []
        for msg in messages:
            # Add user message
            result.append({
                "role": "user",
                "content": msg["user_message"],
                "timestamp": msg["timestamp"]
            })
            # Add AI response
            result.append({
                "role": "assistant",
                "content": msg["ai_response"],
                "timestamp": msg["timestamp"],
                "provider": msg.get("provider"),
                "model": msg.get("model"),
                "usage": msg.get("usage")
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        return []

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db = Depends(get_database)
):
    """Delete a chat session and all its messages"""
    if db is None:
        return {"status": "no database"}
    
    try:
        # Delete session
        await db.chat_sessions.delete_one({"session_id": session_id})
        
        # Delete all messages
        result = await db.chat_messages.delete_many({"session_id": session_id})
        
        return {
            "status": "deleted",
            "session_id": session_id,
            "deleted_messages": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def save_chat_message(
    db, session_id: str, user_message: dict, ai_response: dict, 
    message_id: str, timestamp: datetime
):
    """Background task to save chat message"""
    try:
        # Update or create session
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "session_id": session_id,
                    "updated_at": timestamp
                },
                "$setOnInsert": {
                    "created_at": timestamp,
                    "name": f"Chat {timestamp.strftime('%Y-%m-%d %H:%M')}"
                }
            },
            upsert=True
        )
        
        # Save message
        await db.chat_messages.insert_one({
            "message_id": message_id,
            "session_id": session_id,
            "user_message": user_message["content"],
            "ai_response": ai_response["content"],
            "provider": ai_response["provider"],
            "model": ai_response["model"],
            "usage": ai_response.get("usage"),
            "timestamp": timestamp
        })
        
    except Exception as e:
        logger.error(f"Save message error: {e}")