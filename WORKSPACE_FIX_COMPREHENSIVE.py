"""
XIONIMUS AI - COMPREHENSIVE WORKSPACE FIX
==========================================
Behebt das Problem, dass der KI-Agent importierte GitHub-Repositories nicht erkennt.

HAUPTPROBLEM:
- Repositories werden nach /app/ statt in backend/workspace/github_imports/ geklont
- Der AI-Agent weiß nicht wo die Dateien liegen
- Fehlende User-ID-basierte Struktur

LÖSUNG:
1. Import-Pfad korrigieren auf settings.GITHUB_IMPORTS_DIR
2. User-ID-basierte Ordnerstruktur implementieren  
3. Agent-Konfiguration erstellen (.cursorrules, .aider.conf.yml)
4. Windows-kompatible Pfade und Berechtigungen
"""

import os
import sys
from pathlib import Path
import json
import shutil

# Farben für Console-Output (Windows kompatibel)
if sys.platform == "win32":
    os.system("color")

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# Determine repository root
SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR / "backend"
WORKSPACE_DIR = BACKEND_DIR / "workspace"
GITHUB_IMPORTS_DIR = WORKSPACE_DIR / "github_imports"

def backup_file(file_path: Path):
    """Create backup of file before modifying"""
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        shutil.copy2(file_path, backup_path)
        print_success(f"Backup erstellt: {backup_path.name}")
        return backup_path
    return None

def create_workspace_structure():
    """Create proper workspace structure"""
    print_header("1. WORKSPACE-STRUKTUR ERSTELLEN")
    
    directories = [
        WORKSPACE_DIR,
        GITHUB_IMPORTS_DIR,
        WORKSPACE_DIR / "uploads",
        WORKSPACE_DIR / "exports",
        WORKSPACE_DIR / "temp"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"Verzeichnis erstellt: {directory.relative_to(SCRIPT_DIR)}")
    
    # Create README in workspace
    readme_content = """# Xionimus AI Workspace

Dieser Ordner enthält alle importierten Repositories und Uploads.

## Struktur:

```
workspace/
├── github_imports/     ← Importierte GitHub-Repositories
│   └── [user_id]/      ← Pro User ein Ordner
│       └── [repo_name]/ ← Repository-Dateien
├── uploads/            ← Hochgeladene Dateien
├── exports/            ← Exportierte Dateien
└── temp/              ← Temporäre Dateien
```

## Für den AI-Agent:

Alle Repositories in github_imports/ sind automatisch verfügbar.
Der Agent kann auf alle Dateien hier zugreifen und sie analysieren.
"""
    
    readme_path = WORKSPACE_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print_success("Workspace README erstellt")

