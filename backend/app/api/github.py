"""
GitHub API Endpoints
OAuth, Repository Management, Code Pushing
"""
import sys
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import tempfile
import asyncio
from datetime import datetime, timezone

IS_WINDOWS = sys.platform == 'win32'

from ..core.github_integration import (
    GitHubIntegration, 
    generate_github_oauth_url,
    exchange_code_for_token
)
from ..core.auth import get_current_user_optional, User

logger = logging.getLogger(__name__)
router = APIRouter()

def extract_github_token(authorization: str = Header(None)) -> str:
    """Extract GitHub token from Authorization header"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid Authorization header. Use: Authorization: Bearer <token>"
        )
    return authorization.replace('Bearer ', '')

# Load GitHub OAuth Configuration from stored settings or environment
def get_github_credentials():
    """Get GitHub credentials from stored settings or environment variables"""
    from pathlib import Path
    import json
    
    # Try to load from stored settings first
    settings_file = Path.home() / ".xionimus_ai" / "app_settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                github_config = settings.get('github_oauth', {})
                if github_config.get('client_id') and github_config.get('client_secret'):
                    return {
                        'client_id': github_config['client_id'],
                        'client_secret': github_config['client_secret'],
                        'redirect_uri': github_config.get('redirect_uri', 'http://localhost:3000/github/callback')
                    }
        except Exception as e:
            logger.warning(f"Failed to load stored GitHub credentials: {e}")
    
    # Fall back to environment variables
    return {
        'client_id': os.getenv("GITHUB_CLIENT_ID", ""),
        'client_secret': os.getenv("GITHUB_CLIENT_SECRET", ""),
        'redirect_uri': os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/github/callback")
    }

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
    credentials = get_github_credentials()
    GITHUB_CLIENT_ID = credentials['client_id']
    GITHUB_CLIENT_SECRET = credentials['client_secret']
    GITHUB_REDIRECT_URI = credentials['redirect_uri']
    
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
    credentials = get_github_credentials()
    GITHUB_CLIENT_ID = credentials['client_id']
    GITHUB_CLIENT_SECRET = credentials['client_secret']
    
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
async def get_github_user(authorization: str = Header(None)):
    """Get authenticated user information"""
    try:
        access_token = extract_github_token(authorization)
        github = GitHubIntegration(access_token)
        try:
            user_info = await github.get_user_info()
            return user_info
        finally:
            await github.close()  # Always close, even on error
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/repositories")
async def list_repositories(authorization: str = Header(None)):
    """List user's repositories"""
    try:
        access_token = extract_github_token(authorization)
        github = GitHubIntegration(access_token)
        try:
            repos = await github.list_repositories()
            return repos
        finally:
            await github.close()  # Always close, even on error
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list repositories: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/repositories")
async def create_repository(
    request: CreateRepoRequest,
    authorization: str = Header(None)
):
    """Create a new repository"""
    try:
        access_token = extract_github_token(authorization)
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
    authorization: str = Header(None)
):
    """List branches in a repository"""
    try:
        # Extract token from Authorization header
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        access_token = authorization.replace('Bearer ', '')
        
        github = GitHubIntegration(access_token)
        branches = await github.list_branches(owner, repo)
        await github.close()
        return branches
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list branches: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/repositories/{owner}/{repo}/branches")
async def create_branch(
    owner: str,
    repo: str,
    request: CreateBranchRequest,
    authorization: str = Header(None)
):
    """Create a new branch"""
    try:
        access_token = extract_github_token(authorization)
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
    credentials = get_github_credentials()
    GITHUB_CLIENT_ID = credentials['client_id']
    GITHUB_CLIENT_SECRET = credentials['client_secret']
    GITHUB_REDIRECT_URI = credentials['redirect_uri']
    
    configured = bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET)
    return {
        "status": "configured" if configured else "not_configured",
        "oauth_enabled": configured,
        "redirect_uri": GITHUB_REDIRECT_URI if configured else None
    }

