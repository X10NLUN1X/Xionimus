"""
GitHub API Endpoints
OAuth, Repository Management, Code Pushing
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os

from ..core.github_integration import (
    GitHubIntegration, 
    generate_github_oauth_url,
    exchange_code_for_token
)

logger = logging.getLogger(__name__)
router = APIRouter()

# GitHub OAuth Configuration (aus Environment)
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/github/callback")

class GitHubAuthRequest(BaseModel):
    code: str

class CreateRepoRequest(BaseModel):
    name: str
    description: str = ""
    private: bool = False

class CreateBranchRequest(BaseModel):
    owner: str
    repo: str
    branch_name: str
    from_branch: str = "main"

class PushFilesRequest(BaseModel):
    owner: str
    repo: str
    files: List[Dict[str, str]]  # [{"path": "...", "content": "..."}]
    commit_message: str
    branch: str = "main"
    access_token: str

@router.get("/oauth/url")
async def get_github_oauth_url():
    """Get GitHub OAuth authorization URL"""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured. Please set GITHUB_CLIENT_ID environment variable."
        )
    
    oauth_url = generate_github_oauth_url(
        client_id=GITHUB_CLIENT_ID,
        redirect_uri=GITHUB_REDIRECT_URI,
        scope="repo user"
    )
    
    return {
        "oauth_url": oauth_url,
        "redirect_uri": GITHUB_REDIRECT_URI
    }

@router.post("/oauth/token")
async def exchange_github_code(request: GitHubAuthRequest):
    """Exchange OAuth code for access token"""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured"
        )
    
    try:
        token_data = await exchange_code_for_token(
            client_id=GITHUB_CLIENT_ID,
            client_secret=GITHUB_CLIENT_SECRET,
            code=request.code
        )
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Get user info
        github = GitHubIntegration(token_data["access_token"])
        user_info = await github.get_user_info()
        await github.close()
        
        return {
            "access_token": token_data["access_token"],
            "user": {
                "login": user_info.get("login"),
                "name": user_info.get("name"),
                "avatar_url": user_info.get("avatar_url")
            }
        }
    except Exception as e:
        logger.error(f"OAuth exchange failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
async def get_github_user(access_token: str = Query(...)):
    """Get authenticated user information"""
    try:
        github = GitHubIntegration(access_token)
        user_info = await github.get_user_info()
        await github.close()
        return user_info
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/repositories")
async def list_repositories(access_token: str = Query(...)):
    """List user's repositories"""
    try:
        github = GitHubIntegration(access_token)
        repos = await github.list_repositories()
        await github.close()
        return repos
    except Exception as e:
        logger.error(f"Failed to list repositories: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/repositories")
async def create_repository(
    request: CreateRepoRequest,
    access_token: str = Query(...)
):
    """Create a new repository"""
    try:
        github = GitHubIntegration(access_token)
        repo = await github.create_repository(
            name=request.name,
            description=request.description,
            private=request.private
        )
        await github.close()
        return repo
    except Exception as e:
        logger.error(f"Failed to create repository: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/repositories/{owner}/{repo}/branches")
async def list_branches(
    owner: str,
    repo: str,
    access_token: str = Query(...)
):
    """List branches in a repository"""
    try:
        github = GitHubIntegration(access_token)
        branches = await github.list_branches(owner, repo)
        await github.close()
        return branches
    except Exception as e:
        logger.error(f"Failed to list branches: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/repositories/{owner}/{repo}/branches")
async def create_branch(
    owner: str,
    repo: str,
    request: CreateBranchRequest,
    access_token: str = Query(...)
):
    """Create a new branch"""
    try:
        github = GitHubIntegration(access_token)
        branch = await github.create_branch(
            owner=owner,
            repo=repo,
            branch_name=request.branch_name,
            from_branch=request.from_branch
        )
        await github.close()
        return branch
    except Exception as e:
        logger.error(f"Failed to create branch: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/push")
async def push_to_github(request: PushFilesRequest):
    """
    Push files to GitHub repository
    
    This is the main endpoint for code pushing
    """
    try:
        github = GitHubIntegration(request.access_token)
        
        result = await github.push_multiple_files(
            owner=request.owner,
            repo=request.repo,
            files=request.files,
            commit_message=request.commit_message,
            branch=request.branch
        )
        
        await github.close()
        
        logger.info(f"✅ Pushed {result['files_count']} files to {request.owner}/{request.repo}/{request.branch}")
        
        return {
            "success": True,
            "commit_sha": result["commit_sha"],
            "files_pushed": result["files_count"],
            "repository": f"{request.owner}/{request.repo}",
            "branch": result["branch"],
            "message": f"Successfully pushed {result['files_count']} files"
        }
    except Exception as e:
        logger.error(f"Failed to push to GitHub: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def github_health():
    """Check GitHub API health"""
    configured = bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET)
    return {
        "status": "configured" if configured else "not_configured",
        "oauth_enabled": configured,
        "redirect_uri": GITHUB_REDIRECT_URI if configured else None
    }
