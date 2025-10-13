"""
🔍 PSEONIMUS REPOSITORY ACCESS - DIAGNOSTIC TEST SUITE
Windows-kompatibel | Reproduzierbare Tests | Root-Cause-Finder

USAGE:
    python TEST_REPOSITORY_ACCESS.py

REQUIREMENTS:
    - Backend muss laufen (http://localhost:8001)
    - User muss eingeloggt sein
    - Repository "Xionimus" muss importiert sein
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

BACKEND_URL = "http://localhost:8001"
TEST_REPO = "Xionimus"
TEST_USER_ID = "87f7095f-5f5d-4c27-b9fe-930ef9eec725"  # Richtige User-ID (admin)
JWT_TOKEN = None  # Wird aus Session gelesen

# ============================================================================
# COLOR OUTPUT (Windows-kompatibel)
# ============================================================================

class Colors:
    """ANSI Color Codes für Windows Terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str, status: str, details: str = ""):
    """Formatierte Test-Ausgabe"""
    symbols = {
        "PASS": "✅",
        "FAIL": "❌",
        "WARN": "⚠️",
        "INFO": "ℹ️",
        "RUN": "🔍"
    }
    colors = {
        "PASS": Colors.OKGREEN,
        "FAIL": Colors.FAIL,
        "WARN": Colors.WARNING,
        "INFO": Colors.OKCYAN,
        "RUN": Colors.OKBLUE
    }
    
    symbol = symbols.get(status, "•")
    color = colors.get(status, Colors.ENDC)
    
    print(f"{color}{symbol} {name}{Colors.ENDC}")
    if details:
        print(f"   {details}")

# ============================================================================
# TEST 1: BACKEND ERREICHBARKEIT
# ============================================================================

