"""
GitHub Integration für Xionimus AI
Funktionen: OAuth, Repository Management, Branch Management, Commit & Push
"""
from typing import Dict, Any, Optional, List
import logging
import httpx
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """
    GitHub Integration Manager
    Handles OAuth, repository operations, and code pushing
    """
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.api_base = "https://api.github.com"
        self.client = httpx.AsyncClient(
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {access_token}" if access_token else ""
            },
            timeout=30.0
        )
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        try:
            response = await self.client.get(f"{self.api_base}/user")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    async def list_repositories(self, per_page: int = 30) -> List[Dict[str, Any]]:
        """List user's repositories"""
        try:
            response = await self.client.get(
                f"{self.api_base}/user/repos",
                params={"per_page": per_page, "sort": "updated"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            raise
    
    async def create_repository(
        self, 
        name: str, 
        description: str = "",
        private: bool = False
    ) -> Dict[str, Any]:
        """Create a new repository"""
        try:
            response = await self.client.post(
                f"{self.api_base}/user/repos",
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": True  # Initialize with README
                }
            )
            response.raise_for_status()
            logger.info(f"✅ Repository created: {name}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create repository: {e}")
            raise
    
    async def list_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List branches in a repository"""
        try:
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/branches"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list branches: {e}")
            raise
    
    async def create_branch(
        self, 
        owner: str, 
        repo: str, 
        branch_name: str,
        from_branch: str = "main"
    ) -> Dict[str, Any]:
        """Create a new branch"""
        try:
            # Get the SHA of the source branch
            ref_response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{from_branch}"
            )
            ref_response.raise_for_status()
            sha = ref_response.json()["object"]["sha"]
            
            # Create new branch
            response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/git/refs",
                json={
                    "ref": f"refs/heads/{branch_name}",
                    "sha": sha
                }
            )
            response.raise_for_status()
            logger.info(f"✅ Branch created: {branch_name}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            raise
    
    async def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        path: str,
        branch: str = "main"
    ) -> Optional[Dict[str, Any]]:
        """Get file content from repository"""
        try:
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": branch}
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            return None
    
    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
        sha: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update a file in repository"""
        try:
            # Encode content to base64
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            payload = {
                "message": message,
                "content": content_base64,
                "branch": branch
            }
            
            # If sha provided, it's an update
            if sha:
                payload["sha"] = sha
            
            response = await self.client.put(
                f"{self.api_base}/repos/{owner}/{repo}/contents/{path}",
                json=payload
            )
            response.raise_for_status()
            logger.info(f"✅ File {'updated' if sha else 'created'}: {path}")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create/update file: {e}")
            raise
    
    async def push_multiple_files(
        self,
        owner: str,
        repo: str,
        files: List[Dict[str, str]],  # [{"path": "...", "content": "..."}]
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Push multiple files at once using GitHub's tree API
        More efficient than multiple single file commits
        """
        try:
            # Get the latest commit SHA
            ref_response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{branch}"
            )
            ref_response.raise_for_status()
            latest_commit_sha = ref_response.json()["object"]["sha"]
            
            # Get the tree SHA of the latest commit
            commit_response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/git/commits/{latest_commit_sha}"
            )
            commit_response.raise_for_status()
            base_tree_sha = commit_response.json()["tree"]["sha"]
            
            # Create blobs for each file
            tree_items = []
            for file in files:
                # Create blob
                blob_response = await self.client.post(
                    f"{self.api_base}/repos/{owner}/{repo}/git/blobs",
                    json={
                        "content": file["content"],
                        "encoding": "utf-8"
                    }
                )
                blob_response.raise_for_status()
                blob_sha = blob_response.json()["sha"]
                
                tree_items.append({
                    "path": file["path"],
                    "mode": "100644",  # File mode
                    "type": "blob",
                    "sha": blob_sha
                })
            
            # Create new tree
            tree_response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/git/trees",
                json={
                    "base_tree": base_tree_sha,
                    "tree": tree_items
                }
            )
            tree_response.raise_for_status()
            new_tree_sha = tree_response.json()["sha"]
            
            # Create new commit
            commit_data = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [latest_commit_sha]
            }
            new_commit_response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/git/commits",
                json=commit_data
            )
            new_commit_response.raise_for_status()
            new_commit_sha = new_commit_response.json()["sha"]
            
            # Update reference
            update_ref_response = await self.client.patch(
                f"{self.api_base}/repos/{owner}/{repo}/git/refs/heads/{branch}",
                json={"sha": new_commit_sha}
            )
            update_ref_response.raise_for_status()
            
            logger.info(f"✅ Pushed {len(files)} files to {branch}")
            return {
                "commit_sha": new_commit_sha,
                "files_count": len(files),
                "branch": branch
            }
        except Exception as e:
            logger.error(f"Failed to push multiple files: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Helper functions for OAuth flow
def generate_github_oauth_url(
    client_id: str,
    redirect_uri: str,
    scope: str = "repo user"
) -> str:
    """
    Generate GitHub OAuth authorization URL
    
    Scopes:
    - repo: Full control of private repositories
    - user: Read user profile data
    """
    return (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )


async def exchange_code_for_token(
    client_id: str,
    client_secret: str,
    code: str
) -> Dict[str, Any]:
    """
    Exchange OAuth code for access token
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()
