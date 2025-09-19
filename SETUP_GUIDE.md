# 🚀 XIONIMUS AI - SETUP GUIDE (LOKAL)

## ⚠️ WICHTIGER HINWEIS
Das GitHub-Repository enthält keine `.env` Dateien (Sicherheit). Sie müssen diese manuell erstellen.

## 📋 INSTALLATIONSSCHRITTE

### **1. Repository klonen**
```bash
git clone https://github.com/X10NLUN1X/Xionimus.git
cd Xionimus
```

### **2. Umgebungsvariablen erstellen**

**Frontend .env erstellen:**
```bash
cd frontend
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
EOF
cd ..
```

**Backend .env erstellen:**
```bash
cd backend  
cat > .env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# AI API Keys - Direct API Integration (No emergentintegrations dependency)
# Get your Perplexity API key from: https://www.perplexity.ai/settings/api (format: pplx-...)
# PERPLEXITY_API_KEY=pplx-your_perplexity_key_here

# Get your Anthropic API key from: https://console.anthropic.com/ (format: sk-ant-...)  
# ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
EOF
cd ..
```

### **3. Dependencies installieren**
```bash
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend  
cd frontend
yarn install
cd ..
```

### **4. Services starten (3 separate Terminals)**

**Terminal 1 - MongoDB:**
```bash
mongod
```

**Terminal 2 - Backend:**
```bash
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 3 - Frontend:**
```bash
cd frontend
yarn start
```

### **5. Testen**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api/health

### **6. API Keys konfigurieren**
1. Öffnen Sie http://localhost:3000
2. Klicken Sie auf ⚙️ (Settings)
3. Fügen Sie Ihre API Keys hinzu:
   - **Perplexity**: `pplx-...` (von https://www.perplexity.ai/settings/api)
   - **Anthropic**: `sk-ant-...` (von https://console.anthropic.com/)

## 🎯 WICHTIGE FIXES ANGEWENDET

✅ **Frontend URL korrigiert**: Von Emergent-Server zu `http://localhost:8001`  
✅ **Emergentintegrations entfernt**: Direkte API-Clients verwenden  
✅ **API Key System**: Funktioniert mit offiziellen Keys  
✅ **Alle 8 Agents**: Verfügbar und funktionsfähig  

## 🔧 PROBLEMBEHANDLUNG

**Port bereits belegt:**
```bash
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
```

**MongoDB nicht gefunden:**
```bash
# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongodb

# macOS  
brew install mongodb/brew/mongodb-community
brew services start mongodb/brew/mongodb-community
```

**Node.js/Yarn nicht gefunden:**
```bash
# Node.js 18+ installieren von https://nodejs.org
# Yarn installieren
npm install -g yarn
```