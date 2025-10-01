"""
Code Review API Endpoints
MVP version with file upload and review management
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import logging
from datetime import datetime, timezone

from ..core.database import get_database
from ..core.code_review_agents import AgentManager
from ..models.code_review_models import CodeReview, ReviewFinding
from sqlalchemy import desc

router = APIRouter()
logger = logging.getLogger(__name__)


class ReviewRequest(BaseModel):
    """Request model for code review"""
    title: str
    code: str
    file_path: Optional[str] = None
    language: Optional[str] = "python"
    review_scope: str = "full"  # full, code_analysis, debug
    api_keys: Dict[str, str]


class ReviewResponse(BaseModel):
    """Response model for review status"""
    review_id: str
    status: str
    message: str


@router.post("/review/submit", response_model=ReviewResponse)
async def submit_code_review(
    request: ReviewRequest, 
    db=Depends(get_database)
):
    """Submit code for review
    
    Rate limit: 10 reviews per minute per IP (AI cost protection, configured in main.py)
    """
    try:
        review_id = str(uuid.uuid4())
        
        # Create review record
        review = CodeReview(
            id=review_id,
            title=request.title,
            review_type="manual_submission",
            source_type="code_snippet",
            source_path=request.file_path,
            review_scope=request.review_scope,
            status="in_progress"
        )
        
        db.add(review)
        db.commit()
        
        logger.info(f"📝 Starting review {review_id}")
        
        # Run review agents
        agent_manager = AgentManager()
        context = {
            "file_path": request.file_path or "code_snippet",
            "language": request.language
        }
        
        results = await agent_manager.coordinate_review(
            code=request.code,
            context=context,
            api_keys=request.api_keys,
            review_scope=request.review_scope
        )
        
        # Save findings
        for finding_data in results.get("all_findings", []):
            finding = ReviewFinding(
                id=str(uuid.uuid4()),
                review_id=review_id,
                agent_name=finding_data.get("agent_name"),
                severity=finding_data.get("severity"),
                category=finding_data.get("category"),
                title=finding_data.get("title"),
                description=finding_data.get("description"),
                file_path=finding_data.get("file_path"),
                line_number=finding_data.get("line_number"),
                recommendation=finding_data.get("recommendation"),
                fix_code=finding_data.get("fix_code")
            )
            db.add(finding)
        
        # Update review status
        summary = results.get("summary", {})
        review.status = "completed"
        review.critical_issues = summary.get("critical", 0)
        review.high_issues = summary.get("high", 0)
        review.medium_issues = summary.get("medium", 0)
        review.low_issues = summary.get("low", 0)
        review.quality_score = results.get("agents", {}).get("code_analysis", {}).get("quality_score")
        review.summary = f"Found {summary.get('total_findings', 0)} issues"
        review.completed_at = datetime.now(timezone.utc).isoformat()
        
        db.commit()
        
        logger.info(f"✅ Review {review_id} completed: {summary.get('total_findings', 0)} findings")
        
        return ReviewResponse(
            review_id=review_id,
            status="completed",
            message=f"Review completed. Found {summary.get('total_findings', 0)} issues."
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Review error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{review_id}")
async def get_review(review_id: str, db=Depends(get_database)):
    """Get review details and findings"""
    try:
        review = db.query(CodeReview).filter(CodeReview.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        findings = db.query(ReviewFinding).filter(ReviewFinding.review_id == review_id).all()
        
        return {
            "review": {
                "id": review.id,
                "title": review.title,
                "status": review.status,
                "review_scope": review.review_scope,
                "quality_score": review.quality_score,
                "summary": review.summary,
                "critical_issues": review.critical_issues,
                "high_issues": review.high_issues,
                "medium_issues": review.medium_issues,
                "low_issues": review.low_issues,
                "created_at": review.created_at,
                "completed_at": review.completed_at
            },
            "findings": [
                {
                    "id": f.id,
                    "agent_name": f.agent_name,
                    "severity": f.severity,
                    "category": f.category,
                    "title": f.title,
                    "description": f.description,
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "recommendation": f.recommendation,
                    "fix_code": f.fix_code
                }
                for f in findings
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get review error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews")
async def list_reviews(limit: int = 20, offset: int = 0, db=Depends(get_database)):
    """List all code reviews"""
    try:
        reviews = db.query(CodeReview).order_by(desc(CodeReview.created_at)).limit(limit).offset(offset).all()
        
        return {
            "reviews": [
                {
                    "id": r.id,
                    "title": r.title,
                    "status": r.status,
                    "quality_score": r.quality_score,
                    "total_issues": r.critical_issues + r.high_issues + r.medium_issues + r.low_issues,
                    "critical_issues": r.critical_issues,
                    "created_at": r.created_at,
                    "completed_at": r.completed_at
                }
                for r in reviews
            ],
            "total": len(reviews),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"List reviews error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/review/{review_id}")
async def delete_review(review_id: str, db=Depends(get_database)):
    """Delete a code review"""
    try:
        review = db.query(CodeReview).filter(CodeReview.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Delete findings
        db.query(ReviewFinding).filter(ReviewFinding.review_id == review_id).delete()
        
        # Delete review
        db.delete(review)
        db.commit()
        
        return {"success": True, "message": "Review deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Delete review error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/upload")
async def upload_file_review(
    file: UploadFile = File(...),
    title: str = Form(...),
    review_scope: str = Form("full"),
    openai_key: Optional[str] = Form(None),
    anthropic_key: Optional[str] = Form(None),
    db=Depends(get_database)
):
    """Upload file for review"""
    try:
        # Read file content
        content = await file.read()
        code = content.decode('utf-8')
        
        # Detect language from file extension
        language = "python"
        if file.filename.endswith('.js') or file.filename.endswith('.jsx'):
            language = "javascript"
        elif file.filename.endswith('.ts') or file.filename.endswith('.tsx'):
            language = "typescript"
        elif file.filename.endswith('.java'):
            language = "java"
        
        # Build API keys
        api_keys = {}
        if openai_key:
            api_keys['openai'] = openai_key
        if anthropic_key:
            api_keys['anthropic'] = anthropic_key
        
        # Create review request
        request = ReviewRequest(
            title=title or file.filename,
            code=code,
            file_path=file.filename,
            language=language,
            review_scope=review_scope,
            api_keys=api_keys
        )
        
        # Submit for review
        return await submit_code_review(request, db)
        
    except Exception as e:
        logger.error(f"File upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
