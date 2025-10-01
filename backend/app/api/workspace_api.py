"""
Workspace Management API endpoints
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
import io
from pathlib import Path

from ..core.workspace_manager import WorkspaceManager

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])
logger = logging.getLogger(__name__)

# Initialize workspace manager
workspace_manager = WorkspaceManager()

# Xionimus AI code workspace path
XIONIMUS_WORKSPACE = Path("/app/xionimus-ai")

class CreateWorkspaceRequest(BaseModel):
    name: str
    template: Optional[str] = None
    description: str = ""

@router.get("/")
async def list_workspaces():
    """List all workspaces"""
    return {
        "status": "success",
        "workspaces": workspace_manager.list_workspaces()
    }

@router.post("/create")
async def create_workspace(request: CreateWorkspaceRequest):
    """Create a new workspace"""
    try:
        workspace = workspace_manager.create_workspace(
            name=request.name,
            template=request.template,
            description=request.description
        )
        return {
            "status": "success",
            "workspace": workspace
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workspace_id}")
async def get_workspace(workspace_id: str):
    """Get workspace details"""
    workspace = workspace_manager.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return {
        "status": "success",
        "workspace": workspace
    }

@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    """Delete a workspace"""
    success = workspace_manager.delete_workspace(workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return {
        "status": "success",
        "message": f"Workspace {workspace_id} deleted"
    }

@router.get("/{workspace_id}/files")
async def get_workspace_files(workspace_id: str):
    """Get all files in workspace"""
    files = workspace_manager.get_workspace_files(workspace_id)
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "files": files,
        "count": len(files)
    }

@router.get("/{workspace_id}/export")
async def export_workspace(workspace_id: str):
    """Export workspace as ZIP"""
    try:
        zip_data = workspace_manager.export_workspace(workspace_id)
        
        return StreamingResponse(
            io.BytesIO(zip_data),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={workspace_id}.zip"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_workspace(
    name: str,
    file: UploadFile = File(...),
    description: str = ""
):
    """Import workspace from ZIP"""
    try:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="File must be a ZIP archive")
        
        zip_data = await file.read()
        workspace = workspace_manager.import_workspace(name, zip_data, description)
        
        return {
            "status": "success",
            "workspace": workspace,
            "message": f"Workspace '{name}' imported successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/list")
async def list_templates():
    """List available workspace templates"""
    return {
        "status": "success",
        "templates": workspace_manager.get_templates()
    }

@router.get("/stats")
async def get_workspace_stats():
    """Get workspace manager statistics"""
    return workspace_manager.get_stats()