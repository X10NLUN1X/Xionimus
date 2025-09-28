from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any
from core.database import get_database
import uuid
from datetime import datetime
import aiofiles
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db = Depends(get_database)
) -> Dict[str, Any]:
    """Upload a file"""
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Save metadata to database
        file_data = {
            "file_id": file_id,
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "content_type": file.content_type,
            "uploaded_at": datetime.utcnow()
        }
        
        await db.uploaded_files.insert_one(file_data)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "status": "uploaded"
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_files(
    db = Depends(get_database)
) -> List[Dict[str, Any]]:
    """List all uploaded files"""
    try:
        cursor = db.uploaded_files.find().sort("uploaded_at", -1)
        files = await cursor.to_list(length=100)
        
        # Convert ObjectId to string
        for file in files:
            file["_id"] = str(file["_id"])
        
        return files
        
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db = Depends(get_database)
) -> Dict[str, str]:
    """Delete a file"""
    try:
        # Find file in database
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