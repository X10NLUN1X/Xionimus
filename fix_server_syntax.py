#!/usr/bin/env python3
"""
XIONIMUS AI - Server Syntax-Reparatur
Behebt alle Syntax-Fehler in server.py durch fehlerhaft kommentierte Zeilen
"""

import re
from pathlib import Path

def fix_server_syntax():
    """Behebt alle Syntax-Fehler in server.py"""
    server_path = Path('/app/backend/server.py')
    
    try:
        content = server_path.read_text(encoding='utf-8')
        
        # Finde und repariere alle problematischen Kommentare
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Suche nach problematischen Kommentar-Patterns
            if '# REMOVED:' in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                
                # Wenn die nächste Zeile eingerückt ist und kein Kommentar, dann kommentiere sie aus
                if next_line.strip() and not next_line.strip().startswith('#') and len(next_line) - len(next_line.lstrip()) > len(line) - len(line.lstrip()):
                    # Kommentiere die eingerückten Folgezeilen aus
                    fixed_lines.append(line)
                    i += 1
                    
                    # Kommentiere alle eingerückten Folgezeilen aus
                    while i < len(lines):
                        follow_line = lines[i]
                        if follow_line.strip() and not follow_line.strip().startswith('#'):
                            # Prüfe ob die Zeile zur vorherigen gehört (Einrückung)
                            if len(follow_line) - len(follow_line.lstrip()) > len(line) - len(line.lstrip()):
                                fixed_lines.append(f"                    # {follow_line.strip()}")
                                i += 1
                            else:
                                break
                        else:
                            fixed_lines.append(follow_line)
                            i += 1
                            break
                else:
                    fixed_lines.append(line)
                    i += 1
            else:
                fixed_lines.append(line)
                i += 1
        
        # Spezifische problematische Patterns reparieren
        content = '\n'.join(fixed_lines)
        
        # Repariere bekannte problematische Bereiche
        problematic_patterns = [
            # Pattern 1: Mehrzeilige Funktionsaufrufe nach REMOVED-Kommentar
            (r'# REMOVED:.*?\n\s+([^#\n]+(?:\n\s+[^#\n]+)*)', lambda m: f"# REMOVED: {m.group(0).split('# REMOVED:')[1].strip()}\n                    # {m.group(1).replace(chr(10), chr(10) + '                    # ')}"),
        ]
        
        for pattern, replacement in problematic_patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Schreibe reparierte Datei
        server_path.write_text(content, encoding='utf-8')
        
        print("✅ server.py Syntax repariert")
        
        # Teste ob die Datei jetzt parsebar ist
        try:
            compile(content, 'server.py', 'exec')
            print("✅ server.py Syntax-Test bestanden")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax-Fehler bleibt in Zeile {e.lineno}: {e.msg}")
            return False
        
    except Exception as e:
        print(f"❌ Fehler beim Reparieren: {e}")
        return False

def main():
    print("🔧 Repariere server.py Syntax-Fehler...")
    success = fix_server_syntax()
    
    if success:
        print("\n🎉 server.py erfolgreich repariert!")
    else:
        print("\n⚠️ server.py benötigt manuelle Reparatur")

if __name__ == "__main__":
    main()