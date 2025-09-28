@echo off
title Emergent-Next - Complete Platform
color 0A

echo.
echo ==========================================
echo    EMERGENT-NEXT - START PLATFORM
echo ==========================================
echo.

cd /d "%~dp0"

REM Prüfe Installation
if not exist "backend\.env" (
    echo [ERROR] Platform nicht installiert!
    echo [INFO] Führen Sie zuerst die Installation durch:
    echo         ./install.sh oder INSTALL_V3.bat
    pause
    exit /b 1
)

echo [INFO] Starte Complete Development Platform...
echo.

REM Starte Backend
echo [START] Backend wird gestartet...
start "Emergent-Next Backend" START_BACKEND.bat

REM Warte kurz
timeout /t 3 /nobreak >nul

REM Starte Frontend
echo [START] Frontend wird gestartet...
start "Emergent-Next Frontend" START_FRONTEND.bat

echo.
echo ✅ EMERGENT-NEXT GESTARTET!
echo.
echo 🌐 ZUGRIFF:
echo   → Platform: http://localhost:3000
echo   → API:      http://localhost:8001
echo   → Docs:     http://localhost:8001/docs
echo.
echo ⚠️ WICHTIG:
echo   → Lassen Sie beide Server-Fenster geöffnet
echo   → Konfigurieren Sie API-Keys in Settings
echo.
echo [AUTO] Browser öffnet in 10 Sekunden...
timeout /t 10 /nobreak >nul
start http://localhost:3000

echo [INFO] Platform gestartet - Browser sollte sich öffnen
pause