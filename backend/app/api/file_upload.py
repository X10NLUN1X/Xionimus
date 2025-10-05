"""
File Upload API
Upload files directly to workspace/active project
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import logging
from pathlib import Path
import shutil
from datetime import datetime, timezone

from ..core.auth import get_current_user, get_current_user_optional, User
from ..core.database import get_db_session as get_database
from ..models.session_models import Session

logger = logging.getLogger(__name__)
router = APIRouter()

WORKSPACE_ROOT = Path("/app")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file

class UploadResponse(BaseModel):
    """Response after file upload"""
    success: bool
    uploaded_files: List[str]
    target_directory: str
    total_size_mb: float
    message: str


class UploadedFileInfo(BaseModel):
    """Info about uploaded file"""
    filename: str
    path: str
    size_bytes: int
    size_mb: float


@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    target_directory: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Upload files to workspace
    
    - If session_id provided: Upload to active project of that session
    - If target_directory provided: Upload to that directory
    - Otherwise: Upload to 'uploads' directory
    """
    db = None
    try:
        uploaded_files = []
        total_size = 0
        
        # Determine target directory
        if session_id and not target_directory:
            # Get active project from session
            db = get_database()
            session = db.query(Session).filter(Session.id == session_id).first()
            
            if session and session.active_project:
                target_dir = WORKSPACE_ROOT / session.active_project
                logger.info(f"📁 Uploading to active project: {session.active_project}")
            else:
                # No active project, use uploads
                target_dir = WORKSPACE_ROOT / "uploads"
                logger.info("📁 No active project, uploading to /uploads")
        elif target_directory:
            target_dir = WORKSPACE_ROOT / target_directory
            logger.info(f"📁 Uploading to specified directory: {target_directory}")
        else:
            # Default: uploads directory
            target_dir = WORKSPACE_ROOT / "uploads"
            logger.info("📁 Uploading to default /uploads directory")
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate and upload files
        for file in files:
            # Check file size
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Datei '{file.filename}' ist zu groß ({file_size / (1024*1024):.1f}MB). Maximum: 50MB"
                )
            
            # Sanitize filename
            safe_filename = file.filename.replace("..", "").replace("/", "_").replace("\\", "_")
            file_path = target_dir / safe_filename
            
            # Handle duplicate filenames
            counter = 1
            original_stem = file_path.stem
            original_suffix = file_path.suffix
            while file_path.exists():
                file_path = target_dir / f"{original_stem}_{counter}{original_suffix}"
                counter += 1
            
            # Write file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            uploaded_files.append(str(file_path.relative_to(WORKSPACE_ROOT)))
            total_size += file_size
            
            logger.info(f"✅ Uploaded: {file.filename} → {file_path.relative_to(WORKSPACE_ROOT)} ({file_size / 1024:.1f} KB)")
        
        message = f"✅ {len(uploaded_files)} Datei(en) erfolgreich hochgeladen"
        if session_id and session and session.active_project:
            message += f" ins aktive Projekt '{session.active_project}'"
        
        return UploadResponse(
            success=True,
            uploaded_files=uploaded_files,
            target_directory=str(target_dir.relative_to(WORKSPACE_ROOT)),
            total_size_mb=round(total_size / (1024 * 1024), 2),
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload fehlgeschlagen: {str(e)}"
        )
    finally:
        if db:
            db.close()


@router.get("/uploads")
async def list_uploaded_files(
    directory: Optional[str] = None,
    current_user: User = Depends(get_current_user_optional)
):
    """
    List uploaded files in a directory
    """
    try:
        if directory:
            target_dir = WORKSPACE_ROOT / directory
        else:
            target_dir = WORKSPACE_ROOT / "uploads"
        
        if not target_dir.exists():
            return {
                "directory": str(target_dir.relative_to(WORKSPACE_ROOT)),
                "files": [],
                "total_files": 0,
                "total_size_mb": 0
            }
        
        files_info = []
        total_size = 0
        
        for file_path in target_dir.iterdir():
            if file_path.is_file():
                file_size = file_path.stat().st_size
                files_info.append({
                    "filename": file_path.name,
                    "path": str(file_path.relative_to(WORKSPACE_ROOT)),
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                total_size += file_size
        
        return {
            "directory": str(target_dir.relative_to(WORKSPACE_ROOT)),
            "files": files_info,
            "total_files": len(files_info),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/uploads/{filename}")
async def delete_uploaded_file(
    filename: str,
    directory: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an uploaded file
    """
    try:
        if directory:
            target_dir = WORKSPACE_ROOT / directory
        else:
            target_dir = WORKSPACE_ROOT / "uploads"
        
        file_path = target_dir / filename
        
        # Security check
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(WORKSPACE_ROOT)):
            raise HTTPException(status_code=400, detail="Ungültiger Pfad")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Datei nicht gefunden")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Pfad ist keine Datei")
        
        file_path.unlink()
        
        logger.info(f"🗑️ Deleted: {file_path.relative_to(WORKSPACE_ROOT)}")
        
        return {
            "success": True,
            "message": f"✅ Datei '{filename}' gelöscht"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
