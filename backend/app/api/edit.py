"""
Edit Agent API - User-directed code editing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..core.edit_agent import edit_agent

logger = logging.getLogger(__name__)
router = APIRouter()


class EditFileRequest(BaseModel):
    """Request to edit a single file"""
    file_path: str = Field(..., description="Path to file relative to workspace")
    instructions: str = Field(..., min_length=10, description="Edit instructions")
    workspace_path: Optional[str] = Field(None, description="Custom workspace path")


class BatchEditRequest(BaseModel):
    """Request to edit multiple files"""
    edits: List[Dict[str, str]] = Field(..., description="List of edit requests")
    workspace_path: Optional[str] = Field(None, description="Custom workspace path")


class AnalyzeWorkspaceRequest(BaseModel):
    """Request to analyze workspace for potential edits"""
    workspace_path: Optional[str] = Field(None, description="Custom workspace path")


@router.post("/file")
async def edit_file(request: EditFileRequest) -> Dict[str, Any]:
    """
    Edit a specific file based on natural language instructions
    
    Example:
    {
        "file_path": "backend/app/core/ai_manager.py",
        "instructions": "Fix the bug where temperature is being passed incorrectly"
    }
    """
    try:
        logger.info(f"📝 API: Edit request for {request.file_path}")
        
        result = await edit_agent.user_directed_edit(
            file_path=request.file_path,
            edit_instructions=request.instructions,
            workspace_path=request.workspace_path
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Edit file API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_edit(request: BatchEditRequest) -> Dict[str, Any]:
    """
    Edit multiple files in a single request
    
    Example:
    {
        "edits": [
            {"file": "backend/app/api/chat.py", "instructions": "Remove unused imports"},
            {"file": "frontend/src/App.tsx", "instructions": "Fix PropTypes warning"}
        ]
    }
    """
    try:
        logger.info(f"📝 API: Batch edit request for {len(request.edits)} files")
        
        result = await edit_agent.batch_edit(
            edit_requests=request.edits,
            workspace_path=request.workspace_path
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Batch edit API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_workspace(request: AnalyzeWorkspaceRequest) -> Dict[str, Any]:
    """
    Analyze workspace and suggest potential edits without applying them
    
    Returns suggestions that can be reviewed before applying
    """
    try:
        logger.info("🔍 API: Analyzing workspace for potential edits")
        
        result = await edit_agent.analyze_and_suggest_edits(
            workspace_path=request.workspace_path
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Analyze workspace API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get Edit Agent status and capabilities
    """
    return {
        "status": "active",
        "agent": "Edit Agent",
        "version": "1.0.0",
        "capabilities": [
            "User-directed file editing",
            "Autonomous bug fixing from code review",
            "Batch file editing",
            "Workspace analysis and suggestions",
            "Multi-language support (Python, JS, TS, HTML, CSS)"
        ],
        "supported_languages": [
            "Python (.py)",
            "JavaScript (.js, .jsx)",
            "TypeScript (.ts, .tsx)",
            "HTML (.html)",
            "CSS (.css)",
            "JSON (.json)",
            "YAML (.yaml, .yml)",
            "Markdown (.md)"
        ]
    }
