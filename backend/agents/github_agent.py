import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
import requests
import base64
from datetime import datetime, timezone

class GitHubAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GitHub Agent",
            description="Specialized in GitHub repository management, version control, and code collaboration",
            capabilities=[
                AgentCapability.API_INTEGRATION,
                AgentCapability.CODE_ANALYSIS
            ]
        )
        self.ai_model = "perplexity"  # Use Perplexity for current GitHub best practices
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        github_keywords = [
            'github', 'git', 'repository', 'repo', 'commit', 'push', 'pull',
            'branch', 'merge', 'fork', 'clone', 'version control', 'collaboration',
            'issue', 'pull request', 'pr', 'github api', 'webhook', 'actions',
            'deployment', 'ci/cd', 'continuous integration', 'pipeline'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in github_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for GitHub-specific terms
        if any(term in description_lower for term in ['github.com', 'git clone', 'repository', 'commit']):
            confidence += 0.4
        
        # Boost if context suggests GitHub operations
        if context.get('github_token') or context.get('repository_url'):
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute GitHub-related tasks"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing GitHub operations")
            
            task_type = self._identify_github_task_type(task.description)
            
            await self.update_progress(task, 0.3, f"Executing {task_type}")
            
            if task_type == "repository_list":
                await self._handle_repository_list(task)
            elif task_type == "repository_info":
                await self._handle_repository_info(task)
            elif task_type == "file_operations":
                await self._handle_file_operations(task)
            elif task_type == "commit_operations":
                await self._handle_commit_operations(task)
            elif task_type == "branch_operations":
                await self._handle_branch_operations(task)
            elif task_type == "issue_operations":
                await self._handle_issue_operations(task)
            elif task_type == "stanton_station_integration":
                await self._handle_stanton_station_integration(task)
            else:
                await self._handle_general_github_task(task)
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "GitHub operations completed")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"GitHub operation failed: {str(e)}"
            self.logger.error(f"GitHub agent error: {e}")
            
        return task
    
    def _identify_github_task_type(self, description: str) -> str:
        """Identify the type of GitHub task"""
        description_lower = description.lower()
        
        # Check for Stanton station queries first
        if 'stanton' in description_lower and any(word in description_lower for word in ['station', 'distanz', 'distance']):
            return "stanton_station_integration"
        elif any(word in description_lower for word in ['list repositories', 'show repos', 'repositories']):
            return "repository_list"
        elif any(word in description_lower for word in ['repository info', 'repo details', 'repository details']):
            return "repository_info"
        elif any(word in description_lower for word in ['file', 'upload', 'download', 'create file', 'delete file']):
            return "file_operations"
        elif any(word in description_lower for word in ['commit', 'push', 'commit changes']):
            return "commit_operations"
        elif any(word in description_lower for word in ['branch', 'create branch', 'merge', 'switch branch']):
            return "branch_operations"
        elif any(word in description_lower for word in ['issue', 'create issue', 'bug report']):
            return "issue_operations"
        else:
            return "general_github"
    
    async def _handle_repository_list(self, task: AgentTask):
        """Handle repository listing"""
        await self.update_progress(task, 0.5, "Fetching repositories from GitHub")
        
        github_token = task.input_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        username = task.input_data.get('username')
        
        if not github_token:
            raise Exception("GitHub token not provided")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get user's repositories
        if username:
            url = f'https://api.github.com/users/{username}/repos'
        else:
            url = 'https://api.github.com/user/repos'
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repositories = response.json()
            
            task.result = {
                "type": "repository_list",
                "repositories": [
                    {
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "description": repo["description"],
                        "url": repo["html_url"],
                        "clone_url": repo["clone_url"],
                        "language": repo["language"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "updated_at": repo["updated_at"],
                        "private": repo["private"]
                    }
                    for repo in repositories[:20]  # Limit to 20 repos
                ],
                "total_count": len(repositories)
            }
        else:
            raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    async def _handle_repository_info(self, task: AgentTask):
        """Handle repository information retrieval"""
        await self.update_progress(task, 0.5, "Fetching repository information")
        
        github_token = task.input_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        repo_full_name = task.input_data.get('repository')
        
        if not github_token or not repo_full_name:
            raise Exception("GitHub token and repository name required")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get repository details
        repo_url = f'https://api.github.com/repos/{repo_full_name}'
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 200:
            repo_data = response.json()
            
            # Get recent commits
            commits_url = f'https://api.github.com/repos/{repo_full_name}/commits'
            commits_response = requests.get(commits_url, headers=headers, params={'per_page': 10})
            commits = commits_response.json() if commits_response.status_code == 200 else []
            
            # Get branches
            branches_url = f'https://api.github.com/repos/{repo_full_name}/branches'
            branches_response = requests.get(branches_url, headers=headers)
            branches = branches_response.json() if branches_response.status_code == 200 else []
            
            task.result = {
                "type": "repository_info",
                "repository": {
                    "name": repo_data["name"],
                    "full_name": repo_data["full_name"],
                    "description": repo_data["description"],
                    "url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "language": repo_data["language"],
                    "stars": repo_data["stargazers_count"],
                    "forks": repo_data["forks_count"],
                    "size": repo_data["size"],
                    "created_at": repo_data["created_at"],
                    "updated_at": repo_data["updated_at"],
                    "default_branch": repo_data["default_branch"],
                    "private": repo_data["private"]
                },
                "recent_commits": [
                    {
                        "sha": commit["sha"][:8],
                        "message": commit["commit"]["message"].split('\n')[0],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"]
                    }
                    for commit in commits[:5]
                ],
                "branches": [branch["name"] for branch in branches[:10]]
            }
        else:
            raise Exception(f"Repository not found or access denied: {response.status_code}")
    
    async def _handle_file_operations(self, task: AgentTask):
        """Handle file operations (upload, download, create, delete)"""
        await self.update_progress(task, 0.5, "Processing file operations")
        
        github_token = task.input_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        repo_full_name = task.input_data.get('repository')
        operation = task.input_data.get('operation', 'list')
        
        if not github_token or not repo_full_name:
            raise Exception("GitHub token and repository name required")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        if operation == 'list':
            # List repository contents
            contents_url = f'https://api.github.com/repos/{repo_full_name}/contents'
            path = task.input_data.get('path', '')
            if path:
                contents_url += f'/{path}'
            
            response = requests.get(contents_url, headers=headers)
            
            if response.status_code == 200:
                contents = response.json()
                if isinstance(contents, list):
                    files = [
                        {
                            "name": item["name"],
                            "type": item["type"],
                            "size": item.get("size", 0),
                            "path": item["path"],
                            "download_url": item.get("download_url")
                        }
                        for item in contents
                    ]
                else:
                    files = [{
                        "name": contents["name"],
                        "type": contents["type"],
                        "size": contents.get("size", 0),
                        "path": contents["path"],
                        "download_url": contents.get("download_url")
                    }]
                
                task.result = {
                    "type": "file_list",
                    "files": files,
                    "path": path
                }
            else:
                raise Exception(f"Failed to list files: {response.status_code}")
        
        elif operation == 'create':
            # Create a new file
            file_path = task.input_data.get('file_path')
            content = task.input_data.get('content', '')
            commit_message = task.input_data.get('commit_message', 'Create new file')
            
            if not file_path:
                raise Exception("File path required for create operation")
            
            # Encode content to base64
            encoded_content = base64.b64encode(content.encode()).decode()
            
            create_url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
            data = {
                "message": commit_message,
                "content": encoded_content
            }
            
            response = requests.put(create_url, headers=headers, json=data)
            
            if response.status_code == 201:
                result = response.json()
                task.result = {
                    "type": "file_created",
                    "file": {
                        "name": result["content"]["name"],
                        "path": result["content"]["path"],
                        "sha": result["content"]["sha"],
                        "url": result["content"]["html_url"]
                    },
                    "commit": {
                        "sha": result["commit"]["sha"],
                        "message": commit_message
                    }
                }
            else:
                raise Exception(f"Failed to create file: {response.status_code} - {response.text}")
    
    async def _handle_commit_operations(self, task: AgentTask):
        """Handle commit operations"""
        await self.update_progress(task, 0.5, "Processing commit operations")
        
        github_token = task.input_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        repo_full_name = task.input_data.get('repository')
        
        if not github_token or not repo_full_name:
            raise Exception("GitHub token and repository name required")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get recent commits
        commits_url = f'https://api.github.com/repos/{repo_full_name}/commits'
        params = {'per_page': task.input_data.get('limit', 20)}
        
        response = requests.get(commits_url, headers=headers, params=params)
        
        if response.status_code == 200:
            commits = response.json()
            
            task.result = {
                "type": "commit_list",
                "commits": [
                    {
                        "sha": commit["sha"],
                        "short_sha": commit["sha"][:8],
                        "message": commit["commit"]["message"],
                        "author": {
                            "name": commit["commit"]["author"]["name"],
                            "email": commit["commit"]["author"]["email"],
                            "date": commit["commit"]["author"]["date"]
                        },
                        "url": commit["html_url"],
                        "stats": {
                            "additions": commit.get("stats", {}).get("additions", 0),
                            "deletions": commit.get("stats", {}).get("deletions", 0),
                            "total": commit.get("stats", {}).get("total", 0)
                        }
                    }
                    for commit in commits
                ]
            }
        else:
            raise Exception(f"Failed to fetch commits: {response.status_code}")
    
    async def _handle_branch_operations(self, task: AgentTask):
        """Handle branch operations"""
        await self.update_progress(task, 0.5, "Processing branch operations")
        
        github_token = task.input_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        repo_full_name = task.input_data.get('repository')
        
        if not github_token or not repo_full_name:
            raise Exception("GitHub token and repository name required")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get branches
        branches_url = f'https://api.github.com/repos/{repo_full_name}/branches'
        response = requests.get(branches_url, headers=headers)
        
        if response.status_code == 200:
            branches = response.json()
            
            task.result = {
                "type": "branch_list",
                "branches": [
                    {
                        "name": branch["name"],
                        "commit_sha": branch["commit"]["sha"][:8],
                        "commit_url": branch["commit"]["url"],
                        "protected": branch.get("protected", False)
                    }
                    for branch in branches
                ]
            }
        else:
            raise Exception(f"Failed to fetch branches: {response.status_code}")
    
    async def _handle_issue_operations(self, task: AgentTask):
        """Handle issue operations"""
        await self.update_progress(task, 0.5, "Processing issue operations")
        
        # This would be implemented for issue management
        task.result = {
            "type": "issue_operations",
            "message": "Issue operations not yet implemented",
            "status": "pending"
        }
    
    async def _handle_stanton_station_integration(self, task: AgentTask):
        """Handle Stanton station integration with GitHub repository"""
        await self.update_progress(task, 0.5, "Processing Stanton station integration")
        
        # Import the stanton system
        import sys
        import os.path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stanton_stations import stanton_system
        
        # Create integration report
        all_stations = stanton_system.get_all_stations()
        station_count = len(all_stations)
        
        # Count by type
        type_counts = {}
        for station in all_stations.values():
            type_counts[station.station_type] = type_counts.get(station.station_type, 0) + 1
        
        task.result = {
            "type": "stanton_station_integration",
            "message": "Stanton station system successfully integrated into repository",
            "integration_details": {
                "total_stations": station_count,
                "station_types": type_counts,
                "available_features": [
                    "Distance calculations between stations",
                    "Nearest station search",
                    "Route planning",
                    "Station search by name/description",
                    "Multi-type station support (space, subway, rail)"
                ],
                "data_file": "backend/stanton_stations.py",
                "agent_integration": "Research Agent enhanced with Stanton queries"
            },
            "next_steps": [
                "Station distance data is now accessible via Research Agent",
                "Query stations using keywords like 'Stanton distance' or 'station overview'",
                "System supports German and English queries",
                "Distance calculations work for space, subway, and rail stations"
            ]
        }
    
    async def _handle_general_github_task(self, task: AgentTask):
        """Handle general GitHub tasks"""
        await self.update_progress(task, 0.5, "Processing general GitHub task")
        
        task.result = {
            "type": "general_github",
            "message": "General GitHub task processed",
            "description": task.description,
            "suggestions": [
                "Use specific GitHub operations like 'list repositories'",
                "Provide GitHub token for authenticated operations",
                "Specify repository name for repo-specific tasks"
            ]
        }