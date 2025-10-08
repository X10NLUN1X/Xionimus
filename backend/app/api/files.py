from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import aiofiles
import os
import sys
from pathlib import Path
import logging

# Try to import magic, but make it optional for Windows compatibility
try:
    import magic
    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False
    print("ℹ️ python-magic not available. MIME type detection disabled.")
    print("   For Windows: pip install python-magic-bin")
    print("   For Linux/Mac: pip install python-magic")
    logging.info("ℹ️ python-magic not available - MIME type detection disabled (non-critical)")

from ..core.database import get_db_session as get_database
from ..core.config import settings
from ..models.user_models import UploadedFile
from ..core.auth_middleware import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db = Depends(get_database)
):
    """Upload a file to the platform"""
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Security: Check for path traversal attempts
        if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Validate file extension (whitelist)
        allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.csv', '.json', '.xml', '.md'}
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # SECURITY: Validate MIME type (prevents executable uploads)
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_buffer(content, mime=True)
                logger.info(f"📄 File MIME type detected: {mime_type}")
                
                # Block dangerous MIME types
                dangerous_types = {
                    'application/x-executable',
                    'application/x-dosexec',
                    'application/x-msdos-program',
                    'application/x-msdownload',
                    'application/x-sh',
                    'application/x-shellscript',
                    'text/x-python',  # Python scripts can be dangerous
                    'text/x-sh',
                }
                
                if mime_type in dangerous_types:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File type {mime_type} is not allowed for security reasons"
                    )
            except Exception as e:
                logger.warning(f"⚠️ MIME type detection failed: {e}")
                # Continue anyway if magic fails
        else:
            logger.info("⚠️ MIME type detection skipped (python-magic not available)")
        
        # Sanitize filename (prevent special characters)
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in '._- ')
        if not safe_filename:
            safe_filename = "unnamed_file"
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(safe_filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file with restricted permissions
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Set file permissions (read/write for owner only) - Unix only
        if sys.platform != 'win32':
            os.chmod(file_path, 0o600)
            logger.info(f"✅ File saved with restricted permissions: {file_path}")
        else:
            logger.info(f"✅ File saved: {file_path} (Windows - using default permissions)")
        
        # Save metadata to database using SQLAlchemy
        if db is not None:
            new_file = UploadedFile(
                id=file_id,
                filename=unique_filename,
                original_filename=file.filename or "unknown",
                file_path=str(file_path),
                mime_type=file.content_type,
                file_size=len(content),
                uploaded_at=datetime.now(timezone.utc).isoformat(),
                file_metadata=f'{{"description": "{description or ""}"}}' 
            )
            db.add(new_file)
            db.commit()
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "status": "uploaded",
            "url": f"/uploads/{unique_filename}"
        }
        
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_files(
    db = Depends(get_database),
    limit: int = 100
):
    """List uploaded files"""
    if db is None:
        return []
    
    try:
        # Query using SQLAlchemy
        files = db.query(UploadedFile).order_by(
            UploadedFile.uploaded_at.desc()
        ).limit(limit).all()
        
        # Convert to dict and add download URL
        result = []
        for file in files:
            result.append({
                "file_id": file.id,
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_size": file.file_size,
                "content_type": file.mime_type,
                "uploaded_at": file.uploaded_at,
                "download_url": f"/uploads/{file.filename}"
            })
        
        return result
        
    except Exception as e:
        logger.error(f"List files error: {e}")
        return []

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db = Depends(get_database)
):
    """Delete an uploaded file"""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Find file using SQLAlchemy
        file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete physical file
        file_path = Path(file_record.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        db.delete(file_record)
        db.commit()
        
        return {"status": "deleted", "file_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))