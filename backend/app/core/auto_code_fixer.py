"""
Auto Code Fixer - Automatically applies code improvements
Works with 4 agents to analyze and fix code automatically
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import re
import json
from filelock import FileLock
from pathlib import Path

logger = logging.getLogger(__name__)


class AutoCodeFixer:
    """Applies code fixes automatically to files with file locking"""
    
    def __init__(self):
        self.locks = {}  # Per-file locks
        self.lock_dir = Path("/tmp/xionimus_locks")
        self.lock_dir.mkdir(exist_ok=True)
    
    async def apply_fixes(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply fixes from agent findings to actual files
        
        Args:
            findings: List of findings from review agents
            
        Returns:
            Summary of applied fixes
        """
        logger.info(f"🔧 Starting auto-fix for {len(findings)} findings")
        
        results = {
            'total_findings': len(findings),
            'fixes_applied': 0,
            'fixes_failed': 0,
            'files_modified': set(),
            'changes': []
        }
        
        for finding in findings:
            # Check if finding has fix code
            if not finding.get('fix_code'):
                continue
            
            # Check if finding has file path
            file_path = finding.get('file_path')
            if not file_path or file_path == 'code_snippet':
                continue
            
            try:
                # Apply fix
                success = await self._apply_single_fix(finding)
                
                if success:
                    results['fixes_applied'] += 1
                    results['files_modified'].add(file_path)
                    results['changes'].append({
                        'file': file_path,
                        'title': finding.get('title'),
                        'agent': finding.get('agent_name'),
                        'severity': finding.get('severity')
                    })
                    logger.info(f"✅ Applied fix: {finding.get('title')} in {file_path}")
                else:
                    results['fixes_failed'] += 1
                    logger.warning(f"⚠️ Could not apply fix: {finding.get('title')}")
                    
            except Exception as e:
                results['fixes_failed'] += 1
                logger.error(f"❌ Error applying fix: {e}", exc_info=True)
        
        results['files_modified'] = list(results['files_modified'])
        
        logger.info(f"✅ Auto-fix complete: {results['fixes_applied']} applied, {results['fixes_failed']} failed")
        
        return results
    
    async def _apply_single_fix(self, finding: Dict[str, Any]) -> bool:
        """Apply a single fix to a file with file locking to prevent race conditions"""
        file_path = finding.get('file_path')
        if not file_path:
            return False
        
        # Get or create lock for this file
        lock_file = self.lock_dir / f"{Path(file_path).name}.lock"
        lock = FileLock(lock_file, timeout=10)
        
        try:
            # Acquire lock before modifying file
            with lock:
                logger.debug(f"🔒 Acquired lock for {file_path}")
                
                fix_code = finding.get('fix_code')
                line_number = finding.get('line_number')
                
                # Read current file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # Strategy 1: If line number is provided, replace that section
                if line_number and line_number > 0 and line_number <= len(lines):
                    # Try to replace the specific line or section
                    original_line = lines[line_number - 1]
                    
                    # If fix_code is a single line, replace directly
                    if '\n' not in fix_code:
                        lines[line_number - 1] = fix_code
                        new_content = '\n'.join(lines)
                        
                        # Write back
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        logger.info(f"✅ Applied fix to {file_path}:{line_number}")
                        return True
                
                # Strategy 2: Try to find and replace pattern
                # Look for similar code and replace
                # This is conservative - only replaces if high confidence
                
                # For now, skip complex replacements
                # In production, this would use more sophisticated matching
                logger.debug(f"⚠️ No simple fix strategy available for {file_path}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error applying fix to {file_path}: {e}")
            return False
        finally:
            logger.debug(f"🔓 Released lock for {file_path}")
    
    def generate_commit_message(self, results: Dict[str, Any]) -> str:
        """Generate git commit message from fix results"""
        changes = results.get('changes', [])
        files_count = len(results.get('files_modified', []))
        
        message_parts = [
            "🤖 Auto Code Review & Fix",
            "",
            f"Applied {results['fixes_applied']} fixes across {files_count} files",
            ""
        ]
        
        # Group by agent
        by_agent = {}
        for change in changes:
            agent = change['agent']
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(change)
        
        # Add agent summaries
        agent_icons = {
            'code_analysis': '🔍',
            'debug': '🐛',
            'enhancement': '✨',
            'test': '🧪'
        }
        
        for agent, agent_changes in by_agent.items():
            icon = agent_icons.get(agent, '🤖')
            message_parts.append(f"{icon} {agent.upper()}: {len(agent_changes)} fixes")
            for change in agent_changes[:5]:  # First 5 only
                message_parts.append(f"  - {change['title']}")
            if len(agent_changes) > 5:
                message_parts.append(f"  - ... and {len(agent_changes) - 5} more")
            message_parts.append("")
        
        return '\n'.join(message_parts)


class FileWriter:
    """Writes fixes to files safely"""
    
    @staticmethod
    async def write_file(file_path: str, content: str) -> bool:
        """Write content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    @staticmethod
    async def backup_file(file_path: str) -> Optional[str]:
        """Create backup of file before modification"""
        try:
            backup_path = f"{file_path}.backup"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return backup_path
        except Exception as e:
            logger.error(f"Error backing up file {file_path}: {e}")
            return None
