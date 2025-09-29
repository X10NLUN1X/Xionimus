@echo off
title Emergent-Next - Backend
color 0A

echo.
echo ==========================================
echo    EMERGENT-NEXT - BACKEND SERVER
echo ==========================================
echo.

cd /d "%~dp0"

REM Prüfe Projektstruktur
if not exist "backend\main.py" (
    echo [ERROR] Backend nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem emergent-next Verzeichnis aus
    pause
    exit /b 1
)

REM Prüfe .env
if not exist "backend\.env" (
    echo [ERROR] Backend nicht konfiguriert!
    echo [INFO] Führen Sie zuerst die Installation durch:
    echo         ./install.sh oder INSTALL_V3.bat
    pause
    exit /b 1
)

echo [INFO] Starte Emergent-Next Backend...
echo [INFO] API: http://localhost:8001
echo [INFO] Docs: http://localhost:8001/docs
echo.

cd backend
python main.py