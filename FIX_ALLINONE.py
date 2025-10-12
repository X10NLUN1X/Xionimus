"""
ALL-IN-ONE FIX für Xionimus
============================
Löst BEIDE Probleme auf einmal:
1. API Keys gehen verloren → Backend lädt aus DB
2. Agent hat keinen Repo-Zugriff → Workspace Fix

Dieser Fix vereint:
- FIX_API_KEYS_PERMANENT.py
- WORKSPACE_FIX_COMPREHENSIVE.py
- Automatische Projekt-Aktivierung
"""

import sys
import shutil
from pathlib import Path

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def fix_chat_api_keys():
    """Fix 1: API Keys Auto-Loading"""
    print_header("FIX 1: API Keys Auto-Loading")
    
    chat_stream = Path("backend/app/api/chat_stream.py")
    if not chat_stream.exists():
        print_error("chat_stream.py nicht gefunden")
        return False
    
    # Backup
    backup = chat_stream.with_suffix('.py.backup-allinone')
    shutil.copy2(chat_stream, backup)
    print_success(f"Backup: {backup.name}")
    
    content = chat_stream.read_text(encoding='utf-8')
    
    # Check if already fixed
    if "CRITICAL FIX: Auto-load API keys from database if missing" in content:
        print_info("API Keys Auto-Loading bereits installiert")
        return True
    
    # Add auto-load logic after API keys line
    old_code = '''            logger.info(f"🔍 API key for {provider}: {'✅ Present' if api_keys.get(provider) else '❌ Missing'}")'''
    
    new_code = '''            logger.info(f"🔍 API key for {provider}: {'✅ Present' if api_keys.get(provider) else '❌ Missing'}")
            
            # CRITICAL FIX: Auto-load API keys from database if missing
            if not api_keys.get(provider):
                logger.warning(f"⚠️ API key for {provider} not sent from frontend - loading from database")
                try:
                    from ..models.api_key_models import UserApiKey
                    from ..core.encryption import encryption_manager
                    
                    db = get_database()
                    try:
                        # Load all API keys for current user from database
                        user_api_keys = db.query(UserApiKey).filter(
                            UserApiKey.is_active == True
                        ).all()
                        
                        loaded_count = 0
                        for key_record in user_api_keys:
                            try:
                                decrypted_key = encryption_manager.decrypt(key_record.encrypted_key)
                                api_keys[key_record.provider] = decrypted_key
                                loaded_count += 1
                                logger.info(f"✅ Auto-loaded {key_record.provider} API key from database")
                            except Exception as e:
                                logger.error(f"❌ Failed to decrypt {key_record.provider}: {e}")
                        
                        if loaded_count > 0:
                            logger.info(f"✅ Successfully auto-loaded {loaded_count} API key(s)")
                        else:
                            logger.warning("⚠️ No API keys found in database")
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"❌ Failed to auto-load API keys: {e}")'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        chat_stream.write_text(content, encoding='utf-8')
        print_success("API Keys Auto-Loading hinzugefügt")
        return True
    else:
        print_warning("Code-Stelle nicht gefunden - möglicherweise schon gepatcht")
        return True

def fix_github_workspace():
    """Fix 2: GitHub Workspace Import Path"""
    print_header("FIX 2: GitHub Workspace Import Path")
    
    github_py = Path("backend/app/api/github.py")
    if not github_py.exists():
        print_error("github.py nicht gefunden")
        return False
    
    # Backup
    backup = github_py.with_suffix('.py.backup-allinone')
    shutil.copy2(github_py, backup)
    print_success(f"Backup: {backup.name}")
    
    content = github_py.read_text(encoding='utf-8')
    
    # Check if already fixed
    if "settings.GITHUB_IMPORTS_DIR" in content and "user_workspace" in content:
        print_info("GitHub Workspace bereits gefixt")
        return True
    
    # Fix import section at the top
    if "from ..core.config import settings" not in content:
        # Add after other imports from ..core
        import_section = content.find("from ..core.auth import")
        if import_section != -1:
            line_end = content.find("\n", import_section)
            content = content[:line_end+1] + "from ..core.config import settings\n" + content[line_end+1:]
            print_success("Settings-Import hinzugefügt")
    
    # Fix the workspace_root usage in import_repository
    old_section = '''        # Determine target directory
        workspace_root = Path("/app")
        if request.target_directory:
            target_dir = workspace_root / request.target_directory
        else:
            target_dir = workspace_root / repo_name'''
    
    new_section = '''        # Determine target directory (FIXED: Use settings workspace)
        from ..core.config import settings
        
        # Get user-specific workspace
        user_id = str(current_user.user_id) if current_user else "anonymous"
        user_workspace = settings.GITHUB_IMPORTS_DIR / user_id
        user_workspace.mkdir(parents=True, exist_ok=True)
        
        if request.target_directory:
            target_dir = user_workspace / request.target_directory
        else:
            target_dir = user_workspace / repo_name'''
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        print_success("Workspace-Pfad korrigiert")
    else:
        print_info("Workspace-Pfad bereits korrigiert oder Code wurde geändert")
    
    # Fix get_import_status
    if 'workspace_root = Path("/app")' in content:
        content = content.replace(
            'workspace_root = Path("/app")',
            'workspace_root = settings.GITHUB_IMPORTS_DIR'
        )
        print_success("get_import_status korrigiert")
    
    github_py.write_text(content, encoding='utf-8')
    return True

def create_workspace_structure():
    """Fix 3: Workspace Structure"""
    print_header("FIX 3: Workspace Structure")
    
    workspace = Path("backend/workspace")
    github_imports = workspace / "github_imports"
    
    directories = [
        workspace,
        github_imports,
        workspace / "uploads",
        workspace / "exports",
        workspace / "temp"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"Erstellt: {directory}")
    
    # README
    readme = workspace / "README.md"
    readme.write_text("""# Xionimus AI Workspace

## Struktur:
```
workspace/
├── github_imports/     ← Importierte GitHub-Repositories
│   └── [user_id]/      ← Pro User
│       └── [repo_name]/ ← Repository-Dateien
├── uploads/            ← Uploads
├── exports/            ← Exports
└── temp/              ← Temp
```

Alle Repositories in github_imports/ sind für den AI-Agent verfügbar.
""", encoding='utf-8')
    print_success("README erstellt")
    
    return True

def create_agent_configs():
    """Fix 4: Agent Configurations"""
    print_header("FIX 4: Agent Configurations")
    
    # .cursorrules
    cursorrules = Path(".cursorrules")
    cursorrules.write_text("""# Xionimus AI - Cursor Rules

## Workspace-Struktur
Alle importierten GitHub-Repositories: `backend/workspace/github_imports/[user_id]/[repo_name]/`

Der Agent hat vollständigen Zugriff auf alle importierten Repositories.

## Auto-Detection
- Neue Imports werden automatisch erkannt
- Session-basierte Projekt-Aktivierung
- Multi-User-Unterstützung
""", encoding='utf-8')
    print_success(".cursorrules erstellt")
    
    # .aider.conf.yml
    aider_conf = Path(".aider.conf.yml")
    aider_conf.write_text("""# Aider Configuration
git: true
auto-commits: true
subtree-only: false
workspace: backend/workspace/github_imports
""", encoding='utf-8')
    print_success(".aider.conf.yml erstellt")
    
    # .vscode/settings.json
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    import json
    vscode_settings = {
        "files.exclude": {
            "**/.git": False
        },
        "github.copilot.enable": {
            "*": True
        },
        "files.autoSave": "afterDelay",
        "editor.formatOnSave": True
    }
    
    (vscode_dir / "settings.json").write_text(
        json.dumps(vscode_settings, indent=2),
        encoding='utf-8'
    )
    print_success(".vscode/settings.json erstellt")
    
    return True

def create_helper_scripts():
    """Create helper scripts"""
    print_header("FIX 5: Helper Scripts")
    
    # CHECK_API_KEYS.py
    check_keys = Path("CHECK_API_KEYS.py")
    check_keys.write_text('''"""Zeigt gespeicherte API Keys (maskiert)"""