@router.post("/push-project")
async def push_project_to_github(
    owner: str = Query(..., description="GitHub username"),
    repo: str = Query(..., description="Repository name"),
    commit_message: str = Query(default="Update from Xionimus AI", description="Commit message"),
    branch: str = Query(default="main", description="Target branch"),
    authorization: str = Header(None)
):
    """
    Push entire Xionimus AI project to GitHub repository
    Collects all project files and pushes them
    """
    try:
        access_token = extract_github_token(authorization)
        from pathlib import Path
        
        # Define project root
        project_root = Path("/app")
        
        # Directories to include
        include_dirs = ["backend", "frontend"]
        
        # Directories and files to skip
        skip_dirs = {'node_modules', 'venv', '__pycache__', '.git', 'dist', 'build', '.next', '.venv', 'vendor'}
        skip_files = {'.DS_Store', 'Thumbs.db', '.env', '.env.local'}
        
        def should_skip(path: Path) -> bool:
            """Check if path should be skipped"""
            # Skip if any parent is in skip_dirs
            if any(skip in path.parts for skip in skip_dirs):
                return True
            # Skip if filename is in skip_files
            if path.name in skip_files:
                return True
            return False
        
        # Collect files
        files_to_push = []
        
        for dir_name in include_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and not should_skip(file_path):
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Get relative path from project root
                        rel_path = str(file_path.relative_to(project_root))
                        
                        files_to_push.append({
                            'path': rel_path,
                            'content': content
                        })
                    except Exception as e:
                        # Skip binary files or files that can't be read as text
                        logger.warning(f"Skipping file {file_path}: {e}")
                        continue
        
        if not files_to_push:
            raise HTTPException(status_code=400, detail="No files found to push")
        
        # Also add root-level files
        for root_file in ['README.md', 'package.json', '.gitignore', 'install.bat', 'start.bat']:
            root_file_path = project_root / root_file
            if root_file_path.exists():
                try:
                    with open(root_file_path, 'r', encoding='utf-8') as f:
                        files_to_push.append({
                            'path': root_file,
                            'content': f.read()
                        })
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Skipping root file {root_file}: {e}")
        
        # Push to GitHub using existing integration
        github = GitHubIntegration(access_token)
        
        result = await github.push_multiple_files(
            owner=owner,
            repo=repo,
            files=files_to_push,
            commit_message=commit_message,
            branch=branch
        )
        
        await github.close()
        
        logger.info(f"✅ Pushed entire project ({len(files_to_push)} files) to {owner}/{repo}/{branch}")
        
        return {
            "success": True,
            "commit_sha": result["commit_sha"],
            "files_pushed": result["files_count"],
            "repository": f"{owner}/{repo}",
            "branch": result["branch"],
            "message": f"Successfully pushed {result['files_count']} files to GitHub",
            "repository_url": f"https://github.com/{owner}/{repo}"
        }
        
    except Exception as e:
        logger.error(f"Failed to push project: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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
            except (OSError, UnicodeDecodeError):
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


# ==================== GitHub Import ====================

class ImportRepoRequest(BaseModel):
    """Request to import a repository from GitHub"""
    repo_url: str
    branch: Optional[str] = "main"
    target_directory: Optional[str] = None  # If None, uses repo name
    session_id: Optional[str] = None  # If provided, set as active project for this session
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_url": "https://github.com/username/repository",
                "branch": "main",
                "target_directory": "my-project",
                "session_id": "session_123"
            }
        }

