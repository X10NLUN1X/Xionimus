#!/bin/bash

echo "=========================================="
echo "      XIONIMUS AI - INSTALLATION"
echo "=========================================="
echo ""
echo "[INFO] Installiert Backend und Frontend Dependencies"
echo "[INFO] Erstellt notwendige Konfigurationsdateien"
echo ""

# Wechsle ins Skript-Verzeichnis
cd "$(dirname "$0")"

# Prüfe Projektstruktur
if [ ! -f "backend/server.py" ]; then
    echo "[ERROR] Backend nicht gefunden!"
    echo "[INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus"
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    echo "[ERROR] Frontend nicht gefunden!"
    echo "[INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus"
    exit 1
fi

echo "[SUCCESS] Projektstruktur validiert"
echo ""

# ==========================================
echo "[STEP 1/6] SYSTEM-VORAUSSETZUNGEN PRÜFEN"
echo "=========================================="

# Python prüfen
echo "[CHECK] Python Installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 nicht gefunden!"
    echo "[INFO] Bitte Python 3.10+ installieren"
    exit 1
else
    python3 --version
    echo "[SUCCESS] Python3 verfügbar"
fi

# Node.js prüfen
echo "[CHECK] Node.js Installation..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js nicht gefunden!"
    echo "[INFO] Bitte Node.js 18+ installieren"
    exit 1
else
    node --version
    echo "[SUCCESS] Node.js verfügbar"
fi

# NPM prüfen
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm nicht gefunden!"
    exit 1
else
    npm --version
    echo "[SUCCESS] npm verfügbar"
fi

echo ""

# ==========================================
echo "[STEP 2/6] PROJEKT-KONFIGURATION"
echo "=========================================="

echo "[CREATE] Erstelle notwendige Verzeichnisse..."
mkdir -p backend/local_data
mkdir -p backend/sessions
mkdir -p backend/uploads

echo "[CREATE] Backend .env Datei..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
MONGO_URL=mongodb://localhost:27017/xionimus_ai
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PERPLEXITY_API_KEY=
DEBUG=true
HOST=0.0.0.0
PORT=8001
EOF
    echo "[SUCCESS] Backend .env erstellt"
else
    echo "[INFO] Backend .env bereits vorhanden"
fi

echo "[CREATE] Frontend .env Datei..."
if [ ! -f "frontend/.env" ]; then
    echo "REACT_APP_BACKEND_URL=http://localhost:8001" > frontend/.env
    echo "[SUCCESS] Frontend .env erstellt"
else
    echo "[INFO] Frontend .env bereits vorhanden"
fi

echo ""

# ==========================================
echo "[STEP 3/6] BACKEND DEPENDENCIES"
echo "=========================================="

echo "[DEBUG] Aktuelles Verzeichnis: $(pwd)"
echo "[ACTION] Wechsle ins Backend-Verzeichnis..."

cd backend

echo "[DEBUG] Backend-Verzeichnis: $(pwd)"
if [ ! -f "server.py" ]; then
    echo "[ERROR] server.py nicht gefunden - falsches Verzeichnis?"
    echo "[DEBUG] Verfügbare Python-Dateien:"
    ls -la *.py 2>/dev/null || echo "Keine Python-Dateien gefunden"
    echo "[WARNING] Backend Installation wird übersprungen"
    cd ..
    goto skip_backend_install
fi

echo "[TEST] Teste Python und pip Verfügbarkeit..."
python3 --version
if [ $? -ne 0 ]; then
    echo "[ERROR] Python3 nicht verfügbar im Backend-Verzeichnis"
    echo "[WARNING] Backend Installation wird übersprungen"
    cd ..
    goto skip_backend_install
fi

python3 -m pip --version
if [ $? -ne 0 ]; then
    echo "[ERROR] pip nicht verfügbar"
    echo "[WARNING] Backend Installation wird übersprungen"
    cd ..
    goto skip_backend_install
fi

echo "[UPDATE] Pip modernisieren..."
python3 -m pip install --upgrade pip setuptools wheel

echo "[INSTALL] Backend Dependencies..."
echo "[INFO] Installiere Web Framework..."
python3 -m pip install fastapi==0.115.6 uvicorn==0.32.1 starlette

echo "[INFO] Installiere Async/Network Dependencies..."
python3 -m pip install aiohttp aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache

echo "[INFO] Installiere Data Models..."
python3 -m pip install pydantic typing_extensions

echo "[INFO] Installiere Database..."
python3 -m pip install motor pymongo dnspython

echo "[INFO] Installiere AI APIs..."
python3 -m pip install anthropic openai

echo "[INFO] Installiere Additional Dependencies..."
python3 -m pip install python-dotenv requests PyYAML Jinja2 rich click jsonschema attrs httpx httpcore

echo "[VALIDATE] Teste kritische Backend Dependencies..."
python3 -c "
import sys
try:
    import fastapi, uvicorn, aiohttp, motor, anthropic, openai
    from dotenv import load_dotenv
    print('[SUCCESS] Alle kritischen Backend Dependencies verfügbar')
    sys.exit(0)
except ImportError as e:
    print(f'[ERROR] Fehlende Dependency: {e}')
    sys.exit(1)
"

skip_backend_install:
cd ..

