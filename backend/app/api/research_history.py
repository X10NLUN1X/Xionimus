"""
Research History API
Endpoints for managing research history with MongoDB storage and PDF export
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
import io

from app.models.research_models import (
    ResearchHistoryItem,
    ResearchHistoryCreate,
    ResearchHistoryResponse,
    BulkExportRequest
)
from app.core.auth import get_current_user
from app.core.auth import User
from app.core.pdf_generator import PDFGenerator
from app.core.mongo_db import get_database

router = APIRouter(prefix="/research", tags=["research_history"])


@router.post("/save", response_model=ResearchHistoryResponse)
async def save_research(
    research_data: ResearchHistoryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Save research result to history (MongoDB + returns data for localStorage backup)
    """
    try:
        db = get_database()
        
        # Create research history item
        research_item = ResearchHistoryItem(
            user_id=current_user.user_id,
            query=research_data.query,
            result=research_data.result,
            duration_seconds=research_data.duration_seconds,
            token_usage=research_data.token_usage,
            is_favorite=False
        )
        
        # Convert to dict for MongoDB
        item_dict = research_item.dict()
        
        # Insert into MongoDB
        result = await db.research_history.insert_one(item_dict)
        
        # Return the created item
        return ResearchHistoryResponse(**item_dict)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save research: {str(e)}")


@router.get("/history", response_model=List[ResearchHistoryResponse])
async def get_research_history(
    limit: int = 50,
    skip: int = 0,
    favorites_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Get research history for current user
    """
    try:
        db = get_database()
        
        # Build query
        query = {"user_id": current_user.user_id}
        if favorites_only:
            query["is_favorite"] = True
        
        # Fetch from MongoDB
        cursor = db.research_history.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        
        # Convert to response models
        return [ResearchHistoryResponse(**item) for item in items]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.delete("/history/{research_id}")
async def delete_research(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a research item from history
    """
    try:
        db = get_database()
        
        # Verify ownership and delete
        result = await db.research_history.delete_one({
            "id": research_id,
            "user_id": current_user.user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Research not found or unauthorized")
        
        return {"message": "Research deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete research: {str(e)}")


@router.patch("/history/{research_id}/favorite")
async def toggle_favorite(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Toggle favorite status for a research item
    """
    try:
        db = get_database()
        
        # Find the item
        item = await db.research_history.find_one({
            "id": research_id,
            "user_id": current_user.user_id
        })
        
        if not item:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Toggle favorite
        new_favorite_status = not item.get("is_favorite", False)
        
        await db.research_history.update_one(
            {"id": research_id, "user_id": current_user.user_id},
            {"$set": {"is_favorite": new_favorite_status}}
        )
        
        return {"is_favorite": new_favorite_status}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {str(e)}")


@router.get("/history/{research_id}/export-pdf")
async def export_research_pdf(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Export a single research item as PDF
    Note: Requires WeasyPrint with GTK libraries (not available on Windows by default)
    """
    try:
        db = get_database()
        
        # Fetch the research item
        item = await db.research_history.find_one({
            "id": research_id,
            "user_id": current_user.user_id
        })
        
        if not item:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        result = item.get('result', {})
        
        pdf_bytes = pdf_generator.generate_research_pdf(
            query=item.get('query', 'No query'),
            content=result.get('content', ''),
            citations=result.get('citations', []),
            sources_count=result.get('sources_count', 0),
            related_questions=result.get('related_questions'),
            model_used=result.get('model_used'),
            duration_seconds=item.get('duration_seconds'),
            timestamp=item.get('timestamp')
        )
        
        # Return as downloadable PDF
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=research-{research_id[:8]}.pdf"
            }
        )
    
    except HTTPException:
        raise
    except RuntimeError as e:
        # WeasyPrint not available
        raise HTTPException(
            status_code=501,
            detail=f"PDF export not available on this system: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.post("/export-bulk-pdf")
async def export_bulk_pdf(
    export_request: BulkExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Export multiple research items as a single PDF
    Note: Requires WeasyPrint with GTK libraries (not available on Windows by default)
    """
    try:
        db = get_database()
        
        # Fetch all requested research items
        items = []
        for research_id in export_request.research_ids:
            item = await db.research_history.find_one({
                "id": research_id,
                "user_id": current_user.user_id
            })
            if item:
                items.append(item)
        
        if not items:
            raise HTTPException(status_code=404, detail="No research items found")
        
        # Generate bulk PDF
        pdf_generator = PDFGenerator()
        pdf_bytes = pdf_generator.generate_bulk_research_pdf(
            research_items=items,
            title=export_request.title,
            include_sources=export_request.include_sources,
            include_metadata=export_request.include_metadata
        )
        
        # Return as downloadable PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=research-export-{timestamp}.pdf"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate bulk PDF: {str(e)}")


@router.get("/stats")
async def get_research_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get research statistics for current user
    """
    try:
        db = get_database()
        
        # Count total queries
        total_queries = await db.research_history.count_documents({"user_id": current_user.user_id})
        
        # Count favorites
        favorites_count = await db.research_history.count_documents({
            "user_id": current_user.user_id,
            "is_favorite": True
        })
        
        # Aggregate statistics
        pipeline = [
            {"$match": {"user_id": current_user.user_id}},
            {"$group": {
                "_id": None,
                "total_sources": {"$sum": "$result.sources_count"},
                "total_tokens": {"$sum": "$token_usage.total_tokens"}
            }}
        ]
        
        agg_result = await db.research_history.aggregate(pipeline).to_list(length=1)
        stats = agg_result[0] if agg_result else {"total_sources": 0, "total_tokens": 0}
        
        return {
            "total_queries": total_queries,
            "favorites": favorites_count,
            "total_sources": stats.get("total_sources", 0),
            "total_tokens": stats.get("total_tokens", 0),
            "average_sources_per_query": stats.get("total_sources", 0) / total_queries if total_queries > 0 else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
