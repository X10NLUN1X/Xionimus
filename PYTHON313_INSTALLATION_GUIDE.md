# 🚀 XIONIMUS AI - Python 3.13 Installation Guide

## ✅ Ihr System Update erkannt!

**Vorher:** Python 3.10.11 → **Jetzt:** Python 3.13.2032.0

**Aktueller Fehler:** `ModuleNotFoundError: No module named 'aiohttp'`

---

## 🔥 Sofortige 30-Sekunden Lösung

```batch
# Im backend\ Verzeichnis:
pip install aiohttp fastapi uvicorn motor pymongo anthropic openai python-dotenv

# Dann Backend starten:
python server.py
```

---

## 🛠️ Vollständige Installation (Empfohlen)

### Option 1: Quick Fix Script (Automatisch)
```batch
# Im XIONIMUS Hauptverzeichnis:
WINDOWS_QUICK_FIX_PYTHON313.bat
```

### Option 2: Manuelle Installation

#### Schritt 1: Python 3.13 Dependencies installieren
```batch
cd backend

# Python 3.13 optimierte Requirements:
pip install -r requirements_python313.txt

# ODER minimale Installation:
pip install aiohttp aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache
pip install fastapi uvicorn motor pymongo anthropic openai python-dotenv
pip install numpy pandas pydantic httpx
```

#### Schritt 2: .env Dateien prüfen/erstellen

**backend/.env:**
```env
MONGO_URL=mongodb://localhost:27017/xionimus_ai
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PERPLEXITY_API_KEY=
```

#### Schritt 3: System starten
```batch
# Backend (Terminal 1):
cd backend
python server.py

# Frontend (Terminal 2):  
cd frontend
yarn start
```

---

## 🎯 Python 3.13 Vorteile

### ✅ Was jetzt besser funktioniert:
- **Neueste numpy/pandas** Versionen verfügbar (numpy 2.2.1, pandas 2.2.3)
- **grpcio** funktioniert einwandfrei (war bei Python 3.10 problematisch)
- **Bessere Performance** durch Python 3.13 Optimierungen  
- **Alle AI Libraries** unterstützen Python 3.13 vollständig

### 📦 Neue Requirements-Dateien:
1. **`requirements_python313.txt`** - Vollständig für Python 3.13 optimiert
2. **`WINDOWS_QUICK_FIX_PYTHON313.bat`** - Automatische Reparatur
3. **Alte Dateien** (für andere Python Versionen):
   - `requirements_minimal_py310.txt` (Python 3.10)
   - `requirements_windows_py310.txt` (Python 3.10)

---

## 🔧 Der Hauptfehler war:

```python
# In dns_bypass.py Zeile 7:
import aiohttp  # ← Fehlte komplett!
```

**Warum ist das passiert?**
- Bei der ersten Installation wurden nicht alle Dependencies installiert
- `aiohttp` ist kritisch für das AI Orchestrator System
- Ohne `aiohttp` kann das Backend nicht starten

---

## 🧪 Installation testen

```batch
# 1. Dependencies prüfen:
python -c "import aiohttp; print('✅ aiohttp OK')"
python -c "import fastapi; print('✅ FastAPI OK')"  
python -c "import motor; print('✅ MongoDB OK')"

# 2. Backend Test:
curl http://localhost:8001/api/health

# 3. Frontend Test:
# Browser: http://localhost:3000
```

---

## 🛠️ Erweiterte Problembehandlung

### ❌ Falls weiterhin Import-Fehler:
```batch
# Alle Dependencies neu installieren:
pip uninstall -y aiohttp fastapi uvicorn motor
pip install aiohttp fastapi uvicorn motor pymongo

# Python Cache leeren:
python -Bc "import py_compile; py_compile.main()"
```

### ❌ Falls SSL/TLS Probleme (Windows):
```batch
pip install --trusted-host pypi.org --trusted-host pypi.python.org aiohttp
```

### ❌ Falls Permission Fehler:
```batch
# Als Administrator:
pip install --user aiohttp fastapi uvicorn motor pymongo
```

---

## 📊 Vollständiger Systemcheck

### ✅ Ihr aktueller Status:
- **Python:** 3.13.2032.0 ✅ (Neueste Version!)
- **Node.js:** v20.10.0 ✅
- **Windows:** Unterstützt ✅
- **XIONIMUS:** Backend läuft (nach aiohttp Fix) ✅

### 🔧 Nach erfolgreicher Installation:
- **9 AI-Agenten** verfügbar
- **Chat Interface** funktional
- **GitHub Integration** bereit  
- **Projekt Management** aktiviert
- **Modern Gold/Black UI** geladen

---

## 🚀 Start-Befehle

### Backend starten:
```batch
cd C:\AI\XionimusX-main\backend
python server.py
```

### Frontend starten:
```batch  
cd C:\AI\XionimusX-main\frontend
yarn start
```

### System öffnen:
```
http://localhost:3000
```

---

## 💡 Python 3.13 Optimierungen

**requirements_python313.txt** nutzt:
- **numpy==2.2.1** (neueste, Python 3.13 optimiert)
- **pandas==2.2.3** (beste Performance)
- **fastapi==0.115.6** (neueste Features)
- **aiohttp==3.11.10** (war der Hauptfehler!)
- **grpcio==1.68.1** (perfekte Python 3.13 Unterstützung)

---

**🎉 Mit Python 3.13 haben Sie die beste XIONIMUS AI Performance!**

**Der aiohttp-Fehler ist in 30 Sekunden behoben! 🚀**