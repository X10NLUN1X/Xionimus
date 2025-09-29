@echo off
title Emergent-Next - Frontend
color 0A

echo.
echo ==========================================
echo    EMERGENT-NEXT - FRONTEND SERVER
echo ==========================================
echo.

cd /d "%~dp0"

REM Prüfe Projektstruktur
if not exist "frontend\package.json" (
    echo [ERROR] Frontend nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem emergent-next Verzeichnis aus
    pause
    exit /b 1
)

REM Prüfe Installation
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend Dependencies nicht installiert!
    echo [INFO] Führen Sie zuerst die Installation durch:
    echo         ./install.sh oder INSTALL_V3.bat
    pause
    exit /b 1
)

echo [INFO] Starte Emergent-Next Frontend...
echo [INFO] Platform: http://localhost:3000
echo.

cd frontend
npm run dev