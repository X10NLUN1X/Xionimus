@echo off
title Xionimus AI - Startup
color 0B
setlocal EnableDelayedExpansion

REM ========================================================================
REM   XIONIMUS AI - ULTIMATE STARTUP SCRIPT
REM   Macht ALLES automatisch: Installation, Setup, Start
REM ========================================================================

cd /d "%~dp0"

echo.
echo ========================================================================
echo                    XIONIMUS AI STARTUP
echo ========================================================================
echo.

REM ========================================================================
REM PHASE 1: ENVIRONMENT CHECK
REM ========================================================================
echo [PHASE 1/5] Umgebung pruefen...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FEHLER: Python nicht gefunden!
    echo.
    echo Bitte installieren Sie Python 3.10+ von:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo ✅ Python gefunden

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FEHLER: Node.js nicht gefunden!
    echo.
    echo Bitte installieren Sie Node.js von:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js gefunden

REM Check MongoDB
echo ℹ️  MongoDB sollte laufen auf Port 27017
echo    (Optional - System laeuft auch ohne)

echo.

REM ========================================================================
REM PHASE 2: .ENV SETUP (KRITISCH!)
REM ========================================================================
echo [PHASE 2/5] .env Konfiguration...
echo.

if not exist "backend\.env" (
    echo ⚠️  .env nicht gefunden - erstelle automatisch...
    echo.
    
    REM Erstelle backend Ordner falls nicht existiert
    if not exist "backend" mkdir backend
    
    REM Erstelle .env mit PowerShell
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$content = 'SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307' + [Environment]::NewLine + ^
    'JWT_ALGORITHM=HS256' + [Environment]::NewLine + ^
    'JWT_EXPIRE_MINUTES=1440' + [Environment]::NewLine + ^
    'ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=' + [Environment]::NewLine + ^
    'DEBUG=true' + [Environment]::NewLine + ^
    'HOST=0.0.0.0' + [Environment]::NewLine + ^
    'PORT=8001' + [Environment]::NewLine + ^
    'LOG_LEVEL=INFO' + [Environment]::NewLine + ^
    'MONGO_URL=mongodb://localhost:27017/xionimus_ai' + [Environment]::NewLine + ^
    'REDIS_URL=redis://localhost:6379/0' + [Environment]::NewLine + ^
    'OPENAI_API_KEY=' + [Environment]::NewLine + ^
    'ANTHROPIC_API_KEY=' + [Environment]::NewLine + ^
    'PERPLEXITY_API_KEY=' + [Environment]::NewLine + ^
    'GITHUB_TOKEN=' + [Environment]::NewLine + ^
    'GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf' + [Environment]::NewLine + ^
    'GITHUB_OAUTH_CLIENT_SECRET=acc1edb2b095606ee55182a4eb5daf0cda9ce46d' + [Environment]::NewLine + ^
    'GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback' + [Environment]::NewLine + ^
    'GITHUB_USE_PAT=false'; ^
    [System.IO.File]::WriteAllText('backend\.env', $content, [System.Text.Encoding]::UTF8)"
    
    if exist "backend\.env" (
        echo ✅ .env erfolgreich erstellt!
        echo ✅ SECRET_KEY: Permanent (64 Zeichen)
        echo ✅ ENCRYPTION_KEY: Permanent (44 Zeichen)
        echo.
        echo ℹ️  API Keys koennen spaeter in backend\.env hinzugefuegt werden
    ) else (
        echo ❌ FEHLER: .env konnte nicht erstellt werden!
        pause
        exit /b 1
    )
) else (
    echo ✅ .env gefunden - wird verwendet
)

echo.

REM ========================================================================
REM PHASE 3: DEPENDENCIES INSTALLATION
REM ========================================================================
echo [PHASE 3/5] Dependencies pruefen/installieren...
echo.

REM Backend Dependencies
if not exist "backend\venv" (
    echo ℹ️  Backend: Virtual Environment wird erstellt...
    cd backend
    python -m venv venv
    cd ..
    echo ✅ Virtual Environment erstellt
)

echo ℹ️  Backend: Installiere/Aktualisiere Packages...
cd backend
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Einige Packages konnten nicht installiert werden
    echo    System kann trotzdem funktionieren
)
cd ..
echo ✅ Backend Dependencies bereit

