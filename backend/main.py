from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import json
import jwt

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import API routes
from app.api import chat, auth, files, workspace, github, testing, agents, supervisor, bulk_files, knowledge, vision, sessions, chat_stream, multimodal_api, rag_api, workspace_api, clipboard_api, edit, tokens, metrics, rate_limits, session_management, github_pat, session_fork, file_upload, version, sandbox, sandbox_templates, api_keys, multi_agents, research_history
from app.api import settings as settings_api
from app.api import developer_modes  # PHASE 2: Developer Modes
from app.core.database import init_database, close_database
from app.core.redis_client import init_redis, close_redis_async
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

# Validate environment variables (must happen after load_dotenv)
try:
    from app.core.env_validator import validate_environment
    validate_environment(strict_mode=False)
    logger.info("✅ Environment validation successful")
except Exception as e:
    logger.error(f"❌ Environment validation failed: {e}")
    # In development, we continue with warnings
    if settings.DEBUG:
        logger.warning("⚠️  Running in DEBUG mode - continuing despite validation errors")
    else:
        raise

# Run auto-setup to fix common issues
try:
    from app.core.auto_setup import run_auto_setup
    run_auto_setup()
except Exception as e:
    logger.warning(f"Auto-setup skipped: {e}")

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    import time
    
    # Store startup time for uptime calculation
    app.state.start_time = time.time()
    
    logger.info("🚀 Xionimus AI Backend starting...")
    
    # Initialize PostgreSQL database with pgvector support
    await init_database()
    
    # Initialize Redis cache
    await init_redis()
    
    # Initialize MongoDB for research history
    from app.core.mongo_db import connect_mongodb, close_mongodb
    try:
        await connect_mongodb()
    except Exception as e:
        logger.warning(f"⚠️  MongoDB connection failed: {e}. Research history will not be available.")
    
    # Test AI services
    from app.core.ai_manager import test_ai_services
    await test_ai_services()
    
    # Create upload directories
    Path("uploads").mkdir(exist_ok=True)
    Path("workspace").mkdir(exist_ok=True)
    
    yield
    
    await close_database()
    await close_redis_async()
    try:
        await close_mongodb()
    except:
        pass
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

# Advanced Rate Limiting System
from app.core.rate_limiter import rate_limiter
from app.core.rate_limiter import RateLimitExceeded as CustomRateLimitExceeded
from app.core.auth import get_current_user, get_optional_user, User

async def _custom_rate_limit_handler(request: Request, exc: CustomRateLimitExceeded):
    """Handle rate limit exceeded exceptions"""
    retry_after = getattr(exc, 'retry_after', 60)
    headers = {"Retry-After": str(retry_after)}
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "rate_limit_exceeded",
            "retry_after": str(retry_after)
        },
        headers=headers
    )

# Register custom rate limit handler
app.add_exception_handler(CustomRateLimitExceeded, _custom_rate_limit_handler)
# Also register slowapi's RateLimitExceeded
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger.info("✅ Advanced Rate Limiting enabled with user-based quotas")

# Register exception handlers
app.add_exception_handler(XionimusException, xionimus_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

logger.info("✅ Security headers middleware enabled")

# Authentication & Authorization Middleware with Rate Limiting
from app.core.auth import AuthenticationError

@app.middleware("http")
async def auth_and_rate_limit_middleware(request: Request, call_next):
    """
    Combined Authentication and Rate Limiting middleware
    - Handles both auth requirements and rate limiting
    - WebSocket endpoints: skip both auth and rate limiting
    - Public endpoints: skip auth but apply rate limiting
    - Protected endpoints: require auth and apply rate limiting
    """
    # Public endpoints (no auth required but rate limited)
    public_paths = {
        "/api/health",
        "/api/v1/health",  # Versioned health endpoint - public
        "/docs", 
        "/redoc",
        "/openapi.json",
        "/",
        "/metrics",
        "/api/metrics",  # Prometheus metrics endpoint - public
        "/api/v1/metrics",  # V1 metrics endpoint - public
        "/api/rate-limits/limits",
        "/api/rate-limits/health",
        "/api/metrics/performance",  # Performance tracking - no auth needed
        "/api/metrics/health",
        "/api/v1/metrics/health",  # V1 metrics health - public
        "/api/settings/github-config",  # GitHub config status check - no auth needed (no sensitive data)
        "/api/github/import",  # GitHub import - allow public repo imports without auth
        "/api/github/import/status",  # Import status - no auth needed
        "/api/version",  # API version info - public
        "/api/v1/version",  # API version info - public
        "/api/migration-guide",  # Migration guide - public
        "/api/v1/migration-guide",  # Migration guide - public
        "/api/version/stats",  # Version stats - public
        "/api/v1/version/stats"  # Version stats - public
    }
    
    # Public path prefixes (no auth required for paths starting with these)
    public_path_prefixes = [
        "/api/github/import/check-directory/",  # Directory availability check - no auth needed
    ]
    
    # Auth endpoints (no auth required for login/register but rate limited)
    auth_paths = {"/api/auth/login", "/api/auth/register", "/api/v1/auth/login", "/api/v1/auth/register"}
    
    # Skip everything for WebSockets and static uploads
    if ("websocket" in request.headers.get("upgrade", "").lower() or
        request.url.path.startswith("/uploads/")):
        return await call_next(request)
    
    # Extract user info for rate limiting (if authenticated)
    user_id = None
    user_role = "user"
    
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("authorization")
        
        # Check if path matches any public prefix
        is_public_prefix = any(request.url.path.startswith(prefix) for prefix in public_path_prefixes)
        
        # Authentication check for protected endpoints
        if (request.url.path not in public_paths and 
            request.url.path not in auth_paths and
            not is_public_prefix):
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authentication required", "type": "auth_required"}
                )
            
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) == 2 else None
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token format", "type": "auth_invalid"}
                )
            
            # Extract user info for rate limiting (basic parsing)
            try:
                import jwt
                from app.core.config import settings
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                user_id = payload.get("sub")
                user_role = payload.get("role", "user")
            except Exception as e:
                # Invalid token will be caught by endpoint dependencies
                # Log for monitoring but don't block request
                logger.debug(f"Token decode failed in rate limiter: {str(e)}")
                pass
        
        # Rate limiting check for all API endpoints
        is_ai_call = "/api/chat/" in request.url.path
        
        rate_limit_allowed = await rate_limiter.check_rate_limit(
            request=request,
            user_id=user_id,
            user_role=user_role,
            is_ai_call=is_ai_call
        )
        
        if not rate_limit_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "type": "rate_limit_exceeded",
                    "retry_after": "60"
                },
                headers={"Retry-After": "60"}
            )
    
    response = await call_next(request)
    return response

# Configure CORS (Environment-aware)
from app.core.cors_config import get_cors_middleware_config, CORSConfig

cors_config = get_cors_middleware_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Print CORS configuration summary
CORSConfig.print_config_summary()

# Rate limiting is configured and active
# Global protection against abuse and cost explosion
# Specific endpoints have custom limits:
# - Chat/AI: 30 req/min (protects AI API costs)
# - Auth/Login: 5 req/min (prevents brute force)
# - Code Review: 10 req/min (protects review costs)
logger.info("✅ Rate limiting configured")

# API Versioning System
from app.core.versioning import APIVersioningMiddleware, APIVersion
app.add_middleware(
    APIVersioningMiddleware,
    enable_redirect=True,  # Enable backward compatibility
    log_usage=True  # Track migration progress
)
logger.info(f"✅ API Versioning enabled (current: {APIVersion.CURRENT})")
logger.info("   ℹ️  Legacy /api/* routes redirect to /api/v1/* with deprecation headers")

