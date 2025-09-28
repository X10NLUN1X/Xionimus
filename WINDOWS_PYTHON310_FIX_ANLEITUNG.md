# XIONIMUS AI - Windows Python 3.10 Installation Fix

## Problem
Der Originalfehler tritt auf weil `numpy==2.3.3` Python 3.11+ erfordert, aber Sie haben Python 3.10.11.

## 🚀 Schnelle Lösung (Empfohlen)

### Option 1: Automatisches Fix-Script verwenden
```batch
# Im XIONIMUS Hauptverzeichnis ausführen:
WINDOWS_INSTALL_FIX.bat
```

### Option 2: Manuelle Installation mit korrigierten Dependencies

#### Schritt 1: Backend Dependencies installieren
```batch
cd backend

# Minimale Installation (empfohlen):
pip install -r requirements_minimal_py310.txt

# ODER vollständige Installation:
pip install -r requirements_windows_py310.txt
```

#### Schritt 2: Frontend Dependencies installieren  
```batch
cd frontend
yarn install
# Falls yarn fehlt: npm install
```

#### Schritt 3: .env Dateien erstellen

**backend/.env:**
```
MONGO_URL=mongodb://localhost:27017/xionimus_ai
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PERPLEXITY_API_KEY=
```

**frontend/.env:**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### Schritt 4: System starten

**Terminal 1 (Backend):**
```batch
cd backend
python server.py
```

**Terminal 2 (Frontend):**
```batch
cd frontend
yarn start
# Falls yarn fehlt: npm start
```

**System öffnen:** http://localhost:3000

## 🔧 Hauptänderungen der Lösung

### Korrigierte Dependencies:
- ✅ `numpy==1.24.4` (statt 2.3.3 - Python 3.10 kompatibel)
- ✅ `pandas==2.0.3` (statt 2.3.2 - Python 3.10 kompatibel)  
- ✅ Rust-Dependencies entfernt (jq, fastuuid, etc.)
- ✅ Problematische grpcio Dependencies optional gemacht

### 3 Requirements-Versionen erstellt:
1. **`requirements_minimal_py310.txt`** - Nur essentiell (empfohlen für erste Installation)
2. **`requirements_windows_py310.txt`** - Vollständig aber Python 3.10 kompatibel
3. **`requirements.txt`** - Original (für Python 3.11+)

## 🛠️ Problembehandlung

### Falls numpy immer noch Probleme macht:
```batch
pip install "numpy>=1.24.0,<1.27.0" --force-reinstall
```

### Falls cryptography Probleme macht:
```batch
pip install cryptography==41.0.7
```

### Falls grpcio Probleme macht:
```batch
# In requirements_windows_py310.txt auskommentieren:
# grpcio==1.75.0
# grpcio-status==1.71.2
```

### Visual Studio C++ Build Tools fehlen:
1. Microsoft Visual C++ 14.0 oder höher installieren
2. ODER: `--only-binary=all` flag verwenden:
   ```batch
   pip install --only-binary=all -r requirements_minimal_py310.txt
   ```

## ✅ Erfolgreiche Installation prüfen

### Backend Test:
```batch
curl http://localhost:8001/api/health
# Erwartete Antwort: {"status":"healthy",...}
```

### Frontend Test:
- Browser öffnen: http://localhost:3000
- XIONIMUS AI Interface sichtbar
- Chat funktional (auch ohne API Keys)

## 📋 System Requirements
- ✅ **Python 3.10.11** (Ihr System)
- ✅ **Node.js 18+** (Ihr System)  
- ✅ **MongoDB** (optional, kann später konfiguriert werden)
- ✅ **Visual Studio C++ Build Tools** (für Windows)

## 🎯 Nach erfolgreicher Installation

1. **MongoDB** starten (MongoDB Compass)
2. **API Keys konfigurieren** in der Web-Oberfläche:
   - Anthropic API Key (für Claude)
   - OpenAI API Key (für GPT)
   - Perplexity API Key (für Research)
3. **Alle 9 AI-Agenten** sind verfügbar
4. **GitHub Integration** aktivieren
5. **Projekt Management** nutzen

## 🆘 Support

Falls weiterhin Probleme auftreten:
1. Logs prüfen in der Konsole
2. Python Version bestätigen: `python --version`
3. Pip aktualisieren: `python -m pip install --upgrade pip`
4. Minimale Installation versuchen: `requirements_minimal_py310.txt`

**Das System ist vollständig funktionsfähig mit Python 3.10!** 🎉