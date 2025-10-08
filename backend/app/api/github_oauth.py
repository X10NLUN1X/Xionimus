"""
GitHub OAuth Integration - Like Emergent.sh
Implements OAuth 2.0 flow for seamless GitHub connection
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import logging
import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session as DBSession

from ..core.database import get_db_session as get_database
from ..core.auth import get_current_user, User
from ..models.api_key_models import UserApiKey
from ..core.encryption import encryption_manager
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class GitHubOAuthConfig:
    """GitHub OAuth Configuration"""
    CLIENT_ID = settings.GITHUB_OAUTH_CLIENT_ID if hasattr(settings, 'GITHUB_OAUTH_CLIENT_ID') else None
    CLIENT_SECRET = settings.GITHUB_OAUTH_CLIENT_SECRET if hasattr(settings, 'GITHUB_OAUTH_CLIENT_SECRET') else None
    REDIRECT_URI = settings.GITHUB_OAUTH_REDIRECT_URI if hasattr(settings, 'GITHUB_OAUTH_REDIRECT_URI') else "http://localhost:3000/auth/github/callback"
    SCOPES = "repo user"
    
    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.CLIENT_ID and cls.CLIENT_SECRET)


class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


class GitHubOAuthStatus(BaseModel):
    connected: bool
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    configured: bool
    message: Optional[str] = None


@router.get("/status")
async def github_oauth_status(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_database)
):
    """
    Check if GitHub OAuth is connected for current user
    """
    try:
        # Check if OAuth is configured
        if not GitHubOAuthConfig.is_configured():
            return GitHubOAuthStatus(
                connected=False,
                configured=False,
                message="GitHub OAuth not configured. Please set GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET in .env"
            )
        
        # Check if user has GitHub token
        github_token_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.provider == "github",
            UserApiKey.is_active == True
        ).first()
        
        if not github_token_record:
            return GitHubOAuthStatus(
                connected=False,
                configured=True,
                message="GitHub not connected. Click 'Connect GitHub' to authorize."
            )
        
        # Try to decrypt and validate token
        try:
            github_token = encryption_manager.decrypt(github_token_record.encrypted_key)
            
            # Fetch user info from GitHub to verify token
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return GitHubOAuthStatus(
                        connected=True,
                        configured=True,
                        username=user_data.get("login"),
                        avatar_url=user_data.get("avatar_url"),
                        message="GitHub connected successfully"
                    )
                else:
                    return GitHubOAuthStatus(
                        connected=False,
                        configured=True,
                        message="GitHub token invalid. Please reconnect."
                    )
        except Exception as e:
            logger.error(f"Error validating GitHub token: {e}")
            return GitHubOAuthStatus(
                connected=False,
                configured=True,
                message="GitHub token corrupted. Please reconnect."
            )
            
    except Exception as e:
        logger.error(f"Error checking GitHub OAuth status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "db" in locals() and db is not None:
            db.close()


@router.get("/login")
async def github_oauth_login(
    current_user: User = Depends(get_current_user)
):
    """
    Redirect user to GitHub OAuth authorization page
    Like Emergent.sh - seamless GitHub connection
    """
    if not GitHubOAuthConfig.is_configured():
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth not configured. Please contact administrator."
        )
    
    # Build authorization URL
    params = {
        "client_id": GitHubOAuthConfig.CLIENT_ID,
        "redirect_uri": GitHubOAuthConfig.REDIRECT_URI,
        "scope": GitHubOAuthConfig.SCOPES,
        "state": current_user.user_id,  # Use user_id as state for security
        "allow_signup": "true"
    }
    
    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    logger.info(f"Redirecting user {current_user.username} to GitHub OAuth")
    
    return RedirectResponse(url=auth_url)


@router.post("/callback")
async def github_oauth_callback(
    request: GitHubCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_database)
):
    """
    Handle GitHub OAuth callback
    Exchange authorization code for access token
    """
    try:
        if not GitHubOAuthConfig.is_configured():
            raise HTTPException(status_code=503, detail="GitHub OAuth not configured")
        
        logger.info(f"Processing GitHub OAuth callback for user {current_user.username}")
        
        # Exchange code for access token
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Accept": "application/json"
                },
                data={
                    "client_id": GitHubOAuthConfig.CLIENT_ID,
                    "client_secret": GitHubOAuthConfig.CLIENT_SECRET,
                    "code": request.code,
                    "redirect_uri": GitHubOAuthConfig.REDIRECT_URI
                }
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to exchange authorization code for token"
                )
            
            token_data = response.json()
            
            if "error" in token_data:
                logger.error(f"GitHub OAuth error: {token_data}")
                raise HTTPException(
                    status_code=400,
                    detail=token_data.get("error_description", "OAuth authorization failed")
                )
            
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received from GitHub")
        
        # Fetch user info from GitHub
        async with httpx.AsyncClient(timeout=5.0) as client:
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch GitHub user info")
            
            github_user = user_response.json()
        
        # Encrypt and store token
        encrypted_token = encryption_manager.encrypt(access_token)
        
        # Check if user already has GitHub token
        existing_token = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.provider == "github"
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.encrypted_key = encrypted_token
            existing_token.is_active = True
            existing_token.last_test_status = "success"
            logger.info(f"Updated GitHub token for user {current_user.username}")
        else:
            # Create new token record
            new_token = UserApiKey(
                user_id=current_user.user_id,
                provider="github",
                encrypted_key=encrypted_token,
                is_active=True,
                last_test_status="success"
            )
            db.add(new_token)
            logger.info(f"Created new GitHub token for user {current_user.username}")
        
        db.commit()
        
        logger.info(f"✅ GitHub OAuth successful for user {current_user.username} (GitHub: {github_user.get('login')})")
        
        return {
            "success": True,
            "message": f"Successfully connected to GitHub as {github_user.get('login')}",
            "github_username": github_user.get("login"),
            "avatar_url": github_user.get("avatar_url")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in GitHub OAuth callback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "db" in locals() and db is not None:
            db.close()


@router.delete("/disconnect")
async def github_oauth_disconnect(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_database)
):
    """
    Disconnect GitHub OAuth (remove stored token)
    """
    try:
        token_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == current_user.user_id,
            UserApiKey.provider == "github"
        ).first()
        
        if not token_record:
            raise HTTPException(status_code=404, detail="GitHub not connected")
        
        db.delete(token_record)
        db.commit()
        
        logger.info(f"✅ Disconnected GitHub for user {current_user.username}")
        
        return {
            "success": True,
            "message": "GitHub disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting GitHub: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "db" in locals() and db is not None:
            db.close()
