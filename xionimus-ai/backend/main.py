from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import json

# Import API routes
from app.api import chat, auth, files, workspace
from app.core.database import init_database, close_database
from app.core.config import settings
from app.core.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# WebSocket manager
ws_manager = WebSocketManager()

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("🚀 Xionimus AI Backend starting...")
    
    # Initialize database
    await init_database()
    logger.info("✅ Database initialized")
    
    # Test AI services
    from app.core.ai_manager import test_ai_services
    await test_ai_services()
    
    # Create upload directories
    Path("uploads").mkdir(exist_ok=True)
    Path("workspace").mkdir(exist_ok=True)
    
    yield
    
    await close_database()
    logger.info("👋 Xionimus AI Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Xionimus AI",
    description="Advanced AI Development Platform with Multi-Agent Intelligence",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Add support for port 3001
        "http://127.0.0.1:3001",  # Add support for port 3001
        "http://localhost:3002",  # Add support for port 3002
        "http://127.0.0.1:3002",  # Add support for port 3002
        "http://localhost:5173",  # Vite dev server alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process AI chat message
            from app.core.ai_manager import AIManager
            ai_manager = AIManager()
            
            response = await ai_manager.generate_response(
                provider=message_data.get("provider", "openai"),
                model=message_data.get("model", "gpt-5"),  # Latest GPT-5 default
                messages=message_data.get("messages", []),
                stream=True
            )
            
            # Send response back
            await websocket.send_text(json.dumps({
                "type": "response",
                "content": response["content"],
                "usage": response.get("usage"),
                "model": response["model"]
            }))
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, session_id)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    from app.core.ai_manager import AIManager
    ai_manager = AIManager()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "platform": "Xionimus AI",
        "ai_models": "Latest models with classic API keys (GPT-5, Claude-Opus-4.1, Perplexity)",
        "services": {
            "database": "connected",
            "ai_providers": ai_manager.get_provider_status(),
            "available_models": ai_manager.get_available_models(),
            "integration_method": "Classic API Keys Only"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Xionimus AI Backend v1.0.0",
        "platform": "Advanced AI Development Platform",
        "docs": "/docs"
    }

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting Xionimus AI on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )