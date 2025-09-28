@echo off
title XIONIMUS AI - Backend Server
color 0A

echo.
echo ==========================================
echo    XIONIMUS AI - BACKEND SERVER START
echo ==========================================
echo.

REM Wechsle ins richtige Verzeichnis
cd /d "%~dp0"

REM Prüfe Projektstruktur
if not exist "backend\main.py" (
    echo [ERROR] Backend nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus
    pause
    exit /b 1
)

REM Prüfe ob Installation durchgeführt wurde
if not exist "backend\.env" (
    echo [ERROR] Backend nicht installiert!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         WINDOWS_INSTALL.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Starte XIONIMUS AI Backend Server...
echo [INFO] Backend läuft auf: http://localhost:8001
echo [INFO] LASSEN SIE DIESES FENSTER GEÖFFNET!
echo.

cd backend

echo [START] XIONIMUS Backend wird gestartet...
echo.
echo ========================================
echo   Backend läuft auf http://localhost:8001
echo   NICHT SCHLIESSEN - Server läuft hier!
echo ========================================
echo.

python main.py