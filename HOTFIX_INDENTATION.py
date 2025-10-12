"""
HOTFIX: IndentationError in backend/app/api/github.py
Behebt den Fehler an Zeile 687
"""

import sys
from pathlib import Path

def fix_github_api():
    """Fix the indentation error in github.py"""
    
    # Find the file
    backend_dir = Path(__file__).parent / "backend"
    github_api_path = backend_dir / "app" / "api" / "github.py"
    
    if not github_api_path.exists():
        print(f"❌ Datei nicht gefunden: {github_api_path}")
        print(f"   Aktuelles Verzeichnis: {Path.cwd()}")
        print(f"   Bitte führe das Script aus dem Xionimus-Root-Verzeichnis aus!")
        return False
    
    print(f"✅ Datei gefunden: {github_api_path}")
    
    # Backup erstellen
    backup_path = github_api_path.with_suffix('.py.backup-hotfix')
    import shutil
    shutil.copy2(github_api_path, backup_path)
    print(f"✅ Backup erstellt: {backup_path.name}")
    
    # Read content
    with open(github_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix: Replace the problematic section
    # Das Problem ist, dass workspace_root = Path("/app") bleiben muss,
    # aber wir müssen es durch settings.GITHUB_IMPORTS_DIR ersetzen
    
    old_section = '''        # Determine target directory
        workspace_root = Path("/app")
        if request.target_directory:
            target_dir = workspace_root / request.target_directory
        else:
            target_dir = workspace_root / repo_name'''
    
    new_section = '''        # Determine target directory (FIXED: Use settings)
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
        print("✅ Import-Pfad korrigiert (import_repository)")
    else:
        print("⚠️  Sektion nicht gefunden - versuche alternative Methode...")
        
        # Alternative: Zeile für Zeile ersetzen
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == 'workspace_root = Path("/app")':
                # Prüfe ob wir in der import_repository Funktion sind
                # Suche rückwärts nach "async def import_repository"
                in_import_func = False
                for j in range(i-1, max(0, i-50), -1):
                    if 'async def import_repository' in lines[j]:
                        in_import_func = True
                        break
                
                if in_import_func:
                    # Ersetze diese Zeile und die folgenden
                    indent = ' ' * 8  # 8 Spaces Einrückung
                    lines[i] = f'{indent}# Determine target directory (FIXED: Use settings)'
                    lines.insert(i+1, f'{indent}from ..core.config import settings')
                    lines.insert(i+2, f'{indent}')
                    lines.insert(i+3, f'{indent}# Get user-specific workspace')
                    lines.insert(i+4, f'{indent}user_id = str(current_user.user_id) if current_user else "anonymous"')
                    lines.insert(i+5, f'{indent}user_workspace = settings.GITHUB_IMPORTS_DIR / user_id')
                    lines.insert(i+6, f'{indent}user_workspace.mkdir(parents=True, exist_ok=True)')
                    
                    # Jetzt die if/else Blöcke anpassen
                    # Finde die nächsten Zeilen mit target_dir
                    for k in range(i+7, min(len(lines), i+15)):
                        if 'target_dir = workspace_root' in lines[k]:
                            lines[k] = lines[k].replace('workspace_root', 'user_workspace')
                    
                    print(f"✅ Import-Pfad korrigiert bei Zeile {i+1}")
                    break
        
        content = '\n'.join(lines)
    
    # Fix 2: get_import_status function
    old_status = '''    workspace_root = Path("/app")'''
    new_status = '''    from ..core.config import settings
    workspace_root = settings.GITHUB_IMPORTS_DIR'''
    
    if old_status in content:
        content = content.replace(old_status, new_status)
        print("✅ Import-Status korrigiert (get_import_status)")
    
    # Write fixed content
    with open(github_api_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Datei gespeichert: {github_api_path}")
    print(f"\n📁 Backup verfügbar: {backup_path}")
    return True

def verify_syntax():
    """Verify Python syntax of fixed file"""
    backend_dir = Path(__file__).parent / "backend"
    github_api_path = backend_dir / "app" / "api" / "github.py"
    
    if not github_api_path.exists():
        return False
    
    print("\n🔍 Verifiziere Python-Syntax...")
    
    import py_compile
    try:
        py_compile.compile(str(github_api_path), doraise=True)
        print("✅ Syntax OK!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax-Fehler gefunden:")
        print(f"   {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("  XIONIMUS HOTFIX - IndentationError in github.py")
    print("="*70)
    print()
    
    if fix_github_api():
        if verify_syntax():
            print("\n" + "="*70)
            print("  ✅ HOTFIX ERFOLGREICH!")
            print("="*70)
            print("\nNächste Schritte:")
            print("  1. Backend neu starten: START.bat")
            print("  2. GitHub Import testen")
            print()
        else:
            print("\n❌ Syntax-Fehler nach Fix!")
            print("   Wiederherstellung möglich mit:")
            print("   copy backend\\app\\api\\github.py.backup-hotfix backend\\app\\api\\github.py")
    else:
        print("\n❌ Hotfix fehlgeschlagen!")
        sys.exit(1)
