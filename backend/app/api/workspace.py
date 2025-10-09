from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import os
import aiofiles
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Get workspace directory (Windows + Linux compatible via settings property)
WORKSPACE_DIR = settings.WORKSPACE_DIR
logger.info(f"📁 Workspace directory: {WORKSPACE_DIR}")


def validate_path(user_path: str) -> Path:
    """
    Validate that the user-provided path is within WORKSPACE_DIR
    and prevent path traversal attacks
    """
    try:
        # Join with workspace dir and resolve to absolute path
        full_path = (WORKSPACE_DIR / user_path).resolve()
        
        # Check if the resolved path is within workspace directory
        if not str(full_path).startswith(str(WORKSPACE_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access denied: Path traversal detected")
        
        return full_path
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid path")

@router.get("/tree")
async def get_workspace_tree(path: str = ""):
    """Get workspace directory tree"""
    try:
        base_path = validate_path(path) if path else WORKSPACE_DIR
        
        if not base_path.exists() or not base_path.is_dir():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        tree = []
        for item in base_path.iterdir():
            item_data = {
                "name": item.name,
                "path": str(item.relative_to(WORKSPACE_DIR)),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            }
            
            if item.is_file():
                item_data["extension"] = item.suffix
            
            tree.append(item_data)
        
        return sorted(tree, key=lambda x: (x["type"] == "file", x["name"]))
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Get workspace tree error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{file_path:path}")
async def get_file_content(file_path: str):
    """Get content of a workspace file"""
    try:
        full_path = validate_path(file_path)
        
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if file is too large
        if full_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit for text files
            raise HTTPException(status_code=413, detail="File too large to display")
        
        async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        return {
            "path": file_path,
            "content": content,
            "size": full_path.stat().st_size,
            "extension": full_path.suffix,
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=415, detail="File is not text-readable")
    except Exception as e:
        logger.error(f"Get file content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file/{file_path:path}")
async def save_file_content(
    file_path: str,
    content: Dict[str, str]
):
    """Save content to a workspace file"""
    try:
        full_path = validate_path(file_path)
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
            await f.write(content["content"])
        
        return {
            "status": "saved",
            "path": file_path,
            "size": len(content["content"].encode('utf-8'))
        }
        
    except Exception as e:
        logger.error(f"Save file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{file_path:path}")
async def delete_workspace_file(file_path: str):
    """Delete a workspace file"""
    try:
        full_path = validate_path(file_path)
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if full_path.is_dir():
            # For directories, only delete if empty
            if any(full_path.iterdir()):
                raise HTTPException(status_code=400, detail="Directory not empty")
            full_path.rmdir()
        else:
            full_path.unlink()
        
        return {"status": "deleted", "path": file_path}
        
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/directory")
async def create_directory(
    data: Dict[str, str]
):
    """Create a new directory in workspace"""
    try:
        dir_path = data.get("path", "")
        full_path = validate_path(dir_path)
        
        full_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "status": "created",
            "path": dir_path,
            "type": "directory"
        }
        
    except Exception as e:
        logger.error(f"Create directory error: {e}")

        raise HTTPException(status_code=500, detail=str(e))


# ==================== Active Project Management ====================

from pydantic import BaseModel
from typing import Optional
from ..core.auth import get_current_user_optional, User
from ..core.database import get_db_session as get_database
from ..models.session_models import Session

WORKSPACE_ROOT = Path("/app")


class SetActiveProjectRequest(BaseModel):
    """Request to set active project for a session"""
    session_id: str
    project_name: str
    branch: Optional[str] = None


class ActiveProjectInfo(BaseModel):
    """Active project information"""
    project_name: Optional[str]
    project_path: Optional[str]
    branch: Optional[str]
    file_count: Optional[int]
    size_mb: Optional[float]
    exists: bool


@router.post("/active-project")
async def set_active_project(
    request: SetActiveProjectRequest,
    current_user: User = Depends(get_current_user_optional)
):
    """Set the active project for a session - makes it available to AI agents"""
    try:
        db = get_database()
        
        # Get session
        session = db.query(Session).filter(Session.id == request.session_id).first()
        if not session:
            db.close()
            raise HTTPException(status_code=404, detail=f"Session '{request.session_id}' not found")
        
        # Verify project exists
        project_path = WORKSPACE_ROOT / request.project_name
        if not project_path.exists():
            db.close()
            raise HTTPException(status_code=404, detail=f"❌ Projekt '{request.project_name}' nicht im Workspace gefunden")
        
        # Update session with active project
        session.active_project = request.project_name
        session.active_project_branch = request.branch
        db.commit()
        
        # Get project info
        file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in project_path.rglob('*') if f.is_file())
        
        db.close()
        
        logger.info(f"Set active project for session {request.session_id}: {request.project_name}")
        
        return {
            "success": True,
            "message": f"✅ Projekt '{request.project_name}' ist jetzt aktiv und für KI-Agenten verfügbar",
            "project": {
                "name": request.project_name,
                "path": str(project_path),
                "branch": request.branch,
                "file_count": file_count,
                "size_mb": round(total_size / (1024 * 1024), 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set active project: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Setzen des aktiven Projekts: {str(e)}")


@router.get("/active-project/{session_id}")
async def get_active_project(
    session_id: str,
    current_user: User = Depends(get_current_user_optional)
) -> ActiveProjectInfo:
    """Get the active project for a session"""
    try:
        db = get_database()
        
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            db.close()
            return ActiveProjectInfo(
                project_name=None, project_path=None, branch=None,
                file_count=None, size_mb=None, exists=False
            )
        
        active_project = session.active_project
        active_branch = session.active_project_branch
        db.close()
        
        if not active_project:
            return ActiveProjectInfo(
                project_name=None, project_path=None, branch=None,
                file_count=None, size_mb=None, exists=False
            )
        
        # Check if project still exists
        project_path = WORKSPACE_ROOT / active_project
        if not project_path.exists():
            return ActiveProjectInfo(
                project_name=active_project, project_path=str(project_path),
                branch=active_branch, file_count=None, size_mb=None, exists=False
            )
        
        # Get project info
        file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in project_path.rglob('*') if f.is_file())
        
        return ActiveProjectInfo(
            project_name=active_project, project_path=str(project_path),
            branch=active_branch, file_count=file_count,
            size_mb=round(total_size / (1024 * 1024), 2), exists=True
        )
        
    except Exception as e:
        logger.error(f"Failed to get active project: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des aktiven Projekts: {str(e)}")


@router.get("/context/{session_id}")
async def get_workspace_context(
    session_id: str,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Get complete workspace context for AI agents
    Includes active project info and workspace structure
    """
    try:
        db = get_database()
        
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            db.close()
            raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
        
        active_project = session.active_project
        active_branch = session.active_project_branch
        db.close()
        
        context = {
            "workspace_root": str(WORKSPACE_ROOT),
            "active_project": None,
            "available_projects": []
        }
        
        # Get active project details
        if active_project:
            project_path = WORKSPACE_ROOT / active_project
            if project_path.exists():
                files = []
                directories = []
                for item in project_path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    if item.is_file():
                        files.append(item.name)
                    elif item.is_dir():
                        directories.append(item.name)
                
                context["active_project"] = {
                    "name": active_project,
                    "path": str(project_path),
                    "branch": active_branch,
                    "directories": sorted(directories),
                    "files": sorted(files),
                    "file_count": sum(1 for _ in project_path.rglob('*') if _.is_file())
                }
        
        # List all available projects
        if WORKSPACE_ROOT.exists():
            for item in WORKSPACE_ROOT.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    context["available_projects"].append(item.name)
        
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workspace context: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Workspace-Kontexts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))