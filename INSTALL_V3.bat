@echo off
title XIONIMUS AI v3.0.0 - Installation
color 0A

echo.
echo ==========================================
echo      XIONIMUS AI v3.0.0 - INSTALLATION
echo ==========================================
echo.

cd /d "%~dp0"

REM Prüfe neue Projektstruktur
if not exist "backend\main.py" (
    echo [ERROR] Backend\main.py nicht gefunden!
    echo [INFO] Stellen Sie sicher, dass Sie XIONIMUS v3.0.0 haben
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [ERROR] Frontend\package.json nicht gefunden!
    pause
    exit /b 1
)

echo [SUCCESS] Projektstruktur validiert
echo.

REM Python prüfen
echo [CHECK] Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden - installieren Sie Python 3.10+
    pause
    exit /b 1
)
python --version

REM Node.js prüfen
echo [CHECK] Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden - installieren Sie Node.js 18+
    pause
    exit /b 1
)
node --version

REM NPM prüfen
echo [CHECK] NPM...
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm nicht gefunden
    pause
    exit /b 1
)
npm --version

echo [SUCCESS] Alle Systemvoraussetzungen erfüllt
echo.

REM Backend installieren
echo [INSTALL] Backend Dependencies...
cd backend
python -m pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Backend installiert
) else (
    echo [WARNING] Backend Installation Probleme
)
cd ..

REM Frontend installieren
echo [INSTALL] Frontend Dependencies mit NPM...
cd frontend
npm install
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Frontend installiert
    if exist "node_modules" (
        echo [SUCCESS] node_modules erstellt
    )
) else (
    echo [WARNING] Frontend Installation Probleme
)
cd ..

echo.
echo ✅ INSTALLATION ABGESCHLOSSEN!
echo.
echo [START] Verwenden Sie:
echo    npm run start:all
echo.
echo [ACCESS] Dann öffnen Sie:
echo    http://localhost:3000
echo.
echo [SETUP] Konfigurieren Sie API-Keys in Settings
echo.

pause