"""
Documentation Agent - Automated README & API Docs Generation
Erstellt automatisch vollständige Dokumentation für generierten Code
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentationAgent:
    """Generates comprehensive documentation automatically"""
    
    def __init__(self, workspace_root: str = "/app/xionimus-ai"):
        self.workspace_root = Path(workspace_root)
    
    async def generate_documentation(
        self,
        code_files: List[Dict[str, Any]],
        project_description: str,
        ai_manager,
        api_keys: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate complete documentation for the project
        
        Args:
            code_files: List of generated files with path and content
            project_description: Description of what was built
            ai_manager: AI Manager for LLM calls
            api_keys: API keys for LLM
            
        Returns:
            Dict with README content and API docs
        """
        logger.info(f"📚 Generating documentation for {len(code_files)} files")
        
        try:
            # Prepare file summary
            files_summary = "\n".join([
                f"- {file['file_path']}: {file.get('description', 'Code file')}"
                for file in code_files[:10]  # Limit to prevent token overflow
            ])
            
            # Create comprehensive README prompt
            readme_prompt = f"""Als Dokumentations-Experte, erstelle eine vollständige README.md für dieses Projekt.

**Projekt-Beschreibung:**
{project_description}

**Generierte Dateien:**
{files_summary}

**Erstelle eine README.md mit:**

1. **📋 Projekt-Titel & Beschreibung**
   - Klare Überschrift
   - Was macht das Projekt?
   - Hauptfeatures (3-5 Punkte)

2. **🚀 Quick Start**
   - Installations-Schritte
   - Schnellstart-Befehle
   - Erste Verwendung

3. **📦 Installation**
   - Prerequisites
   - Schritt-für-Schritt Anleitung
   - Environment Setup

4. **🔧 Konfiguration**
   - Environment Variables
   - Config-Dateien
   - API-Keys Setup (falls nötig)

5. **💻 Verwendung**
   - Grundlegende Beispiele
   - Code-Snippets
   - Typische Use-Cases

6. **📁 Projekt-Struktur**
   - Verzeichnis-Übersicht
   - Wichtige Dateien erklärt

7. **🧪 Testing** (falls Tests vorhanden)
   - Test-Befehle
   - Test-Coverage

8. **🚀 Deployment** (optional)
   - Build-Schritte
   - Deployment-Optionen

9. **📝 API-Dokumentation** (falls Backend)
   - Wichtigste Endpoints
   - Request/Response-Beispiele

10. **🤝 Contributing & License**
    - Contribution-Guidelines
    - License-Info

**Format:**
- Markdown mit Emojis für bessere Lesbarkeit
- Code-Blöcke mit Syntax-Highlighting
- Klare Struktur mit Überschriften
- Praxisnahe Beispiele

Schreibe die README direkt, ohne zusätzliche Erklärungen."""

            # Generate README
            response = await ai_manager.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-5-20250929",
                messages=[{"role": "user", "content": readme_prompt}],
                stream=False,
                api_keys=api_keys
            )
            
            readme_content = response.get("content", "")
            
            if readme_content:
                logger.info(f"✅ README generiert: {len(readme_content)} Zeichen")
                
                # Save README to workspace
                readme_path = self.workspace_root / "README.md"
                try:
                    readme_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    logger.info(f"💾 README gespeichert: {readme_path}")
                    saved = True
                except Exception as e:
                    logger.error(f"❌ Fehler beim Speichern der README: {e}")
                    saved = False
                
                return {
                    "success": True,
                    "readme_content": readme_content,
                    "readme_path": str(readme_path) if saved else None,
                    "saved": saved,
                    "length": len(readme_content)
                }
            else:
                logger.warning("⚠️ Keine README generiert")
                return {
                    "success": False,
                    "error": "Empty README content"
                }
                
        except Exception as e:
            logger.error(f"❌ Documentation generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_documentation_summary(self, result: Dict[str, Any]) -> str:
        """Format documentation result as human-readable text"""
        if not result.get("success"):
            return f"⚠️ Dokumentation konnte nicht erstellt werden: {result.get('error', 'Unbekannter Fehler')}"
        
        lines = [
            "## 📚 Automatische Dokumentation erstellt",
            "",
            f"✅ **README.md** generiert ({result['length']:,} Zeichen)",
        ]
        
        if result.get("saved"):
            lines.append(f"💾 Gespeichert: `{result['readme_path']}`")
        
        lines.extend([
            "",
            "**Inhalt:**",
            "- 📋 Projekt-Beschreibung & Features",
            "- 🚀 Quick Start & Installation",
            "- 💻 Verwendungs-Beispiele",
            "- 📁 Projekt-Struktur",
            "- 📝 API-Dokumentation (falls vorhanden)",
            ""
        ])
        
        return "\n".join(lines)

# Global instance
documentation_agent = DocumentationAgent()
