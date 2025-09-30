"""
Settings API Endpoints
Manage application settings including GitHub OAuth configuration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Settings file path
SETTINGS_FILE = Path.home() / ".xionimus_ai" / "app_settings.json"
SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

class GitHubOAuthConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str = "http://localhost:3000/github/callback"

class SettingsUpdate(BaseModel):
    github_oauth: Optional[GitHubOAuthConfig] = None

def load_settings() -> Dict[str, Any]:
    """Load settings from file"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return {}
    return {}

def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        logger.info("Settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        return False

@router.get("/github-config")
async def get_github_config():
    """Get GitHub OAuth configuration status"""
    settings = load_settings()
    github_config = settings.get('github_oauth', {})
    
    is_configured = bool(
        github_config.get('client_id') and 
        github_config.get('client_secret')
    )
    
    return {
        "configured": is_configured,
        "redirect_uri": github_config.get('redirect_uri', 'http://localhost:3000/github/callback'),
        # Don't return sensitive data
        "has_client_id": bool(github_config.get('client_id')),
        "has_client_secret": bool(github_config.get('client_secret'))
    }

@router.post("/github-config")
async def save_github_config(config: GitHubOAuthConfig):
    """Save GitHub OAuth configuration"""
    try:
        # Validate inputs
        if not config.client_id or not config.client_secret:
            raise HTTPException(
                status_code=400,
                detail="Both client_id and client_secret are required"
            )
        
        # Load existing settings
        settings = load_settings()
        
        # Update GitHub OAuth config
        settings['github_oauth'] = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'redirect_uri': config.redirect_uri
        }
        
        # Save settings
        if not save_settings(settings):
            raise HTTPException(
                status_code=500,
                detail="Failed to save settings"
            )
        
        logger.info("GitHub OAuth configuration saved successfully")
        
        return {
            "success": True,
            "message": "GitHub OAuth configured successfully",
            "configured": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save GitHub config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save configuration: {str(e)}"
        )

@router.delete("/github-config")
async def delete_github_config():
    """Delete GitHub OAuth configuration"""
    try:
        settings = load_settings()
        
        if 'github_oauth' in settings:
            del settings['github_oauth']
            save_settings(settings)
        
        logger.info("GitHub OAuth configuration deleted")
        
        return {
            "success": True,
            "message": "GitHub OAuth configuration removed"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete GitHub config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete configuration: {str(e)}"
        )
