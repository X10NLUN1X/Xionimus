from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import json

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import API routes
from app.api import chat, auth, files, workspace, github, testing, agents, supervisor, bulk_files, knowledge, vision, sessions, chat_stream, multimodal_api, rag_api, workspace_api, clipboard_api, code_review, edit, tokens, metrics
from app.api import settings as settings_api
from app.core.database import init_database, close_database
from app.core.config import settings
from app.core.errors import (
    XionimusException,
    xionimus_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from fastapi.exceptions import RequestValidationError

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    import time
    
    # Store startup time for uptime calculation
    app.state.start_time = time.time()
    
    logger.info("🚀 Xionimus AI Backend starting...")
    
    # Initialize SQLAlchemy database (unified database strategy)
    await init_database()
    
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

# Initialize Rate Limiter (only for HTTP endpoints, not WebSocket)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Custom rate limit exception handler that excludes WebSocket connections
async def custom_rate_limit_handler(request, exc):
    """
    Custom rate limit handler that properly handles WebSocket upgrade requests
    WebSocket connections should never hit rate limits as they use a different protocol
    """
    # Check if this is a WebSocket upgrade request
    if request.headers.get("upgrade", "").lower() == "websocket":
        # This should never happen, but if it does, log it and allow the connection
        logger.warning("⚠️ Rate limit applied to WebSocket connection - this should not happen")
        return None
    
    # Apply normal rate limit handling for HTTP requests
    return await _rate_limit_exceeded_handler(request, exc)

app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

logger.info("✅ Rate limiting enabled (WebSocket connections properly excluded)")

# Register exception handlers
app.add_exception_handler(XionimusException, xionimus_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Configure CORS
# Note: WebSocket connections also need proper CORS handling
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
        # Allow all localhost for development (WebSocket compatibility)
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers for WebSocket
)

# Rate limiting is configured and active
# Global protection against abuse and cost explosion
# Specific endpoints have custom limits:
# - Chat/AI: 30 req/min (protects AI API costs)
# - Auth/Login: 5 req/min (prevents brute force)
# - Code Review: 10 req/min (protects review costs)
logger.info("✅ Rate limiting configured")

# Register API routes
# Core APIs (always loaded)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(chat_stream.router, prefix="/api", tags=["streaming"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

# Feature APIs (with feature flags)
if os.getenv("ENABLE_GITHUB_INTEGRATION", "true").lower() == "true":
    app.include_router(github.router, prefix="/api/github", tags=["github"])
    logger.info("✅ GitHub Integration enabled")

# Settings API (always available)
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings"])
logger.info("✅ Settings API enabled")

# Register Code Review API
app.include_router(code_review.router, prefix="/api/code-review", tags=["code-review"])
logger.info("✅ Code Review System enabled")

# Register Edit Agent API (NEW)
app.include_router(edit.router, prefix="/api/edit", tags=["edit-agent"])
logger.info("✅ Edit Agent enabled")

# Register Token Usage API (NEW)
app.include_router(tokens.router, prefix="/api/tokens", tags=["tokens"])
logger.info("✅ Token Usage Tracking enabled")

# Register Performance Metrics API (NEW)
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
logger.info("✅ Performance Metrics enabled")

if os.getenv("ENABLE_RAG_SYSTEM", "true").lower() == "true":
    app.include_router(rag_api.router, tags=["rag"])
    logger.info("✅ RAG System enabled")

if os.getenv("ENABLE_MULTIMODAL", "true").lower() == "true":
    app.include_router(multimodal_api.router, tags=["multimodal"])
    logger.info("✅ Multimodal Support enabled")

if os.getenv("ENABLE_WORKSPACE", "true").lower() == "true":
    app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])
    app.include_router(workspace_api.router, tags=["workspace-advanced"])
    logger.info("✅ Workspace Management enabled")

# Optional/Advanced APIs (disabled by default in production)
if os.getenv("ENABLE_AGENTS", "false").lower() == "true":
    app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
    app.include_router(supervisor.router, prefix="/api/supervisor", tags=["supervisor"])
    logger.info("✅ Agent System enabled")

if os.getenv("ENABLE_ADVANCED_FILES", "false").lower() == "true":
    app.include_router(bulk_files.router, prefix="/api/bulk", tags=["bulk-operations"])
    logger.info("✅ Advanced File Operations enabled")

if os.getenv("ENABLE_KNOWLEDGE_GRAPH", "false").lower() == "true":
    app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge-graph"])
    logger.info("✅ Knowledge Graph enabled")

if os.getenv("ENABLE_VISION_EXPERT", "false").lower() == "true":
    app.include_router(vision.router, prefix="/api/vision", tags=["vision-expert"])
    logger.info("✅ Vision Expert enabled")

if os.getenv("ENABLE_CLIPBOARD", "false").lower() == "true":
    app.include_router(clipboard_api.router, tags=["clipboard"])
    logger.info("✅ Clipboard Assistant enabled")

# Development only
if os.getenv("ENVIRONMENT", "development") == "development":
    app.include_router(testing.router, prefix="/api/testing", tags=["testing"])
    logger.info("⚠️ Testing endpoints enabled (development mode)")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Enhanced health check endpoint for monitoring and observability
    
    Returns comprehensive system health status including:
    - Overall status
    - Service availability (database, AI providers)
    - System metrics (uptime, memory)
    - Configuration status
    """
    from app.core.ai_manager import AIManager
    from datetime import datetime, timezone
    import time
    import psutil
    
    ai_manager = AIManager()
    
    # Calculate uptime
    uptime_seconds = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
    
    # Get system metrics
    memory = psutil.virtual_memory()
    
    # Check database connectivity
    db_status = "connected"
    db_error = None
    try:
        from app.core.database import engine
        from sqlalchemy import text
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    
    # Get AI provider status
    ai_providers = ai_manager.get_provider_status()
    ai_configured_count = sum(1 for status in ai_providers.values() if status)
    
    # Determine overall health status
    overall_status = "healthy"
    if db_status == "error":
        overall_status = "degraded"
    elif ai_configured_count == 0:
        overall_status = "limited"  # Works but no AI providers configured
    
    return {
        "status": overall_status,
        "version": "2.0.0",
        "platform": "Xionimus AI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": int(uptime_seconds),
        "services": {
            "database": {
                "status": db_status,
                "type": "SQLite",
                "error": db_error
            },
            "ai_providers": {
                "configured": ai_configured_count,
                "total": len(ai_providers),
                "status": ai_providers
            }
        },
        "system": {
            "memory_used_percent": memory.percent,
            "memory_available_mb": round(memory.available / (1024 * 1024), 2)
        },
        "environment": {
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL
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