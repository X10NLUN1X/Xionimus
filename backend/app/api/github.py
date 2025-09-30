"""
GitHub API Endpoints
OAuth, Repository Management, Code Pushing
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
from datetime import datetime, timezone

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
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        # Return helpful configuration guide instead of error
        return {
            "configured": False,
            "error": "GitHub OAuth not configured",
            "message": "GitHub OAuth is optional. To enable it, follow these steps:",
            "setup_guide": {
                "step_1": "Create a GitHub OAuth App at https://github.com/settings/developers",
                "step_2": "Set Application name: 'Xionimus AI'",
                "step_3": "Set Homepage URL: http://localhost:3000",
                "step_4": "Set Authorization callback URL: http://localhost:3000/github/callback",
                "step_5": "Copy Client ID and Client Secret",
                "step_6": "Add to backend/.env file:",
                "example": {
                    "GITHUB_CLIENT_ID": "your_client_id_here",
                    "GITHUB_CLIENT_SECRET": "your_client_secret_here",
                    "GITHUB_REDIRECT_URI": "http://localhost:3000/github/callback"
                },
                "step_7": "Restart the backend server"
            },
            "alternative": {
                "method": "Personal Access Token (No OAuth needed)",
                "url": "https://github.com/settings/tokens",
                "steps": [
                    "Generate new token (classic)",
                    "Select scopes: repo, user",
                    "Use token directly in push requests"
                ]
            }
        }
    
    oauth_url = generate_github_oauth_url(
        client_id=GITHUB_CLIENT_ID,
        redirect_uri=GITHUB_REDIRECT_URI,
        scope="repo user"
    )
    
    return {
        "configured": True,
        "oauth_url": oauth_url,
        "redirect_uri": GITHUB_REDIRECT_URI
    }

@router.post("/oauth/token")
async def exchange_github_code(request: GitHubAuthRequest):
    """Exchange OAuth code for access token"""
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=400, 
            detail="GitHub OAuth ist nicht konfiguriert. Bitte setzen Sie GITHUB_CLIENT_ID und GITHUB_CLIENT_SECRET Umgebungsvariablen."
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

@router.get("/fork-summary")
async def get_fork_summary():
    """
    Generate comprehensive project/fork summary
    Includes project structure, file statistics, and code analysis
    """
    try:
        from pathlib import Path
        import mimetypes
        from collections import defaultdict
        
        # Define project root (the entire Xionimus AI application)
        project_root = Path("/app")
        
        # Directories to analyze
        important_dirs = ["backend", "frontend"]
        
        # Extensions to categorize
        code_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.md': 'Markdown',
            '.yaml': 'YAML',
            '.yml': 'YAML'
        }
        
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_size_bytes': 0,
            'by_language': defaultdict(lambda: {'files': 0, 'lines': 0}),
            'file_tree': {},
            'key_files': []
        }
        
        # Directories to skip
        skip_dirs = {'node_modules', 'venv', '__pycache__', '.git', 'dist', 'build', '.next'}
        
        def should_skip(path: Path) -> bool:
            """Check if path should be skipped"""
            return any(skip in path.parts for skip in skip_dirs)
        
        def count_lines(file_path: Path) -> int:
            """Count lines in a text file"""
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return len(f.readlines())
            except:
                return 0
        
        # Analyze project structure
        for dir_name in important_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                continue
            
            stats['file_tree'][dir_name] = {
                'path': str(dir_path.relative_to(project_root)),
                'files': []
            }
            
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and not should_skip(file_path):
                    ext = file_path.suffix.lower()
                    
                    # Get language
                    language = code_extensions.get(ext, 'Other')
                    
                    # Count lines if it's a code file
                    lines = 0
                    if ext in code_extensions:
                        lines = count_lines(file_path)
                        stats['by_language'][language]['files'] += 1
                        stats['by_language'][language]['lines'] += lines
                        stats['total_lines'] += lines
                    
                    # Add to stats
                    stats['total_files'] += 1
                    stats['total_size_bytes'] += file_path.stat().st_size
                    
                    # Track key files
                    rel_path = str(file_path.relative_to(project_root))
                    if any(key in file_path.name for key in ['main.', 'app.', 'index.', 'package.json', 'requirements.txt']):
                        stats['key_files'].append({
                            'path': rel_path,
                            'name': file_path.name,
                            'language': language,
                            'lines': lines,
                            'size': file_path.stat().st_size
                        })
        
        # Convert defaultdict to regular dict for JSON serialization
        stats['by_language'] = dict(stats['by_language'])
        
        # Calculate derived statistics
        total_size_mb = round(stats['total_size_bytes'] / (1024 * 1024), 2)
        
        # Generate summary
        summary = {
            'project_name': 'Xionimus AI',
            'description': 'Advanced local-first AI assistant with multi-modal RAG capabilities',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'statistics': {
                'total_files': stats['total_files'],
                'total_lines_of_code': stats['total_lines'],
                'total_size_mb': total_size_mb,
                'total_size_bytes': stats['total_size_bytes'],
                'languages': stats['by_language'],
                'key_files_count': len(stats['key_files'])
            },
            'structure': {
                'directories_analyzed': important_dirs,
                'backend': {
                    'description': 'FastAPI Python backend',
                    'key_features': [
                        'Multi-modal RAG with ChromaDB',
                        'Real-time WebSocket streaming',
                        'GitHub OAuth integration',
                        'Workspace management',
                        'SQLite persistence'
                    ]
                },
                'frontend': {
                    'description': 'React + Vite frontend',
                    'key_features': [
                        'Chakra UI components',
                        'Real-time chat streaming',
                        'Multi-provider AI support',
                        'GitHub integration UI',
                        'Responsive design'
                    ]
                }
            },
            'key_files': stats['key_files'][:20],  # Top 20 key files
            'technology_stack': {
                'backend': ['Python 3.10+', 'FastAPI', 'SQLite', 'ChromaDB', 'SQLAlchemy'],
                'frontend': ['React 18', 'TypeScript', 'Vite', 'Chakra UI', 'Framer Motion'],
                'ai_ml': ['sentence-transformers', 'OpenAI', 'Anthropic', 'Perplexity']
            }
        }
        
        logger.info(f"Generated fork summary: {stats['total_files']} files, {stats['total_lines']} lines")
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate fork summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
