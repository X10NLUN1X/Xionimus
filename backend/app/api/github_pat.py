"""
GitHub Personal Access Token (PAT) Management
Simple, direct GitHub authentication without OAuth
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import httpx
from datetime import datetime, timezone
from github import Github, GithubException
import base64
import json

from ..core.database import get_database
from ..core.auth import get_current_user, User
from ..models.user_models import User as UserModel
from ..models.session_models import Session, Message
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)
router = APIRouter()

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
        db.close()

@router.get("/repositories", response_model=List[GitHubRepoResponse])
async def list_github_repositories(
    current_user: User = Depends(get_current_user),
    per_page: int = 30,
    page: int = 1
):
    """
    List user's GitHub repositories using saved PAT
    """
    db = get_database()
    try:
        user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
        if not user or not user.github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected. Please add your Personal Access Token in Settings."
            )
        
        # Fetch repositories from GitHub
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"token {user.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get(
                f"https://api.github.com/user/repos?per_page={per_page}&page={page}&sort=updated",
                headers=headers,
                timeout=15.0
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch repositories from GitHub"
                )
            
            repos = response.json()
            
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
        db.close()

@router.get("/user-info")
async def get_github_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed GitHub user information
    """
    db = get_database()
    try:
        user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
        if not user or not user.github_token:
            raise HTTPException(
                status_code=401,
                detail="GitHub not connected"
            )
        
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
                raise HTTPException(status_code=401, detail="Invalid GitHub token")
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching GitHub user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user info")
    finally:
        db.close()
