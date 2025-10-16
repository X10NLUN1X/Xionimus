"""
GitHub Personal Access Token (PAT) Management
Simple, direct GitHub authentication without OAuth
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
import httpx
from datetime import datetime, timezone
from github import Github, GithubException
import base64
import json
import asyncio
import os
from pathlib import Path

def parse_datetime_string(dt_str: str) -> datetime:
    """Parse ISO datetime string to datetime object"""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError, TypeError) as e:
        logger.warning(f"Failed to parse datetime string '{dt_str}': {e}")
        return datetime.now(timezone.utc)

from sqlalchemy.orm import Session as DBSession

from ..core.database import get_db_session as get_database
from ..core.auth import get_current_user, User
from ..models.user_models import User as UserModel
from ..models.session_models import Session, Message
from ..models.api_key_models import UserApiKey
from ..core.encryption import encryption_manager
from ..core.config import settings
from ..core.github_pat_storage import get_github_pat, is_github_pat_configured
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== GitHub OAuth Models ====================

class GitHubOAuthUrlResponse(BaseModel):
    authorization_url: str
    state: str

class GitHubOAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

class GitHubOAuthStatusResponse(BaseModel):
    connected: bool
    github_username: Optional[str] = None
    message: str

# ==================== GitHub OAuth Endpoints ====================

@router.get("/oauth/status")
async def get_github_oauth_status(db = Depends(get_database)):
    """
    Public endpoint to check GitHub OAuth/PAT configuration status
    No authentication required
    """
    try:
        # Check if PAT mode is enabled
        use_pat = getattr(settings, 'GITHUB_USE_PAT', False)
        
        # Check PAT in database (secure storage)
        pat_configured = is_github_pat_configured(db) if use_pat else False
        
        # Check OAuth configuration - first check database, then fall back to .env
        from ..core.github_pat_storage import is_github_oauth_configured
        oauth_configured_db = is_github_oauth_configured(db)
        oauth_configured_env = bool(settings.GITHUB_OAUTH_CLIENT_ID and settings.GITHUB_OAUTH_CLIENT_SECRET)
        oauth_configured = oauth_configured_db or oauth_configured_env
        
        # Determine the mode and message
        if use_pat and pat_configured:
            return {
                "mode": "pat",
                "configured": True,
                "oauth_configured": oauth_configured,
                "pat_configured": True,
                "use_pat": True,
                "message": "GitHub Personal Access Token is configured",
                "setup_instructions": None
            }
        elif oauth_configured:
            return {
                "mode": "oauth",
                "configured": True,
                "oauth_configured": True,
                "pat_configured": pat_configured,
                "use_pat": False,
                "callback_url": settings.GITHUB_OAUTH_CALLBACK_URL,
                "message": "GitHub OAuth is configured and ready",
                "setup_instructions": None
            }
        else:
            return {
                "mode": "none",
                "configured": False,
                "oauth_configured": False,
                "pat_configured": False,
                "use_pat": False,
                "message": "GitHub authentication is not configured",
                "setup_instructions": {
                    "option1": "Use Personal Access Token (Recommended for local dev)",
                    "option2": "Use OAuth (Recommended for production)",
                    "steps_pat": [
                        "1. Go to https://github.com/settings/tokens",
                        "2. Generate new token with 'repo' and 'user' scopes",
                        "3. Add GITHUB_USE_PAT=true and GITHUB_PAT=your_token to .env"
                    ],
                    "steps_oauth": [
                        "1. Go to https://github.com/settings/developers",
                        "2. Click 'New OAuth App'",
                        "3. Set Homepage and Callback URLs",
                        "4. Add GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET to .env"
                    ]
                }
            }
    except Exception as e:
        logger.error(f"Error checking OAuth status: {e}")
        return {
            "configured": False,
            "message": f"Error checking configuration: {str(e)}"
        }

@router.get("/oauth/authorize-url")
async def get_github_oauth_url(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generate GitHub OAuth authorization URL or indicate PAT mode
    
    Returns the URL to redirect user to for GitHub OAuth authorization,
    or indicates that PAT mode is being used.
    
    Requires authentication - user must be logged in.
    """
    try:
        # Check if PAT mode is enabled
        use_pat = getattr(settings, 'GITHUB_USE_PAT', False)
        
        # Check PAT in database
        pat_configured = is_github_pat_configured(db) if use_pat else False
        
        if use_pat and pat_configured:
            logger.info(f"GitHub PAT mode enabled for user {current_user.username}")
            # Return PAT mode indicator - frontend should handle this differently
            return {
                "mode": "pat",
                "configured": True,
                "message": "GitHub is configured with Personal Access Token",
                "instructions": "GitHub authentication is handled automatically with configured PAT"
            }
        
        # Check if OAuth is configured - first check database, then .env
        from ..core.github_pat_storage import get_github_oauth_credentials
        oauth_creds = get_github_oauth_credentials(db)
        
        # Use database credentials if available, otherwise fall back to .env
        if oauth_creds:
            client_id = oauth_creds.get("client_id")
            client_secret = oauth_creds.get("client_secret")
            redirect_uri = oauth_creds.get("callback_url") or "http://localhost:3000/github/callback"
            logger.info(f"Using OAuth credentials from database for user {current_user.username}")
        elif settings.GITHUB_OAUTH_CLIENT_ID and settings.GITHUB_OAUTH_CLIENT_SECRET:
            client_id = settings.GITHUB_OAUTH_CLIENT_ID
            client_secret = settings.GITHUB_OAUTH_CLIENT_SECRET
            redirect_uri = settings.GITHUB_OAUTH_CALLBACK_URL
            logger.info(f"Using OAuth credentials from .env for user {current_user.username}")
        else:
            logger.error("GitHub OAuth not configured in database or .env")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "GitHub OAuth not configured",
                    "message": "GitHub OAuth credentials are missing. Please configure them in Settings.",
                    "user_action": "Go to Settings and configure GitHub OAuth credentials"
                }
            )
        
        # Generate state parameter for CSRF protection
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Store state in session or database for verification (simplified for now)
        # In production, you'd want to store this in Redis or database
        
        # Build GitHub OAuth URL
        scope = "repo user"  # Request repo and user scopes
        
        authorization_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&state={state}"
        )
        
        logger.info(f"🔗 Generated GitHub OAuth URL for user: {current_user.username}")
        
        # Return OAuth mode response
        return {
            "mode": "oauth",
            "authorization_url": authorization_url,
            "state": state
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating GitHub OAuth URL: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate GitHub OAuth URL"
        )

