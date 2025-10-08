"""
Advanced Workspace Management for Xionimus AI
Organize projects, templates, and exports
"""

import logging
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import zipfile
import io

logger = logging.getLogger(__name__)

class WorkspaceManager:
    """Manage workspaces, projects, and code organization"""
    
    def __init__(self, base_dir: str = "~/.xionimus_ai/workspaces"):
        """
        Initialize workspace manager
        
        Args:
            base_dir: Base directory for all workspaces
        """
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Templates directory
        self.templates_dir = self.base_dir / "_templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize default templates
        self._init_default_templates()
        
        logger.info(f"Workspace Manager initialized at {self.base_dir}")
    
    def _init_default_templates(self):
        """Create default project templates"""
        templates = {
            "react-app": {
                "name": "React App",
                "description": "React + Vite starter template",
                "files": {
                    "package.json": json.dumps({
                        "name": "react-app",
                        "version": "0.1.0",
                        "scripts": {
                            "dev": "vite",
                            "build": "vite build"
                        },
                        "dependencies": {
                            "react": "^18.2.0",
                            "react-dom": "^18.2.0"
                        }
                    }, indent=2),
                    "src/App.tsx": "import React from 'react'\n\nfunction App() {\n  return <h1>Hello World</h1>\n}\n\nexport default App",
                    "index.html": "<!DOCTYPE html>\n<html>\n<head><title>React App</title></head>\n<body><div id=\"root\"></div></body>\n</html>"
                }
            },
            "python-fastapi": {
                "name": "Python FastAPI",
                "description": "FastAPI + Python starter",
                "files": {
                    "main.py": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'message': 'Hello World'}",
                    "requirements.txt": "fastapi\nuvicorn[standard]",
                    "README.md": "# FastAPI Project\n\nRun: `uvicorn main:app --reload`"
                }
            },
            "blank": {
                "name": "Blank Project",
                "description": "Empty project structure",
                "files": {
                    "README.md": "# New Project\n\nStart building..."
                }
            }
        }
        
        for template_id, template_data in templates.items():
            template_path = self.templates_dir / f"{template_id}.json"
            if not template_path.exists():
                with open(template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)
    
    def create_workspace(
        self,
        name: str,
        template: Optional[str] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new workspace
        
        Args:
            name: Workspace name
            template: Template ID to use
            description: Workspace description
            
        Returns:
            Workspace metadata
        """
        # Sanitize name
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        workspace_path = self.base_dir / safe_name
        
        if workspace_path.exists():
            raise ValueError(f"Workspace '{name}' already exists")
        
        workspace_path.mkdir(parents=True)
        
        # Apply template if specified
        if template:
            self._apply_template(workspace_path, template)
        
        # Create metadata
        metadata = {
            "name": name,
            "id": safe_name,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_modified": datetime.now(timezone.utc).isoformat(),
            "template": template,
            "file_count": 0,
            "size_bytes": 0
        }
        
        # Save metadata
        meta_path = workspace_path / ".xionimus_meta.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Created workspace: {name}")
        return metadata
    
    def _apply_template(self, workspace_path: Path, template_id: str):
        """Apply template files to workspace"""
        template_path = self.templates_dir / f"{template_id}.json"
        
        if not template_path.exists():
            logger.warning(f"Template not found: {template_id}")
            return
        
        with open(template_path) as f:
            template_data = json.load(f)
        
        # Create files from template
        for file_path, content in template_data.get('files', {}).items():
            full_path = workspace_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """List all workspaces"""
        workspaces = []
        
        for workspace_dir in self.base_dir.iterdir():
            if workspace_dir.is_dir() and not workspace_dir.name.startswith('_'):
                meta_path = workspace_dir / ".xionimus_meta.json"
                
                if meta_path.exists():
                    with open(meta_path) as f:
                        metadata = json.load(f)
                    
                    # Update file stats
                    metadata['file_count'] = sum(1 for _ in workspace_dir.rglob('*') if _.is_file())
                    metadata['size_bytes'] = sum(f.stat().st_size for f in workspace_dir.rglob('*') if f.is_file())
                    
                    workspaces.append(metadata)
        
        return sorted(workspaces, key=lambda x: x.get('last_modified', ''), reverse=True)
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace metadata"""
        workspace_path = self.base_dir / workspace_id
        meta_path = workspace_path / ".xionimus_meta.json"
        
        if meta_path.exists():
            with open(meta_path) as f:
                return json.load(f)
        return None
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace"""
        workspace_path = self.base_dir / workspace_id
        
        if workspace_path.exists():
            shutil.rmtree(workspace_path)
            logger.info(f"Deleted workspace: {workspace_id}")
            return True
        return False
    
    def export_workspace(self, workspace_id: str) -> bytes:
        """
        Export workspace as ZIP file
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            ZIP file bytes
        """
        workspace_path = self.base_dir / workspace_id
        
        if not workspace_path.exists():
            raise ValueError(f"Workspace not found: {workspace_id}")
        
        # Create ZIP in memory
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in workspace_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.xionimus'):
                    arcname = file_path.relative_to(workspace_path)
                    zipf.write(file_path, arcname)
        
        buffer.seek(0)
        logger.info(f"Exported workspace: {workspace_id}")
        return buffer.getvalue()
    
    def import_workspace(
        self,
        name: str,
        zip_data: bytes,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Import workspace from ZIP file
        
        Args:
            name: Workspace name
            zip_data: ZIP file bytes
            description: Description
            
        Returns:
            Workspace metadata
        """
        # Create workspace
        workspace_meta = self.create_workspace(name, description=description)
        workspace_path = self.base_dir / workspace_meta['id']
        
        # Extract ZIP
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zipf:
            zipf.extractall(workspace_path)
        
        logger.info(f"Imported workspace: {name}")
        return workspace_meta
    
    def get_workspace_files(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all files in workspace"""
        workspace_path = self.base_dir / workspace_id
        
        if not workspace_path.exists():
            return []
        
        files = []
        for file_path in workspace_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.xionimus'):
                rel_path = file_path.relative_to(workspace_path)
                files.append({
                    'path': str(rel_path),
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).isoformat()
                })
        
        return sorted(files, key=lambda x: x['path'])
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates"""
        templates = []
        
        for template_file in self.templates_dir.glob('*.json'):
            with open(template_file) as f:
                template_data = json.load(f)
                templates.append({
                    'id': template_file.stem,
                    'name': template_data.get('name', template_file.stem),
                    'description': template_data.get('description', ''),
                    'file_count': len(template_data.get('files', {}))
                })
        
        return templates
    
    def get_stats(self) -> Dict[str, Any]:
        """Get workspace manager statistics"""
        workspaces = self.list_workspaces()
        total_size = sum(w.get('size_bytes', 0) for w in workspaces)
        total_files = sum(w.get('file_count', 0) for w in workspaces)
        
        return {
            'workspace_count': len(workspaces),
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'base_directory': str(self.base_dir),
            'template_count': len(list(self.templates_dir.glob('*.json')))
        }
