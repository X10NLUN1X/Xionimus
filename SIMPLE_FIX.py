"""
SUPER-SIMPLE FIX für IndentationError
Ersetzt nur die problematischen Zeilen 684-689 in github.py
"""

import sys
from pathlib import Path

def simple_fix():
    """Ultra-einfacher Fix: Nur die kaputte Stelle ersetzen"""
    
    # Finde Datei
    github_path = Path("backend/app/api/github.py")
    
    if not github_path.exists():
        print("❌ Datei nicht gefunden!")
        print(f"   Erwarteter Pfad: {github_path.absolute()}")
        print(f"   Aktuelles Verzeichnis: {Path.cwd()}")
        print("\n💡 Bitte aus dem Xionimus-Root-Verzeichnis ausführen:")
        print("   cd C:\\AI\\Xionimus")
        print("   python SIMPLE_FIX.py")
        return False
    
    print(f"✅ Datei gefunden: {github_path}")
    
    # Backup
    import shutil
    backup = github_path.with_suffix('.py.backup-simple')
    shutil.copy2(github_path, backup)
    print(f"✅ Backup: {backup}")
    
    # Lies Datei
    with open(github_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Datei hat {len(lines)} Zeilen")
    
    # Finde die problematische Stelle
    # Suche nach: "# Determine target directory"
    
    found = False
    for i in range(len(lines)):
        if i >= 683 and i <= 690:  # Zeilen 684-690 (0-indexed)
            if 'Determine target directory' in lines[i]:
                found = True
                print(f"\n✅ Gefunden bei Zeile {i+1}")
                print(f"   Original: {lines[i].rstrip()}")
                
                # Ersetze die nächsten 6 Zeilen
                indent = '        '  # 8 Spaces
                
                new_lines = [
                    f'{indent}# Determine target directory (use settings workspace)\n',
                    f'{indent}from ..core.config import settings\n',
                    f'{indent}\n',
                    f'{indent}# User-specific directory\n',
                    f'{indent}user_id = str(current_user.user_id) if current_user else "anonymous"\n',
                    f'{indent}user_workspace = settings.GITHUB_IMPORTS_DIR / user_id\n',
                    f'{indent}user_workspace.mkdir(parents=True, exist_ok=True)\n',
                    f'{indent}\n',
                    f'{indent}if request.target_directory:\n',
                    f'{indent}    target_dir = user_workspace / request.target_directory\n',
                    f'{indent}else:\n',
                    f'{indent}    target_dir = user_workspace / repo_name\n',
                ]
                
                # Ersetze Zeilen i bis i+6
                lines[i:i+6] = new_lines
                
                print("✅ Zeilen ersetzt")
                break
    
    if not found:
        print("❌ Konnte die Stelle nicht finden!")
        print("   Die Datei wurde möglicherweise schon geändert.")
        return False
    
    # Schreibe zurück
    with open(github_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Datei gespeichert: {github_path}")
    
    # Syntax-Check
    print("\n🔍 Syntax-Check...")
    import py_compile
    try:
        py_compile.compile(str(github_path), doraise=True)
        print("✅ Syntax OK!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax-Fehler: {e}")
        print("\n🔄 Wiederherstellung aus Backup...")
        shutil.copy2(backup, github_path)
        print("✅ Backup wiederhergestellt")
        return False

if __name__ == "__main__":
    print("="*70)
    print("  XIONIMUS - SIMPLE FIX für github.py IndentationError")
    print("="*70)
    print()
    
    success = simple_fix()
    
    if success:
        print("\n" + "="*70)
        print("  ✅ FIX ERFOLGREICH!")
        print("="*70)
        print("\n🚀 Nächste Schritte:")
        print("   1. Backend starten: START.bat")
        print("   2. Browser: http://localhost:8001")
        print("   3. GitHub Import testen")
        print()
        print("📁 Backup verfügbar: backend\\app\\api\\github.py.backup-simple")
    else:
        print("\n" + "="*70)
        print("  ❌ FIX FEHLGESCHLAGEN")
        print("="*70)
        print("\n📝 Manuelle Lösung:")
        print("   Siehe: SOFORT_FIX.md")
        print()
        sys.exit(1)
