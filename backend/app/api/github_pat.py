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
        
        # Check OAuth configuration
        oauth_configured = bool(settings.GITHUB_OAUTH_CLIENT_ID and settings.GITHUB_OAUTH_CLIENT_SECRET)
        
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
        
        # Check if OAuth is configured
        if not settings.GITHUB_OAUTH_CLIENT_ID or not settings.GITHUB_OAUTH_CLIENT_SECRET:
            logger.error(f"GitHub OAuth not configured - CLIENT_ID: {bool(settings.GITHUB_OAUTH_CLIENT_ID)}, SECRET: {bool(settings.GITHUB_OAUTH_CLIENT_SECRET)}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "GitHub OAuth not configured",
                    "message": "GitHub OAuth credentials are missing. Please contact your administrator.",
                    "user_action": "Ask administrator to configure GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET or set up a Personal Access Token"
                }
            )
        
        # Generate state parameter for CSRF protection
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Store state in session or database for verification (simplified for now)
        # In production, you'd want to store this in Redis or database
        
        # Build GitHub OAuth URL
        client_id = settings.GITHUB_OAUTH_CLIENT_ID
        redirect_uri = settings.GITHUB_OAUTH_CALLBACK_URL
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
    current_user: User = Depends(get_current_user)
):
    """
    Handle GitHub OAuth callback
    
    Exchange authorization code for access token and store it securely.
    """
    try:
        # Check if OAuth is configured
        if not settings.GITHUB_OAUTH_CLIENT_ID or not settings.GITHUB_OAUTH_CLIENT_SECRET:
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
                    "client_id": settings.GITHUB_OAUTH_CLIENT_ID,
                    "client_secret": settings.GITHUB_OAUTH_CLIENT_SECRET,
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
        db = get_database()
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

@router.get("/oauth/status", response_model=GitHubOAuthStatusResponse)
async def get_github_oauth_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check GitHub OAuth connection status
    
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
            UserApiKey.is_active == True
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
    Preview files that will be pushed to GitHub without actually pushing
    
    ⚠️ PRIVACY: Only code and created data are included
    NO chat history, NO conversation metadata, NO session details
    
    Returns:
    - List of code files extracted from the session
    - Content preview for each file
    - File sizes and total size
    """
    db = get_database()
    try:
        # Get session from database
        session = db.query(Session).filter(
            Session.id == request.session_id,
            Session.user_id == current_user.user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all messages from session
        messages = db.query(Message).filter(
            Message.session_id == request.session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(status_code=400, detail="Session has no messages")
        
        files_preview = []
        total_size = 0
        
        # Extract only code blocks from messages (no chat history, no metadata)
        # Only code and created data will be pushed to GitHub
        for idx, msg in enumerate(messages):
            if msg.role == "assistant" and "```" in msg.content:
                blocks = msg.content.split("```")
                for block_idx, block in enumerate(blocks[1::2], 1):
                    lines = block.strip().split("\n")
                    if len(lines) > 1:
                        first_line = lines[0].strip()
                        code_content = "\n".join(lines[1:]) if first_line else block.strip()
                        
                        lang_map = {
                            "python": "py", "javascript": "js", "typescript": "ts",
                            "java": "java", "cpp": "cpp", "c": "c", "go": "go",
                            "rust": "rs", "html": "html", "css": "css", "json": "json"
                        }
                        ext = lang_map.get(first_line.lower(), "txt")
                        
                        filename = f"code/message_{idx}_block_{block_idx}.{ext}"
                        code_size = len(code_content.encode('utf-8'))
                        files_preview.append(FilePreview(
                            path=filename,
                            content=code_content[:300] + "..." if len(code_content) > 300 else code_content,
                            size=code_size,
                            type="code"
                        ))
                        total_size += code_size
        
        logger.info(f"📋 Preview generated: {len(files_preview)} files, {total_size} bytes")
        
        return PreviewSessionResponse(
            files=files_preview,
            total_size=total_size,
            file_count=len(files_preview)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "db" in locals() and db is not None:
            db.close()


@router.post("/push-session", response_model=PushSessionResponse)
async def push_session_to_github(
    request: PushSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Push code and created data to GitHub repository
    
    ⚠️ PRIVACY: Only code files are pushed to GitHub
    NO chat history, NO conversation metadata, NO session details
    
    Creates a new repository with:
    - Minimal README.md (only repo info, no chat content)
    - Code files extracted from assistant messages
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
        
        # Get all messages from session
        messages = db.query(Message).filter(
            Message.session_id == request.session_id
        ).order_by(Message.timestamp).all()
        
        if not messages:
            raise HTTPException(status_code=400, detail="Session has no messages to push")
        
        # Generate repository name if not provided
        if not request.repo_name:
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            request.repo_name = f"xionimus-session-{date_str}"
        
        # Default description
        if not request.repo_description:
            request.repo_description = f"Xionimus AI Session - {session.name or 'Conversation'}"
        
        logger.info(f"🚀 Starting GitHub push for session {request.session_id} to repo {request.repo_name}")
        
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
                auto_init=False  # No auto-init, we'll create our own README if needed
            )
            logger.info(f"✅ Created new repository: {repo.full_name}")
        
        # Prepare minimal README.md (optional, only code info)
        readme_content = f"""# {request.repo_name}

