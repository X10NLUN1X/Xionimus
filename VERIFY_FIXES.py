"""
Xionimus Fixes Verification Script
Testet ob die Fixes korrekt installiert wurden
"""

import sys
from pathlib import Path

def check_file_exists(filepath):
    """Check if file exists and return status"""
    if filepath.exists():
        print(f"✅ {filepath.name} gefunden")
        return True
    else:
        print(f"❌ {filepath.name} NICHT gefunden")
        return False

def check_code_fix(filepath, search_string, fix_type):
    """Check if the fix is present in the file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {fix_type} ist implementiert")
                return True
            else:
                print(f"❌ {fix_type} FEHLT")
                return False
    except Exception as e:
        print(f"❌ Fehler beim Lesen von {filepath.name}: {e}")
        return False

def main():
    print("="*60)
    print("🔍 XIONIMUS FIXES VERIFICATION")
    print("="*60)
    print()
    
    # Get project root
    project_root = Path("C:/AI/Xionimus")
    
    if not project_root.exists():
        print(f"❌ Projekt-Verzeichnis nicht gefunden: {project_root}")
        print("Bitte passe den Pfad im Script an!")
        return
    
    print(f"📂 Projekt-Root: {project_root}")
    print()
    
    # Check files exist
    print("📋 SCHRITT 1: DATEIEN PRÜFEN")
    print("-" * 60)
    
    github_pat_path = project_root / "backend" / "app" / "api" / "github_pat.py"
    chat_stream_path = project_root / "backend" / "app" / "api" / "chat_stream.py"
    
    files_ok = True
    files_ok &= check_file_exists(github_pat_path)
    files_ok &= check_file_exists(chat_stream_path)
    
    if not files_ok:
        print("\n❌ DATEIEN FEHLEN - Bitte Fixes installieren!")
        return
    
    print()
    
    # Check Fix #1: github_pat.py
    print("📋 SCHRITT 2: FIX #1 PRÜFEN (github_pat.py)")
    print("-" * 60)
    
    fix1_checks = [
        ("session.active_project = repo.name", "active_project als String"),
        ("session.active_project_branch = branch_name", "active_project_branch gesetzt"),
        ("# FIXED: active_project should be a string", "Fix-Kommentar vorhanden")
    ]
    
    fix1_ok = True
    for search_str, desc in fix1_checks:
        fix1_ok &= check_code_fix(github_pat_path, search_str, desc)
    
    # Check that OLD code is NOT present
    if "session.active_project = {" in open(github_pat_path, 'r', encoding='utf-8').read():
        print("❌ WARNUNG: Alter Code (Dictionary) noch vorhanden!")
        fix1_ok = False
    else:
        print("✅ Alter Code (Dictionary) nicht mehr vorhanden")
    
    print()
    
    # Check Fix #2: chat_stream.py
    print("📋 SCHRITT 3: FIX #2 PRÜFEN (chat_stream.py)")
    print("-" * 60)
    
    fix2_checks = [
        ("async def handle_command(", "/activate Command Handler"),
        ('if command == "/activate":', "/activate Command implementiert"),
        ('elif command == "/help":', "/help Command implementiert"),
        ("if user_message.strip().startswith", "Command-Check in Main-Loop")
    ]
    
    fix2_ok = True
    for search_str, desc in fix2_checks:
        fix2_ok &= check_code_fix(chat_stream_path, search_str, desc)
    
    print()
    
    # Check backups exist
    print("📋 SCHRITT 4: BACKUPS PRÜFEN")
    print("-" * 60)
    
    backup_exists = False
    backup_suffixes = [".backup", ".backup_vor_fix", ".bak"]
    
    for suffix in backup_suffixes:
        backup_path = github_pat_path.parent / f"github_pat.py{suffix}"
        if backup_path.exists():
            print(f"✅ Backup gefunden: {backup_path.name}")
            backup_exists = True
            break
    
    if not backup_exists:
        print("⚠️ WARNUNG: Kein Backup gefunden!")
        print("   Empfehlung: Erstelle Backup vor nächstem Update!")
    
    print()
    
    # Check __pycache__ (should be deleted)
    print("📋 SCHRITT 5: CACHE PRÜFEN")
    print("-" * 60)
    
    pycache_path = project_root / "backend" / "app" / "api" / "__pycache__"
    
    if pycache_path.exists():
        print("⚠️ __pycache__ existiert noch")
        print(f"   Empfehlung: Lösche: {pycache_path}")
    else:
        print("✅ __pycache__ wurde gelöscht (gut!)")
    
    print()
    print("="*60)
    
    # Final verdict
    if fix1_ok and fix2_ok:
        print("🎉 ALLE FIXES ERFOLGREICH INSTALLIERT!")
        print()
        print("📋 NÄCHSTE SCHRITTE:")
        print("1. Backend neu starten (START.bat)")
        print("2. Im Chat testen: /help")
        print("3. Im Chat testen: /activate Xionimus")
        print("4. Repository-Struktur analysieren lassen")
    else:
        print("❌ EINIGE FIXES FEHLEN ODER SIND INKORREKT")
        print()
        print("📋 AKTION ERFORDERLICH:")
        print("1. Überprüfe die Dateien github_pat.py und chat_stream.py")
        print("2. Stelle sicher, dass die neuen Dateien korrekt kopiert wurden")
        print("3. Lösche __pycache__ und starte Backend neu")
    
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nDrücke Enter zum Beenden...")
