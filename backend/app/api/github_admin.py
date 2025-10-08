"""
GitHub Admin Endpoints
For configuring system-level GitHub PAT
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import logging

from ..core.database import get_db_session as get_database
from ..core.github_pat_storage import (
    store_github_pat, 
    get_github_pat, 
    delete_github_pat,
    is_github_pat_configured,
    store_github_oauth_credentials,
    get_github_oauth_credentials,
    is_github_oauth_configured
)

logger = logging.getLogger(__name__)
router = APIRouter()


class GitHubPATRequest(BaseModel):
    pat_token: str = Field(..., min_length=20, description="GitHub Personal Access Token")


class GitHubPATResponse(BaseModel):
    success: bool
    message: str
    configured: bool


class GitHubOAuthCredentialsRequest(BaseModel):
    client_id: str = Field(..., min_length=10, description="GitHub OAuth Client ID")
    client_secret: str = Field(..., min_length=20, description="GitHub OAuth Client Secret")
    callback_url: Optional[str] = Field(None, description="OAuth Callback URL")


class GitHubOAuthCredentialsResponse(BaseModel):
    success: bool
    message: str
    configured: bool
    client_id: Optional[str] = None
    callback_url: Optional[str] = None


@router.post("/admin/github-pat/store", response_model=GitHubPATResponse)
async def store_pat(
    request: GitHubPATRequest,
    db = Depends(get_database)
):
    """
    Store GitHub PAT securely in encrypted database
    
    ⚠️ Admin endpoint - Should be protected in production
    For development: Use this to store PAT securely without exposing in .env
    """
    try:
        # Validate token format
        if not request.pat_token.startswith('ghp_'):
            raise HTTPException(
                status_code=400,
                detail="Invalid PAT format. Must start with 'ghp_'"
            )
        
        # Store encrypted
        success = store_github_pat(db, request.pat_token)
        
        if success:
            logger.info("✅ GitHub PAT stored successfully")
            return GitHubPATResponse(
                success=True,
                message="GitHub PAT stored securely",
                configured=True
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to store GitHub PAT"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing GitHub PAT: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store PAT: {str(e)}"
        )


@router.get("/admin/github-pat/status", response_model=GitHubPATResponse)
async def get_pat_status(db = Depends(get_database)):
    """
    Check if GitHub PAT is configured
    
    Public endpoint - Returns only status, not the actual token
    """
    try:
        configured = is_github_pat_configured(db)
        
        return GitHubPATResponse(
            success=True,
            message="GitHub PAT is configured" if configured else "GitHub PAT not configured",
            configured=configured
        )
        
    except Exception as e:
        logger.error(f"Error checking GitHub PAT status: {e}")
        return GitHubPATResponse(
            success=False,
            message=f"Error: {str(e)}",
            configured=False
        )


@router.delete("/admin/github-pat/delete", response_model=GitHubPATResponse)
async def delete_pat(db = Depends(get_database)):
    """
    Delete GitHub PAT from database
    
    ⚠️ Admin endpoint - Should be protected in production
    """
    try:
        success = delete_github_pat(db)
        
        if success:
            return GitHubPATResponse(
                success=True,
                message="GitHub PAT deleted successfully",
                configured=False
            )
        else:
            return GitHubPATResponse(
                success=False,
                message="GitHub PAT not found",
                configured=False
            )
        
    except Exception as e:
        logger.error(f"Error deleting GitHub PAT: {e}")



# ==================== GitHub OAuth Credentials Endpoints ====================

@router.post("/admin/github-oauth/store", response_model=GitHubOAuthCredentialsResponse)
async def store_oauth_credentials(
    request: GitHubOAuthCredentialsRequest,
    db = Depends(get_database)
):
    """
    Store GitHub OAuth credentials securely in encrypted database
    
    Client ID is stored as-is (public identifier)
    Client Secret is encrypted with AES-128
    """
    try:
        # Validate client_id format (starts with Ov)
        if not request.client_id.startswith('Ov'):
            raise HTTPException(
                status_code=400,
                detail="Invalid Client ID format. Should start with 'Ov'"
            )
        
        # Set default callback URL if not provided
        callback_url = request.callback_url or "http://localhost:3000/github/callback"
        
        # Store encrypted
        success = store_github_oauth_credentials(
            db, 
            request.client_id, 
            request.client_secret,
            callback_url
        )
        
        if success:
            logger.info("✅ GitHub OAuth credentials stored successfully")
            return GitHubOAuthCredentialsResponse(
                success=True,
                message="GitHub OAuth credentials stored securely",
                configured=True,
                client_id=request.client_id,
                callback_url=callback_url
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to store GitHub OAuth credentials"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing GitHub OAuth credentials: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store credentials: {str(e)}"
        )


@router.get("/admin/github-oauth/status", response_model=GitHubOAuthCredentialsResponse)
async def get_oauth_status(db = Depends(get_database)):
    """
    Check if GitHub OAuth is configured and return client ID
    
    Public endpoint - Returns status and client ID (not secret)
    """
    try:
        configured = is_github_oauth_configured(db)
        
        if configured:
            credentials = get_github_oauth_credentials(db)
            return GitHubOAuthCredentialsResponse(
                success=True,
                message="GitHub OAuth is configured",
                configured=True,
                client_id=credentials.get("client_id"),
                callback_url=credentials.get("callback_url")
            )
        else:
            return GitHubOAuthCredentialsResponse(
                success=True,
                message="GitHub OAuth not configured",
                configured=False,
                client_id=None,
                callback_url=None
            )
        
    except Exception as e:
        logger.error(f"Error checking GitHub OAuth status: {e}")
        return GitHubOAuthCredentialsResponse(
            success=False,
            message=f"Error: {str(e)}",
            configured=False,
            client_id=None,
            callback_url=None
        )


@router.get("/admin/github-oauth/credentials")
async def get_oauth_credentials(db = Depends(get_database)):
    """
    Get GitHub OAuth credentials for display (masks secret)
    
    Returns client_id and masked secret
    """
    try:
        credentials = get_github_oauth_credentials(db)
        
        if credentials:
            # Mask the secret
            secret = credentials.get("client_secret", "")
            masked_secret = f"{secret[:4]}...{secret[-4:]}" if len(secret) > 8 else "***"
            
            return {
                "success": True,
                "configured": True,
                "client_id": credentials.get("client_id"),
                "client_secret_masked": masked_secret,
                "callback_url": credentials.get("callback_url")
            }
        else:
            return {
                "success": True,
                "configured": False,
                "client_id": None,
                "client_secret_masked": None,
                "callback_url": None
            }
        
    except Exception as e:
        logger.error(f"Error retrieving OAuth credentials: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve credentials: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete PAT: {str(e)}"
        )
