"""
File Tools API - Advanced File Search (Glob & Grep)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from ..core.file_tools import file_tools

logger = logging.getLogger(__name__)
router = APIRouter()

class GlobRequest(BaseModel):
    pattern: str
    base_path: Optional[str] = None

class GrepRequest(BaseModel):
    pattern: str
    path: Optional[str] = None
    file_pattern: Optional[str] = None
    case_sensitive: bool = False
    context_lines: int = 0

@router.post("/glob")
async def glob_search(request: GlobRequest) -> Dict[str, Any]:
    """
    Find files matching glob pattern
    Examples: **/*.py, src/**/*.tsx, *.json
    """
    try:
        result = await file_tools.glob_files(
            pattern=request.pattern,
            base_path=request.base_path
        )
        
        # Generate report
        report = file_tools.generate_search_report(result, "glob")
        result['report'] = report
        
        return result
        
    except Exception as e:
        logger.error(f"Glob error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grep")
async def grep_search(request: GrepRequest) -> Dict[str, Any]:
    """
    Search for pattern in file contents
    """
    try:
        result = await file_tools.grep_content(
            pattern=request.pattern,
            path=request.path,
            file_pattern=request.file_pattern,
            case_sensitive=request.case_sensitive,
            context_lines=request.context_lines
        )
        
        # Generate report
        report = file_tools.generate_search_report(result, "search")
        result['report'] = report
        
        return result
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/glob")
async def glob_search_get(
    pattern: str = Query(..., description="Glob pattern (e.g., **/*.py)"),
    base_path: Optional[str] = Query(None, description="Base path to search from")
) -> Dict[str, Any]:
    """
    Find files matching glob pattern (GET method)
    """
    return await glob_search(GlobRequest(pattern=pattern, base_path=base_path))

@router.get("/grep")
async def grep_search_get(
    pattern: str = Query(..., description="Search pattern"),
    path: Optional[str] = Query(None, description="Path to search in"),
    file_pattern: Optional[str] = Query(None, description="File pattern filter"),
    case_sensitive: bool = Query(False, description="Case sensitive search"),
    context_lines: int = Query(0, description="Number of context lines")
) -> Dict[str, Any]:
    """
    Search for pattern in file contents (GET method)
    """
    return await grep_search(GrepRequest(
        pattern=pattern,
        path=path,
        file_pattern=file_pattern,
        case_sensitive=case_sensitive,
        context_lines=context_lines
    ))
