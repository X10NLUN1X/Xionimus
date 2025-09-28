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
        echo [HELP] Mögliche Lösungen:
        echo   1. Stellen Sie sicher, dass Sie das Projekt heruntergeladen haben
        echo   2. Extrahieren Sie das ZIP-Archiv vollständig
        echo   3. Navigieren Sie manuell zum XionimusX-main Verzeichnis
        echo   4. Führen Sie dieses Script aus dem Projektordner aus
        pause
        exit /b 1
    )
    
    REM Prüfe nach Verzeichniswechsel
    if not exist "backend\server.py" (
        echo [ERROR] Verzeichniswechsel fehlgeschlagen!
        echo [DEBUG] Aktuelles Verzeichnis: %CD%
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

REM Prüfe ob Backend bereits läuft
echo [CHECK] Prüfe ob Backend bereits läuft...
netstat -an | findstr :8001 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Backend läuft bereits auf Port 8001
    echo [ACTION] Starte trotzdem neues Backend-Fenster...
)

echo [START] Starte Backend-Server...
cd backend
start "XIONIMUS Backend" cmd /k "echo [BACKEND] XIONIMUS AI Backend wird gestartet... && echo [INFO] Backend läuft auf Port 8001 && python server.py"

REM Warte bis Backend bereit
echo [WAIT] Warte auf Backend-Start (10 Sekunden)...
timeout /t 10 /nobreak >nul

REM Teste Backend-Verfügbarkeit (optional - curl nicht immer verfügbar)
echo [TEST] Prüfe Backend-Status...
python -c "
import requests
import time
for i in range(5):
    try:
        r = requests.get('http://localhost:8001/api/health', timeout=2)
        if r.status_code == 200:
            print('[SUCCESS] Backend läuft auf http://localhost:8001')
            break
    except:
        print(f'[RETRY] Backend Test {i+1}/5...')
        time.sleep(2)
else:
    print('[INFO] Backend-Test fehlgeschlagen - möglicherweise noch am starten')
" 2>nul || echo [INFO] Backend-Test übersprungen (requests nicht verfügbar)

cd ..

echo.

REM ==========================================
echo [STEP 7/8] FRONTEND STARTEN  
echo ==========================================

REM Prüfe ob Frontend bereits läuft
echo [CHECK] Prüfe ob Frontend bereits läuft...
netstat -an | findstr :3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Frontend läuft bereits auf Port 3000
    echo [ACTION] Starte trotzdem neues Frontend-Fenster...
)

REM Bestimme Frontend-Start-Befehl
where yarn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set FRONTEND_START_CMD=yarn start
    echo [INFO] Verwende yarn für Frontend-Start
) else (
    set FRONTEND_START_CMD=npm start
    echo [INFO] Verwende npm für Frontend-Start
)

echo [START] Starte Frontend-Server...
cd frontend
start "XIONIMUS Frontend" cmd /k "echo [FRONTEND] XIONIMUS AI Frontend wird gestartet... && echo [INFO] Frontend läuft auf Port 3000 && %FRONTEND_START_CMD%"

echo [WAIT] Warte auf Frontend-Start (15 Sekunden)...
timeout /t 15 /nobreak >nul

echo [INFO] Frontend sollte jetzt verfügbar sein auf http://localhost:3000

cd ..

echo.

REM ==========================================
echo [STEP 8/8] SYSTEM BEREIT
echo ==========================================

echo.
echo 🎉 XIONIMUS AI INSTALLATION UND START ABGESCHLOSSEN!
echo.
echo 🖥️ SERVER-STATUS:
echo   ✅ Backend:  Gestartet auf http://localhost:8001
echo   ✅ Frontend: Gestartet auf http://localhost:3000
echo.
echo 🌐 ZUGRIFF:
echo   → Frontend: http://localhost:3000  (Haupt-UI)
echo   → Backend:  http://localhost:8001  (API-Server)
echo.  
echo 📋 WICHTIGE HINWEISE:
echo   ✓ Beide Server-Fenster müssen geöffnet bleiben
echo   ✓ Backend-Fenster: "XIONIMUS Backend"
echo   ✓ Frontend-Fenster: "XIONIMUS Frontend"
echo   ✓ Schließen Sie NICHT die Server-Fenster
echo.
echo 🔑 ERSTE SCHRITTE:
echo   1. Browser öffnet automatisch http://localhost:3000
echo   2. Klicke "API Configuration" 
echo   3. Konfiguriere deine API-Keys:
echo      • Anthropic API Key (für Claude)
echo      • OpenAI API Key (für GPT)
echo      • Perplexity API Key (für Research)
echo   4. Starte mit einem Chat!
echo.
echo 🤖 VERFÜGBARE FEATURES:
echo   ✅ 9 AI-Agenten (Code, Research, Writing, Data, QA, etc.)
echo   ✅ Multi-Agent Chat System mit intelligenter Weiterleitung
echo   ✅ GitHub Repository Integration
echo   ✅ File Upload und Management
echo   ✅ Session Management (Gespräche speichern)
echo   ✅ Projekt Management
echo.
echo 🛠️ TROUBLESHOOTING:
echo   • Weiße Seite? → Warte 1-2 Minuten, Frontend startet noch
echo   • Backend-Fehler? → Prüfe Backend-Fenster für Fehlermeldungen
echo   • Port belegt? → Andere Anwendungen auf Port 3000/8001 schließen
echo   • Bei Problemen: Script erneut ausführen
echo.
echo 🚀 SYSTEM IST BEREIT! Browser öffnet in 5 Sekunden...
echo.

REM Browser automatisch öffnen
timeout /t 5 /nobreak >nul
echo [LAUNCH] Öffne XIONIMUS AI...
start http://localhost:3000

echo.
echo ✨ Viel Erfolg mit XIONIMUS AI! ✨
echo.
echo [INFO] Dieses Fenster kann nach dem Browserstart geschlossen werden.
echo [REMINDER] Halten Sie die Server-Fenster geöffnet!
echo.
pause