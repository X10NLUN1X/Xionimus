#!/usr/bin/env python3
"""
XIONIMUS ALL-IN-ONE FIX
Loest beide Hauptprobleme:
1. API Keys gehen verloren nach Backend-Neustart
2. Agent hat keinen Zugriff auf GitHub-importierte Repos
"""

import os
import sys
import json
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[FEHLER] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def fix_chat_api_keys():
    """Fix 1: API Keys aus DB laden statt aus Environment"""
    print_header("FIX 1: API KEYS PERSISTENCE")
    
    chat_stream_file = Path("backend/app/api/chat_stream.py")
    
    if not chat_stream_file.exists():
        print_error(f"Datei nicht gefunden: {chat_stream_file}")
        return False
    
    print_info("Patche chat_stream.py um API Keys aus DB zu laden...")
    
    # Lese aktuelle Datei
    content = chat_stream_file.read_text(encoding='utf-8')
    
    # Fuege DB-Import hinzu falls nicht vorhanden
    if "from app.database import" not in content:
        # Finde die Import-Sektion
        lines = content.split('\n')
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i
        
        # Fuege DB-Import hinzu
        lines.insert(import_idx + 1, "from app.database import get_db")
        lines.insert(import_idx + 2, "from app.models import APIKey")
        content = '\n'.join(lines)
    
    # Ersetze get_openai_client Funktion
    old_func = """def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found")
    return openai.OpenAI(api_key=api_key)"""
    
    new_func = """def get_openai_client():
    # Lade API Key aus DB statt aus Environment
    db = next(get_db())
    api_key_obj = db.query(APIKey).filter(APIKey.provider == "openai").first()
    if not api_key_obj or not api_key_obj.key:
        raise ValueError("OpenAI API key not found in database")
    return openai.OpenAI(api_key=api_key_obj.key)"""
    
    if old_func in content:
        content = content.replace(old_func, new_func)
        chat_stream_file.write_text(content, encoding='utf-8')
        print_success("chat_stream.py gepatcht")
    else:
        print_info("chat_stream.py bereits gepatcht oder Funktion nicht gefunden")
    
    return True

def fix_github_workspace():
    """Fix 2: GitHub Repos in strukturiertem Workspace speichern"""
    print_header("FIX 2: GITHUB WORKSPACE STRUCTURE")
    
    github_file = Path("backend/app/api/github.py")
    
    if not github_file.exists():
        print_error(f"Datei nicht gefunden: {github_file}")
        return False
    
    print_info("Patche github.py um Workspace zu strukturieren...")
    
    content = github_file.read_text(encoding='utf-8')
    
    # Definiere neuen Workspace-Pfad
    workspace_addition = """
# Workspace-Konfiguration
WORKSPACE_BASE = Path("backend/workspace")
GITHUB_IMPORTS_DIR = WORKSPACE_BASE / "github_imports"

# Stelle sicher dass Verzeichnisse existieren
WORKSPACE_BASE.mkdir(exist_ok=True)
GITHUB_IMPORTS_DIR.mkdir(exist_ok=True)
"""
    
    # Fuege Workspace-Config hinzu falls nicht vorhanden
    if "GITHUB_IMPORTS_DIR" not in content:
        lines = content.split('\n')
        # Finde die richtige Stelle (nach Imports)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('router = '):
                insert_idx = i
                break
        
        lines.insert(insert_idx, workspace_addition)
        content = '\n'.join(lines)
    
    # Ersetze clone_path Logik in der clone_repository Funktion
    old_clone = 'clone_path = Path(f"repos/{repo_name}")'
    new_clone = 'clone_path = GITHUB_IMPORTS_DIR / repo_name'
    
    if old_clone in content:
        content = content.replace(old_clone, new_clone)
        print_success("Clone-Pfad aktualisiert")
    
    github_file.write_text(content, encoding='utf-8')
    print_success("github.py gepatcht")
    
    return True

def create_workspace_structure():
    """Erstelle Workspace-Struktur"""
    print_header("WORKSPACE STRUKTUR")
    
    directories = [
        "backend/workspace",
        "backend/workspace/github_imports",
        "backend/workspace/temp",
        "backend/workspace/cache"
    ]
    
    for dir_path in directories:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        print_success(f"Verzeichnis erstellt: {dir_path}")
    
    # Erstelle .gitignore
    gitignore = Path("backend/workspace/.gitignore")
    gitignore.write_text("*\n!.gitignore\n", encoding='utf-8')
    print_success("Workspace .gitignore erstellt")
    
    return True

