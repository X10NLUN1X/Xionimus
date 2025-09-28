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

REM Prüfe .env Datei
if not exist ".env" (
    echo [WARNING] .env Datei nicht gefunden - erstelle Standard-Konfiguration
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env
    echo [SUCCESS] Standard .env erstellt
)

REM Prüfe node_modules
if not exist "node_modules" (
    echo [WARNING] Dependencies nicht installiert - starte Installation...
    echo [INFO] Das kann einige Minuten dauern...
    yarn install
    if %ERRORLEVEL% NEQ 0 (
        echo [FALLBACK] yarn fehlgeschlagen - verwende npm...
        npm install
    )
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