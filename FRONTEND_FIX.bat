@echo off
title XIONIMUS AI - Frontend (FENSTER BLEIBT OFFEN)
color 0A
echo ==========================================
echo     FRONTEND - FENSTER BLEIBT IMMER OFFEN
echo ==========================================
echo.
echo [INFO] Dieses Fenster schliesst sich NIE automatisch!
echo.

REM IMMER erstmal anzeigen wo wir sind
echo [DEBUG] Aktuelles Verzeichnis: %CD%
echo [DEBUG] Script-Pfad: %~dp0
echo.

REM Hauptverzeichnis finden
cd /d "%~dp0"
echo [DEBUG] Nach Verzeichniswechsel: %CD%
echo.

REM Frontend Verzeichnis prüfen - OHNE EXIT!
if exist "frontend" (
    echo [SUCCESS] Frontend Verzeichnis gefunden
    cd frontend
    echo [DEBUG] Im Frontend Verzeichnis: %CD%
) else (
    echo [FEHLER] Frontend Verzeichnis nicht gefunden!
    echo [DEBUG] Verfügbare Verzeichnisse:
    dir /b
    echo.
    echo [INFO] Trotzdem weitermachen - kein Exit!
    goto :show_diagnostics
)

REM package.json prüfen - OHNE EXIT!
if exist "package.json" (
    echo [SUCCESS] package.json gefunden
) else (
    echo [FEHLER] package.json nicht gefunden!
    echo [DEBUG] Dateien im Frontend Verzeichnis:
    dir /b
    echo.
    echo [INFO] Trotzdem weitermachen - kein Exit!
)

REM Node.js prüfen - OHNE EXIT!
echo [CHECK] Prüfe Node.js Installation...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Node.js ist NICHT installiert!
    echo.
    echo [LÖSUNG] Installieren Sie Node.js:
    echo   1. Gehen Sie zu: https://nodejs.org
    echo   2. Laden Sie die LTS Version herunter
    echo   3. Installieren Sie Node.js
    echo   4. Starten Sie dieses Script erneut
    echo.
    echo [INFO] Script läuft trotzdem weiter für Diagnose...
    set NODE_MISSING=1
) else (
    echo [SUCCESS] Node.js gefunden:
    node --version
    set NODE_MISSING=0
)

REM .env Datei prüfen und erstellen
echo.
echo [CHECK] Prüfe .env Datei...
if exist ".env" (
    echo [SUCCESS] .env Datei gefunden
    echo [INHALT]:
    type .env
) else (
    echo [INFO] .env Datei nicht gefunden - erstelle sie...
    echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
    echo WDS_SOCKET_PORT=3000>> .env
    echo [SUCCESS] .env Datei erstellt
    echo [INHALT]:
    type .env
)

:show_diagnostics
echo.
echo ==========================================
echo           DIAGNOSE ABGESCHLOSSEN
echo ==========================================
echo.
echo [ZUSAMMENFASSUNG]:
if %NODE_MISSING%==1 (
    echo   - Node.js: FEHLT - muss installiert werden
    echo   - Grund für sofortiges Schließen: Node.js Check fehlgeschlagen
) else (
    echo   - Node.js: OK
)

if exist "package.json" (
    echo   - package.json: OK
) else (
    echo   - package.json: FEHLT
)

if exist ".env" (
    echo   - .env Datei: OK
) else (
    echo   - .env Datei: FEHLT
)

echo.
echo [HAUPTPROBLEM IDENTIFIZIERT]:
echo   Die BAT-Dateien pruefen Node.js und schliessen sofort
echo   wenn Node.js fehlt - BEVOR die pause-Befehle erreicht werden!
echo.

if %NODE_MISSING%==1 (
    echo [NÄCHSTE SCHRITTE]:
    echo   1. Installieren Sie Node.js von https://nodejs.org
    echo   2. Starten Sie EINFACH_INSTALL.bat
    echo   3. Dann START_FRONTEND.bat verwenden
) else (
    echo [FRONTEND STARTEN]:
    echo   Versuche Frontend zu starten...
    npm start
)

echo.
echo ==========================================
echo    FENSTER BLEIBT OFFEN FÜR DEBUGGING
echo ==========================================
echo.
echo Druecken Sie eine beliebige Taste um zu beenden...
pause >nul