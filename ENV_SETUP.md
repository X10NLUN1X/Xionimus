# 🔧 ENVIRONMENT SETUP - KRITISCHE KONFIGURATION

## ⚠️ WICHTIGER HINWEIS
**Das GitHub Repository enthält keine .env Dateien (Sicherheitsgründe). Diese müssen manuell erstellt werden!**

## 📁 FRONTEND .ENV ERSTELLEN

**Datei:** `frontend/.env`
```bash
cd frontend
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
EOF
```

## 📁 BACKEND .ENV ERSTELLEN

**Datei:** `backend/.env`
```bash
cd backend
cat > .env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# AI API Keys - Direct API Integration (No emergentintegrations)
# Get your Perplexity API key from: https://www.perplexity.ai/settings/api (format: pplx-...)
# PERPLEXITY_API_KEY=pplx-your_perplexity_key_here

# Get your Anthropic API key from: https://console.anthropic.com/ (format: sk-ant-...)
# ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
EOF
```

## 🚀 SCHNELL-SETUP SKRIPT

```bash
#!/bin/bash
echo "=== XIONIMUS AI - ENV SETUP ==="

# Frontend .env
echo "Creating frontend/.env..."
cat > frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
EOF

# Backend .env
echo "Creating backend/.env..."
cat > backend/.env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# AI API Keys - Direct API Integration
# PERPLEXITY_API_KEY=pplx-your_key_here
# ANTHROPIC_API_KEY=sk-ant-your_key_here
EOF

echo "✅ Environment files created!"
echo "⚠️  Remember to add your API keys to backend/.env"
```

## 🔑 API KEYS KONFIGURIEREN

Nach der Installation:
1. **Perplexity API Key:** https://www.perplexity.ai/settings/api (Format: `pplx-...`)
2. **Anthropic API Key:** https://console.anthropic.com/ (Format: `sk-ant-...`)
3. Uncomment die Lines in `backend/.env` und fügen Sie Ihre Keys ein

## ⚡ INSTALLATION MIT ENV SETUP

```bash
# 1. Repository klonen
git clone <repository-url>
cd xionimus-ai

# 2. ENV Dateien erstellen (KRITISCH!)
bash ENV_SETUP.md  # Oder manuell die .env Dateien erstellen

# 3. Dependencies installieren
cd backend && pip install -r requirements.txt && cd ..
cd frontend && yarn install && cd ..

# 4. Services starten
# Terminal 1: mongod
# Terminal 2: cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
# Terminal 3: cd frontend && yarn start
```

## 🔍 PROBLEMBEHANDLUNG

**"Fehler beim Laden der Projekte":**
- ✅ Prüfen Sie `frontend/.env` → `REACT_APP_BACKEND_URL=http://localhost:8001`
- ✅ Backend läuft auf Port 8001
- ✅ Browser-Cache leeren (Ctrl+F5)

**API Key Fehler:**
- ✅ Prüfen Sie `backend/.env` → API Keys uncommented und korrekt
- ✅ Gültige Keys verwenden (pplx-... und sk-ant-...)