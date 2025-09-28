@echo off
title XIONIMUS AI - Master Installation & Start
color 0A

REM ==========================================
echo.
echo ==========================================
echo    XIONIMUS AI - MASTER INSTALLATION
echo ==========================================
echo.
echo [INFO] Vollständige Installation, Konfiguration und Start
echo [INFO] Für Python 3.10+ und Node.js 18+  
echo [INFO] Behebt alle bekannten Import- und Konfigurationsprobleme
echo.

REM Benutzer über Ablauf informieren
echo [WORKFLOW] Dieser Script führt folgende Schritte aus:
echo   1. System-Voraussetzungen prüfen
echo   2. Projekt-Konfiguration erstellen  
echo   3. Backend Dependencies installieren
echo   4. Frontend Dependencies installieren
echo   5. System-Tests durchführen
echo   6. Backend und Frontend starten
echo.
set /p continue="Fortfahren? (y/n): "
if /i not "%continue%"=="y" exit /b 0

REM ==========================================
echo.
echo [STEP 1/8] SYSTEM-VORAUSSETZUNGEN PRÜFEN
echo ==========================================

REM Verzeichnis-Struktur prüfen
echo [CHECK] Verzeichnis-Struktur...
set INSTALL_DIR=%CD%
echo [INFO] Arbeitsverzeichnis: %INSTALL_DIR%

REM Automatische Pfad-Erkennung
if not exist "backend\server.py" (
    echo [SEARCH] Suche XIONIMUS Verzeichnis...
    
    if exist "C:\AI\XionimusX-main\backend\server.py" (
        cd /d "C:\AI\XionimusX-main"
        echo [FOUND] Gefunden: C:\AI\XionimusX-main
    ) else if exist "%USERPROFILE%\Desktop\XionimusX-main\backend\server.py" (
        cd /d "%USERPROFILE%\Desktop\XionimusX-main"
        echo [FOUND] Gefunden: Desktop\XionimusX-main
    ) else if exist "%USERPROFILE%\Downloads\XionimusX-main\backend\server.py" (
        cd /d "%USERPROFILE%\Downloads\XionimusX-main"
        echo [FOUND] Gefunden: Downloads\XionimusX-main
    ) else (
        echo [ERROR] XIONIMUS Verzeichnis nicht gefunden!
        echo [FIX] Bitte navigieren Sie manuell zum XionimusX-main Verzeichnis
        pause
        exit /b 1
    )
)

if not exist "frontend\package.json" (
    echo [ERROR] Frontend-Verzeichnis nicht vollständig!
    pause
    exit /b 1
)

echo [SUCCESS] Projektstruktur validiert

REM Python prüfen
echo [CHECK] Python Installation...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden!
    echo [INFO] Bitte Python 3.10+ installieren: https://python.org
    pause
    exit /b 1
) else (
    python --version
    python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python 3.10+ erforderlich
        pause  
        exit /b 1
    )
    echo [SUCCESS] Python Version kompatibel
)

REM Node.js prüfen
echo [CHECK] Node.js Installation...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden!
    echo [INFO] Bitte Node.js 18+ installieren: https://nodejs.org
    pause
    exit /b 1
) else (
    node --version
    echo [SUCCESS] Node.js verfügbar
)

echo.

REM ==========================================
echo [STEP 2/8] PROJEKT-KONFIGURATION
echo ==========================================

echo [CREATE] Erstelle notwendige Verzeichnisse...
if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads  
if not exist "backend\local_data" mkdir backend\local_data

echo [CREATE] Konfigurationsdateien...

REM Backend .env
(
echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
echo ANTHROPIC_API_KEY=
echo OPENAI_API_KEY=  
echo PERPLEXITY_API_KEY=
) > backend\.env

REM Frontend .env  
echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env

if exist "backend\.env" if exist "frontend\.env" (
    echo [SUCCESS] Konfigurationsdateien erstellt
) else (
    echo [ERROR] Fehler beim Erstellen der .env Dateien
    pause
    exit /b 1
)

echo.

REM ==========================================
echo [STEP 3/8] BACKEND DEPENDENCIES
echo ==========================================

cd backend

echo [UPDATE] Pip modernisieren...  
python -m pip install --upgrade pip setuptools wheel --quiet

echo [INSTALL] Kritische Dependencies...
python -m pip install aiohttp==3.12.15 anyio==4.11.0 --quiet
python -m pip install fastapi==0.110.1 uvicorn==0.25.0 --quiet
python -m pip install motor==3.3.1 pymongo==4.5.0 --quiet
python -m pip install anthropic==0.68.1 openai==1.109.1 --quiet
python -m pip install python-dotenv==1.1.1 requests==2.32.5 --quiet

echo [INSTALL] Standard-Dependencies...
python -m pip install numpy pandas pydantic httpx --quiet
python -m pip install PyYAML Jinja2 rich click --quiet

echo [TEST] Backend Import-Test...
python -c "
try:
    from agents.agent_manager import AgentManager
    print('[SUCCESS] Backend-System importiert')
except Exception as e:
    print(f'[ERROR] Backend-Import: {e}')
    exit(1)
