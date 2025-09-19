# 🤖 XIONIMUS AI - Windows Native Installation

## ⚡ SCHNELL-INSTALLATION (3 Schritte)

1. **Als Administrator ausführen:**
   ```batch
   WINDOWS_INSTALL.bat
   ```

2. **System starten (2 Doppelklicks):**
   - `START_BACKEND.bat`
   - `START_FRONTEND.bat`

3. **Fertig!** Frontend öffnet automatisch: http://localhost:3000

---

## 📋 SYSTEM REQUIREMENTS

- **Windows 10/11**
- **MongoDB Compass** (für Datenverwaltung)
- **Internet-Verbindung** (für automatische Installation)

**Alles andere wird automatisch installiert:** Python, Node.js, Dependencies

---

## 🎯 WAS PASSIERT

### **WINDOWS_INSTALL.bat macht:**
✅ Python 3.11 automatisch installieren  
✅ Node.js 20 LTS automatisch installieren  
✅ MongoDB Verzeichnisse erstellen  
✅ Alle Dependencies installieren  
✅ Lokale Windows-Konfiguration  

### **Nach Installation verfügbar:**
✅ **START_BACKEND.bat** - Backend Server (Port 8001)  
✅ **START_FRONTEND.bat** - Frontend Server (Port 3000 + Auto-Browser)  
✅ **MongoDB Compass** - Datenbank GUI (`mongodb://localhost:27017`)  

---

## 🔑 API KEYS (Optional)

**Für AI-Funktionen:**
1. **Perplexity:** https://www.perplexity.ai/settings/api  
2. **Anthropic:** https://console.anthropic.com/  
3. **Keys in `backend\.env` eintragen**
4. **Backend neu starten**

---

## 🗃️ DATENBANK

**MongoDB Compass Verbindung:**
- **Connection String:** `mongodb://localhost:27017`
- **Database:** `xionimus_ai` (automatisch erstellt)
- **Collections:** `projects`, `chat_sessions`, `uploaded_files`

---

## 🎉 FERTIG!

Nach der Installation haben Sie:
- **Voll funktionsfähiges AI-System**
- **Lokale Datenspeicherung** 
- **Visuelle Datenbank-Verwaltung**
- **Keine Docker-Container**
- **Native Windows-Performance**

**Detaillierte Anleitung: `WINDOWS_README.md`**

---

## 🔧 **MANUELLE INSTALLATION**

### **Schritt 1: Abhängigkeiten installieren**

```bash
# Backend-Abhängigkeiten
cd backend
pip install -r requirements.txt
cd ..

# Frontend-Abhängigkeiten
cd frontend
yarn install
cd ..
```

### **Schritt 2: Umgebungsvariablen konfigurieren**

#### **Backend (.env)**
```bash
# /app/backend/.env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# Optional: API-Schlüssel (können auch später in der UI hinzugefügt werden)
# PERPLEXITY_API_KEY=your_perplexity_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# GITHUB_TOKEN=your_github_token_here
```

#### **Frontend (.env)**
```bash
# /app/frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_HOST=localhost
WDS_SOCKET_PORT=3000
```

### **Schritt 3: Services starten**

```bash
# MongoDB starten (falls nicht mit Docker)
mongod --dbpath ./data/db

# Backend starten
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Frontend starten (neues Terminal)
cd frontend
yarn start
```

---

## 🐳 **DOCKER INSTALLATION (Empfohlen)**

### **docker-compose.yml bereits konfiguriert:**

```bash
# Alles mit einem Befehl starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Services stoppen
docker-compose down
```

---

## 🤖 **AGENTEN-SYSTEM ÜBERSICHT**

### **8 Spezialisierte Agenten:**

