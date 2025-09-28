@echo off
title XIONIMUS AI - Installation
color 0B

echo.
echo ==========================================
echo      XIONIMUS AI - INSTALLATION
echo ==========================================
echo.
echo [INFO] Installiert Backend und Frontend Dependencies
echo [INFO] Erstellt notwendige Konfigurationsdateien
echo [INFO] Bereitet System für den Start vor
echo.

REM Prüfe Verzeichnis und Projektstruktur
cd /d "%~dp0"

if not exist "backend\server.py" (
    echo [ERROR] Backend-Verzeichnis nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [ERROR] Frontend-Verzeichnis nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus
    pause
    exit /b 1
)

echo [SUCCESS] Projektstruktur validiert
echo.

REM ==========================================
echo [SCHRITT 1/4] SYSTEM-VORAUSSETZUNGEN PRÜFEN
echo ==========================================

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
echo [SCHRITT 2/4] KONFIGURATIONSDATEIEN ERSTELLEN
echo ==========================================

echo [CREATE] Erstelle notwendige Verzeichnisse...
if not exist "backend\local_data" mkdir backend\local_data
if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads

echo [CREATE] Backend .env Datei...
cd backend
if not exist ".env" (
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    echo DEBUG=true
    echo HOST=0.0.0.0
    echo PORT=8001
    ) > .env
    echo [SUCCESS] Backend .env erstellt
) else (
    echo [INFO] Backend .env bereits vorhanden
)

cd ..\frontend

echo [CREATE] Frontend .env Datei...
if not exist ".env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env
    echo [SUCCESS] Frontend .env erstellt
) else (
    echo [INFO] Frontend .env bereits vorhanden
)

cd ..
echo.

REM ==========================================
echo [SCHRITT 3/4] BACKEND DEPENDENCIES INSTALLIEREN
echo ==========================================

cd backend

echo [UPDATE] Pip modernisieren...
python -m pip install --upgrade pip

echo [INSTALL] Backend Dependencies...
echo [INFO] Installiere Web Framework...
python -m pip install fastapi==0.115.6 uvicorn==0.32.1 starlette

echo [INFO] Installiere Async/Network Dependencies...
python -m pip install aiohttp==3.11.10 aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache

echo [INFO] Installiere Data Models...
python -m pip install pydantic==2.10.3 typing_extensions

echo [INFO] Installiere Database...
python -m pip install motor==3.3.1 pymongo==4.5.0 dnspython

echo [INFO] Installiere AI APIs...
python -m pip install anthropic==0.40.0 openai==1.57.4

echo [INFO] Installiere Additional Dependencies...
python -m pip install python-dotenv==1.1.1 requests PyYAML Jinja2 rich click jsonschema attrs httpx httpcore

echo [VALIDATE] Teste kritische Backend Dependencies...
python -c "
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

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend Dependencies Installation fehlgeschlagen
    pause
    exit /b 1
)

cd ..
echo.

REM ==========================================
echo [SCHRITT 4/4] FRONTEND DEPENDENCIES INSTALLIEREN
echo ==========================================

cd frontend

echo [CHECK] Package Manager verfügbar...
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% NEQ 0 (
        echo [INFO] Verwende npm als Fallback
        set USE_NPM=1
    )
)

echo [INSTALL] Frontend Dependencies...
if defined USE_NPM (
    echo [INFO] Verwende npm...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Frontend Dependencies Installation fehlgeschlagen
        cd ..
        pause
        exit /b 1
    )
    echo npm start > .start_command
) else (
    echo [INFO] Verwende yarn...
    yarn install
    if %ERRORLEVEL% NEQ 0 (
        echo [FALLBACK] yarn fehlgeschlagen - verwende npm...
        npm install
        if %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Frontend Dependencies Installation fehlgeschlagen
            cd ..
            pause
            exit /b 1
        )
        echo npm start > .start_command
    ) else (
        echo yarn start > .start_command
    )
)

echo [VALIDATE] Prüfe Frontend Dependencies...
if exist "node_modules" (
    echo [SUCCESS] Frontend Dependencies erfolgreich installiert
) else (
    echo [ERROR] node_modules Verzeichnis nicht gefunden
    cd ..
    pause
    exit /b 1
)

cd ..
echo.

REM ==========================================
echo [INSTALLATION ABGESCHLOSSEN]
echo ==========================================

echo.
echo ✅ XIONIMUS AI INSTALLATION ERFOLGREICH!
echo.
echo 📋 NÄCHSTE SCHRITTE:
echo.
echo [START] Backend starten:
echo    START_BACKEND.bat
echo.
echo [START] Frontend starten (in separatem Terminal):
echo    START_FRONTEND.bat
echo.
echo [ACCESS] Nach dem Start verfügbar unter:
echo    → Frontend: http://localhost:3000
echo    → Backend:  http://localhost:8001
echo.
echo 🔑 API-KONFIGURATION:
echo    → Öffnen Sie http://localhost:3000
echo    → Klicken Sie auf "API Configuration"
echo    → Konfigurieren Sie Ihre API-Keys:
echo      • Anthropic API Key (für Claude)
echo      • OpenAI API Key (für GPT)
echo      • Perplexity API Key (für Research)
echo.
echo 🎯 INSTALLATION VOLLSTÄNDIG - READY TO START!
echo.

pause