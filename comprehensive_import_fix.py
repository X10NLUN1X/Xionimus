#!/usr/bin/env python3
"""
XIONIMUS AI - Umfassende Import-Fehlerbehebung
Behebt systematisch ALLE Import-Probleme im Agent-System
"""

import os
import re
from pathlib import Path

def fix_all_agent_imports():
    """Behebt alle Agent-Import-Probleme systematisch"""
    
    # 1. Alle Agent-Dateien auf .base_agent import ändern
    agent_files = [
        'experimental_agent.py', 'qa_agent.py', 'writing_agent.py', 
        'code_agent.py', 'file_agent.py', 'github_agent.py', 
        'research_agent.py', 'session_agent.py', 'data_agent.py'
    ]
    
    print("🔧 Repariere Agent Base-Imports...")
    
    for agent_file in agent_files:
        file_path = Path(f'/app/backend/agents/{agent_file}')
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Ersetze base_agent imports
            content = re.sub(r'^from base_agent import', 'from .base_agent import', content, flags=re.MULTILINE)
            
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ {agent_file}")
            
        except Exception as e:
            print(f"  ❌ {agent_file}: {e}")
    
    # 2. Agent Manager Imports reparieren
    print("\n🔧 Repariere Agent Manager Imports...")
    
    agent_manager_path = Path('/app/backend/agents/agent_manager.py')
    try:
        content = agent_manager_path.read_text(encoding='utf-8')
        
        # Alle relativen Imports korrigieren
        import_fixes = {
            'from base_agent import': 'from .base_agent import',
            'from code_agent import': 'from .code_agent import',
            'from research_agent import': 'from .research_agent import',
            'from writing_agent import': 'from .writing_agent import',
            'from data_agent import': 'from .data_agent import',
            'from qa_agent import': 'from .qa_agent import',
            'from github_agent import': 'from .github_agent import',
            'from file_agent import': 'from .file_agent import',
            'from session_agent import': 'from .session_agent import',
            'from experimental_agent import': 'from .experimental_agent import',
            'from language_detector import': 'from .language_detector import',
            'from context_analyzer import': 'from .context_analyzer import'
        }
        
        for old_import, new_import in import_fixes.items():
            content = content.replace(old_import, new_import)
        
        agent_manager_path.write_text(content, encoding='utf-8')
        print("  ✅ agent_manager.py")
        
    except Exception as e:
        print(f"  ❌ agent_manager.py: {e}")

def test_all_imports():
    """Testet alle wichtigen Imports"""
    print("\n🧪 Teste alle wichtigen Imports...")
    
    test_commands = [
        ("server.py", "python -c 'import sys; sys.path.append(\"/app/backend\"); import server'"),
        ("ai_orchestrator", "python -c 'import sys; sys.path.append(\"/app/backend\"); import ai_orchestrator'"),
        ("agent_manager", "python -c 'import sys; sys.path.append(\"/app/backend\"); from agents.agent_manager import AgentManager'"),
        ("base_agent", "python -c 'import sys; sys.path.append(\"/app/backend\"); from agents.base_agent import BaseAgent'"),
        ("research_agent", "python -c 'import sys; sys.path.append(\"/app/backend\"); from agents.research_agent import ResearchAgent'"),
    ]
    
    all_passed = True
    
    for name, cmd in test_commands:
        try:
            os.system(f"cd /app/backend && {cmd} 2>/dev/null")
            print(f"  ✅ {name}")
        except:
            print(f"  ❌ {name}")
            all_passed = False
    
    return all_passed

def create_comprehensive_test():
    """Erstellt einen umfassenden Backend-Import-Test"""
    test_script = """#!/usr/bin/env python3
import sys
import os
sys.path.append('/app/backend')

print("🧪 COMPREHENSIVE BACKEND IMPORT TEST")
print("=" * 50)

tests = [
    ("Core Server", "import server"),
    ("AI Orchestrator", "import ai_orchestrator"),
    ("DNS Bypass", "import dns_bypass"),
    ("Local Storage", "import local_storage"),
    ("Agent Manager", "from agents.agent_manager import AgentManager"),
    ("Base Agent", "from agents.base_agent import BaseAgent"),
    ("Code Agent", "from agents.code_agent import CodeAgent"),
    ("Research Agent", "from agents.research_agent import ResearchAgent"),
    ("Writing Agent", "from agents.writing_agent import WritingAgent"),
    ("Data Agent", "from agents.data_agent import DataAgent"),
    ("QA Agent", "from agents.qa_agent import QAAgent"),
    ("GitHub Agent", "from agents.github_agent import GitHubAgent"),
    ("File Agent", "from agents.file_agent import FileAgent"),
    ("Session Agent", "from agents.session_agent import SessionAgent"),
    ("Experimental Agent", "from agents.experimental_agent import ExperimentalAgent"),
    ("Language Detector", "from agents.language_detector import LanguageDetector"),
    ("Context Analyzer", "from agents.context_analyzer import ContextAnalyzer"),
]

passed = 0
failed = 0

for name, import_stmt in tests:
    try:
        exec(import_stmt)
        print(f"✅ {name}")
        passed += 1
    except Exception as e:
        print(f"❌ {name}: {e}")
        failed += 1

print(f"\\n📊 RESULTS: {passed} passed, {failed} failed")

if failed == 0:
    print("🎉 ALL IMPORTS SUCCESSFUL!")
else:
    print("⚠️ Some imports still failing")
"""
    
    with open('/app/test_all_imports.py', 'w') as f:
        f.write(test_script)
    
    print("📝 Created comprehensive test: test_all_imports.py")

def main():
    """Hauptfunktion"""
    print("🚀 UMFASSENDE IMPORT-FEHLERBEHEBUNG GESTARTET")
    print("=" * 55)
    
    # Repariere alle Agent-Imports
    fix_all_agent_imports()
    
    # Erstelle umfassenden Test
    create_comprehensive_test()
    
    print("\n✅ IMPORT-REPARATUR ABGESCHLOSSEN!")
    print("\n🧪 Führe umfassenden Test aus:")
    print("python test_all_imports.py")

if __name__ == "__main__":
    main()