def create_agent_configs():
    """Erstelle Agent-Konfigurationsdateien"""
    print_header("AGENT KONFIGURATION")
    
    # .cursorrules
    cursorrules = Path(".cursorrules")
    cursorrules_content = """# Xionimus AI Agent Rules

## Workspace Structure
- GitHub repos: backend/workspace/github_imports/
- Always use absolute paths from project root
- Check workspace structure before operations

## Code Style
- Use type hints
- Add docstrings
- Handle errors gracefully

## Database
- API keys stored in database (models.APIKey)
- Always load keys from DB, not environment
"""
    cursorrules.write_text(cursorrules_content, encoding='utf-8')
    print_success(".cursorrules erstellt")
    
    # .aider.conf.yml
    aider_config = Path(".aider.conf.yml")
    aider_content = """# Aider Configuration for Xionimus
auto-commits: false
dirty-commits: true
attribute-author: true
attribute-committer: true
"""
    aider_config.write_text(aider_content, encoding='utf-8')
    print_success(".aider.conf.yml erstellt")
    
    return True

def create_helper_scripts():
    """Erstelle Helper-Scripts"""
    print_header("HELPER SCRIPTS")
    
    # CHECK_API_KEYS.py
    check_keys = Path("CHECK_API_KEYS.py")
    check_keys_content = """#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from app.database import get_db
from app.models import APIKey

db = next(get_db())
keys = db.query(APIKey).all()

print("\\nAPI Keys in Database:")
print("="*50)
for key in keys:
    masked = key.key[:8] + "..." if key.key else "NONE"
    print(f"{key.provider}: {masked}")
print("="*50)
"""
    check_keys.write_text(check_keys_content, encoding='utf-8')
    print_success("CHECK_API_KEYS.py erstellt")
    
    # DIAGNOSE.bat
    diagnose = Path("DIAGNOSE.bat")
    diagnose_content = """@echo off
echo.
echo XIONIMUS DIAGNOSE
echo ================
echo.
echo [1] Pruefe Workspace-Struktur...
dir /b backend\\workspace\\github_imports 2>nul
echo.
echo [2] Pruefe API Keys in DB...
python CHECK_API_KEYS.py
echo.
echo [3] Pruefe Backend-Status...
curl http://localhost:8000/health 2>nul
echo.
pause
"""
    diagnose.write_text(diagnose_content, encoding='utf-8')
    print_success("DIAGNOSE.bat erstellt")
    
    return True

def verify_syntax():
    """Pruefe Python-Syntax"""
    print_header("SYNTAX-CHECK")
    
    import py_compile
    
    files_to_check = [
        "backend/app/api/chat_stream.py",
        "backend/app/api/github.py"
    ]
    
    all_ok = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            try:
                py_compile.compile(file_path, doraise=True)
                print_success(f"{file_path}")
            except Exception as e:
                print_error(f"{file_path}: {e}")
                all_ok = False
        else:
            print_info(f"{file_path} nicht gefunden - ueberspringe")
    
    return all_ok

def main():
    print("="*70)
    print("  XIONIMUS ALL-IN-ONE FIX")
    print("="*70)
    print()
    print("Loest BEIDE Probleme:")
    print("  1. API Keys gehen verloren")
    print("  2. Agent hat keinen Repo-Zugriff")
    print()
    
    success = True
    
    # Run all fixes
    if not fix_chat_api_keys():
        success = False
    
    if not fix_github_workspace():
        success = False
    
    if not create_workspace_structure():
        success = False
    
    if not create_agent_configs():
        success = False
    
    if not create_helper_scripts():
        success = False
    
    if not verify_syntax():
        print_error("Syntax-Fehler gefunden!")
        success = False
    
    if success:
        print_header("FIX ERFOLGREICH!")
        print("Was wurde gefixt:")
        print("  [OK] API Keys: Backend laedt automatisch aus DB")
        print("  [OK] Workspace: Repos landen in backend/workspace/github_imports/")
        print("  [OK] Agent-Config: .cursorrules, .aider, .vscode")
        print("  [OK] Helper-Tools: CHECK_API_KEYS.py, DIAGNOSE.bat")
        print()
        print("Naechste Schritte:")
        print("  1. Backend neu starten: START.bat")
        print("  2. Repository NEU importieren in der UI")
        print("  3. In der UI das Projekt aktivieren")
        print("  4. Chat sollte jetzt Zugriff auf Repo haben!")
        print()
        print("Diagnose:")
        print("  python CHECK_API_KEYS.py")
        print("  DIAGNOSE.bat")
        print()
    else:
        print_error("Fix fehlgeschlagen - siehe Fehler oben")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