@router.post("/oauth/callback", response_model=GitHubOAuthStatusResponse)
async def github_oauth_callback(
    request: GitHubOAuthCallbackRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Handle GitHub OAuth callback
    
    Exchange authorization code for access token and store it securely.
    """
    try:
        # Get OAuth credentials from database or .env
        from ..core.github_pat_storage import get_github_oauth_credentials
        oauth_creds = get_github_oauth_credentials(db)
        
        if oauth_creds:
            client_id = oauth_creds.get("client_id")
            client_secret = oauth_creds.get("client_secret")
            logger.info("Using OAuth credentials from database for callback")
        elif settings.GITHUB_OAUTH_CLIENT_ID and settings.GITHUB_OAUTH_CLIENT_SECRET:
            client_id = settings.GITHUB_OAUTH_CLIENT_ID
            client_secret = settings.GITHUB_OAUTH_CLIENT_SECRET
            logger.info("Using OAuth credentials from .env for callback")
        else:
            raise HTTPException(
                status_code=500,
                detail="GitHub OAuth is not configured. Please contact administrator."
            )
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Accept": "application/json"
                },
                json={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": request.code
                },
                timeout=10.0
            )
            
            if token_response.status_code != 200:
                logger.error(f"GitHub OAuth token exchange failed: {token_response.status_code}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to exchange authorization code for access token"
                )
            
            token_data = token_response.json()
            
            if "error" in token_data:
                logger.error(f"GitHub OAuth error: {token_data.get('error_description', token_data['error'])}")
                raise HTTPException(
                    status_code=400,
                    detail=token_data.get("error_description", "OAuth authorization failed")
                )
            
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="No access token received from GitHub"
                )
            
            # Verify token and get user info
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10.0
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to verify GitHub token"
                )
            
            github_user = user_response.json()
            github_username = github_user.get("login")
            
            logger.info(f"✅ GitHub OAuth successful for user: {github_username}")
        
        # Store token in API Keys system (encrypted)
        try:
            # Check if GitHub key already exists
            existing_key = db.query(UserApiKey).filter(
                UserApiKey.user_id == current_user.user_id,
                UserApiKey.provider == "github"
            ).first()
            
            # Encrypt the access token
            encrypted_token = encryption_manager.encrypt(access_token)
            
            if existing_key:
                # Update existing key
                existing_key.encrypted_key = encrypted_token
                existing_key.is_active = True
                existing_key.metadata = json.dumps({
                    "github_username": github_username,
                    "oauth": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })
                logger.info(f"🔄 Updated existing GitHub OAuth token for user: {current_user.username}")
            else:
                # Create new key
                new_key = UserApiKey(
                    user_id=current_user.user_id,
                    provider="github",
                    encrypted_key=encrypted_token,
                    is_active=True,
                    metadata=json.dumps({
                        "github_username": github_username,
                        "oauth": True,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                )
                db.add(new_key)
                logger.info(f"✅ Stored new GitHub OAuth token for user: {current_user.username}")
            
            db.commit()
            
            return GitHubOAuthStatusResponse(
                connected=True,
                github_username=github_username,
                message=f"Successfully connected to GitHub as {github_username} via OAuth"
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error storing GitHub OAuth token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to store GitHub token"
            )
        finally:
            if "db" in locals() and db is not None:
                db.close()
            
    except HTTPException:
        raise
    except httpx.RequestError as e:
        logger.error(f"GitHub OAuth request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to GitHub"
        )
    except Exception as e:
        logger.error(f"Unexpected error in GitHub OAuth callback: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during OAuth"
        )

@router.get("/oauth/user-status", response_model=GitHubOAuthStatusResponse)
async def get_github_oauth_user_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check if current user has connected their GitHub account via OAuth
    
    Returns whether user has connected GitHub via OAuth and their username.
    """
    db = get_database()
    try:
        # Check if GitHub token exists in API Keys
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        if not github_token:
            return GitHubOAuthStatusResponse(
                connected=False,
                github_username=None,
                message="Not connected to GitHub. Please authorize the application."
            )
        
        # Verify token is still valid
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                # Token is invalid, mark as inactive
                api_key_record = db.query(UserApiKey).filter(
                    UserApiKey.user_id == current_user.user_id,
                    UserApiKey.provider == "github"
                ).first()
                
                if api_key_record:
                    api_key_record.is_active = False
                    db.commit()
                
                return GitHubOAuthStatusResponse(
                    connected=False,
                    github_username=None,
                    message="GitHub token is invalid or expired. Please reconnect."
                )
            
            github_user = response.json()
            github_username = github_user.get("login")
            
            return GitHubOAuthStatusResponse(
                connected=True,
                github_username=github_username,
                message=f"Connected to GitHub as {github_username}"
            )
            
    except Exception as e:
        logger.error(f"Error checking GitHub OAuth status: {e}")
        return GitHubOAuthStatusResponse(
            connected=False,
            github_username=None,
            message="Failed to check GitHub connection status"
        )
    finally:
        if "db" in locals() and db is not None:
            db.close()

# ==================== Helper Functions ====================

def get_github_token_from_api_keys(db, user_id: int) -> Optional[str]:
    """
    Get GitHub token from API Keys storage (encrypted)
    Handles decryption errors by deleting corrupted keys
    """
    try:
        api_key_record = db.query(UserApiKey).filter(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == "github",
            UserApiKey.is_active
        ).first()
        
        if not api_key_record:
            return None
        
        # Decrypt the token
        try:
            decrypted_token = encryption_manager.decrypt(api_key_record.encrypted_key)
            return decrypted_token
        except Exception as decrypt_error:
            # Decryption failed - encryption key has changed
            logger.warning(f"⚠️ Failed to decrypt GitHub token: {decrypt_error}")
            logger.info(f"🗑️ Deleting corrupted GitHub token for user {user_id}")
            db.delete(api_key_record)
            db.commit()
            return None
    except Exception as e:
        logger.error(f"Error getting GitHub token from API keys: {e}")
        return None

def set_active_project_for_user(db, user_id: str, repo_name: str, branch_name: str = "main", session_id: Optional[str] = None) -> bool:
    """
    Set active project for user's session.
    
    Args:
        db: Database session
        user_id: User ID (can be string or int)
        repo_name: Repository name (not full_name, just the repo name)
        branch_name: Branch name (default: "main")
        session_id: Specific session ID to update (if None, uses most recent session)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from ..models.session_models import Session as SessionModel
        import uuid
        
        # Convert user_id to string for consistency
        user_id_str = str(user_id)
        
        # If session_id is provided, try to use that specific session
        if session_id:
            session = db.query(SessionModel).filter(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id_str
            ).first()
            
            if session:
                # Update the specific session
                session.active_project = repo_name
                session.active_project_branch = branch_name
                session.updated_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"✅ Active project set for specific session: {repo_name} (Session: {session.id[:8]}...)")
                return True
            else:
                # Session doesn't exist - CREATE IT with the provided session_id!
                logger.info(f"📝 Specific session {session_id[:8]}... not found, creating it with active project...")
                
                new_session = SessionModel(
                    id=session_id,  # ← Use the provided session_id!
                    user_id=user_id_str,
                    name=f"Repository: {repo_name}",
                    active_project=repo_name,
                    active_project_branch=branch_name,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(new_session)
                db.commit()
                logger.info(f"✅ Created new session with active project: {repo_name} (Session: {new_session.id[:8]}...)")
                return True
        
        # Find the most recent session for this user
        session = db.query(SessionModel).filter(
            SessionModel.user_id == user_id_str
        ).order_by(SessionModel.updated_at.desc()).first()
        
        if session:
            # Update existing session
            session.active_project = repo_name
            session.active_project_branch = branch_name
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"✅ Active project set: {repo_name} (Session: {session.id[:8]}...)")
            return True
        else:
            # No session exists - create a new one with provided session_id or generate new one
            new_session_id = session_id or str(uuid.uuid4())
            logger.info(f"📝 No session found for user {user_id_str}, creating new session: {new_session_id[:8]}...")
            
            new_session = SessionModel(
                id=new_session_id,
                user_id=user_id_str,
                name=f"Repository: {repo_name}",
                active_project=repo_name,
                active_project_branch=branch_name,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(new_session)
            db.commit()
            logger.info(f"✅ Created new session and set active project: {repo_name} (Session: {new_session.id[:8]}...)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to set active project: {e}")
        import traceback
        traceback.print_exc()
        return False

class SaveGitHubTokenRequest(BaseModel):
    token: str

class GitHubTokenResponse(BaseModel):
    connected: bool
    github_username: Optional[str] = None
    message: str

class GitHubRepoResponse(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    private: bool
    url: str
    clone_url: str
    default_branch: str
    updated_at: str

@router.post("/save-token", response_model=GitHubTokenResponse)
async def save_github_token(
    request: SaveGitHubTokenRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Save GitHub Personal Access Token and verify it
    
    Steps:
    1. Verify token with GitHub API
    2. Get GitHub username
    3. Save token to user profile
    """
    try:
        # Verify token with GitHub API
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {request.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub token verification failed: {response.status_code}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid GitHub token. Please check your Personal Access Token."
                )
            
            github_user = response.json()
            github_username = github_user.get("login")
            
            logger.info(f"✅ GitHub token verified for user: {github_username}")
        
        # Save token to database
        db = get_database()
        try:
            user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.github_token = request.token
            user.github_username = github_username
            
            db.commit()
            logger.info(f"✅ GitHub token saved for user: {current_user.username}")
            
            return GitHubTokenResponse(
                connected=True,
                github_username=github_username,
                message=f"Successfully connected to GitHub as {github_username}"
            )
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error saving GitHub token: {e}")
            raise HTTPException(status_code=500, detail="Failed to save GitHub token")
        finally:
            if "db" in locals() and db is not None:
                db.close()
            
    except httpx.RequestError as e:
        logger.error(f"GitHub API request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to connect to GitHub. Please check your internet connection."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving GitHub token: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/verify-token", response_model=GitHubTokenResponse)
async def verify_github_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify existing GitHub token and return connection status
    """
    db = get_database()
    try:
        user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
        if not user or not user.github_token:
            return GitHubTokenResponse(
                connected=False,
                github_username=None,
                message="No GitHub token found. Please add your Personal Access Token."
            )
        
        # Verify token is still valid
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {user.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                # Token is invalid, remove it
                user.github_token = None
                user.github_username = None
                db.commit()
                
                return GitHubTokenResponse(
                    connected=False,
                    github_username=None,
                    message="GitHub token expired or invalid. Please add a new token."
                )
            
            github_user = response.json()
            github_username = github_user.get("login")
            
            # Update username if changed
            if user.github_username != github_username:
                user.github_username = github_username
                db.commit()
            
            return GitHubTokenResponse(
                connected=True,
                github_username=github_username,
                message=f"Connected to GitHub as {github_username}"
            )
            
    except Exception as e:
        logger.error(f"Error verifying GitHub token: {e}")
        return GitHubTokenResponse(
            connected=False,
            github_username=None,
            message="Failed to verify GitHub connection"
        )
    finally:
        if "db" in locals() and db is not None:
            db.close()

@router.delete("/remove-token", response_model=GitHubTokenResponse)
async def remove_github_token(
    current_user: User = Depends(get_current_user)
):
    """
    Remove GitHub Personal Access Token from user profile
    """
    db = get_database()
    try:
        user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.github_token = None
        user.github_username = None
        
        db.commit()
        logger.info(f"✅ GitHub token removed for user: {current_user.username}")
        
        return GitHubTokenResponse(
            connected=False,
            github_username=None,
            message="GitHub token removed successfully"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error removing GitHub token: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove GitHub token")
    finally:
        if "db" in locals() and db is not None:
            db.close()

@router.get("/repositories", response_model=List[GitHubRepoResponse])
async def list_github_repositories(
    current_user: User = Depends(get_current_user),
    per_page: int = 30,
    page: int = 1
):
    """
    List user's GitHub repositories using saved PAT from API Keys
    """
    db = get_database()
    try:
        # Get GitHub token from API Keys storage
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        if not github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected. Please add your Personal Access Token in Settings."
            )
        
        # Fetch repositories from GitHub
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get(
                f"https://api.github.com/user/repos?per_page={per_page}&page={page}&sort=updated",
                headers=headers,
                timeout=15.0
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch repositories from GitHub"
                )
            
            repos = response.json()
            
            logger.info(f"✅ Fetched {len(repos)} repositories for user {current_user.username}")
            
            return [
                GitHubRepoResponse(
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description"),
                    private=repo["private"],
                    url=repo["html_url"],
                    clone_url=repo["clone_url"],
                    default_branch=repo.get("default_branch", "main"),
                    updated_at=repo["updated_at"]
                )
                for repo in repos
            ]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching GitHub repositories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch repositories")
    finally:
        if "db" in locals() and db is not None:
            db.close()

@router.get("/user-info")
async def get_github_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed GitHub user information from API Keys storage
    """
    db = get_database()
    try:
        # Get GitHub token from API Keys storage
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        if not github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected. Please add your Personal Access Token in Settings."
            )
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid GitHub token")
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching GitHub user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user info")
    finally:
        if "db" in locals() and db is not None:
            db.close()


class GitHubBranch(BaseModel):
    name: str
    protected: bool
    commit_sha: str


@router.get("/repositories/{owner}/{repo}/branches", response_model=List[GitHubBranch])
async def list_repository_branches(
    owner: str,
    repo: str,
    current_user: User = Depends(get_current_user)
):
    """
    List branches for a specific repository from API Keys storage
    """
    db = get_database()
    try:
        # Get GitHub token from API Keys storage
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        if not github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected. Please add your Personal Access Token in Settings."
            )
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/branches",
                headers=headers,
                timeout=15.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch branches from GitHub"
                )
            
            branches = response.json()
            
            return [
                GitHubBranch(
                    name=branch["name"],
                    protected=branch.get("protected", False),
                    commit_sha=branch["commit"]["sha"]
                )
                for branch in branches
            ]
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching branches: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch branches")
    finally:
        if "db" in locals() and db is not None:
            db.close()