@router.post("/import")
async def import_repository(
    request: ImportRepoRequest,
    authorization: str = Header(None),
    current_user: User = Depends(get_current_user_optional)  # NEW: Optional user auth
):
    """
    Import a GitHub repository into Xionimus workspace
    
    Supports:
    - Public repos: No authentication needed
    - Private repos: Requires GitHub PAT (stored in user settings)
    
    Example:
    {
        "repo_url": "https://github.com/user/repo",
        "branch": "main"
    }
    """
    try:
        import subprocess
        import sys
        if sys.platform == "win32":
            subprocess.CREATE_NO_WINDOW = 0x08000000
        import shutil
        from pathlib import Path
        import re
        
        # Extract token - try JWT auth first (for user's stored PAT), then direct OAuth token
        access_token = None
        
        # If user is authenticated, try to get their GitHub PAT from database
        if current_user:
            try:
                from ..core.database import get_db_session as get_database
                from ..models.user_models import User as UserModel
                
                db = get_database()
                user = db.query(UserModel).filter(UserModel.id == current_user.user_id).first()
                if user and user.github_token:
                    access_token = user.github_token
                    logger.info(f"Using GitHub PAT from user settings for {current_user.username}")
                db.close()
            except Exception as e:
                logger.warning(f"Failed to fetch GitHub PAT from user settings: {e}")
        
        # Fallback: Try OAuth token from Authorization header
        if not access_token:
            try:
                access_token = extract_github_token(authorization)
                logger.info("Using OAuth token from Authorization header")
            except Exception as e:
                logger.info(f"No GitHub token provided, attempting public repo clone: {e}")
        
        # Parse repository URL
        # Supports: https://github.com/owner/repo or git@github.com:owner/repo.git
        github_pattern = r'github\.com[:/]([^/]+)/([^/\.]+)'
        match = re.search(github_pattern, request.repo_url)
        
        if not match:
            raise HTTPException(
                status_code=400,
                detail=f"❌ Ungültige GitHub-URL: '{request.repo_url}'. Bitte verwende das Format: https://github.com/username/repository"
            )
        
        owner, repo_name = match.groups()
        
        # Determine target directory
        workspace_root = Path("/app")
        if request.target_directory:
            target_dir = workspace_root / request.target_directory
        else:
            target_dir = workspace_root / repo_name
        
        # Check if directory already exists
        if target_dir.exists():
            raise HTTPException(
                status_code=400,
                detail=f"❌ Verzeichnis '{target_dir.name}' existiert bereits im Workspace. Lösungen: 1) Lösche das vorhandene Verzeichnis, oder 2) Wähle ein anderes Zielverzeichnis im Feld 'Zielverzeichnis'."
            )
        
        # Create temporary directory for cloning (secure)
        temp_dir = Path(tempfile.mkdtemp(prefix=f"github_import_{repo_name}_"))
        
        try:
            # Build git clone URL with token if available
            if access_token:
                clone_url = f"https://{access_token}@github.com/{owner}/{repo_name}.git"
            else:
                clone_url = f"https://github.com/{owner}/{repo_name}.git"
            
            logger.info(f"Cloning repository: {owner}/{repo_name} (branch: {request.branch})")
            
            # Clone repository
            clone_cmd = [
                "git", "clone",
                "--branch", request.branch,
                "--depth", "1",  # Shallow clone for speed
                clone_url,
                str(temp_dir / repo_name)
            ]
            
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr
                if "Repository not found" in error_msg or "not found" in error_msg.lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"❌ Repository '{owner}/{repo_name}' nicht gefunden oder nicht zugänglich. Prüfe: 1) Repository existiert, 2) Bei privaten Repos: GitHub PAT in Settings hinterlegt."
                    )
                elif "branch" in error_msg.lower() and request.branch:
                    raise HTTPException(
                        status_code=400,
                        detail=f"❌ Branch '{request.branch}' existiert nicht in diesem Repository. Versuche 'main' oder 'master'."
                    )
                elif "Authentication" in error_msg or "credentials" in error_msg.lower():
                    raise HTTPException(
                        status_code=401,
                        detail=f"❌ Authentifizierung fehlgeschlagen. Für private Repositories musst du ein GitHub Personal Access Token (PAT) in den Settings hinterlegen."
                    )
                else:
                    # Provide the full error for debugging but make it more user-friendly
                    raise HTTPException(
                        status_code=400,
                        detail=f"❌ Git-Clone fehlgeschlagen. Fehler: {error_msg[:200]}"
                    )
            
            cloned_repo_path = temp_dir / repo_name
            
            # Remove .git directory to avoid confusion
            # Windows-compatible: Handle permission errors
            git_dir = cloned_repo_path / ".git"
            if git_dir.exists():
                def handle_remove_readonly(func, path, exc):
                    """Handle readonly files on Windows"""
                    import os
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                
                try:
                    shutil.rmtree(git_dir, onerror=handle_remove_readonly)
                except Exception as e:
                    logger.warning(f"Could not remove .git directory (non-critical): {e}")
                    # Continue anyway - .git removal is optional
            
            # Move to workspace
            workspace_root.mkdir(parents=True, exist_ok=True)
            shutil.move(str(cloned_repo_path), str(target_dir))
            
            # Count files and analyze structure
            total_files = 0
            file_types = {}
            
            for file_path in target_dir.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    ext = file_path.suffix or 'no_extension'
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            logger.info(f"✅ Successfully imported {owner}/{repo_name} ({total_files} files)")
            
            # Auto-activate project if session_id provided
            project_activated = False
            if request.session_id:
                try:
                    from ..core.database import get_db_session as get_database
                    from ..models.session_models import Session
                    
                    db = get_database()
                    session = db.query(Session).filter(Session.id == request.session_id).first()
                    if session:
                        session.active_project = target_dir.name
                        session.active_project_branch = request.branch
                        db.commit()
                        project_activated = True
                        logger.info(f"✅ Auto-activated project for session {request.session_id}")
                    db.close()
                except Exception as e:
                    logger.warning(f"Failed to auto-activate project: {e}")
            
            return {
                "status": "success",
                "message": f"Successfully imported repository: {owner}/{repo_name}",
                "repository": {
                    "owner": owner,
                    "name": repo_name,
                    "branch": request.branch,
                    "url": f"https://github.com/{owner}/{repo_name}"
                },
                "import_details": {
                    "target_directory": str(target_dir.relative_to(workspace_root)),
                    "total_files": total_files,
                    "file_types": file_types
                },
                "workspace_path": str(target_dir),
                "project_activated": project_activated,
                "session_id": request.session_id if project_activated else None
            }
            
        finally:
            # Clean up temp directory (Windows-compatible)
            if temp_dir.exists():
                def handle_remove_readonly(func, path, exc):
                    """Handle readonly files on Windows"""
                    import os
                    import stat
                    try:
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    except (OSError, PermissionError) as e:
                        logger.debug(f"Cannot change permissions for {path}: {e}")
                
                try:
                    # First attempt with retry logic for Windows
                    import time
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
                            break
                        except PermissionError as e:
                            if attempt < max_retries - 1:
                                logger.info(f"Cleanup attempt {attempt + 1} failed, retrying...")
                                await asyncio.sleep(0.5)  # Wait before retry (non-blocking)
                            else:
                                logger.warning(f"Failed to clean up temp directory after {max_retries} attempts: {e}")
                        except Exception as e:
                            logger.warning(f"Failed to clean up temp directory: {e}")
                            break
                except Exception as e:
                    logger.warning(f"Cleanup error: {e}")
                    # Non-critical - continue anyway
        
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="⏱️ Repository-Clone Timeout (>2 Minuten). Das Repository ist möglicherweise zu groß. Versuche es mit einem kleineren Repository."
        )
    except Exception as e:
        logger.error(f"Failed to import repository: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"❌ Import fehlgeschlagen: {str(e)}"
        )


