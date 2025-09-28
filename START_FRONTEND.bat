@echo off
title XIONIMUS AI - Frontend Server
color 0A

echo.
echo ==========================================
echo    XIONIMUS AI - FRONTEND SERVER START
echo ==========================================
echo.

REM Wechsle ins richtige Verzeichnis
cd /d "%~dp0"

REM Prüfe Projektstruktur
if not exist "frontend\package.json" (
    echo [ERROR] Frontend nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus
    pause
    exit /b 1
)

REM Prüfe ob Installation durchgeführt wurde
if not exist "frontend\.env" (
    echo [ERROR] Frontend nicht installiert!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         WINDOWS_INSTALL.bat
    echo.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [ERROR] Frontend Dependencies nicht installiert!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         WINDOWS_INSTALL.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Starte XIONIMUS AI Frontend Server...
echo [INFO] Frontend läuft auf: http://localhost:3000
echo [INFO] LASSEN SIE DIESES FENSTER GEÖFFNET!
echo.

cd frontend

echo [START] XIONIMUS Frontend wird gestartet...
echo.
echo ========================================
echo   Frontend läuft auf http://localhost:3000
echo   NICHT SCHLIESSEN - Server läuft hier!
echo ========================================
echo.

REM Verwende npm run dev für Vite
echo [INFO] Starte Frontend mit Vite...
npm run dev