class PushSessionRequest(BaseModel):
    session_id: str
    repo_name: Optional[str] = None
    repo_description: Optional[str] = None
    is_private: bool = False
    selected_files: Optional[List[str]] = None  # List of file paths to push (if None, push all)


class PushSessionResponse(BaseModel):
    success: bool
    message: str
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None


class FilePreview(BaseModel):
    path: str
    content: str
    size: int
    type: str  # 'readme', 'messages', 'code'


class PreviewSessionRequest(BaseModel):
    session_id: str


class PreviewSessionResponse(BaseModel):
    files: List[FilePreview]
    total_size: int
    file_count: int

@router.post("/preview-session-files", response_model=PreviewSessionResponse)
async def preview_session_files(
    request: PreviewSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Preview files from session workspace that will be pushed to GitHub
    
    🆕 FIX: Reads actual files from github_imports workspace
    NO MORE: Extracting code blocks from messages
    
    Returns:
    - List of actual files from the workspace
    - Content preview for each file
    - File sizes and total size
    """
    db = get_database()
    try:
        logger.info(f"📂 Loading files for session: {request.session_id}")
        
        # Get session from database
        session = db.query(Session).filter(
            Session.id == request.session_id,
            Session.user_id == current_user.user_id
        ).first()

        if not session:
            logger.error(f"❌ Session not found: {request.session_id}")
            raise HTTPException(status_code=404, detail="Session not found")

        # 🆕 FIX: Keine Message-Prüfung mehr!
        # Sessions können ohne Messages Dateien haben!
        
        # Get active project from session
        if not session.active_project:
            logger.error(f"❌ Session has no active_project: {request.session_id}")
            raise HTTPException(
                status_code=400, 
                detail="Session has no active project. Please import a repository first."
            )

        # 🆕 FIX: Build workspace path from active_project
        workspace_base = Path("github_imports")
        user_workspace = workspace_base / current_user.user_id / session.active_project
        
        logger.info(f"📁 Workspace path: {user_workspace}")
        
        if not user_workspace.exists():
            logger.error(f"❌ Workspace not found: {user_workspace}")
            raise HTTPException(
                status_code=404,
                detail=f"Workspace directory not found: {user_workspace}"
            )

        # 🆕 FIX: Read actual files from workspace
        files_preview = []
        total_size = 0
        
        # File extensions to include (code and config files)
        include_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
            '.go', '.rs', '.rb', '.php', '.html', '.css', '.scss', '.json',
            '.yaml', '.yml', '.toml', '.xml', '.md', '.txt', '.sh', '.bat',
            '.sql', '.r', '.swift', '.kt', '.dart', '.vue', '.svelte'
        }
        
        # Files/folders to exclude
        exclude_patterns = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules', 
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.egg-info',
            '.DS_Store', 'Thumbs.db', '.env', '.vscode', '.idea'
        }
        
        # Walk through workspace and collect files
        for root, dirs, files in os.walk(user_workspace):
            # Remove excluded directories from search
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                # Skip excluded files
                if file in exclude_patterns or file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                file_ext = file_path.suffix.lower()
                
                # Only include relevant file types
                if file_ext not in include_extensions:
                    continue
                
                try:
                    # Get relative path from workspace root
                    rel_path = file_path.relative_to(user_workspace)
                    
                    # Read file content (with preview limit)
                    file_size = file_path.stat().st_size
                    
                    # Skip very large files (>1MB)
                    if file_size > 1024 * 1024:
                        logger.warning(f"⚠️ Skipping large file: {rel_path} ({file_size} bytes)")
                        continue
                    
                    # Read content for preview
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Preview: first 300 chars
                            preview = content[:300] + "..." if len(content) > 300 else content
                    except UnicodeDecodeError:
                        # Binary file
                        preview = f"[Binary file: {file_ext}]"
                        content = ""
                    
                    # Determine file type
                    if file_ext in {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go', '.rs'}:
                        file_type = "code"
                    elif file_ext in {'.json', '.yaml', '.yml', '.toml', '.xml'}:
                        file_type = "config"
                    elif file_ext in {'.md', '.txt'}:
                        file_type = "docs"
                    else:
                        file_type = "other"
                    
                    files_preview.append(FilePreview(
                        path=str(rel_path),
                        content=preview,
                        size=file_size,
                        type=file_type
                    ))
                    total_size += file_size
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error reading file {file_path}: {e}")
                    continue
        
        logger.info(f"✅ Preview generated: {len(files_preview)} files, {total_size} bytes")
        
        if len(files_preview) == 0:
            logger.warning(f"⚠️ No files found in workspace: {user_workspace}")
            raise HTTPException(
                status_code=404,
                detail="No files found in workspace. The directory may be empty."
            )

        return PreviewSessionResponse(
            files=files_preview,
            total_size=total_size,
            file_count=len(files_preview)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Preview error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "db" in locals() and db is not None:
            db.close()

@router.post("/push-to-github", response_model=PushSessionResponse)
async def push_session_to_github(
    request: PushSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Push workspace files AND chat-generated code to GitHub repository
    
    HYBRID APPROACH - Pushes from TWO sources:
    1. Workspace files (imported repositories + Xionimus edits)
    2. Code blocks from chat messages (generated by AI)
    
    Workspace files take priority if there are naming conflicts.
    
    ⚠️ PRIVACY: Only code files are pushed to GitHub
    NO chat history, NO conversation metadata, NO session details
    """
    db = get_database()
    try:
        # Get user's GitHub token from API Keys storage
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        if not github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected. Please add your Personal Access Token in Settings."
            )
        
        # Get session from database
        session = db.query(Session).filter(
            Session.id == request.session_id,
            Session.user_id == current_user.user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate repository name if not provided
        if not request.repo_name:
            if session.active_project:
                request.repo_name = session.active_project
            else:
                date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
                request.repo_name = f"xionimus-session-{date_str}"
        
        # Default description
        if not request.repo_description:
            if session.active_project:
                request.repo_description = f"Repository: {session.active_project}"
            else:
                request.repo_description = f"Xionimus AI Session - {session.name or 'Conversation'}"
        
        logger.info(f"🚀 Starting HYBRID GitHub push for session {request.session_id} to repo {request.repo_name}")
        
        # Initialize PyGithub
        g = Github(github_token)
        github_user = g.get_user()
        
        # Create or get repository
        try:
            repo = github_user.get_repo(request.repo_name)
            logger.info(f"📦 Using existing repository: {repo.full_name}")
        except GithubException:
            # Repository doesn't exist, create it
            repo = github_user.create_repo(
                name=request.repo_name,
                description=request.repo_description,
                private=request.is_private,
                auto_init=False
            )
            logger.info(f"✅ Created new repository: {repo.full_name}")
        
        # ====================================================================
        # SOURCE 1: WORKSPACE FILES (imported + edited)
        # ====================================================================
        workspace_files = {}  # path -> content
        
        if session.active_project:
            workspace_base = Path("github_imports")
            user_workspace = workspace_base / current_user.user_id / session.active_project
            
            if user_workspace.exists():
                logger.info(f"📂 Loading workspace files from: {user_workspace}")
                
                # File extensions to include
                include_extensions = {
                    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
                    '.go', '.rs', '.rb', '.php', '.html', '.css', '.scss', '.json',
                    '.yaml', '.yml', '.toml', '.xml', '.md', '.txt', '.sh', '.bat',
                    '.sql', '.r', '.swift', '.kt', '.dart', '.vue', '.svelte'
                }
                
                # Files/folders to exclude
                exclude_patterns = {
                    '__pycache__', '.git', '.venv', 'venv', 'node_modules',
                    '.pytest_cache', '.mypy_cache', 'dist', 'build', '.egg-info',
                    '.DS_Store', 'Thumbs.db', '.env', '.vscode', '.idea'
                }
                
                # Walk through workspace and collect files
                for root, dirs, files in os.walk(user_workspace):
                    # Remove excluded directories
                    dirs[:] = [d for d in dirs if d not in exclude_patterns]
                    
                    for file in files:
                        if file in exclude_patterns or file.startswith('.'):
                            continue
                        
                        file_path = Path(root) / file
                        file_ext = file_path.suffix.lower()
                        
                        # Only include relevant file types
                        if file_ext not in include_extensions:
                            continue
                        
                        try:
                            # Get relative path from workspace root
                            rel_path = file_path.relative_to(user_workspace)
                            rel_path_str = str(rel_path).replace('\\', '/')  # GitHub uses forward slashes
                            
                            # Read file content
                            file_size = file_path.stat().st_size
                            
                            # Skip very large files (>1MB)
                            if file_size > 1024 * 1024:
                                logger.warning(f"⚠️ Skipping large file: {rel_path_str} ({file_size} bytes)")
                                continue
                            
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    workspace_files[rel_path_str] = content
                            except UnicodeDecodeError:
                                # Skip binary files
                                logger.debug(f"Skipping binary file: {rel_path_str}")
                                continue
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Error reading file {file_path}: {e}")
                            continue
                
                logger.info(f"✅ Loaded {len(workspace_files)} files from workspace")
            else:
                logger.info(f"⚠️ Workspace not found: {user_workspace}")
        else:
            logger.info("ℹ️ Session has no active_project, skipping workspace files")
        
        # ====================================================================
        # SOURCE 2: CODE BLOCKS FROM CHAT MESSAGES (AI-generated)
        # ====================================================================
        message_code_files = {}  # path -> content
        
        messages = db.query(Message).filter(
            Message.session_id == request.session_id
        ).order_by(Message.timestamp).all()
        
        if messages:
            logger.info(f"💬 Extracting code from {len(messages)} messages")
            
            for idx, msg in enumerate(messages):
                if msg.role == "assistant" and "```" in msg.content:
                    # Extract code blocks
                    blocks = msg.content.split("```")
                    for block_idx, block in enumerate(blocks[1::2], 1):  # Every odd element is code
                        lines = block.strip().split("\n")
                        if len(lines) > 1:
                            # First line might be language identifier
                            first_line = lines[0].strip()
                            code_content = "\n".join(lines[1:]) if first_line else block.strip()
                            
                            # Determine file extension
                            lang_map = {
                                "python": "py", "javascript": "js", "typescript": "ts",
                                "java": "java", "cpp": "cpp", "c": "c", "go": "go",
                                "rust": "rs", "html": "html", "css": "css", "json": "json",
                                "bash": "sh", "shell": "sh", "yaml": "yml"
                            }
                            ext = lang_map.get(first_line.lower(), "txt")
                            
                            # Place in generated/ folder to avoid conflicts with workspace
                            filename = f"generated/message_{idx}_block_{block_idx}.{ext}"
                            message_code_files[filename] = code_content
            
            logger.info(f"✅ Extracted {len(message_code_files)} code blocks from messages")
        else:
            logger.info("ℹ️ Session has no messages, skipping message code extraction")
        
        # ====================================================================
        # MERGE: Workspace files + Message code (workspace has priority)
        # ====================================================================
        all_files = {}
        
        # Add message code first (lower priority)
        all_files.update(message_code_files)
        
        # Add workspace files (higher priority - will override conflicts)
        all_files.update(workspace_files)
        
        logger.info(f"📊 Total files to push:")
        logger.info(f"   - Workspace files: {len(workspace_files)}")
        logger.info(f"   - Generated code: {len(message_code_files)}")
        logger.info(f"   - Total (after merge): {len(all_files)}")
        
        if len(all_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="No files to push. Session has no workspace files or generated code."
            )
        
        # Filter by selected_files if provided
        selected_set = set(request.selected_files) if request.selected_files else None
        if selected_set:
            all_files = {path: content for path, content in all_files.items() if path in selected_set}
            logger.info(f"🔍 Filtered to {len(all_files)} selected files")
        
        # ====================================================================
        # PUSH TO GITHUB
        # ====================================================================
        logger.info(f"📤 Pushing {len(all_files)} files to GitHub...")
        
        files_pushed = 0
        try:
            for file_path, file_content in all_files.items():
                try:
                    # Check if file already exists
                    existing_file = repo.get_contents(file_path)
                    # Update existing file
                    repo.update_file(
                        file_path,
                        f"Update {file_path}",
                        file_content,
                        existing_file.sha
                    )
                    logger.debug(f"📝 Updated {file_path}")
                except GithubException:
                    # File doesn't exist, create it
                    repo.create_file(
                        file_path,
                        f"Add {file_path}",
                        file_content
                    )
                    logger.debug(f"✅ Created {file_path}")
                
                files_pushed += 1
                
                # Progress logging
                if files_pushed % 50 == 0:
                    logger.info(f"📊 Progress: {files_pushed}/{len(all_files)} files pushed")
            
            logger.info(f"✅ Successfully pushed {files_pushed} files to {repo.html_url}")
            logger.info(f"   - Workspace files: {len([p for p in all_files.keys() if not p.startswith('generated/')])}")
            logger.info(f"   - Generated code: {len([p for p in all_files.keys() if p.startswith('generated/')])}")
            
            return PushSessionResponse(
                success=True,
                message=f"Successfully pushed {files_pushed} file(s) to GitHub! ({len(workspace_files)} workspace + {len(message_code_files)} generated)",
                repo_url=repo.html_url,
                repo_name=repo.full_name
            )
            
        except GithubException as e:
            logger.error(f"GitHub API error during file push: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to push files to repository: {str(e)}"
            )
        
    except HTTPException:
        raise
    except GithubException as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"GitHub API error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error pushing to GitHub: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        if "db" in locals() and db is not None:
            db.close()





# Import models
class ImportFromGitHubRequest(BaseModel):
    repo_full_name: str  # e.g., "username/repo-name"
    branch: Optional[str] = "main"
    session_id: Optional[str] = None

class ImportFromUrlRequest(BaseModel):
    repo_url: str  # e.g., "https://github.com/username/repo-name"
    branch: Optional[str] = "main"
    session_id: Optional[str] = None

class ImportResponse(BaseModel):
    success: bool
    message: str
    files_imported: int
    session_id: Optional[str] = None

@router.post("/import-from-github", response_model=ImportResponse)
async def import_from_github(
    request: ImportFromGitHubRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Import repository from GitHub using authenticated access
    """
    db = get_database()
    try:
        # Get GitHub token from API Keys storage
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        if not github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected. Please add your Personal Access Token in Settings."
            )
        
        # Initialize GitHub client
        g = Github(github_token)
        
        try:
            # Get repository
            repo = g.get_repo(request.repo_full_name)
            branch = request.branch or repo.default_branch
            
            logger.info(f"📥 Importing repository {request.repo_full_name} (branch: {branch}) using FAST archive download")
            
            import os
            import tarfile
            import tempfile
            import shutil
            
            # Directories and files to skip
            SKIP_DIRS = {
                'node_modules', '__pycache__', '.git', '.vscode', '.idea',
                'venv', 'env', '.env', 'dist', 'build', 'uploads', 
                '.next', 'out', 'target', 'bin', 'obj', '.pytest_cache',
                'coverage', '.mypy_cache', '.tox', 'htmlcov'
            }
            SKIP_EXTENSIONS = {
                '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', 
                '.bin', '.log', '.db', '.sqlite', '.sqlite3', '.map'
            }
            MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB max per file
            
            # Use GitHub Archive API - MUCH FASTER (single request instead of 100s)
            archive_url = f"https://api.github.com/repos/{request.repo_full_name}/tarball/{branch}"
            
            logger.info(f"⬇️ Downloading archive from GitHub...")
            
            # Download tarball using async httpx
            # Get GitHub token from API Keys storage
            github_token_str = get_github_token_from_api_keys(db, current_user.user_id)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    archive_url,
                    headers={
                        "Authorization": f"token {github_token_str}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    follow_redirects=True
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to download archive: HTTP {response.status_code}")
                
                tarball_data = response.content
            
            logger.info(f"📦 Archive downloaded ({len(tarball_data) / 1024 / 1024:.1f} MB), extracting...")
            
            # Create workspace directory (Windows + Linux compatible)
            from pathlib import Path
            from app.core.config import settings
            workspace_base = Path(settings.GITHUB_IMPORTS_DIR)
            workspace_dir = workspace_base / str(current_user.user_id) / repo.name
            workspace_dir.mkdir(parents=True, exist_ok=True)
            workspace_dir = str(workspace_dir)  # Convert back to string for compatibility
            
            files_imported = 0
            files_skipped = 0
            
            # Extract and filter in one pass
            with tempfile.TemporaryDirectory() as temp_dir:
                tarball_path = os.path.join(temp_dir, "repo.tar.gz")
                
                # Save tarball
                with open(tarball_path, 'wb') as f:
                    f.write(tarball_data)
                
                # Extract tarball
                with tarfile.open(tarball_path, 'r:gz') as tar:
                    tar.extractall(temp_dir)
                
                # Find extracted directory (GitHub creates repo-commit_hash/)
                extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                if not extracted_dirs:
                    raise Exception("No directory found in extracted archive")
                
                extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
                
                logger.info(f"🔍 Filtering and copying files...")
                
                # Copy files to workspace, filtering as we go
                for root, dirs, files in os.walk(extracted_dir):
                    # Filter directories in-place to skip unwanted ones
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, extracted_dir)
                        
                        # Check file extension
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext in SKIP_EXTENSIONS:
                            files_skipped += 1
                            continue
                        
                        # Check file size
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size > MAX_FILE_SIZE:
                                files_skipped += 1
                                continue
                        except (OSError, IOError) as e:
                            logger.debug(f"Skipping file due to error: {e}")
                            files_skipped += 1
                            continue
                        
                        # Copy file to workspace
                        dest_path = os.path.join(workspace_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        
                        try:
                            shutil.copy2(file_path, dest_path)
                            files_imported += 1
                            
                            if files_imported % 100 == 0:
                                logger.info(f"📥 Progress: {files_imported} files imported...")
                        except Exception as e:
                            logger.warning(f"Failed to copy {rel_path}: {e}")
                            files_skipped += 1
            
            logger.info(f"✅ Imported {files_imported} files from {request.repo_full_name} (skipped {files_skipped} files)")
            logger.info(f"📁 Files saved to: {workspace_dir}")
            
            # ===================================================================
            # 🆕 AUTO-SET ACTIVE PROJECT AFTER SUCCESSFUL IMPORT
            # ===================================================================
            set_active_project_for_user(
                db=db,
                user_id=current_user.user_id,
                repo_name=repo.name,
                branch_name=branch,
                session_id=request.session_id  # ← Pass session_id from request
            )
            # ===================================================================
            
            return ImportResponse(
                success=True,
                message=f"Successfully imported {files_imported} files from {request.repo_full_name}",
                files_imported=files_imported,
                session_id=request.session_id
            )
            
        except GithubException as e:
            logger.error(f"GitHub API error during import: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to import repository: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        if "db" in locals() and db is not None:
            db.close()

@router.post("/import-from-url", response_model=ImportResponse)
async def import_from_url(
    request: ImportFromUrlRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Import repository from GitHub URL (public or with token)
    """
    db = get_database()
    try:
        # Extract owner/repo from URL
        # https://github.com/username/repo-name -> username/repo-name
        import re
        match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$', request.repo_url)
        
        if not match:
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL. Please provide a valid GitHub repository URL."
            )
        
        owner = match.group(1)
        repo_name = match.group(2)
        repo_full_name = f"{owner}/{repo_name}"
        
        logger.info(f"📥 Importing from URL: {repo_full_name}")
        
        # Get GitHub token if available (for private repos)
        github_token = get_github_token_from_api_keys(db, current_user.user_id)
        
        # Initialize GitHub client
        if github_token:
            g = Github(github_token)
        else:
            g = Github()  # Public access only
        
        try:
            # Get repository
            repo = g.get_repo(repo_full_name)
            branch = request.branch or repo.default_branch
            
            # Directories and files to skip
            SKIP_DIRS = {
                'node_modules', '__pycache__', '.git', '.vscode', '.idea',
                'venv', 'env', '.env', 'dist', 'build', 'uploads', 
                '.next', 'out', 'target', 'bin', 'obj'
            }
            SKIP_EXTENSIONS = {
                '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', 
                '.bin', '.log', '.db', '.sqlite', '.sqlite3'
            }
            MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB max per file
            
            # Create workspace directory for this import (Windows + Linux compatible)
            import os
            from pathlib import Path
            from app.core.config import settings
            workspace_base = Path(settings.GITHUB_IMPORTS_DIR)
            workspace_dir = workspace_base / str(current_user.user_id) / repo.name
            workspace_dir.mkdir(parents=True, exist_ok=True)
            workspace_dir = str(workspace_dir)
            
            # Get repository contents
            contents = repo.get_contents("", ref=branch)
            files_imported = 0
            files_skipped = 0
            
            # Download files recursively
            def download_contents(contents_list, path=""):
                nonlocal files_imported, files_skipped
                
                for content in contents_list:
                    # Skip directories that should be ignored
                    if content.type == "dir":
                        if content.name in SKIP_DIRS:
                            logger.debug(f"⏭️ Skipping directory: {content.path}")
                            files_skipped += 1
                            continue
                        
                        # Recursively download directory contents
                        try:
                            dir_contents = repo.get_contents(content.path, ref=branch)
                            download_contents(dir_contents, content.path)
                        except Exception as e:
                            logger.warning(f"Failed to access directory {content.path}: {e}")
                    
                    else:
                        # Check file extension
                        file_ext = os.path.splitext(content.name)[1].lower()
                        if file_ext in SKIP_EXTENSIONS:
                            logger.debug(f"⏭️ Skipping file type: {content.path}")
                            files_skipped += 1
                            continue
                        
                        # Check file size
                        if content.size > MAX_FILE_SIZE:
                            logger.debug(f"⏭️ Skipping large file ({content.size} bytes): {content.path}")
                            files_skipped += 1
                            continue
                        
                        # Download and save file
                        try:
                            # Try to get content as text first
                            try:
                                file_content = content.decoded_content.decode('utf-8')
                                is_binary = False
                            except (UnicodeDecodeError, AttributeError):
                                # Binary file - get raw content
                                file_content = content.decoded_content
                                is_binary = True
                            
                            # Save file to workspace
                            file_path = os.path.join(workspace_dir, content.path)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            
                            if is_binary:
                                with open(file_path, 'wb') as f:
                                    f.write(file_content)
                            else:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(file_content)
                            
                            files_imported += 1
                            if files_imported % 10 == 0:
                                logger.info(f"📥 Progress: {files_imported} files imported...")
                            
                        except Exception as e:
                            logger.warning(f"Failed to download {content.path}: {e}")
                            files_skipped += 1
            
            download_contents(contents if isinstance(contents, list) else [contents])
            
            logger.info(f"✅ Imported {files_imported} files from {repo_full_name} (skipped {files_skipped} files)")
            logger.info(f"📁 Files saved to: {workspace_dir}")
            
            # ===================================================================
            # 🆕 AUTO-SET ACTIVE PROJECT AFTER SUCCESSFUL IMPORT
            # ===================================================================
            set_active_project_for_user(
                db=db,
                user_id=current_user.user_id,
                repo_name=repo.name,
                branch_name=branch,
                session_id=request.session_id  # ← Pass session_id from request
            )
            # ===================================================================
            
            return ImportResponse(
                success=True,
                message=f"Successfully imported {files_imported} files from {repo_full_name}",
                files_imported=files_imported,
                session_id=request.session_id
            )
            
        except GithubException as e:
            logger.error(f"GitHub API error during import: {e}")
            if e.status == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Repository not found or you don't have access to it."
                )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to import repository: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during URL import: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        if "db" in locals() and db is not None:
            db.close()



