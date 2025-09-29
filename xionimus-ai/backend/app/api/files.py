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
        # Validate file size
        content = await file.read()
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
        
        # Save metadata to database
        file_data = {
            "file_id": file_id,
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "content_type": file.content_type,
            "description": description,
            "uploaded_at": datetime.now(timezone.utc)
        }
        
        if db is not None:
            await db.uploaded_files.insert_one(file_data)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "status": "uploaded",
            "url": f"/uploads/{unique_filename}"
        }
        
    except Exception as e:
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
        cursor = db.uploaded_files.find().sort("uploaded_at", -1).limit(limit)
        files = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string and add download URL
        for file in files:
            file["_id"] = str(file["_id"])
            file["download_url"] = f"/uploads/{file['stored_filename']}"
        
        return files
        
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
        # Find file
        file_doc = await db.uploaded_files.find_one({"file_id": file_id})
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete physical file
        file_path = Path(file_doc["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        await db.uploaded_files.delete_one({"file_id": file_id})
        
        return {"status": "deleted", "file_id": file_id}
        
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))