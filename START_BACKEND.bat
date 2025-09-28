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
if not exist "backend\server.py" (
    echo [ERROR] Backend nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Script aus dem XIONIMUS Hauptverzeichnis aus
    pause
    exit /b 1
)

echo [INFO] Starte XIONIMUS AI Backend Server...
echo [INFO] Backend läuft auf: http://localhost:8001
echo [INFO] LASSEN SIE DIESES FENSTER GEÖFFNET!
echo.

cd backend

REM Prüfe .env Datei
if not exist ".env" (
    echo [WARNING] .env Datei nicht gefunden - erstelle Standard-Konfiguration
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    ) > .env
    echo [SUCCESS] Standard .env erstellt
)

echo [START] XIONIMUS Backend wird gestartet...
echo.
echo ========================================
echo   Backend läuft auf http://localhost:8001
echo   NICHT SCHLIESSEN - Server läuft hier!
echo ========================================
echo.

python server.py