@router.get("/import-progress/{repo_owner}/{repo_name}")
async def import_with_progress(
    repo_owner: str,
    repo_name: str,
    branch: str = "main",
    token: str = None,
    session_id: str = None  # ← Add session_id parameter
):
    """
    Import repository with real-time progress updates via SSE
    EventSource can't send headers, so token is passed as query parameter
    """
    
    # Verify JWT token BEFORE starting generator (otherwise 401 from FastAPI)
    if not token:
        logger.error("Import progress: No token provided")
        raise HTTPException(status_code=401, detail="No authentication token provided. Please login again.")
    
    # URL decode token if needed (in case it's double-encoded)
    from urllib.parse import unquote
    token = unquote(token)
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            logger.error("Import progress: Token has no user ID")
            raise HTTPException(status_code=401, detail="Invalid token - no user ID. Please login again.")
        
        logger.info(f"✅ Token validated for user_id: {user_id}")
        
    except jwt.ExpiredSignatureError:
        logger.error("Import progress: Token expired")
        raise HTTPException(status_code=401, detail="Token expired. Please login again.")
    except jwt.JWTError as e:
        logger.error(f"Import progress: JWT Error: {e}")
        logger.error(f"Token (first 50 chars): {token[:50]}...")
        raise HTTPException(status_code=401, detail=f"Invalid token. Please logout and login again.")
    except Exception as e:
        logger.error(f"Import progress: Token validation error: {e}")
        logger.error(f"Token (first 50 chars): {token[:50]}...")
        raise HTTPException(status_code=401, detail=f"Authentication failed. Please login again.")
    
    # Get database and GitHub token BEFORE generator
    db = get_database()
    try:
        github_token = get_github_token_from_api_keys(db, user_id)
        if not github_token:
            raise HTTPException(status_code=401, detail="GitHub not connected. Please add your GitHub token in Settings.")
    finally:
        db.close()
    
    async def generate_progress() -> AsyncGenerator[str, None]:
        db = None
        try:
            # Token already validated above
            # Get fresh database session for generator
            db = get_database()
            
            # GitHub token already retrieved above
            # Re-get for safety
            github_token_gen = get_github_token_from_api_keys(db, user_id)
            
            if not github_token_gen:
                yield f"data: {json.dumps({'error': 'GitHub not connected'})}\n\n"
                return
            
            # Initialize GitHub client
            g = Github(github_token_gen)
            repo_full_name = f"{repo_owner}/{repo_name}"
            
            try:
                repo = g.get_repo(repo_full_name)
                branch_name = branch or repo.default_branch
                
                yield f"data: {json.dumps({'status': 'downloading', 'percentage': 0, 'message': 'Downloading repository archive...'})}\n\n"
                await asyncio.sleep(0.1)
                
                import os
                import tarfile
                import tempfile
                import shutil
                
                # Use GitHub Archive API - MUCH FASTER (single request)
                archive_url = f"https://api.github.com/repos/{repo_full_name}/tarball/{branch_name}"
                
                # Download tarball
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(
                        archive_url,
                        headers={
                            "Authorization": f"token {github_token_gen}",
                            "Accept": "application/vnd.github.v3+json"
                        },
                        follow_redirects=True
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"Failed to download archive: HTTP {response.status_code}")
                    
                    tarball_data = response.content
                
                yield f"data: {json.dumps({'status': 'extracting', 'percentage': 30, 'message': 'Extracting files...'})}\n\n"
                await asyncio.sleep(0.1)
                
                # Create workspace directory (Windows + Linux compatible)
                from pathlib import Path
                from app.core.config import settings
                
                try:
                    workspace_base = Path(settings.GITHUB_IMPORTS_DIR)
                    logger.info(f"📁 Creating workspace directory: {workspace_base}")
                    
                    workspace_dir = workspace_base / str(user_id) / repo.name
                    logger.info(f"📁 Full workspace path: {workspace_dir}")
                    
                    # Ensure parent directories exist
                    workspace_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"✅ Workspace directory created successfully")
                    
                    workspace_dir = str(workspace_dir)
                except Exception as e:
                    error_msg = f"Failed to create workspace directory: {e}"
                    logger.error(f"❌ {error_msg}")
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                    return
                
                # Extract tarball to temp directory
                logger.info(f"📦 Extracting tarball to temporary directory...")
                with tempfile.TemporaryDirectory() as temp_dir:
                    logger.info(f"📁 Temp directory created: {temp_dir}")
                    tarball_path = os.path.join(temp_dir, "repo.tar.gz")
                    
                    # Save tarball
                    logger.info(f"💾 Saving tarball ({len(tarball_data)} bytes)...")
                    with open(tarball_path, 'wb') as f:
                        f.write(tarball_data)
                    logger.info(f"✅ Tarball saved to {tarball_path}")
                    
                    yield f"data: {json.dumps({'status': 'extracting', 'percentage': 50, 'message': 'Unpacking archive...'})}\n\n"
                    await asyncio.sleep(0.1)
                    
                    # Extract tarball
                    logger.info(f"📂 Extracting tarball contents...")
                    with tarfile.open(tarball_path, 'r:gz') as tar:
                        tar.extractall(temp_dir)
                    logger.info(f"✅ Tarball extracted")
                    
                    # Find extracted directory (GitHub creates repo-commit_hash/)
                    extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if not extracted_dirs:
                        raise Exception("No directory found in extracted archive")
                    
                    extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
                    logger.info(f"📁 Found extracted directory: {extracted_dirs[0]}")
                    
                    yield f"data: {json.dumps({'status': 'filtering', 'percentage': 70, 'message': 'Filtering files...'})}\n\n"
                    await asyncio.sleep(0.1)
                    
                    logger.info(f"🔍 Starting file filtering and copying...")
                    
                    # Directories and files to skip
                    SKIP_DIRS = {
                        'node_modules', '__pycache__', '.git', '.vscode', '.idea',
                        'venv', 'env', '.env', 'dist', 'build', 'uploads', 
                        '.next', 'out', 'target', 'bin', 'obj', '.pytest_cache',
                        'coverage', '.mypy_cache', '.tox', 'htmlcov'
                    }
                    SKIP_EXTENSIONS = {
                        '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', 
                        '.bin', '.log', '.db', '.sqlite', '.sqlite3', '.map'
                    }
                    MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
                    
                    # Copy files to workspace, filtering as we go
                    files_imported = 0
                    files_skipped = 0
                    
                    logger.info(f"📁 Walking through directory: {extracted_dir}")
                    logger.info(f"📁 Target workspace: {workspace_dir}")
                    
                    for root, dirs, files in os.walk(extracted_dir):
                        # Filter directories in-place to skip unwanted ones
                        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, extracted_dir)
                            
                            # Check file extension
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext in SKIP_EXTENSIONS:
                                files_skipped += 1
                                continue
                            
                            # Check file size
                            try:
                                file_size = os.path.getsize(file_path)
                                if file_size > MAX_FILE_SIZE:
                                    files_skipped += 1
                                    continue
                            except (OSError, IOError) as e:
                                logger.debug(f"Skipping file due to error: {e}")
                                files_skipped += 1
                                continue
                            
                            # Copy file to workspace
                            dest_path = os.path.join(workspace_dir, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            
                            try:
                                shutil.copy2(file_path, dest_path)
                                files_imported += 1
                            except Exception as e:
                                logger.warning(f"Failed to copy {rel_path}: {e}")
                                files_skipped += 1
                    
                    logger.info(f"📊 Import statistics: {files_imported} files imported, {files_skipped} files skipped")
                    
                    # ===================================================================
                    # 🆕 AUTO-SET ACTIVE PROJECT AFTER SUCCESSFUL IMPORT
                    # ===================================================================
                    # This ensures the AI can immediately access the imported repository
                    logger.info(f"🔄 Setting active project for session {session_id[:8]}...")
                    
                    try:
                        set_active_project_for_user(
                            db=db,
                            user_id=user_id,
                            repo_name=repo.name,
                            branch_name=branch_name,
                            session_id=session_id  # ← Pass session_id from query parameter
                        )
                        logger.info(f"✅ Active project set successfully for session {session_id[:8]}")
                    except Exception as e:
                        logger.error(f"❌ Failed to set active project: {e}")
                        # Continue anyway - files are imported
                    # ===================================================================

                
                logger.info(f"🎉 Import complete! Yielding final status...")
                yield f"data: {json.dumps({'status': 'complete', 'current': files_imported, 'total': files_imported, 'percentage': 100, 'message': f'Import complete! {files_imported} files imported (skipped {files_skipped})', 'workspace': workspace_dir})}\n\n"
                logger.info(f"✅ Final yield complete")
                
            except GithubException as e:
                logger.error(f"GitHub API error: {e}")
                yield f"data: {json.dumps({'error': f'GitHub error: {str(e)}'})}\n\n"
                
        except Exception as e:
            logger.error(f"Import error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            if "db" in locals() and db is not None:
                db.close()
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

