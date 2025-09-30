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

WORKSPACE_DIR = Path(settings.WORKSPACE_DIR)
WORKSPACE_DIR.mkdir(exist_ok=True)


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
        full_path = WORKSPACE_DIR / file_path
        
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
        full_path = WORKSPACE_DIR / file_path
        
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
        full_path = WORKSPACE_DIR / dir_path
        
        full_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "status": "created",
            "path": dir_path,
            "type": "directory"
        }
        
    except Exception as e:
        logger.error(f"Create directory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))