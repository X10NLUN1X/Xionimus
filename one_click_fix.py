"""
ONE-CLICK FIX für ai_manager.py
Patcht automatisch die Zeilen 494-548

VERWENDUNG:
    python one_click_fix.py
"""
import os
from pathlib import Path

def fix_ai_manager():
    print("="*70)
    print("  AI MANAGER ONE-CLICK FIX")
    print("="*70)
    print()
    
    # Pfad
    ai_manager_path = Path(r"C:\AI\Xionimus\backend\app\core\ai_manager.py")
    
    if not ai_manager_path.exists():
        print("❌ FEHLER: ai_manager.py nicht gefunden!")
        print(f"   Gesucht: {ai_manager_path}")
        return False
    
    print(f"✅ Gefunden: {ai_manager_path}")
    print()
    
    # Lese Datei
    print("📖 Lese Datei...")
    with open(ai_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = str(ai_manager_path) + ".backup"
    print(f"💾 Erstelle Backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Suche und ersetze
    print("🔍 Suche Code-Abschnitt...")
    
    # Der Code der ersetzt werden soll (Zeilen 494-548)
    old_code = '''        # CRITICAL: Inject project context into system message
        if project_context and project_context.get("project_name"):
            project_info = f"""

🎯 AKTIVES PROJEKT: {project_context['project_name']}'''
    
    # Neuer Code
    new_code = '''        # CRITICAL: Inject project context into system message
        if project_context and project_context.get("project_name"):
            # 🆕 CHECK: Use enhanced repository_context if available
            if "repository_context" in project_context:
                # Enhanced context with Framework Detection + Repository Structure
                project_info = project_context["repository_context"]
                logger.info(f"✅ Using enhanced repository context with framework detection")
                logger.info(f"   Framework: {project_context.get('framework', 'unknown')}")
                logger.info(f"   Confidence: {project_context.get('framework_confidence', 0)}%")
            else:
                # Fallback: Basic project context (old behavior)
                project_info = f"""

🎯 AKTIVES PROJEKT: {project_context['project_name']}'''
    
    if old_code in content:
        print("✅ Code-Abschnitt gefunden!")
        print("✏️  Ersetze Code...")
        
        # Ersetze nur den Anfang, der Rest bleibt gleich
        content = content.replace(old_code, new_code)
        
        # Schreibe zurück
        print("💾 Schreibe geänderte Datei...")
        with open(ai_manager_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print()
        print("="*70)
        print("  ✅ FIX ERFOLGREICH!")
        print("="*70)
        print()
        print("Was geändert wurde:")
        print("  • ai_manager.py prüft jetzt auf 'repository_context'")
        print("  • Framework-Detection wird an KI weitergeleitet")
        print("  • Repository-Struktur in System Message")
        print()
        print("🎯 Nächste Schritte:")
        print("  1. Backend NEU starten (Strg+C, dann START.bat)")
        print("  2. Repository NEU importieren (im Frontend)")
        print("  3. NEUE Chat-Session starten")
        print("  4. Testen: 'Welches Framework nutzt dieses Projekt?'")
        print()
        return True
    else:
        print("❌ FEHLER: Code-Abschnitt nicht gefunden!")
        print()
        print("Mögliche Gründe:")
        print("  • ai_manager.py wurde bereits geändert")
        print("  • Datei hat andere Struktur als erwartet")
        print()
        print("Lösung:")
        print("  • Prüfe ob Zeile 494 beginnt mit:")
        print("    '# CRITICAL: Inject project context'")
        print("  • Falls nein: Nutze manuelle Anleitung")
        print()
        return False

if __name__ == "__main__":
    try:
        success = fix_ai_manager()
        print()
        input("Drücke Enter zum Beenden...")
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        print()
        input("Drücke Enter zum Beenden...")
