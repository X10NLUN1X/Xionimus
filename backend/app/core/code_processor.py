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
    
    def generate_summary(self, process_result: Dict, ai_response: str = "") -> str:
        """
        Generate comprehensive summary with file details, purpose, and next steps
        """
        if process_result['code_blocks_found'] == 0:
            return ""
        
        lines = ["📝 **Code-Generierung abgeschlossen:**\n"]
        
        # 1. WAS WURDE GECODET - List all files
        lines.append("### 📄 Erstellte/Aktualisierte Dateien:")
        for file_info in process_result['files']:
            if file_info.get('success'):
                action_emoji = "✏️" if file_info['action'] == 'updated' else "📄"
                file_type = self._get_file_type_description(file_info['file_path'])
                lines.append(
                    f"{action_emoji} **`{file_info['file_path']}`** ({file_type})\n"
                    f"   └─ {file_info['lines']} Zeilen, {file_info['size']} Bytes"
                )
        
        lines.append(f"\n✅ **{process_result['files_written']} Datei(en) erfolgreich geschrieben**\n")
        
        # 2. WOFÜR MAN ES BRAUCHT - Purpose and functionality
        lines.append("### 🎯 Zweck und Funktionalität:")
        purpose = self._extract_purpose_from_files(process_result['files'])
        lines.append(purpose)
        
        # 3. NÄCHSTE SCHRITTE - Suggestions
        lines.append("\n### 💡 Vorschläge für nächste Schritte:")
        suggestions = self._generate_next_steps(process_result['files'])
        for i, suggestion in enumerate(suggestions, 1):
            lines.append(f"**{i}.** {suggestion}")
        
        return "\n".join(lines)
    
    def _get_file_type_description(self, file_path: str) -> str:
        """Get friendly description of file type"""
        ext = Path(file_path).suffix.lower()
        type_map = {
            '.py': 'Python Backend',
            '.js': 'JavaScript',
            '.jsx': 'React Component',
            '.tsx': 'React TypeScript Component',
            '.ts': 'TypeScript',
            '.html': 'HTML Template',
            '.css': 'Stylesheet',
            '.scss': 'SASS Stylesheet',
            '.json': 'Configuration',
            '.md': 'Documentation',
            '.sh': 'Shell Script',
            '.sql': 'Database Schema',
            '.yaml': 'Config File',
            '.yml': 'Config File',
        }
        return type_map.get(ext, 'Code File')
    
    def _extract_purpose_from_files(self, files: List[Dict]) -> str:
        """Extract purpose from generated files"""
        purposes = []
        
        for file_info in files:
            if not file_info.get('success'):
                continue
                
            file_path = file_info['file_path']
            
            # Backend files
            if 'backend' in file_path or file_path.endswith('.py'):
                if 'api' in file_path:
                    purposes.append("🔌 **Backend API:** Stellt REST-Endpunkte für die Kommunikation zwischen Frontend und Backend bereit")
                elif 'model' in file_path or 'schema' in file_path:
                    purposes.append("📊 **Datenmodell:** Definiert die Struktur der Daten in der Datenbank")
                elif 'service' in file_path:
                    purposes.append("⚙️ **Business Logic:** Implementiert die Hauptfunktionalität der Anwendung")
                elif 'config' in file_path:
                    purposes.append("🔧 **Konfiguration:** Verwaltet Einstellungen und Umgebungsvariablen")
                else:
                    purposes.append("🐍 **Python Backend:** Server-seitige Logik und Datenverarbeitung")
            
            # Frontend files
            elif any(ext in file_path for ext in ['.jsx', '.tsx', '.js', '.ts']):
                if 'component' in file_path.lower() or 'Component' in file_path:
                    purposes.append("🎨 **UI Component:** Wiederverwendbare React-Komponente für die Benutzeroberfläche")
                elif 'page' in file_path.lower() or 'Page' in file_path:
                    purposes.append("📱 **Seite:** Vollständige Seite der Anwendung mit Routing")
                elif 'hook' in file_path.lower():
                    purposes.append("🪝 **Custom Hook:** Wiederverwendbare React-Logik für State Management")
                elif 'context' in file_path.lower() or 'Context' in file_path:
                    purposes.append("🌐 **Context:** Globaler State für die gesamte Anwendung")
                elif 'service' in file_path.lower():
                    purposes.append("🔄 **Frontend Service:** API-Calls und Datenverarbeitung im Frontend")
                else:
                    purposes.append("⚛️ **Frontend Logic:** Client-seitige Funktionalität und UI-Interaktionen")
            
            # Styling
            elif file_path.endswith(('.css', '.scss')):
                purposes.append("🎨 **Styling:** Design und Layout der Benutzeroberfläche")
            
            # Config files
            elif file_path.endswith(('.json', '.yaml', '.yml', '.env')):
                purposes.append("⚙️ **Konfiguration:** Projekt-Einstellungen und Abhängigkeiten")
            
            # Documentation
            elif file_path.endswith('.md'):
                purposes.append("📚 **Dokumentation:** Erklärungen und Anleitungen für Entwickler")
        
        # Remove duplicates and format
        unique_purposes = list(dict.fromkeys(purposes))
        if not unique_purposes:
            return "Diese Dateien bilden die Grundlage für die Anwendungsfunktionalität."
        
        return "\n".join(unique_purposes)
    
    def _generate_next_steps(self, files: List[Dict]) -> List[str]:
        """Generate smart suggestions for next steps based on created files"""
        suggestions = []
        
        # Analyze what was created
        has_backend = any('backend' in f['file_path'] or f['file_path'].endswith('.py') for f in files if f.get('success'))
        has_frontend = any(any(ext in f['file_path'] for ext in ['.jsx', '.tsx', '.js', '.ts']) for f in files if f.get('success'))
        has_api = any('api' in f['file_path'] for f in files if f.get('success'))
        has_component = any('component' in f['file_path'].lower() for f in files if f.get('success'))
        has_config = any(f['file_path'].endswith(('.json', '.yaml', '.yml')) for f in files if f.get('success'))
        has_database = any('model' in f['file_path'] or 'schema' in f['file_path'] for f in files if f.get('success'))
        
        # Generate contextual suggestions
        if has_backend and not has_frontend:
            suggestions.extend([
                "Frontend-Komponenten erstellen, um die Backend-API zu nutzen",
                "Tests für die Backend-Endpunkte schreiben (Unit & Integration Tests)",
                "Fehlerbehandlung und Input-Validierung hinzufügen"
            ])
        elif has_frontend and not has_backend:
            suggestions.extend([
                "Backend-API implementieren für die Datenverwaltung",
                "State Management verbessern (Redux, Zustand, oder Context API)",
                "Responsive Design für mobile Geräte optimieren"
            ])
        elif has_backend and has_frontend:
            suggestions.extend([
                "Frontend-Backend Integration testen und debuggen",
                "Authentifizierung und Authorization hinzufügen",
                "Performance-Optimierung und Caching implementieren"
            ])
        elif has_api:
            suggestions.extend([
                "API-Dokumentation mit Swagger/OpenAPI erstellen",
                "Rate Limiting und Sicherheitsmaßnahmen implementieren",
                "Frontend-Client für die API-Nutzung entwickeln"
            ])
        elif has_component:
            suggestions.extend([
                "Storybook für Component-Dokumentation einrichten",
                "Props und Types erweitern für mehr Flexibilität",
                "Unit Tests mit Jest/React Testing Library schreiben"
            ])
        elif has_database:
            suggestions.extend([
                "Migrations und Seed-Daten für die Datenbank erstellen",
                "CRUD-Operationen (Create, Read, Update, Delete) implementieren",
                "Datenbank-Indizes für Performance-Optimierung hinzufügen"
            ])
        elif has_config:
            suggestions.extend([
                "Environment-spezifische Konfigurationen (.env.development, .env.production)",
                "CI/CD Pipeline für automatisches Deployment einrichten",
                "Docker-Container für einheitliche Entwicklungsumgebung"
            ])
        else:
            # Generic suggestions
            suggestions.extend([
                "Fehlerbehandlung und Logging verbessern",
                "Unit Tests und Integration Tests hinzufügen",
                "Code-Dokumentation und README aktualisieren"
            ])
        
        # Ensure we always return exactly 3 suggestions
        return suggestions[:3]


# Global instance
code_processor = CodeProcessor()
