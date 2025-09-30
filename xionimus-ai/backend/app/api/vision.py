"""
Vision Expert API - AI Image Selection
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from ..core.vision_expert import vision_expert

logger = logging.getLogger(__name__)
router = APIRouter()

class ImageSearchRequest(BaseModel):
    problem_statement: str
    search_keywords: List[str]
    count: int = 5
    color: Optional[str] = None

@router.post("/search")
async def search_images(request: ImageSearchRequest) -> Dict[str, Any]:
    """
    Search for relevant images based on keywords
    """
    try:
        result = await vision_expert.search_images(
            keywords=request.search_keywords,
            count=request.count,
            color=request.color
        )
        
        # Generate report
        report = vision_expert.generate_image_report(result)
        result['report'] = report
        
        return result
        
    except Exception as e:
        logger.error(f"Image search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_needs(problem_statement: str, context: str = "") -> Dict[str, Any]:
    """
    Analyze what kind of images are needed
    """
    try:
        result = vision_expert.analyze_image_needs(
            problem_statement=problem_statement,
            context=context
        )
        return result
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
