"""
Developer Modes API - Phase 2
Provides information about Junior and Senior Developer modes
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from ..core.developer_mode import developer_mode_manager
from ..core.auth import get_current_user, User

router = APIRouter(prefix="/developer-modes", tags=["developer-modes"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=Dict[str, Any])
async def get_developer_modes(
    current_user: User = Depends(get_current_user)
):
    """
    Get available developer modes with their configurations
    
    Returns:
        - junior: Junior Developer mode (Claude Haiku - fast & cheap)
        - senior: Senior Developer mode (Claude Sonnet/Opus - premium quality)
        - default: Default mode
    """
    try:
        modes_info = developer_mode_manager.get_mode_comparison()
        
        return {
            "modes": modes_info,
            "default_mode": developer_mode_manager.DEFAULT_MODE,
            "description": {
                "junior": "🌱 Fast & Budget-Friendly - Perfect for learning and quick prototyping",
                "senior": "🚀 Premium Quality - Best for production code and complex debugging"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get developer modes: {e}")
        raise

@router.get("/comparison")
async def get_modes_comparison(
    current_user: User = Depends(get_current_user)
):
    """Get detailed comparison between Junior and Senior modes"""
    
    return {
        "comparison": {
            "junior": {
                "name": "Junior Developer 🌱",
                "model": "Claude Haiku 3.5",
                "cost": "$2.40 per 1M tokens",
                "speed": "⚡ Fast",
                "quality": "⭐⭐⭐ Good",
                "best_for": ["Learning", "Simple tasks", "Quick prototypes", "Budget projects"],
                "features": {
                    "ultra_thinking": False,
                    "smart_routing": False,
                    "savings": "73% cheaper than Senior"
                }
            },
            "senior": {
                "name": "Senior Developer 🚀",
                "model": "Claude Sonnet 4.5 + Opus 4.1",
                "cost": "$9-15 per 1M tokens",
                "speed": "⚡⚡ Smart",
                "quality": "⭐⭐⭐⭐⭐ Excellent",
                "best_for": ["Production code", "Complex debugging", "Architecture", "Mission-critical"],
                "features": {
                    "ultra_thinking": True,
                    "smart_routing": True,
                    "savings": "Best quality & reliability"
                }
            }
        },
        "recommendation": "Start with Senior for best results, switch to Junior for simple tasks to save costs"
    }
