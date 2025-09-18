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
from emergentintegrations.llm.chat import LlmChat, UserMessage
from agents.agent_manager import AgentManager

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Emergent Desktop Alternative", description="Private AI Assistant with Perplexity and Claude")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Global AI clients and agent manager
perplexity_client = None
claude_chat = None
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

async def get_claude_chat():
    global claude_chat
    if claude_chat is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            claude_chat = LlmChat(
                api_key=api_key,
                session_id="claude-session",
                system_message="Du bist Claude, ein hilfsreicher KI-Assistent. Antworte auf Deutsch."
            ).with_model("anthropic", "claude-3-5-sonnet-20241022")
    return claude_chat

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
        
        # Process with selected AI
        if request.model == "perplexity":
            client = await get_perplexity_client()
            if not client:
                raise HTTPException(status_code=400, detail="Perplexity API key not configured")
            
            try:
                messages = [{"role": "user", "content": request.message}]
                if request.system_message:
                    messages.insert(0, {"role": "system", "content": request.system_message})
                
                response = await client.chat.completions.create(
                    model="sonar-pro",
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                sources = getattr(response, 'search_results', [])
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            except Exception as e:
                logging.error(f"Perplexity API error: {e}")
                raise HTTPException(status_code=400, detail=f"Perplexity API error: {str(e)}")
            
        elif request.model == "claude":
            chat = await get_claude_chat()
            if not chat:
                raise HTTPException(status_code=400, detail="Anthropic API key not configured")
            
            try:
                user_msg = UserMessage(text=request.message)
                response = await chat.send_message(user_msg)
                
                content = response
                sources = None
                tokens_used = None
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
            sources=sources
        )
        
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
    global perplexity_client, claude_chat
    if api_key.service == "perplexity":
        perplexity_client = None
    elif api_key.service == "anthropic":
        claude_chat = None
    
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()