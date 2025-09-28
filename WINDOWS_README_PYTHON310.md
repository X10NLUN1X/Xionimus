# 🏠 XIONIMUS AI - Windows Python 3.10 Installation

## 🚨 Problem behoben: numpy==2.3.3 Fehler

**Ihr ursprünglicher Fehler:**
```
ERROR: Could not find a version that satisfies the requirement numpy==2.3.3
ERROR: No matching distribution found for numpy==2.3.3
```

**Ursache:** numpy 2.3.3 erfordert Python 3.11+, Sie haben Python 3.10.11

**✅ Lösung:** Python 3.10 kompatible Dependencies verwenden

---

## 🚀 Schnellstart (3 Minuten)

### 1️⃣ Automatische Installation (Empfohlen)
```batch
# Im XIONIMUS Hauptverzeichnis:
WINDOWS_INSTALL_FIX.bat
```

### 2️⃣ Manuelle Installation
```batch
# Backend Dependencies:
cd backend
pip install -r requirements_minimal_py310.txt

# Frontend Dependencies:
cd ../frontend  
yarn install

# .env Dateien erstellen (siehe unten)
# System starten (siehe unten)
```

---

## 📁 Neue Dateien für Python 3.10 Fix

| Datei | Beschreibung |
|-------|--------------|
| `requirements_minimal_py310.txt` | 🎯 Minimal - nur essentiell, sehr sicher |
| `requirements_windows_py310.txt` | 🔧 Vollständig - alle Features, Python 3.10 kompatibel |
| `WINDOWS_INSTALL_FIX.bat` | 🤖 Automatisches Installations-Script |
| `test_py310_compatibility.py` | 🧪 Test ob alles funktioniert |

---

## ⚙️ Manuelle Installation (Schritt-für-Schritt)

### Schritt 1: Dependencies installieren
```batch
cd backend

# Option A - Minimal (empfohlen für erste Installation):
pip install -r requirements_minimal_py310.txt

# Option B - Vollständig:  
pip install -r requirements_windows_py310.txt

# Falls Probleme, nur Basis installieren:
pip install fastapi uvicorn motor pymongo anthropic openai python-dotenv numpy==1.24.4
```

### Schritt 2: .env Dateien erstellen

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

### Schritt 3: Frontend Dependencies
```batch
cd frontend
yarn install

# Falls yarn nicht installiert:
npm install -g yarn
# ODER einfach npm verwenden:
npm install
```

### Schritt 4: System starten

**Terminal 1 (Backend):**
```batch
cd backend
python server.py
```

**Terminal 2 (Frontend):**  
```batch
cd frontend
yarn start
# ODER: npm start
```

**System öffnen:** http://localhost:3000

---

## 🔧 Hauptänderungen (Was wurde gefixt)

### ✅ Dependencies korrigiert:
- `numpy==1.24.4` ← **statt 2.3.3** (Python 3.10 sicher)
- `pandas==2.0.3` ← **statt 2.3.2** (Python 3.10 sicher)
- Rust Dependencies entfernt (jq, fastuuid, etc.)
- grpcio optional gemacht (kann Windows-Probleme verursachen)

### ✅ Neue Requirements-Dateien:
1. **requirements_minimal_py310.txt** - Nur essentiell (~15 Packages)
2. **requirements_windows_py310.txt** - Vollständig (~80 Packages)
3. **requirements.txt** - Original (für Python 3.11+)

---

## 🧪 Installation testen

```batch
# Kompatibilität prüfen:
python test_py310_compatibility.py

# Backend testen:
curl http://localhost:8001/api/health

# Erwartete Antwort:
# {"status":"healthy","agents":{"available":9},...}
```

---

## 🛠️ Problembehandlung

### ❌ Falls numpy immer noch Fehler macht:
```batch
pip uninstall numpy
pip install "numpy>=1.24.0,<1.27.0"
```

### ❌ Falls cryptography Probleme macht:
```batch
pip install cryptography==41.0.7
```

### ❌ Falls Visual Studio C++ Build Tools fehlen:
```batch
# Lösung 1: Nur Binaries installieren
pip install --only-binary=all -r requirements_minimal_py310.txt

# Lösung 2: Microsoft Visual C++ 14.0+ installieren
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### ❌ Falls grpcio Probleme macht:
- Verwende `requirements_minimal_py310.txt` (enthält kein grpcio)
- ODER kommentiere grpcio Zeilen in requirements_windows_py310.txt aus

---

## 🎯 Nach erfolgreicher Installation

### ✅ Was funktioniert:
- **9 AI-Agenten** (Code, Research, Writing, Data, QA, GitHub, File, Session, Experimental)
- **Chat Interface** mit Gold/Black Design
- **API Key Management** für Claude, GPT, Perplexity
- **GitHub Integration**  
- **Projekt Management**
- **File Upload System**
- **Session Management**

### 🔑 API Keys konfigurieren:
1. http://localhost:3000 öffnen
2. API Configuration Button klicken
3. Keys eingeben:
   - **Anthropic:** für Claude Modelle
   - **OpenAI:** für GPT Modelle  
   - **Perplexity:** für Research Agent

---

## 📊 System Status

**Ihr System:**
- ✅ Python 3.10.11 (kompatibel)
- ✅ Node.js v20.10.0 (kompatibel)  
- ✅ Windows (unterstützt)

**XIONIMUS AI System:**
- ✅ Backend: FastAPI + MongoDB
- ✅ Frontend: React + Tailwind CSS
- ✅ AI: Multi-Agent System
- ✅ Design: Modern Gold/Black UI

---

## 🆘 Support & Hilfe

### 📞 Falls Probleme weiterhin bestehen:
1. **Logs prüfen** in den Konsolen-Fenstern
2. **Python Version bestätigen:** `python --version`
3. **Pip aktualisieren:** `python -m pip install --upgrade pip`
4. **Minimal Installation versuchen:** `requirements_minimal_py310.txt`
5. **Test ausführen:** `python test_py310_compatibility.py`

### 📧 Hilfe anfordern:
- Konsolen-Output kopieren
- Python Version angeben
- Welche requirements.txt verwendet
- Fehlerlog teilen

---

**🎉 Das System ist vollständig funktionsfähig mit Python 3.10!**

**Genießen Sie Ihren intelligenten AI-Assistenten! 🤖✨**