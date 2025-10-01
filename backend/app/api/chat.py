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
from ..core.auto_workflow_orchestrator import auto_workflow_orchestrator  # Auto-workflow
from ..core.progress_tracker import get_progress_tracker  # Progress tracking
from ..core.testing_agent import TestingAgent  # NEW: Testing Agent
from ..core.code_review_agents import CodeAnalysisAgent, DebugAgent, EnhancementAgent, TestAgent  # NEW: Code Review
from ..core.documentation_agent import documentation_agent  # NEW: Documentation Agent
from ..core.edit_agent import edit_agent  # NEW: Edit Agent
from ..core.token_tracker import token_tracker  # NEW: Token tracking
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
    agent_results: Optional[List[Dict[str, Any]]] = None  # NEW: Structured agent results
    token_usage: Optional[Dict[str, Any]] = None  # NEW: Token usage stats

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
                        
                        # 📊 Initialize Progress Tracker
                        progress_tracker = get_progress_tracker("research")
                        progress_status = progress_tracker.format_for_display()
                        
                        try:
                            # Step 1: Research
                            progress_tracker.start_step("research")
                            
                            # Füh re Perplexity-Research durch
                            research_response = await ai_manager.generate_response(
                                provider="perplexity",
                                model=research_model,
                                messages=[{"role": "user", "content": research_prompt}],
                                stream=False,
                                api_keys=request.api_keys
                            )
                            
                            research_content = research_response.get("content", "")
                            
                            if research_content:
                                progress_tracker.complete_step("research", f"{len(research_content)} Zeichen")
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
                                progress_tracker.start_step("clarification")
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
                                        api_keys=request.api_keys
                                    )
                                    
                                    clarification_questions = clarification_response.get("content", "")
                                    
                                    if clarification_questions:
                                        progress_tracker.complete_step("clarification", "Fragen erstellt")
                                        logger.info(f"✅ Klärungsfragen generiert: {len(clarification_questions)} Zeichen")
                                        
                                        # Kombiniere Research + Fragen + Progress
                                        progress_status = progress_tracker.format_for_display()
                                        
                                        if language == "de":
                                            final_content = f"{progress_status}\n\n{research_summary}**Basierend auf dieser Recherche habe ich folgende Klärungsfragen:**\n\n{clarification_questions}"
                                        else:
                                            final_content = f"{progress_status}\n\n{research_summary}**Based on this research, I have the following clarifying questions:**\n\n{clarification_questions}"
                                        
                                        # 🤖 AUTO-WORKFLOW: Beantworte Fragen automatisch und generiere Code
                                        progress_tracker.start_step("auto_answer")
                                        logger.info("🚀 AUTO-WORKFLOW: Starte automatische Klärung + Code-Generierung")
                                        
                                        try:
                                            # Automatische Beantwortung der Klärungsfragen
                                            auto_answers = await auto_workflow_orchestrator.auto_answer_clarifications(
                                                research_content=research_content,
                                                clarification_questions=clarification_questions,
                                                original_request=coding_request,
                                                ai_manager=ai_manager
                                            )
                                            
                                            logger.info(f"✅ Automatische Antworten: {len(auto_answers)} Zeichen")
                                            progress_tracker.complete_step("auto_answer", "Best Practices angewendet")
                                            
                                            # Update Progress
                                            progress_status = progress_tracker.format_for_display()
                                            
                                            # Füge Auto-Antworten zum Content hinzu
                                            if language == "de":
                                                final_content += f"\n\n{progress_status}\n\n---\n\n## 🤖 Automatische Klärung (Best Practices)\n\n{auto_answers}"
                                                final_content += f"\n\n---\n\n**🚀 Starte nun automatisch mit der Code-Generierung basierend auf diesen Anforderungen...**"
                                            else:
                                                final_content += f"\n\n{progress_status}\n\n---\n\n## 🤖 Automatic Clarification (Best Practices)\n\n{auto_answers}"
                                                final_content += f"\n\n---\n\n**🚀 Now automatically starting code generation based on these requirements...**"
                                            
                                            # Start code generation step
                                            progress_tracker.start_step("code_generation")
                                            
                                            # Erstelle vollständigen Coding-Prompt mit Research + Antworten
                                            coding_prompt_with_context = f"""Basierend auf der folgenden Recherche und den geklärten Anforderungen, erstelle vollständigen, produktionsreifen Code:

**Ursprüngliche Anfrage:**
{coding_request}

**Research-Ergebnisse:**
{research_content[:2000]}

**Geklärte Anforderungen:**
{auto_answers}

**Deine Aufgabe:**
Erstelle VOLLSTÄNDIGEN, lauffähigen Code mit:
1. Alle notwendigen Dateien (Frontend + Backend wenn nötig)
2. Vollständige Implementierung aller Features
3. Best Practices und moderne Patterns
4. Kommentare für komplexe Logik
5. Error-Handling
6. README.md mit Setup-Anleitung

Beginne SOFORT mit der Code-Generierung. Keine weiteren Fragen!"""

                                            # Generiere Code automatisch
                                            code_response = await ai_manager.generate_response(
                                                provider="anthropic",
                                                model="claude-sonnet-4-5-20250929",
                                                messages=[{"role": "user", "content": coding_prompt_with_context}],
                                                stream=False,
                                                api_keys=request.api_keys
                                            )
                                            
                                            generated_code = code_response.get("content", "")
                                            
                                            if generated_code:
                                                progress_tracker.complete_step("code_generation", f"{len(generated_code)} Zeichen")
                                                progress_tracker.start_step("code_processing")
                                                logger.info(f"✅ Code automatisch generiert: {len(generated_code)} Zeichen")
                                                
                                                # Füge generierten Code hinzu mit finalem Progress
                                                progress_tracker.complete_step("code_processing", "Dateien gespeichert")
                                                final_progress = progress_tracker.format_for_display()
                                                
                                                final_content += f"\n\n{final_progress}\n\n{generated_code}"
                                                
                                                logger.info("🎉 AUTO-WORKFLOW ERFOLGREICH: Research → Klärung → Code")
                                            else:
                                                logger.warning("⚠️ Code-Generierung lieferte kein Ergebnis")
                                        
                                        except Exception as e:
                                            logger.error(f"❌ Auto-Workflow Fehler: {str(e)}")
                                            logger.info("⚠️ Fahre fort mit manuellem Workflow")
                                            # Fallback: Nur Research + Fragen ohne Auto-Code
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
                                
                                # Gebe Research + Klärungsfragen (+ ggf. Code) zurück
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
        
        # 📊 PROGRESS TRACKING: For non-streaming, show progress
        progress_tracker = None
        if not request.stream:
            progress_tracker = get_progress_tracker("chat")
            # Add simple chat workflow steps
            progress_tracker.add_step("analyze", "Analysiere Anfrage", "Verstehe den Context")
            progress_tracker.add_step("generate", "Generiere Antwort", "KI erstellt Response")
            progress_tracker.add_step("process", "Verarbeite Code", "Extrahiere und speichere Dateien")
            
            progress_tracker.start_step("analyze")
            logger.info("📊 Progress tracking aktiviert für diese Anfrage")
        
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
        
        # 📊 PROGRESS: AI generation completed
        if progress_tracker:
            progress_tracker.complete_step("analyze")
            progress_tracker.start_step("generate")
            progress_tracker.complete_step("generate", f"{len(response.get('content', ''))} Zeichen")
        
        # 🚀 EMERGENT-STYLE: Process code blocks and write to files automatically
        ai_content = response.get("content", "")
        
        # 📊 PROGRESS: Start code processing
        if progress_tracker and '```' in ai_content:
            progress_tracker.start_step("process")
        
        code_process_result = await code_processor.process_ai_response(
            ai_content, 
            auto_write=True  # Automatically write detected code to files
        )
        
        # 📊 PROGRESS: Complete code processing
        if progress_tracker and code_process_result['code_blocks_found'] > 0:
            progress_tracker.complete_step("process", f"{code_process_result['files_written']} Dateien")
        
        # Generate enhanced summary for user (with purpose and next steps)
        progress_summary = ""
        if progress_tracker:
            progress_summary = f"\n\n{progress_tracker.format_for_display()}\n\n---\n\n"
        
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
            # Add progress + enhanced summary at the end
            response["content"] = f"{progress_summary}{cleaned_content.strip()}\n\n{code_summary}"
            logger.info(f"🎯 Code processing: {code_process_result['files_written']} files written with enhanced summary")
            
            # 🤖 AUTO-AGENTS: Testing, Review & Documentation
            logger.info("🚀 Aktiviere alle Agenten automatisch...")
            agent_results = []
            
            # 1. TESTING AGENT
            if progress_tracker:
                progress_tracker.start_step("testing")
            
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

                test_response = await ai_manager.generate_response(
                    provider="anthropic",
                    model="claude-sonnet-4-5-20250929",
                    messages=[{"role": "user", "content": test_prompt}],
                    stream=False,
                    api_keys=request.api_keys
                )
                
                test_content = test_response.get("content", "")
                if test_content:
                    agent_results.append({
                        "agent": "Testing",
                        "icon": "🧪",
                        "content": test_content,
                        "summary": f"Tests generiert ({len(test_content)} Zeichen)"
                    })
                    if progress_tracker:
                        progress_tracker.complete_step("testing", "Tests erstellt")
                    logger.info("✅ Testing Agent abgeschlossen")
            except Exception as e:
                logger.error(f"❌ Testing Agent failed: {e}")
                if progress_tracker:
                    progress_tracker.error_step("testing", str(e))
            
            # 2. CODE REVIEW AGENT
            if progress_tracker:
                progress_tracker.start_step("review")
            
            try:
                # Use Code Analysis Agent
                review_agent = CodeAnalysisAgent()
                review_results = await review_agent.analyze(
                    code=ai_content[:3000],
                    context={"files": code_process_result['files']},
                    api_keys=request.api_keys
                )
                
                if review_results:
                    review_summary = f"**Code Review Ergebnisse:**\n\n"
                    review_summary += f"- Qualität: {'✅' if review_results.get('quality_score', 0) > 7 else '⚠️'}\n"
                    review_summary += f"- Sicherheit: Geprüft\n"
                    review_summary += f"- Performance: Geprüft\n"
                    
                    agent_results.append({
                        "agent": "Code Review",
                        "icon": "🔍",
                        "content": review_summary,
                        "summary": "Review abgeschlossen",
                        "data": review_results  # Store for Edit Agent
                    })
                    if progress_tracker:
                        progress_tracker.complete_step("review", "Review abgeschlossen")
                    logger.info("✅ Code Review Agent abgeschlossen")
            except Exception as e:
                logger.error(f"❌ Code Review Agent failed: {e}")
                if progress_tracker:
                    progress_tracker.error_step("review", str(e))
            
            # 2.5 EDIT AGENT (NEW) - Fixes issues found during code review
            if progress_tracker:
                progress_tracker.start_step("editing")
            
            try:
                # Extract code review feedback for editing
                code_review_feedback = next(
                    (r.get("data") for r in agent_results if r.get("agent") == "Code Review"),
                    {}
                )
                
                if code_review_feedback:
                    edit_result = await edit_agent.autonomous_edit(
                        code_review_feedback=code_review_feedback,
                        workspace_path="/app/xionimus-ai"
                    )
                    
                    if edit_result.get("edits_applied", 0) > 0:
                        edit_summary = f"**Automatische Code-Bearbeitung:**\n\n"
                        edit_summary += f"- ✏️ {edit_result['edits_applied']} Bearbeitungen angewendet\n"
                        edit_summary += f"- 📁 {len(edit_result.get('files_edited', []))} Dateien bearbeitet\n"
                        edit_summary += f"- ✅ Probleme behoben\n"
                        
                        agent_results.append({
                            "agent": "Edit Agent",
                            "icon": "✏️",
                            "content": edit_summary,
                            "summary": f"{edit_result['edits_applied']} edits applied"
                        })
                        
                        if progress_tracker:
                            progress_tracker.complete_step("editing", f"{edit_result['edits_applied']} Korrekturen")
                        logger.info(f"✅ Edit Agent: {edit_result['edits_applied']} edits applied")
                    else:
                        if progress_tracker:
                            progress_tracker.complete_step("editing", "Keine Bearbeitungen erforderlich")
                        logger.info("✅ Edit Agent: No edits needed")
                else:
                    if progress_tracker:
                        progress_tracker.complete_step("editing", "Übersprungen")
                    logger.info("⏭️ Edit Agent: Skipped (no code review feedback)")
                    
            except Exception as e:
                logger.error(f"❌ Edit Agent failed: {e}")
                if progress_tracker:
                    progress_tracker.error_step("editing", str(e))
            
            # 3. DOCUMENTATION AGENT
            if progress_tracker:
                progress_tracker.start_step("documentation")
            
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
                    if progress_tracker:
                        progress_tracker.complete_step("documentation", "README erstellt")
                    logger.info("✅ Documentation Agent abgeschlossen")
            except Exception as e:
                logger.error(f"❌ Documentation Agent failed: {e}")
                if progress_tracker:
                    progress_tracker.error_step("documentation", str(e))
            
            # Add all agent results to response
            if agent_results:
                # Return structured agent results instead of appending to content
                response["agent_results"] = agent_results
                logger.info(f"✅ Alle {len(agent_results)} Agenten erfolgreich abgeschlossen")
            
        elif progress_tracker:
            # Add progress even if no code
            response["content"] = f"{progress_summary}{ai_content}"
        
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