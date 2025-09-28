#!/usr/bin/env python3
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

print(f"\n📊 RESULTS: {passed} passed, {failed} failed")

if failed == 0:
    print("🎉 ALL IMPORTS SUCCESSFUL!")
else:
    print("⚠️ Some imports still failing")