| Agent | AI-Engine | Spezialisierung |
|-------|-----------|----------------|
| **Code Agent** | Claude | Programmierung, Debugging, Code-Analyse |
| **Research Agent** | Perplexity | Web-Recherche, aktuelle Informationen |
| **Writing Agent** | Claude | Dokumentation, Content-Erstellung |
| **Data Agent** | Claude | Datenanalyse, Visualisierung |
| **QA Agent** | Perplexity | Testing, Quality Assurance |
| **GitHub Agent** | Perplexity | Repository-Management, Version Control |
| **File Agent** | Claude | File Upload/Management, Organisation |
| **Session Agent** | Claude | Session Fork/Backup, State Management |

### **Automatische Agent-Auswahl:**
- **Code-Anfragen** → Code Agent (Claude)
- **Research-Anfragen** → Research Agent (Perplexity)
- **Dokumentation** → Writing Agent (Claude)
- **Datenanalyse** → Data Agent (Claude)
- **Testing** → QA Agent (Perplexity)
- **GitHub** → GitHub Agent (Perplexity)
- **Normale Unterhaltung** → Perplexity (Standard)

---

## 🔑 **API-SCHLÜSSEL KONFIGURATION**

### **In der UI konfigurieren:**
1. Klicken Sie auf das ⚙️ **Settings-Icon**
2. Geben Sie Ihre API-Schlüssel ein:
   - **Perplexity API Key**: `pplx-...`
   - **Anthropic API Key**: `sk-ant-...`
   - **GitHub Token**: `ghp_...` (optional)

### **API-Schlüssel erhalten:**

#### **Perplexity API:**
- Website: https://www.perplexity.ai/settings/api
- Kosten: ~$5-20/Monat je nach Nutzung
- Verwendet für: Recherche, QA, GitHub, normale Unterhaltung

#### **Anthropic Claude:**
- Website: https://console.anthropic.com/
- Kosten: ~$10-50/Monat je nach Nutzung
- Verwendet für: Code, Writing, Data Analysis, File Management

#### **GitHub Token (Optional):**
- GitHub → Settings → Developer settings → Personal access tokens
- Scopes: `repo`, `user`, `gist`
- Verwendet für: Repository-Management, Code-Upload

---

## 🎮 **FEATURES & FUNKTIONEN**

### **💬 Chat-System**
- **Intelligente Agent-Auswahl** basierend auf Anfrage-Typ
- **Mehrsprachige Unterstützung** (Deutsch, Englisch, Spanisch, Französisch)
- **Automatische Spracherkennung**
- **Conversation Memory** mit Verlauf

### **💻 Code-Entwicklung**
- **Code-Generierung** in allen Programmiersprachen
- **Code-Analyse** und Optimierung
- **Debugging-Unterstützung**
- **Monaco Editor** mit Syntax-Highlighting

### **📁 Projekt-Management**
- **Vollständige CRUD-Operationen** für Projekte
- **Datei-Management** mit Upload/Download
- **Code-Organisation** nach Projekten
- **Automatische Backups**

### **🔗 GitHub Integration**
- **Repository-Management**: Listen, Erstellen, Klonen
- **Commit-Operationen**: Push, Pull, Merge
- **Branch-Management**: Erstellen, Wechseln, Mergen
- **Datei-Operationen**: Upload, Download, Bearbeiten

### **📂 File Management**
- **Drag & Drop Upload** für alle Dateitypen
- **Automatische Organisation** nach Typ/Datum
- **Datei-Analyse** und Vorschau
- **Archivierung** mit ZIP-Kompression

### **🍴 Session Fork System**
- **Vollständige Session-Backups** mit allen Daten
- **Ein-Klick Wiederherstellung** von Sessions
- **Export/Import** von Sessions
- **Projekt-State Preservation**

---

## 📱 **BENUTZEROBERFLÄCHE**

### **Dystopisches Cyberpunk Design:**
- **Matrix-Style Hintergrund** mit Scanlines
- **Terminal-Ästhetik** mit grün-rot-violetter Farbpalette
- **Glitch-Effekte** und Animationen
- **Responsive Design** für alle Bildschirmgrößen

### **Navigation:**
- **CHAT**: Unterhaltung mit AI-Agenten
- **CODE**: Code-Entwicklung und -Analyse
- **PROJ**: Projekt-Management
- **GIT**: GitHub-Integration
- **FILES**: Datei-Management
- **FORK**: Session-Management

