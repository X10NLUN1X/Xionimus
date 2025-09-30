"""
Advanced File Tools - Glob & Grep Operations
Emergent-Style File Pattern Matching and Content Search
"""
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import fnmatch

logger = logging.getLogger(__name__)

class FileTools:
    """Advanced file search and pattern matching tools"""
    
    def __init__(self, workspace_root: str = "/app/xionimus-ai"):
        self.workspace_root = Path(workspace_root)
        self.gitignore_patterns = self._load_gitignore()
    
    def _load_gitignore(self) -> List[str]:
        """Load .gitignore patterns"""
        gitignore_path = self.workspace_root / '.gitignore'
        patterns = [
            'node_modules',
            '.git',
            '__pycache__',
            '*.pyc',
            '.env',
            'venv',
            '.venv',
            'dist',
            'build'
        ]
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                logger.warning(f"Could not read .gitignore: {e}")
        
        return patterns
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored based on gitignore patterns"""
        path_str = str(path.relative_to(self.workspace_root))
        
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
            if path_str.startswith(pattern.rstrip('/')):
                return True
        
        return False
    
    async def glob_files(
        self, 
        pattern: str,
        base_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find files matching glob pattern
        Pattern examples: "**/*.py", "src/**/*.tsx", "*.json"
        """
        try:
            search_root = self.workspace_root / base_path if base_path else self.workspace_root
            
            if not search_root.exists():
                return {
                    'success': False,
                    'error': f'Base path not found: {base_path}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Find matching files
            matches = []
            for file_path in search_root.glob(pattern):
                if file_path.is_file() and not self._should_ignore(file_path):
                    relative_path = file_path.relative_to(self.workspace_root)
                    matches.append({
                        'path': str(relative_path),
                        'size': file_path.stat().st_size,
                        'name': file_path.name
                    })
            
            logger.info(f"🔍 Glob found {len(matches)} files matching '{pattern}'")
            
            return {
                'success': True,
                'pattern': pattern,
                'base_path': base_path or '.',
                'matches': matches,
                'count': len(matches),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Glob error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def grep_content(
        self,
        pattern: str,
        path: Optional[str] = None,
        file_pattern: Optional[str] = None,
        case_sensitive: bool = False,
        context_lines: int = 0
    ) -> Dict[str, Any]:
        """
        Search for pattern in file contents using ripgrep/grep
        """
        try:
            search_path = str(self.workspace_root / path) if path else str(self.workspace_root)
            
            # Build grep command (prefer ripgrep if available)
            cmd = []
            
            # Try ripgrep first
            try:
                subprocess.run(['which', 'rg'], capture_output=True, check=True)
                cmd = ['rg', '--json']
                
                if not case_sensitive:
                    cmd.append('-i')
                
                if context_lines > 0:
                    cmd.extend(['-C', str(context_lines)])
                
                if file_pattern:
                    cmd.extend(['-g', file_pattern])
                
                cmd.extend([pattern, search_path])
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to grep
                cmd = ['grep', '-r']
                
                if not case_sensitive:
                    cmd.append('-i')
                
                if context_lines > 0:
                    cmd.extend(['-C', str(context_lines)])
                
                if file_pattern:
                    cmd.extend(['--include', file_pattern])
                
                cmd.extend([pattern, search_path])
            
            # Execute search
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=10.0
            )
            
            output = stdout.decode()
            
            # Parse results
            matches = []
            for line in output.split('\n'):
                if not line:
                    continue
                
                # Simple parsing (format: file:line:content)
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    matches.append({
                        'file': parts[0],
                        'line': parts[1],
                        'content': parts[2]
                    })
            
            logger.info(f"🔍 Grep found {len(matches)} matches for '{pattern}'")
            
            return {
                'success': True,
                'pattern': pattern,
                'path': path or '.',
                'file_pattern': file_pattern,
                'case_sensitive': case_sensitive,
                'matches': matches,
                'count': len(matches),
                'timestamp': datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            logger.error("Grep timeout")
            return {
                'success': False,
                'error': 'Search timeout (>10s)',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Grep error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_search_report(self, search_result: Dict[str, Any], search_type: str) -> str:
        """
        Generate human-readable search report
        """
        if not search_result['success']:
            return f"❌ Search failed: {search_result.get('error')}"
        
        lines = [f"# 🔍 {search_type.title()} Search Report\n"]
        
        if search_type == "glob":
            lines.append(f"**Pattern**: `{search_result['pattern']}`")
            lines.append(f"**Matches**: {search_result['count']}\n")
            
            if search_result['count'] > 0:
                lines.append("## Files Found")
                for match in search_result['matches'][:20]:  # Limit to 20
                    lines.append(f"- `{match['path']}` ({match['size']} bytes)")
                
                if search_result['count'] > 20:
                    lines.append(f"\n... and {search_result['count'] - 20} more files")
        
        elif search_type == "grep":
            lines.append(f"**Pattern**: `{search_result['pattern']}`")
            lines.append(f"**Matches**: {search_result['count']}\n")
            
            if search_result['count'] > 0:
                lines.append("## Matches Found")
                for match in search_result['matches'][:20]:  # Limit to 20
                    lines.append(f"- `{match['file']}:{match['line']}` - {match['content'][:80]}...")
                
                if search_result['count'] > 20:
                    lines.append(f"\n... and {search_result['count'] - 20} more matches")
        
        return "\n".join(lines)


# Global instance
file_tools = FileTools()
