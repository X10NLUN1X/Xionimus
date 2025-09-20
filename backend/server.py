from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
from openai import AsyncOpenAI
import anthropic
# Removed emergentintegrations dependency - using direct API clients
from agents.agent_manager import AgentManager

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Xionimus AI", description="Autonomous Artificial Intelligence with Specialized Agents")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global clients for reuse
perplexity_client = None
claude_client = None
agent_manager = AgentManager()

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
    model: str  # 'perplexity' or 'claude'
    conversation_id: Optional[str] = None
    system_message: Optional[str] = None
    use_agent: Optional[bool] = True  # Enable agent processing by default
    context: Optional[Dict[str, Any]] = None

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

# Chat endpoints
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Save user message
        user_message = ChatMessage(
            role="user",
            content=request.message,
            model=request.model
        )
        await db.messages.insert_one(user_message.dict())
        
        # Check if agent processing is requested and available
        agent_result = None
        agent_used = None
        processing_steps = None
        language_detected = None
        
        # Always try agent processing first, then fall back
        try:
            # Process with agent manager
            context = request.context or {}
            agent_response = await agent_manager.process_request(request.message, context)
            
            language_detected = agent_response.get('language_info', {}).get('language')
            
            if request.use_agent and agent_response.get('requires_agent'):
                # Agent processing was used
                agent_used = agent_response.get('agent_used')
                agent_result = agent_response.get('result')
                processing_steps = agent_response.get('steps', [])
                
                if agent_response.get('status') == 'completed' and agent_result:
                    # Format agent result based on agent type and content
                    content = await _format_agent_response(agent_used, agent_result, language_detected)
                    
                    # Save agent response
                    assistant_message = ChatMessage(
                        role="assistant",
                        content=content,
                        model=f"{agent_used}",
                        tokens_used=agent_result.get('tokens_used') if isinstance(agent_result, dict) else None
                    )
                    await db.messages.insert_one(assistant_message.dict())
                    
                    return ChatResponse(
                        message=assistant_message,
                        conversation_id=conversation_id,
                        agent_used=agent_used,
                        agent_result=agent_result,
                        language_detected=language_detected,
                        processing_steps=processing_steps
                    )
                elif agent_response.get('status') == 'error':
                    # Agent failed, fall back to regular AI
                    logging.warning(f"Agent processing failed: {agent_response.get('error')}")
            
            # Use enhanced system message from agent manager or default to Perplexity for general chat
            enhanced_system_message = agent_response.get('system_message', request.system_message)
            enhanced_prompt = agent_response.get('enhanced_prompt', request.message)
            
        except Exception as e:
            logging.error(f"Agent processing error: {e}")
            # Fall back to regular AI processing
            enhanced_system_message = request.system_message
            enhanced_prompt = request.message
        
        # Process with selected AI model
        if request.model == "perplexity":
            client = await get_perplexity_client()
            if not client:
                raise HTTPException(status_code=400, detail="Perplexity API key not configured")
            
            try:
                messages = [{"role": "user", "content": enhanced_prompt}]
                if enhanced_system_message:
                    messages.insert(0, {"role": "system", "content": enhanced_system_message})
                
                response = await client.chat.completions.create(
                    model="sonar",
                    messages=messages,
                    max_tokens=4000,
                    temperature=0.7,
                    stream=False
                )
                
                content = response.choices[0].message.content
                sources = []
                # Try to get search results if available
                if hasattr(response, 'citations') and response.citations:
                    sources = [{"url": citation.get("url", ""), "title": citation.get("title", "")} 
                              for citation in response.citations[:5]]
                
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else None
            except Exception as e:
                logging.error(f"Perplexity API error: {e}")
                raise HTTPException(status_code=400, detail=f"Perplexity API error: {str(e)}")
            
        elif request.model == "claude":
            client = await get_claude_client()
            if not client:
                raise HTTPException(status_code=400, detail="Anthropic API key not configured")
            
            try:
                # Validate that we have a non-empty prompt
                final_prompt = enhanced_prompt if enhanced_prompt and enhanced_prompt.strip() else request.message
                if not final_prompt or not final_prompt.strip():
                    raise HTTPException(status_code=400, detail="Empty message not allowed")
                
                # Create messages for Claude API
                messages = [
                    {
                        "role": "user",
                        "content": final_prompt
                    }
                ]
                
                # Create system message
                system_message = enhanced_system_message if enhanced_system_message else "Du bist Claude, ein hilfsreicher KI-Assistent. Antworte auf Deutsch in einem natürlichen, menschlichen Stil."
                
                # Call Claude API with Claude 3.5 Sonnet (simplified model name)
                response = await client.messages.create(
                    model="claude-3-5-sonnet",
                    max_tokens=4000,
                    temperature=0.7,
                    system=system_message,
                    messages=messages
                )
                
                content = response.content[0].text
                sources = None
                tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            except Exception as e:
                logging.error(f"Claude API error: {e}")
                raise HTTPException(status_code=400, detail=f"Claude API error: {str(e)}")
            
        else:
            raise HTTPException(status_code=400, detail="Invalid model selection")
        
        # Save assistant response
        assistant_message = ChatMessage(
            role="assistant",
            content=content,
            model=request.model,
            tokens_used=tokens_used
        )
        await db.messages.insert_one(assistant_message.dict())
        
        return ChatResponse(
            message=assistant_message,
            conversation_id=conversation_id,
            sources=sources,
            agent_used=agent_used,
            agent_result=agent_result,
            language_detected=language_detected,
            processing_steps=processing_steps
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 400 errors) without modification
        raise
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    messages = await db.messages.find({"conversation_id": conversation_id}).sort("timestamp", 1).to_list(100)
    return [ChatMessage(**msg) for msg in messages]

