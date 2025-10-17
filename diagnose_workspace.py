"""
WORKSPACE DIAGNOSE-TOOL
Prüft was im importierten Workspace liegt und warum Framework-Detection falsch läuft

VERWENDUNG:
    python diagnose_workspace.py
"""
import os
from pathlib import Path
import json


def find_workspace():
    """Find the imported workspace"""
    base = Path(r"C:\AI\Xionimus\backend\workspace\github_imports")
    
    if not base.exists():
        return None
    
    # Find latest user workspace
    user_dirs = [d for d in base.iterdir() if d.is_dir()]
    if not user_dirs:
        return None
    
    # Get the latest one (by modification time)
    latest_user = max(user_dirs, key=lambda x: x.stat().st_mtime)
    
    # Find Xionimus folder
    xionimus_dir = latest_user / "Xionimus"
    if xionimus_dir.exists():
        return xionimus_dir
    
    return None


def diagnose_workspace(workspace_path):
    """Diagnose what's in the workspace"""
    print("="*70)
    print("  WORKSPACE DIAGNOSE")
    print("="*70)
    print()
    print(f"📁 Workspace: {workspace_path}")
    print()
    
    # Check key files
    print("🔍 Prüfe FastAPI-Indikatoren:")
    print("-" * 70)
    
    key_files = {
        "main.py": "Haupt-Datei (FastAPI Entry Point)",
        "backend/main.py": "Backend-Haupt-Datei",
        "server.py": "Alternative Server-Datei",
        "backend/server.py": "Backend Server-Datei",
        "requirements.txt": "Python Dependencies",
        "backend/requirements.txt": "Backend Dependencies",
        "app.py": "Flask-style Entry Point",
        "backend/app.py": "Backend Flask Entry"
    }
    
    found_files = []
    missing_files = []
    
    for filename, description in key_files.items():
        filepath = workspace_path / filename
        exists = filepath.exists()
        symbol = "✅" if exists else "❌"
        print(f"{symbol} {filename:30s} - {description}")
        
        if exists:
            found_files.append(filename)
            # Show first few lines if it's a Python file
            if filename.endswith('.py'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:10]
                        print(f"   📄 First lines:")
                        for line in lines[:5]:
                            print(f"      {line.rstrip()}")
                        if len(lines) > 5:
                            print(f"      ...")
                except Exception as e:
                    print(f"   ⚠️ Couldn't read: {e}")
        else:
            missing_files.append(filename)
    
    print()
    print("🔍 Prüfe Verzeichnis-Struktur:")
    print("-" * 70)
    
    key_dirs = {
        "backend": "Backend-Verzeichnis",
        "backend/app": "FastAPI App-Verzeichnis",
        "backend/app/api": "API Endpoints",
        "backend/app/core": "Core Modules",
        "frontend": "Frontend-Verzeichnis"
    }
    
    for dirname, description in key_dirs.items():
        dirpath = workspace_path / dirname
        exists = dirpath.is_dir() if dirpath.exists() else False
        symbol = "✅" if exists else "❌"
        print(f"{symbol} {dirname:30s} - {description}")
        
        if exists:
            # Count files
            try:
                py_files = list(dirpath.rglob("*.py"))
                print(f"   📊 {len(py_files)} Python-Dateien")
            except Exception:
                pass
    
    print()
    print("🔍 Prüfe FastAPI-Imports:")
    print("-" * 70)
    
    # Search for FastAPI imports
    fastapi_found = []
    django_found = []
    flask_found = []
    
    for py_file in workspace_path.rglob("*.py"):
        # Skip venv, __pycache__, node_modules
        if any(skip in str(py_file) for skip in ['venv', '__pycache__', 'node_modules', '.venv']):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'from fastapi import' in content or 'import fastapi' in content:
                    rel_path = py_file.relative_to(workspace_path)
                    fastapi_found.append(str(rel_path))
                
                if 'from django' in content or 'import django' in content:
                    rel_path = py_file.relative_to(workspace_path)
                    django_found.append(str(rel_path))
                
                if 'from flask import' in content or 'import flask' in content:
                    rel_path = py_file.relative_to(workspace_path)
                    flask_found.append(str(rel_path))
        except Exception:
            continue
    
    print(f"FastAPI Imports: {len(fastapi_found)}")
    if fastapi_found:
        for f in fastapi_found[:5]:
            print(f"  ✅ {f}")
        if len(fastapi_found) > 5:
            print(f"  ... und {len(fastapi_found) - 5} weitere")
    
    print()
    print(f"Django Imports: {len(django_found)}")
    if django_found:
        for f in django_found[:5]:
            print(f"  ⚠️ {f}")
        if len(django_found) > 5:
            print(f"  ... und {len(django_found) - 5} weitere")
    
    print()
    print(f"Flask Imports: {len(flask_found)}")
    if flask_found:
        for f in flask_found[:5]:
            print(f"  ⚠️ {f}")
        if len(flask_found) > 5:
            print(f"  ... und {len(flask_found) - 5} weitere")
    
    print()
    print("="*70)
    print("  ANALYSE-ERGEBNIS")
    print("="*70)
    print()
    
    if not found_files:
        print("❌ PROBLEM: Keine wichtigen Dateien gefunden!")
        print()
        print("Mögliche Ursachen:")
        print("  • Import hat Dateien nicht korrekt kopiert")
        print("  • Workspace-Pfad ist falsch")
        print("  • Dateien wurden gefiltert")
    elif "main.py" in found_files or "backend/main.py" in found_files:
        print("✅ main.py gefunden - FastAPI sollte erkannt werden!")
        print()
        if len(fastapi_found) > 0:
            print(f"✅ {len(fastapi_found)} Dateien mit FastAPI-Imports")
            print()
            print("💡 EMPFEHLUNG:")
            print("  Framework-Detection sollte FastAPI erkennen.")
            print("  Falls nicht: Nutze framework_detector_v2.py")
        else:
            print("⚠️ Keine FastAPI-Imports gefunden")
            print()
            print("💡 EMPFEHLUNG:")
            print("  Prüfe ob main.py tatsächlich FastAPI nutzt")
    else:
        print("⚠️ main.py fehlt im Workspace!")
        print()
        print("💡 EMPFEHLUNG:")
        print("  • Prüfe ob der Import korrekt lief")
        print("  • Evtl. .gitignore filtert main.py?")
    
    print()
    print("🔧 Nächste Schritte:")
    if len(fastapi_found) > len(django_found):
        print("  1. Installiere framework_detector_v2.py")
        print("  2. Backend neu starten")
        print("  3. Repository neu importieren")
    else:
        print("  1. Prüfe warum Django-Imports vorhanden sind")
        print("  2. Evtl. sind Beispiel-Dateien im Repo?")
        print("  3. Framework-Detection muss robuster werden")
    
    print()


def main():
    print()
    print("🔍 Suche importierten Workspace...")
    
    workspace_path = find_workspace()
    
    if not workspace_path:
        print()
        print("❌ Konnte Workspace nicht finden!")
        print()
        print("Erwartet:")
        print("  C:\\AI\\Xionimus\\backend\\workspace\\github_imports\\...\\Xionimus")
        print()
        print("Lösung:")
        print("  1. Stelle sicher, dass Repository importiert wurde")
        print("  2. Oder gib Pfad manuell an:")
        print('     python diagnose_workspace.py "C:\\Pfad\\zum\\Workspace"')
        print()
        input("Drücke Enter zum Beenden...")
        return
    
    print(f"✅ Gefunden: {workspace_path}")
    print()
    
    diagnose_workspace(workspace_path)
    
    print()
    input("Drücke Enter zum Beenden...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        workspace_path = Path(sys.argv[1])
        if workspace_path.exists():
            diagnose_workspace(workspace_path)
        else:
            print(f"❌ Pfad existiert nicht: {workspace_path}")
    else:
        main()
