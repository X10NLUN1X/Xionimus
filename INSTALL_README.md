# Emergent-Next Installation Scripts

Automatische Installationsskripte für die Emergent-Next Development Platform.

## 🚀 Verfügbare Installationsoptionen

### 1. Vollständige Installation (Linux/macOS)
```bash
cd /app
chmod +x install-all.sh
./install-all.sh
```

**Was wird installiert:**
- Node.js 20+ und Yarn
- Python Virtual Environment + Dependencies
- MongoDB (falls nicht vorhanden)
- Frontend Dependencies (React, Monaco Editor, Chakra UI)
- Backend Dependencies (FastAPI, Motor, PyMongo)
- CORS-Konfiguration
- Startup-Skripte
- Environment-Dateien

### 2. Schnellinstallation (Linux/macOS)
```bash
cd /app
chmod +x quick-install.sh
./quick-install.sh
```

**Für bestehende Entwicklungsumgebungen mit:**
- Node.js bereits installiert
- Python bereits installiert
- MongoDB bereits konfiguriert

### 3. Windows Installation
```batch
# Als Administrator ausführen
install-windows.bat
```

**Automatische Windows-Installation** mit Überprüfung aller Systemanforderungen.

## 📋 Systemanforderungen

### Minimum Requirements
- **Python**: 3.10+
- **Node.js**: 18+
- **MongoDB**: 7.0+
- **RAM**: 4GB
- **Speicher**: 2GB frei

### Empfohlene Specs
- **Python**: 3.11+
- **Node.js**: 20+
- **MongoDB**: 7.0+
- **RAM**: 8GB+
- **Speicher**: 5GB+ frei

## 🎯 Nach der Installation

### 1. Starten der Anwendung
```bash
cd /app/emergent-next
./start-all.sh        # Linux/macOS
# oder
start-all.bat         # Windows
```

### 2. Zugriff auf die Anwendung
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Dokumentation**: http://localhost:8002/docs

### 3. AI API Keys konfigurieren (Optional)
Bearbeite `/app/emergent-next/backend/.env`:
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
```

## 🛠️ Verfügbare Skripte

Nach der Installation stehen folgende Skripte zur Verfügung:

### Linux/macOS
```bash
./start-all.sh        # Startet Frontend + Backend
./start-backend.sh    # Nur Backend
./start-frontend.sh   # Nur Frontend
```

### Windows
```batch
start-all.bat         # Startet Frontend + Backend
start-backend.bat     # Nur Backend
start-frontend.bat    # Nur Frontend
```

## 📊 Development Environment Features

### Monaco Editor (VS Code Experience)
- Syntax-Highlighting für 20+ Sprachen
- Auto-Save mit Ctrl+S
- IntelliSense und Code-Vervollständigung
- Datei-Tabs und Multi-File-Editing

### File Management
- TreeView mit Drag & Drop
- 250MB File Upload Limit
- Kontextmenüs (Erstellen, Löschen, Umbenennen)
- File-Type Icons

### Backend Features
- FastAPI mit automatischer API-Dokumentation
- MongoDB Integration
- WebSocket-Support für Real-time Chat
- File Upload/Download APIs
- Workspace Management APIs

## 🔧 Problembehandlung

### MongoDB Verbindungsfehler
```bash
# MongoDB Status prüfen
sudo systemctl status mongod

# MongoDB starten
sudo systemctl start mongod
```

### Port-Konflikte
```bash
# Prozesse auf Port 3000/8002 beenden
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8002 | xargs kill -9
```

### Node.js/Yarn Probleme
```bash
# Yarn Cache leeren
yarn cache clean

# Node modules neu installieren
rm -rf node_modules yarn.lock
yarn install
```

### Python Virtual Environment Probleme
```bash
# Virtual Environment neu erstellen
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Log-Dateien

Nach dem Start finden Sie Log-Dateien in:
- Backend: `/app/emergent-next/backend/backend.log`
- Frontend: `/app/emergent-next/frontend/frontend.log`

## 🆘 Support

Bei Problemen prüfen Sie:

1. **System-Requirements** erfüllt?
2. **Alle Ports** (3000, 8002, 27017) verfügbar?
3. **MongoDB** läuft?
4. **Log-Dateien** auf Fehler prüfen

## 🎉 Features nach Installation

### ✅ Sofort verfügbar:
- Monaco Code Editor
- File Tree Navigation
- File Upload/Download (bis 250MB)
- Workspace Management
- REST API Endpoints

### 📝 Mit API Keys:
- AI-powered Chat (OpenAI, Anthropic, Perplexity)
- Code-Analyse Features
- AI-Code-Kommentare

### 🔮 Geplant:
- File Versioning
- Git Integration
- Real-time Collaboration
- Plugin System