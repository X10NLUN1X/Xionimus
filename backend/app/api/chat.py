from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import logging
import re

from ..core.database import get_database
from ..core.ai_manager import AIManager
from ..core.intelligent_agents import intelligent_agent_manager
from ..core.coding_prompt import coding_prompt_manager
from ..core.code_processor import code_processor
from ..models.session_models import Session as SessionModel, Message as MessageModel
from sqlalchemy import desc, func

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=100000)
    timestamp: Optional[datetime] = None
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or only whitespace')
        return v.strip()

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=100)
    provider: str = Field(default="openai", pattern="^(openai|anthropic|perplexity)$")
    model: str = Field(default="gpt-5", min_length=1, max_length=100)
    session_id: Optional[str] = Field(None, max_length=100)
    stream: bool = False
    api_keys: Optional[Dict[str, str]] = None  # Dynamic API keys from frontend
    auto_agent_selection: bool = True  # Enable intelligent agent selection
    ultra_thinking: bool = False  # Enable extended thinking for Claude models
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('Messages list cannot be empty')
        # Check for at least one user message
        if not any(msg.role == 'user' for msg in v):
            raise ValueError('At least one user message is required')
        return v

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
        
        # Extract session_id from request or generate new one
        session_id = request.session_id or str(uuid.uuid4())
        
        # Convert Pydantic models to dict for AI manager
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Remove consecutive duplicate messages (same role and content)
        # This prevents issues with APIs that require alternating user/assistant messages
        deduplicated_messages = []
        for msg in messages_dict:
            if not deduplicated_messages or (
                deduplicated_messages[-1]["role"] != msg["role"] or 
                deduplicated_messages[-1]["content"] != msg["content"]
            ):
                deduplicated_messages.append(msg)
        
        messages_dict = deduplicated_messages
        logger.info(f"📝 Messages after deduplication: {len(messages_dict)} messages")
        
        # XIONIMUS CODING-ASSISTENT: System-Prompt automatisch einfügen
        # Füge System-Prompt nur ein, wenn noch keine System-Message existiert
        has_system_message = any(msg["role"] == "system" for msg in messages_dict)
        if not has_system_message and messages_dict:
            # Erkenne Sprache aus erster User-Message
            first_user_msg = next((msg for msg in messages_dict if msg["role"] == "user"), None)
            language = "de"  # Default Deutsch
            if first_user_msg:
                # Einfache Sprach-Erkennung
                content_lower = first_user_msg["content"].lower()
                english_indicators = ["create", "build", "develop", "please", "help me", "i want", "i need"]
                if any(indicator in content_lower for indicator in english_indicators):
                    language = "en"
            
            # System-Prompt einfügen
            system_prompt = coding_prompt_manager.get_system_prompt(language)
            messages_dict.insert(0, {"role": "system", "content": system_prompt})
            logger.info(f"🤖 Xionimus Coding-Assistent System-Prompt eingefügt (Sprache: {language})")
        
        # RESEARCH-CHOICE ERKENNUNG & DURCHFÜHRUNG
        # Prüfe ob letzte User-Message eine Research-Choice ist
        research_performed = False
        if messages_dict and messages_dict[-1]["role"] == "user":
            last_user_message = messages_dict[-1]["content"]
            research_choice = coding_prompt_manager.detect_research_choice(last_user_message)
            
            if research_choice:
                logger.info(f"🔍 Research-Choice erkannt: {research_choice}")
                
                # Wenn "keine" gewählt wurde, bestätige und fahre fort
                if research_choice == "none":
                    logger.info("✅ Keine Recherche gewünscht - fahre direkt mit Coding fort")
                else:
                    # Führe automatische Perplexity-Research durch
                    logger.info(f"🔍 Starte automatische {research_choice} Research")
                    
                    # Extrahiere Topic aus vorheriger Message
                    # Finde die ursprüngliche Coding-Anfrage (vor der Research-Choice)
                    coding_request = None
                    for i in range(len(messages_dict) - 2, -1, -1):
                        if messages_dict[i]["role"] == "user":
                            potential_request = messages_dict[i]["content"]
                            if coding_prompt_manager.is_coding_related(potential_request):
                                coding_request = potential_request
                                break
                    
                    if coding_request:
                        # Erkenne Sprache
                        language = "de"
                        content_lower = coding_request.lower()
                        english_indicators = ["create", "build", "develop", "please", "help me"]
                        if any(indicator in content_lower for indicator in english_indicators):
                            language = "en"
                        
                        # Generiere Research-Prompt
                        research_prompt = coding_prompt_manager.get_research_prompt(
                            coding_request, 
                            research_choice,
                            language
                        )
                        
                        # Wähle Perplexity-Modell basierend auf Choice
                        research_model = coding_prompt_manager.get_research_model(research_choice)
                        
                        logger.info(f"🔍 Research-Modell: {research_model}")
                        logger.info(f"🔍 Research-Prompt: {research_prompt[:100]}...")
                        
                        try:
                            # Führe Perplexity-Research durch
                            research_response = await ai_manager.generate_response(
                                provider="perplexity",
                                model=research_model,
                                messages=[{"role": "user", "content": research_prompt}],
                                stream=False,
                                api_keys=request.api_keys
                            )
                            
                            research_content = research_response.get("content", "")
                            
                            if research_content:
                                logger.info(f"✅ Research erfolgreich: {len(research_content)} Zeichen")
                                
                                # Füge Research-Ergebnis als Assistant-Message ein
                                research_size = {"small": "Klein", "medium": "Mittel", "large": "Groß"}[research_choice]
                                
                                if language == "de":
                                    research_summary = f"✅ **{research_size} Recherche abgeschlossen!**\n\n{research_content}\n\n---\n\nBasierend auf dieser Recherche habe ich einige Klärungsfragen:"
                                else:
                                    research_summary = f"✅ **{research_size} Research completed!**\n\n{research_content}\n\n---\n\nBased on this research, I have some clarifying questions:"
                                
                                # Entferne die Research-Choice Message
                                messages_dict = messages_dict[:-1]
                                
                                # Füge Research-Ergebnis hinzu
                                messages_dict.append({
                                    "role": "assistant",
                                    "content": research_summary
                                })
                                
                                research_performed = True
                                logger.info("✅ Research-Ergebnis in Kontext eingefügt")
                                
                                # Gebe Research-Ergebnis direkt zurück (ohne weitere AI-Generierung)
                                # Speichere in Datenbank
                                message_id = str(uuid.uuid4())
                                timestamp = datetime.now(timezone.utc)
                                
                                # Save to database
                                if db:
                                    # Get or create session
                                    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
                                    if not session:
                                        session = SessionModel(
                                            id=session_id,
                                            title=f"Chat {session_id[:8]}",
                                            created_at=timestamp,
                                            updated_at=timestamp
                                        )
                                        db.add(session)
                                    else:
                                        session.updated_at = timestamp
                                    
                                    # Save message
                                    message = MessageModel(
                                        session_id=session_id,
                                        role="assistant",
                                        content=research_summary,
                                        provider="perplexity",
                                        model=research_model,
                                        created_at=timestamp
                                    )
                                    db.add(message)
                                    db.commit()
                                
                                # Gebe direkt zurück
                                return ChatResponse(
                                    content=research_summary,
                                    provider="perplexity",
                                    model=research_model,
                                    session_id=session_id,
                                    message_id=message_id,
                                    usage=research_response.get("usage"),
                                    timestamp=timestamp
                                )
                            else:
                                logger.warning("⚠️ Research lieferte leeren Content")
                                
                        except Exception as e:
                            logger.error(f"❌ Research fehlgeschlagen: {str(e)}")
                            # Fahre trotzdem fort ohne Research
                    else:
                        logger.warning("⚠️ Keine Coding-Anfrage vor Research-Choice gefunden")
        
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
            api_keys=request.api_keys,
            ultra_thinking=request.ultra_thinking
        )
        
        # Debug: Check response content
        logger.info(f"✅ AI Response received: content_length={len(response.get('content', ''))} chars")
        logger.info(f"✅ Response keys: {list(response.keys())}")
        if response.get("content"):
            logger.info(f"✅ Content preview: {response['content'][:100]}...")
        else:
            logger.error(f"❌ EMPTY CONTENT! Full response: {response}")
        
        # 🚀 EMERGENT-STYLE: Process code blocks and write to files automatically
        ai_content = response.get("content", "")
        code_process_result = await code_processor.process_ai_response(
            ai_content, 
            auto_write=True  # Automatically write detected code to files
        )
        
        # Generate summary for user (instead of showing raw code)
        if code_process_result['code_blocks_found'] > 0:
            code_summary = code_processor.generate_summary(code_process_result)
            # Replace code blocks in response with summary
            # Remove code blocks from the content
            cleaned_content = re.sub(
                r'```[\w]*\s*\n.*?\n```',
                '',
                ai_content,
                flags=re.DOTALL
            )
            # Add summary at the end
            response["content"] = f"{cleaned_content.strip()}\n\n{code_summary}"
            logger.info(f"🎯 Code processing: {code_process_result['files_written']} files written")
        
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
        
    except ValueError as e:
        # Configuration errors (missing API keys, invalid provider, etc.)
        logger.warning(f"Chat validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors
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

@router.post("/agent-recommendation")
async def get_agent_recommendation(data: Dict[str, Any]):
    """Get intelligent agent recommendation for a message"""
    try:
        message = data.get("message", "")
        available_providers = data.get("available_providers", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        recommendation = intelligent_agent_manager.get_agent_recommendation(
            message, available_providers
        )
        
        return {
            "success": True,
            "recommendation": recommendation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-assignments")
async def get_agent_assignments():
    """Get all intelligent agent assignments for documentation"""
    return {
        "assignments": intelligent_agent_manager.get_all_assignments(),
        "description": "Intelligent agent assignments based on task types",
        "total_agents": len(intelligent_agent_manager.agent_assignments)
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
        # Query sessions using SQLAlchemy
        sessions = db.query(SessionModel).order_by(desc(SessionModel.updated_at)).limit(limit).all()
        
        result = []
        for session in sessions:
            # Get message count
            message_count = db.query(func.count(MessageModel.id)).filter(
                MessageModel.session_id == session.id
            ).scalar()
            
            # Get last message
            last_msg = db.query(MessageModel).filter(
                MessageModel.session_id == session.id
            ).order_by(desc(MessageModel.created_at)).first()
            
            result.append(ChatSession(
                session_id=session.id,
                name=session.title or f"Session {session.id[:8]}",
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=message_count or 0,
                last_message=last_msg.content[:100] + "..." if last_msg and len(last_msg.content) > 100 else last_msg.content if last_msg else None
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
        # Query messages using SQLAlchemy
        messages = db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at).all()
        
        # Convert to chat format
        result = []
        for msg in messages:
            result.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at,
                "provider": msg.provider,
                "model": msg.model
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