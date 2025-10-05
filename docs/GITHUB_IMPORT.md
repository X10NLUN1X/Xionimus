# GitHub Import Feature - Dokumentation

## Übersicht

Das **GitHub Import Feature** ermöglicht es dir, existierende GitHub-Repositories direkt in deinen Xionimus Workspace zu importieren, um sie weiterzuentwickeln.

## Features

### ✅ Was kann importiert werden?
- **Öffentliche Repositories**: Ohne GitHub-Token
- **Private Repositories**: Mit GitHub-Login
- **Beliebige Branches**: main, master, develop, etc.
- **Custom Verzeichnis**: Wähle eigenen Namen für importiertes Projekt

### 🚀 Workflow

1. **Klick auf "📥 GitHub Import"** Button (im Header oder Welcome Screen)
2. **Eingabe der Repository URL**: z.B. `https://github.com/user/repo`
3. **Optional**: Branch und Zielverzeichnis anpassen
4. **Import starten**: Projekt wird in `/app/xionimus-ai/` geklont
5. **Weiterentwickeln**: Sofort mit AI-Assistenz weiterarbeiten

## Nutzung

### Via UI (Frontend)

**Locations:**
- Welcome Screen: Button "📥 GitHub Import"
- Chat Header: Download-Icon Button (Tooltip: "Import von GitHub")

**Dialog-Felder:**
- **Repository URL** (erforderlich): `https://github.com/username/repo`
- **Branch** (optional): Default = `main`
- **Zielverzeichnis** (optional): Default = Repository-Name

### Via API (Backend)

**Endpoint:** `POST /api/github/import`

**Request:**
```json
{
  "repo_url": "https://github.com/user/repo",
  "branch": "main",
  "target_directory": "my-project"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully imported repository: user/repo",
  "repository": {
    "owner": "user",
    "name": "repo",
    "branch": "main",
    "url": "https://github.com/user/repo"
  },
  "import_details": {
    "target_directory": "my-project",
    "total_files": 42,
    "file_types": {
      ".py": 15,
      ".js": 20,
      ".md": 7
    }
  },
  "workspace_path": "/app/xionimus-ai/my-project"
}
```

### Status Check

**Endpoint:** `GET /api/github/import/status`

Zeigt aktuelle Workspace-Projekte und Import-Capabilities.

## Beispiele

### Public Repository importieren

```bash
curl -X POST http://localhost:8001/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/vercel/next.js",
    "branch": "canary"
  }'
```

### Private Repository (mit Token)

```bash
curl -X POST http://localhost:8001/api/github/import \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ghp_YOUR_TOKEN" \
  -d '{
    "repo_url": "https://github.com/myuser/private-repo",
    "branch": "main"
  }'
```

### Custom Verzeichnis

```bash
curl -X POST http://localhost:8001/api/github/import \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/facebook/react",
    "branch": "main",
    "target_directory": "react-source"
  }'
```

## Technische Details

### Backend-Implementierung

**Datei:** `/app/backend/app/api/github.py`

**Funktionsweise:**
1. URL wird geparst (Regex-Extraktion von Owner/Repo)
2. Git clone in temporäres Verzeichnis
3. `.git` Ordner wird entfernt
4. Dateien nach `/app/xionimus-ai/` verschoben
5. Datei-Analyse (Anzahl, Typen)
6. Temp-Verzeichnis bereinigt

**Features:**
- Shallow clone (`--depth 1`) für Performance
- Timeout-Schutz (120 Sekunden)
- Automatische Fehlerbehandlung
- Support für HTTPS + SSH URLs

### Frontend-Implementierung

**Komponente:** `/app/frontend/src/components/GitHubImportDialog.tsx`

**Features:**
- Validierung der GitHub-URL
- Branch-Auswahl
- Custom Zielverzeichnis
- Import-Progress-Anzeige
- Erfolgs-/Fehler-Feedback
- Zusammenfassung nach Import

**Context:** `/app/frontend/src/contexts/GitHubContext.tsx`

Neue Funktion: `importRepository(repoUrl, branch?, targetDirectory?)`

## Fehlerbehandlung

### Häufige Fehler

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| Repository not found | Repo existiert nicht oder ist privat | Token hinzufügen oder URL prüfen |
| Branch not found | Branch existiert nicht | Korrekten Branch-Namen eingeben |
| Directory already exists | Zielverzeichnis belegt | Anderes Zielverzeichnis wählen |
| Timeout | Repository zu groß (&gt;500MB) | Kleineres Repo oder manual clone |
| Permission denied | Kein Zugriff auf privates Repo | GitHub-Login erforderlich |

## Einschränkungen

- **Max. Repository-Größe**: ~500MB (2 Minuten Timeout)
- **Shallow Clone**: Nur letzter Commit (keine Git History)
- **Keine Git-Integration**: `.git` Ordner wird entfernt
- **Einmal-Import**: Kein automatisches Update bei Repo-Änderungen

## Workspace-Management

### Importierte Projekte anzeigen

```bash
GET /api/github/import/status
```

Zeigt alle Projekte in `/app/xionimus-ai/` mit Dateianzahl.

### Projekt löschen

```bash
rm -rf /app/xionimus-ai/PROJECT_NAME
```

**Hinweis:** Derzeit keine UI-Funktion zum Löschen.

## Verwendung mit Xionimus AI

Nach dem Import kannst du:

1. **Code analysieren lassen**: "Analysiere die Projektstruktur"
2. **Features hinzufügen**: "Füge Feature X hinzu"
3. **Bugs fixen**: "Fix Bug in file.py"
4. **Refactoring**: "Refactor component Y"
5. **Tests schreiben**: "Erstelle Tests für Z"
6. **Dokumentation**: "Generiere README für dieses Projekt"

**Tipp:** Sage dem AI explizit, in welchem Verzeichnis gearbeitet werden soll:
```
"Arbeite im Projekt Hello-World und füge eine neue Funktion hinzu"
```

## Best Practices

### ✅ Empfohlen
- Kleine bis mittelgroße Projekte (< 100MB)
- Public Repos für schnellen Start
- Klare Verzeichnisnamen wählen
- Nach Import: Projektstruktur analysieren lassen

### ❌ Vermeiden
- Sehr große Monorepos (&gt;500MB)
- Repos mit binären Dateien (Videos, große Assets)
- Identische Verzeichnisnamen zweimal importieren
- Import ohne Verzeichnis-Check

## Zukünftige Features (geplant)

- [ ] Import-Progress-Anzeige in Echtzeit
- [ ] Repository-Browser im UI
- [ ] Update-Funktion (Pull changes)
- [ ] Automatisches Forking
- [ ] Import-History
- [ ] Batch-Import (mehrere Repos)

## Troubleshooting

### Frontend zeigt Import-Button nicht
- Browser-Cache leeren
- Frontend neu laden
- Console auf Fehler prüfen

### Backend-Import schlägt fehl
```bash
# Logs prüfen
tail -n 50 /var/log/supervisor/backend.err.log

# Git verfügbar?
git --version

# Workspace-Rechte prüfen
ls -la /app/xionimus-ai/
```

### Import dauert zu lange
- Repository-Größe prüfen
- Netzwerkverbindung testen
- Shallow clone bereits aktiv (--depth 1)

## Support

Bei Problemen:
1. Backend-Logs prüfen
2. API-Status checken: `GET /api/github/import/status`
3. Test mit kleinem Public Repo (z.B. octocat/Hello-World)
4. Workspace-Verzeichnis manuell prüfen

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Erstellt**: 2025-01-XX  
**Last Updated**: 2025-01-XX