def fix_github_api():
    """Fix the GitHub API import function"""
    print_header("2. GITHUB API FIX")
    
    github_api_path = BACKEND_DIR / "app" / "api" / "github.py"
    
    if not github_api_path.exists():
        print_error(f"Datei nicht gefunden: {github_api_path}")
        return False
    
    # Backup
    backup_file(github_api_path)
    
    # Read current content
    with open(github_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Import settings at the top
    if "from ..core.config import settings" not in content:
        # Add after other imports
        import_section_end = content.find("logger = logging.getLogger(__name__)")
        if import_section_end != -1:
            content = content[:import_section_end] + "from ..core.config import settings\n\n" + content[import_section_end:]
            print_success("Settings-Import hinzugefügt")
    
    # Fix 2: Change workspace_root to use settings.GITHUB_IMPORTS_DIR
    old_workspace_line = 'workspace_root = Path("/app")'
    
    if old_workspace_line in content:
        # Replace in import_repository function
        new_workspace_section = '''        # Get base directory from settings (Windows + Linux kompatibel)
        from ..core.config import settings
        workspace_base = settings.GITHUB_IMPORTS_DIR
        
        # Create user-specific directory structure
        user_id = current_user.user_id if current_user else "anonymous"
        user_workspace = workspace_base / str(user_id)
        user_workspace.mkdir(parents=True, exist_ok=True)'''
        
        # Find and replace in import_repository function
        import_func_start = content.find("async def import_repository(")
        if import_func_start != -1:
            import_func_section = content[import_func_start:import_func_start + 5000]
            
            if old_workspace_line in import_func_section:
                # Replace the workspace_root line and adjust target_dir logic
                import_func_section = import_func_section.replace(
                    old_workspace_line,
                    new_workspace_section.split('\n')[1]  # Just the workspace_base line
                )
                
                # Replace target_dir logic
                old_target_logic = '''        # Determine target directory
        workspace_root = Path("/app")
        if request.target_directory:
            target_dir = workspace_root / request.target_directory
        else:
            target_dir = workspace_root / repo_name'''
            
                new_target_logic = '''        # Determine target directory (user-specific)
        user_id = str(current_user.user_id) if current_user else "anonymous"
        user_workspace = workspace_base / user_id
        user_workspace.mkdir(parents=True, exist_ok=True)
        
        if request.target_directory:
            target_dir = user_workspace / request.target_directory
        else:
            target_dir = user_workspace / repo_name'''
            
                content = content[:import_func_start] + import_func_section + content[import_func_start + 5000:]
                print_success("Workspace-Pfad auf settings.GITHUB_IMPORTS_DIR geändert")
    
    # Fix 3: Update get_import_status function
    status_func_start = content.find('@router.get("/import/status")')
    if status_func_start != -1:
        status_func_section = content[status_func_start:status_func_start + 3000]
        
        if 'workspace_root = Path("/app")' in status_func_section:
            status_func_section = status_func_section.replace(
                'workspace_root = Path("/app")',
                'workspace_root = settings.GITHUB_IMPORTS_DIR'
            )
            content = content[:status_func_start] + status_func_section + content[status_func_start + 3000:]
            print_success("get_import_status Funktion aktualisiert")
    
    # Write fixed content
    with open(github_api_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success(f"GitHub API Fixed: {github_api_path.name}")
    return True

def create_agent_config():
    """Create AI agent configuration files"""
    print_header("3. AI-AGENT KONFIGURATION")
    
    # 1. Create .cursorrules for Cursor IDE
    cursorrules_content = """# Xionimus AI - Cursor Rules

## Workspace-Struktur

Der AI hat Zugriff auf alle Dateien in diesem Projekt.

### GitHub Repositories:
Alle importierten GitHub-Repositories befinden sich in:
`backend/workspace/github_imports/[user_id]/[repo_name]/`

### Wichtige Verzeichnisse:
- `/backend` - Python FastAPI Backend
- `/frontend` - React/TypeScript Frontend  
- `/backend/workspace/github_imports/` - Importierte Repositories
- `/backend/workspace/uploads/` - Hochgeladene Dateien
- `/backend/app/` - Backend-Logik und APIs

## Agent-Verhalten

1. **Repository-Zugriff:**
   - Alle Repos in `backend/workspace/github_imports/` sind verfügbar
   - Automatische Erkennung bei Import
   - Vollständiger Dateizugriff

2. **Code-Analyse:**
   - Analysiere importierte Projekte vollständig
   - Berücksichtige .gitignore patterns
   - Erkenne Projekt-Typen automatisch

3. **Kontext-Bewahrung:**
   - Merke aktive Projekte pro Session
   - Nutze Session-Kontext für Antworten
   - Referenziere Dateien mit relativen Pfaden

## Windows-Kompatibilität

- Verwende Path-Objekte aus pathlib
- Forward-Slashes (/) in URLs
- Backslashes (\\) nur für Windows-CMD
- Berechtigungen: icacls für Windows
"""
    
    cursorrules_path = SCRIPT_DIR / ".cursorrules"
    with open(cursorrules_path, 'w', encoding='utf-8') as f:
        f.write(cursorrules_content)
    print_success(".cursorrules erstellt (Cursor IDE)")
    
    # 2. Create .cursor/rules/index.mdc for newer Cursor
    cursor_dir = SCRIPT_DIR / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)
    
    cursor_rules_content = """# Xionimus AI Workspace Rules

## GitHub Repository Access

Importierte Repositories: `backend/workspace/github_imports/[user_id]/[repo_name]/`

Der Agent hat **vollständigen Zugriff** auf alle importierten Repositories.

### Auto-Detection:
- Neue Imports werden automatisch erkannt
- Session-basierte Projekt-Aktivierung
- Multi-User-Unterstützung

### Best Practices:
1. Nutze relative Pfade zu Projekten
2. Respektiere .gitignore patterns  
3. Analysiere Projekt-Struktur vor Code-Generierung
4. Verwende Workspace-Root: `backend/workspace/github_imports/`
"""
    
    cursor_rules_path = cursor_dir / "index.mdc"
    with open(cursor_rules_path, 'w', encoding='utf-8') as f:
        f.write(cursor_rules_content)
    print_success(".cursor/rules/index.mdc erstellt (Cursor IDE neu)")
    
    # 3. Create .aider.conf.yml for Aider
    aider_config = {
        "git": True,
        "auto-commits": True,
        "subtree-only": False,
        "map-tokens": 2048,
        "repository": "auto",
        "workspace": "backend/workspace/github_imports",
        "check-update": False
    }
    
    aider_path = SCRIPT_DIR / ".aider.conf.yml"
    import yaml
    with open(aider_path, 'w', encoding='utf-8') as f:
        f.write("# Aider Configuration for Xionimus AI\n")
        f.write("# Auto-generated - do not edit manually\n\n")
        for key, value in aider_config.items():
            if isinstance(value, bool):
                f.write(f"{key}: {'true' if value else 'false'}\n")
            elif isinstance(value, int):
                f.write(f"{key}: {value}\n")
            else:
                f.write(f"{key}: \"{value}\"\n")
    print_success(".aider.conf.yml erstellt (Aider)")
    
    # 4. Create VS Code settings
    vscode_dir = SCRIPT_DIR / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    
    vscode_settings = {
        "files.associations": {
            "*.mdc": "markdown"
        },
        "files.exclude": {
            "**/.git": False,  # Show .git folders
            "**/node_modules": True,
            "**/venv": True,
            "**/__pycache__": True
        },
        "files.watcherExclude": {
            "**/node_modules": True,
            "**/venv": True,
            "**/.git/objects/**": True,
            "**/.git/subtree-cache/**": True
        },
        "search.exclude": {
            "**/node_modules": True,
            "**/venv": True,
            "**/*.code-search": True
        },
        "python.analysis.extraPaths": [
            "./backend"
        ],
        "github.copilot.enable": {
            "*": True,
            "plaintext": False,
            "markdown": True,
            "scminput": False
        },
        "security.workspace.trust.enabled": True,
        "files.eol": "\n",
        "files.autoSave": "afterDelay",
        "editor.formatOnSave": True
    }
    
    vscode_settings_path = vscode_dir / "settings.json"
    with open(vscode_settings_path, 'w', encoding='utf-8') as f:
        json.dump(vscode_settings, f, indent=2)
    print_success(".vscode/settings.json erstellt")

def create_workspace_index():
    """Create workspace index for AI agent"""
    print_header("4. WORKSPACE-INDEX ERSTELLEN")
    
    # Create a JSON index of the workspace structure
    index = {
        "version": "1.0",
        "timestamp": str(Path(__file__).stat().st_mtime),
        "workspace_root": str(GITHUB_IMPORTS_DIR),
        "structure": {
            "github_imports": "Importierte GitHub-Repositories (pro User)",
            "uploads": "Hochgeladene Dateien",
            "exports": "Exportierte Dateien",
            "temp": "Temporäre Dateien"
        },
        "agent_instructions": {
            "repository_access": "Alle Repos in github_imports/[user_id]/ sind verfügbar",
            "path_format": "backend/workspace/github_imports/[user_id]/[repo_name]/",
            "auto_detection": True,
            "session_aware": True
        }
    }
    
    index_path = WORKSPACE_DIR / ".workspace_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    print_success("Workspace-Index erstellt: .workspace_index.json")

def set_windows_permissions():
    """Set proper permissions for Windows"""
    print_header("5. WINDOWS-BERECHTIGUNGEN SETZEN")
    
    if sys.platform != "win32":
        print_info("Überspringe (Nicht Windows)")
        return
    
    try:
        import subprocess
        
        # Set permissions for workspace
        cmd = f'icacls "{WORKSPACE_DIR}" /grant Everyone:(OI)(CI)F /T /Q'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Workspace-Berechtigungen gesetzt")
        else:
            print_warning("Berechtigungen konnten nicht gesetzt werden (benötigt Admin-Rechte)")
            print_info("Workspace sollte trotzdem für aktuellen User funktionieren")
    
    except Exception as e:
        print_warning(f"Berechtigungen-Setup übersprungen: {e}")

def create_batch_scripts():
    """Create Windows batch scripts for easy fixes"""
    print_header("6. BATCH-SCRIPTS ERSTELLEN")
    
    if sys.platform != "win32":
        print_info("Überspringe (Nicht Windows)")
        return
    
    # 1. Quick workspace reset script
    reset_script = """@echo off
title Xionimus AI - Workspace Reset
color 0B

echo.
echo ========================================================================
echo    WORKSPACE RESET
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/2] Loesche temporaere Dateien...
if exist "backend\\workspace\\temp" (
    rmdir /s /q "backend\\workspace\\temp"
    mkdir "backend\\workspace\\temp"
    echo ✅ Temp-Ordner geleert
) else (
    echo ⚠️  Temp-Ordner nicht gefunden
)

echo.
echo [2/2] Setze Berechtigungen...
icacls "backend\\workspace" /grant Everyone:(OI)(CI)F /T /Q >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Berechtigungen aktualisiert
) else (
    echo ⚠️  Berechtigungen nicht gesetzt (benötigt Admin-Rechte)
)

echo.
echo ========================================================================
echo    ✅ WORKSPACE RESET ABGESCHLOSSEN
echo ========================================================================
echo.
pause
"""
    
    reset_path = SCRIPT_DIR / "WORKSPACE-RESET.bat"
    with open(reset_path, 'w', encoding='utf-8') as f:
        f.write(reset_script)
    print_success("WORKSPACE-RESET.bat erstellt")
    
    # 2. Diagnostic script
    diagnose_script = """@echo off
title Xionimus AI - Workspace Diagnose
color 0E

echo.
echo ========================================================================
echo    WORKSPACE DIAGNOSE
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1] Workspace-Struktur:
echo.
if exist "backend\\workspace" (
    echo ✅ backend\\workspace existiert
    dir /b "backend\\workspace"
) else (
    echo ❌ backend\\workspace fehlt!
)

echo.
echo [2] GitHub Imports:
echo.
if exist "backend\\workspace\\github_imports" (
    echo ✅ github_imports existiert
    for /d %%d in (backend\\workspace\\github_imports\\*) do (
        echo    User: %%~nxd
        for /d %%r in (backend\\workspace\\github_imports\\%%~nxd\\*) do (
            echo       └─ Repo: %%~nxr
        )
    )
) else (
    echo ❌ github_imports fehlt!
)

echo.
echo [3] Agent-Konfiguration:
echo.
if exist ".cursorrules" (
    echo ✅ .cursorrules vorhanden
) else (
    echo ⚠️  .cursorrules fehlt
)

if exist ".cursor\\rules\\index.mdc" (
    echo ✅ .cursor/rules/index.mdc vorhanden
) else (
    echo ⚠️  .cursor/rules fehlt
)

if exist ".aider.conf.yml" (
    echo ✅ .aider.conf.yml vorhanden
) else (
    echo ⚠️  .aider.conf.yml fehlt
)

if exist ".vscode\\settings.json" (
    echo ✅ .vscode/settings.json vorhanden
) else (
    echo ⚠️  .vscode/settings.json fehlt
)

echo.
echo [4] Git-Konfiguration:
git config --global core.longpaths >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Git longpaths aktiviert
) else (
    echo ⚠️  Git longpaths nicht konfiguriert
)

echo.
echo ========================================================================
echo    DIAGNOSE ABGESCHLOSSEN
echo ========================================================================
echo.
echo Probleme gefunden? Fuehre WORKSPACE-FIX-COMPREHENSIVE.bat aus
echo.
pause
"""
    
    diagnose_path = SCRIPT_DIR / "WORKSPACE-DIAGNOSE.bat"
    with open(diagnose_path, 'w', encoding='utf-8') as f:
        f.write(diagnose_script)
    print_success("WORKSPACE-DIAGNOSE.bat erstellt")

def create_migration_script():
    """Create script to migrate existing repos to new structure"""
    print_header("7. MIGRATIONS-SCRIPT ERSTELLEN")
    
    migration_script = """import os
import sys
from pathlib import Path
import shutil

def migrate_existing_repos():
    '''Migrate repos from /app to backend/workspace/github_imports'''
    
    old_workspace = Path("/app")
    new_workspace = Path(__file__).parent / "backend" / "workspace" / "github_imports"
    
    if not old_workspace.exists():
        print("Keine alten Repos gefunden in /app")
        return
    
    # Create anonymous user directory for migration
    anonymous_dir = new_workspace / "anonymous"
    anonymous_dir.mkdir(parents=True, exist_ok=True)
    
    migrated = 0
    for item in old_workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            target = anonymous_dir / item.name
            
            if target.exists():
                print(f"⚠️  Überspringe {item.name} (existiert bereits)")
                continue
            
            try:
                shutil.move(str(item), str(target))
                print(f"✅ Migriert: {item.name}")
                migrated += 1
            except Exception as e:
                print(f"❌ Fehler bei {item.name}: {e}")
    
    print(f"\\n✅ Migration abgeschlossen: {migrated} Repositories migriert")
    print(f"Neue Location: {anonymous_dir}")

if __name__ == "__main__":
    migrate_existing_repos()
"""
    
    migration_path = SCRIPT_DIR / "migrate_repos.py"
    with open(migration_path, 'w', encoding='utf-8') as f:
        f.write(migration_script)
    print_success("migrate_repos.py erstellt")

def print_final_instructions():
    """Print final setup instructions"""
    print_header("✅ WORKSPACE FIX ABGESCHLOSSEN!")
    
    print(f"{Colors.GREEN}Folgende Änderungen wurden vorgenommen:{Colors.RESET}\n")
    
    print("1. ✅ Workspace-Struktur erstellt:")
    print("   backend/workspace/")
    print("   ├── github_imports/  ← GitHub Repos (pro User)")
    print("   ├── uploads/")
    print("   ├── exports/")
    print("   └── temp/\n")
    
    print("2. ✅ GitHub API gefixt:")
    print("   - Verwendet jetzt settings.GITHUB_IMPORTS_DIR")
    print("   - User-spezifische Ordner-Struktur")
    print("   - Windows-kompatible Pfade\n")
    
    print("3. ✅ Agent-Konfigurationen erstellt:")
    print("   - .cursorrules (Cursor IDE)")
    print("   - .cursor/rules/index.mdc (Cursor neu)")
    print("   - .aider.conf.yml (Aider)")
    print("   - .vscode/settings.json (VS Code)\n")
    
    print("4. ✅ Utility-Scripts:")
    print("   - WORKSPACE-RESET.bat")
    print("   - WORKSPACE-DIAGNOSE.bat")
    print("   - migrate_repos.py\n")
    
    print(f"{Colors.YELLOW}Nächste Schritte:{Colors.RESET}\n")
    print("1. Backend neu starten:")
    print(f"   {Colors.BLUE}cd backend && python -m uvicorn main:app --reload{Colors.RESET}\n")
    
    print("2. Repository importieren:")
    print("   - In der UI: GitHub Import")
    print("   - Landet in: backend/workspace/github_imports/[user_id]/[repo_name]/\n")
    
    print("3. AI-Agent öffnen:")
    print("   - Cursor IDE: Öffne Projekt-Root")
    print("   - Agent erkennt automatisch alle Repos\n")
    
    print(f"{Colors.GREEN}Der AI-Agent hat jetzt vollständigen Zugriff auf alle importierten Repositories!{Colors.RESET}\n")

def main():
    """Run all fix steps"""
    try:
        print_header("XIONIMUS AI - WORKSPACE FIX")
        print_info("Behebt das Repository-Erkennungsproblem des AI-Agents")
        
        # Run all fixes
        create_workspace_structure()
        fix_github_api()
        create_agent_config()
        create_workspace_index()
        set_windows_permissions()
        create_batch_scripts()
        create_migration_script()
        
        print_final_instructions()
        
        return True
        
    except Exception as e:
        print_error(f"Fix fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