---

## 🛠️ **PROBLEMBEHANDLUNG**

### **Häufige Probleme:**

#### **"Connection refused" Fehler:**
```bash
# Überprüfen Sie die Ports
netstat -tulpn | grep :8001
netstat -tulpn | grep :3000

# Services neu starten
docker-compose restart
```

#### **"API Key not configured" Fehler:**
- Gehen Sie zu Settings (⚙️) und fügen Sie Ihre API-Schlüssel hinzu
- Überprüfen Sie die .env-Dateien
- Starten Sie das Backend neu nach Änderungen

#### **MongoDB-Verbindungsfehler:**
```bash
# MongoDB-Status prüfen
docker-compose logs mongodb

# Datenbank zurücksetzen (falls nötig)
docker-compose down -v
docker-compose up -d
```

#### **Frontend lädt nicht:**
```bash
# Node-Module neu installieren
cd frontend
rm -rf node_modules
yarn install
yarn start
```

### **Debug-Modi:**

#### **Backend-Logs:**
```bash
# Docker
docker-compose logs -f backend

# Manuell
tail -f backend/logs/app.log
```

#### **Frontend-Logs:**
- Öffnen Sie Browser Developer Tools (F12)
- Überprüfen Sie Console und Network Tabs

---

## 🔒 **SICHERHEIT**

### **Empfohlene Sicherheitsmaßnahmen:**
- **API-Schlüssel** niemals in Git committen
- **Firewall** für Produktionsumgebungen konfigurieren
- **HTTPS** für öffentliche Deployments verwenden
- **Regelmäßige Updates** der Abhängigkeiten

### **Umgebungsvariablen sicher verwalten:**
```bash
# .env-Dateien zu .gitignore hinzufügen
echo "*.env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## 📊 **SYSTEM-REQUIREMENTS**

### **Minimum:**
- **RAM**: 4GB
- **Storage**: 10GB freier Speicherplatz
- **CPU**: 2 Kerne
- **Netzwerk**: Internetverbindung für AI-APIs

### **Empfohlen:**
- **RAM**: 8GB oder mehr
- **Storage**: 50GB SSD
- **CPU**: 4+ Kerne
- **Netzwerk**: Breitband-Internet

---

## 🔄 **UPDATES**

### **System aktualisieren:**
```bash
# Repository aktualisieren
git pull origin main

# Abhängigkeiten aktualisieren
cd backend && pip install -r requirements.txt
cd ../frontend && yarn install

# Docker-Images neu erstellen
docker-compose build --no-cache
docker-compose up -d
```

---

## 🤝 **SUPPORT & COMMUNITY**

### **Hilfe erhalten:**
- **GitHub Issues**: Bug-Reports und Feature-Requests
- **Discord Community**: Echtzeit-Support
- **Wiki**: Detaillierte Dokumentation
- **Video-Tutorials**: YouTube-Kanal

### **Beitragen:**
- **Fork** das Repository
- **Erstellen** Sie einen Feature-Branch
- **Commiten** Sie Ihre Änderungen
- **Erstellen** Sie einen Pull Request

---

## 📄 **LIZENZ**

MIT License - Siehe [LICENSE](LICENSE) Datei für Details.

---

## 🎯 **ERSTE SCHRITTE**

1. **Installation abschließen** (siehe oben)
2. **API-Schlüssel konfigurieren** (Settings-Menü)
3. **Erstes Projekt erstellen** (PROJ Tab)
4. **Code generieren lassen** (CODE Tab)
5. **Session forken** für Backup (FORK Tab)

---

**> SYSTEM READY. NEURAL NETWORK ONLINE. PROCEED WITH CAUTION.**

```
[XIONIMUS_AI] Initialisierung abgeschlossen...
[STATUS] Alle Agenten operationsbereit
[WARNING] Autonome KI aktiv - Überwachung empfohlen
```