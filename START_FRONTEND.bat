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

echo [INFO] Starte XIONIMUS AI Frontend Server...
echo [INFO] Frontend läuft auf: http://localhost:3000
echo [INFO] LASSEN SIE DIESES FENSTER GEÖFFNET!
echo.

cd frontend

REM Prüfe ob Installation durchgeführt wurde
if not exist ".env" (
    echo [ERROR] .env Datei nicht gefunden!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         install.bat
    echo.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [ERROR] Dependencies nicht installiert!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         install.bat
    echo.
    pause
    exit /b 1
)

echo [START] XIONIMUS Frontend wird gestartet...
echo.
echo ========================================
echo   Frontend läuft auf http://localhost:3000
echo   NICHT SCHLIESSEN - Server läuft hier!
echo ========================================
echo.

REM Verwende yarn falls verfügbar, sonst npm
where yarn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    yarn start
) else (
    npm start
)