@echo off
title XIONIMUS AI - Windows Installation
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - AUTOMATISCHE INSTALLATION
echo ==========================================
echo.
echo [INFO] Diese Installation richtet Xionimus AI komplett fuer Windows ein
echo [INFO] Erfordert: Python 3.9+, Node.js 18+, MongoDB Compass
echo.
pause

REM Admin-Rechte pruefen
echo [CHECK] Pruefe Administrator-Rechte...
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNUNG] Nicht als Administrator ausgefuehrt
    echo [INFO] Einige Funktionen koennen eingeschraenkt sein
) else (
    echo [SUCCESS] Administrator-Rechte gefunden
)
echo.

REM Aktuelles Verzeichnis setzen
set INSTALL_DIR=%CD%
echo [INFO] Installationsverzeichnis: %INSTALL_DIR%
echo.

REM ==========================================
echo [STEP 1/8] PYTHON INSTALLATION PRUEFEN
REM ==========================================
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden!
    echo [DOWNLOAD] Lade Python 3.11 herunter...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
    echo [INSTALL] Installiere Python... (Folgen Sie dem Assistenten)
    echo [WICHTIG] Aktivieren Sie "Add Python to PATH"!
    start /wait %TEMP%\python-installer.exe
    del %TEMP%\python-installer.exe
) else (
    echo [SUCCESS] Python gefunden
    python --version
)
echo.

REM ==========================================
echo [STEP 2/8] NODE.JS INSTALLATION PRUEFEN
REM ==========================================
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden!
    echo [DOWNLOAD] Lade Node.js 20 LTS herunter...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi' -OutFile '%TEMP%\nodejs-installer.msi'"
    echo [INSTALL] Installiere Node.js...
    start /wait msiexec /i %TEMP%\nodejs-installer.msi /quiet
    del %TEMP%\nodejs-installer.msi
) else (
    echo [SUCCESS] Node.js gefunden
    node --version
)
echo.

REM ==========================================
echo [STEP 3/8] MONGODB COMPASS SETUP
REM ==========================================
echo [INFO] MongoDB Compass Setup...
if not exist "C:\data\db" (
    echo [CREATE] Erstelle MongoDB Datenverzeichnis...
    mkdir "C:\data\db"
)

REM MongoDB Service pruefen
sc query MongoDB >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] MongoDB Service gefunden
    sc start MongoDB >nul 2>nul
) else (
    echo [INFO] MongoDB Service nicht gefunden - verwende MongoDB Compass
)
echo.

REM ==========================================
echo [STEP 4/8] YARN INSTALLATION
REM ==========================================
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn global...
    npm install -g yarn
) else (
    echo [SUCCESS] Yarn bereits installiert
)
echo.

REM ==========================================
echo [STEP 5/8] PROJEKTVERZEICHNISSE ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle Projektverzeichnisse...
if not exist "uploads" mkdir uploads
if not exist "sessions" mkdir sessions
if not exist "logs" mkdir logs
echo [SUCCESS] Verzeichnisse erstellt: uploads, sessions, logs
echo.

REM ==========================================
echo [STEP 6/8] .ENV DATEIEN ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle .env Dateien...

REM Frontend .env
echo REACT_APP_BACKEND_URL=http://localhost:8001> frontend\.env
echo WDS_SOCKET_PORT=3000>> frontend\.env
echo [SUCCESS] frontend\.env erstellt

REM Backend .env
echo MONGO_URL="mongodb://localhost:27017"> backend\.env
echo DB_NAME="xionimus_ai">> backend\.env
echo CORS_ORIGINS="*">> backend\.env
echo.>> backend\.env
echo # AI API Keys - Uncomment und Keys einfuegen>> backend\.env
echo # PERPLEXITY_API_KEY=pplx-your_key_here>> backend\.env
echo # ANTHROPIC_API_KEY=sk-ant-your_key_here>> backend\.env
echo [SUCCESS] backend\.env erstellt
echo.

REM ==========================================
echo [STEP 7/8] PYTHON DEPENDENCIES INSTALLIEREN
REM ==========================================
echo [INSTALL] Installiere Python Dependencies...

REM Pip aktualisieren
echo [UPDATE] Aktualisiere pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pip update fehlgeschlagen - verwende vorhandene Version
)

REM Wichtige Python Packages vorinstallieren
echo [INSTALL] Installiere wichtige Python Packages...
python -m pip install wheel setuptools
python -m pip install motor pymongo fastapi uvicorn anthropic openai python-dotenv pathlib

cd backend
echo [INSTALL] Installiere Backend Dependencies aus requirements.txt...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python Dependencies Installation fehlgeschlagen!
    echo [DEBUG] Versuche einzelne Installation...
    python -m pip install fastapi uvicorn motor anthropic openai python-dotenv pathlib
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Auch einzelne Installation fehlgeschlagen!
        pause
        exit /b 1
    )
)
cd ..
echo [SUCCESS] Python Dependencies installiert
echo.

REM ==========================================
echo [STEP 8/8] NODE.JS DEPENDENCIES INSTALLIEREN
REM ==========================================
echo [INSTALL] Installiere Node.js Dependencies...
cd frontend
yarn install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js Dependencies Installation fehlgeschlagen!
    pause
    exit /b 1
)
cd ..
echo [SUCCESS] Node.js Dependencies installiert
echo.

REM ==========================================
echo [FINAL] INSTALLATION ABGESCHLOSSEN!
REM ==========================================
color 0B
echo.
echo  ╔════════════════════════════════════════╗
echo  ║     XIONIMUS AI INSTALLATION FERTIG!   ║
echo  ╚════════════════════════════════════════╝
echo.
echo [SUCCESS] Alle Komponenten wurden installiert!
echo.
echo [NAECHSTE SCHRITTE]:
echo   1. API Keys konfigurieren (optional):
echo      - Oeffnen Sie: backend\.env
echo      - Uncomment die API Key Zeilen
echo      - Keys von https://www.perplexity.ai/settings/api
echo      - Keys von https://console.anthropic.com/
echo.
echo   2. System starten (2 separate Fenster):
echo      a) Doppelklick: START_BACKEND.bat
echo      b) Doppelklick: START_FRONTEND.bat
echo.
echo   3. MongoDB Compass oeffnen:
echo      - Verbindung: mongodb://localhost:27017
echo      - Database: xionimus_ai
echo.
echo [URLS NACH START]:
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8001/api/health
echo   - API Docs:  http://localhost:8001/docs
echo.
echo [FILES ERSTELLT]:
echo   - START_BACKEND.bat
echo   - START_FRONTEND.bat
echo   - frontend\.env
echo   - backend\.env
echo   - uploads\ Verzeichnis
echo   - sessions\ Verzeichnis
echo.
pause