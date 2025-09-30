"""
Bulk File Manager - Multi-File Operations
Emergent-Style Bulk File Writing and Reading
"""
import asyncio
import aiofiles
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BulkFileManager:
    """Manages bulk file operations"""
    
    MAX_FILES = 20  # Emergent limit
    
    def __init__(self, workspace_root: str = "/app/xionimus-ai"):
        self.workspace_root = Path(workspace_root)
    
    async def write_file(
        self, 
        file_path: str, 
        content: str,
        create_backup: bool = False
    ) -> Dict[str, Any]:
        """
        Write single file
        """
        try:
            full_path = self.workspace_root / file_path
            
            # Create directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup if exists
            if create_backup and full_path.exists():
                backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                async with aiofiles.open(full_path, 'r') as src:
                    backup_content = await src.read()
                async with aiofiles.open(backup_path, 'w') as dst:
                    await dst.write(backup_content)
            
            # Write new content
            async with aiofiles.open(full_path, 'w') as f:
                await f.write(content)
            
            return {
                'success': True,
                'file_path': file_path,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }
    
    async def bulk_write(
        self, 
        files: List[Dict[str, str]],
        create_backups: bool = False
    ) -> Dict[str, Any]:
        """
        Write multiple files simultaneously
        files: List of {"path": str, "content": str}
        """
        if len(files) > self.MAX_FILES:
            return {
                'success': False,
                'error': f'Too many files. Maximum: {self.MAX_FILES}',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"📦 Bulk writing {len(files)} files...")
        
        # Write all files concurrently
        tasks = [
            self.write_file(
                file_path=file_data['path'],
                content=file_data['content'],
                create_backup=create_backups
            )
            for file_data in files
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for result in results:
            if isinstance(result, Exception):
                failed.append({
                    'success': False,
                    'error': str(result)
                })
            elif result.get('success'):
                successful.append(result)
            else:
                failed.append(result)
        
        logger.info(f"✅ Bulk write complete: {len(successful)}/{len(files)} successful")
        
        return {
            'success': len(failed) == 0,
            'total_files': len(files),
            'successful': len(successful),
            'failed': len(failed),
            'results': {
                'successful': successful,
                'failed': failed
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read single file
        """
        try:
            full_path = self.workspace_root / file_path
            
            if not full_path.exists():
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'File not found'
                }
            
            async with aiofiles.open(full_path, 'r') as f:
                content = await f.read()
            
            return {
                'success': True,
                'file_path': file_path,
                'content': content,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }
    
    async def bulk_read(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Read multiple files simultaneously
        """
        if len(file_paths) > self.MAX_FILES:
            return {
                'success': False,
                'error': f'Too many files. Maximum: {self.MAX_FILES}',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"📖 Bulk reading {len(file_paths)} files...")
        
        # Read all files concurrently
        tasks = [self.read_file(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = []
        failed = []
        
        for result in results:
            if isinstance(result, Exception):
                failed.append({
                    'success': False,
                    'error': str(result)
                })
            elif result.get('success'):
                successful.append(result)
            else:
                failed.append(result)
        
        logger.info(f"✅ Bulk read complete: {len(successful)}/{len(file_paths)} successful")
        
        return {
            'success': len(failed) == 0,
            'total_files': len(file_paths),
            'successful': len(successful),
            'failed': len(failed),
            'files': successful,
            'errors': failed,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_bulk_report(self, bulk_result: Dict[str, Any], operation: str) -> str:
        """
        Generate human-readable report for bulk operations
        """
        lines = [f"# 📦 Bulk {operation.title()} Report\n"]
        
        lines.append(f"**Total Files**: {bulk_result['total_files']}")
        lines.append(f"**Successful**: {bulk_result['successful']}")
        lines.append(f"**Failed**: {bulk_result['failed']}\n")
        
        if bulk_result['successful'] > 0:
            lines.append("## Successful Files")
            
            if operation == "write":
                for file_info in bulk_result['results']['successful']:
                    lines.append(f"✅ `{file_info['file_path']}` ({file_info['lines']} lines, {file_info['size']} bytes)")
            elif operation == "read":
                for file_info in bulk_result['files']:
                    lines.append(f"✅ `{file_info['file_path']}` ({file_info['lines']} lines, {file_info['size']} bytes)")
        
        if bulk_result['failed'] > 0:
            lines.append("\n## Failed Files")
            
            failed_list = bulk_result.get('results', {}).get('failed', []) or bulk_result.get('errors', [])
            for error_info in failed_list:
                file_path = error_info.get('file_path', 'unknown')
                error = error_info.get('error', 'Unknown error')
                lines.append(f"❌ `{file_path}`: {error}")
        
        return "\n".join(lines)


# Global instance
bulk_file_manager = BulkFileManager()
