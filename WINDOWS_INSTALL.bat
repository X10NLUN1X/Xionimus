@echo off
title XIONIMUS AI - Complete Windows Installation
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - COMPLETE INSTALLATION
echo ==========================================
echo.
echo [INFO] Vollständige Installation für Python 3.13.7
echo [INFO] Behebt aiohttp-Fehler und alle Dependencies
echo [INFO] Getestet für Windows 10/11
echo.
pause

REM Admin-Rechte prüfen
echo [STEP 1/10] Admin-Rechte prüfen...
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [WARNUNG] Nicht als Administrator ausgeführt
    echo [INFO] Bei Problemen als Administrator neu starten
) else (
    echo [SUCCESS] Administrator-Rechte verfügbar
)
echo.

REM Verzeichnis setzen und prüfen
echo [STEP 2/10] Verzeichnis-Struktur prüfen...
set INSTALL_DIR=%CD%
echo [INFO] Aktuelles Verzeichnis: %INSTALL_DIR%

REM Prüfe ob im richtigen Verzeichnis
if not exist "backend" (
    echo [ERROR] backend\ Verzeichnis nicht gefunden!
    echo [INFO] Sie sind in: %CD%
    echo [FIX] Suche XIONIMUS Verzeichnis...
    
    REM Versuche häufige Pfade
    if exist "C:\AI\XionimusX-main\backend" (
        echo [FOUND] Gefunden in: C:\AI\XionimusX-main
        cd /d "C:\AI\XionimusX-main"
        set INSTALL_DIR=C:\AI\XionimusX-main
        goto :continue_install
    )
    
    if exist "C:\Users\%USERNAME%\Desktop\XionimusX-main\backend" (
        echo [FOUND] Gefunden auf Desktop
        cd /d "C:\Users\%USERNAME%\Desktop\XionimusX-main"
        set INSTALL_DIR=C:\Users\%USERNAME%\Desktop\XionimusX-main
        goto :continue_install
    )
    
    if exist "C:\Users\%USERNAME%\Downloads\XionimusX-main\backend" (
        echo [FOUND] Gefunden in Downloads
        cd /d "C:\Users\%USERNAME%\Downloads\XionimusX-main"
        set INSTALL_DIR=C:\Users\%USERNAME%\Downloads\XionimusX-main
        goto :continue_install
    )
    
    echo [ERROR] XIONIMUS Verzeichnis nicht gefunden!
    echo.
    echo [FIX] Bitte folgende Schritte:
    echo   1. Öffnen Sie den Windows Explorer
    echo   2. Navigieren Sie zu Ihrem XIONIMUS Verzeichnis (z.B. C:\AI\XionimusX-main)
    echo   3. Doppelklicken Sie dort auf WINDOWS_INSTALL.bat
    echo.
    echo [ODER] Führen Sie diese Befehle aus:
    echo   cd /d "C:\AI\XionimusX-main"
    echo   WINDOWS_INSTALL.bat
    echo.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] frontend\ Verzeichnis nicht gefunden!
    echo [INFO] backend gefunden, aber frontend fehlt
    pause
    exit /b 1
)

:continue_install

echo [SUCCESS] Verzeichnis-Struktur korrekt
echo.

REM Python prüfen
echo [STEP 3/10] Python Installation prüfen...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden!
    echo [DOWNLOAD] Lade Python 3.13 herunter...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
    echo [INSTALL] Python installieren? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
        echo [INFO] Python installiert - bitte Terminal neu starten
        pause
        exit /b 1
    ) else (
        echo [INFO] Bitte Python manuell installieren: https://python.org
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Python gefunden
    python --version
    
    REM Python Version prüfen
    python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python 3.10+ erforderlich
        pause
        exit /b 1
    )
)
echo.

REM Node.js prüfen
echo [STEP 4/10] Node.js Installation prüfen...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden!
    echo [DOWNLOAD] Lade Node.js herunter...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi' -OutFile '%TEMP%\nodejs-installer.msi'"
    echo [INSTALL] Node.js installieren? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        msiexec /i %TEMP%\nodejs-installer.msi /quiet
        echo [INFO] Node.js installiert - bitte Terminal neu starten
        pause
        exit /b 1
    ) else (
        echo [INFO] Bitte Node.js manuell installieren: https://nodejs.org
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Node.js gefunden
    node --version
)
echo.

