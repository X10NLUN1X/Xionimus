"""
Developer Mode System - Phase 2 Enhancement
Two modes for different experience levels and budgets
"""
import logging
from typing import Dict, Literal

logger = logging.getLogger(__name__)

DeveloperMode = Literal["junior", "senior"]

class DeveloperModeManager:
    """
    Manages Junior and Senior Developer modes
    
    Junior Developer Mode:
    - Claude Haiku 3.5 (fast & cheap: $2.40/1M tokens)
    - No smart routing to expensive models
    - Quick responses for simple tasks
    - 73% cheaper than Senior mode
    
    Senior Developer Mode:
    - Claude Sonnet 4.5 (premium: $9.00/1M tokens)
    - Smart routing to Opus 4.1 for complex tasks ($15.00/1M tokens)
    - Ultra-thinking enabled
    - Best quality responses
    """
    
    MODES: Dict[str, Dict[str, any]] = {
        "junior": {
            "name": "Junior Developer 🌱",
            "description": "Fast & Budget-Friendly - Claude Haiku",
            "provider": "anthropic",
            "model": "claude-haiku-3.5-20241022",
            "cost_per_1m_tokens": 2.40,
            "ultra_thinking": False,  # Disabled for speed
            "smart_routing": False,  # No auto-upgrade to expensive models
            "emoji": "🌱",
            "color": "#10b981",  # Green
            "features": [
                "⚡ Fast responses",
                "💰 73% cheaper than Senior",
                "✅ Good for simple tasks",
                "🚀 Quick prototyping"
            ]
        },
        "senior": {
            "name": "Senior Developer 🚀",
            "description": "Premium Quality - Claude Sonnet 4.5 + Opus 4.1",
            "provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929",
            "cost_per_1m_tokens": 9.00,
            "ultra_thinking": True,  # Enabled by default
            "smart_routing": True,  # Auto-upgrade to Opus for complex tasks
            "emoji": "🚀",
            "color": "#3b82f6",  # Blue
            "features": [
                "🧠 Ultra-thinking enabled",
                "🎯 Smart routing to Opus 4.1",
                "✨ Best quality responses",
                "🔧 Complex debugging & architecture"
            ]
        }
    }
    
    DEFAULT_MODE: DeveloperMode = "senior"  # Start with premium quality
    
    def get_mode_config(self, mode: DeveloperMode = "senior") -> Dict:
        """Get configuration for specified developer mode"""
        if mode not in self.MODES:
            logger.warning(f"Invalid mode '{mode}', falling back to senior")
            mode = "senior"
        
        config = self.MODES[mode].copy()
        logger.info(f"🎯 Developer Mode: {config['name']} - {config['description']}")
        return config
    
    def should_use_smart_routing(self, mode: DeveloperMode) -> bool:
        """Check if smart routing is enabled for this mode"""
        return self.MODES.get(mode, {}).get("smart_routing", False)
    
    def get_provider_and_model(self, mode: DeveloperMode = "senior") -> tuple[str, str]:
        """
        Get provider and model for specified mode
        
        Returns:
            (provider, model) tuple
        """
        config = self.get_mode_config(mode)
        return config["provider"], config["model"]
    
    def get_ultra_thinking_setting(self, mode: DeveloperMode) -> bool:
        """Get ultra-thinking setting for mode"""
        return self.MODES.get(mode, {}).get("ultra_thinking", True)
    
    def get_mode_comparison(self) -> Dict:
        """Get comparison between modes for frontend display"""
        return {
            "junior": {
                **self.MODES["junior"],
                "savings": "73% cheaper",
                "best_for": "Simple tasks, quick prototyping, learning"
            },
            "senior": {
                **self.MODES["senior"],
                "savings": "Premium quality",
                "best_for": "Complex debugging, architecture, production code"
            }
        }

# Global instance
developer_mode_manager = DeveloperModeManager()
