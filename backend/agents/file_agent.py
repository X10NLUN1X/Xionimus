import re
import os
import uuid
import shutil
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
from pathlib import Path
import mimetypes
import zipfile
import json
from datetime import datetime, timezone

class FileAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="File Agent",
            description="Specialized in file management, upload, download, and organization",
            capabilities=[
                AgentCapability.API_INTEGRATION
            ]
        )
        self.ai_model = "claude"  # Use Claude for file analysis and organization
        # Windows lokaler Pfad statt Docker
        self.upload_dir = Path.cwd() / "uploads"
        self.upload_dir.mkdir(exist_ok=True)
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        file_keywords = [
            'file', 'upload', 'download', 'organize', 'manage files',
            'file system', 'directory', 'folder', 'archive', 'zip',
            'import', 'export', 'attach', 'attachment', 'document',
            'datei', 'hochladen', 'herunterladen', 'organisieren'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in file_keywords if keyword in description_lower)
        confidence = min(matches / 2, 1.0)
        
        # Boost confidence for file-specific operations
        if any(term in description_lower for term in ['upload file', 'manage files', 'file upload']):
            confidence += 0.4
        
        # Boost if context suggests file operations
        if context.get('files') or context.get('file_data'):
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute file-related tasks"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing file operations")
            
            task_type = self._identify_file_task_type(task.description)
            
            await self.update_progress(task, 0.3, f"Executing {task_type}")
            
            if task_type == "upload":
                await self._handle_file_upload(task)
            elif task_type == "download":
                await self._handle_file_download(task)
            elif task_type == "organize":
                await self._handle_file_organization(task)
            elif task_type == "analyze":
                await self._handle_file_analysis(task)
            elif task_type == "archive":
                await self._handle_file_archive(task)
            elif task_type == "list":
                await self._handle_file_listing(task)
            else:
                await self._handle_general_file_task(task)
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "File operations completed")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"File operation failed: {str(e)}"
            self.logger.error(f"File agent error: {e}")
            
        return task
    
    def _identify_file_task_type(self, description: str) -> str:
        """Identify the type of file task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['upload', 'hochladen', 'attach']):
            return "upload"
        elif any(word in description_lower for word in ['download', 'herunterladen', 'export']):
            return "download"
        elif any(word in description_lower for word in ['organize', 'sort', 'manage', 'organisieren']):
            return "organize"
        elif any(word in description_lower for word in ['analyze', 'analyse', 'examine', 'inspect']):
            return "analyze"
        elif any(word in description_lower for word in ['archive', 'zip', 'compress', 'archiv']):
            return "archive"
        elif any(word in description_lower for word in ['list', 'show files', 'directory', 'auflisten']):
            return "list"
        else:
            return "general_file"
    
    async def _handle_file_upload(self, task: AgentTask):
        """Handle file upload operations"""
        await self.update_progress(task, 0.5, "Processing file upload")
        
        files_data = task.input_data.get('files', [])
        if not files_data:
            raise Exception("No files provided for upload")
        
        uploaded_files = []
        project_id = task.input_data.get('project_id')
        
        for file_data in files_data:
            file_id = str(uuid.uuid4())
            filename = file_data.get('name', f'file_{file_id}')
            content = file_data.get('content', '')
            file_type = file_data.get('type', 'text/plain')
            
            # Create project-specific directory if project_id provided
            if project_id:
                file_dir = self.upload_dir / project_id
                file_dir.mkdir(exist_ok=True)
            else:
                file_dir = self.upload_dir
            
            file_path = file_dir / f"{file_id}_{filename}"
            
            # Save file
            if isinstance(content, str):
                file_path.write_text(content, encoding='utf-8')
            else:
                file_path.write_bytes(content)
            
            file_info = {
                "id": file_id,
                "name": filename,
                "path": str(file_path),
                "type": file_type,
                "size": file_path.stat().st_size,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "project_id": project_id
            }
            
            uploaded_files.append(file_info)
        
        task.result = {
            "type": "file_upload",
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "total_size": sum(f["size"] for f in uploaded_files)
        }
    
    async def _handle_file_download(self, task: AgentTask):
        """Handle file download operations"""
        await self.update_progress(task, 0.5, "Preparing file download")
        
        file_ids = task.input_data.get('file_ids', [])
        if not file_ids:
            raise Exception("No file IDs provided for download")
        
        download_files = []
        
        for file_id in file_ids:
            # Find file by ID (this would be improved with a proper database)
            file_found = False
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    if file.startswith(file_id):
                        file_path = Path(root) / file
                        original_name = file[len(file_id) + 1:]  # Remove ID prefix
                        
                        file_info = {
                            "id": file_id,
                            "name": original_name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "type": mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
                        }
                        
                        # Read file content for small files
                        if file_path.stat().st_size < 10 * 1024 * 1024:  # 10MB limit
                            try:
                                if file_info["type"].startswith('text/'):
                                    file_info["content"] = file_path.read_text(encoding='utf-8')
                                else:
                                    file_info["content_base64"] = True
                            except:
                                file_info["content"] = None
                        
                        download_files.append(file_info)
                        file_found = True
                        break
                
                if file_found:
                    break
        
        task.result = {
            "type": "file_download",
            "files": download_files,
            "total_files": len(download_files)
        }
    
    async def _handle_file_organization(self, task: AgentTask):
        """Handle file organization operations"""
        await self.update_progress(task, 0.5, "Organizing files")
        
        project_id = task.input_data.get('project_id')
        organization_type = task.input_data.get('organization_type', 'by_type')
        
        if not project_id:
            raise Exception("Project ID required for organization")
        
        project_dir = self.upload_dir / project_id
        if not project_dir.exists():
            raise Exception("Project directory not found")
        
        organized_files = {}
        
        if organization_type == 'by_type':
            # Organize by file type
            for file_path in project_dir.glob('*'):
                if file_path.is_file():
                    file_type = mimetypes.guess_type(str(file_path))[0] or 'unknown'
                    category = self._get_file_category(file_type)
                    
                    if category not in organized_files:
                        organized_files[category] = []
                    
                    organized_files[category].append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "type": file_type,
                        "size": file_path.stat().st_size
                    })
        
        elif organization_type == 'by_date':
            # Organize by creation date
            for file_path in project_dir.glob('*'):
                if file_path.is_file():
                    creation_date = datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d')
                    
                    if creation_date not in organized_files:
                        organized_files[creation_date] = []
                    
                    organized_files[creation_date].append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "created_at": creation_date
                    })
        
        task.result = {
            "type": "file_organization",
            "organization_type": organization_type,
            "organized_files": organized_files,
            "total_categories": len(organized_files)
        }
    
    async def _handle_file_analysis(self, task: AgentTask):
        """Handle file analysis operations"""
        await self.update_progress(task, 0.5, "Analyzing files")
        
        file_paths = task.input_data.get('file_paths', [])
        if not file_paths:
            raise Exception("No file paths provided for analysis")
        
        analysis_results = []
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue
            
            file_analysis = {
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "type": mimetypes.guess_type(str(file_path))[0] or 'unknown',
                "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "category": self._get_file_category(mimetypes.guess_type(str(file_path))[0] or 'unknown')
            }
            
            # Additional analysis for text files
            if file_analysis["type"].startswith('text/') and file_path.stat().st_size < 1024 * 1024:  # 1MB limit
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_analysis["line_count"] = len(content.split('\n'))
                    file_analysis["word_count"] = len(content.split())
                    file_analysis["char_count"] = len(content)
                except:
                    pass
            
            analysis_results.append(file_analysis)
        
        task.result = {
            "type": "file_analysis",
            "analyzed_files": analysis_results,
            "total_files": len(analysis_results),
            "total_size": sum(f["size"] for f in analysis_results)
        }
    
    async def _handle_file_archive(self, task: AgentTask):
        """Handle file archiving operations"""
        await self.update_progress(task, 0.5, "Creating archive")
        
        project_id = task.input_data.get('project_id')
        archive_name = task.input_data.get('archive_name', f'archive_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        if not project_id:
            raise Exception("Project ID required for archiving")
        
        project_dir = self.upload_dir / project_id
        if not project_dir.exists():
            raise Exception("Project directory not found")
        
        archive_path = self.upload_dir / f"{archive_name}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_dir.rglob('*'):
                if file_path.is_file():
                    # Add file to archive with relative path
                    arcname = file_path.relative_to(project_dir)
                    zipf.write(file_path, arcname)
        
        task.result = {
            "type": "file_archive",
            "archive_path": str(archive_path),
            "archive_name": f"{archive_name}.zip",
            "archive_size": archive_path.stat().st_size,
            "files_archived": len(list(project_dir.rglob('*')))
        }
    
    async def _handle_file_listing(self, task: AgentTask):
        """Handle file listing operations"""
        await self.update_progress(task, 0.5, "Listing files")
        
        project_id = task.input_data.get('project_id')
        
        if project_id:
            list_dir = self.upload_dir / project_id
        else:
            list_dir = self.upload_dir
        
        if not list_dir.exists():
            raise Exception("Directory not found")
        
        file_list = []
        
        for file_path in list_dir.glob('*'):
            if file_path.is_file():
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "type": mimetypes.guess_type(str(file_path))[0] or 'unknown',
                    "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                file_list.append(file_info)
        
        task.result = {
            "type": "file_listing",
            "files": file_list,
            "total_files": len(file_list),
            "directory": str(list_dir)
        }
    
    async def _handle_general_file_task(self, task: AgentTask):
        """Handle general file tasks"""
        await self.update_progress(task, 0.5, "Processing general file task")
        
        task.result = {
            "type": "general_file",
            "message": "General file task processed",
            "description": task.description,
            "suggestions": [
                "Use specific file operations like 'upload files'",
                "Provide file data or file IDs for operations",
                "Specify project ID for project-specific file management"
            ]
        }
    
    def _get_file_category(self, mime_type: str) -> str:
        """Categorize file based on MIME type"""
        if mime_type.startswith('image/'):
            return 'images'
        elif mime_type.startswith('video/'):
            return 'videos'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('text/') or mime_type in ['application/json', 'application/xml']:
            return 'documents'
        elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-tar']:
            return 'archives'
        elif 'pdf' in mime_type:
            return 'pdfs'
        elif any(ext in mime_type for ext in ['word', 'excel', 'powerpoint']):
            return 'office'
        else:
            return 'other'