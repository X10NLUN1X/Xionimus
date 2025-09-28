from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Import API routes
from api import agents, chat, files, sessions
from core.database import init_database
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("🚀 XIONIMUS AI Backend starting...")
    
    # Initialize database
    await init_database()
    logger.info("✅ Database initialized")
    
    # Test AI services
    from core.ai_orchestrator import test_ai_services
    await test_ai_services()
    
    yield
    
    logger.info("👋 XIONIMUS AI Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="XIONIMUS AI",
    description="Advanced Multi-Agent AI System",
    version="3.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "services": {
            "database": "connected",
            "ai_services": "configured"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "XIONIMUS AI Backend v3.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )