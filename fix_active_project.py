"""
FIX: Setze active_project in der Datenbank
"""
import sqlite3
from pathlib import Path

# Verbinde mit Datenbank
db_path = Path.home() / ".xionimus_ai" / "xionimus.db"
print(f"📂 Datenbank: {db_path}")

if not db_path.exists():
    print("❌ Datenbank nicht gefunden!")
    print(f"   Gesucht: {db_path}")
    input("Drücke Enter zum Beenden...")
    exit(1)

db = sqlite3.connect(str(db_path))
cursor = db.cursor()

# Update alle Sessions für diesen User UND Sessions ohne user_id
user_id = "87f7095f-5f5d-4c27-b9fe-930ef9eec725"
cursor.execute("""
    UPDATE sessions 
    SET active_project = 'Xionimus', 
        active_project_branch = 'main' 
    WHERE user_id = ? OR user_id IS NULL
""", (user_id,))

db.commit()

print(f"✅ {cursor.rowcount} session(s) updated!")
print("")

# Zeige Ergebnis
cursor.execute("""
    SELECT id, active_project, active_project_branch 
    FROM sessions 
    WHERE user_id = ? 
    LIMIT 5
""", (user_id,))

print("📊 Sessions:")
for row in cursor.fetchall():
    session_id = row[0][:30]
    active_project = row[1] or "NULL"
    branch = row[2] or "NULL"
    print(f"   {session_id}... → {active_project} ({branch})")

db.close()

print("")
print("✅ FERTIG!")
print("Jetzt im Chat testen: 'Analysiere die Repository-Struktur'")
print("")
input("Drücke Enter zum Beenden...")
