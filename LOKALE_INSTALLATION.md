# 🖥️ XIONIMUS AI - LOKALE INSTALLATION (OHNE DOCKER)

## ⚠️ WICHTIG
Diese Anleitung installiert Xionimus AI komplett lokal auf Ihrem PC ohne Docker-Container.

## 📋 VORAUSSETZUNGEN INSTALLIEREN

### Windows:
1. **Node.js 18+**: https://nodejs.org (LTS Version)
2. **Python 3.9+**: https://python.org 
3. **MongoDB Community**: https://mongodb.com/try/download/community
4. **Git**: https://git-scm.com

### macOS:
```bash
brew install node@18 python@3.11 git
brew tap mongodb/brew && brew install mongodb-community
```

### Linux (Ubuntu/Debian):
```bash
# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python
sudo apt-get install python3 python3-pip

# MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update && sudo apt-get install -y mongodb-org

# Git
sudo apt-get install git
```

## 🚀 INSTALLATION

### Schritt 1: Repository klonen
```bash
git clone https://github.com/X10NLUN1X/Xionimus.git
cd Xionimus
```

### Schritt 2: Frontend einrichten
```bash
cd frontend

# .env Datei erstellen (KRITISCH!)
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
EOF

# Dependencies installieren
npm install -g yarn
yarn install

cd ..
```

### Schritt 3: Backend einrichten
```bash
cd backend

# .env Datei erstellen (KRITISCH!)
cat > .env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# AI API Keys - Direct API Integration
# Get your Perplexity API key from: https://www.perplexity.ai/settings/api (format: pplx-...)
# PERPLEXITY_API_KEY=pplx-your_perplexity_key_here

# Get your Anthropic API key from: https://console.anthropic.com/ (format: sk-ant-...)
# ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
EOF

# Dependencies installieren
pip install -r requirements.txt

cd ..
```

## 🔥 SERVICES STARTEN (3 TERMINALS)

### Terminal 1: MongoDB starten
```bash
# Windows (als Administrator)
mongod --dbpath C:\data\db

# macOS
brew services start mongodb/brew/mongodb-community

# Linux
sudo systemctl start mongod
```

### Terminal 2: Backend starten
```bash
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 3: Frontend starten
```bash
cd frontend
yarn start
```

## ✅ TESTEN

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8001/api/health
3. **MongoDB**: sollte auf Port 27017 laufen

### API-Test:
```bash
curl http://localhost:8001/api/health
# Sollte: {"status":"healthy",...} zurückgeben
```

## 🔑 API KEYS KONFIGURIEREN

1. **Perplexity API Key holen:**
   - Gehen Sie zu: https://www.perplexity.ai/settings/api
   - Erstellen Sie einen Key (Format: `pplx-...`)

2. **Anthropic API Key holen:**
   - Gehen Sie zu: https://console.anthropic.com/
   - Erstellen Sie einen Key (Format: `sk-ant-...`)

3. **Keys eintragen:**
```bash
# Bearbeiten Sie backend/.env:
nano backend/.env  # oder einen anderen Editor

# Uncomment und ersetzen Sie:
PERPLEXITY_API_KEY=pplx-your_actual_key_here
ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
```

4. **Backend neu starten** (Terminal 2):
```bash
# Ctrl+C um zu stoppen, dann:
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## 🔧 PROBLEMBEHANDLUNG

### "Fehler beim Laden der Projekte":
- ✅ Prüfen Sie `frontend/.env` → `REACT_APP_BACKEND_URL=http://localhost:8001`
- ✅ Backend läuft auf Port 8001
- ✅ Browser-Cache leeren (Ctrl+F5)

### Port bereits belegt:
```bash
# Port 3000 freigeben
sudo lsof -ti:3000 | xargs kill -9

# Port 8001 freigeben  
sudo lsof -ti:8001 | xargs kill -9
```

### MongoDB startet nicht:
```bash
# Windows: MongoDB als Service installieren
# macOS: brew services restart mongodb/brew/mongodb-community
# Linux: sudo systemctl restart mongod
```

### Dependencies Fehler:
```bash
# Node.js Version prüfen
node --version  # Sollte v18.x.x oder höher sein

# Python Version prüfen
python --version  # Sollte 3.9.x oder höher sein

# Yarn installieren falls fehlt
npm install -g yarn
```

### API Keys funktionieren nicht:
- ✅ Keys haben korrekte Formate (`pplx-...` und `sk-ant-...`)
- ✅ Keys sind uncommented in `backend/.env`
- ✅ Backend wurde nach Key-Änderung neu gestartet
- ✅ Keys sind gültig und haben ausreichend Credits

## 🎯 VORTEILE LOKALER INSTALLATION

✅ **API Keys persistent gespeichert**
✅ **Volle Kontrolle über alle Services**  
✅ **Kein Docker-Overhead**
✅ **Direkter Dateisystem-Zugriff**
✅ **Einfaches Debugging**
✅ **Keine Container-Netzwerk-Probleme**

## 🔄 SERVICES STOPPEN

```bash
# Alle Terminals: Ctrl+C

# MongoDB stoppen:
# Windows: Ctrl+C im mongod Terminal
# macOS: brew services stop mongodb/brew/mongodb-community  
# Linux: sudo systemctl stop mongod
```