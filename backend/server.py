from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from python_dotenv import load_dotenv
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import json
import zipfile
import tempfile
import shutil
import io
from openai import AsyncOpenAI
import openai
import anthropic
# Removed xionimus-ai-integrations dependency - using direct API clients
from ai_orchestrator import AIOrchestrator
from agents.agent_manager import AgentManager
# REMOVED: from xionimus_orchestrator import XionimusAIOrchestrator
from local_storage import LocalStorageManager, LocalClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Local Storage (No Docker Required)
storage_manager = LocalStorageManager(storage_dir=ROOT_DIR / 'local_data')
client = LocalClient(storage_manager)
db = client['xionimus_ai']

logging.info("🏠 Using Local Storage - No Docker Required!")

# Lifespan events for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with comprehensive logging"""
    logging.info("🚀 XIONIMUS AI Backend starting up...")
    
    try:
        # Test Local Storage connection
        await db.list_collection_names()
        logging.info("✅ Local Storage connection established")
        
        # Load API keys from Local Storage
        loaded_keys = await load_api_keys_from_local_storage()
        
        # Initialize AI Orchestrator if keys available
        services_available = []
        if os.environ.get('ANTHROPIC_API_KEY'):
            services_available.append("Claude 3.5 Sonnet")
        if os.environ.get('PERPLEXITY_API_KEY'):
            services_available.append("Perplexity Deep Research")
        if os.environ.get('OPENAI_API_KEY'):
            services_available.append("GPT-5")
        
        if services_available:
            logging.info(f"🤖 AI Services available: {', '.join(services_available)}")
        else:
            logging.warning("⚠️ No AI services configured - Please add API keys")
        
        logging.info("🎉 XIONIMUS AI Backend startup completed successfully")
        
    except Exception as e:
        logging.error(f"❌ Startup error: {str(e)}")
        logging.info("⚠️ Some features may not be available")
    
    yield  # Server runs here
    
    # Shutdown
    logging.info("🔄 XIONIMUS AI Backend shutting down...")
    client.close()
    logging.info("✅ Cleanup completed")

