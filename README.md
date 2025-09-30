# Xionimus AI 🚀

**Intelligente Desktop-KI-Anwendung** mit automatischer Modellauswahl, Multi-Modal-Support und lokaler Datenspeicherung.

## ⚡ Schnellstart (Windows)

```batch
# 1. Installation (5-10 Min, nur einmal)
install.bat

# 2. Bei Datenbank-Fehlern (optional)
reset-db.bat

# 3. Starten
start.bat
```

**Dann öffnen:** http://localhost:3000

---

## ✨ Neue Features (v2.1.0)

### Settings Überarbeitung
- ✅ **Zurück-Button** - Schnelle Navigation
- ✅ **GitHub Integration** - Code direkt pushen
- ✅ **Fork Summary** - Workspace-Übersicht
- ❌ **Modell-Auswahl entfernt** - Xionimus wählt automatisch!

### Intelligente Features
- 🤖 **Auto-Modellauswahl** - GPT-5, Claude Opus 4.1, Perplexity
- 📄 **PDF & Bilder** - Automatische Verarbeitung
- 🗄️ **RAG-System** - ChromaDB Integration
- 💾 **Lokale Datenbank** - Alle Daten bleiben auf Ihrem PC

---

## 🛠️ Voraussetzungen

- ✅ **Python 3.8+** ([Download](https://www.python.org/downloads/))
  - ⚠️ WICHTIG: "Add Python to PATH" aktivieren!
- ✅ **Node.js v18+** ([Download](https://nodejs.org/))
- ✅ **Windows 10/11**

---

## 📖 Detaillierte Anleitung

Siehe **WINDOWS_INSTALLATION_FINAL.md** für:
- Schritt-für-Schritt Installation
- Fehlerbehebung
- Technische Details
- Support & Hilfe

---

## 🎨 Technologie

**Frontend:** React 18 + TypeScript + Chakra UI + Vite  
**Backend:** FastAPI + Python + SQLite + WebSockets  
**AI:** OpenAI GPT-5, Anthropic Claude Opus 4.1, Perplexity

---

## 🐛 Häufige Probleme

| Problem | Lösung |
|---------|--------|
| "Python nicht gefunden" | Python mit "Add to PATH" neu installieren |
| "no such column: timestamp" | `reset-db.bat` ausführen |
| "Module not found" | `install.bat` nochmal ausführen |
| Backend startet nicht | `cd backend && python main.py` für Details |

---

## 📁 Projekt-Struktur

```
Xionimus-Genesis/
├── backend/           # Python Backend
├── frontend/          # React Frontend
├── install.bat        # Installation
├── start.bat          # Starten
└── reset-db.bat       # DB Reset
```

---

## 🔐 Datenspeicherung

Alle Daten werden lokal gespeichert:
```
C:\Users\[IhrName]\.xionimus_ai\xionimus.db
```

---

**Version:** 2.1.0  
**Status:** ✅ Produktionsbereit  
**Lizenz:** MIT
