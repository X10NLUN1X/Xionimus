# XIONIMUS AI - Installation und Start Guide

## 🚀 Installation und Start (3 Schritte)

### Schritt 1: Installation
```bash
install.bat
```
**Was passiert:**
- Prüft Python 3.10+ und Node.js 18+
- Erstellt `.env` Konfigurationsdateien
- Installiert Backend Dependencies (Python)
- Installiert Frontend Dependencies (Node.js/React)
- Bereitet das System für den Start vor

### Schritt 2: Starten
**Option A - Beide Services gleichzeitig:**
```bash
START_ALL.bat
```

**Option B - Einzeln starten:**
```bash
START_BACKEND.bat    # Terminal 1
START_FRONTEND.bat   # Terminal 2
```

### Schritt 3: Nutzen
- **Frontend:** http://localhost:3000 (Hauptbenutzeroberfläche)
- **Backend API:** http://localhost:8001 (API + Dokumentation)

## 📁 Skript-Übersicht

| Skript | Zweck | Wann verwenden |
|--------|-------|----------------|
| `install.bat` | **Installation** aller Dependencies | Einmalig vor dem ersten Start |
| `START_BACKEND.bat` | **Nur Backend** starten | Backend einzeln starten |
| `START_FRONTEND.bat` | **Nur Frontend** starten | Frontend einzeln starten |
| `START_ALL.bat` | **Beide Services** starten | Komfort-Start (empfohlen) |
| `WINDOWS_INSTALL.bat` | Vollinstallation + Start | Legacy (umfassend) |
| `QUICK_FIX_AIOHTTP.bat` | Reparatur-Installation | Bei Problemen |
| `MINIMAL_INSTALL.bat` | Minimale Installation | Problemlösung |

## 🔧 Installation Details

### Backend Dependencies
- **Web Framework:** FastAPI, Uvicorn, Starlette
- **Async/Network:** aiohttp, aiohappyeyeballs, anyio
- **Database:** Motor (MongoDB), PyMongo
- **AI APIs:** Anthropic (Claude), OpenAI (GPT)
- **Utilities:** python-dotenv, requests, PyYAML

### Frontend Dependencies  
- **Framework:** React 19+
- **Build Tool:** Craco (Create React App Configuration Override)
- **UI Components:** Radix UI, Tailwind CSS
- **Code Editor:** Monaco Editor
- **Icons:** Lucide React

## 🎯 Nach der Installation

### API-Konfiguration
1. Öffne http://localhost:3000
2. Klicke auf "API Configuration"
3. Füge deine API-Keys hinzu:
   - **Anthropic API Key** (für Claude-Agent)
   - **OpenAI API Key** (für GPT-Agent)
   - **Perplexity API Key** (für Research-Agent)

### Verfügbare Features
- **9 AI-Agenten:** Code, Research, Writing, Data, QA, GitHub, File, Session, Experimental
- **Multi-Agent Chat System**
- **GitHub Repository Integration**
- **File Upload und Management**
- **Session Management** (Gespräche speichern)
- **Code Editor** mit Syntax-Highlighting

## 🛠️ Troubleshooting

### Installation schlägt fehl
```bash
QUICK_FIX_AIOHTTP.bat    # Behebt häufige Probleme
MINIMAL_INSTALL.bat      # Minimale Installation
```

### Backend startet nicht
- Prüfe Python 3.10+ Installation
- Prüfe `.env` Datei im backend/ Verzeichnis
- Führe `install.bat` erneut aus

### Frontend startet nicht
- Prüfe Node.js 18+ Installation
- Prüfe `node_modules/` Verzeichnis im frontend/ Ordner
- Führe `install.bat` erneut aus

### Port bereits belegt
- Backend (Port 8001): Andere Anwendung auf dem Port schließen
- Frontend (Port 3000): Andere React-Apps beenden

## 📋 System-Anforderungen

- **Python:** 3.10 oder höher
- **Node.js:** 18.0 oder höher
- **Betriebssystem:** Windows (für .bat Skripte)
- **Speicher:** Mindestens 4GB RAM empfohlen
- **Internetverbindung:** Für AI API-Calls erforderlich