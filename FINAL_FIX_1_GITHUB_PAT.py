"""
═══════════════════════════════════════════════════════════════════════════
FINAL FIX #1: GITHUB_PAT.PY - ACTIVE_PROJECT BEIM IMPORT SETZEN
═══════════════════════════════════════════════════════════════════════════

DATEI: backend/app/api/github_pat.py
FUNKTION: import_repository (ca. Zeile 450-500)

SUCHE NACH DIESER STELLE:
"""

# VORHER (Original Code - ca. Zeile 480):
"""
        # Import erfolgreich
        logger.info(f"✅ Repository {owner}/{repo_name} erfolgreich importiert")
        logger.info(f"📂 Gespeichert in: {repo_destination}")
        
        return {
            "status": "success",
            "repository": f"{owner}/{repo_name}",
            "branch": branch,
            "path": str(repo_destination)
        }
"""

# ═══════════════════════════════════════════════════════════════════════════
# NACHHER (Mit Fix - Füge ZWISCHEN logger.info und return ein):
# ═══════════════════════════════════════════════════════════════════════════

"""
        # Import erfolgreich
        logger.info(f"✅ Repository {owner}/{repo_name} erfolgreich importiert")
        logger.info(f"📂 Gespeichert in: {repo_destination}")
        
        # ===================================================================
        # 🆕 FIX: SETZE ACTIVE_PROJECT IN SESSION
        # ===================================================================
        try:
            from ..models.session_models import Session
            from ..core.database import get_db_session
            from datetime import datetime, timezone
            
            db = get_db_session()
            try:
                # Finde aktuelle Session für diesen User
                # Nehme die zuletzt aktualisierte Session
                session = db.query(Session).filter(
                    Session.user_id == user_id
                ).order_by(Session.updated_at.desc()).first()
                
                if session:
                    # Setze active_project
                    session.active_project = repo_name
                    session.active_project_branch = branch
                    session.updated_at = datetime.now(timezone.utc)
                    
                    db.commit()
                    logger.info(f"✅ Active project gesetzt: {repo_name} (Session: {session.id[:8]}...)")
                else:
                    logger.warning(f"⚠️ Keine Session gefunden für User {user_id}")
            
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"❌ Fehler beim Setzen von active_project: {e}")
            # Nicht kritisch - Import war erfolgreich
        # ===================================================================
        # END FIX
        # ===================================================================
        
        return {
            "status": "success",
            "repository": f"{owner}/{repo_name}",
            "branch": branch,
            "path": str(repo_destination),
            "active": True  # 🆕 Zeige dass Projekt aktiviert wurde
        }
"""

# ═══════════════════════════════════════════════════════════════════════════
# ALTERNATIVE: WENN IMPORTS OBEN FEHLEN
# ═══════════════════════════════════════════════════════════════════════════

"""
Falls du oben in der Datei (bei den anderen Imports, ca. Zeile 1-30) diese Imports 
NOCH NICHT hast, füge sie hinzu:

from datetime import datetime, timezone
from ..models.session_models import Session
from ..core.database import get_db_session

ABER: Wahrscheinlich sind sie schon da, da die Datei Sessions nutzt!
"""

# ═══════════════════════════════════════════════════════════════════════════
# SCHRITT-FÜR-SCHRITT ANLEITUNG
# ═══════════════════════════════════════════════════════════════════════════

"""
1. BACKUP ERSTELLEN:
   cd C:\AI\Xionimus\backend\app\api
   copy github_pat.py github_pat.py.backup

2. DATEI ÖFFNEN:
   C:\AI\Xionimus\backend\app\api\github_pat.py

3. SUCHEN (Strg+F):
   "# Import erfolgreich"
   
   Sollte ca. bei Zeile 480 sein in der import_repository Funktion

4. EINFÜGEN:
   - NACH den beiden logger.info Zeilen
   - VOR dem "return {" Statement
   
   Kopiere den kompletten "# 🆕 FIX" Block (von "try:" bis "# END FIX")

5. SPEICHERN

6. BACKEND NEU STARTEN:
   cd C:\AI\Xionimus\backend
   python server_launcher.py

7. TESTEN:
   - Importiere ein Test-Repository in der UI
   - Prüfe Backend-Log: "✅ Active project gesetzt: ..."
   - Agent sollte Repository sofort sehen!
"""

# ═══════════════════════════════════════════════════════════════════════════
# ERWARTETES ERGEBNIS
# ═══════════════════════════════════════════════════════════════════════════

"""
BACKEND-LOG BEIM IMPORT (vorher):
✅ Repository X10NLUN1X/Xionimus erfolgreich importiert
📂 Gespeichert in: C:\AI\Xionimus\backend\workspace\github_imports\{user_id}\Xionimus

BACKEND-LOG BEIM IMPORT (nachher):
✅ Repository X10NLUN1X/Xionimus erfolgreich importiert
📂 Gespeichert in: C:\AI\Xionimus\backend\workspace\github_imports\{user_id}\Xionimus
✅ Active project gesetzt: Xionimus (Session: abc12345...)  ← 🆕 DIESE ZEILE!

AGENT VERHALTEN:
- Vorher: "Ich habe keinen Zugriff auf Repository"
- Nachher: "Ich sehe das Repository mit folgender Struktur..."
"""

# ═══════════════════════════════════════════════════════════════════════════
# WICHTIGE HINWEISE
# ═══════════════════════════════════════════════════════════════════════════

"""
⚠️ WICHTIG:
1. Das FIX setzt active_project für die NEUESTE Session des Users
2. Wenn User mehrere Sessions hat, wird nur die aktuellste aktiviert
3. Der Fix ist NON-BREAKING - bei Fehler läuft Import trotzdem durch
4. datetime.now(timezone.utc) braucht: from datetime import timezone

✅ SICHER:
- Try-Except verhindert Crash bei Fehler
- finally: db.close() verhindert Connection-Leaks
- Import war bereits erfolgreich BEVOR dieser Code läuft

🔧 DEBUGGING:
Falls es nicht funktioniert:
1. Prüfe Backend-Log: Steht "✅ Active project gesetzt" dort?
2. Falls "⚠️ Keine Session gefunden": User hat keine Sessions in DB
3. Falls Error in Log: Check Imports oben in Datei
4. Falls gar nichts in Log: Code wurde nicht ausgeführt (falsche Stelle?)
"""