@router.get("/import/status")
async def get_import_status():
    """Get import feature status and workspace info with detailed repository information"""
    from pathlib import Path
    import os
    from datetime import datetime
    
    workspace_root = Path("/app")
    
    # List current projects in workspace with detailed info
    # Skip system directories
    skip_dirs = {'xionimus-ai', 'backend', 'frontend', 'node_modules', '.git', '__pycache__', 'venv', 'env'}
    projects = []
    if workspace_root.exists():
        for item in workspace_root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in skip_dirs:
                file_count = sum(1 for _ in item.rglob('*') if _.is_file())
                
                # Get directory size
                total_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                
                # Get creation/modification time
                try:
                    created_at = datetime.fromtimestamp(item.stat().st_ctime).isoformat()
                    modified_at = datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                except (OSError, ValueError):
                    created_at = None
                    modified_at = None
                
                # Try to detect Git branch (if .git exists)
                branch = None
                git_dir = item / ".git"
                if git_dir.exists():
                    try:
                        head_file = git_dir / "HEAD"
                        if head_file.exists():
                            head_content = head_file.read_text().strip()
                            if head_content.startswith("ref: refs/heads/"):
                                branch = head_content.replace("ref: refs/heads/", "")
                    except (OSError, UnicodeDecodeError) as e:
                        logger.debug(f"Cannot read Git HEAD file: {e}")
                
                projects.append({
                    "name": item.name,
                    "path": str(item.relative_to(workspace_root)),
                    "file_count": file_count,
                    "size_bytes": total_size,
                    "size_mb": round(total_size / (1024 * 1024), 2),
                    "branch": branch,
                    "created_at": created_at,
                    "modified_at": modified_at
                })
    
    return {
        "status": "active",
        "feature": "GitHub Import",
        "workspace_root": str(workspace_root),
        "total_projects": len(projects),
        "existing_projects": projects,
        "capabilities": [
            "Clone public repositories",
            "Clone private repositories (with token)",
            "Specify branch to clone",
            "Custom target directory",
            "Automatic file analysis",
            "Repository management and deletion"
        ]
    }


