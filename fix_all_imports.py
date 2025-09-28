#!/usr/bin/env python3
"""
XIONIMUS AI - Systematische Import-Reparatur
Behebt alle identifizierten Import-Probleme automatisch
"""

import os
import re
from pathlib import Path

def fix_standard_library_imports():
    """Behebt Standard-Library Import-Probleme"""
    fixes = [
        # server.py fixes
        {
            'file': '/app/backend/server.py',
            'old': 'from dotenv import load_dotenv',
            'new': 'from python_dotenv import load_dotenv'
        }
    ]
    
    for fix in fixes:
        try:
            with open(fix['file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            if fix['old'] in content:
                content = content.replace(fix['old'], fix['new'])
                with open(fix['file'], 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed: {fix['file']}")
        except Exception as e:
            print(f"❌ Error fixing {fix['file']}: {e}")

def fix_relative_imports():
    """Behebt relative Import-Probleme in Agents"""
    agent_files = [
        'experimental_agent.py', 'qa_agent.py', 'writing_agent.py', 
        'code_agent.py', 'file_agent.py', 'github_agent.py', 
        'research_agent.py', 'session_agent.py', 'data_agent.py'
    ]
    
    for agent_file in agent_files:
        file_path = f'/app/backend/agents/{agent_file}'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix base_agent import
            content = re.sub(
                r'from base_agent import',
                'from .base_agent import',
                content
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed relative imports: {agent_file}")
            
        except Exception as e:
            print(f"❌ Error fixing {agent_file}: {e}")

def fix_agent_manager_imports():
    """Behebt agent_manager.py Import-Probleme"""
    file_path = '/app/backend/agents/agent_manager.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix all relative imports
        replacements = [
            ('from base_agent import', 'from .base_agent import'),
            ('from code_agent import', 'from .code_agent import'),
            ('from research_agent import', 'from .research_agent import'),
            ('from writing_agent import', 'from .writing_agent import'),
            ('from data_agent import', 'from .data_agent import'),
            ('from qa_agent import', 'from .qa_agent import'),
            ('from github_agent import', 'from .github_agent import'),
            ('from file_agent import', 'from .file_agent import'),
            ('from session_agent import', 'from .session_agent import'),
            ('from experimental_agent import', 'from .experimental_agent import'),
            ('from language_detector import', 'from .language_detector import'),
            ('from context_analyzer import', 'from .context_analyzer import')
        ]
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed agent_manager.py imports")
        
    except Exception as e:
        print(f"❌ Error fixing agent_manager.py: {e}")

def remove_missing_service_imports():
    """Entfernt Imports für gelöschte Services"""
    file_path = '/app/backend/server.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Entferne problematische Import-Zeilen
        new_lines = []
        for line in lines:
            if any(service in line for service in [
                'xionimus_orchestrator', 'search_service', 
                'auto_testing_service', 'code_review_ai'
            ]):
                new_lines.append(f"# REMOVED: {line}")
                print(f"Removed: {line.strip()}")
            else:
                new_lines.append(line)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("✅ Removed missing service imports")
        
    except Exception as e:
        print(f"❌ Error removing service imports: {e}")

def main():
    """Hauptreparatur-Funktion"""
    print("🔧 STARTE SYSTEMATISCHE IMPORT-REPARATUR")
    print("=" * 50)
    
    print("\n1. Standard Library Imports...")
    fix_standard_library_imports()
    
    print("\n2. Relative Agent Imports...")
    fix_relative_imports()
    
    print("\n3. Agent Manager Imports...")
    fix_agent_manager_imports()
    
    print("\n4. Entferne fehlende Services...")
    remove_missing_service_imports()
    
    print("\n✅ IMPORT-REPARATUR ABGESCHLOSSEN!")

if __name__ == "__main__":
    main()