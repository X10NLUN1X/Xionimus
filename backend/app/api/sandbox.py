"""
Sandbox API - Secure Code Execution
Provides endpoints for running code in isolated environment
"""
import sys
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

IS_WINDOWS = sys.platform == 'win32'

from ..core.sandbox_executor import sandbox_executor
from ..core.auth import get_current_user, User
from ..core.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)
router = APIRouter()


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(default="python", pattern="^(python|javascript|typescript|bash|cpp|c|csharp|java|go|php|ruby|perl)$")
    timeout: Optional[int] = Field(None, ge=1, le=60)
    stdin: Optional[str] = Field(None, max_length=10000)


class CodeExecutionResponse(BaseModel):
    success: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time: Optional[float] = None
    language: str
    execution_id: Optional[str] = None
    timeout_occurred: Optional[bool] = False
    error: Optional[str] = None


class SupportedLanguagesResponse(BaseModel):
    languages: List[Dict[str, Any]]


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute code in secure sandbox environment
    
    Security features:
    - Resource limits (CPU, memory)
    - Execution timeout
    - No network access
    - Isolated file system
    
    Rate limit: 10 executions per minute per user
    """
    try:
        logger.info(f"📋 Code execution request from user: {current_user.username}")
        logger.info(f"   Language: {request.language}")
        logger.info(f"   Code length: {len(request.code)} chars")
        
        # Execute code
        result = sandbox_executor.execute_code(
            code=request.code,
            language=request.language,
            timeout=request.timeout,
            stdin_input=request.stdin
        )
        
        # Check for errors
        if not result.get("success", False) and "error" in result:
            logger.warning(f"⚠️ Execution error: {result['error']}")
        
        return CodeExecutionResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Sandbox API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of supported programming languages
    """
    languages = sandbox_executor.get_supported_languages()
    return SupportedLanguagesResponse(languages=languages)


@router.get("/health")
async def sandbox_health():
    """
    Check sandbox service health
    """
    return {
        "status": "healthy",
        "service": "sandbox",
        "executor": "subprocess",
        "supported_languages": len(sandbox_executor.LANGUAGE_CONFIGS)
    }