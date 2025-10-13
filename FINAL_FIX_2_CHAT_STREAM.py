"""
═══════════════════════════════════════════════════════════════════════════
FINAL FIX #2: CHAT_STREAM.PY - /ACTIVATE COMMAND HANDLER (OPTIONAL)
═══════════════════════════════════════════════════════════════════════════

HINWEIS: Dieser Fix ist OPTIONAL (Fallback-Lösung)
Wenn FIX #1 (github_pat.py) korrekt implementiert ist, ist dieser nicht nötig!

ABER: Nützlich als Fallback wenn User manuell zwischen Projekten wechseln will.
"""

# ═══════════════════════════════════════════════════════════════════════════
# SCHRITT 1: NEUE FUNKTIONEN OBEN EINFÜGEN
# ═══════════════════════════════════════════════════════════════════════════

"""
POSITION: Nach den Imports (ca. Zeile 1-30), VOR class ConnectionManager

FÜGE DIESE 2 FUNKTIONEN EIN:
"""

# ─────────────────────────────────────────────────────────────────────────
# FUNKTION 1: list_available_projects
# ─────────────────────────────────────────────────────────────────────────

def list_available_projects(user_id: Optional[str]) -> str:
    """Listet alle importierten Projekte für einen User auf"""
    from ..core.config import settings
    from pathlib import Path
    import os
    
    if not user_id:
        return "❌ Kein User gefunden"
    
    base_path = os.path.join(str(settings.GITHUB_IMPORTS_DIR), str(user_id))
    
    if not os.path.exists(base_path):
        return "📂 Noch keine Projekte importiert"
    
    try:
        projects = [d for d in os.listdir(base_path) 
                   if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('.')]
        
        if not projects:
            return "📂 Noch keine Projekte importiert"
        
        result = []
        for project in projects:
            project_path = os.path.join(base_path, project)
            
            # Zähle Dateien
            try:
                file_count = sum(1 for _ in Path(project_path).rglob("*") if _.is_file())
                result.append(f"• `{project}` ({file_count} Dateien)")
            except:
                result.append(f"• `{project}`")
        
        return "\\n".join(result)
    
    except Exception as e:
        return f"❌ Fehler beim Laden: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────
# FUNKTION 2: handle_command
# ─────────────────────────────────────────────────────────────────────────