" || (
    echo [ERROR] Backend-Imports fehlgeschlagen  
    pause
    exit /b 1
)

cd ..

echo.

REM ==========================================
echo [STEP 4/8] FRONTEND DEPENDENCIES  
echo ==========================================

cd frontend

REM Yarn installieren falls nicht vorhanden
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn...
    npm install -g yarn --silent 2>nul
    set USE_NPM=1
)

REM Frontend Dependencies installieren
if defined USE_NPM (
    echo [NPM] Installiere Frontend Dependencies...
    npm install --silent
    set START_FRONTEND_CMD=npm start
) else (
    echo [YARN] Installiere Frontend Dependencies...
    yarn install --silent  
    set START_FRONTEND_CMD=yarn start
)

if %ERRORLEVEL% NEQ 0 (
    echo [FALLBACK] Versuche mit npm...
    npm install
    set START_FRONTEND_CMD=npm start
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Frontend Installation fehlgeschlagen
        pause
        exit /b 1
    )
)

cd ..

echo [SUCCESS] Frontend Dependencies installiert

echo.

REM ==========================================  
echo [STEP 5/8] SYSTEM-TESTS
echo ==========================================

echo [TEST] Backend-Module...
cd backend
python -c "import aiohttp, fastapi, motor; print('✅ Core modules OK')" || echo ❌ Core modules fehlen
python -c "from agents.agent_manager import AgentManager; print('✅ Agent System OK')" || echo ❌ Agent System fehlen

echo [TEST] Konfigurationsdateien...
if exist ".env" (echo ✅ backend\.env) else (echo ❌ backend\.env fehlt)
cd ..\frontend  
if exist ".env" (echo ✅ frontend\.env) else (echo ❌ frontend\.env fehlt)
cd ..

echo.

REM ==========================================
echo [STEP 6/8] BACKEND STARTEN
echo ==========================================

echo [START] Starte Backend-Server...
cd backend
start "XIONIMUS Backend" cmd /k "echo [BACKEND] XIONIMUS AI Backend startet... && python server.py"

REM Warte bis Backend bereit
echo [WAIT] Warte auf Backend-Start...
timeout /t 5 /nobreak >nul

REM Teste Backend-Verfügbarkeit
echo [TEST] Teste Backend-Verfügbarkeit...
for /l %%i in (1,1,10) do (
    curl -s http://localhost:8001/api/health >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Backend läuft auf http://localhost:8001
        goto backend_ready
    )
    echo [RETRY] Warte auf Backend... (%%i/10)
    timeout /t 2 /nobreak >nul
)

echo [WARNING] Backend antwortet nicht - fortfahren mit Frontend
:backend_ready

cd ..

echo.

REM ==========================================
echo [STEP 7/8] FRONTEND STARTEN  
echo ==========================================

echo [START] Starte Frontend-Server...
cd frontend
start "XIONIMUS Frontend" cmd /k "echo [FRONTEND] XIONIMUS AI Frontend startet... && %START_FRONTEND_CMD%"

echo [WAIT] Warte auf Frontend-Start...
timeout /t 5 /nobreak >nul

REM Teste Frontend-Verfügbarkeit
echo [TEST] Teste Frontend-Verfügbarkeit...
for /l %%i in (1,1,15) do (
    curl -s http://localhost:3000 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Frontend läuft auf http://localhost:3000
        goto frontend_ready
    )
    echo [RETRY] Warte auf Frontend... (%%i/15)  
    timeout /t 2 /nobreak >nul
)

echo [WARNING] Frontend antwortet nicht - möglicherweise noch am starten
:frontend_ready

cd ..

echo.

REM ==========================================
echo [STEP 8/8] SYSTEM BEREIT
echo ==========================================

echo.
echo 🎉 XIONIMUS AI ERFOLGREICH GESTARTET!
echo.
echo 🌐 ZUGRIFF:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8001
echo.  
echo 🔑 KONFIGURATION:
echo   → Öffne http://localhost:3000
echo   → Klicke "API Configuration"
echo   → Konfiguriere deine API-Keys:
echo     • Anthropic API Key (für Claude)
echo     • OpenAI API Key (für GPT)  
echo     • Perplexity API Key (für Research)
echo.
echo 🤖 VERFÜGBARE FEATURES:
echo   ✅ 9 AI-Agenten (Code, Research, Writing, Data, QA, etc.)
echo   ✅ Multi-Agent Chat System
echo   ✅ GitHub Integration
echo   ✅ File Management
echo   ✅ Session Management  
echo   ✅ Project Management
echo.
echo 🛠️ TROUBLESHOOTING:
echo   → Beide Server-Fenster sollten geöffnet bleiben
echo   → Bei Problemen: Neustart mit diesem Script
echo   → Logs in den Server-Konsolen prüfen
echo.
echo ✨ Viel Spaß mit XIONIMUS AI! ✨
echo.

REM Browser automatisch öffnen
echo [INFO] Öffne XIONIMUS AI in 5 Sekunden...
timeout /t 5 /nobreak >nul
start http://localhost:3000

pause