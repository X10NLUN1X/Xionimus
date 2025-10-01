"""
Code Processor - Emergent-Style Background Code Generation
Erkennt Code-Blöcke automatisch und schreibt sie in Dateien
"""
import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import aiofiles

logger = logging.getLogger(__name__)

class CodeProcessor:
    """Processes AI responses and automatically writes code to files"""
    
    # Regex patterns for code block detection
    CODE_BLOCK_PATTERN = re.compile(
        r'```(\w+)?\s*\n(.*?)\n```',
        re.DOTALL | re.MULTILINE
    )
    
    FILE_PATH_PATTERN = re.compile(
        r'(?:file|path|filename):\s*([^\s\n]+)',
        re.IGNORECASE
    )
    
    LANGUAGE_EXTENSIONS = {
        'python': '.py',
        'py': '.py',
        'javascript': '.js',
        'js': '.js',
        'typescript': '.ts',
        'ts': '.ts',
        'tsx': '.tsx',
        'jsx': '.jsx',
        'html': '.html',
        'css': '.css',
        'scss': '.scss',
        'json': '.json',
        'yaml': '.yaml',
        'yml': '.yml',
        'markdown': '.md',
        'md': '.md',
        'bash': '.sh',
        'sh': '.sh',
        'sql': '.sql',
    }
    
    def __init__(self, workspace_root: str = "/app/xionimus-ai"):
        self.workspace_root = Path(workspace_root)
        self.processed_files: List[Dict] = []
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract all code blocks from text
        Returns list of dicts with: language, code, context
        """
        code_blocks = []
        matches = self.CODE_BLOCK_PATTERN.finditer(text)
        
        for match in matches:
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            
            # Get context (text before the code block)
            start_pos = match.start()
            context_start = max(0, start_pos - 200)
            context = text[context_start:start_pos].strip()
            
            code_blocks.append({
                'language': language.lower(),
                'code': code,
                'context': context,
                'position': match.start()
            })
        
        logger.info(f"📦 Extracted {len(code_blocks)} code blocks")
        return code_blocks
    
    def detect_file_path(self, context: str, language: str) -> Optional[str]:
        """
        Detect file path from context
        Looks for patterns like: "file: src/app.py" or "path: backend/main.py"
        """
        # Try explicit file path pattern
        match = self.FILE_PATH_PATTERN.search(context)
        if match:
            file_path = match.group(1)
            logger.info(f"📍 Detected file path from context: {file_path}")
            return file_path
        
        # Look for path-like strings in context
        words = context.split()
        for word in words:
            if '/' in word and not word.startswith('http'):
                # Looks like a path
                if '.' in word.split('/')[-1]:
                    logger.info(f"📍 Detected path-like string: {word}")
                    return word
        
        return None
    
    def infer_file_path(self, language: str, code: str, context: str, index: int) -> str:
        """
        Infer a reasonable file path based on language and content
        """
        # Get file extension
        extension = self.LANGUAGE_EXTENSIONS.get(language, '.txt')
        
        # Try to detect if it's frontend or backend code
        is_frontend = any(keyword in code for keyword in ['import React', 'useState', 'useEffect', 'JSX', 'tsx'])
        is_backend = any(keyword in code for keyword in ['from fastapi', 'FastAPI', 'async def', '@router'])
        
        # Determine directory
        if is_frontend:
            directory = 'frontend/src/generated'
        elif is_backend:
            directory = 'backend/app/generated'
        else:
            directory = 'generated'
        
        # Create filename
        filename = f"code_block_{index + 1}{extension}"
        
        file_path = f"{directory}/{filename}"
        logger.info(f"🔮 Inferred file path: {file_path}")
        return file_path
    
    async def write_code_to_file(
        self, 
        file_path: str, 
        code: str, 
        create_backup: bool = True
    ) -> Dict[str, any]:
        """
        Write code to specified file path
        Returns dict with status and details
        """
        try:
            # Resolve full path
            full_path = self.workspace_root / file_path
            
            # Create directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file if requested
            if create_backup and full_path.exists():
                backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                async with aiofiles.open(full_path, 'r', encoding='utf-8') as src:
                    content = await src.read()
                async with aiofiles.open(backup_path, 'w', encoding='utf-8') as dst:
                    await dst.write(content)
                logger.info(f"💾 Created backup: {backup_path}")
            
            # Write new code with UTF-8 encoding (Windows compatibility)
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(code)
            
            result = {
                'success': True,
                'file_path': str(file_path),
                'full_path': str(full_path),
                'lines': len(code.split('\n')),
                'size': len(code),
                'action': 'updated' if full_path.exists() else 'created'
            }
            
            self.processed_files.append(result)
            logger.info(f"✅ {result['action'].title()} file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error writing file {file_path}: {e}")
            return {
                'success': False,
                'file_path': str(file_path),
                'error': str(e)
            }
    
    async def process_ai_response(
        self, 
        response_text: str,
        auto_write: bool = True
    ) -> Dict[str, any]:
        """
        Main processing function: Extract code blocks and optionally write them
        Returns summary of processed code
        """
        code_blocks = self.extract_code_blocks(response_text)
        
        if not code_blocks:
            return {
                'code_blocks_found': 0,
                'files_written': 0,
                'files': []
            }
        
        results = []
        
        for idx, block in enumerate(code_blocks):
            # Detect or infer file path
            detected_path = self.detect_file_path(block['context'], block['language'])
            file_path = detected_path or self.infer_file_path(
                block['language'], 
                block['code'], 
                block['context'], 
                idx
            )
            
            if auto_write:
                write_result = await self.write_code_to_file(file_path, block['code'])
                results.append(write_result)
            else:
                results.append({
                    'success': False,
                    'file_path': file_path,
                    'code_preview': block['code'][:200] + '...',
                    'language': block['language'],
                    'auto_write': False
                })
        
        return {
            'code_blocks_found': len(code_blocks),
            'files_written': sum(1 for r in results if r.get('success')),
            'files': results
        }
    
    def generate_summary(self, process_result: Dict) -> str:
        """
        Generate human-readable summary of code processing
        """
        if process_result['code_blocks_found'] == 0:
            return ""
        
        lines = ["📝 **Code-Generierung abgeschlossen:**\n"]
        
        for file_info in process_result['files']:
            if file_info.get('success'):
                action_emoji = "✏️" if file_info['action'] == 'updated' else "📄"
                lines.append(
                    f"{action_emoji} `{file_info['file_path']}` "
                    f"({file_info['lines']} Zeilen, {file_info['size']} Bytes)"
                )
        
        lines.append(f"\n✅ **{process_result['files_written']} Datei(en) erfolgreich geschrieben**")
        
        return "\n".join(lines)


# Global instance
code_processor = CodeProcessor()
