# Xionimus AI - Windows Installation Guide

## ✅ Finale Version - Komplett getestet

### Schnellstart (3 Schritte)

```batch
1. install.bat       # Installiert alles (5-10 Min)
2. reset-db.bat      # Löscht alte Datenbank (falls Fehler)
3. start.bat         # Startet die Anwendung
```

Dann öffnen: **http://localhost:3000**

---

## Detaillierte Anleitung

### Voraussetzungen

- ✅ **Python 3.8+** ([Download](https://www.python.org/downloads/))
  - ⚠️ Wichtig: "Add Python to PATH" aktivieren!
- ✅ **Node.js v18+** ([Download](https://nodejs.org/))
- ✅ **Windows 10/11**

---

### Installation

#### Schritt 1: Projekt herunterladen
```batch
# Navigieren Sie zum Projektordner
cd C:\Ihr\Pfad\zu\Xionimus-Genesis
```

#### Schritt 2: Installation ausführen
```batch
install.bat
```

**Was passiert:**
- Erstellt Python Virtual Environment
- Installiert ~100 Python-Pakete
- Installiert Node.js Pakete
- Erstellt start.bat Script
- **Dauer: 5-10 Minuten**

#### Schritt 3: Datenbank vorbereiten (nur bei Fehlern)
Falls Backend-Fehler mit "no such column: timestamp":
```batch
reset-db.bat
```

#### Schritt 4: Starten
```batch
start.bat
```

**Zwei Fenster öffnen sich:**
- Backend-Fenster (Port 8001)
- Frontend-Fenster (Port 3000)

**Öffnen Sie im Browser:**
```
http://localhost:3000
```

---

## Neue Features in den Settings

### ✨ Hinzugefügt:

1. **Zurück-Button**
   - Oben links in den Settings
   - Schnelle Navigation zurück

2. **GitHub Integration**
   - GitHub-Account verbinden
   - Code direkt pushen
   - Status-Anzeige

3. **Fork Summary**
   - Button oben rechts
   - Zeigt Workspace-Status
   - Änderungsübersicht

### ❌ Entfernt:

- Manuelle Modell-Auswahl (gpt5)
  - Xionimus AI wählt automatisch das beste Modell!

---

## Fehlerbehebung

### Problem: "Python nicht gefunden"
**Lösung:**
```batch
# Python neu installieren mit "Add to PATH"
# Dann Eingabeaufforderung NEU öffnen
python --version
```

### Problem: "Das System kann den angegebenen Pfad nicht finden"
**Lösung:**
```batch
# Stellen Sie sicher, dass Sie im Hauptordner sind
cd C:\AI\Xionimus-Genesis
# Dann install.bat ausführen
```

### Problem: "no such column: timestamp"
**Lösung:**
```batch
# Alte Datenbank löschen
reset-db.bat
# Backend neu starten
cd backend
python main.py
```

### Problem: "Module not found"
**Lösung:**
```batch
cd backend
venv\Scripts\activate.bat
pip install -r requirements-windows.txt
```

### Problem: Frontend startet nicht
**Lösung:**
```batch
cd frontend
yarn install
yarn dev
```

---

## Projekt-Struktur

```
Xionimus-Genesis/
├── backend/                # Python Backend
│   ├── app/               # API & Core Logic
│   ├── venv/              # Virtual Environment
│   ├── main.py            # Startpunkt
│   └── requirements-windows.txt
│
├── frontend/              # React Frontend
│   ├── src/               # Source Code
│   ├── package.json       # Dependencies
│   └── vite.config.ts     # Build Config
│
├── install.bat           # Installation
├── start.bat             # Starten
├── reset-db.bat          # DB Reset
└── README.md             # Diese Datei
```

---

## Technologie-Stack

### Backend
- FastAPI (Python)
- SQLite (Lokal)
- WebSockets
- OpenAI, Anthropic, Perplexity

### Frontend
- React 18 + TypeScript
- Chakra UI
- Vite
- Framer Motion

---

## Support & Hilfe

### Logs überprüfen

**Backend:**
```batch
cd backend
python main.py
# Fehler werden direkt angezeigt
```

**Frontend:**
```batch
cd frontend
yarn dev
# Browser-Konsole öffnen (F12)
```

### Neu installieren
```batch
# Alles löschen und neu starten
cd backend
rmdir /s /q venv
cd ..\frontend
rmdir /s /q node_modules
cd ..
install.bat
```

---

## Bekannte Einschränkungen

1. **uvloop** - Nicht auf Windows (automatisch übersprungen)
2. **ChromaDB** - Symlinks-Warnung (kann ignoriert werden)
3. **Erste Installation** - Dauert 10-15 Min (große ML-Pakete)

---

## Updates

```batch
# Code aktualisieren
git pull origin main

# Dependencies aktualisieren
install.bat
```

---

## Datenbank-Speicherort

```
C:\Users\[IhrName]\.xionimus_ai\xionimus.db
```

Alle Chats und Einstellungen werden hier lokal gespeichert.

---

**Version:** 2.1.0
**Letztes Update:** 2025-09-30
**Status:** ✅ Produktionsbereit
