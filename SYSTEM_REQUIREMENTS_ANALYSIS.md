# XIONIMUS AI v3.0.0 - Systemvoraussetzungen & Debugging

## 🔧 **SYSTEMVORAUSSETZUNGEN**

### **Software-Anforderungen:**

#### **Python (Backend):**
- **Version:** Python 3.10.0 oder höher (getestet mit 3.11+)
- **Installation:** https://python.org/downloads/
- **Validierung:** `python --version` oder `python3 --version`
- **Package Manager:** pip (automatisch mit Python installiert)
- **Kritisch:** Muss im System PATH verfügbar sein

#### **Node.js (Frontend):**
- **Version:** Node.js 18.0.0 oder höher
- **Installation:** https://nodejs.org/
- **Validierung:** `node --version`
- **NPM:** Automatisch mit Node.js installiert
- **Kritisch:** NPM muss im System PATH verfügbar sein

#### **MongoDB (Database):**
- **Version:** MongoDB 4.4+ (läuft lokal oder als Service)
- **Standard-Port:** 27017
- **Connection:** mongodb://localhost:27017/xionimus_ai
- **Alternative:** Supervisor-verwalteter lokaler Service

### **Hardware-Anforderungen:**
- **RAM:** Mindestens 4GB (8GB empfohlen)
- **Speicher:** Mindestens 2GB freier Speicherplatz
- **CPU:** Moderne Multi-Core CPU empfohlen
- **Internet:** Für NPM/pip Downloads und AI API-Calls

### **Betriebssystem-Unterstützung:**
- **Windows:** 10/11 (für .bat Skripte)
- **Linux/macOS:** Alle modernen Versionen (für .sh Skripte)
- **Berechtigungen:** Schreibrechte im Projektverzeichnis

### **Globale Package-Anforderungen:**

#### **Python Packages (Global):**
```bash
# Nur pip sollte global verfügbar sein
python -m pip --version
```

#### **Node.js Packages (Global):**
```bash
# Keine globalen Packages erforderlich
# NPM sollte ausreichen
npm --version
```

### **Netzwerk-Anforderungen:**
- **Ausgehend HTTPS:** Für NPM Registry (registry.npmjs.org)
- **Ausgehend HTTPS:** Für PyPI (pypi.org)
- **Ausgehend HTTPS:** Für AI APIs (OpenAI, Anthropic, Perplexity)
- **Lokal:** Ports 3000 (Frontend) und 8001 (Backend) verfügbar

## 📁 **ERWARTETE DATEI-/ORDNERSTRUKTUR**

### **Projektwurzel:**
```
XionimusX-main/
├── backend/
│   ├── main.py              # ✓ KRITISCH - Neue Hauptdatei
│   ├── requirements.txt     # ✓ KRITISCH
│   ├── .env                # ✓ KRITISCH
│   ├── core/               # ✓ Neue Architektur
│   ├── api/                # ✓ Neue Architektur
│   └── uploads/            # ✓ Wird automatisch erstellt
├── frontend/
│   ├── package.json        # ✓ KRITISCH - Neue Dependencies
│   ├── .env                # ✓ KRITISCH
│   ├── vite.config.ts      # ✓ Neue Build-Konfiguration
│   ├── src/                # ✓ TypeScript Quellcode
│   └── node_modules/       # ✓ Wird durch NPM erstellt
├── install.sh              # ✓ Linux/macOS Installation
├── INSTALL_V3.bat          # ✓ Windows Installation (einfach)
├── WINDOWS_INSTALL.bat     # ✓ Windows Installation (umfassend)
├── START_BACKEND.bat       # ✓ Windows Backend Start
├── START_FRONTEND.bat      # ✓ Windows Frontend Start
├── START_ALL.bat          # ✓ Windows Beide Services
├── package.json           # ✓ Projekt-weite NPM Scripts
└── README_V3.md           # ✓ Dokumentation
```

### **Automatisch erstellte Verzeichnisse:**
- `backend/uploads/` (File Upload Storage)
- `frontend/node_modules/` (NPM Dependencies)
- `frontend/dist/` (Production Build)

## 🔑 **UMGEBUNGSVARIABLEN**