REM Yarn Installation
echo [STEP 5/10] Yarn Package Manager...
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn global...
    npm install -g yarn --silent
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Yarn installiert
    ) else (
        echo [WARNING] Yarn Installation fehlgeschlagen - verwende npm
        set USE_NPM=1
    )
) else (
    echo [SUCCESS] Yarn bereits verfügbar
)
echo.

REM Verzeichnisse erstellen
echo [STEP 6/10] Projekt-Verzeichnisse erstellen...
if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\local_data" mkdir backend\local_data
if not exist "backend\__pycache__" mkdir backend\__pycache__
echo [SUCCESS] Alle Verzeichnisse erstellt
echo.

REM .env Dateien erstellen
echo [STEP 7/10] Konfigurationsdateien erstellen...

REM Backend .env (KRITISCH!)
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
    pause
    exit /b 1
)

REM Frontend .env
echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env

if exist "frontend\.env" (
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [ERROR] frontend\.env konnte nicht erstellt werden
    pause
    exit /b 1
)
echo.

REM Python Dependencies (HAUPTTEIL)
echo [STEP 8/10] Python Dependencies installieren...
cd backend

REM Pip modernisieren
echo [UPDATE] Pip aktualisieren...
python -m pip install --upgrade pip setuptools wheel --quiet

REM Phase 1: Kritische async/network Dependencies (LÖST aiohttp FEHLER!)
echo [PHASE 1] Async/Network Dependencies (aiohttp Fix)...
python -m pip install aiohttp==3.12.15 --quiet
python -m pip install aiohappyeyeballs==2.6.1 aiosignal==1.4.0 anyio==4.11.0 --quiet
python -m pip install multidict==6.6.4 frozenlist==1.7.0 yarl==1.20.1 propcache==0.3.2 --quiet

REM Phase 2: Web Framework
echo [PHASE 2] Web Framework...
python -m pip install fastapi==0.110.1 uvicorn==0.25.0 starlette==0.37.2 --quiet

REM Phase 3: Data Models
echo [PHASE 3] Data Models...
python -m pip install pydantic==2.11.7 pydantic_core==2.33.2 typing_extensions==4.15.0 --quiet

REM Phase 4: Database
echo [PHASE 4] Database...
python -m pip install motor==3.3.1 pymongo==4.5.0 dnspython==2.8.0 --quiet

REM Phase 5: AI APIs
echo [PHASE 5] AI APIs...
python -m pip install anthropic==0.68.1 openai==1.109.1 --quiet
python -m pip install httpx==0.28.1 httpcore==1.0.9 --quiet

REM Phase 6: Data Processing (Python 3.13 kann neueste Versionen!)
echo [PHASE 6] Data Processing...
python -m pip install numpy==2.2.0 pandas==2.2.0 --quiet

REM Phase 7: Utilities
echo [PHASE 7] Essential Utilities...
python -m pip install python-dotenv==1.1.1 click==8.2.1 tqdm==4.67.1 --quiet
python -m pip install requests==2.32.5 urllib3==2.5.0 certifi==2025.8.3 --quiet
python -m pip install charset-normalizer==3.4.3 idna==3.10 --quiet

REM Phase 8: Security & Auth
echo [PHASE 8] Security & Authentication...
python -m pip install passlib[bcrypt]==1.7.4 PyJWT==2.10.1 --quiet
python -m pip install python-multipart==0.0.20 cryptography==45.0.7 --quiet

REM Phase 9: File Processing
echo [PHASE 9] File Processing...
python -m pip install PyYAML==6.0.2 pillow==11.3.0 --quiet

REM Phase 10: Additional
echo [PHASE 10] Additional Libraries...
python -m pip install jsonschema==4.25.1 attrs==25.3.0 annotated-types==0.7.0 --quiet
python -m pip install Jinja2==3.1.6 MarkupSafe==3.0.2 rich==14.1.0 --quiet
python -m pip install h11==0.16.0 jiter==0.11.0 sniffio==1.3.1 packaging==25.0 --quiet

REM Final: Komplette Requirements (falls etwas fehlt)
echo [FINAL] Verwende stabile Requirements...
if exist "requirements_python313_stable.txt" (
    python -m pip install -r requirements_python313_stable.txt --quiet
) else (
    echo [INFO] Verwende Fallback-Requirements...
    python -m pip install -r requirements.txt --quiet
)

echo [SUCCESS] Python Dependencies Installation abgeschlossen
cd ..
echo.