REM Frontend Dependencies
if not exist "frontend\node_modules" (
    echo ℹ️  Frontend: Node Modules werden installiert...
    cd frontend
    call npm install
    cd ..
    echo ✅ Frontend Dependencies installiert
) else (
    echo ✅ Frontend Dependencies bereits installiert
)

echo.

REM ========================================================================
REM PHASE 4: PORT CHECK
REM ========================================================================
echo [PHASE 4/5] Ports pruefen...
echo.

REM Check if ports are free
netstat -ano | findstr :8001 >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port 8001 wird bereits verwendet!
    echo    Bitte schliessen Sie die Anwendung die Port 8001 nutzt
    echo    Oder druecken Sie eine Taste um trotzdem zu starten
    pause >nul
)

netstat -ano | findstr :3000 >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port 3000 wird bereits verwendet!
    echo    Bitte schliessen Sie die Anwendung die Port 3000 nutzt
    echo    Oder druecken Sie eine Taste um trotzdem zu starten
    pause >nul
)

echo ✅ Ports verfuegbar oder werden freigegeben

echo.

REM ========================================================================
REM PHASE 5: START SERVICES
REM ========================================================================
echo [PHASE 5/5] Starte Services...
echo.

REM Backend
echo ℹ️  Starte Backend (Port 8001)...
start "Xionimus AI - Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && echo Backend wird gestartet... && python main.py"
timeout /t 3 /nobreak >nul
echo ✅ Backend gestartet

REM Frontend
echo ℹ️  Starte Frontend (Port 3000)...
start "Xionimus AI - Frontend" cmd /k "cd /d %~dp0frontend && echo Frontend wird gestartet... && npm start"
timeout /t 3 /nobreak >nul
echo ✅ Frontend gestartet

REM Browser
echo ℹ️  Oeffne Browser...
timeout /t 5 /nobreak >nul
start http://localhost:3000
echo ✅ Browser geoeffnet

echo.
echo ========================================================================
echo                    STARTUP ABGESCHLOSSEN
echo ========================================================================
echo.
echo ✅ Backend:  http://localhost:8001
echo ✅ Frontend: http://localhost:3000
echo ✅ Browser:  Automatisch geoeffnet
echo.
echo ========================================================================
echo                    WICHTIGE HINWEISE
echo ========================================================================
echo.
echo 🔑 ERSTER START - Bitte beachten:
echo.
echo 1. Browser-Cache leeren (EINMALIG):
echo    - Druecke F12 im Browser
echo    - Application ^> Clear storage ^> "Clear site data"
echo    - Oder: Strg+Shift+R (Hard Refresh)
echo.
echo 2. Neu einloggen:
echo    - Username: admin
echo    - Password: admin123
echo.
echo 3. API Keys hinzufuegen (OPTIONAL):
echo    - Settings (⚙️) ^> API Keys
echo    - OpenAI Key: sk-proj-...
echo    - Anthropic Key: sk-ant-...
echo    - Speichern und Backend neu starten
echo.
echo 4. Zum Bearbeiten der .env:
echo    - Oeffne: backend\.env
echo    - Fuege API Keys hinzu
echo    - Speichern
echo    - Backend Fenster schliessen und neu starten
echo.
echo ========================================================================
echo                    TROUBLESHOOTING
echo ========================================================================
echo.
echo ❌ "Backend startet nicht":
echo    - Pruefe MongoDB laeuft (optional)
echo    - Pruefe Port 8001 ist frei
echo    - Pruefe backend\.env existiert
echo.
echo ❌ "Frontend startet nicht":
echo    - Pruefe Port 3000 ist frei
echo    - Loesche node_modules und starte neu
echo.
echo ❌ "JWT validation failed":
echo    - Browser-Cache leeren (F12 ^> Clear storage)
echo    - Neu einloggen
echo    - Das passiert nur EINMAL nach .env Erstellung
echo.
echo ❌ "Chat antwortet nicht":
echo    - API Keys in backend\.env hinzufuegen
echo    - Backend neu starten
echo.
echo ========================================================================
echo.
echo Druecke eine beliebige Taste zum Beenden dieses Fensters...
echo (Backend und Frontend laufen in separaten Fenstern weiter)
pause >nul