async def handle_command(
    user_message: str,
    session_id: str,
    user_id: Optional[str],
    websocket: WebSocket,
    manager: ConnectionManager
) -> bool:
    """
    Behandelt Chat-Commands wie /activate, /deactivate, /list, /help
    
    Returns:
        True wenn Command behandelt wurde
        False wenn normale Chat-Message
    """
    from ..models.session_models import Session
    from ..core.database import get_db_session
    from ..core.config import settings
    from datetime import datetime, timezone
    from pathlib import Path
    import os
    
    message = user_message.strip()
    
    # ========================================================================
    # /activate <project_name>
    # ========================================================================
    if message.lower().startswith("/activate"):
        parts = message.split(maxsplit=1)
        
        if len(parts) < 2:
            await manager.send_message({
                "type": "command_response",
                "content": "❌ **Verwendung:** `/activate <project_name>`\\n\\nBeispiel: `/activate Xionimus`",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, session_id)
            return True
        
        project_name = parts[1].strip()
        
        db = get_db_session()
        try:
            # Prüfe ob Projekt existiert
            repo_path = os.path.join(str(settings.GITHUB_IMPORTS_DIR), str(user_id), project_name)
            
            if not os.path.exists(repo_path):
                available = list_available_projects(user_id)
                await manager.send_message({
                    "type": "command_response",
                    "content": f"❌ **Projekt nicht gefunden:** `{project_name}`\\n\\n**Verfügbare Projekte:**\\n{available}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
                return True
            
            # Setze active_project
            session = db.query(Session).filter(Session.id == session_id).first()
            
            if session:
                session.active_project = project_name
                session.updated_at = datetime.now(timezone.utc)
                db.commit()
                
                # Scanne Repository
                repo_structure = scan_repository_structure(repo_path, max_files=1000)
                file_count = repo_structure.get('summary', {}).get('total_files', 0)
                dir_count = repo_structure.get('summary', {}).get('total_directories', 0)
                
                await manager.send_message({
                    "type": "command_response",
                    "content": f"✅ **Projekt aktiviert:** `{project_name}`\\n\\n📂 **Statistiken:**\\n- Dateien: {file_count}\\n- Verzeichnisse: {dir_count}\\n\\nDu kannst jetzt Fragen zum Repository stellen!",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
                
                logger.info(f"✅ /activate: '{project_name}' activated for session {session_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ /activate error: {e}")
            await manager.send_message({
                "type": "command_response",
                "content": f"❌ **Fehler:** {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, session_id)
            return True
        
        finally:
            db.close()
    
    # ========================================================================
    # /deactivate
    # ========================================================================
    elif message.lower().startswith("/deactivate"):
        db = get_db_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            
            if session and session.active_project:
                old_project = session.active_project
                session.active_project = None
                session.active_project_branch = None
                session.updated_at = datetime.now(timezone.utc)
                db.commit()
                
                await manager.send_message({
                    "type": "command_response",
                    "content": f"✅ **Projekt deaktiviert:** `{old_project}`",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
                
                logger.info(f"✅ /deactivate: '{old_project}' deactivated")
            else:
                await manager.send_message({
                    "type": "command_response",
                    "content": "ℹ️ Kein aktives Projekt vorhanden.",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
            
            return True
        finally:
            db.close()
    
    # ========================================================================
    # /list
    # ========================================================================
    elif message.lower().startswith("/list"):
        projects_list = list_available_projects(user_id)
        
        await manager.send_message({
            "type": "command_response",
            "content": f"📂 **Verfügbare Projekte:**\\n\\n{projects_list}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
        
        return True
    
    # ========================================================================
    # /help
    # ========================================================================
    elif message.lower().startswith("/help"):
        await manager.send_message({
            "type": "command_response",
            "content": """📖 **Verfügbare Commands:**

`/activate <project>` - Aktiviere importiertes GitHub-Projekt
`/deactivate` - Deaktiviere aktuelles Projekt
`/list` - Zeige alle importierten Projekte
`/help` - Zeige diese Hilfe

**Beispiel:**
```
/activate Xionimus
```

Nach Aktivierung kannst du Fragen zum Repository stellen!""",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
        
        return True
    
    # Kein Command erkannt
    return False


# ═══════════════════════════════════════════════════════════════════════════
# SCHRITT 2: COMMAND-CHECK IN WEBSOCKET-HANDLER EINFÜGEN
# ═══════════════════════════════════════════════════════════════════════════

"""
POSITION: In der WebSocket-Handler Funktion, VOR "Add user message to history"

SUCHE NACH (ca. Zeile 380-400):
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })

FÜGE DAVOR EIN:
"""

# ─────────────────────────────────────────────────────────────────────────
# CODE ZUM EINFÜGEN (Schritt 2):
# ─────────────────────────────────────────────────────────────────────────

"""
            # ===================================================================
            # 🆕 COMMAND HANDLER
            # ===================================================================
            if user_message.strip().startswith("/"):
                command_handled = await handle_command(
                    user_message=user_message,
                    session_id=session_id,
                    user_id=user_id,
                    websocket=websocket,
                    manager=manager
                )
                
                # Wenn Command behandelt wurde, nicht an AI senden
                if command_handled:
                    continue
            # ===================================================================
            # END COMMAND HANDLER
            # ===================================================================
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
"""

# ═══════════════════════════════════════════════════════════════════════════
# KOMPLETTE SCHRITT-FÜR-SCHRITT ANLEITUNG
# ═══════════════════════════════════════════════════════════════════════════

"""
1. BACKUP:
   cd C:\AI\Xionimus\backend\app\api
   copy chat_stream.py chat_stream.py.backup

2. ÖFFNE:
   C:\AI\Xionimus\backend\app\api\chat_stream.py

3. SCHRITT 2A - Funktionen oben einfügen:
   - Scrolle nach oben (nach Imports, vor class ConnectionManager)
   - Füge BEIDE Funktionen ein (list_available_projects + handle_command)

4. SCHRITT 2B - Command-Check einfügen:
   - Suche: "# Add user message to history"
   - Füge den Command-Handler-Block DAVOR ein

5. IMPORTS PRÜFEN (sollten schon da sein):
   from datetime import datetime, timezone
   from pathlib import Path
   from typing import Optional
   import os

6. SPEICHERN

7. BACKEND NEU STARTEN:
   cd C:\AI\Xionimus\backend
   python server_launcher.py

8. TESTEN:
   Im Chat: /help
   Im Chat: /list
   Im Chat: /activate Xionimus
"""

# ═══════════════════════════════════════════════════════════════════════════
# ERWARTETES VERHALTEN
# ═══════════════════════════════════════════════════════════════════════════

"""
COMMANDS:
---------
/help    → Zeigt alle verfügbaren Commands
/list    → Zeigt alle importierten Repositories
/activate Xionimus → Aktiviert das Xionimus Repository
/deactivate → Deaktiviert aktuelles Repository

BEISPIEL-DIALOG:
----------------
User: /list
Bot: 📂 Verfügbare Projekte:
     • Xionimus (1839 Dateien)
     • TestRepo (245 Dateien)

User: /activate Xionimus
Bot: ✅ Projekt aktiviert: Xionimus
     📂 Statistiken:
     - Dateien: 1839
     - Verzeichnisse: 460
     Du kannst jetzt Fragen zum Repository stellen!

User: Zeig mir die README
Bot: [Inhalt der README.md aus dem Repository]
"""

# ═══════════════════════════════════════════════════════════════════════════
# WICHTIGE HINWEISE
# ═══════════════════════════════════════════════════════════════════════════

"""
⚠️ DIESER FIX IST OPTIONAL:
- FIX #1 (github_pat.py) ist der WICHTIGERE Fix
- FIX #2 ist nur Fallback/Convenience für User
- Wenn FIX #1 implementiert ist, funktioniert Import automatisch

✅ VORTEIL VON FIX #2:
- User kann manuell zwischen Projekten wechseln
- Kein Re-Import nötig bei mehreren Repos
- Bessere User-Experience

🔧 DEBUGGING:
Falls Commands nicht funktionieren:
1. Backend-Log prüfen: Steht "✅ /activate: ..." dort?
2. Frontend: Öffne Browser Console (F12) - Fehler?
3. Teste zuerst /help - funktioniert das?
4. Prüfe ob handle_command WIRKLICH aufgerufen wird (logger.info am Anfang)
"""