@router.delete("/import/{directory_name}")
async def delete_imported_repository(directory_name: str):
    """
    Delete an imported repository from the LOCAL workspace ONLY
    
    ⚠️ GOLDENE REGEL ⚠️
    This endpoint ONLY deletes the local copy in /app/
    It NEVER affects the remote GitHub repository!
    
    Args:
        directory_name: Name of the local directory to delete
    
    Returns:
        Success message with deleted repository details
    """
    from pathlib import Path
    import shutil
    import time
    
    workspace_root = Path("/app")
    target_path = workspace_root / directory_name
    
    # Security check: ensure path is within workspace
    try:
        target_path = target_path.resolve()
        workspace_root = workspace_root.resolve()
        if not str(target_path).startswith(str(workspace_root)):
            raise HTTPException(
                status_code=400,
                detail="❌ Sicherheitsfehler: Ungültiger Pfad"
            )
    except Exception as e:
        logger.error(f"Path resolution error: {e}")
        raise HTTPException(
            status_code=400,
            detail="❌ Ungültiger Verzeichnisname"
        )
    
    # Check if directory exists
    if not target_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"❌ Lokales Verzeichnis '{directory_name}' nicht im Workspace gefunden"
        )
    
    if not target_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"❌ '{directory_name}' ist kein Verzeichnis"
        )
    
    # Get info before deletion
    try:
        file_count = sum(1 for _ in target_path.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in target_path.rglob('*') if f.is_file())
    except Exception as e:
        logger.warning(f"Failed to get directory stats: {e}")
        file_count = 0
        total_size = 0
    
    # Delete directory (Windows-compatible)
    def handle_remove_readonly(func, path, exc):
        """Handle read-only files on Windows"""
        import stat
        import os
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    try:
        # Try to remove with error handler for Windows compatibility
        max_retries = 3
        for attempt in range(max_retries):
            try:
                shutil.rmtree(target_path, onerror=handle_remove_readonly)
                logger.info(f"Successfully deleted repository: {directory_name}")
                break
            except PermissionError as e:
                if attempt < max_retries - 1:
                    logger.info(f"Deletion attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(0.5)  # Non-blocking sleep
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"❌ Löschen fehlgeschlagen nach {max_retries} Versuchen. Möglicherweise wird das Verzeichnis noch verwendet."
                    )
            except Exception as e:
                logger.error(f"Failed to delete directory: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"❌ Löschen fehlgeschlagen: {str(e)}"
                )
        
        return {
            "success": True,
            "message": f"✅ Lokale Kopie von '{directory_name}' aus dem Workspace entfernt (GitHub-Repository bleibt unberührt)",
            "deleted_directory": directory_name,
            "files_removed": file_count,
            "space_freed_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"❌ Unerwarteter Fehler beim Löschen: {str(e)}"
        )


@router.get("/import/check-directory/{directory_name}")
async def check_directory_availability(directory_name: str):
    """
    Check if a directory name is available in the workspace
    Returns: {"available": true/false, "exists": true/false, "suggestion": "alternative-name"}
    """
    from pathlib import Path
    import re
    
    workspace_root = Path("/app")
    target_path = workspace_root / directory_name
    
    exists = target_path.exists()
    available = not exists
    
    # If not available, suggest an alternative name
    suggestion = None
    if not available:
        # Generate alternative names by appending numbers
        counter = 1
        while (workspace_root / f"{directory_name}-{counter}").exists():
            counter += 1
        suggestion = f"{directory_name}-{counter}"
    
    return {
        "directory_name": directory_name,
        "available": available,
        "exists": exists,
        "suggestion": suggestion,
        "message": f"✅ Verzeichnis '{directory_name}' ist verfügbar" if available else f"❌ Verzeichnis '{directory_name}' existiert bereits. Vorschlag: '{suggestion}'"
    }