# Create the main app with lifespan
app = FastAPI(
    title="Xionimus AI", 
    description="Autonomous Artificial Intelligence with Specialized Agents",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global clients for reuse
perplexity_client = None
claude_client = None
ai_orchestrator = AIOrchestrator()
agent_manager = AgentManager()
# REMOVED: xionimus_orchestrator = XionimusAIOrchestrator(agent_manager)

async def get_perplexity_client():
    global perplexity_client
    if perplexity_client is None:
        api_key = os.environ.get('PERPLEXITY_API_KEY')
        if api_key:
            perplexity_client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
    return perplexity_client

async def get_claude_client():
    global claude_client
    if claude_client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            claude_client = anthropic.AsyncAnthropic(api_key=api_key)
    return claude_client

async def _format_agent_response(agent_name: str, agent_result: Dict[str, Any], language: str) -> str:
    """Format agent response for display"""
    if not isinstance(agent_result, dict):
        return str(agent_result)
    
    content = f"**{agent_name} Ergebnis:**\n\n"
    
    # Code Agent formatting
    if agent_name == "Code Agent":
        if 'main_code' in agent_result and agent_result['main_code']:
            language_code = agent_result.get('language', 'text')
            content += f"```{language_code}\n{agent_result['main_code']}\n```\n\n"
        
        if 'explanation' in agent_result:
            content += f"**Erklärung:**\n{agent_result['explanation']}\n\n"
        
        if 'recommendations' in agent_result and agent_result['recommendations']:
            content += f"**Empfehlungen:**\n"
            for rec in agent_result['recommendations'][:5]:
                content += f"• {rec}\n"
    
    # Research Agent formatting
    elif agent_name == "Research Agent":
        if 'research_content' in agent_result:
            content += agent_result['research_content']
        
        if 'sources' in agent_result and agent_result['sources']:
            content += f"\n\n**Quellen:**\n"
            for i, source in enumerate(agent_result['sources'][:5], 1):
                if isinstance(source, dict):
                    title = source.get('title', 'Unknown')
                    url = source.get('url', '')
                    content += f"{i}. [{title}]({url})\n"
    
    # Writing Agent formatting
    elif agent_name == "Writing Agent":
        if 'content' in agent_result:
            content += agent_result['content']
        
        if 'sections' in agent_result and agent_result['sections']:
            content += f"\n\n**Abschnitte:**\n"
            for section in agent_result['sections'][:5]:
                content += f"• {section}\n"
    
    # Data Agent formatting
    elif agent_name == "Data Agent":
        if 'main_code' in agent_result and agent_result['main_code']:
            content += f"```python\n{agent_result['main_code']}\n```\n\n"
        
        if 'insights' in agent_result and agent_result['insights']:
            content += f"**Wichtige Erkenntnisse:**\n"
            for insight in agent_result['insights'][:5]:
                content += f"• {insight}\n"
    
    # QA Agent formatting
    elif agent_name == "QA Agent":
        if 'qa_content' in agent_result:
            content += agent_result['qa_content']
        
        if 'tools_recommended' in agent_result and agent_result['tools_recommended']:
            content += f"\n\n**Empfohlene Tools:**\n"
            for tool in agent_result['tools_recommended'][:5]:
                content += f"• {tool}\n"
    
    # Generic formatting
    else:
        if 'summary' in agent_result:
            content += agent_result['summary']
        elif 'content' in agent_result:
            content += agent_result['content']
        else:
            content += str(agent_result)
    
    return content

# Pydantic Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: Optional[str] = None
    tokens_used: Optional[int] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []
    conversation_id: Optional[str] = None
    use_agent: Optional[bool] = True  # Enable intelligent orchestration by default

class ChatResponse(BaseModel):
    message: ChatMessage
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    agent_used: Optional[str] = None
    agent_result: Optional[Dict[str, Any]] = None
    language_detected: Optional[str] = None
    processing_steps: Optional[List[str]] = None

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    files: List[Dict[str, Any]] = []
    conversation_ids: List[str] = []

class ProjectRequest(BaseModel):
    name: str
    description: str

class CodeFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    content: str
    language: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CodeFileRequest(BaseModel):
    project_id: str
    name: str
    content: str
    language: str

class APIKey(BaseModel):
    service: str  # 'perplexity' or 'anthropic'
    key: str
    is_active: bool = True

class GitHubPushRequest(BaseModel):
    repository: str  # owner/repo format
    branch: str = "main"
    files: List[Dict[str, str]]  # [{"path": "file.py", "content": "code"}]
    commit_message: str = "Add generated code"
    github_token: Optional[str] = None

class StreamingCodeRequest(BaseModel):
    prompt: str
    language: str = "python"
    model: str = "claude"
    stream_updates: bool = True

class CodeGenerationProgress(BaseModel):
    stage: str  # "analyzing", "generating", "formatting", "complete"
    progress: float  # 0.0 to 1.0
    current_code: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Chat endpoints
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Intelligenter Chat-Endpoint mit automatischer Model-Auswahl
    Nutzt Claude 3.5 Sonnet, Perplexity Deep Research und GPT-5
    """
    try:
        # Load API keys from local storage first (in case they were added via UI)
        await load_api_keys_from_local_storage()
        
        # Get API keys from environment (now includes both stored and env vars)
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')
        perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
        
        # Validate API keys with proper format checking
        configured_keys = []
        if anthropic_key and anthropic_key.startswith('sk-ant-'):
            configured_keys.append('anthropic')
        if perplexity_key and perplexity_key.startswith('pplx-'):
            configured_keys.append('perplexity')
        if openai_key and openai_key.startswith('sk-'):
            configured_keys.append('openai')
            
        # Check if at least one API key is properly configured
        if not configured_keys:
            logging.warning("🔑 Chat request blocked - No valid API keys configured")
            raise HTTPException(
                status_code=400, 
                detail="API-Schlüssel erforderlich: Mindestens ein gültiger API-Schlüssel (Anthropic, OpenAI oder Perplexity) muss konfiguriert sein um die Chat-Funktion zu nutzen."
            )
        
        # Erstelle AI-Orchestrator Instanz und initialize clients (even if already set)
        orchestrator = ai_orchestrator
        if anthropic_key:
            orchestrator.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_key)
        if openai_key:
            orchestrator.openai_client = AsyncOpenAI(api_key=openai_key)
        if perplexity_key:
            orchestrator.perplexity_client = AsyncOpenAI(
                api_key=perplexity_key,
                base_url="https://api.perplexity.ai"
            )
        
        # Konvertiere Konversation für Kontext
        context = []
        if hasattr(request, 'conversation_history') and request.conversation_history:
            context = [
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                for msg in request.conversation_history[-6:]  # Letzte 6 Nachrichten
            ]
        
        # Check for FULL AUTOMATION trigger
        automation_triggers = [
            "vollautomatisch", "full automation", "end-to-end", "automated chain",
            "automatic completion", "agents solve completely", "agenten lösen vollständig",
            "automatisch abarbeiten", "selbstständig lösen", "komplette automatisierung"
        ]
        
        use_full_automation = any(trigger in request.message.lower() for trigger in automation_triggers)
        
        if use_full_automation:
            logging.info("🚀 FULL AUTOMATION MODE triggered")
            try:
                # Initialize orchestrator if needed
                if not hasattr(orchestrator, 'execute_fully_automated_chain'):
                    logging.warning("Orchestrator doesn't support full automation - falling back to regular processing")
                    use_full_automation = False
                else:
                    # Execute fully automated chain
                    automation_result = await orchestrator.execute_fully_automated_chain(
                        initial_request=request.message,
                        context={
                            "conversation_id": request.conversation_id,
                            "user_message": request.message,
                            "configured_keys": configured_keys
                        }
                    )
                    
                    if automation_result.get("success", False):
                        final_result = automation_result["final_result"]
                        
                        # Create response with automation metadata
                        return ChatResponse(
                            message=ChatMessage(
                                role="assistant",
                                content=final_result,
                                model="XIONIMUS_AI_AUTOMATION",
                                timestamp=datetime.now(timezone.utc)
                            ),
                            conversation_id=request.conversation_id,
                            agent_used="XIONIMUS AI Orchestrator - FULL AUTOMATION",
                            model_used="automated_agent_chain",
                            metadata={
                                **automation_result.get("metadata", {}),
                                "automation_mode": "full_end_to_end",
                                "no_manual_intervention": True,
                                "agents_coordinated": automation_result.get("automation_chain", {}).get("active_agents", []),
                                "total_iterations": automation_result.get("metadata", {}).get("total_iterations", 0)
                            }
                        )
                    else:
                        logging.warning(f"Full automation failed: {automation_result.get('error', 'Unknown error')}")
                        use_full_automation = False  # Fall back to regular processing
            except Exception as automation_error:
                logging.error(f"Full automation error: {str(automation_error)}")
                use_full_automation = False  # Fall back to regular processing
        
        # First, try to process with AgentManager if use_agent is enabled
        result = None
        use_xionimus = False
        
        if request.use_agent:
            try:
                agent_context = {
                    'conversation_history': context,
                    'conversation_id': request.conversation_id
                }
                
                # Analyze complexity with XIONIMUS AI (REMOVED)
                # complexity_level, complexity_score = await xionimus_orchestrator.analyze_request_complexity(
                #     request.message, agent_context
                # )
                
                # Fallback for removed complexity analysis
                complexity_level = type('ComplexityLevel', (), {'value': 'medium'})()
                complexity_score = 5.0
                
                # Use XIONIMUS AI for complex or advanced tasks
                if complexity_level.value in ['complex', 'xionimus_ai'] and complexity_score > 7.0:
                    use_xionimus = True
                    logging.info(f"🚀 Using XIONIMUS AI for complex request (score: {complexity_score:.2f})")
                    
                    # Process with XIONIMUS AI (REMOVED)
                    # swarm_task = await xionimus_orchestrator.assemble_agent_swarm(
                    #     request.message, complexity_level, complexity_score, agent_context
                    # )
                    
                    # xionimus_result = await xionimus_orchestrator.coordinate_xionimus_workflows(
                    #     swarm_task, agent_context
                    # )
                    
                    # Fallback result for removed XIONIMUS orchestrator
                    xionimus_result = {
                        'content': f"Anfrage verarbeitet (XIONIMUS Orchestrator temporär deaktiviert): {request.message}",
                        'services_used': ['fallback']
                    }
                    
                    # Format XIONIMUS result
                    primary_result = xionimus_result.get("result", {})
                    if isinstance(primary_result, dict) and "primary_result" in primary_result:
                        content = primary_result["primary_result"].get("content", "No content generated")
                    else:
                        content = str(primary_result.get("content", primary_result))
                    
                    result = {
                        'response': content,
                        'metadata': {
                            'agent_used': 'XIONIMUS AI Orchestrator',
                            'complexity_level': complexity_level.value,
                            'complexity_score': complexity_score,
                            'swarm_coordination': xionimus_result.get("swarm_coordination", {}),
                            'xionimus_metadata': xionimus_result.get("xionimus_metadata", {}),
                            'processing_steps': [
                                f"XIONIMUS Analysis: {complexity_level.value} complexity",
                                f"Agent Swarm: {len(swarm_task.assigned_agents)} primary agents",
                                f"Collaboration: {swarm_task.collaboration_type}",
                                "Collective Intelligence Applied"
                            ],
# REMOVED:                             'services_used': ['xionimus_orchestrator']
                        }
                    }
                
                else:
                    # Use standard agent processing for simpler tasks
                    agent_result = await agent_manager.process_request(request.message, agent_context)
                    
                    # If agent processing is required and successful, use agent result
                    if agent_result.get('requires_agent'):
                        # Format agent response for the chat
                        if 'result' in agent_result and agent_result['result']:
                            agent_response = await _format_agent_response(
                                agent_result.get('agent_used', 'Unknown Agent'),
                                agent_result['result'],
                                agent_result.get('language_info', {}).get('language', 'en')
                            )
                            result = {
                                'response': agent_response,
                                'metadata': {
                                    'agent_used': agent_result.get('agent_used'),
                                    'task_id': agent_result.get('task_id'),
                                    'language_detected': agent_result.get('language_info', {}).get('language'),
                                    'processing_steps': agent_result.get('steps', []),
                                    'services_used': ['specialized_agent'],
                                    'complexity_analysis': {
                                        'level': complexity_level.value,
                                        'score': round(complexity_score, 2)
                                    }
                                }
                            }
                        elif 'error' in agent_result:
                            # Agent failed, fall back to AI Orchestrator
                            logging.warning(f"Agent execution failed: {agent_result['error']}")
                            result = await orchestrator.process_request(request.message, context)
                            result['metadata']['agent_fallback'] = True
                            result['metadata']['agent_error'] = agent_result['error']
                    else:
                        # Agent decided not to handle this request, use AI Orchestrator
                        result = await orchestrator.process_request(request.message, context)
                        result['metadata']['agent_recommendation'] = agent_result.get('agent_recommendation', 'No specialized agent needed')
                        result['metadata']['complexity_analysis'] = {
                            'level': complexity_level.value,
                            'score': round(complexity_score, 2)
                        }
                    
            except Exception as e:
                logging.error(f"AgentManager/XIONIMUS error: {e}")
                # Fall back to AI Orchestrator on any agent error
                result = await orchestrator.process_request(request.message, context)
                result['metadata']['agent_fallback'] = True
                result['metadata']['agent_error'] = str(e)
        
        # If no agent processing or agent disabled, use AI Orchestrator
        if not result:
            result = await orchestrator.process_request(request.message, context)
        
        # Create response in expected format
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Save user message to chat history
        user_message = ChatMessage(
            role="user",
            content=request.message
        )
        await db.chat_sessions.insert_one({
            **user_message.dict(),
            "conversation_id": conversation_id
        })
        
        # Create assistant message
        assistant_message = ChatMessage(
            role="assistant",
            content=result['response'],
            model="xionimus-ai",  # Einheitlicher Model-Name für User
            tokens_used=result.get('metadata', {}).get('tokens_used')
        )
        
        # Save assistant message with analysis metadata to chat history
        assistant_message_data = {
            **assistant_message.dict(),
            "conversation_id": conversation_id,
            "agent_used": result.get('metadata', {}).get('agent_used'),
            "sources": result.get('metadata', {}).get('sources', []),
            "language_detected": result.get('metadata', {}).get('language_detected'),
            "processing_steps": result.get('metadata', {}).get('processing_steps', []),
            "agent_result": result.get('metadata', {})
        }
        await db.chat_sessions.insert_one(assistant_message_data)
        
        logging.info(f"💬 Saved chat messages to conversation {conversation_id}")
        
        return ChatResponse(
            message=assistant_message,
            conversation_id=conversation_id,
            sources=result.get('metadata', {}).get('sources', []),
            agent_used=result.get('metadata', {}).get('agent_used'),
            agent_result=result.get('metadata', {}),
            language_detected=result.get('metadata', {}).get('language_detected'),
            processing_steps=result.get('metadata', {}).get('processing_steps', [])
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions unchanged
    except anthropic.APIError as e:
        logging.error(f"Anthropic API error: {e}")
        raise HTTPException(status_code=503, detail=f"Claude API error: {str(e)}")
    except openai.APIError as e:
        logging.error(f"OpenAI/Perplexity API error: {e}")
        raise HTTPException(status_code=503, detail=f"AI API error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    cursor = await db.chat_sessions.find({"conversation_id": conversation_id})
    messages = cursor.sort("timestamp", 1).to_list(100)
    return [ChatMessage(**msg) for msg in messages]

# Project Management endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(request: ProjectRequest):
    project = Project(name=request.name, description=request.description)
    await db.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    cursor = await db.projects.find()
    projects = cursor.sort("updated_at", -1).to_list(100)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, request: ProjectRequest):
    update_data = request.dict()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.projects.update_one(
        {"id": project_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Also delete associated files
    await db.code_files.delete_many({"project_id": project_id})
    return {"message": "Project deleted successfully"}

# Code File Management endpoints
@api_router.post("/files")
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = Form(...)
):
    """Upload a file to a project"""
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Determine language from file extension
        language = "text"
        if file.filename:
            if file.filename.endswith('.py'):
                language = "python"
            elif file.filename.endswith('.js'):
                language = "javascript"
            elif file.filename.endswith('.html'):
                language = "html"
            elif file.filename.endswith('.css'):
                language = "css"
        
        # Create code file
        code_file = CodeFile(
            project_id=project_id,
            name=file.filename or "uploaded_file",
            content=content_str,
            language=language
        )
        
        await db.code_files.insert_one(code_file.dict())
        
        # Add file to project
        await db.projects.update_one(
            {"id": project_id},
            {"$push": {"files": {"id": code_file.id, "name": code_file.name, "language": code_file.language}}}
        )
        
        return {
            "id": code_file.id,
            "filename": code_file.name,
            "project_id": project_id,
            "language": code_file.language,
            "size": len(content),
            "uploaded_at": code_file.created_at.isoformat()
        }
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text-based")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.post("/files/json", response_model=CodeFile)
async def create_code_file(request: CodeFileRequest):
    """Create a code file from JSON data"""
    code_file = CodeFile(**request.dict())
    await db.code_files.insert_one(code_file.dict())
    
    # Add file to project
    await db.projects.update_one(
        {"id": request.project_id},
        {"$push": {"files": {"id": code_file.id, "name": code_file.name, "language": code_file.language}}}
    )
    
    return code_file

@api_router.get("/files/{project_id}")
async def get_project_files(project_id: str):
    cursor = await db.code_files.find({"project_id": project_id})
    files = cursor.sort("updated_at", -1).to_list(100)
    return [CodeFile(**file) for file in files]

@api_router.get("/files/content/{file_id}")
async def get_file_content(file_id: str):
    file = await db.code_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return CodeFile(**file)

@api_router.put("/files/{file_id}")
async def update_file_content(file_id: str, request: CodeFileRequest):
    update_data = request.dict()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.code_files.update_one(
        {"id": file_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    
    updated_file = await db.code_files.find_one({"id": file_id})
    return CodeFile(**updated_file)

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    file = await db.code_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Remove from project
    await db.projects.update_one(
        {"id": file["project_id"]},
        {"$pull": {"files": {"id": file_id}}}
    )
    
    await db.code_files.delete_one({"id": file_id})
    return {"message": "File deleted successfully"}

# Local Storage-based API Key Management with comprehensive logging
@api_router.post("/api-keys")
async def save_api_key(api_key: APIKey):
    """Save API key with Local Storage persistence and comprehensive logging"""
    try:
        logging.info(f"🔄 Starting API key save for service: {api_key.service}")
        
        # Validate service
        valid_services = ["perplexity", "anthropic", "openai"]
        if api_key.service not in valid_services:
            logging.error(f"❌ Invalid service: {api_key.service}")
            raise HTTPException(status_code=400, detail=f"Invalid service. Must be one of: {valid_services}")
        
        # Validate key format
        key_validations = {
            "perplexity": lambda k: k.startswith("pplx-") and len(k) > 10,
            "anthropic": lambda k: k.startswith("sk-ant-") and len(k) > 15,
            "openai": lambda k: k.startswith("sk-") and len(k) > 10
        }
        
        if not key_validations[api_key.service](api_key.key):
            logging.error(f"❌ Invalid key format for {api_key.service}")
            raise HTTPException(status_code=400, detail=f"Invalid API key format for {api_key.service}")
        
        # Local Storage operation with detailed logging
        api_key_doc = {
            "service": api_key.service,
            "key": api_key.key,
            "is_active": getattr(api_key, 'is_active', True),
            "updated_at": datetime.now(),
            "key_preview": f"...{api_key.key[-4:]}" if len(api_key.key) > 4 else "***"
        }
        
        logging.info(f"🔄 Local Storage upsert operation for {api_key.service}")
        
        # Use upsert to update existing or create new
        result = await db.api_keys.update_one(
            {"service": api_key.service},
            {
                "$set": api_key_doc,
                "$setOnInsert": {"created_at": datetime.now()}
            },
            upsert=True
        )
        
        logging.info(f"✅ Local Storage operation completed - Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_id}")
        
        # Store in environment for immediate use
        env_var = f"{api_key.service.upper()}_API_KEY"
        os.environ[env_var] = api_key.key
        logging.info(f"✅ Environment variable {env_var} set")
        
        # Persist to .env file as backup
        try:
            env_file_path = os.path.join(os.path.dirname(__file__), '.env')
            logging.info(f"🔄 Updating .env file: {env_file_path}")
            
            env_lines = []
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    env_lines = f.readlines()
            
            key_line = f"{env_var}={api_key.key}\n"
            key_found = False
            
            for i, line in enumerate(env_lines):
                if line.startswith(f"{env_var}=") or line.startswith(f"# {env_var}="):
                    env_lines[i] = key_line
                    key_found = True
                    break
            
            if not key_found:
                env_lines.append(key_line)
            
            with open(env_file_path, 'w') as f:
                f.writelines(env_lines)
                
            logging.info(f"✅ .env file updated successfully")
            
        except Exception as env_error:
            logging.warning(f"⚠️ .env file update failed (non-critical): {str(env_error)}")
        
        # Reset clients to use new keys
        global perplexity_client, claude_client
        if api_key.service == "perplexity":
            perplexity_client = None
            logging.info("🔄 Perplexity client reset")
        elif api_key.service == "anthropic":
            claude_client = None
            logging.info("🔄 Claude client reset")
        elif api_key.service == "openai":
            logging.info("🔄 OpenAI client will be reset by AIOrchestrator")
        
        # Verify the save by reading back from Local Storage
        verification = await db.api_keys.find_one({"service": api_key.service})
        if verification:
            logging.info(f"✅ Local Storage verification successful for {api_key.service}")
            
            return {
                "message": f"{api_key.service} API key saved successfully",
                "service": api_key.service,
                "status": "configured",
                "local_storage_doc_id": str(verification["_id"]),
                "created_at": verification.get("created_at"),
                "updated_at": verification.get("updated_at"),
                "key_preview": verification.get("key_preview")
            }
        else:
            logging.error(f"❌ Local Storage verification failed for {api_key.service}")
            raise HTTPException(status_code=500, detail="API key saved but verification failed")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Critical error saving API key for {api_key.service}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save API key: {str(e)}")

@api_router.get("/api-keys/status")
async def get_api_keys_status():
    """Get API keys status from Local Storage with detailed information and logging"""
    try:
        logging.info("🔄 Starting API keys status check")
        
        # Get all API keys from Local Storage
        cursor = await db.api_keys.find({})
        storage_keys = cursor.to_list(length=None)
        logging.info(f"📊 Found {len(storage_keys)} API keys in Local Storage")
        
        # Initialize status structure
        services = ["perplexity", "anthropic", "openai"]
        status = {}
        details = {}
        local_storage_info = {}
        
        # Process Local Storage results
        for key_doc in storage_keys:
            service = key_doc.get("service")
            if service in services:
                # Check if key exists in environment (runtime availability)
                env_var = f"{service.upper()}_API_KEY"
                env_available = bool(os.environ.get(env_var))
                
                status[service] = env_available and key_doc.get("is_active", True)
                details[service] = {
                    "configured": True,
                    "local_storage_stored": True,
                    "environment_available": env_available,
                    "preview": key_doc.get("key_preview", "****"),
                    "created_at": key_doc.get("created_at"),
                    "updated_at": key_doc.get("updated_at"),
                    "is_active": key_doc.get("is_active", True)
                }
                local_storage_info[service] = {
                    "doc_id": str(key_doc["_id"]),
                    "collection": "api_keys"
                }
                
                logging.info(f"✅ {service}: Local Storage=✓, Environment={env_available}")
        
        # Handle services not in Local Storage
        for service in services:
            if service not in status:
                env_var = f"{service.upper()}_API_KEY"
                env_available = bool(os.environ.get(env_var))
                
                status[service] = env_available
                details[service] = {
                    "configured": env_available,
                    "local_storage_stored": False,
                    "environment_available": env_available,
                    "preview": None,
                    "created_at": None,
                    "updated_at": None,
                    "is_active": True
                }
                local_storage_info[service] = None
                
                if env_available:
                    logging.warning(f"⚠️ {service}: Environment=✓, but not in Local Storage")
                else:
                    logging.info(f"ℹ️ {service}: Not configured")
        
        response_data = {
            "status": status,
            "details": details,
            "local_storage_info": local_storage_info,
            "total_configured": sum(1 for configured in status.values() if configured),
            "total_services": len(services),
            "mongodb_connection": "connected",  # Report as mongodb for compatibility
            "timestamp": datetime.now().isoformat()
        }
        
        logging.info(f"✅ API keys status check completed - {response_data['total_configured']}/{response_data['total_services']} configured")
        
        return response_data
        
    except Exception as e:
        logging.error(f"❌ Error getting API keys status: {str(e)}")
        
        # Fallback to environment-only check
        try:
            services = ["perplexity", "anthropic", "openai"]
            fallback_status = {}
            fallback_details = {}
            
            for service in services:
                env_var = f"{service.upper()}_API_KEY"
                env_available = bool(os.environ.get(env_var))
                
                fallback_status[service] = env_available
                fallback_details[service] = {
                    "configured": env_available,
                    "local_storage_stored": False,
                    "environment_available": env_available,
                    "preview": None,
                    "error": "Local Storage unavailable"
                }
            
            return {
                "status": fallback_status,
                "details": fallback_details,
                "mongodb_connection": "error",  # Report as mongodb for compatibility
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as fallback_error:
            logging.error(f"❌ Critical error in fallback status check: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=f"Failed to get API keys status: {str(e)}")

@api_router.delete("/api-keys/{service}")
async def delete_api_key(service: str):
    """Delete API key from Local Storage and environment with comprehensive logging"""
    try:
        logging.info(f"🔄 Starting API key deletion for service: {service}")
        
        valid_services = ["perplexity", "anthropic", "openai"]
        if service not in valid_services:
            logging.error(f"❌ Invalid service for deletion: {service}")
            raise HTTPException(status_code=400, detail=f"Invalid service. Must be one of: {valid_services}")
        
        # Delete from Local Storage
        result = await db.api_keys.delete_one({"service": service})
        logging.info(f"📊 Local Storage delete result - Deleted count: {result.deleted_count}")
        
        if result.deleted_count == 0:
            logging.warning(f"⚠️ No Local Storage document found for service: {service}")
        else:
            logging.info(f"✅ Local Storage document deleted for {service}")
        
        # Remove from environment
        env_var = f"{service.upper()}_API_KEY"
        if env_var in os.environ:
            del os.environ[env_var]
            logging.info(f"✅ Environment variable {env_var} removed")
        else:
            logging.info(f"ℹ️ Environment variable {env_var} was not set")
        
        # Remove from .env file
        try:
            env_file_path = os.path.join(os.path.dirname(__file__), '.env')
            
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    env_lines = f.readlines()
                
                original_count = len(env_lines)
                filtered_lines = [line for line in env_lines if not line.startswith(f"{env_var}=")]
                
                if len(filtered_lines) < original_count:
                    with open(env_file_path, 'w') as f:
                        f.writelines(filtered_lines)
                    logging.info(f"✅ .env file updated - removed {env_var}")
                else:
                    logging.info(f"ℹ️ {env_var} was not in .env file")
            else:
                logging.info("ℹ️ .env file does not exist")
                
        except Exception as env_error:
            logging.warning(f"⚠️ .env file update failed (non-critical): {str(env_error)}")
        
        # Reset clients
        global perplexity_client, claude_client
        if service == "perplexity":
            perplexity_client = None
            logging.info("🔄 Perplexity client reset")
        elif service == "anthropic":
            claude_client = None
            logging.info("🔄 Claude client reset")
        
        logging.info(f"✅ API key deletion completed for {service}")
        
        return {
            "message": f"{service} API key deleted successfully",
            "service": service,
            "status": "removed",
            "local_storage_deleted": result.deleted_count > 0,
            "environment_cleared": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error deleting API key for {service}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete API key: {str(e)}")

@api_router.get("/api-keys/debug")
async def debug_api_keys():
    """Debug endpoint for comprehensive API key system analysis"""
    try:
        logging.info("🔧 Starting comprehensive API key debug analysis")
        
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "local_storage_analysis": {},
            "environment_analysis": {},
            "file_system_analysis": {},
            "system_health": {}
        }
        
        # Local Storage Analysis
        try:
            cursor = await db.api_keys.find({})
            storage_keys = cursor.to_list(length=None)
            debug_info["local_storage_analysis"] = {
                "connection_status": "connected",
                "collection_name": "api_keys",
                "document_count": len(storage_keys),
                "documents": [
                    {
                        "service": doc.get("service"),
                        "is_active": doc.get("is_active"),
                        "created_at": doc.get("created_at"),
                        "updated_at": doc.get("updated_at"),
                        "key_preview": doc.get("key_preview"),
                        "doc_id": str(doc["_id"])
                    } for doc in storage_keys
                ]
            }
            logging.info(f"✅ Local Storage analysis: {len(storage_keys)} documents found")
        except Exception as mongo_error:
            debug_info["local_storage_analysis"] = {
                "connection_status": "error",
                "error": str(mongo_error)
            }
            logging.error(f"❌ Local Storage analysis failed: {str(mongo_error)}")
        
        # Environment Analysis
        services = ["perplexity", "anthropic", "openai"]
        env_status = {}
        
        for service in services:
            env_var = f"{service.upper()}_API_KEY"
            env_value = os.environ.get(env_var)
            
            env_status[service] = {
                "variable_name": env_var,
                "is_set": bool(env_value),
                "value_preview": f"...{env_value[-4:]}" if env_value and len(env_value) > 4 else None,
                "value_length": len(env_value) if env_value else 0
            }
        
        debug_info["environment_analysis"] = env_status
        logging.info(f"✅ Environment analysis completed")
        
        # File System Analysis
        try:
            env_file_path = os.path.join(os.path.dirname(__file__), '.env')
            
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    env_content = f.read()
                
                api_key_lines = []
                for line in env_content.split('\n'):
                    if any(f"{service.upper()}_API_KEY" in line for service in services):
                        # Mask the actual key value
                        if '=' in line and not line.strip().startswith('#'):
                            key_name, key_value = line.split('=', 1)
                            masked_value = f"...{key_value[-4:]}" if len(key_value) > 4 else "***"
                            api_key_lines.append(f"{key_name}={masked_value}")
                        else:
                            api_key_lines.append(line)
                
                debug_info["file_system_analysis"] = {
                    "env_file_exists": True,
                    "env_file_path": env_file_path,
                    "api_key_lines": api_key_lines,
                    "total_lines": len(env_content.split('\n'))
                }
            else:
                debug_info["file_system_analysis"] = {
                    "env_file_exists": False,
                    "env_file_path": env_file_path
                }
                
            logging.info("✅ File system analysis completed")
            
        except Exception as fs_error:
            debug_info["file_system_analysis"] = {
                "error": str(fs_error)
            }
            logging.error(f"❌ File system analysis failed: {str(fs_error)}")
        
        # System Health
        configured_count = sum(1 for service in services if os.environ.get(f"{service.upper()}_API_KEY"))
        
        debug_info["system_health"] = {
            "total_services": len(services),
            "configured_services": configured_count,
            "configuration_percentage": round((configured_count / len(services)) * 100, 1),
            "all_systems_operational": configured_count > 0,
            "recommendations": []
        }
        
        # Add recommendations
        if configured_count == 0:
            debug_info["system_health"]["recommendations"].append("No API keys configured. Please add at least one API key.")
        elif configured_count < len(services):
            debug_info["system_health"]["recommendations"].append(f"Only {configured_count}/{len(services)} services configured. Consider adding more for full functionality.")
        else:
            debug_info["system_health"]["recommendations"].append("All API key services configured. System ready for full operation.")
        
        logging.info(f"✅ Debug analysis completed - {configured_count}/{len(services)} services configured")
        
        return debug_info
        
    except Exception as e:
        logging.error(f"❌ Critical error in debug analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug analysis failed: {str(e)}")

# Agent management endpoints
@api_router.get("/agents")
async def get_available_agents():
    """Get information about all available agents and their capabilities"""
    try:
        agents_info = agent_manager.get_available_agents()
        
        # Add additional runtime information
        for agent_info in agents_info:
            agent_name = agent_info["name"]
            agent = agent_manager.agents.get(agent_name)
            if agent:
                agent_info.update({
                    "ai_model": getattr(agent, 'ai_model', 'Unknown'),
                    "status": "available",
                    "capabilities": agent.get_capabilities_description() if hasattr(agent, 'get_capabilities_description') else []
                })
        
        return {
            "agents": agents_info,
            "total_agents": len(agents_info),
            "agent_manager_status": "active"
        }
    except Exception as e:
        logging.error(f"❌ Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@api_router.get("/agents/{agent_name}/capabilities")
async def get_agent_capabilities(agent_name: str):
    """Get detailed capabilities of a specific agent"""
    try:
        agent = agent_manager.agents.get(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        return {
            "name": agent.name,
            "description": agent.description,
            "ai_model": getattr(agent, 'ai_model', 'Unknown'),
            "capabilities": agent.get_capabilities_description() if hasattr(agent, 'get_capabilities_description') else [],
            "status": "available"
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error getting agent capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent capabilities: {str(e)}")

@api_router.get("/agents/suggest")
async def suggest_agent_for_query(query: str = Query(None, description="Query to suggest agent for")):
    """Suggest the best agent for a given query"""
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
            
        context = {"query": query}
        suggested_agent = agent_manager._select_best_agent(query, context)
        
        # Enhanced with XIONIMUS AI complexity analysis
# REMOVED:         complexity_level, complexity_score = await xionimus_orchestrator.analyze_request_complexity(query, context)
        
        if suggested_agent:
            return {
                "suggested_agent": {
                    "name": suggested_agent.name,
                    "description": suggested_agent.description,
                    "ai_model": getattr(suggested_agent, 'ai_model', 'Unknown'),
                    "confidence": "high" if complexity_score > 6.0 else "medium"
                },
                "requires_agent_processing": True,
                "xionimus_analysis": {
                    "complexity_level": complexity_level.value,
                    "complexity_score": round(complexity_score, 2),
                    "xionimus_ai_properties": complexity_level.value in ["complex", "xionimus_ai"]
                }
            }
        else:
            return {
                "suggested_agent": None,
                "requires_agent_processing": False,
                "message": "This query can be handled by the general AI orchestrator",
                "xionimus_analysis": {
                    "complexity_level": complexity_level.value,
                    "complexity_score": round(complexity_score, 2)
                }
            }
    except Exception as e:
        logging.error(f"❌ Error suggesting agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest agent: {str(e)}")

@api_router.get("/xionimus/status")
async def get_xionimus_status():
    """Get XIONIMUS AI system status and adaptive properties"""
    try:
# REMOVED:         system_status = xionimus_orchestrator.get_system_status()
        return {
            "xionimus_ai_status": "active",
            "orchestrator_version": "1.0.0",
            "adaptive_intelligence": system_status,
            "capabilities": {
                "adaptive_routing": True,
                "cross_agent_learning": True,
                "pattern_discovery": True,
                "collective_intelligence": True,
                "dynamic_sub_agents": True
            }
        }
    except Exception as e:
        logging.error(f"❌ Error getting XIONIMUS status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get XIONIMUS status: {str(e)}")

@api_router.post("/xionimus/process")
async def process_with_xionimus_ai(request: ChatRequest):
    """Process request using XIONIMUS AI multi-agent orchestration"""
    try:
        # Load API keys from local storage first
        await load_api_keys_from_local_storage()
        
        # Analyze request complexity
# REMOVED:         complexity_level, complexity_score = await xionimus_orchestrator.analyze_request_complexity(
            request.message, {"conversation_history": request.conversation_history}
        )
        
        # Assemble agent swarm based on complexity
# REMOVED:         swarm_task = await xionimus_orchestrator.assemble_agent_swarm(
            request.message, complexity_level, complexity_score,
            {"conversation_history": request.conversation_history}
        )
        
        # Coordinate XIONIMUS workflows
# REMOVED:         result = await xionimus_orchestrator.coordinate_xionimus_workflows(
            swarm_task, {"conversation_history": request.conversation_history}
        )
        
        # Format response
        content = result.get("result", {}).get("primary_result", {}).get("content", "No result generated")
        if isinstance(content, dict):
            content = content.get("content", str(content))
        
        # Create response message
        response_message = ChatMessage(
            role="assistant",
            content=str(content),
            model="xionimus-ai-orchestrator",
            tokens_used=None  # TODO: Calculate token usage across agents
        )
        
        return ChatResponse(
            message=response_message,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            sources=[],
            agent_used="XIONIMUS AI Orchestrator",
            agent_result=result.get("swarm_coordination", {}),
            language_detected=None,
            processing_steps=[
                f"Complexity Analysis: {complexity_level.value} (score: {complexity_score:.1f})",
                f"Agent Swarm: {len(swarm_task.assigned_agents)} primary + {len(swarm_task.sub_agents)} sub-agents",
                f"Collaboration: {swarm_task.collaboration_type}",
                f"Patterns: {len(swarm_task.xionimus_ai_patterns)} adaptive patterns"
            ]
        )
        
    except Exception as e:
        logging.error(f"❌ Error processing with XIONIMUS AI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"XIONIMUS AI processing failed: {str(e)}")

# Code Generation endpoint
@api_router.post("/generate-code")
async def generate_code(request: Dict[str, Any]):
    """Generate code using AI - requires valid API keys"""
    
    # Load API keys from local storage first
    await load_api_keys_from_local_storage()
    
    # Get API keys from environment
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
    
    # Validate API keys with proper format checking
    configured_keys = []
    if anthropic_key and anthropic_key.startswith('sk-ant-'):
        configured_keys.append('anthropic')
    if perplexity_key and perplexity_key.startswith('pplx-'):
        configured_keys.append('perplexity')
    if openai_key and openai_key.startswith('sk-'):
        configured_keys.append('openai')
        
    # Check if at least one API key is properly configured
    if not configured_keys:
        logging.warning("🔑 Code generation request blocked - No valid API keys configured")
        raise HTTPException(
            status_code=400, 
            detail="API-Schlüssel erforderlich: Mindestens ein gültiger API-Schlüssel (Anthropic, OpenAI oder Perplexity) muss konfiguriert sein um Code-Generierung zu nutzen."
        )
    
    prompt = request.get("prompt")
    language = request.get("language", "python")
    model = request.get("model", "claude")
    
    enhanced_prompt = f"""
    Generate {language} code for the following requirement:
    {prompt}
    
    Please provide clean, well-commented code with proper error handling.
    Only return the code, no explanations unless specifically requested.
    """
    
    chat_request = ChatRequest(
        message=enhanced_prompt,
        model=model
    )
    
    response = await chat_with_ai(chat_request)
    return {
        "code": response.message.content,
        "language": language,
        "tokens_used": response.message.tokens_used
    }

# Agent Management endpoints
@api_router.get("/agents")
async def get_available_agents():
    """Get list of all available agents"""
    return agent_manager.get_available_agents()

@api_router.get("/agents/task/{task_id}")
async def get_agent_task_status(task_id: str):
    """Get status of a specific agent task"""
    status = agent_manager.get_agent_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@api_router.post("/agents/task/{task_id}/cancel")
async def cancel_agent_task(task_id: str):
    """Cancel an active agent task"""
    success = agent_manager.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task cancelled successfully"}

@api_router.post("/agents/analyze")
async def analyze_request(request: Dict[str, Any]):
    """Analyze a request to determine which agent should handle it using enhanced context recognition"""
    message = request.get("message", "")
    context = request.get("context", {})
    
    # Get enhanced context analysis
    try:
        context_analysis = agent_manager.context_analyzer.analyze_content(message, context)
        enhanced_recommendations = agent_manager.context_analyzer.get_agent_recommendations(context_analysis)
        
        # Also get legacy agent scores for comparison
        legacy_scores = {}
        for agent_name, agent in agent_manager.agents.items():
            confidence = agent.can_handle_task(message, context)
            if confidence > 0:
                legacy_scores[agent_name] = confidence
    except Exception as e:
        # Fallback to legacy method if enhanced analysis fails
        logging.error(f"Enhanced analysis failed: {e}")
        context_analysis = None
        enhanced_recommendations = {}
        legacy_scores = {}
        for agent_name, agent in agent_manager.agents.items():
            confidence = agent.can_handle_task(message, context)
            if confidence > 0:
                legacy_scores[agent_name] = confidence
    
    # Determine best recommendations (prefer enhanced if available)
    if enhanced_recommendations:
        best_recommendations = enhanced_recommendations
        analysis_method = "enhanced"
    else:
        best_recommendations = legacy_scores
        analysis_method = "legacy"
    
    # Detect language
    language_info = agent_manager.language_detector.detect_language(message)
    
    response = {
        "message": message,
        "language_detected": language_info,
        "agent_recommendations": best_recommendations,
        "best_agent": max(best_recommendations, key=best_recommendations.get) if best_recommendations else None,
        "requires_agent": agent_manager._requires_agent_processing(message, context),
        "analysis_method": analysis_method
    }
    
    # Add enhanced analysis details if available
    if context_analysis:
        response["enhanced_analysis"] = {
            "primary_domain": context_analysis.primary_domain.value,
            "confidence_score": context_analysis.confidence_score,
            "content_complexity": context_analysis.content_complexity,
            "context_hints": context_analysis.context_hints,
            "requires_specialization": context_analysis.requires_specialization
        }
    
    # Add comparison for debugging
    if legacy_scores and enhanced_recommendations:
        response["comparison"] = {
            "legacy_scores": legacy_scores,
            "enhanced_scores": enhanced_recommendations
        }
    
    return response

# OpenAI Connection Test endpoint
@api_router.post("/test-openai-connection")
async def test_openai_connection(request: Dict[str, Any]):
    """Test OpenAI API connection with provided API key"""
    try:
        api_key = request.get("api_key")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        if not api_key.startswith("sk-"):
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key format")
        
        # Create OpenAI client for testing
        test_client = AsyncOpenAI(api_key=api_key)
        
        # Test with a simple models request
        try:
            models = await test_client.models.list()
            model_count = len(models.data) if models.data else 0
            
            # Get some example model names
            example_models = [model.id for model in models.data[:3]] if models.data else []
            
            return {
                "success": True,
                "message": "OpenAI connection successful",
                "details": {
                    "available_models": model_count,
                    "example_models": example_models,
                    "api_key_preview": f"...{api_key[-8:] if len(api_key) > 8 else '***'}"
                }
            }
            
        except openai.AuthenticationError:
            raise HTTPException(status_code=401, detail="Invalid API key - Authentication failed")
        except openai.RateLimitError:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        except openai.APIError as e:
            raise HTTPException(status_code=503, detail=f"OpenAI API error: {str(e)}")
        finally:
            # Clean up client
            await test_client.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"OpenAI connection test error: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

# GitHub Repository Analysis endpoint
@api_router.post("/analyze-repo")
async def analyze_repository(request: Dict[str, Any]):
    """Analyze GitHub repository using AI agents"""
    
    # Load API keys from local storage first
    await load_api_keys_from_local_storage()
    
    # Get API keys from environment
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
    
    # Check if at least one API key is properly configured
    if not anthropic_key and not perplexity_key:
        logging.warning("🔑 Repository analysis request blocked - No valid API keys configured")
        raise HTTPException(
            status_code=400, 
            detail="API keys required: At least one valid API key (Anthropic or Perplexity) must be configured to analyze repositories."
        )
    
    repo_url = request.get("url")
    model = request.get("model", "claude")
    conversation_id = request.get("conversation_id", str(uuid.uuid4()))
    
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")
    
    enhanced_prompt = f"""
    Analyze the GitHub repository at: {repo_url}
    
    Please provide a comprehensive analysis including:
    1. Project overview and purpose
    2. Technology stack and dependencies
    3. Code structure and architecture
    4. Key features and functionality
    5. Code quality assessment
    6. Potential improvements or issues
    
    Focus on providing actionable insights for developers.
    """
    
    try:
        # Use the GitHub agent through agent manager
        agent_name = "GitHub Agent"
        if agent_name not in agent_manager.agents:
            raise HTTPException(status_code=500, detail="GitHub agent not available")
        
        # Create chat request for repository analysis with conversation ID
        chat_request = ChatRequest(
            message=enhanced_prompt,
            model=model,
            conversation_id=conversation_id,
            use_agent=True  # Ensure agent processing is enabled
        )
        
        # Process through chat endpoint logic to ensure proper context saving
        response = await chat_with_ai(chat_request)
        
        # Prepare GitHub context for broadcasting to all agents
        github_info = {
            'repository_url': repo_url,
            'repository_name': repo_url.split('/')[-1] if '/' in repo_url else repo_url,
            'analysis_summary': response.message.content,
            'analyzed_at': datetime.now().isoformat(),
            'model_used': response.message.model,
            'agent_used': response.agent_used,
            'conversation_id': conversation_id
        }
        
        # Broadcast GitHub context to all agents
        try:
            await agent_manager.broadcast_github_context(github_info)
            logging.info(f"🚀 GitHub context broadcasted to all {len(agent_manager.agents)} agents")
        except Exception as broadcast_error:
            logging.error(f"⚠️ GitHub broadcast failed: {str(broadcast_error)}")
            # Don't fail the request if broadcast fails
        
        # Additional metadata for repository analysis
        analysis_metadata = {
            "analysis_type": "repository_analysis",
            "repository_url": repo_url,
            "analyzed_at": datetime.now().isoformat(),
            "model_used": response.message.model,
            "conversation_id": conversation_id,
            "agent_used": response.agent_used,
            "broadcast_status": "completed"  # Indicate broadcasting was attempted
        }
        
        # Save additional metadata about the repository analysis
        await db.chat_sessions.insert_one({
            "role": "system",
            "content": f"Repository analysis completed for: {repo_url}",
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc),
            "analysis_metadata": analysis_metadata
        })
        
        logging.info(f"🔍 Repository analysis saved to conversation {conversation_id}")
        
        return {
            "analysis": response.message.content,
            "model_used": response.message.model,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "agent_used": response.agent_used,
            "repository_url": repo_url
        }
        
    except Exception as e:
        logging.error(f"❌ Repository analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Repository analysis failed: {str(e)}")

# Health check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Local Storage connection (used as MongoDB replacement)
        await db.list_collection_names()
        storage_status = "connected"
    except:
        storage_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": storage_status,  # Report as mongodb for compatibility
            "perplexity": "configured" if os.environ.get('PERPLEXITY_API_KEY') else "not_configured",
            "claude": "configured" if os.environ.get('ANTHROPIC_API_KEY') else "not_configured",
            "openai": "configured" if os.environ.get('OPENAI_API_KEY') else "not_configured"
        },
        "agents": {
            "available": len(agent_manager.agents),
            "agents_list": list(agent_manager.agents.keys())
        },
        "ai_orchestrator": {
            "available": True,
            "services": ["claude-opus-4-1", "perplexity-deep-research", "gpt-5"]
        }
    }

# CORS configuration - consolidated and fixed
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000", 
    "http://127.0.0.1:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Xionimus AI Backend",
        "version": "2.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

# Streaming Code Generation endpoint
@api_router.post("/stream-code-generation")
async def stream_code_generation(request: StreamingCodeRequest):
    """Generate code with real-time streaming updates"""
    
    # Load API keys from local storage first
    await load_api_keys_from_local_storage()
    
    # Get API keys from environment
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
    
    # Check if at least one API key is properly configured
    if not anthropic_key and not perplexity_key:
        raise HTTPException(
            status_code=400, 
            detail="API keys required for streaming code generation"
        )
    
    async def generate_code_stream():
        try:
            # Stage 1: Analyzing request
            progress = CodeGenerationProgress(
                stage="analyzing",
                progress=0.1,
                current_code="",
                message=f"📝 Analyzing {request.language} code generation request..."
            )
            yield f"data: {progress.model_dump_json()}\n\n"
            
            # Stage 2: Planning code structure
            await asyncio.sleep(0.5)
            progress = CodeGenerationProgress(
                stage="planning",
                progress=0.3,
                current_code=f"# {request.language.title()} Code Generation\n# Planning structure...\n",
                message=f"🏗️ Planning {request.language} code structure..."
            )
            yield f"data: {progress.model_dump_json()}\n\n"
            
            # Stage 3: Generate actual code using AI
            enhanced_prompt = f"""
            Generate {request.language} code for the following requirement:
            {request.prompt}
            
            Please provide clean, well-commented code with proper error handling.
            Structure the code professionally with good practices.
            Only return the code, no explanations unless specifically requested.
            """
            
            chat_request = ChatRequest(
                message=enhanced_prompt,
                model=request.model
            )
            
            response = await chat_with_ai(chat_request)
            generated_code = response.message.content
            
            # Stage 4: Show code generation progress
            code_lines = generated_code.split('\n')
            accumulated_code = ""
            
            for i, line in enumerate(code_lines):
                accumulated_code += line + '\n'
                progress_val = 0.4 + (0.5 * (i + 1) / len(code_lines))
                
                progress = CodeGenerationProgress(
                    stage="generating",
                    progress=min(progress_val, 0.9),
                    current_code=accumulated_code,
                    message=f"💻 Writing {request.language} code... ({i+1}/{len(code_lines)} lines)"
                )
                yield f"data: {progress.model_dump_json()}\n\n"
                
                # Small delay to simulate real-time generation
                await asyncio.sleep(0.1)
            
            # Stage 5: Complete
            progress = CodeGenerationProgress(
                stage="complete",
                progress=1.0,
                current_code=generated_code,
                message=f"✅ {request.language} code generation complete!"
            )
            yield f"data: {progress.model_dump_json()}\n\n"
            
        except Exception as e:
            error_progress = CodeGenerationProgress(
                stage="error",
                progress=0.0,
                current_code="",
                message=f"❌ Error: {str(e)}"
            )
            yield f"data: {error_progress.model_dump_json()}\n\n"
    
    return StreamingResponse(
        generate_code_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# GitHub Push endpoint
@api_router.post("/github-push")
async def push_code_to_github(request: GitHubPushRequest):
    """Push generated code to GitHub repository"""
    
    try:
        # Use GitHub Agent to handle the push operation
        from agents.agent_manager import AgentManager
        from agents.base_agent import AgentTask, AgentStatus
        
        agent_manager = AgentManager()
        
        # Create agent task for GitHub push
        task_description = f"Push {len(request.files)} files to GitHub repository {request.repository}"
        task = AgentTask(
            id=str(uuid.uuid4()),
            description=task_description,
            input_data={
                "operation": "push_files",
                "repository": request.repository,
                "branch": request.branch,
                "files": request.files,
                "commit_message": request.commit_message,
                "github_token": request.github_token or os.environ.get('GITHUB_TOKEN')
            },
            status=AgentStatus.PENDING
        )
        
        # Execute with GitHub Agent
        github_agent = None
        for agent in agent_manager.agents.values():
            if agent.name == "GitHub Agent":
                github_agent = agent
                break
        
        if not github_agent:
            raise HTTPException(status_code=500, detail="GitHub Agent not available")
        
        result = await github_agent.execute_task(task)
        
        if result.status == AgentStatus.COMPLETED:
            return {
                "success": True,
                "message": f"Successfully pushed {len(request.files)} files to {request.repository}",
                "result": result.result,
                "repository": request.repository,
                "branch": request.branch,
                "commit_message": request.commit_message
            }
        else:
            raise HTTPException(status_code=500, detail=f"Push failed: {result.result}")
            
    except Exception as e:
        logging.error(f"❌ GitHub push error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GitHub push failed: {str(e)}")

# RAR Download endpoint
@api_router.post("/download-code-rar")
async def download_code_as_rar(request: Dict[str, Any]):
    """Download generated code as RAR/ZIP file"""
    
    try:
        files = request.get("files", [])
        project_name = request.get("project_name", "generated_code")
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided for download")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / project_name
            project_path.mkdir(parents=True)
            
            # Write files to temporary directory
            for file_info in files:
                file_path = project_path / file_info.get("name", "file.txt")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info.get("content", ""))
            
            # Create ZIP file (since RAR requires WinRAR license, we use ZIP)
            zip_path = Path(temp_dir) / f"{project_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        arc_path = file_path.relative_to(project_path)
                        zip_file.write(file_path, arc_path)
            
            # Read ZIP file for response
            with open(zip_path, 'rb') as zip_file:
                zip_content = zip_file.read()
        
        return StreamingResponse(
            io.BytesIO(zip_content),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={project_name}.zip"}
        )
        
    except Exception as e:
        logging.error(f"❌ Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# ===== VERSION 2.1 "CORE ENHANCEMENTS" ENDPOINTS =====

# Enhanced Search Service
# REMOVED: from search_service import EnhancedSearchService, SearchType
# REMOVED: from auto_testing_service import AutoTestingService, TestFramework
# REMOVED: from code_review_ai import CodeReviewAI

# Initialize Version 2.1 services
# REMOVED: search_service = EnhancedSearchService(db_client=db)
# REMOVED: auto_testing_service = AutoTestingService()
# REMOVED: code_review_ai = CodeReviewAI()

@api_router.get("/search")
async def enhanced_search(
    query: str = Query(..., description="Search query"),
    type: str = Query("all", description="Search type: all, projects, sessions, files, chat"),
    limit: int = Query(50, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """🔍 Enhanced Search - Volltext-Suche durch alle Projekte und Sessions"""
    try:
        search_type = SearchType(type.lower())
# REMOVED:         results = await search_service.search(
            query=query,
            search_type=search_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "query": query,
            "type": type,
            "total_results": len(results),
            "results": [
                {
                    "id": r.id,
                    "title": r.title,
                    "content": r.content,
                    "type": r.type,
                    "score": r.score,
                    "metadata": r.metadata,
                    "highlighted_content": r.highlighted_content,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "updated_at": r.updated_at.isoformat() if r.updated_at else None
                }
                for r in results
            ]
        }
    except Exception as e:
        logging.error(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@api_router.get("/search/suggestions")
async def get_search_suggestions(
    partial_query: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(10, le=20, description="Maximum suggestions")
):
    """🔍 Get search suggestions based on partial query"""
    try:
# REMOVED:         suggestions = await search_service.get_search_suggestions(
            partial_query=partial_query,
            limit=limit
        )
        
        return {
            "success": True,
            "partial_query": partial_query,
            "suggestions": suggestions
        }
    except Exception as e:
        logging.error(f"❌ Search suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search suggestions failed: {str(e)}")

@api_router.get("/search/stats")
async def get_search_stats():
    """🔍 Get search statistics and performance metrics"""
    try:
# REMOVED:         stats = await search_service.get_search_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logging.error(f"❌ Search stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search stats failed: {str(e)}")

@api_router.post("/auto-test/generate")
async def generate_tests(request: Dict[str, Any]):
    """🤖 Auto-Testing - Automatische Test-Generierung"""
    try:
        code = request.get("code", "")
        language = request.get("language", "python")
        framework = request.get("framework")
        test_types = request.get("test_types", ["unit"])
        coverage_target = request.get("coverage_target", 80.0)
        
        if not code:
            raise HTTPException(status_code=400, detail="Code is required")
        
# REMOVED:         test_suite = await auto_testing_service.generate_tests(
            code=code,
            language=language,
            framework=framework,
            test_types=test_types,
            coverage_target=coverage_target
        )
        
        return {
            "success": True,
            "test_suite": {
                "name": test_suite.name,
                "language": test_suite.language,
                "framework": test_suite.framework,
                "test_count": len(test_suite.test_cases),
                "test_cases": test_suite.test_cases,
                "setup_code": test_suite.setup_code,
                "teardown_code": test_suite.teardown_code,
                "dependencies": test_suite.dependencies
            }
        }
    except Exception as e:
        logging.error(f"❌ Test generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")

@api_router.post("/auto-test/execute")
async def execute_tests(request: Dict[str, Any]):
    """🤖 Auto-Testing - Automatische Test-Ausführung"""
    try:
# REMOVED:         from auto_testing_service import TestSuite
        
        # Parse test suite from request
        suite_data = request.get("test_suite", {})
        test_suite = TestSuite(
            name=suite_data.get("name", "auto_test"),
            language=suite_data.get("language", "python"),
            framework=suite_data.get("framework", "pytest"),
            test_cases=suite_data.get("test_cases", []),
            setup_code=suite_data.get("setup_code", ""),
            teardown_code=suite_data.get("teardown_code", ""),
            dependencies=suite_data.get("dependencies", [])
        )
        
        project_path = request.get("project_path")
        
# REMOVED:         results = await auto_testing_service.execute_tests(
            test_suite=test_suite,
            project_path=project_path
        )
        
        # Calculate summary statistics
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == 'passed'])
        failed_tests = len([r for r in results if r.status == 'failed'])
        error_tests = len([r for r in results if r.status == 'error'])
        
        return {
            "success": True,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "execution_time": r.execution_time,
                    "output": r.output,
                    "error_message": r.error_message,
                    "coverage": r.coverage
                }
                for r in results
            ]
        }
    except Exception as e:
        logging.error(f"❌ Test execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

@api_router.post("/code-review")
async def review_code(request: Dict[str, Any]):
    """📝 Code Review AI - Intelligente Code-Review mit Verbesserungsvorschlägen"""
    try:
        code = request.get("code", "")
        language = request.get("language", "python")
        file_path = request.get("file_path")
        context = request.get("context", {})
        
        if not code:
            raise HTTPException(status_code=400, detail="Code is required")
        
# REMOVED:         review_result = await code_review_ai.review_code(
            code=code,
            language=language,
            file_path=file_path,
            context=context
        )
        
        return {
            "success": True,
            "review": {
                "overall_score": review_result.overall_score,
                "grade": review_result.grade,
                "summary": review_result.review_summary,
                "metrics": {
                    "complexity": review_result.metrics.complexity,
                    "maintainability_index": review_result.metrics.maintainability_index,
                    "lines_of_code": review_result.metrics.lines_of_code,
                    "code_duplication": review_result.metrics.code_duplication,
                    "security_score": review_result.metrics.security_score,
                    "performance_score": review_result.metrics.performance_score,
                    "documentation_coverage": review_result.metrics.documentation_coverage
                },
                "issues": [
                    {
                        "id": issue.id,
                        "severity": issue.severity,
                        "category": issue.category,
                        "title": issue.title,
                        "description": issue.description,
                        "line_number": issue.line_number,
                        "column": issue.column,
                        "suggestion": issue.suggestion,
                        "example_fix": issue.example_fix,
                        "confidence": issue.confidence
                    }
                    for issue in review_result.issues
                ],
                "suggestions": review_result.suggestions,
                "positive_aspects": review_result.positive_aspects,
                "generated_at": review_result.generated_at.isoformat()
            }
        }
    except Exception as e:
        logging.error(f"❌ Code review error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(e)}")

@api_router.get("/version-info")
async def get_version_info():
    """Get XIONIMUS AI version information"""
    return {
        "success": True,
        "version": "2.1.0",
        "codename": "Core Enhancements",
        "features": {
            "enhanced_search": "✅ Volltext-Suche durch alle Projekte und Sessions",
            "auto_testing": "✅ Automatische Test-Generierung und -Ausführung",
# REMOVED:             "code_review_ai": "✅ Intelligente Code-Review mit Verbesserungsvorschlägen",
            "voice_commands": "🚧 Coming Soon",
            "git_integration": "🚧 Coming Soon"
        },
        "release_date": "2024-09-25",
        "status": "active"
    }

# Include the API router
app.include_router(api_router)

async def load_api_keys_from_local_storage():
    """Load API keys from Local Storage into environment on startup"""
    try:
        logging.info("🔄 Loading API keys from Local Storage on startup")
        
        # Get all API keys from Local Storage
        cursor = await db.api_keys.find({"is_active": True})
        api_keys = cursor.to_list(length=None)
        storage_loaded = 0
        
        for key_doc in api_keys:
            service = key_doc.get("service")
            key_value = key_doc.get("key")
            
            if service and key_value:
                env_var = f"{service.upper()}_API_KEY"
                os.environ[env_var] = key_value
                storage_loaded += 1
                logging.info(f"✅ Loaded {service} API key from Local Storage")
        
        logging.info(f"✅ API key loading complete - Loaded {storage_loaded} keys from storage")
        return storage_loaded
        
    except Exception as e:
        logging.warning(f"⚠️ Failed to load API keys from Local Storage: {str(e)}")
        logging.info("ℹ️ No API keys loaded - please configure API keys via the UI")
        return 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")