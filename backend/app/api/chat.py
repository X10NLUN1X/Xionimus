from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field, validator, ValidationError
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
from ..core.intent_detector import intent_detector
from ..core.auto_review_orchestrator import auto_review_orchestrator
from ..core.context_manager import context_manager  # Context management
from ..core.improvement_suggestions import improvement_suggestions_generator  # Improvement suggestions
from ..core.auto_routing import auto_routing_manager  # Auto-routing to agents
from ..core.research_storage import research_storage  # Research storage
from ..core.auto_workflow_orchestrator import auto_workflow_orchestrator  # NEW: Auto-workflow
from ..models.session_models import Session as SessionModel, Message as MessageModel
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

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
    messages: List[ChatMessage] = Field(..., min_length=1, max_length=500)  # Increased for 200k context
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
    context_stats: Optional[Dict[str, Any]] = None  # NEW: Context statistics

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
    """Generate AI chat completion with intelligent agent selection
    
    Rate limit: 30 requests per minute per IP (configured in main.py)
    """
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
                                
                                # 💾 PHASE 4: Store research for future use (all agents can access)
                                research_id = research_storage.store_research(
                                    topic=coding_request,
                                    content=research_content,
                                    source="perplexity",
                                    metadata={
                                        "size": research_choice,
                                        "model": research_model,
                                        "language": language
                                    }
                                )
                                logger.info(f"💾 Research gespeichert: ID={research_id}")
                                
                                # Füge Research-Ergebnis als Assistant-Message ein
                                research_size = {"small": "Klein", "medium": "Mittel", "large": "Groß"}[research_choice]
                                
                                if language == "de":
                                    research_summary = f"✅ **{research_size} Recherche abgeschlossen!**\n\n{research_content}\n\n---\n\n"
                                else:
                                    research_summary = f"✅ **{research_size} Research completed!**\n\n{research_content}\n\n---\n\n"
                                
                                # Entferne die Research-Choice Message
                                messages_dict = messages_dict[:-1]
                                
                                # Generiere Klärungsfragen basierend auf Research
                                logger.info("🤔 Generiere Klärungsfragen basierend auf Research...")
                                
                                # Erstelle Prompt für Klärungsfragen
                                if language == "de":
                                    clarification_prompt = f"""Basierend auf der folgenden Recherche, stelle präzise Klärungsfragen für die Implementierung:

**Ursprüngliche Anfrage:**
{coding_request}

**Recherche-Ergebnisse:**
{research_content}

**Deine Aufgabe:**
Stelle 3-5 gezielte Klärungsfragen, um die Anforderungen zu präzisieren. Frage nach:
- Programmiersprache/Framework-Präferenzen
- Frontend/Backend/Full-Stack
- Spezifische Features oder Anforderungen
- Design/UI-Präferenzen
- Authentifizierung, Datenbank oder andere Integrationen

Formuliere die Fragen klar und nummeriert. Sei präzise und relevant zum Thema."""
                                else:
                                    clarification_prompt = f"""Based on the following research, ask precise clarifying questions for implementation:

**Original Request:**
{coding_request}

**Research Results:**
{research_content}

**Your Task:**
Ask 3-5 targeted clarifying questions to specify the requirements. Ask about:
- Programming language/framework preferences
- Frontend/Backend/Full-Stack
- Specific features or requirements
- Design/UI preferences
- Authentication, database, or other integrations

Formulate the questions clearly and numbered. Be precise and relevant to the topic."""
                                
                                try:
                                    # Verwende Claude für Klärungsfragen (coding-related task)
                                    clarification_response = await ai_manager.generate_response(
                                        provider="anthropic",
                                        model="claude-sonnet-4-5-20250929",
                                        messages=[{"role": "user", "content": clarification_prompt}],
                                        stream=False,
                                        api_keys=request.api_keys,
                                        temperature=0.7
                                    )
                                    
                                    clarification_questions = clarification_response.get("content", "")
                                    
                                    if clarification_questions:
                                        logger.info(f"✅ Klärungsfragen generiert: {len(clarification_questions)} Zeichen")
                                        
                                        # Kombiniere Research + Fragen
                                        if language == "de":
                                            final_content = f"{research_summary}**Basierend auf dieser Recherche habe ich folgende Klärungsfragen:**\n\n{clarification_questions}"
                                        else:
                                            final_content = f"{research_summary}**Based on this research, I have the following clarifying questions:**\n\n{clarification_questions}"
                                    else:
                                        logger.warning("⚠️ Keine Klärungsfragen generiert, verwende nur Research")
                                        final_content = research_summary
                                        
                                except Exception as e:
                                    logger.error(f"❌ Fehler bei Klärungsfragen-Generierung: {str(e)}")
                                    # Fallback: nur Research ohne Fragen
                                    final_content = research_summary
                                
                                # Füge finalen Content in Kontext ein
                                messages_dict.append({
                                    "role": "assistant",
                                    "content": final_content
                                })
                                
                                research_performed = True
                                logger.info("✅ Research + Klärungsfragen in Kontext eingefügt")
                                
                                # Speichere in Datenbank
                                message_id = str(uuid.uuid4())
                                timestamp = datetime.now(timezone.utc)
                                timestamp_str = timestamp.isoformat()
                                
                                # Save to database
                                if db:
                                    # Get or create session
                                    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
                                    if not session:
                                        session = SessionModel(
                                            id=session_id,
                                            name=f"Chat {session_id[:8]}",
                                            created_at=timestamp_str,
                                            updated_at=timestamp_str
                                        )
                                        db.add(session)
                                    else:
                                        session.updated_at = timestamp_str
                                    
                                    # Save message
                                    message = MessageModel(
                                        id=message_id,
                                        session_id=session_id,
                                        role="assistant",
                                        content=final_content,
                                        provider="anthropic",  # Claude generiert die Fragen
                                        model="claude-sonnet-4-5-20250929",
                                        timestamp=timestamp_str
                                    )
                                    db.add(message)
                                    db.commit()
                                
                                # Gebe Research + Klärungsfragen zurück
                                return ChatResponse(
                                    content=final_content,
                                    provider="anthropic",
                                    model="claude-sonnet-4-5-20250929",
                                    session_id=session_id,
                                    message_id=message_id,
                                    usage=clarification_response.get("usage") if 'clarification_response' in locals() else None,
                                    timestamp=timestamp
                                )
                            else:
                                logger.warning("⚠️ Research lieferte leeren Content")
                                
                        except (KeyError, ValueError, TypeError) as e:
                            logger.error(f"❌ Research data error: {str(e)}")
                            # Continue without research
                        except (ConnectionError, TimeoutError) as e:
                            logger.error(f"❌ Research connection failed: {str(e)}")
                            # Continue without research
                        except Exception as e:
                            logger.critical(f"❌ Unexpected research error: {str(e)}", exc_info=True)
                            # Continue without research
                    else:
                        logger.warning("⚠️ Keine Coding-Anfrage vor Research-Choice gefunden")
        
        # AUTO CODE REVIEW DETECTION & EXECUTION
        # Check if user wants automatic code review
        if messages_dict and messages_dict[-1]["role"] == "user":
            last_user_message = messages_dict[-1]["content"]
            review_intent = intent_detector.detect_code_review_intent(last_user_message)
            
            if review_intent:
                logger.info(f"🎯 Auto Code Review intent detected: {review_intent['scope']}")
                
                try:
                    # Run automatic code review
                    review_result = await auto_review_orchestrator.run_auto_review(
                        api_keys=request.api_keys or {},
                        scope=review_intent['scope'],
                        language=review_intent['language']
                    )
                    
                    # Generate response message
                    response_content = review_result['summary']
                    
                    # Save to database
                    message_id = str(uuid.uuid4())
                    timestamp = datetime.now(timezone.utc)
                    timestamp_str = timestamp.isoformat()
                    
                    if db:
                        # Get or create session
                        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
                        if not session:
                            session = SessionModel(
                                id=session_id,
                                name=f"Auto Review {session_id[:8]}",
                                created_at=timestamp_str,
                                updated_at=timestamp_str
                            )
                            db.add(session)
                        else:
                            session.updated_at = timestamp_str
                        
                        # Save message
                        message = MessageModel(
                            id=message_id,
                            session_id=session_id,
                            role="assistant",
                            content=response_content,
                            provider="auto_review",
                            model="4-agent-system",
                            timestamp=timestamp_str
                        )
                        db.add(message)
                        db.commit()
                    
                    # Return auto review result
                    return ChatResponse(
                        content=response_content,
                        provider="auto_review",
                        model="4-agent-system",
                        session_id=session_id,
                        message_id=message_id,
                        usage=None,
                        timestamp=timestamp
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Auto review failed: {e}", exc_info=True)
                    # Continue with normal chat if auto review fails
        
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
        
        # 📊 CONTEXT MANAGEMENT: Get stats and trim if needed
        context_stats_before = context_manager.get_context_stats(messages_dict, request.model)
        logger.info(f"📊 Context before: {context_stats_before['total_tokens']:,} tokens ({context_stats_before['usage_percent']:.1f}% of {context_stats_before['model_limit']:,})")
        
        # Trim context if needed (reserve 4000 tokens for response)
        messages_dict, trim_stats = context_manager.trim_context(messages_dict, request.model, reserve_tokens=4000)
        
        if trim_stats['trimmed']:
            logger.warning(f"✂️ Context trimmed: {trim_stats['removed_messages']} messages removed")
        
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
        
        # Generate enhanced summary for user (with purpose and next steps)
        if code_process_result['code_blocks_found'] > 0:
            # Pass AI response for context extraction
            code_summary = code_processor.generate_summary(code_process_result, ai_content)
            # Replace code blocks in response with summary
            # Remove code blocks from the content
            cleaned_content = re.sub(
                r'```[\w]*\s*\n.*?\n```',
                '',
                ai_content,
                flags=re.DOTALL
            )
            # Add enhanced summary at the end
            response["content"] = f"{cleaned_content.strip()}\n\n{code_summary}"
            logger.info(f"🎯 Code processing: {code_process_result['files_written']} files written with enhanced summary")
        
        # 🤖 PHASE 3: Auto-Routing to specialized agents
        user_last_message = messages_dict[-1]['content'] if messages_dict else ""
        routing_decision = auto_routing_manager.should_route_to_agent(
            ai_response=response["content"],
            user_request=user_last_message,
            session_context=messages_dict
        )
        
        if routing_decision:
            logger.info(f"🎯 Auto-routing to {routing_decision['agent']} agent: {routing_decision['reason']}")
            
            # Generate specialized agent prompt
            agent_prompt = auto_routing_manager.get_agent_prompt(routing_decision, user_last_message)
            
            # Call specialized agent (using Claude for all specialized tasks)
            try:
                agent_response = await ai_manager.generate_response(
                    provider="anthropic",
                    model="claude-sonnet-4-5-20250929",
                    messages=[{"role": "user", "content": agent_prompt}],
                    stream=False,
                    api_keys=request.api_keys
                )
                
                agent_content = agent_response.get("content", "")
                if agent_content:
                    # Append agent response to main response
                    response["content"] += f"\n\n---\n\n## 🤖 Automatische Verbesserung durch {routing_decision['agent'].title()}-Agent\n\n"
                    response["content"] += agent_content
                    logger.info(f"✅ Agent {routing_decision['agent']} completed successfully")
                else:
                    logger.warning(f"⚠️ Agent {routing_decision['agent']} returned empty response")
                    
            except Exception as e:
                logger.error(f"❌ Agent {routing_decision['agent']} failed: {str(e)}")
                # Continue without agent enhancement
        
        # 💡 PHASE 2: Generate improvement suggestions
        improvement_suggestions = improvement_suggestions_generator.generate_suggestions(
            ai_response=response["content"],
            user_request=user_last_message,
            code_blocks_count=code_process_result.get('code_blocks_found', 0)
        )
        
        # Append suggestions to response
        response["content"] = f"{response['content']}{improvement_suggestions}"
        logger.info("💡 Improvement suggestions added to response")
        
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
        
        # 📊 Get final context stats (after adding AI response)
        final_context_stats = context_manager.get_context_stats(messages_dict, request.model)
        final_context_stats['trimming'] = trim_stats  # Add trimming info
        
        return ChatResponse(
            content=response["content"],
            provider=response["provider"],
            model=response["model"],
            session_id=session_id,
            message_id=message_id,
            usage=response.get("usage"),
            timestamp=timestamp,
            context_stats=final_context_stats  # NEW: Include context statistics
        )
        
    except ValueError as e:
        # Configuration errors (missing API keys, invalid provider, etc.)
        logger.warning(f"Chat validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise
    except (ConnectionError, TimeoutError) as e:
        # Network errors
        logger.error(f"Chat connection error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    except Exception as e:
        # Unexpected errors - log with full traceback
        logger.critical(f"Unexpected chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

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
    
    except ValueError as e:
        logger.error(f"Agent recommendation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.critical(f"Agent recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate agent recommendation")

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
    """Get user's chat sessions with optimized N+1 query fix"""
    if db is None:
        return []
    
    try:
        from sqlalchemy import func, select
        from sqlalchemy.orm import aliased
        
        # Optimized query: Get sessions with message count in single query using JOIN
        # This eliminates N+1 problem by using GROUP BY
        query = (
            db.query(
                SessionModel,
                func.count(MessageModel.id).label('message_count'),
                func.max(MessageModel.timestamp).label('last_message_time')
            )
            .outerjoin(MessageModel, SessionModel.id == MessageModel.session_id)
            .group_by(SessionModel.id)
            .order_by(desc(SessionModel.updated_at))
            .limit(limit)
        )
        
        sessions_with_counts = query.all()
        
        # Get session IDs to fetch last messages in batch
        session_ids = [s[0].id for s in sessions_with_counts]
        
        # Fetch all last messages in single query using window function simulation
        last_messages = {}
        if session_ids:
            # Get the last message for each session in one query
            subquery = (
                db.query(
                    MessageModel.session_id,
                    MessageModel.content,
                    MessageModel.timestamp,
                    func.row_number().over(
                        partition_by=MessageModel.session_id,
                        order_by=desc(MessageModel.timestamp)
                    ).label('rn')
                )
                .filter(MessageModel.session_id.in_(session_ids))
                .subquery()
            )
            
            last_msg_query = db.query(
                subquery.c.session_id,
                subquery.c.content
            ).filter(subquery.c.rn == 1)
            
            for sid, content in last_msg_query:
                last_messages[sid] = content
        
        # Build result
        result = []
        for session, msg_count, _ in sessions_with_counts:
            last_msg = last_messages.get(session.id)
            
            result.append(ChatSession(
                session_id=session.id,
                name=session.name or f"Session {session.id[:8]}",
                created_at=session.created_at if isinstance(session.created_at, datetime) else datetime.fromisoformat(session.created_at),
                updated_at=session.updated_at if isinstance(session.updated_at, datetime) else datetime.fromisoformat(session.updated_at),
                message_count=msg_count or 0,
                last_message=last_msg[:100] + "..." if last_msg and len(last_msg) > 100 else last_msg if last_msg else None
            ))
        
        logger.info(f"✅ Fetched {len(result)} sessions with optimized query (eliminated N+1)")
        return result
    
    except SQLAlchemyError as e:
        logger.error(f"Database error getting sessions: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.critical(f"Unexpected error getting sessions: {e}", exc_info=True)
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
        ).order_by(MessageModel.timestamp).all()
        
        # Convert to chat format
        result = []
        for msg in messages:
            result.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp if isinstance(msg.timestamp, str) else msg.timestamp.isoformat(),
                "provider": msg.provider,
                "model": msg.model
            })
        
        return result
    
    except SQLAlchemyError as e:
        logger.error(f"Database error getting messages: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.critical(f"Unexpected error getting messages: {e}", exc_info=True)
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
        # Delete messages first (due to foreign key)
        deleted_messages = db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).delete()
        
        # Delete session
        db.query(SessionModel).filter(SessionModel.id == session_id).delete()
        
        db.commit()
        
        return {
            "status": "deleted",
            "session_id": session_id,
            "deleted_messages": deleted_messages
        }
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error deleting session: {e}")
        raise HTTPException(status_code=409, detail="Cannot delete session due to data constraints")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        db.rollback()
        logger.critical(f"Unexpected error deleting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

async def save_chat_message(
    db, session_id: str, user_message: dict, ai_response: dict, 
    message_id: str, timestamp: datetime
):
    """Background task to save chat message"""
    try:
        timestamp_str = timestamp.isoformat()
        
        # Get or create session
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            session = SessionModel(
                id=session_id,
                name=f"Chat {timestamp.strftime('%Y-%m-%d %H:%M')}",
                created_at=timestamp_str,
                updated_at=timestamp_str
            )
            db.add(session)
        else:
            session.updated_at = timestamp_str
        
        # Save user message
        user_msg = MessageModel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=user_message["content"],
            timestamp=timestamp_str
        )
        db.add(user_msg)
        
        # Save AI response
        ai_msg = MessageModel(
            id=message_id,
            session_id=session_id,
            role="assistant",
            content=ai_response["content"],
            provider=ai_response["provider"],
            model=ai_response["model"],
            timestamp=timestamp_str
        )
        db.add(ai_msg)
        
        db.commit()
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error saving message: {e}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error saving message: {e}", exc_info=True)
    except Exception as e:
        db.rollback()
        logger.critical(f"Unexpected error saving message: {e}", exc_info=True)