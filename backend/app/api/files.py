from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import aiofiles
import os
from pathlib import Path
import logging

from ..core.database import get_database
from ..core.config import settings
from ..models.user_models import UploadedFile

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
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename or "").suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
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