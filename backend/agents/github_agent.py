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
            
            # Check for specific operations first
            if task.input_data.get("operation") == "push_files":
                await self._handle_push_files_operation(task)
            else:
                task_type = self._identify_github_task_type(task.description)
                
                await self.update_progress(task, 0.3, f"Executing {task_type}")
                
                if task_type == "github_debugging":
                    await self._handle_github_debugging(task)
                elif task_type == "repository_analysis":
                    await self._handle_repository_analysis(task)
                elif task_type == "repository_list":
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
        
        # Check for debugging requests (German and English)
        if any(word in description_lower for word in ['debugging', 'debug', 'fehler', 'error', 'problem', 'issue', 'bug']):
            if any(word in description_lower for word in ['github', 'git', 'laden', 'load', 'loading']):
                return "github_debugging"
        
        # Check for GitHub URLs
        if 'github.com' in description_lower or description.startswith('https://github.com/'):
            return "repository_analysis"
        
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
        
        description = task.description.lower()
        is_german = any(word in description for word in ['beim', 'fehler', 'laden', 'github', 'git'])
        
        if is_german:
            task.result = {
                "type": "general_github",
                "message": "Allgemeine GitHub-Anfrage verarbeitet",
                "description": task.description,
                "suggestions": [
                    "Für Repository-Informationen: Geben Sie eine GitHub-URL an",
                    "Für Debugging: Beschreiben Sie das spezifische Problem",
                    "Für API-Operationen: GitHub Personal Access Token bereitstellen",
                    "Unterstützte Operationen: Repository-Analyse, Datei-Operationen, Commit-Verlauf"
                ],
                "examples": [
                    "https://github.com/username/repository - Analysiert das Repository",
                    "GitHub laden funktioniert nicht - Startet Debugging-Hilfe",
                    "Liste meine Repositories - Zeigt Ihre GitHub-Repositories"
                ]
            }
        else:
            task.result = {
                "type": "general_github",
                "message": "General GitHub task processed",
                "description": task.description,
                "suggestions": [
                    "For repository information: Provide a GitHub URL",
                    "For debugging: Describe the specific problem",
                    "For API operations: Provide GitHub Personal Access Token", 
                    "Supported operations: Repository analysis, file operations, commit history"
                ],
                "examples": [
                    "https://github.com/username/repository - Analyzes the repository",
                    "GitHub loading not working - Starts debugging assistance",
                    "List my repositories - Shows your GitHub repositories"
                ]
            }
    
    async def _handle_push_files_operation(self, task: AgentTask):
        """Handle pushing multiple files to GitHub repository"""
        await self.update_progress(task, 0.1, "Starting file push operation")
        
        github_token = task.input_data.get('github_token') or os.environ.get('GITHUB_TOKEN')
        repo_full_name = task.input_data.get('repository')
        branch = task.input_data.get('branch', 'main')
        files = task.input_data.get('files', [])
        commit_message = task.input_data.get('commit_message', 'Add generated files')
        
        if not github_token or not repo_full_name:
            raise Exception("GitHub token and repository name required for push operation")
        
        if not files:
            raise Exception("No files provided for push operation")
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        await self.update_progress(task, 0.3, f"Pushing {len(files)} files to {repo_full_name}/{branch}")
        
        pushed_files = []
        failed_files = []
        
        for i, file_info in enumerate(files):
            try:
                file_path = file_info.get('path') or file_info.get('name')
                content = file_info.get('content', '')
                
                if not file_path:
                    failed_files.append({"error": "No file path provided", "file": file_info})
                    continue
                
                # Check if file exists first
                check_url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
                check_response = requests.get(check_url, headers=headers)
                
                # Encode content to base64
                encoded_content = base64.b64encode(content.encode()).decode()
                
                # Prepare data for file creation/update
                data = {
                    "message": commit_message,
                    "content": encoded_content,
                    "branch": branch
                }
                
                # If file exists, we need the SHA for update
                if check_response.status_code == 200:
                    existing_file = check_response.json()
                    data["sha"] = existing_file["sha"]
                    operation = "update"
                else:
                    operation = "create"
                
                # Create or update the file
                response = requests.put(check_url, headers=headers, json=data)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    pushed_files.append({
                        "path": file_path,
                        "operation": operation,
                        "sha": result["content"]["sha"],
                        "url": result["content"]["html_url"],
                        "size": len(content)
                    })
                    
                    # Update progress
                    progress = 0.3 + (0.6 * (i + 1) / len(files))
                    await self.update_progress(task, progress, f"Pushed {file_path} ({i+1}/{len(files)})")
                    
                else:
                    failed_files.append({
                        "path": file_path,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "file": file_info
                    })
                
            except Exception as e:
                failed_files.append({
                    "path": file_info.get('path', 'unknown'),
                    "error": str(e),
                    "file": file_info
                })
        
        await self.update_progress(task, 1.0, f"Push operation complete: {len(pushed_files)} successful, {len(failed_files)} failed")
        
        # Prepare final result
        task.result = {
            "type": "push_files_complete",
            "repository": repo_full_name,
            "branch": branch,
            "commit_message": commit_message,
            "total_files": len(files),
            "pushed_files": pushed_files,
            "failed_files": failed_files,
            "success_count": len(pushed_files),
            "failure_count": len(failed_files),
            "success": len(failed_files) == 0
        }

    async def _handle_github_debugging(self, task: AgentTask):
        """Handle GitHub debugging requests"""
        await self.update_progress(task, 0.5, "Analyzing GitHub debugging request")
        
        description = task.description.lower()
        
        # Detect language for proper response
        is_german = any(word in description for word in ['beim', 'fehler', 'laden', 'debugging', 'der', 'die', 'das', 'hat', 'wieder', 'einen', 'eine', 'ein', 'und', 'mit', 'ist', 'nicht'])
        
        # Common GitHub issues and solutions
        common_issues = {
            "authentication": {
                "de": {
                    "issue": "GitHub-Authentifizierung fehlgeschlagen",
                    "solutions": [
                        "GitHub Personal Access Token überprüfen",
                        "Token-Berechtigungen kontrollieren (repo, read:user)",
                        "Token ist möglicherweise abgelaufen",
                        "Zwei-Faktor-Authentifizierung richtig konfiguriert?"
                    ]
                },
                "en": {
                    "issue": "GitHub authentication failed",
                    "solutions": [
                        "Check GitHub Personal Access Token",
                        "Verify token permissions (repo, read:user)",
                        "Token may be expired",
                        "Two-factor authentication properly configured?"
                    ]
                }
            },
            "network": {
                "de": {
                    "issue": "Netzwerk-/Verbindungsprobleme",
                    "solutions": [
                        "Internetverbindung prüfen",
                        "Firewall-Einstellungen kontrollieren",
                        "GitHub API-Status überprüfen (status.github.com)",
                        "DNS-Einstellungen prüfen"
                    ]
                },
                "en": {
                    "issue": "Network/connection problems",
                    "solutions": [
                        "Check internet connection",
                        "Verify firewall settings",
                        "Check GitHub API status (status.github.com)",
                        "Verify DNS settings"
                    ]
                }
            },
            "repository": {
                "de": {
                    "issue": "Repository-Zugriffsprobleme",
                    "solutions": [
                        "Repository-Name korrekt geschrieben?",
                        "Repository ist öffentlich oder Sie haben Zugriff?",
                        "Repository-URL format: owner/repository-name",
                        "Organisationsberechtigungen prüfen"
                    ]
                },
                "en": {
                    "issue": "Repository access problems",
                    "solutions": [
                        "Repository name spelled correctly?",
                        "Repository is public or you have access?",
                        "Repository URL format: owner/repository-name",
                        "Check organization permissions"
                    ]
                }
            }
        }
        
        # Determine most likely issue based on description
        likely_issues = []
        if any(word in description for word in ['token', 'auth', 'login', 'access']):
            likely_issues.append("authentication")
        if any(word in description for word in ['network', 'connection', 'timeout', 'connect']):
            likely_issues.append("network")
        if any(word in description for word in ['repository', 'repo', 'not found', '404']):
            likely_issues.append("repository")
        
        if not likely_issues:
            likely_issues = ["authentication", "network", "repository"]  # Show all if unclear
        
        lang = "de" if is_german else "en"
        
        debugging_info = {
            "detected_language": lang,
            "analysis": "GitHub-Debugging-Analyse" if is_german else "GitHub debugging analysis",
            "common_solutions": []
        }
        
        for issue_type in likely_issues:
            issue_info = common_issues[issue_type][lang]
            debugging_info["common_solutions"].append({
                "category": issue_info["issue"],
                "solutions": issue_info["solutions"]
            })
        
        task.result = {
            "type": "github_debugging",
            "message": "GitHub-Debugging-Informationen bereitgestellt" if is_german else "GitHub debugging information provided",
            "debugging_info": debugging_info,
            "next_steps": [
                "Überprüfen Sie die häufigsten Lösungen oben" if is_german else "Review the common solutions above",
                "Testen Sie mit einem einfachen GitHub API-Aufruf" if is_german else "Test with a simple GitHub API call",
                "Kontaktieren Sie den Support mit spezifischen Fehlermeldungen" if is_german else "Contact support with specific error messages"
            ]
        }

    async def _handle_repository_analysis(self, task: AgentTask):
        """Handle repository URL analysis"""
        await self.update_progress(task, 0.5, "Analyzing repository URL")
        
        description = task.description
        
        # Extract GitHub URL
        github_url = None
        if 'github.com' in description:
            # Extract URL from description
            import re
            url_pattern = r'https://github\.com/([^/\s]+)/([^/\s\.]+)'
            match = re.search(url_pattern, description)
            if match:
                owner = match.group(1)
                repo = match.group(2)
                github_url = f"https://github.com/{owner}/{repo}"
                repo_full_name = f"{owner}/{repo}"
            else:
                # Try to extract from .git URL
                git_pattern = r'https://github\.com/([^/\s]+)/([^/\s]+)\.git'
                match = re.search(git_pattern, description)
                if match:
                    owner = match.group(1)
                    repo = match.group(2)
                    github_url = f"https://github.com/{owner}/{repo}"
                    repo_full_name = f"{owner}/{repo}"
        
        if not github_url:
            task.result = {
                "type": "repository_analysis_error",
                "message": "Could not extract valid GitHub repository URL",
                "suggestion": "Please provide a valid GitHub URL in format: https://github.com/owner/repository"
            }
            return
        
        # Try to get basic repository info without authentication
        try:
            response = requests.get(f'https://api.github.com/repos/{repo_full_name}')
            
            if response.status_code == 200:
                repo_data = response.json()
                
                task.result = {
                    "type": "repository_analysis_success",
                    "repository": {
                        "url": github_url,
                        "name": repo_data["name"],
                        "full_name": repo_data["full_name"],
                        "description": repo_data["description"],
                        "language": repo_data["language"],
                        "stars": repo_data["stargazers_count"],
                        "forks": repo_data["forks_count"],
                        "size": repo_data["size"],
                        "created_at": repo_data["created_at"],
                        "updated_at": repo_data["updated_at"],
                        "default_branch": repo_data["default_branch"],
                        "private": repo_data["private"],
                        "archived": repo_data["archived"]
                    },
                    "analysis": {
                        "status": "Repository accessible",
                        "accessibility": "Public" if not repo_data["private"] else "Private",
                        "activity": "Active" if not repo_data["archived"] else "Archived",
                        "primary_language": repo_data["language"] or "Not specified"
                    },
                    "suggestions": [
                        "Repository is accessible and can be cloned",
                        "Use 'git clone " + github_url + ".git' to clone locally",
                        "For API operations, provide a GitHub token for better rate limits"
                    ]
                }
            elif response.status_code == 404:
                task.result = {
                    "type": "repository_analysis_error",
                    "message": "Repository not found or not accessible",
                    "repository_url": github_url,
                    "suggestions": [
                        "Check if repository name is spelled correctly",
                        "Repository might be private - provide GitHub token for access",
                        "Repository might have been moved or deleted",
                        "Check if you have access to this repository"
                    ]
                }
            else:
                task.result = {
                    "type": "repository_analysis_error",
                    "message": f"GitHub API returned status {response.status_code}",
                    "repository_url": github_url,
                    "suggestions": [
                        "GitHub API might be experiencing issues",
                        "Try again in a few minutes",
                        "Check GitHub status at status.github.com"
                    ]
                }
                
        except Exception as e:
            task.result = {
                "type": "repository_analysis_error",
                "message": f"Error analyzing repository: {str(e)}",
                "repository_url": github_url,
                "suggestions": [
                    "Check your internet connection",
                    "GitHub might be temporarily unavailable",
                    "Try accessing the repository directly in a browser"
                ]
            }