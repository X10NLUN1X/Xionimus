"""
Bulk File API - Multi-File Operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

from ..core.bulk_file_manager import bulk_file_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class FileContent(BaseModel):
    path: str
    content: str

class BulkWriteRequest(BaseModel):
    files: List[FileContent]
    create_backups: bool = False

class BulkReadRequest(BaseModel):
    file_paths: List[str]

@router.post("/write")
async def bulk_write(request: BulkWriteRequest) -> Dict[str, Any]:
    """
    Write multiple files simultaneously (max 20 files)
    """
    try:
        files_data = [
            {'path': f.path, 'content': f.content}
            for f in request.files
        ]
        
        result = await bulk_file_manager.bulk_write(
            files=files_data,
            create_backups=request.create_backups
        )
        
        # Generate report
        report = bulk_file_manager.generate_bulk_report(result, "write")
        result['report'] = report
        
        return result
        
    except Exception as e:
        logger.error(f"Bulk write error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read")
async def bulk_read(request: BulkReadRequest) -> Dict[str, Any]:
    """
    Read multiple files simultaneously (max 20 files)
    """
    try:
        result = await bulk_file_manager.bulk_read(request.file_paths)
        
        # Generate report
        report = bulk_file_manager.generate_bulk_report(result, "read")
        result['report'] = report
        
        return result
        
    except Exception as e:
        logger.error(f"Bulk read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/limits")
async def get_limits():
    """
    Get bulk operation limits
    """
    return {
        'max_files': bulk_file_manager.MAX_FILES,
        'operations': ['write', 'read']
    }
