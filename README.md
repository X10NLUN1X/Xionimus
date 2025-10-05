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
- ✅ **GitHub Integration** - Code direkt pushen (OAuth über UI konfigurierbar!)
- ✅ **Fork Summary** - Umfassende Projektübersicht mit Statistiken
- ✅ **GitHub OAuth Configuration** - Einfache Einrichtung über die Benutzeroberfläche
- ❌ **Modell-Auswahl entfernt** - Xionimus wählt automatisch!

### GitHub Features
- 🔗 **OAuth über UI** - Keine .env Dateien mehr nötig!
- 📊 **Fork Summary** - Projektstatistiken (Dateien, Zeilen, Sprachen)
- 🚀 **Push to GitHub** - Gesamtes Projekt mit einem Klick pushen
- 🔐 **Sichere Speicherung** - Credentials bleiben lokal

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

## 🔗 GitHub Integration einrichten

### Option 1: Über die Benutzeroberfläche (Empfohlen)

1. **Starten Sie die Anwendung** und öffnen Sie http://localhost:3000
2. **Gehen Sie zu Settings** (Einstellungen)
3. **Scrollen Sie zum Abschnitt "GitHub Integration"**
4. **Klicken Sie auf "Configure OAuth"** um die Konfiguration anzuzeigen

5. **Erstellen Sie eine GitHub OAuth App:**
   - Besuchen Sie: https://github.com/settings/developers
   - Klicken Sie auf **"New OAuth App"**
   - Füllen Sie die Felder aus:
     - **Application name:** Xionimus AI
     - **Homepage URL:** `http://localhost:3000`
     - **Authorization callback URL:** `http://localhost:3000/github/callback`
   - Klicken Sie auf **"Register application"**

6. **Kopieren Sie Ihre Credentials:**
   - Kopieren Sie die **Client ID**
   - Generieren Sie ein neues **Client Secret** und kopieren Sie es

7. **Fügen Sie die Credentials in Xionimus AI ein:**
   - Gehen Sie zurück zu den Settings in Xionimus AI
   - Geben Sie die **Client ID** ein
   - Geben Sie das **Client Secret** ein
   - Klicken Sie auf **"Save GitHub OAuth Configuration"**

8. **Verbinden Sie Ihr GitHub-Konto:**
   - Klicken Sie auf **"Connect GitHub"**
   - Autorisieren Sie die Anwendung in GitHub
   - Sie werden zurück zu Xionimus AI weitergeleitet

9. **Verwenden Sie die GitHub-Features:**
   - **Fork Summary:** Zeigt eine umfassende Projektübersicht
   - **Push to GitHub:** Pusht Ihr gesamtes Projekt zu einem GitHub Repository

### Option 2: Alternative - Personal Access Token

Wenn Sie OAuth nicht konfigurieren möchten:
1. Erstellen Sie einen Personal Access Token: https://github.com/settings/tokens
2. Wählen Sie Scopes: `repo`, `user`
3. Verwenden Sie den Token direkt für Push-Operationen

### Gespeicherte Konfiguration

Die OAuth-Konfiguration wird sicher gespeichert in:
```
C:\Users\[IhrName]\.xionimus_ai\app_settings.json
```

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
