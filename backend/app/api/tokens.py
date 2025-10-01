"""
Token Usage API
Endpoints for token tracking and usage statistics
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..core.token_tracker import token_tracker

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats")
async def get_token_stats() -> Dict[str, Any]:
    """
    Get current token usage statistics and recommendations
    
    Returns:
    - Current session usage
    - Limits and percentages
    - Fork/summary recommendations
    - All-time usage
    """
    try:
        stats = token_tracker.get_usage_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get token stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_session_tokens() -> Dict[str, str]:
    """
    Reset current session token counters
    Use this after forking or creating a summary
    """
    try:
        # Save current session to total before reset
        if token_tracker.current_session.get('total_tokens', 0) > 0:
            token_tracker.total_usage['all_time_tokens'] += token_tracker.current_session['total_tokens']
            token_tracker.total_usage['sessions_count'] += 1
        
        token_tracker.reset_session()
        token_tracker.save_usage()
        
        logger.info("✅ Session token counters reset")
        
        return {
            "status": "success",
            "message": "Session token counters have been reset"
        }
    except Exception as e:
        logger.error(f"Failed to reset tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendation")
async def get_fork_recommendation() -> Dict[str, Any]:
    """
    Get specific recommendation about forking/summary
    """
    try:
        stats = token_tracker.get_usage_stats()
        recommendation = stats['recommendation']
        
        return {
            "should_fork": token_tracker.should_recommend_fork(),
            "current_tokens": stats['current_session']['total_tokens'],
            "recommendation": recommendation,
            "tips": {
                "fork": "Create a fork to start fresh while preserving conversation history",
                "summary": "Generate a summary to condense information and reduce context size",
                "continue": "Continue if under soft limit and conversation is coherent"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