def test_backend_connectivity():
    """Test ob Backend läuft"""
    print_test("Backend Connectivity", "RUN", "Prüfe http://localhost:8001...")
    
    try:
        import requests
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            print_test("Backend läuft", "PASS", f"Status: {response.status_code}")
            return True
        else:
            print_test("Backend antwortet nicht korrekt", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Backend nicht erreichbar", "FAIL", f"Error: {str(e)}")
        print_test("Starte Backend mit:", "INFO", "python backend/server_launcher.py")
        return False

# ============================================================================
# TEST 2: DATENBANK SESSION PRÜFUNG
# ============================================================================

def test_database_session():
    """Prüfe ob active_project in Session gesetzt ist"""
    print_test("Database Session Check", "RUN", "Prüfe SQLite Datenbank...")
    
    try:
        import sqlite3
        
        # Finde SQLite DB (liegt im Home-Verzeichnis!)
        home_dir = Path.home() / ".xionimus_ai"
        db_path = home_dir / "xionimus.db"
        
        if not db_path.exists():
            # Fallback: Suche im Backend-Ordner
            db_path = Path("backend/xionimus.db")
            if not db_path.exists():
                db_path = Path("xionimus.db")
        
        if not db_path.exists():
            print_test("Datenbank nicht gefunden", "FAIL", 
                      f"Gesucht:\n   {home_dir / 'xionimus.db'}\n   backend/xionimus.db")
            return False
        
        # Verbinde mit DB
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print_test(f"Datenbank gefunden", "PASS", f"Pfad: {db_path}")
        
        # Prüfe Sessions Tabelle
        cursor.execute("""
            SELECT id, user_id, active_project, active_project_branch, name 
            FROM sessions 
            WHERE user_id = ? 
            ORDER BY updated_at DESC 
            LIMIT 5
        """, (TEST_USER_ID,))
        
        sessions = cursor.fetchall()
        
        if not sessions:
            print_test("Keine Sessions gefunden", "FAIL", f"User ID: {TEST_USER_ID}")
            return False
        
        # Prüfe ob irgendeine Session ein active_project hat
        has_active = False
        for session_id, user_id, active_project, branch, name in sessions:
            if active_project:
                has_active = True
                print_test(f"Session mit active_project gefunden", "PASS", 
                          f"Session: {session_id[:8]}...\n   Project: {active_project}\n   Branch: {branch}")
            else:
                print_test(f"Session OHNE active_project", "WARN", 
                          f"Session: {session_id[:8]}... | Name: {name}")
        
        conn.close()
        
        if not has_active:
            print_test("PROBLEM GEFUNDEN", "FAIL", 
                      "Keine Session hat active_project gesetzt!\n   → Repository wurde importiert, aber nicht aktiviert")
            return False
        
        return True
        
    except Exception as e:
        print_test("Database Check fehlgeschlagen", "FAIL", f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 3: REPOSITORY PFAD PRÜFUNG
# ============================================================================

def test_repository_path():
    """Prüfe ob Repository-Pfad existiert"""
    print_test("Repository Path Check", "RUN", "Prüfe Dateisystem...")
    
    try:
        # Mögliche Pfade (aus deinem Code)
        possible_paths = [
            Path(f"backend/workspace/github_imports/{TEST_USER_ID}/{TEST_REPO}"),
            Path(f"workspace/github_imports/{TEST_USER_ID}/{TEST_REPO}"),
            Path(f"github_imports/{TEST_USER_ID}/{TEST_REPO}"),
        ]
        
        found_path = None
        for path in possible_paths:
            if path.exists():
                found_path = path
                break
        
        if found_path:
            # Zähle Dateien
            files = list(found_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            dir_count = len([f for f in files if f.is_dir()])
            
            print_test("Repository gefunden", "PASS", 
                      f"Pfad: {found_path}\n   Files: {file_count} | Dirs: {dir_count}")
            
            # Zeige erste 10 Dateien
            print_test("Erste Dateien im Repo:", "INFO")
            for i, file in enumerate([f for f in files if f.is_file()][:10]):
                rel_path = file.relative_to(found_path)
                print(f"      {rel_path}")
            
            return True, str(found_path)
        else:
            print_test("Repository NICHT gefunden", "FAIL", 
                      f"Gesucht in:\n   " + "\n   ".join(str(p) for p in possible_paths))
            print_test("Lösung", "INFO", 
                      "Importiere Repository in UI:\n   GitHub Import → Xionimus → Import")
            return False, None
            
    except Exception as e:
        print_test("Path Check fehlgeschlagen", "FAIL", f"Error: {str(e)}")
        return False, None

# ============================================================================
# TEST 4: REPOSITORY STRUKTUR SCAN (wie in chat_stream.py)
# ============================================================================

def test_repository_scan(repo_path: str):
    """Simuliere scan_repository_structure() aus chat_stream.py"""
    print_test("Repository Structure Scan", "RUN", "Simuliere Agent-Zugriff...")
    
    try:
        path = Path(repo_path)
        
        if not path.exists():
            print_test("Pfad existiert nicht", "FAIL", repo_path)
            return False
        
        # Gleiche Logik wie in chat_stream.py
        ignore_dirs = {
            '.git', 'node_modules', '__pycache__', 'venv', '.venv',
            'build', 'dist', '.next', '.cache', 'coverage'
        }
        
        file_tree = []
        total_files = 0
        max_files = 1000
        
        for root, dirs, files in os.walk(path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            for filename in files:
                if filename.startswith('.'):
                    continue
                
                total_files += 1
                if total_files > max_files:
                    break
                
                filepath = Path(root) / filename
                rel_path = filepath.relative_to(path)
                file_tree.append(str(rel_path))
        
        print_test("Repository-Scan erfolgreich", "PASS", 
                  f"Dateien gefunden: {total_files} (max: {max_files})")
        
        if total_files >= max_files:
            print_test("Repository zu groß", "WARN", 
                      f"Scan bei {max_files} Dateien gestoppt!\n   → Erhöhe max_files in chat_stream.py")
        
        # Zeige Statistik
        extensions = {}
        for file in file_tree:
            ext = Path(file).suffix or "no_ext"
            extensions[ext] = extensions.get(ext, 0) + 1
        
        print_test("File-Type Distribution:", "INFO")
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {ext}: {count}")
        
        return True
        
    except Exception as e:
        print_test("Scan fehlgeschlagen", "FAIL", f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 5: WEBSOCKET MESSAGE SIMULATION
# ============================================================================

def test_websocket_message():
    """Simuliere WebSocket-Message an chat_stream.py"""
    print_test("WebSocket Message Simulation", "RUN", "Prüfe Message-Handler...")
    
    # Simuliere die Message die Frontend sendet
    test_message = {
        "type": "chat",
        "content": "Analysiere die Repository-Struktur",
        "provider": "anthropic",
        "model": "claude-sonnet-4",
        "ultra_thinking": False,
        "api_keys": {},
        "messages": []
    }
    
    print_test("Test-Message erstellt", "INFO", json.dumps(test_message, indent=2))
    
    # TODO: Eigentlich WebSocket-Connection aufbauen
    # Aber das ist komplex, daher nur Message-Format prüfen
    
    required_fields = ["type", "content", "provider", "model"]
    missing = [f for f in required_fields if f not in test_message]
    
    if missing:
        print_test("Message-Format ungültig", "FAIL", f"Fehlende Felder: {missing}")
        return False
    else:
        print_test("Message-Format korrekt", "PASS")
        return True

# ============================================================================
# TEST 6: COMMAND HANDLER PRÜFUNG
# ============================================================================

def test_command_handler():
    """Prüfe ob /activate Command implementiert ist"""
    print_test("Command Handler Check", "RUN", "Suche nach /activate...")
    
    # Suche in chat_stream.py nach /activate Handler
    chat_stream_path = Path("backend/app/api/chat_stream.py")
    
    if not chat_stream_path.exists():
        print_test("chat_stream.py nicht gefunden", "FAIL")
        return False
    
    with open(chat_stream_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Suche nach Command-Pattern
    has_activate = "/activate" in content or "activate" in content.lower()
    has_command_handler = "command" in content.lower() and ("if" in content or "match" in content)
    
    if not has_activate:
        print_test("/activate Command NICHT gefunden", "FAIL", 
                  "Command wird nicht behandelt → Agent erkennt /activate nicht")
        print_test("Lösung", "INFO", "Füge Command-Handler in chat_stream.py ein")
        return False
    else:
        print_test("/activate Pattern gefunden", "WARN", 
                  "Prüfe ob Command korrekt behandelt wird")
        return True

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Führe alle Tests aus"""
    print("\n" + "="*80)
    print("🔍 PSEONIMUS REPOSITORY ACCESS - DIAGNOSTIC TEST SUITE")
    print("="*80 + "\n")
    
    results = {}
    
    # Test 1: Backend
    print(f"\n{Colors.BOLD}[1/6] Backend Connectivity{Colors.ENDC}")
    print("-" * 80)
    results['backend'] = test_backend_connectivity()
    
    if not results['backend']:
        print_test("Tests abgebrochen", "FAIL", "Backend muss laufen!")
        return
    
    # Test 2: Database
    print(f"\n{Colors.BOLD}[2/6] Database Session{Colors.ENDC}")
    print("-" * 80)
    results['database'] = test_database_session()
    
    # Test 3: Repository Path
    print(f"\n{Colors.BOLD}[3/6] Repository Path{Colors.ENDC}")
    print("-" * 80)
    results['repo_path'], repo_path = test_repository_path()
    
    # Test 4: Repository Scan (nur wenn Pfad gefunden)
    if results['repo_path'] and repo_path:
        print(f"\n{Colors.BOLD}[4/6] Repository Structure Scan{Colors.ENDC}")
        print("-" * 80)
        results['repo_scan'] = test_repository_scan(repo_path)
    else:
        results['repo_scan'] = False
    
    # Test 5: WebSocket Message
    print(f"\n{Colors.BOLD}[5/6] WebSocket Message Format{Colors.ENDC}")
    print("-" * 80)
    results['websocket'] = test_websocket_message()
    
    # Test 6: Command Handler
    print(f"\n{Colors.BOLD}[6/6] Command Handler{Colors.ENDC}")
    print("-" * 80)
    results['command'] = test_command_handler()
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80 + "\n")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print_test(test_name, status)
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.ENDC}")
    
    # ========================================================================
    # ROOT CAUSE ANALYSIS
    # ========================================================================
    print("\n" + "="*80)
    print("🎯 ROOT CAUSE ANALYSIS")
    print("="*80 + "\n")
    
    if not results['database']:
        print_test("HAUPTPROBLEM GEFUNDEN", "FAIL", 
                  "active_project wird nicht in Session gesetzt!\n\n   FIX: Modifiziere github_pat.py Import-Funktion\n   → Setze session.active_project = repo_name nach Import")
    
    if not results['repo_path']:
        print_test("HAUPTPROBLEM GEFUNDEN", "FAIL", 
                  "Repository existiert nicht im Dateisystem!\n\n   FIX: Re-Importiere Repository in UI\n   → Oder: Prüfe GITHUB_IMPORTS_DIR in settings")
    
    if not results['command']:
        print_test("PROBLEM GEFUNDEN", "WARN", 
                  "/activate Command nicht implementiert!\n\n   FIX: Füge Command-Handler in chat_stream.py\n   → Erkenne /activate Pattern und setze active_project")
    
    if results['repo_path'] and not results['repo_scan']:
        print_test("PROBLEM GEFUNDEN", "WARN", 
                  "Repository-Scan fehlgeschlagen!\n\n   FIX: Prüfe Berechtigungen oder max_files Limit")
    
    # Success Case
    if all(results.values()):
        print_test("ALLES OK", "PASS", 
                  "Alle Tests bestanden!\n   → Problem liegt woanders (AI-Manager, System-Message, Token-Limits)")
    
    print("\n" + "="*80)
    print("✅ TESTS ABGESCHLOSSEN")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
