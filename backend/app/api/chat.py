from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import logging
import re

from ..core.database import get_db_session as get_database
from ..core.ai_manager import AIManager
from ..core.intelligent_agents import intelligent_agent_manager
from ..core.coding_prompt import coding_prompt_manager
from ..core.code_processor import code_processor
from ..core.intent_detector import intent_detector
# auto_review_orchestrator removed - chat only mode
from ..core.context_manager import context_manager  # Context management
# improvement_suggestions and auto_routing removed - chat only mode
from ..core.research_storage import research_storage  # Research storage
# auto_workflow_orchestrator and progress_tracker removed - direct coding after research
from ..core.testing_agent import TestingAgent  # NEW: Testing Agent
# Code review agents removed - chat only mode
from ..core.documentation_agent import documentation_agent  # NEW: Documentation Agent
from ..core.edit_agent import edit_agent  # NEW: Edit Agent
from ..core.token_tracker import token_tracker  # NEW: Token tracking
from ..core.auth import get_current_user, get_optional_user, User  # NEW: Authentication
from ..core.multi_agent_orchestrator import get_orchestrator, AgentType  # HYBRID: Multi-Agent System
from ..core.claude_router import claude_router  # PHASE 2: Claude smart routing
from ..core.developer_mode import developer_mode_manager  # PHASE 2: Developer Mode System
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
    developer_mode: str = Field(default="senior", pattern="^(junior|senior)$")  # 🎯 PHASE 2: Developer Mode (junior/senior)
    provider: Optional[str] = Field(None, pattern="^(openai|anthropic|perplexity)$")  # Auto-set by developer_mode
    model: Optional[str] = Field(None, min_length=1, max_length=100)  # Auto-set by developer_mode
    session_id: Optional[str] = Field(None, max_length=100)
    stream: bool = False
    api_keys: Optional[Dict[str, str]] = None  # Dynamic API keys from frontend
    auto_agent_selection: bool = True  # Enable intelligent agent selection
    ultra_thinking: Optional[bool] = None  # Auto-set by developer_mode
    multi_agent_mode: bool = False  # HYBRID: Enable Multi-Agent System (default OFF for streaming)
    
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
    agent_results: Optional[List[Dict[str, Any]]] = None  # NEW: Structured agent results
    token_usage: Optional[Dict[str, Any]] = None  # NEW: Token usage stats
    quick_actions: Optional[Dict[str, Any]] = None  # NEW: Quick action buttons (research/post-code options)
    research_sources: Optional[List[Dict[str, Any]]] = None  # NEW: Research sources from Perplexity

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
    current_user: User = Depends(get_current_user),
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
        
        # 🎯 PHASE 2: Apply Developer Mode settings
        mode_config = developer_mode_manager.get_mode_config(request.developer_mode)
        
        # Override provider/model based on developer mode if not explicitly set
        if request.provider is None:
            request.provider = mode_config["provider"]
        if request.model is None:
            request.model = mode_config["model"]
        if request.ultra_thinking is None:
            request.ultra_thinking = mode_config["ultra_thinking"]
        
        # 🔧 FIX: Disable auto_agent_selection when developer_mode is explicitly set
        # User's explicit mode choice should take precedence over intelligent routing
        skip_research_workflow = False
        if request.developer_mode:
            request.auto_agent_selection = False
            skip_research_workflow = True  # Skip research workflow for direct AI access
            logger.info(f"🎯 Developer Mode: {mode_config['name']} (auto_agent_selection disabled, research workflow skipped)")
        
        logger.info(f"🎯 Config: Provider={request.provider} | Model={request.model} | Ultra-Thinking={request.ultra_thinking}")
        
        # XIONIMUS CODING-ASSISTENT: System-Prompt NUR bei Coding-Anfragen
        # Füge System-Prompt nur ein, wenn:
        # 1. Noch keine System-Message existiert
        # 2. Es eine Coding-bezogene Anfrage ist (verhindert doppelte Antworten bei Small Talk)
        has_system_message = any(msg["role"] == "system" for msg in messages_dict)
        
        # Prüfe ob es eine Coding-Anfrage ist
        last_user_msg = next((msg for msg in reversed(messages_dict) if msg["role"] == "user"), None)
        is_coding_request = False
        if last_user_msg:
            is_coding_request = coding_prompt_manager.is_coding_related(last_user_msg["content"])
        
        if not has_system_message and messages_dict and is_coding_request:
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
        elif not is_coding_request:
            logger.info(f"💬 Small Talk erkannt - kein Coding System-Prompt nötig")
        
        # RESEARCH-FRAGE AUTOMATISCH STELLEN
        # Prüfe ob wir Research-Optionen anbieten sollten
        # Skip research workflow if developer_mode is explicitly set
        if not skip_research_workflow and coding_prompt_manager.should_offer_research(messages_dict):
            # Erkenne Sprache
            last_user_msg = next((msg for msg in reversed(messages_dict) if msg["role"] == "user"), None)
            language = "de"
            if last_user_msg:
                content_lower = last_user_msg["content"].lower()
                english_indicators = ["create", "build", "develop", "please", "help me", "i want", "i need"]
                if any(indicator in content_lower for indicator in english_indicators):
                    language = "en"
            
            # Generiere Research-Frage mit klickbaren Optionen (inkl. Auto-Option)
            coding_request = last_user_msg.get("content", "") if last_user_msg else ""
            research_options = coding_prompt_manager.generate_research_question(language, coding_request)
            
            logger.info("🔍 Erste Coding-Anfrage erkannt - stelle Research-Frage mit Auto-Option und klickbaren Optionen")
            
            # Gib Research-Frage direkt zurück (ohne AI zu befragen)
            return ChatResponse(
                content=research_options["message"],
                model="xionimus-workflow",
                provider="system",
                timestamp=datetime.now(timezone.utc),
                usage={
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                session_id=session_id,
                message_id=str(uuid.uuid4()),
                quick_actions=research_options  # Klickbare Research-Optionen
            )
        
        # RESEARCH-CHOICE ERKENNUNG & DURCHFÜHRUNG
        # Prüfe ob letzte User-Message eine Research-Choice ist
        # Skip if developer_mode is explicitly set
        research_performed = False
        research_sources = []  # Store research sources for frontend display
        if not skip_research_workflow and messages_dict and messages_dict[-1]["role"] == "user":
            last_user_message = messages_dict[-1]["content"]
            research_choice = coding_prompt_manager.detect_research_choice(last_user_message)
            
            if research_choice:
                logger.info(f"🔍 Research-Choice erkannt: {research_choice}")
                
                # Wenn "keine" gewählt wurde, bestätige und fahre fort
                if research_choice == "none":
                    logger.info("✅ Keine Recherche gewünscht - fahre direkt mit Coding fort")
                else:
                    # Handle "auto" choice - calculate optimal size
                    if research_choice == "auto":
                        # Finde Coding-Request für Komplexitätsberechnung
                        coding_request_for_calc = None
                        for i in range(len(messages_dict) - 2, -1, -1):
                            if messages_dict[i]["role"] == "user":
                                potential = messages_dict[i]["content"]
                                if coding_prompt_manager.is_coding_related(potential):
                                    coding_request_for_calc = potential
                                    break
                        
                        # Berechne optimale Größe
                        complexity = coding_prompt_manager._calculate_prompt_complexity(coding_request_for_calc or "")
                        if complexity < 3:
                            research_choice = "small"
                            logger.info(f"⚡ AUTO: Niedrige Komplexität ({complexity}) → KLEIN")
                        elif complexity > 6:
                            research_choice = "large"
                            logger.info(f"⚡ AUTO: Hohe Komplexität ({complexity}) → GROSS")
                        else:
                            research_choice = "medium"
                            logger.info(f"⚡ AUTO: Mittlere Komplexität ({complexity}) → MITTEL")
                    
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
                        
                        # 🎯 Hybrid Routing: Wähle optimales Research-Modell
                        research_model_config = coding_prompt_manager.get_research_model(
                            research_choice, 
                            topic=coding_request  # Pass topic for intelligent analysis
                        )
                        research_model = research_model_config["model"]
                        
                        logger.info(f"🔍 Research-Modell: {research_model} (${research_model_config['cost_per_1m']}/1M)")
                        logger.info(f"💡 Grund: {research_model_config['reason']}")
                        logger.info(f"🔍 Research-Prompt: {research_prompt[:100]}...")
                        
                        # Minimales Progress Tracking - nur bei sehr großen Research
                        show_progress = research_choice == "large"
                        
                        try:
                            # 🎯 PHASE 2: Perplexity Deep Research with Anthropic fallback
                            # Try Perplexity sonar-deep-research first
                            try:
                                logger.info("🔍 Trying Perplexity Deep Research (sonar-deep-research)...")
                                research_response = await ai_manager.generate_response(
                                    provider="perplexity",
                                    model="sonar-deep-research",  # Always use deep research
                                    messages=[{"role": "user", "content": research_prompt}],
                                    stream=False,
                                    api_keys=request.api_keys
                                )
                            except Exception as perplexity_error:
                                # Fallback to Anthropic Claude for research
                                logger.warning(f"⚠️ Perplexity failed: {perplexity_error}")
                                logger.info("🔄 Falling back to Anthropic Claude Sonnet for research...")
                                research_response = await ai_manager.generate_response(
                                    provider="anthropic",
                                    model="claude-sonnet-4-5-20250929",
                                    messages=[{"role": "user", "content": research_prompt}],
                                    stream=False,
                                    api_keys=request.api_keys
                                )
                            
                            research_content = research_response.get("content", "")
                            citations = research_response.get("citations", [])
                            search_results = research_response.get("search_results", [])
                            
                            # Format sources for frontend
                            # Use search_results if available (has more info), otherwise use citations
                            if search_results:
                                for result in search_results:
                                    research_sources.append({
                                        "url": result.get("url", ""),
                                        "title": result.get("name", result.get("url", "Unknown Source")),
                                        "snippet": result.get("snippet", ""),
                                        "status": "completed",
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    })
                                logger.info(f"✅ Verwendet search_results: {len(search_results)} Quellen mit Details")
                            elif citations:
                                # Fallback to citations if search_results not available
                                for citation in citations:
                                    # Try to extract a better title from URL
                                    title = citation.split('/')[2] if '/' in citation else citation  # Extract domain
                                    if '/' in citation:
                                        path_parts = citation.split('/')
                                        if len(path_parts) > 3:
                                            # Try to get page name from last path segment
                                            page_name = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
                                            if page_name and len(page_name) > 2:
                                                title = f"{path_parts[2]} - {page_name}"
                                    
                                    research_sources.append({
                                        "url": citation,
                                        "title": title,
                                        "status": "completed",
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    })
                                logger.info(f"✅ Verwendet citations: {len(citations)} Quellen")
                            
                            if research_content:
                                logger.info(f"✅ Research erfolgreich: {len(research_content)} Zeichen")
                                logger.info(f"✅ Gefunden: {len(citations)} Citations, {len(search_results)} Search Results")
                                logger.info(f"✅ Formatiert: {len(research_sources)} Sources für Frontend")
                                
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
                                
                                # DIREKT MIT CODING BEGINNEN (ohne Klärungsfragen)
                                logger.info("🚀 Research abgeschlossen - erstelle erweiterten Coding-Prompt...")
                                
                                # Entferne Research-Choice Message UND Research-Options Message
                                # So dass nur noch die Original User-Anfrage bleibt
                                while len(messages_dict) > 0 and (
                                    messages_dict[-1].get("role") == "assistant" or
                                    coding_prompt_manager.detect_research_choice(messages_dict[-1].get("content", ""))
                                ):
                                    messages_dict.pop()
                                
                                # WICHTIG: Erstelle EINE neue User-Message mit Research + Coding-Request
                                # Dies vermeidet Extended Thinking Probleme mit Assistant-Messages
                                if language == "de":
                                    enhanced_coding_prompt = f"""Basierend auf folgender Recherche, erstelle vollständigen Code:

**Recherche-Ergebnisse:**
{research_content[:3000]}

**Aufgabe:**
{coding_request}

Erstelle lauffähigen, produktionsreifen Code mit allen notwendigen Dateien."""
                                else:
                                    enhanced_coding_prompt = f"""Based on the following research, create complete code:

**Research Results:**
{research_content[:3000]}

**Task:**
{coding_request}

Create production-ready, runnable code with all necessary files."""
                                
                                # Füge neue User-Message hinzu (statt letzte zu ersetzen)
                                messages_dict.append({
                                    "role": "user",
                                    "content": enhanced_coding_prompt
                                })
                                
                                research_performed = True
                                # research_sources bleibt im Scope und wird später in der finalen Response verwendet
                                logger.info(f"✅ Research abgeschlossen mit {len(research_sources)} Sources - fahre fort mit Code-Generierung")
                                
                                # 🚀 HYBRID MULTI-AGENT MODE
                                # If multi_agent_mode enabled, use orchestrator instead of single agent
                                if request.multi_agent_mode:
                                    logger.info("🎯 MULTI-AGENT MODE: Initiating agent orchestration")
                                    
                                    try:
                                        orchestrator = get_orchestrator(ai_manager)
                                        
                                        # Plan agents based on request
                                        tasks = orchestrator.plan_agents(coding_request, research_content)
                                        logger.info(f"📋 Planned {len(tasks)} specialized agents")
                                        
                                        # Execute agents in parallel
                                        multi_agent_result = await orchestrator.execute_parallel(
                                            api_keys=request.api_keys or {},
                                            user_request=coding_request,
                                            research_data=research_content
                                        )
                                        
                                        # Use consolidated multi-agent output as response
                                        if multi_agent_result.get("success"):
                                            response = {
                                                "content": multi_agent_result["code"] + "\n\n" + multi_agent_result["documentation"],
                                                "provider": "multi-agent",
                                                "model": "hybrid-system",
                                                "agent_tasks": multi_agent_result["agent_tasks"]
                                            }
                                            logger.info("✅ Multi-Agent execution successful")
                                            
                                            # Skip normal single-agent code generation
                                            # Jump to saving and return
                                            message_id = str(uuid.uuid4())
                                            timestamp = datetime.now(timezone.utc)
                                            
                                            # Save to database
                                            background_tasks.add_task(
                                                save_chat_message,
                                                current_user.user_id, session_id, messages_dict[-1], response, message_id, timestamp
                                            )
                                            
                                            return ChatResponse(
                                                content=response["content"],
                                                provider=response["provider"],
                                                model=response["model"],
                                                session_id=session_id,
                                                message_id=message_id,
                                                usage=None,
                                                timestamp=timestamp,
                                                research_sources=research_sources,
                                                agent_results=multi_agent_result["agent_tasks"]
                                            )
                                    except Exception as e:
                                        logger.error(f"❌ Multi-Agent execution failed: {e}")
                                        logger.info("⚠️ Falling back to single-agent mode")
                                        # Continue with normal single-agent flow below
                                
                                # Der messages_dict enthält jetzt:
                                # 1. Original User Request
                                # 2. Assistant: Research-Ergebnisse  
                                # 3. User: "Erstelle jetzt den Code..."
                                # research_sources bleibt verfügbar für die finale Response
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
        
        # Auto Code Review removed - chat only mode
        
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
        
        # 🔍 CHECK: Prüfe ob Research im Context ist
        research_in_context = False
        research_size_in_context = 0
        for msg in messages_dict:
            if "Recherche abgeschlossen" in msg.get("content", "") or "Research completed" in msg.get("content", ""):
                research_in_context = True
                research_size_in_context = len(msg.get("content", ""))
                logger.info(f"✅ Research-Context gefunden! Länge: {research_size_in_context} Zeichen")
                break
        
        if research_in_context:
            logger.info("🔍 Code wird MIT Research-Informationen generiert")
        else:
            logger.info("ℹ️ Code wird OHNE Research-Informationen generiert (User hat keine Research gewählt)")
        
        # Minimales Progress Tracking - nur bei sehr langen Operationen
        # (Progress Tracker wird nicht mehr für normale Chat-Anfragen verwendet)
        
        # 🎯 PHASE 2: Claude Smart Routing - Only for Senior Mode
        if (developer_mode_manager.should_use_smart_routing(request.developer_mode) and 
            request.provider == "anthropic" and "sonnet" in request.model.lower()):
            recommended_model = claude_router.get_recommended_model(messages_dict, request.model)
            if recommended_model != request.model:
                logger.info(f"🚀 SENIOR MODE: Smart routing upgraded {request.model} → {recommended_model}")
                request.model = recommended_model
        elif request.developer_mode == "junior":
            logger.info(f"🌱 JUNIOR MODE: Using Claude Haiku (no smart routing)")
        
        # Generate response with classic AI manager (with automatic fallback)
        try:
            response = await ai_manager.generate_response(
                provider=request.provider,
                model=request.model,
                messages=messages_dict,
                stream=request.stream,
                api_keys=request.api_keys,
                ultra_thinking=request.ultra_thinking
            )
        except Exception as e:
            # 🎯 PHASE 2: Auto-fallback - Sonnet → Opus → GPT-4o
            logger.error(f"❌ Primary model failed: {str(e)}")
            
            if request.provider == "anthropic" and "sonnet" in request.model.lower():
                # Fallback to Opus 4.1
                fallback_model = "claude-opus-4-1"
                logger.info(f"⚠️ PHASE 2: Falling back from Sonnet to Opus 4.1")
                try:
                    response = await ai_manager.generate_response(
                        provider=request.provider,
                        model=fallback_model,
                        messages=messages_dict,
                        stream=request.stream,
                        api_keys=request.api_keys,
                        ultra_thinking=request.ultra_thinking
                    )
                except Exception as e2:
                    # Final fallback to OpenAI GPT-4o
                    logger.error(f"❌ Opus also failed, falling back to OpenAI GPT-4o")
                    response = await ai_manager.generate_response(
                        provider="openai",
                        model="gpt-4o",
                        messages=messages_dict,
                        stream=request.stream,
                        api_keys=request.api_keys,
                        ultra_thinking=False  # GPT doesn't support ultra-thinking
                    )
            elif request.provider == "anthropic" and "opus" in request.model.lower():
                # Opus failed, fallback to OpenAI
                logger.info(f"⚠️ PHASE 2: Falling back from Opus to OpenAI GPT-4o")
                response = await ai_manager.generate_response(
                    provider="openai",
                    model="gpt-4o",
                    messages=messages_dict,
                    stream=request.stream,
                    api_keys=request.api_keys,
                    ultra_thinking=False
                )
            else:
                # Re-raise if not Claude
                raise
        
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
            
            # 💡 AUTO-SUMMARY: Generate brief summary and recommendations after coding
            try:
                # Detect language from messages
                language = "de"
                if messages_dict and len(messages_dict) > 0:
                    first_user_msg = next((msg for msg in messages_dict if msg["role"] == "user"), None)
                    if first_user_msg:
                        content_lower = first_user_msg["content"].lower()
                        english_indicators = ["create", "build", "develop", "please", "help me", "i want"]
                        if any(indicator in content_lower for indicator in english_indicators):
                            language = "en"
                
                # Create prompt for summary
                if language == "de":
                    summary_prompt = f"""Analysiere diesen generierten Code und gib eine SEHR KURZE Antwort (maximal 2-3 Sätze):

Code-Dateien: {', '.join(code_process_result.get('files', []))}

1. Was wurde implementiert? (1 Satz)
2. Empfohlene nächste Schritte? (1-2 Sätze)

Antworte direkt und prägnant, ohne Einleitung."""
                else:
                    summary_prompt = f"""Analyze this generated code and provide a VERY BRIEF response (max 2-3 sentences):

Code files: {', '.join(code_process_result.get('files', []))}

1. What was implemented? (1 sentence)
2. Recommended next steps? (1-2 sentences)

Answer directly and concisely, without introduction."""
                
                # Use cost-effective model for summary (gpt-4o-mini)
                summary_response = await ai_manager.generate_response(
                    provider="openai",
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": summary_prompt}],
                    stream=False,
                    api_keys=request.api_keys
                )
                
                auto_summary = summary_response.get("content", "").strip()
                logger.info(f"💡 Auto-summary generated: {auto_summary[:100]}...")
                
                # Add summary after code summary
                response["content"] = f"{cleaned_content.strip()}\n\n{code_summary}\n\n---\n\n**💡 Zusammenfassung & Empfehlungen:**\n\n{auto_summary}"
            except Exception as e:
                logger.error(f"❌ Failed to generate auto-summary: {str(e)}")
                # Fallback: just use code summary without auto-summary
                response["content"] = f"{cleaned_content.strip()}\n\n{code_summary}"
            
            logger.info(f"🎯 Code processing: {code_process_result['files_written']} files written with enhanced summary")
            
            # 🤖 AUTO-AGENTS: Testing, Review & Documentation
            # NUR aktivieren wenn Code von Claude Sonnet 4-5 generiert wurde
            used_model = response.get("model", "").lower()
            is_sonnet_45 = "sonnet-4" in used_model or "sonnet-5" in used_model
            
            if is_sonnet_45:
                logger.info(f"🚀 Aktiviere Auto-Agents (Code von {response.get('model')} generiert)...")
            else:
                logger.info(f"ℹ️ Auto-Agents übersprungen (Code von {response.get('model')}, nicht Sonnet 4-5)")
            
            agent_results = []
            
            # 1. TESTING AGENT (nur bei Sonnet 4-5)
            if is_sonnet_45:
                try:
                    testing_agent = TestingAgent()
                    # Generate test code for generated files
                    test_prompt = f"""Erstelle vollständige automatische Tests für diesen generierten Code:

{ai_content[:3000]}

Erstelle:
1. Unit Tests für alle Funktionen
2. Integration Tests
3. Test-Setup und Konfiguration

Format: Vollständige Test-Dateien mit Code-Blöcken."""

                    # 🎯 Hybrid Model Router: Smart test generation
                    from ..core.hybrid_model_router import HybridModelRouter, TaskCategory
                    hybrid_router = HybridModelRouter()
                    test_model_config = hybrid_router.get_model_for_testing(
                        test_prompt,
                        context={"type": "test_generation", "original_prompt": user_message}
                    )
                    
                    test_response = await ai_manager.generate_response(
                        provider=test_model_config["provider"],
                        model=test_model_config["model"],
                        messages=[{"role": "user", "content": test_prompt}],
                        stream=False,
                        api_keys=request.api_keys
                    )
                    
                    logger.info(
                        f"🧪 Test Generation using {test_model_config['model']} "
                        f"({test_model_config['reason']})"
                    )
                    
                    test_content = test_response.get("content", "")
                    if test_content:
                        agent_results.append({
                            "agent": "Testing",
                            "icon": "🧪",
                            "content": test_content,
                            "summary": f"Tests generiert ({len(test_content)} Zeichen)"
                        })
                        logger.info("✅ Testing Agent abgeschlossen")
                except Exception as e:
                    logger.error(f"❌ Testing Agent failed: {e}")
            
            # Code Review Agent removed - chat only mode
            
            # 3. DOCUMENTATION AGENT (nur bei Sonnet 4-5)
            if is_sonnet_45:
                try:
                    doc_result = await documentation_agent.generate_documentation(
                        code_files=code_process_result['files'],
                        project_description=user_last_message if 'user_last_message' in locals() else "Generated code project",
                        ai_manager=ai_manager,
                        api_keys=request.api_keys
                    )
                    
                    if doc_result.get("success"):
                        doc_summary = documentation_agent.format_documentation_summary(doc_result)
                        agent_results.append({
                            "agent": "Documentation",
                            "icon": "📚",
                            "content": doc_summary,
                            "summary": "README erstellt"
                        })
                        logger.info("✅ Documentation Agent abgeschlossen")
                except Exception as e:
                    logger.error(f"❌ Documentation Agent failed: {e}")
            
            # Add all agent results to response
            if agent_results:
                # Return structured agent results instead of appending to content
                response["agent_results"] = agent_results
                logger.info(f"✅ Alle {len(agent_results)} Agenten erfolgreich abgeschlossen")
            
        # Auto-routing removed - chat only mode
        
        # GENERATE QUICK ACTIONS after code generation
        # Help user know what they can do next
        if code_process_result and code_process_result.get('has_code'):
            quick_actions = {
                "message": "💡 Wie kann ich weiterhelfen?",
                "options": [
                    {
                        "id": "add_feature",
                        "title": "➕ Feature hinzufügen",
                        "description": "Erweitere den Code mit neuen Funktionen",
                        "action": "add_feature"
                    },
                    {
                        "id": "improve_code",
                        "title": "🔧 Code verbessern",
                        "description": "Optimiere Performance, Lesbarkeit oder Struktur",
                        "action": "improve"
                    },
                    {
                        "id": "add_tests",
                        "title": "🧪 Tests hinzufügen",
                        "description": "Erstelle Unit Tests und Integrationstests",
                        "action": "add_tests"
                    },
                    {
                        "id": "documentation",
                        "title": "📚 Dokumentation",
                        "description": "Erweitere Kommentare und README",
                        "action": "documentation"
                    }
                ]
            }
            response["quick_actions"] = quick_actions
            logger.info("💡 Quick actions added to response")
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Save to database in background
        background_tasks.add_task(
            save_chat_message,
            current_user.user_id, session_id, messages_dict[-1], response, message_id, timestamp
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
        
        # 📊 Track token usage
        usage = response.get("usage", {})
        if usage:
            token_tracker.track_usage(
                session_id=session_id,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )
        
        # Get current token stats
        token_stats = token_tracker.get_usage_stats()
        
        # 🎯 POST-CODE OPTIONS: Offer options after code generation
        post_code_options = None
        if coding_prompt_manager.should_offer_post_code_options(messages_dict + [{"role": "assistant", "content": response["content"]}]):
            # Detect language
            language = "de"
            first_user_msg = next((msg for msg in messages_dict if msg["role"] == "user"), None)
            if first_user_msg:
                content_lower = first_user_msg["content"].lower()
                english_indicators = ["create", "build", "develop", "please", "help me", "i want", "i need"]
                if any(indicator in content_lower for indicator in english_indicators):
                    language = "en"
            
            post_code_options = coding_prompt_manager.generate_post_code_options(language)
            logger.info("🎯 Post-Code Optionen werden angeboten")
        
        return ChatResponse(
            content=response["content"],
            provider=response["provider"],
            model=response["model"],
            session_id=session_id,
            message_id=message_id,
            usage=response.get("usage"),
            timestamp=timestamp,
            context_stats=final_context_stats,  # NEW: Include context statistics
            token_usage=token_stats,  # NEW: Include token usage stats
            quick_actions=post_code_options,  # NEW: Post-code options
            research_sources=research_sources if research_sources else None  # NEW: Research sources from Perplexity
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

@router.get("/hybrid-routing-info")
async def get_hybrid_routing_info(current_user: User = Depends(get_current_user)):
    """
    Get information about hybrid routing cost savings
    """
    from ..core.hybrid_model_router import HybridModelRouter
    
    hybrid_router = HybridModelRouter()
    savings_report = hybrid_router.get_cost_savings_report()
    
    return {
        "enabled": True,
        "strategy": "Smart cost-quality optimization",
        "savings_report": savings_report,
        "description": "Automatically selects optimal models based on task complexity"
    }

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
    user_id: str, session_id: str, user_message: dict, ai_response: dict, 
    message_id: str, timestamp: datetime
):
    """Background task to save chat message - creates its own DB session"""
    db = None
    try:
        # Create a new database session for this background task
        from ..core.database import SessionLocal
        db = SessionLocal()
        
        timestamp_str = timestamp.isoformat()
        
        # Get or create session
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            session = SessionModel(
                id=session_id,
                name=f"Chat {timestamp.strftime('%Y-%m-%d %H:%M')}",
                user_id=user_id,  # Associate with user
                created_at=timestamp_str,
                updated_at=timestamp_str
            )
            db.add(session)
            logger.info(f"✅ Created new session: {session_id} for user: {user_id}")
        else:
            session.updated_at = timestamp_str
            logger.info(f"📝 Updated existing session: {session_id}")
        
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
            provider=ai_response.get("provider", "unknown"),
            model=ai_response.get("model", "unknown"),
            timestamp=timestamp_str
        )
        db.add(ai_msg)
        
        db.commit()
        logger.info(f"✅ Successfully saved messages to session {session_id}")
    
    except IntegrityError as e:
        if db:
            db.rollback()
        logger.error(f"❌ Database integrity error saving message: {e}", exc_info=True)
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        logger.error(f"❌ Database error saving message: {e}", exc_info=True)
    except Exception as e:
        if db:
            db.rollback()
        logger.critical(f"❌ Unexpected error saving message: {e}", exc_info=True)
    finally:
        if db:
            db.close()
            logger.debug(f"🔒 Closed database session for background task")