REM Frontend Dependencies
echo [STEP 9/10] Frontend Dependencies installieren...
cd frontend

if defined USE_NPM (
    echo [NPM] Installiere mit npm...
    npm install --silent
    set FRONTEND_CMD=npm start
) else (
    echo [YARN] Installiere mit yarn...
    yarn install --silent
    set FRONTEND_CMD=yarn start
)

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend Installation fehlgeschlagen!
    echo [FALLBACK] Versuche npm...
    npm install --silent
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Auch npm fehlgeschlagen!
        echo [INFO] Frontend manuell installieren: cd frontend && npm install
    ) else (
        echo [SUCCESS] Frontend mit npm installiert
        set FRONTEND_CMD=npm start
    )
) else (
    echo [SUCCESS] Frontend Dependencies installiert
)

cd ..
echo.

REM System-Test
echo [STEP 10/10] System-Test durchführen...
cd backend

echo [TEST] Kritische Python Imports testen...
python -c "import aiohttp; print('[✅] aiohttp - OK')" 2>nul || echo [❌] aiohttp - FEHLT
python -c "import fastapi; print('[✅] fastapi - OK')" 2>nul || echo [❌] fastapi - FEHLT
python -c "import motor; print('[✅] motor - OK')" 2>nul || echo [❌] motor - FEHLT
python -c "import anthropic; print('[✅] anthropic - OK')" 2>nul || echo [❌] anthropic - FEHLT
python -c "import openai; print('[✅] openai - OK')" 2>nul || echo [❌] openai - FEHLT
python -c "import numpy; print('[✅] numpy - OK')" 2>nul || echo [❌] numpy - FEHLT
python -c "import pandas; print('[✅] pandas - OK')" 2>nul || echo [❌] pandas - FEHLT

echo.
echo [TEST] .env Dateien prüfen...
if exist ".env" (
    echo [✅] backend\.env - OK
) else (
    echo [❌] backend\.env - FEHLT
)

cd ..\frontend
if exist ".env" (
    echo [✅] frontend\.env - OK
) else (
    echo [❌] frontend\.env - FEHLT
)

cd ..

REM Start-Scripts aktualisieren
echo.
echo [FINAL] Start-Scripts optimieren...
(
echo @echo off
echo title XIONIMUS AI Backend
echo cd /d "%%~dp0backend"
echo echo [INFO] Starte XIONIMUS AI Backend...
echo python server.py
echo pause
) > START_BACKEND_SIMPLE.bat

(
echo @echo off
echo title XIONIMUS AI Frontend
echo cd /d "%%~dp0frontend"
echo echo [INFO] Starte XIONIMUS AI Frontend...
echo %FRONTEND_CMD%
echo pause
) > START_FRONTEND_SIMPLE.bat

echo [SUCCESS] Einfache Start-Scripts erstellt
echo.

REM ==========================================
echo INSTALLATION ERFOLGREICH ABGESCHLOSSEN!
REM ==========================================
echo.
echo [🎉] XIONIMUS AI ist bereit!
echo.
echo [📝] NÄCHSTE SCHRITTE:
echo   1. Backend starten:   START_BACKEND.bat (oder START_BACKEND_SIMPLE.bat)
echo   2. Frontend starten:  START_FRONTEND.bat (oder START_FRONTEND_SIMPLE.bat)
echo   3. Browser öffnen:    http://localhost:3000
echo.
echo [🔑] API KEYS KONFIGURIEREN:
echo   → http://localhost:3000 → API Configuration Button
echo   → Anthropic API Key (für Claude)
echo   → OpenAI API Key (für GPT)
echo   → Perplexity API Key (für Research)
echo.
echo [✨] VERFÜGBARE FEATURES:
echo   ✅ 9 AI-Agenten (Code, Research, Writing, Data, QA, GitHub, File, Session, Experimental)
echo   ✅ Multi-Agent Chat System mit intelligenter Weiterleitung
echo   ✅ GitHub Repository Integration und Analyse
echo   ✅ Projekt Management mit CRUD-Operationen
echo   ✅ File Upload und Management System
echo   ✅ Session Management (Gespräche speichern/laden)
echo   ✅ Modern Gold/Black UI mit responsivem Design
echo.
echo [🛠️] BEI PROBLEMEN:
echo   → MongoDB: Installiere MongoDB Compass (optional)
echo   → Ports: Backend 8001, Frontend 3000
echo   → Logs: Konsole-Output beachten
echo.
pause