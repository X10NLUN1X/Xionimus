"""
Clipboard Assistant API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from ..core.clipboard_manager import ClipboardManager

router = APIRouter(prefix="/api/clipboard", tags=["clipboard"])
logger = logging.getLogger(__name__)

# Initialize clipboard manager
clipboard_manager = ClipboardManager()

class AddClipboardRequest(BaseModel):
    content: str
    content_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None

class TransformRequest(BaseModel):
    item_id: str
    transformation: str
    ai_result: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 20

@router.post("/add")
async def add_clipboard_item(request: AddClipboardRequest):
    """Add item to clipboard history"""
    try:
        item = clipboard_manager.add_item(
            content=request.content,
            content_type=request.content_type,
            metadata=request.metadata
        )
        return {
            "status": "success",
            "item": item
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding clipboard item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_clipboard_history(
    limit: int = 50,
    content_type: Optional[str] = None
):
    """Get clipboard history"""
    history = clipboard_manager.get_history(limit=limit, content_type=content_type)
    return {
        "status": "success",
        "history": history,
        "count": len(history)
    }

@router.get("/item/{item_id}")
async def get_clipboard_item(item_id: str):
    """Get specific clipboard item"""
    item = clipboard_manager.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {
        "status": "success",
        "item": item
    }

@router.delete("/item/{item_id}")
async def delete_clipboard_item(item_id: str):
    """Delete clipboard item"""
    success = clipboard_manager.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {
        "status": "success",
        "message": "Item deleted"
    }

@router.delete("/clear")
async def clear_clipboard():
    """Clear all clipboard history"""
    count = clipboard_manager.clear_history()
    return {
        "status": "success",
        "message": f"Cleared {count} items"
    }

@router.post("/search")
async def search_clipboard(request: SearchRequest):
    """Search clipboard history"""
    results = clipboard_manager.search(request.query, request.limit)
    return {
        "status": "success",
        "query": request.query,
        "results": results,
        "count": len(results)
    }

@router.post("/transform")
async def transform_clipboard(request: TransformRequest):
    """Store AI transformation result"""
    try:
        item = clipboard_manager.transform_content(
            item_id=request.item_id,
            transformation=request.transformation,
            ai_result=request.ai_result
        )
        return {
            "status": "success",
            "item": item,
            "message": "Transformation saved"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error transforming clipboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/favorites")
async def get_favorites(threshold: int = 3):
    """Get frequently accessed clipboard items"""
    favorites = clipboard_manager.get_favorites(threshold=threshold)
    return {
        "status": "success",
        "favorites": favorites,
        "count": len(favorites)
    }

@router.get("/stats")
async def get_clipboard_stats():
    """Get clipboard manager statistics"""
    return clipboard_manager.get_stats()