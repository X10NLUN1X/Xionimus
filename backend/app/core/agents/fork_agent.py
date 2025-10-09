"""Fork Agent using GitHub API"""
import logging
from typing import Dict, Any, Optional
from github import GithubException

from ...models.agent_models import AgentType
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ForkAgent(BaseAgent):
    """
    Fork Agent powered by GitHub API
    Manages repository forking and session forking operations
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.FORK, api_keys=api_keys)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate fork operation input"""
        super()._validate_input(input_data)
        
        operation = input_data.get("operation")
        valid_operations = ["fork_repo", "create_branch", "list_repos", "get_repo_info"]
        
        if not operation:
            raise ValueError(f"Operation is required. Valid operations: {', '.join(valid_operations)}")
        
        if operation not in valid_operations:
            raise ValueError(f"Invalid operation: {operation}. Valid operations: {', '.join(valid_operations)}")
    
    def get_system_prompt(self) -> str:
        """Get fork agent system prompt"""
        return "Fork Agent for GitHub repository operations"
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute fork/repository operation"""
        operation = input_data["operation"]
        
        try:
            if operation == "fork_repo":
                return await self._fork_repository(input_data)
            
            elif operation == "create_branch":
                return await self._create_branch(input_data)
            
            elif operation == "list_repos":
                return await self._list_repositories(input_data)
            
            elif operation == "get_repo_info":
                return await self._get_repository_info(input_data)
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except GithubException as e:
            logger.error(f"GitHub API error: {e.status} - {e.data}")
            raise Exception(f"GitHub API error: {e.status} - {e.data.get('message', str(e))}")
    
    async def _fork_repository(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fork a repository"""
        repo_full_name = input_data.get("repository")  # e.g., "owner/repo"
        
        if not repo_full_name:
            raise ValueError("Repository name is required for fork operation")
        
        # Get the repository
        repo = self.client.get_repo(repo_full_name)
        
        # Fork it
        forked_repo = repo.create_fork()
        
        return {
            "operation": "fork_repo",
            "success": True,
            "original_repo": repo.full_name,
            "forked_repo": forked_repo.full_name,
            "fork_url": forked_repo.html_url,
            "clone_url": forked_repo.clone_url,
            "created_at": forked_repo.created_at.isoformat()
        }
    
    async def _create_branch(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new branch in a repository"""
        repo_name = input_data.get("repository")
        branch_name = input_data.get("branch_name")
        source_branch = input_data.get("source_branch", "main")
        
        if not repo_name or not branch_name:
            raise ValueError("Repository and branch name are required")
        
        repo = self.client.get_repo(repo_name)
        
        # Get source branch ref
        source_ref = repo.get_git_ref(f"heads/{source_branch}")
        
        # Create new branch
        new_ref = repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=source_ref.object.sha
        )
        
        return {
            "operation": "create_branch",
            "success": True,
            "repository": repo_name,
            "branch_name": branch_name,
            "source_branch": source_branch,
            "sha": new_ref.object.sha
        }
    
    async def _list_repositories(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """List user repositories"""
        user = self.client.get_user()
        limit = input_data.get("limit", 10)
        
        repos = user.get_repos()[:limit]
        
        repo_list = [
            {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "private": repo.private,
                "fork": repo.fork,
                "stars": repo.stargazers_count,
                "language": repo.language
            }
            for repo in repos
        ]
        
        return {
            "operation": "list_repos",
            "success": True,
            "user": user.login,
            "repository_count": len(repo_list),
            "repositories": repo_list
        }
    
    async def _get_repository_info(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed repository information"""
        repo_name = input_data.get("repository")
        
        if not repo_name:
            raise ValueError("Repository name is required")
        
        repo = self.client.get_repo(repo_name)
        
        return {
            "operation": "get_repo_info",
            "success": True,
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "private": repo.private,
            "fork": repo.fork,
            "stars": repo.stargazers_count,
            "watchers": repo.watchers_count,
            "forks": repo.forks_count,
            "language": repo.language,
            "default_branch": repo.default_branch,
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat(),
            "size": repo.size,
            "open_issues": repo.open_issues_count
        }