echo ""

# ==========================================
echo "[STEP 4/6] FRONTEND DEPENDENCIES"
echo "=========================================="

echo "[DEBUG] Aktuelles Verzeichnis vor Frontend-Installation: $(pwd)"

# Wechsle ins Frontend-Verzeichnis
cd frontend
if [ $? -ne 0 ]; then
    echo "[ERROR] Kann nicht ins Frontend-Verzeichnis wechseln"
    echo "[WARNING] Frontend Installation wird übersprungen"
    goto skip_frontend
fi

echo "[DEBUG] Aktuelles Verzeichnis nach Wechsel: $(pwd)"

# Prüfe package.json
if [ ! -f "package.json" ]; then
    echo "[ERROR] package.json nicht gefunden im Frontend-Verzeichnis"
    echo "[DEBUG] Verzeichnisinhalt:"
    ls -la
    cd ..
    echo "[WARNING] Frontend Installation übersprungen"
    goto skip_frontend
fi

echo "[SUCCESS] package.json gefunden"
echo "[INFO] Starte Frontend Dependencies Installation..."

# Lösche alte node_modules für saubere Installation
if [ -d "node_modules" ]; then
    echo "[INFO] Alte node_modules gefunden - werden für saubere Installation entfernt"
    rm -rf node_modules
    if [ -d "node_modules" ]; then
        echo "[WARNING] node_modules konnten nicht vollständig gelöscht werden - Installation fortsetzen"
    fi
fi

# NPM Installation
echo "[NPM] Starte npm install im Verzeichnis: $(pwd)"
npm install --legacy-peer-deps
if [ $? -eq 0 ]; then
    echo "[SUCCESS] npm install erfolgreich ausgeführt"
else
    echo "[ERROR] npm install fehlgeschlagen - Fehlercode: $?"
    echo "[RETRY] Versuche Cache bereinigen und erneut installieren..."
    npm cache clean --force
    npm install --legacy-peer-deps --no-optional
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] npm install beim zweiten Versuch erfolgreich"
    else
        echo "[ERROR] npm install auch beim zweiten Versuch fehlgeschlagen"
        echo "[DEBUG] NPM Version und Konfiguration:"
        npm --version
        npm config list
        echo "[WARNING] Frontend Dependencies möglicherweise unvollständig installiert"
    fi
fi

# Validiere Installation
echo "[VERIFY] Überprüfe Installation..."
if [ -d "node_modules" ]; then
    echo "[SUCCESS] node_modules Verzeichnis existiert"
    echo "[INFO] Anzahl installierter Packages:"
    ls -1 node_modules | wc -l || echo "Package-Zählung fehlgeschlagen"
    
    # Prüfe wichtige Dependencies
    if [ -d "node_modules/react" ]; then
        echo "[SUCCESS] React installiert"
    else
        echo "[WARNING] React nicht gefunden in node_modules"
    fi
    
    if [ -d "node_modules/@craco" ]; then
        echo "[SUCCESS] Craco installiert"
    else
        echo "[WARNING] Craco nicht gefunden in node_modules"
    fi
else
    echo "[ERROR] node_modules Verzeichnis nicht erstellt"
    echo "[DEBUG] Aktueller Verzeichnisinhalt:"
    ls -la
    echo "[WARNING] Frontend möglicherweise unvollständig installiert"
fi

echo "[INFO] Frontend Dependencies Installation abgeschlossen"

skip_frontend:
cd ..

echo ""

# ==========================================
echo "[STEP 5/6] SYSTEM-TESTS"
echo "=========================================="

echo "[TEST] Konfigurationsdateien..."
if [ -f "backend/.env" ]; then
    echo "✅ backend/.env"
else
    echo "❌ backend/.env fehlt"
fi

if [ -f "frontend/.env" ]; then
    echo "✅ frontend/.env"  
else
    echo "❌ frontend/.env fehlt"
fi

echo ""

# ==========================================
echo "[INSTALLATION ABGESCHLOSSEN - STEP 6/6]"
echo "=========================================="

echo ""
echo "✅ XIONIMUS AI INSTALLATION ERFOLGREICH!"
echo ""
echo "📋 NÄCHSTE SCHRITTE:"
echo ""
echo "[START] Verwenden Sie die Start-Skripte:"
echo "    START_BACKEND.bat    - Backend starten"
echo "    START_FRONTEND.bat   - Frontend starten"  
echo "    START_ALL.bat        - Beide Services starten"
echo ""
echo "[ACCESS] Nach dem Start verfügbar unter:"
echo "    → Frontend: http://localhost:3000"
echo "    → Backend:  http://localhost:8001"
echo ""
echo "🔑 API-KONFIGURATION:"
echo "    → Öffnen Sie http://localhost:3000"
echo "    → Klicken Sie auf 'API Configuration'"
echo "    → Konfigurieren Sie Ihre API-Keys:"
echo "      • Anthropic API Key (für Claude)"
echo "      • OpenAI API Key (für GPT)"
echo "      • Perplexity API Key (für Research)"
echo ""
echo "🎯 INSTALLATION VOLLSTÄNDIG ABGESCHLOSSEN!"
echo ""

echo "[INFO] Verwenden Sie START_ALL.bat für den einfachen Start beider Services"
echo ""