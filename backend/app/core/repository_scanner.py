"""
Repository Scanner - Scans codebase for review
Finds all relevant code files in the repository
"""
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RepositoryScanner:
    """Scans repository for code files"""
    
    # File extensions to include
    CODE_EXTENSIONS = {
        '.py',      # Python
        '.js',      # JavaScript
        '.jsx',     # React JavaScript
        '.ts',      # TypeScript
        '.tsx',     # React TypeScript
        '.java',    # Java
        '.cpp',     # C++
        '.c',       # C
        '.go',      # Go
        '.rs',      # Rust
        '.rb',      # Ruby
        '.php',     # PHP
    }
    
    # Directories to exclude
    EXCLUDE_DIRS = {
        'node_modules',
        '__pycache__',
        '.git',
        '.emergent',
        'venv',
        'env',
        '.venv',
        'build',
        'dist',
        '.next',
        'coverage',
        '.pytest_cache',
        '.mypy_cache',
        'migrations',  # Skip DB migrations
    }
    
    # Files to exclude
    EXCLUDE_FILES = {
        '__init__.py',  # Usually empty
        'package-lock.json',
        'yarn.lock',
        'poetry.lock',
    }
    
    def __init__(self, root_path: str = "/app"):
        self.root_path = Path(root_path)
        
    def scan_repository(self, max_files: int = 100) -> List[Dict[str, Any]]:
        """
        Scan repository for code files
        
        Returns:
            List of dicts with file information
        """
        logger.info(f"🔍 Scanning repository: {self.root_path}")
        
        files = []
        file_count = 0
        
        try:
            for file_path in self._walk_directory(self.root_path):
                if file_count >= max_files:
                    logger.warning(f"⚠️ Reached max files limit: {max_files}")
                    break
                
                try:
                    # Get file info
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        files.append(file_info)
                        file_count += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not process {file_path}: {e}")
                    continue
            
            logger.info(f"✅ Found {len(files)} code files")
            
            # Sort by priority (backend > frontend > root)
            files = self._sort_by_priority(files)
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Repository scan failed: {e}", exc_info=True)
            return []
    
    def _walk_directory(self, directory: Path):
        """Walk directory and yield code files"""
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check extension
                if file_path.suffix not in self.CODE_EXTENSIONS:
                    continue
                
                # Check excluded files
                if file in self.EXCLUDE_FILES:
                    continue
                
                yield file_path
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate metrics
            lines = content.split('\n')
            
            return {
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.root_path)),
                'name': file_path.name,
                'extension': file_path.suffix,
                'size': len(content),
                'lines': len(lines),
                'content': content,
                'language': self._detect_language(file_path.suffix)
            }
            
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return None
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from extension"""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
        }
        return lang_map.get(extension, 'unknown')
    
    def _sort_by_priority(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort files by priority (backend > frontend > root)"""
        def priority_key(file_info):
            path = file_info['relative_path']
            if path.startswith('backend/'):
                return (0, path)
            elif path.startswith('frontend/'):
                return (1, path)
            else:
                return (2, path)
        
        return sorted(files, key=priority_key)
    
    def get_summary(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics of scanned files"""
        total_lines = sum(f['lines'] for f in files)
        total_size = sum(f['size'] for f in files)
        
        by_language = {}
        for file in files:
            lang = file['language']
            if lang not in by_language:
                by_language[lang] = {'count': 0, 'lines': 0}
            by_language[lang]['count'] += 1
            by_language[lang]['lines'] += file['lines']
        
        return {
            'total_files': len(files),
            'total_lines': total_lines,
            'total_size': total_size,
            'by_language': by_language
        }