{request.repo_description or 'Code generated with Xionimus AI'}

## 📁 Contents

This repository contains code files generated during a Xionimus AI session.

**Created:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}

---

*Generated with [Xionimus AI](https://xionimus.ai)*
"""
        
        # Extract code blocks from messages
        code_files = []
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
                            "rust": "rs", "html": "html", "css": "css", "json": "json"
                        }
                        ext = lang_map.get(first_line.lower(), "txt")
                        
                        filename = f"code/message_{idx}_block_{block_idx}.{ext}"
                        code_files.append({
                            "path": filename,
                            "content": code_content
                        })
        
        # Filter files based on selection (if provided)
        selected_set = set(request.selected_files) if request.selected_files else None
        files_to_push = 0
        
        # Push files to repository
        try:
            # Only create README.md if repository is new (no files yet)
            # This provides basic info about the repo
            try:
                repo.get_contents("README.md")
                logger.info("📝 README.md already exists, skipping")
            except GithubException:
                # README doesn't exist, create minimal one
                repo.create_file(
                    "README.md",
                    "Initialize repository with Xionimus AI",
                    readme_content
                )
                logger.info("📝 Created minimal README.md")
                files_to_push += 1
            
            # Push code files (if selected or no filter)
            for code_file in code_files:
                if selected_set and code_file["path"] not in selected_set:
                    continue  # Skip non-selected files
                try:
                    existing_file = repo.get_contents(code_file["path"])
                    repo.update_file(
                        code_file["path"],
                        f"Update {code_file['path']}",
                        code_file["content"],
                        existing_file.sha
                    )
                except GithubException:
                    repo.create_file(
                        code_file["path"],
                        f"Add {code_file['path']}",
                        code_file["content"]
                    )
                logger.info(f"💻 Pushed {code_file['path']}")
                files_to_push += 1
            
            logger.info(f"✅ Successfully pushed session to {repo.html_url}")
            
            return PushSessionResponse(
                success=True,
                message=f"Successfully pushed {files_to_push} file(s) to GitHub!",
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
            
            # Create workspace directory
            workspace_dir = f"/app/workspace/github_imports/{current_user.user_id}/{repo.name}"
            os.makedirs(workspace_dir, exist_ok=True)
            
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
            
            # Create workspace directory for this import
            import os
            workspace_dir = f"/app/workspace/github_imports/{current_user.user_id}/{repo.name}"
            os.makedirs(workspace_dir, exist_ok=True)
            
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
    token: str = None
):
    """
    Import repository with real-time progress updates via SSE
    EventSource can't send headers, so token is passed as query parameter
    """
    
    # Verify JWT token BEFORE starting generator (otherwise 401 from FastAPI)
    if not token:
        logger.error("Import progress: No token provided")
        raise HTTPException(status_code=401, detail="No authentication token provided. Please login again.")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            logger.error("Import progress: Token has no user ID")
            raise HTTPException(status_code=401, detail="Invalid token - no user ID. Please login again.")
    except jwt.ExpiredSignatureError:
        logger.error("Import progress: Token expired")
        raise HTTPException(status_code=401, detail="Token expired. Please login again.")
    except jwt.JWTError as e:
        logger.error(f"Import progress: JWT Error: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token (signature mismatch). Please logout and login again.")
    except Exception as e:
        logger.error(f"Import progress: Token validation error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed. Please login again.")
    
    # Get database and GitHub token BEFORE generator
    db = get_database()
    try:
        github_token = get_github_token_from_api_keys(db, int(user_id))
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
            github_token_gen = get_github_token_from_api_keys(db, int(user_id))
            
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
                
                # Create workspace directory
                workspace_dir = f"/app/workspace/github_imports/{current_user.user_id}/{repo.name}"
                os.makedirs(workspace_dir, exist_ok=True)
                
                # Extract tarball to temp directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    tarball_path = os.path.join(temp_dir, "repo.tar.gz")
                    
                    # Save tarball
                    with open(tarball_path, 'wb') as f:
                        f.write(tarball_data)
                    
                    yield f"data: {json.dumps({'status': 'extracting', 'percentage': 50, 'message': 'Unpacking archive...'})}\n\n"
                    await asyncio.sleep(0.1)
                    
                    # Extract tarball
                    with tarfile.open(tarball_path, 'r:gz') as tar:
                        tar.extractall(temp_dir)
                    
                    # Find extracted directory (GitHub creates repo-commit_hash/)
                    extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if not extracted_dirs:
                        raise Exception("No directory found in extracted archive")
                    
                    extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
                    
                    yield f"data: {json.dumps({'status': 'filtering', 'percentage': 70, 'message': 'Filtering files...'})}\n\n"
                    await asyncio.sleep(0.1)
                    
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
                
                yield f"data: {json.dumps({'status': 'complete', 'current': files_imported, 'total': files_imported, 'percentage': 100, 'message': f'Import complete! {files_imported} files imported (skipped {files_skipped})', 'workspace': workspace_dir})}\n\n"
                
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

