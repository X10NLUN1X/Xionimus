# 🔧 Backend Scripts

Dieses Verzeichnis enthält Wartungs- und Operations-Scripts für das Backend.

## 📜 Verfügbare Scripts

### init_indexes.py

**Zweck**: Datenbank-Index Management für optimale Query-Performance

**Verwendung**:

```bash
# Standard: Indizes initialisieren
python scripts/init_indexes.py

# Index-Status anzeigen
python scripts/init_indexes.py --status

# Datenbank optimieren (VACUUM)
python scripts/init_indexes.py --vacuum

# Alles ausführen (init + vacuum + status)
python scripts/init_indexes.py --all
```

**Erstellte Indizes**:

#### Users Table
- `idx_users_role` - Filterung nach Rolle (admin/user)
- `idx_users_is_active` - Aktive User-Queries
- `idx_users_github_username` - GitHub Integration Lookups
- `idx_users_last_login` - Login-Historie Queries

#### Sessions Table
- `idx_sessions_user_id` - User's Sessions
- `idx_sessions_workspace_id` - Workspace-bezogene Sessions
- `idx_sessions_created_at` - Zeitbasierte Sortierung
- `idx_sessions_updated_at` - Letzte Aktivität
- `idx_sessions_user_updated` - Composite für User + Zeit Queries

#### Messages Table
- `idx_messages_session_id` - Nachrichten einer Session
- `idx_messages_timestamp` - Zeitbasierte Sortierung
- `idx_messages_role` - Filterung nach Rolle (user/assistant)
- `idx_messages_parent_id` - Threaded Conversations
- `idx_messages_session_timestamp` - Composite für Session + Zeit

#### Uploaded Files Table
- `idx_uploaded_files_user_id` - User's Files
- `idx_uploaded_files_uploaded_at` - Upload-Historie
- `idx_uploaded_files_mime_type` - Datei-Typ Filterung
- `idx_uploaded_files_user_uploaded` - Composite für User + Zeit

**Features**:
- ✅ Idempotent - kann mehrfach ausgeführt werden
- ✅ Auto-detect existierende Indizes
- ✅ ANALYZE für Query-Planer Optimization
- ✅ VACUUM für Datenbankdatei-Komprimierung

**Wann ausführen**:
- Nach Schema-Änderungen
- Bei Performance-Problemen
- Nach größeren Datenimports
- Regelmäßig (z.B. monatlich mit VACUUM)

## 📊 Performance-Überwachung

### Query Performance prüfen

```bash
# SQLite EXPLAIN QUERY PLAN
sqlite3 ~/.xionimus_ai/xionimus.db

sqlite> EXPLAIN QUERY PLAN
SELECT * FROM sessions WHERE user_id = 'test_user' ORDER BY updated_at DESC;
```

**Erwartete Ausgabe mit Indizes**:
```
QUERY PLAN
`--SEARCH TABLE sessions USING INDEX idx_sessions_user_updated (user_id=?)
```

Ohne Index würde stehen:
```
`--SCAN TABLE sessions
```

### Datenbank-Statistiken

```sql
-- Tabellen-Größen
SELECT name, 
       (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=name) as index_count
FROM sqlite_master 
WHERE type='table';

-- Alle Indizes anzeigen
SELECT name, tbl_name, sql 
FROM sqlite_master 
WHERE type='index' 
ORDER BY tbl_name, name;
```

## 🚀 Automatisierung

### Cron-Job (Linux/Mac)

```bash
# Täglich um 3 Uhr morgens
0 3 * * * cd /app/backend && python scripts/init_indexes.py --all >> /var/log/db_maintenance.log 2>&1
```

### Systemd Timer (Linux)

```ini
# /etc/systemd/system/xionimus-db-maintenance.timer
[Unit]
Description=Xionimus Database Maintenance

[Timer]
OnCalendar=daily
OnCalendar=03:00
Persistent=true

[Install]
WantedBy=timers.target
```

## 📈 Performance-Tipps

### 1. Index-Coverage prüfen

```python
# Zeige welche Indizes für Query verwendet werden
import sqlite3
conn = sqlite3.connect('~/.xionimus_ai/xionimus.db')
cursor = conn.cursor()
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM messages WHERE session_id = ?", ("test",))
print(cursor.fetchall())
```

### 2. Regelmäßige Wartung

```bash
# Monatlich
python scripts/init_indexes.py --vacuum

# Nach größeren Änderungen
python scripts/init_indexes.py --all
```

### 3. Monitoring

- Langsame Queries in Application Logs tracken
- Query-Zeit > 100ms als Warning loggen
- Bei Performance-Degradation: VACUUM + ANALYZE ausführen

## 🔍 Troubleshooting

### Problem: "Database is locked"

**Ursache**: Andere Prozesse greifen auf DB zu

**Lösung**:
```bash
# Backend stoppen
sudo supervisorctl stop backend

# Wartung ausführen
python scripts/init_indexes.py --all

# Backend starten
sudo supervisorctl start backend
```

### Problem: Indizes werden nicht genutzt

**Diagnose**:
```bash
python scripts/init_indexes.py --status
```

**Lösung**:
```bash
# ANALYZE ausführen für Query-Planer Update
python scripts/init_indexes.py --vacuum
```

### Problem: Datenbank zu groß

**Lösung**:
1. Alte Sessions archivieren
2. VACUUM ausführen
3. Ggf. Retention-Policy implementieren

## 📚 Weitere Ressourcen

- [SQLite Index Documentation](https://sqlite.org/lang_createindex.html)
- [Query Planning in SQLite](https://sqlite.org/queryplanner.html)
- [VACUUM Command](https://sqlite.org/lang_vacuum.html)

---

**Letzte Aktualisierung**: Januar 2025  
**Maintainer**: Backend Team
