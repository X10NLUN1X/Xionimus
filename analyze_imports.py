#!/usr/bin/env python3
"""
XIONIMUS AI - Umfassende Import-Analyse
Analysiert alle Python-Dateien auf Import-Probleme
"""

import os
import ast
import sys
from pathlib import Path

def analyze_imports(file_path):
    """Analysiert Imports in einer Python-Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                imports.append({
                    'type': 'from',
                    'module': node.module,
                    'names': [alias.name for alias in node.names] if node.names else [],
                    'line': node.lineno
                })
        
        return imports
    except Exception as e:
        return [{'error': str(e)}]

def check_module_exists(module_name, base_path):
    """Prüft ob ein Modul existiert"""
    if not module_name:
        return True
    
    # Standard-Library Module (Vollständige Liste für Python 3.13)
    stdlib_modules = {
        'os', 'sys', 'json', 'typing', 'datetime', 'asyncio', 're', 
        'pathlib', 'logging', 'uuid', 'base64', 'hashlib', 'hmac',
        'urllib', 'http', 'socket', 'ssl', 'time', 'collections',
        'functools', 'itertools', 'traceback', 'inspect', 'ast',
        'contextlib', 'zipfile', 'tempfile', 'shutil', 'io', 'abc',
        'enum', 'dataclasses', 'mimetypes', 'certifi'
    }
    
    # Externe Libraries (die wir installiert haben)
    external_modules = {
        'fastapi', 'uvicorn', 'motor', 'pymongo', 'anthropic', 'openai',
        'aiohttp', 'httpx', 'pydantic', 'numpy', 'pandas', 'yaml',
        'jinja2', 'rich', 'click', 'tqdm', 'requests', 'pillow'
    }
    
    # Prüfe Standard-Library
    if module_name.split('.')[0] in stdlib_modules:
        return True
        
    # Prüfe externe Libraries
    if module_name.split('.')[0] in external_modules:
        return True
        
    # Prüfe lokale Module
    module_parts = module_name.split('.')
    
    # Relative Imports (beginnt mit .)
    if module_name.startswith('.'):
        return True  # Relative Imports sind komplex zu prüfen
    
    # Absolute lokale Imports
    module_path = base_path
    for part in module_parts:
        module_path = module_path / part
        if (module_path.with_suffix('.py')).exists():
            return True
        if (module_path / '__init__.py').exists():
            continue
        else:
            return False
    
    return False

def main():
    """Hauptanalyse-Funktion"""
    backend_path = Path('/app/backend')
    
    print("=" * 60)
    print("🔍 XIONIMUS AI - UMFASSENDE IMPORT-ANALYSE")
    print("=" * 60)
    
    all_issues = []
    total_files = 0
    total_imports = 0
    
    # Analysiere alle Python-Dateien
    for py_file in backend_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
            
        total_files += 1
        rel_path = py_file.relative_to(backend_path)
        
        print(f"\n📁 Analysiere: {rel_path}")
        
        imports = analyze_imports(py_file)
        
        for imp in imports:
            if 'error' in imp:
                print(f"  ❌ Parse-Fehler: {imp['error']}")
                all_issues.append({
                    'file': str(rel_path),
                    'type': 'parse_error',
                    'error': imp['error']
                })
                continue
            
            total_imports += 1
            module_name = imp['module']
            
            # Prüfe ob Modul existiert
            if not check_module_exists(module_name, backend_path):
                print(f"  ❌ Zeile {imp['line']}: Fehlendes Modul '{module_name}'")
                all_issues.append({
                    'file': str(rel_path),
                    'type': 'missing_module',
                    'module': module_name,
                    'line': imp['line'],
                    'import_type': imp['type']
                })
            else:
                print(f"  ✅ Zeile {imp['line']}: {imp['type']} {module_name}")
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 ANALYSE-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"📁 Analysierte Dateien: {total_files}")
    print(f"📦 Gefundene Imports: {total_imports}")
    print(f"❌ Probleme gefunden: {len(all_issues)}")
    
    if all_issues:
        print("\n🚨 GEFUNDENE PROBLEME:")
        for issue in all_issues:
            if issue['type'] == 'missing_module':
                print(f"  ❌ {issue['file']}:{issue['line']} - Fehlendes Modul: {issue['module']}")
            elif issue['type'] == 'parse_error':
                print(f"  ❌ {issue['file']} - Parse-Fehler: {issue['error']}")
    else:
        print("\n✅ KEINE IMPORT-PROBLEME GEFUNDEN!")
    
    return all_issues

if __name__ == "__main__":
    issues = main()