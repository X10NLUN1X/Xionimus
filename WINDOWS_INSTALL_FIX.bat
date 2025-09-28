@echo off
title XIONIMUS AI - Windows Python 3.10 Fix Installation
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - WINDOWS PYTHON 3.10 FIX
echo ==========================================
echo.
echo [INFO] Diese Installation behebt den numpy-Fehler fuer Python 3.10.11
echo [INFO] Verwendung: Python 3.10 kompatible Dependencies
echo [INFO] Erfordert: Python 3.10+, Node.js 18+, MongoDB Compass
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
    echo [FIX] Bitte Python 3.10+ manuell installieren: https://python.org
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python gefunden
    python --version
    
    REM Python Version pruefen
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [INFO] Python Version: %PYTHON_VERSION%
)
echo.

REM ==========================================
echo [STEP 2/8] NODE.JS INSTALLATION PRUEFEN  
REM ==========================================
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden!
    echo [FIX] Bitte Node.js 18+ manuell installieren: https://nodejs.org
    pause
    exit /b 1
) else (
    echo [SUCCESS] Node.js gefunden
    node --version
)
echo.

REM ==========================================
echo [STEP 3/8] MONGODB COMPASS SETUP
REM ==========================================
echo [INFO] MongoDB Compass Setup...
sc query MongoDB >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] MongoDB Service gefunden
) else (
    echo [WARNUNG] MongoDB Service nicht gefunden
    echo [INFO] Bitte MongoDB Compass installieren: https://mongodb.com/try/download/compass
    echo [INFO] Installation kann trotzdem fortgesetzt werden
)
echo.

REM ==========================================
echo [STEP 4/8] YARN INSTALLATION
REM ==========================================
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Yarn installiert
    ) else (
        echo [ERROR] Yarn Installation fehlgeschlagen
        echo [FIX] Verwende npm stattdessen
        set USE_NPM=1
    )
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
if not exist "backend\local_data" mkdir backend\local_data

echo [SUCCESS] Verzeichnisse erstellt: uploads, sessions, logs
echo.

REM ==========================================
echo [STEP 6/8] .ENV DATEIEN ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle .env Dateien...

REM Frontend .env
echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
if exist "frontend\.env" (
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [ERROR] frontend\.env konnte nicht erstellt werden
)

REM Backend .env  
(
echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
echo ANTHROPIC_API_KEY=
echo OPENAI_API_KEY=
echo PERPLEXITY_API_KEY=
) > backend\.env

if exist "backend\.env" (
    echo [SUCCESS] backend\.env erstellt
) else (
    echo [ERROR] backend\.env konnte nicht erstellt werden
)
echo.

REM ==========================================
echo [STEP 7/8] PYTHON DEPENDENCIES INSTALLIEREN (PYTHON 3.10 FIX)
REM ==========================================
echo [INSTALL] Installiere Python Dependencies...

REM Erst pip aktualisieren
echo [UPDATE] Aktualisiere pip...
python -m pip install --upgrade pip

REM Core Dependencies installieren (sicher fuer Python 3.10)
echo [INSTALL] Installiere wichtige Python Packages...
python -m pip install wheel setuptools

echo [INSTALL] Installiere Basis-Dependencies...
python -m pip install fastapi uvicorn motor pymongo anthropic openai python-dotenv pathlib

REM Verwende die Python 3.10 kompatible requirements.txt
echo [INSTALL] Installiere Backend Dependencies aus requirements_windows_py310.txt...
cd backend
python -m pip install -r requirements_windows_py310.txt

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python Dependencies Installation fehlgeschlagen!
    echo [DEBUG] Versuche einzelne Installation...
    
    REM Kritische Dependencies einzeln installieren
    python -m pip install fastapi uvicorn motor anthropic openai python-dotenv pathlib
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Auch einzelne Installation fehlgeschlagen!
        echo [FIX] Bitte manuell installieren:
        echo   python -m pip install fastapi uvicorn motor anthropic openai python-dotenv
        pause
    ) else (
        echo [SUCCESS] Basis-Dependencies installiert
    )
) else (
    echo [SUCCESS] Alle Python Dependencies installiert
)

cd ..
echo.

REM ==========================================
echo [STEP 8/8] FRONTEND DEPENDENCIES INSTALLIEREN  
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
        pause
    )
) else (
    echo [SUCCESS] Frontend Dependencies installiert
)

cd ..
echo.

REM ==========================================
echo INSTALLATION ABGESCHLOSSEN
REM ==========================================
echo.
echo [SUCCESS] XIONIMUS AI Installation abgeschlossen!
echo.
echo [INFO] Naechste Schritte:
echo   1. MongoDB Compass starten
echo   2. Backend starten: cd backend ^&^& python server.py
echo   3. Frontend starten: cd frontend ^&^& yarn start
echo   4. Oeffne: http://localhost:3000
echo.
echo [CONFIG] API-Keys konfigurieren in der Web-Oberflaeche:
echo   - Anthropic API Key
echo   - OpenAI API Key  
echo   - Perplexity API Key
echo.
echo [FIX] Falls numpy-Fehler weiterhin auftreten:
echo   python -m pip install "numpy>=1.24.0,<1.27.0"
echo.

REM Batch Scripts erstellen fuer einfachen Start
echo [CREATE] Erstelle Start-Scripts...

REM Backend Start Script
(
echo @echo off
echo title XIONIMUS AI Backend
echo cd /d "%INSTALL_DIR%\backend"
echo echo [INFO] Starte XIONIMUS AI Backend...
echo python server.py
echo pause
) > START_BACKEND.bat

REM Frontend Start Script  
(
echo @echo off
echo title XIONIMUS AI Frontend
echo cd /d "%INSTALL_DIR%\frontend"
echo echo [INFO] Starte XIONIMUS AI Frontend...
if defined USE_NPM (
    echo npm start
) else (
    echo yarn start
)
echo pause
) > START_FRONTEND.bat

echo [SUCCESS] Start-Scripts erstellt: START_BACKEND.bat, START_FRONTEND.bat
echo.

pause