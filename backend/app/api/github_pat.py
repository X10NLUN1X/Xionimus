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
    
    Returns:
    - List of all files (README, messages.json, code files)
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
        
        # 1. README.md preview
        readme_content = f"""# {session.name or 'Xionimus AI Session'}

**Created:** {session.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
**Last Updated:** {session.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
**Messages:** {len(messages)}

## Session Summary

This repository contains a conversation session from Xionimus AI.

### Contents

- `README.md` - This file
- `messages.json` - Full conversation history
- `code/` - Extracted code files from the conversation

## Conversation

"""
        for idx, msg in enumerate(messages, 1):
            role_emoji = "👤" if msg.role == "user" else "🤖"
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            readme_content += f"\n### {role_emoji} Message {idx} ({msg.role})\n\n{content_preview}\n"
        
        readme_size = len(readme_content.encode('utf-8'))
        files_preview.append(FilePreview(
            path="README.md",
            content=readme_content[:500] + "..." if len(readme_content) > 500 else readme_content,
            size=readme_size,
            type="readme"
        ))
        total_size += readme_size
        
        # 2. messages.json preview
        messages_data = {
            "session_id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "model": msg.model
                }
                for msg in messages
            ]
        }
        messages_json = json.dumps(messages_data, indent=2, ensure_ascii=False)
        messages_size = len(messages_json.encode('utf-8'))
        files_preview.append(FilePreview(
            path="messages.json",
            content=messages_json[:500] + "..." if len(messages_json) > 500 else messages_json,
            size=messages_size,
            type="messages"
        ))
        total_size += messages_size
        
        # 3. Extract code blocks from messages
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
        db.close()


@router.post("/push-session", response_model=PushSessionResponse)
async def push_session_to_github(
    request: PushSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Push entire session (messages and code) to GitHub repository
    
    Creates a new repository with:
    - README.md with session summary
    - messages.json with full conversation history
    - code files extracted from assistant messages
    """
    db = get_database()
    try:
        # Get user's GitHub token
        user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
        if not user or not user.github_token:
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
            request.repo_description = f"Xionimus AI Session - {session.title or 'Conversation'}"
        
        logger.info(f"🚀 Starting GitHub push for session {request.session_id} to repo {request.repo_name}")
        
        # Initialize PyGithub
        g = Github(user.github_token)
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
                auto_init=True  # Initialize with README
            )
            logger.info(f"✅ Created new repository: {repo.full_name}")
        
        # Prepare content for README.md
        readme_content = f"""# {session.title or 'Xionimus AI Session'}

**Created:** {session.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
**Last Updated:** {session.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC")}
**Messages:** {len(messages)}

## Session Summary

This repository contains a conversation session from Xionimus AI.

### Contents

- `README.md` - This file
- `messages.json` - Full conversation history
- `code/` - Extracted code files from the conversation

## Conversation

"""
        
        # Add message summary to README
        for idx, msg in enumerate(messages, 1):
            role_emoji = "👤" if msg.role == "user" else "🤖"
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            readme_content += f"\n### {role_emoji} Message {idx} ({msg.role})\n\n{content_preview}\n"
        
        # Prepare messages.json
        messages_data = {
            "session_id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "model": msg.model
                }
                for msg in messages
            ]
        }
        messages_json = json.dumps(messages_data, indent=2, ensure_ascii=False)
        
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
            # Update or create README.md (if selected or no filter)
            if not selected_set or "README.md" in selected_set:
                try:
                    readme_file = repo.get_contents("README.md")
                    repo.update_file(
                        "README.md",
                        f"Update session content - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
                        readme_content,
                        readme_file.sha
                    )
                    logger.info("📝 Updated README.md")
                    files_to_push += 1
                except GithubException:
                    repo.create_file(
                        "README.md",
                        "Add session content",
                        readme_content
                    )
                    logger.info("📝 Created README.md")
                    files_to_push += 1
            
            # Create or update messages.json (if selected or no filter)
            if not selected_set or "messages.json" in selected_set:
                try:
                    messages_file = repo.get_contents("messages.json")
                    repo.update_file(
                        "messages.json",
                        f"Update messages - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
                        messages_json,
                        messages_file.sha
                    )
                    logger.info("💾 Updated messages.json")
                    files_to_push += 1
                except GithubException:
                    repo.create_file(
                        "messages.json",
                        "Add conversation history",
                        messages_json
                    )
                    logger.info("💾 Created messages.json")
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
        db.close()
