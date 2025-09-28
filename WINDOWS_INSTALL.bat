@echo off
title XIONIMUS AI - Windows Installation (Python 3.13)
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - WINDOWS INSTALLATION
echo ==========================================
echo.
echo [INFO] Installation für Windows mit Python 3.13 Support
echo [INFO] Behebt numpy-Fehler und installiert alle Dependencies
echo.
pause

REM Admin-Rechte prüfen
echo [CHECK] Prüfe Administrator-Rechte...
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNUNG] Nicht als Administrator ausgeführt
    echo [INFO] Einige Funktionen können eingeschränkt sein
) else (
    echo [SUCCESS] Administrator-Rechte gefunden
)
echo.

REM Aktuelles Verzeichnis setzen
set INSTALL_DIR=%CD%
echo [INFO] Installationsverzeichnis: %INSTALL_DIR%
echo.

REM ==========================================
echo [STEP 1/7] PYTHON INSTALLATION PRÜFEN
REM ==========================================
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden!
    echo [FIX] Bitte Python 3.10+ installieren: https://python.org
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python gefunden
    python --version
)
echo.

REM ==========================================
echo [STEP 2/7] NODE.JS INSTALLATION PRÜFEN  
REM ==========================================
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden!
    echo [FIX] Bitte Node.js 18+ installieren: https://nodejs.org
    pause
    exit /b 1
) else (
    echo [SUCCESS] Node.js gefunden
    node --version
)
echo.

REM ==========================================
echo [STEP 3/7] YARN INSTALLATION
REM ==========================================
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Yarn installiert
    ) else (
        echo [WARNING] Yarn Installation fehlgeschlagen - verwende npm
        set USE_NPM=1
    )
) else (
    echo [SUCCESS] Yarn bereits installiert
)
echo.

REM ==========================================
echo [STEP 4/7] PROJEKTVERZEICHNISSE ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle Projektverzeichnisse...

if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\local_data" mkdir backend\local_data

echo [SUCCESS] Verzeichnisse erstellt
echo.

REM ==========================================
echo [STEP 5/7] .ENV DATEIEN ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle .env Dateien...

REM Backend .env
if not exist "backend\.env" (
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    ) > backend\.env
    echo [SUCCESS] backend\.env erstellt
) else (
    echo [INFO] backend\.env bereits vorhanden
)

REM Frontend .env  
if not exist "frontend\.env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [INFO] frontend\.env bereits vorhanden
)
echo.

REM ==========================================
echo [STEP 6/7] PYTHON DEPENDENCIES INSTALLIEREN
REM ==========================================
echo [INSTALL] Installiere Python Dependencies...

cd backend

REM Pip aktualisieren
echo [UPDATE] Aktualisiere pip...
python -m pip install --upgrade pip setuptools wheel

REM Kritische Dependencies zuerst (für aiohttp Fehler)
echo [INSTALL] Installiere kritische Dependencies...
python -m pip install aiohttp aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache

REM Core Backend Dependencies
echo [INSTALL] Installiere Core Backend...
python -m pip install fastapi uvicorn starlette pydantic typing_extensions

REM Database
echo [INSTALL] Installiere Database...
python -m pip install motor pymongo dnspython

REM AI APIs
echo [INSTALL] Installiere AI APIs...
python -m pip install anthropic openai httpx httpcore

REM Data Processing (Python 3.13 safe)
echo [INSTALL] Installiere Data Processing...
python -m pip install "numpy>=1.24.0" "pandas>=2.0.0"

REM Utilities
echo [INSTALL] Installiere Utilities...
python -m pip install python-dotenv click tqdm requests urllib3 certifi
python -m pip install PyYAML pillow passlib PyJWT python-multipart
python -m pip install jsonschema attrs annotated-types Jinja2 MarkupSafe
python -m pip install rich h11 jiter sniffio packaging charset-normalizer idna

REM Alle Requirements installieren
echo [INSTALL] Installiere alle Requirements...
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Einige Packages konnten nicht installiert werden
    echo [INFO] Basis-Funktionalität sollte trotzdem funktionieren
) else (
    echo [SUCCESS] Alle Python Dependencies installiert
)

cd ..
echo.

REM ==========================================
echo [STEP 7/7] FRONTEND DEPENDENCIES INSTALLIEREN  
REM ==========================================
echo [INSTALL] Installiere Frontend Dependencies...
cd frontend

if defined USE_NPM (
    echo [INSTALL] Verwende npm...
    npm install
) else (
    echo [INSTALL] Verwende yarn...
    yarn install
)

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend Dependencies Installation fehlgeschlagen!
    echo [FIX] Versuche npm...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Auch npm Installation fehlgeschlagen!
    ) else (
        echo [SUCCESS] Frontend Dependencies mit npm installiert
    )
) else (
    echo [SUCCESS] Frontend Dependencies installiert
)

cd ..
echo.

REM ==========================================
echo [TEST] SYSTEM VERFÜGBARKEIT PRÜFEN
REM ==========================================
echo [TEST] Teste kritische Python Imports...

python -c "import aiohttp; print('[✅] aiohttp - OK')" 2>nul || echo [❌] aiohttp - FEHLT
python -c "import fastapi; print('[✅] fastapi - OK')" 2>nul || echo [❌] fastapi - FEHLT
python -c "import motor; print('[✅] motor - OK')" 2>nul || echo [❌] motor - FEHLT
python -c "import anthropic; print('[✅] anthropic - OK')" 2>nul || echo [❌] anthropic - FEHLT
python -c "import numpy; print('[✅] numpy - OK')" 2>nul || echo [❌] numpy - FEHLT

echo.

REM ==========================================
echo INSTALLATION ABGESCHLOSSEN
REM ==========================================
echo.
echo [SUCCESS] XIONIMUS AI Installation abgeschlossen!
echo.
echo [INFO] System starten:
echo   1. Backend:  START_BACKEND.bat
echo   2. Frontend: START_FRONTEND.bat
echo   3. Browser:  http://localhost:3000
echo.
echo [CONFIG] API Keys konfigurieren:
echo   - Öffne: http://localhost:3000
echo   - Klicke: API Configuration
echo   - Eingeben: Anthropic, OpenAI, Perplexity Keys
echo.
echo [FEATURES] Verfügbare Features:
echo   ✅ 9 AI Agenten (Code, Research, Writing, etc.)
echo   ✅ Multi-Agent Chat System
echo   ✅ GitHub Integration  
echo   ✅ Projekt Management
echo   ✅ Modern Gold/Black UI
echo.
echo [FIX] Falls numpy-Fehler weiterhin auftreten:
echo   cd backend
echo   pip install "numpy>=1.24.0,<2.4.0" --force-reinstall
echo.
pause