# Project Management endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(request: ProjectRequest):
    project = Project(name=request.name, description=request.description)
    await db.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().sort("updated_at", -1).to_list(100)
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
@api_router.post("/files", response_model=CodeFile)
async def create_code_file(request: CodeFileRequest):
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
    files = await db.code_files.find({"project_id": project_id}).sort("updated_at", -1).to_list(100)
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

# API Key Management endpoints
@api_router.post("/api-keys")
async def save_api_key(api_key: APIKey):
    # Store in environment (in real app, use secure storage)
    env_var = f"{api_key.service.upper()}_API_KEY"
    os.environ[env_var] = api_key.key
    
    # Reset clients to use new keys
    global perplexity_client, claude_client
    if api_key.service == "perplexity":
        perplexity_client = None
    elif api_key.service == "anthropic":
        claude_client = None
    
    return {"message": f"{api_key.service} API key saved successfully"}

@api_router.get("/api-keys/status")
async def get_api_keys_status():
    return {
        "perplexity": bool(os.environ.get('PERPLEXITY_API_KEY')),
        "anthropic": bool(os.environ.get('ANTHROPIC_API_KEY'))
    }

# Code Generation endpoint
@api_router.post("/generate-code")
async def generate_code(request: Dict[str, Any]):
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
    """Analyze a request to determine which agent should handle it"""
    message = request.get("message", "")
    context = request.get("context", {})
    
    # Get agent recommendations without executing
    agent_scores = {}
    for agent_name, agent in agent_manager.agents.items():
        confidence = agent.can_handle_task(message, context)
        if confidence > 0:
            agent_scores[agent_name] = confidence
    
    # Detect language
    language_info = agent_manager.language_detector.detect_language(message)
    
    return {
        "message": message,
        "language_detected": language_info,
        "agent_recommendations": agent_scores,
        "best_agent": max(agent_scores, key=agent_scores.get) if agent_scores else None,
        "requires_agent": agent_manager._requires_agent_processing(message, context)
    }

# Health check
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "services": {
            "mongodb": "connected",
            "perplexity": "configured" if os.environ.get('PERPLEXITY_API_KEY') else "not_configured",
            "claude": "configured" if os.environ.get('ANTHROPIC_API_KEY') else "not_configured"
        },
        "agents": {
            "available": len(agent_manager.agents),
            "active_tasks": len(agent_manager.active_tasks),
            "agents_list": list(agent_manager.agents.keys())
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
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

# Include the API router
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()