### **Backend (.env):**
```env
# Database
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# AI API Keys (optional bei Installation)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### **Frontend (.env):**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🛠️ **MANUELLE VORBEREITUNGSSCHRITTE**

### **1. Systemsoftware installieren:**
```bash
# Windows:
1. Python 3.10+ von python.org installieren
2. Node.js 18+ von nodejs.org installieren
3. Beide zu System PATH hinzufügen

# Linux/macOS:
sudo apt update && sudo apt install python3 python3-pip nodejs npm  # Ubuntu
brew install python node  # macOS
```

### **2. Berechtigungen prüfen:**
```bash
# Schreibrechte im Projektverzeichnis
echo test > test_write.tmp && del test_write.tmp  # Windows
echo test > test_write.tmp && rm test_write.tmp   # Linux/macOS
```

### **3. Ports freigeben:**
```bash
# Prüfe ob Ports verfügbar sind
netstat -an | findstr :3000  # Windows
netstat -an | grep :3000     # Linux/macOS
netstat -an | findstr :8001  # Windows  
netstat -an | grep :8001     # Linux/macOS
```

### **4. Firewall/Antivirus:**
- Ports 3000 und 8001 für lokale Verbindungen freigeben
- Python.exe und node.exe in Antivirus-Whitelist
- Projektverzeichnis von Echtzeit-Scanning ausschließen

## 📦 **DEPENDENCY-MATRIX**

### **Backend Dependencies (requirements.txt):**
| Package | Version | Zweck | Kritisch |
|---------|---------|-------|----------|
| fastapi | 0.115.6 | Web Framework | ✅ JA |
| uvicorn | 0.32.1 | ASGI Server | ✅ JA |
| motor | 3.3.1 | MongoDB Driver | ✅ JA |
| openai | 1.57.4 | OpenAI API | ⚠️ Optional |
| anthropic | 0.40.0 | Claude API | ⚠️ Optional |
| httpx | 0.28.1 | HTTP Client | ⚠️ Optional |
| pydantic | 2.10.3 | Data Validation | ✅ JA |
| python-dotenv | 1.1.1 | Environment Variables | ✅ JA |

### **Frontend Dependencies (package.json):**
| Package | Version | Zweck | Kritisch |
|---------|---------|-------|----------|
| react | ^18.2.0 | UI Framework | ✅ JA |
| react-dom | ^18.2.0 | React DOM | ✅ JA |
| vite | ^5.2.0 | Build Tool | ✅ JA |
| typescript | ^5.2.2 | Type Safety | ✅ JA |
| tailwindcss | ^3.4.17 | CSS Framework | ✅ JA |
| @radix-ui/react-* | ^1.1+ | UI Components | ✅ JA |
| lucide-react | ^0.507.0 | Icons | ✅ JA |
| axios | ^1.8.4 | HTTP Client | ✅ JA |

## ⚠️ **BEKANNTE KOMPATIBILITÄTSPROBLEME**

### **Node.js Version Konflikte:**
- **Problem:** React 19 + Node.js 20 + alte Build-Tools
- **Lösung:** React 18 + Vite (im neuen System implementiert)

### **Package Manager Konflikte:**
- **Problem:** yarn.lock vs package-lock.json Konflikte
- **Lösung:** NPM-only Strategie (im neuen System implementiert)

### **Python Version Probleme:**
- **Problem:** Python 3.13 mit älteren Packages
- **Lösung:** Python 3.10-3.11 empfohlen

### **MongoDB Connection:**
- **Problem:** MongoDB nicht verfügbar
- **Lösung:** Supervisor-Service oder lokale Installation

## 🔍 **PRE-INSTALLATION CHECKLIST**

### **Bevor Sie installieren:**
```bash
# 1. Python Check
python --version
# Erwartung: Python 3.10.0+

# 2. Node.js Check  
node --version
# Erwartung: v18.0.0+

# 3. NPM Check
npm --version
# Erwartung: 8.0.0+

# 4. Schreibrechte Check
echo test > test.tmp && del test.tmp
# Erwartung: Keine Fehlermeldung

# 5. Internet Check
ping pypi.org
ping registry.npmjs.org
# Erwartung: Beide erreichbar

# 6. Port Check
netstat -an | findstr ":3000 :8001"
# Erwartung: Keine Ausgabe (Ports frei)
```

### **Installation-Ready Indikator:**
Wenn alle obigen Checks ✅ sind, können Sie mit der Installation fortfahren.

**Diese Voraussetzungen sind für XIONIMUS AI v3.0.0 vollständig dokumentiert.**