# Register API routes
# Core APIs (always loaded)
# V1 Routes (Primary - recommended)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth", "v1"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions", "v1"])
app.include_router(session_management.router, prefix="/api/v1/session-management", tags=["session-management", "v1"])
app.include_router(session_fork.router, prefix="/api/v1/session-fork", tags=["session-fork", "v1"])
app.include_router(file_upload.router, prefix="/api/v1/file-upload", tags=["file-upload", "v1"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat", "v1"])
app.include_router(chat_stream.router, prefix="/api/v1", tags=["streaming", "v1"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files", "v1"])

# Legacy Routes (Deprecated - for backward compatibility)
# These will automatically get deprecation headers via middleware
app.include_router(auth.router, prefix="/api/auth", tags=["auth", "legacy"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions", "legacy"])
app.include_router(session_management.router, prefix="/api/session-management", tags=["session-management", "legacy"])
app.include_router(session_fork.router, prefix="/api/session-fork", tags=["session-fork", "legacy"])
app.include_router(file_upload.router, prefix="/api/file-upload", tags=["file-upload", "legacy"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat", "legacy"])
app.include_router(chat_stream.router, prefix="/api", tags=["streaming", "legacy"])
app.include_router(files.router, prefix="/api/files", tags=["files", "legacy"])

# Feature APIs (with feature flags)
if os.getenv("ENABLE_GITHUB_INTEGRATION", "true").lower() == "true":
    # V1
    app.include_router(github.router, prefix="/api/v1/github", tags=["github", "v1"])
    app.include_router(github_pat.router, prefix="/api/v1/github-pat", tags=["github-pat", "v1"])
    # Legacy
    app.include_router(github.router, prefix="/api/github", tags=["github", "legacy"])
    app.include_router(github_pat.router, prefix="/api/github-pat", tags=["github-pat", "legacy"])
    logger.info("✅ GitHub Integration enabled (OAuth + PAT)")

# Settings API (always available)
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["settings", "v1"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["settings", "legacy"])
logger.info("✅ Settings API enabled")

# Version Info API (always available, public)
# Note: Public endpoints - no auth required
app.include_router(version.router, prefix="/api/v1", tags=["meta", "v1"], dependencies=[])
app.include_router(version.router, prefix="/api", tags=["meta", "legacy"], dependencies=[])
logger.info("✅ Version Info API enabled (public)")

# Code Review API removed - chat only mode

# Register Edit Agent API (NEW)
app.include_router(edit.router, prefix="/api/v1/edit", tags=["edit-agent", "v1"])
app.include_router(edit.router, prefix="/api/edit", tags=["edit-agent", "legacy"])
logger.info("✅ Edit Agent enabled")

# Register Token Usage API (NEW)
app.include_router(tokens.router, prefix="/api/v1/tokens", tags=["tokens", "v1"])
app.include_router(tokens.router, prefix="/api/tokens", tags=["tokens", "legacy"])
logger.info("✅ Token Usage Tracking enabled")

# Register Performance Metrics API (NEW)
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics", "v1"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics", "legacy"])
logger.info("✅ Performance Metrics enabled")

# Register Rate Limiting Management API (NEW)
app.include_router(rate_limits.router, prefix="/api/v1/rate-limits", tags=["rate-limits", "v1"])
app.include_router(rate_limits.router, prefix="/api/rate-limits", tags=["rate-limits", "legacy"])
logger.info("✅ Rate Limiting Management API enabled")

# PHASE 2: Developer Modes - Both v1 and legacy routes
app.include_router(developer_modes.router, prefix="/api/v1", tags=["developer-modes", "v1"])
app.include_router(developer_modes.router, prefix="/api", tags=["developer-modes", "legacy"])
logger.info("✅ Developer Modes System enabled")

# PHASE 4: Sandbox Code Execution - Both v1 and legacy routes
app.include_router(sandbox.router, prefix="/api/v1/sandbox", tags=["sandbox", "v1"])
app.include_router(sandbox.router, prefix="/api/sandbox", tags=["sandbox", "legacy"])
logger.info("✅ Sandbox Code Execution enabled")

# PHASE 4: Sandbox Templates - Code starter templates
app.include_router(sandbox_templates.router, prefix="/api/v1/sandbox/templates", tags=["sandbox-templates", "v1"])
app.include_router(sandbox_templates.router, prefix="/api/sandbox/templates", tags=["sandbox-templates", "legacy"])
logger.info("✅ Sandbox Code Templates enabled")

# PHASE 4: API Keys Management - Secure user API key storage
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["api-keys", "v1"])
app.include_router(api_keys.router, prefix="/api/api-keys", tags=["api-keys", "legacy"])
logger.info("✅ API Keys Management enabled")

# AGENTEN PHASE: Multi-Agent System - Research, Code Review, Testing, etc.
app.include_router(multi_agents.router, prefix="/api/v1", tags=["multi-agents", "v1"])
app.include_router(multi_agents.router, tags=["multi-agents", "legacy"])
logger.info("✅ Multi-Agent System enabled (8 agents: Research, Code Review, Testing, Documentation, Debugging, Security, Performance, Fork)")

# PHASE 5: Research History & PDF Export - Store and export research results
# V1 Routes (Primary - recommended)
app.include_router(research_history.router, prefix="/api/v1", tags=["research-history", "v1"])
# Legacy Routes (Deprecated - for backward compatibility)
app.include_router(research_history.router, prefix="/api", tags=["research-history", "legacy"])
logger.info("✅ Research History & PDF Export enabled")


if os.getenv("ENABLE_RAG_SYSTEM", "true").lower() == "true":
    app.include_router(rag_api.router, prefix="/api/v1", tags=["rag", "v1"])
    app.include_router(rag_api.router, tags=["rag", "legacy"])
    logger.info("✅ RAG System enabled")

if os.getenv("ENABLE_MULTIMODAL", "true").lower() == "true":
    app.include_router(multimodal_api.router, prefix="/api/v1", tags=["multimodal", "v1"])
    app.include_router(multimodal_api.router, tags=["multimodal", "legacy"])
    logger.info("✅ Multimodal Support enabled")

if os.getenv("ENABLE_WORKSPACE", "true").lower() == "true":
    app.include_router(workspace.router, prefix="/api/v1/workspace", tags=["workspace", "v1"])
    app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace", "legacy"])
    app.include_router(workspace_api.router, prefix="/api/v1", tags=["workspace-advanced", "v1"])
    app.include_router(workspace_api.router, tags=["workspace-advanced", "legacy"])
    logger.info("✅ Workspace Management enabled")

# Optional/Advanced APIs (disabled by default in production)
if os.getenv("ENABLE_AGENTS", "false").lower() == "true":
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents", "v1"])
    app.include_router(agents.router, prefix="/api/agents", tags=["agents", "legacy"])
    app.include_router(supervisor.router, prefix="/api/v1/supervisor", tags=["supervisor", "v1"])
    app.include_router(supervisor.router, prefix="/api/supervisor", tags=["supervisor", "legacy"])
    logger.info("✅ Agent System enabled")

if os.getenv("ENABLE_ADVANCED_FILES", "false").lower() == "true":
    app.include_router(bulk_files.router, prefix="/api/v1/bulk", tags=["bulk-operations", "v1"])
    app.include_router(bulk_files.router, prefix="/api/bulk", tags=["bulk-operations", "legacy"])
    logger.info("✅ Advanced File Operations enabled")

if os.getenv("ENABLE_KNOWLEDGE_GRAPH", "false").lower() == "true":
    app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge-graph", "v1"])
    app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge-graph", "legacy"])
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
        from app.core.database import engine, DATABASE_URL
        from sqlalchemy import text
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_error = str(e)
        DATABASE_URL = ""
    
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
                "type": "PostgreSQL" if DATABASE_URL.startswith("postgresql") else "SQLite",
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

# V1 Health check (versioned duplicate for proper routing)
@app.get("/api/v1/health")
async def health_check_v1():
    """V1 health check endpoint - delegates to main health check"""
    return await health_check()

# Prometheus metrics endpoint (both versioned and legacy)
@app.get("/api/metrics")
@app.get("/api/v1/metrics")
async def prometheus_metrics_endpoint():
    """
    Prometheus metrics endpoint
    
    Returns metrics in Prometheus format for scraping.
    Available at: /api/metrics (legacy) and /api/v1/metrics (current)
    """
    from app.core.prometheus_metrics import get_prometheus_metrics
    return get_prometheus_metrics()

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