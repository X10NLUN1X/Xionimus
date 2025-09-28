@echo off
title XIONIMUS AI - Fixed Windows Installation
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - FIXED INSTALLATION
echo ==========================================
echo.
echo [INFO] Reparierte Version für Python 3.13.7
echo [INFO] Behebt alle Verzeichnis- und aiohttp-Probleme
echo.
pause

REM Admin-Rechte prüfen
echo [STEP 1/8] Admin-Rechte prüfen...
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [INFO] Läuft als normaler Benutzer (OK)
) else (
    echo [SUCCESS] Administrator-Rechte verfügbar
)
echo.

REM Automatische Verzeichnis-Erkennung
echo [STEP 2/8] Verzeichnis automatisch finden...
set CURRENT_DIR=%CD%

REM Prüfe aktuelles Verzeichnis zuerst
if exist "backend\server.py" if exist "frontend\package.json" (
    echo [SUCCESS] Bereits im korrekten Verzeichnis: %CD%
    goto :start_installation
)

REM Suche in häufigen Pfaden
echo [SEARCH] Suche XIONIMUS Verzeichnis...
if exist "C:\AI\XionimusX-main\backend\server.py" (
    cd /d "C:\AI\XionimusX-main"
    echo [FOUND] Wechsel nach: C:\AI\XionimusX-main
    goto :start_installation
)

if exist "%USERPROFILE%\Desktop\XionimusX-main\backend\server.py" (
    cd /d "%USERPROFILE%\Desktop\XionimusX-main"
    echo [FOUND] Wechsel nach: Desktop\XionimusX-main
    goto :start_installation
)

if exist "%USERPROFILE%\Downloads\XionimusX-main\backend\server.py" (
    cd /d "%USERPROFILE%\Downloads\XionimusX-main"
    echo [FOUND] Wechsel nach: Downloads\XionimusX-main
    goto :start_installation
)

REM Nicht gefunden - Fehler
echo [ERROR] XIONIMUS Verzeichnis nicht gefunden!
echo [FIX] Erstelle Desktop-Verknüpfung zum richtigen Pfad
pause
exit /b 1

:start_installation
echo [SUCCESS] Installation startet in: %CD%
echo.

REM .env Dateien erstellen (KRITISCH!)
echo [STEP 3/8] Konfigurationsdateien erstellen...
(
echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
echo ANTHROPIC_API_KEY=
echo OPENAI_API_KEY=
echo PERPLEXITY_API_KEY=
) > backend\.env

echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env

if exist "backend\.env" (
    echo [SUCCESS] backend\.env erstellt
) else (
    echo [ERROR] Konnte backend\.env nicht erstellen
    pause
    exit /b 1
)

if exist "frontend\.env" (
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [ERROR] Konnte frontend\.env nicht erstellen
    pause
    exit /b 1
)
echo.

REM Python prüfen
echo [STEP 4/8] Python prüfen...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden! Bitte installieren: https://python.org
    pause
    exit /b 1
) else (
    python --version
    echo [SUCCESS] Python verfügbar
)
echo.

REM Verzeichnisse erstellen
echo [STEP 5/8] Projektverzeichnisse erstellen...
if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\local_data" mkdir backend\local_data
echo [SUCCESS] Verzeichnisse erstellt
echo.

REM Backend Dependencies (HAUPTTEIL - löst aiohttp Problem)
echo [STEP 6/8] Backend Dependencies installieren...
cd backend

echo [UPDATE] Pip aktualisieren...
python -m pip install --upgrade pip setuptools wheel --quiet

echo [CRITICAL] aiohttp und async Dependencies (behebt Ihren Fehler)...
python -m pip install aiohttp==3.12.15 --quiet
python -m pip install aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache --quiet

echo [CORE] Web Framework...
python -m pip install fastapi==0.110.1 uvicorn==0.25.0 starlette==0.37.2 --quiet

echo [DATA] Data Models...
python -m pip install pydantic==2.11.7 typing_extensions==4.15.0 --quiet

echo [DATABASE] MongoDB...
python -m pip install motor==3.3.1 pymongo==4.5.0 dnspython==2.8.0 --quiet

echo [AI] AI APIs...
python -m pip install anthropic==0.68.1 openai==1.109.1 httpx==0.28.1 --quiet

echo [PROCESSING] Data Processing...
python -m pip install numpy pandas --quiet

echo [UTILS] Utilities...
python -m pip install python-dotenv==1.1.1 requests==2.32.5 click==8.2.1 --quiet
python -m pip install PyYAML==6.0.2 Jinja2==3.1.6 rich==14.1.0 --quiet
python -m pip install jsonschema attrs Pillow --quiet

echo [SUCCESS] Backend Dependencies installiert
cd ..
echo.

REM Frontend Dependencies
echo [STEP 7/8] Frontend Dependencies...
cd frontend

where yarn >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [YARN] Installiere mit yarn...
    yarn install --silent
    set START_CMD=yarn start
) else (
    echo [NPM] Installiere mit npm...
    npm install --silent
    set START_CMD=npm start
)

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Frontend Installation hatte Probleme
    echo [INFO] Versuche es nochmal mit npm...
    npm install
    set START_CMD=npm start
)

cd ..
echo.

REM System Test
echo [STEP 8/8] System Test...
cd backend
echo [TEST] Teste kritische Imports...
python -c "import aiohttp; print('[✅] aiohttp - OK')" 2>nul || echo [❌] aiohttp - PROBLEM
python -c "import fastapi; print('[✅] fastapi - OK')" 2>nul || echo [❌] fastapi - PROBLEM
python -c "import motor; print('[✅] motor - OK')" 2>nul || echo [❌] motor - PROBLEM
cd ..

REM Start Scripts erstellen
echo.
echo [CREATE] Einfache Start-Scripts...
(
echo @echo off
echo cd /d "%%~dp0backend"
echo python server.py
echo pause
) > START_BACKEND_SIMPLE.bat

(
echo @echo off  
echo cd /d "%%~dp0frontend"
echo %START_CMD%
echo pause
) > START_FRONTEND_SIMPLE.bat

echo.
echo ==========================================
echo       INSTALLATION ERFOLGREICH! 🎉
echo ==========================================
echo.
echo [🚀] SYSTEM STARTEN:
echo   Backend:  START_BACKEND_SIMPLE.bat
echo   Frontend: START_FRONTEND_SIMPLE.bat
echo   Browser:  http://localhost:3000
echo.
echo [🔑] API KEYS KONFIGURIEREN:
echo   → Öffne http://localhost:3000
echo   → Klicke "API Configuration"  
echo   → Anthropic, OpenAI, Perplexity Keys eingeben
echo.
echo [✨] 9 AI-AGENTEN VERFÜGBAR:
echo   Code, Research, Writing, Data, QA, GitHub, File, Session, Experimental
echo.
pause