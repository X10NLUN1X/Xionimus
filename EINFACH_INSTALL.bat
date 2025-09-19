@echo off
title XIONIMUS AI - Einfache Installation
color 0B
echo ==========================================
echo   XIONIMUS AI - EINFACHE INSTALLATION
echo ==========================================
echo.
echo [INFO] Diese Installation prueft nur und installiert keine Software automatisch
echo [INFO] Sie muessen Python und Node.js manuell installieren falls sie fehlen
echo.

REM ==========================================
echo [CHECK 1/5] PYTHON PRUEFEN
REM ==========================================
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Python nicht gefunden!
    echo [MANUELL] Bitte installieren Sie Python von: https://python.org
    echo [WICHTIG] Aktivieren Sie "Add Python to PATH" bei der Installation!
    echo.
    set PYTHON_MISSING=1
) else (
    echo [SUCCESS] Python gefunden:
    python --version
    echo [SUCCESS] Pip gefunden:
    python -m pip --version
)
echo.

REM ==========================================
echo [CHECK 2/5] NODE.JS PRUEFEN  
REM ==========================================
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Node.js nicht gefunden!
    echo [MANUELL] Bitte installieren Sie Node.js von: https://nodejs.org
    echo [TIPP] Waehlen Sie die LTS Version
    echo.
    set NODEJS_MISSING=1
) else (
    echo [SUCCESS] Node.js gefunden:
    node --version
    echo [SUCCESS] NPM gefunden:
    npm --version
)
echo.

REM ==========================================
echo [CHECK 3/5] PROJEKTVERZEICHNISSE ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle Projektverzeichnisse...
if not exist "uploads" mkdir uploads && echo [OK] uploads\ erstellt
if not exist "sessions" mkdir sessions && echo [OK] sessions\ erstellt  
if not exist "logs" mkdir logs && echo [OK] logs\ erstellt
echo.

REM ==========================================
echo [CHECK 4/5] .ENV DATEIEN ERSTELLEN
REM ==========================================
echo [CREATE] Erstelle .env Dateien...

REM Frontend .env
if not exist "frontend\.env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001> frontend\.env
    echo WDS_SOCKET_PORT=3000>> frontend\.env
    echo [OK] frontend\.env erstellt
) else (
    echo [OK] frontend\.env existiert bereits
)

REM Backend .env  
if not exist "backend\.env" (
    echo MONGO_URL="mongodb://localhost:27017"> backend\.env
    echo DB_NAME="xionimus_ai">> backend\.env
    echo CORS_ORIGINS="*">> backend\.env
    echo.>> backend\.env
    echo # AI API Keys>> backend\.env
    echo # PERPLEXITY_API_KEY=pplx-your_key_here>> backend\.env
    echo # ANTHROPIC_API_KEY=sk-ant-your_key_here>> backend\.env
    echo [OK] backend\.env erstellt
) else (
    echo [OK] backend\.env existiert bereits
)
echo.

REM ==========================================
echo [CHECK 5/5] DEPENDENCIES INSTALLIEREN
REM ==========================================

if defined PYTHON_MISSING (
    echo [SKIP] Python Dependencies - Python nicht verfuegbar
) else (
    echo [INSTALL] Python Dependencies...
    cd backend
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Python Dependencies installiert
    ) else (
        echo [WARNUNG] Python Dependencies Installation mit Fehlern
    )
    cd ..
)

if defined NODEJS_MISSING (
    echo [SKIP] Node.js Dependencies - Node.js nicht verfuegbar
) else (
    echo [INSTALL] Node.js Dependencies...
    
    REM Yarn installieren falls nicht vorhanden
    where yarn >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [INSTALL] Installiere Yarn...
        npm install -g yarn
    )
    
    cd frontend
    yarn install
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Node.js Dependencies installiert
    ) else (
        echo [WARNUNG] Node.js Dependencies Installation mit Fehlern
    )
    cd ..
)

echo.
echo ==========================================
echo   INSTALLATION ABGESCHLOSSEN
echo ==========================================
echo.

if defined PYTHON_MISSING (
    echo [TODO] Installieren Sie Python: https://python.org
)

if defined NODEJS_MISSING (
    echo [TODO] Installieren Sie Node.js: https://nodejs.org
)

if not defined PYTHON_MISSING (
    if not defined NODEJS_MISSING (
        echo [SUCCESS] Alles bereit!
        echo.
        echo [START] Jetzt koennen Sie starten:
        echo   1. START_BACKEND.bat
        echo   2. START_FRONTEND.bat  
        echo.
    )
)

echo [FILES] Diese Dateien stehen zur Verfuegung:
echo   - START_BACKEND.bat (Backend Server)
echo   - START_FRONTEND.bat (Frontend Server)
echo   - SIMPLE_TEST.bat (Test-Skript)
echo   - FRONTEND_DEBUG.bat (Debug-Version)
echo.
pause