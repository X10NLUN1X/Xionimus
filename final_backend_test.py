#!/usr/bin/env python3
"""
XIONIMUS AI - Finaler Backend-Test
Umfassender Test aller Backend-Komponenten nach der Reparatur
"""

import sys
import os
import ast
from pathlib import Path

def test_syntax(file_path):
    """Testet Python-Syntax einer Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, str(file_path), 'exec')
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax-Fehler Zeile {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Fehler: {e}"

def test_imports():
    """Testet alle kritischen Backend-Imports"""
    sys.path.append('/app/backend')
    
    import_tests = [
        ("server.py", "import server"),
        ("ai_orchestrator", "import ai_orchestrator"),
        ("dns_bypass", "import dns_bypass"),
        ("local_storage", "import local_storage"),
        ("agent_manager", "from agents.agent_manager import AgentManager"),
        ("all_agents", "from agents import *"),
    ]
    
    results = {}
    
    for name, import_stmt in import_tests:
        try:
            exec(import_stmt)
            results[name] = {"status": "✅", "error": None}
        except Exception as e:
            results[name] = {"status": "❌", "error": str(e)}
    
    return results

def test_agent_system():
    """Testet das Agent-System"""
    sys.path.append('/app/backend')
    
    try:
        from agents.agent_manager import AgentManager
        
        # Teste AgentManager Erstellung
        agent_manager = AgentManager()
        
        # Teste verfügbare Agents
        agents = agent_manager.get_available_agents()
        
        return {
            "agent_manager_creation": "✅",
            "available_agents": len(agents),
            "agent_list": list(agents.keys()) if isinstance(agents, dict) else agents
        }
        
    except Exception as e:
        return {
            "agent_manager_creation": "❌",
            "error": str(e)
        }

def main():
    """Haupttest-Funktion"""
    print("🧪 FINALER XIONIMUS AI BACKEND-TEST")
    print("=" * 50)
    
    # 1. Syntax-Tests
    print("\n1️⃣ SYNTAX-TESTS")
    print("-" * 20)
    
    python_files = list(Path('/app/backend').rglob('*.py'))
    syntax_results = {}
    
    for py_file in python_files:
        if '__pycache__' in str(py_file):
            continue
            
        success, message = test_syntax(py_file)
        rel_path = py_file.relative_to(Path('/app/backend'))
        syntax_results[str(rel_path)] = {"success": success, "message": message}
        
        status = "✅" if success else "❌"
        print(f"  {status} {rel_path}: {message}")
    
    # 2. Import-Tests
    print("\n2️⃣ IMPORT-TESTS")
    print("-" * 20)
    
    import_results = test_imports()
    
    for name, result in import_results.items():
        error_msg = f" ({result['error']})" if result['error'] else ""
        print(f"  {result['status']} {name}{error_msg}")
    
    # 3. Agent-System Test
    print("\n3️⃣ AGENT-SYSTEM TEST")
    print("-" * 20)
    
    agent_results = test_agent_system()
    
    if "error" in agent_results:
        print(f"  ❌ Agent System: {agent_results['error']}")
    else:
        print(f"  ✅ Agent Manager: {agent_results['agent_manager_creation']}")
        print(f"  📊 Verfügbare Agents: {agent_results['available_agents']}")
        if agent_results.get('agent_list'):
            for agent in agent_results['agent_list']:
                print(f"    • {agent}")
    
    # 4. Zusammenfassung
    print("\n4️⃣ ZUSAMMENFASSUNG")
    print("-" * 20)
    
    syntax_passed = sum(1 for r in syntax_results.values() if r['success'])
    syntax_total = len(syntax_results)
    
    import_passed = sum(1 for r in import_results.values() if r['status'] == '✅')
    import_total = len(import_results)
    
    agent_success = "error" not in agent_results
    
    print(f"  📁 Syntax-Tests: {syntax_passed}/{syntax_total} bestanden")
    print(f"  📦 Import-Tests: {import_passed}/{import_total} bestanden")
    print(f"  🤖 Agent-System: {'✅ OK' if agent_success else '❌ Fehler'}")
    
    overall_success = (syntax_passed == syntax_total and 
                      import_passed == import_total and 
                      agent_success)
    
    if overall_success:
        print(f"\n🎉 ALLE TESTS BESTANDEN! Backend ist bereit.")
        print("🚀 Backend kann jetzt gestartet werden:")
        print("   cd /app/backend && python server.py")
    else:
        print(f"\n⚠️ Einige Tests fehlgeschlagen. Weitere Reparaturen nötig.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)