"""
Agent Workspace Manager
Provides file system access for all agents
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os
import json
import shutil
from datetime import datetime

class AgentWorkspaceManager:
    """
    Centralized file system manager for all agents
    Handles reading, writing, and backing up files
    """
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent.parent.parent
        self.workspace_dir = self.backend_dir / "workspace"
        self.project_root = self.backend_dir.parent
        self.backup_dir = self.workspace_dir / "backups"
        
        # Ensure directories exist
        self.workspace_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
    def resolve_path(self, file_path: str) -> Optional[Path]:
        """Resolve file path to absolute path"""
        if not file_path:
            return None
            
        # If already absolute
        if Path(file_path).is_absolute():
            path = Path(file_path)
            if path.exists():
                return path
        
        # Try different base directories
        search_paths = [
            Path.cwd() / file_path,
            self.workspace_dir / file_path,
            self.backend_dir / file_path,
            self.project_root / file_path,
        ]
        
        for path in search_paths:
            if path.exists():
                return path.resolve()
        
        return None
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Tuple[bool, str]:
        """
        Read file content
        Returns: (success, content_or_error)
        """
        try:
            resolved = self.resolve_path(file_path)
            if resolved and resolved.is_file():
                content = resolved.read_text(encoding=encoding)
                return True, content
            else:
                # File doesn't exist, check if we should create it
                if not resolved:
                    return False, f"File not found: {file_path}"
                else:
                    return False, f"Path is not a file: {file_path}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    def write_file(self, file_path: str, content: str, 
                   create_backup: bool = True, encoding: str = 'utf-8') -> Tuple[bool, str]:
        """
        Write content to file
        Returns: (success, message)
        """
        try:
            # Resolve or create path
            resolved = self.resolve_path(file_path)
            if not resolved:
                # Create new file in workspace
                if Path(file_path).is_absolute():
                    resolved = Path(file_path)
                else:
                    resolved = self.workspace_dir / file_path
            
            # Create backup if file exists
            backup_path = None
            if resolved.exists() and create_backup:
                backup_path = self.create_backup(resolved)
            
            # Ensure directory exists
            resolved.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            resolved.write_text(content, encoding=encoding)
            
            message = f"File written: {resolved}"
            if backup_path:
                message += f" (backup: {backup_path})"
            
            return True, message
            
        except Exception as e:
            return False, f"Error writing file: {str(e)}"
    
    def create_backup(self, file_path: Path) -> Path:
        """Create timestamped backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def list_files(self, directory: str = "", 
                   pattern: str = "*", 
                   recursive: bool = True) -> List[Dict[str, any]]:
        """List files in directory"""
        try:
            base_dir = self.resolve_path(directory) if directory else self.workspace_dir
            if not base_dir or not base_dir.is_dir():
                return []
            
            files = []
            glob_func = base_dir.rglob if recursive else base_dir.glob
            
            for file_path in glob_func(pattern):
                if file_path.is_file():
                    files.append({
                        "path": str(file_path),
                        "relative": str(file_path.relative_to(base_dir)),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return files
            
        except Exception:
            return []
    
    def get_project_structure(self, max_depth: int = 3) -> Dict[str, any]:
        """Get project directory structure"""
        def build_tree(path: Path, depth: int = 0):
            if depth >= max_depth:
                return None
            
            tree = {
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "path": str(path),
            }
            
            if path.is_dir():
                children = []
                try:
                    for child in sorted(path.iterdir()):
                        # Skip hidden files and common ignore patterns
                        if child.name.startswith('.') or child.name in ['__pycache__', 'node_modules', '.git']:
                            continue
                        child_tree = build_tree(child, depth + 1)
                        if child_tree:
                            children.append(child_tree)
                    tree["children"] = children
                except PermissionError:
                    tree["children"] = []
            
            return tree
        
        return build_tree(self.project_root)
    
    def analyze_file(self, file_path: str) -> Dict[str, any]:
        """Analyze file and return metadata"""
        resolved = self.resolve_path(file_path)
        if not resolved or not resolved.is_file():
            return {"error": "File not found"}
        
        try:
            stat = resolved.stat()
            content = resolved.read_text(encoding='utf-8')
            
            # Count lines and detect language
            lines = content.split('\n')
            language = self._detect_language(resolved.suffix)
            
            # Find TODOs, FIXMEs, etc.
            issues = []
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line or 'BUG' in line or 'HACK' in line:
                    issues.append({"line": i, "content": line.strip()})
            
            return {
                "path": str(resolved),
                "name": resolved.name,
                "size": stat.st_size,
                "lines": len(lines),
                "language": language,
                "issues": issues,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": resolved.suffix
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
        }
        return language_map.get(extension.lower(), 'text')


# Global instance for easy access
agent_workspace = AgentWorkspaceManager()

# Convenience functions
def read_file(file_path: str) -> Tuple[bool, str]:
    """Read file content"""
    return agent_workspace.read_file(file_path)

def write_file(file_path: str, content: str) -> Tuple[bool, str]:
    """Write file content"""
    return agent_workspace.write_file(file_path, content)

def list_files(directory: str = "", pattern: str = "*") -> List[Dict]:
    """List files in directory"""
    return agent_workspace.list_files(directory, pattern)

# Export for external use
__all__ = ['AgentWorkspaceManager', 'agent_workspace', 'read_file', 'write_file', 'list_files']