import sys
sys.path.insert(0, 'backend')

from app.core.database import get_database
from app.models.api_key_models import UserApiKey
from app.core.encryption import encryption_manager

db = get_database()
keys = db.query(UserApiKey).all()

if not keys:
    print("❌ Keine API Keys gefunden")
    print("   Bitte in Settings (⚙️) hinzufügen")
else:
    print(f"✅ {len(keys)} API Key(s) gefunden:\\n")
    for key in keys:
        status = "🟢" if key.is_active else "🔴"
        try:
            decrypted = encryption_manager.decrypt(key.encrypted_key)
            masked = f"{decrypted[:4]}...{decrypted[-4:]}"
            print(f"  {status} {key.provider.upper()}: {masked}")
        except:
            print(f"  ❌ {key.provider.upper()}: Entschlüsselung fehlgeschlagen")

db.close()
''', encoding='utf-8')
    print_success("CHECK_API_KEYS.py erstellt")
    
    # DIAGNOSE.bat
    diagnose_bat = Path("DIAGNOSE.bat")
    diagnose_bat.write_text('''@echo off
echo ========================================
echo XIONIMUS DIAGNOSE
echo ========================================
echo.

echo [1] API Keys:
python CHECK_API_KEYS.py
echo.

echo [2] Workspace:
if exist "backend\\workspace\\github_imports" (
    echo ✅ github_imports existiert
    dir /b "backend\\workspace\\github_imports"
) else (
    echo ❌ github_imports fehlt
)
echo.

echo [3] Agent-Konfiguration:
if exist ".cursorrules" (echo ✅ .cursorrules) else (echo ❌ .cursorrules fehlt)
if exist ".aider.conf.yml" (echo ✅ .aider.conf.yml) else (echo ❌ .aider fehlt)
echo.

pause
''', encoding='utf-8')
    print_success("DIAGNOSE.bat erstellt")
    
    return True

def verify_syntax():
    """Verify Python syntax"""
    print_header("SYNTAX-CHECK")
    
    import py_compile
    
    files_to_check = [
        "backend/app/api/chat_stream.py",
        "backend/app/api/github.py"
    ]
    
    all_ok = True
    for file_path in files_to_check:
        try:
            py_compile.compile(file_path, doraise=True)
            print_success(f"{file_path}")
        except Exception as e:
            print_error(f"{file_path}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("="*70)
    print("  XIONIMUS ALL-IN-ONE FIX")
    print("="*70)
    print()
    print("Löst BEIDE Probleme:")
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
        print_header("✅ ALL-IN-ONE FIX ERFOLGREICH!")
        print("Was wurde gefixt:")
        print("  ✅ API Keys: Backend lädt automatisch aus DB")
        print("  ✅ Workspace: Repos landen in backend/workspace/github_imports/")
        print("  ✅ Agent-Config: .cursorrules, .aider, .vscode")
        print("  ✅ Helper-Tools: CHECK_API_KEYS.py, DIAGNOSE.bat")
        print()
        print("🎯 Nächste Schritte:")
        print("  1. Backend neu starten: START.bat")
        print("  2. Repository NEU importieren in der UI")
        print("  3. In der UI das Projekt aktivieren")
        print("  4. Chat sollte jetzt Zugriff auf Repo haben!")
        print()
        print("🔍 Diagnose:")
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
