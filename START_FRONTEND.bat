@echo off
title XIONIMUS AI - Frontend Server (FENSTER BLEIBT OFFEN)
color 0A
echo.
echo ==========================================
echo     XIONIMUS AI - FRONTEND SERVER
echo     FENSTER BLEIBT IMMER OFFEN
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

REM Node.js prüfen - ROBUSTE WINDOWS BATCH METHODE!
echo [CHECK] Prüfe Node.js Installation...
set NODE_FOUND=0
call :check_node_js
if %NODE_FOUND%==0 (
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

REM Yarn prüfen - ROBUSTE METHODE
echo [CHECK] Prüfe Yarn Installation...
set YARN_FOUND=0
call :check_yarn
if %YARN_FOUND%==0 (
    echo [INFO] Yarn nicht gefunden - verwende NPM
    set USE_NPM=1
) else (
    echo [SUCCESS] Yarn gefunden:
    yarn --version
    set USE_NPM=0
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

REM Dependencies prüfen
echo.
echo [CHECK] Prüfe Dependencies...
if exist "node_modules" (
    echo [SUCCESS] node_modules gefunden
) else (
    echo [INFO] node_modules nicht gefunden - installiere Dependencies...
    if %NODE_MISSING%==0 (
        if %USE_NPM%==1 (
            echo [INSTALL] Mit NPM...
            npm install
        ) else (
            echo [INSTALL] Mit Yarn...
            yarn install
        )
        echo [SUCCESS] Dependencies installiert
    ) else (
        echo [SKIP] Node.js fehlt - kann Dependencies nicht installieren
    )
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
    echo   - Grund für Probleme: Node.js Check fehlgeschlagen
) else (
    echo   - Node.js: OK
)

if %USE_NPM%==1 (
    echo   - Package Manager: NPM (Yarn nicht verfügbar)
) else (
    echo   - Package Manager: Yarn
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

if exist "node_modules" (
    echo   - Dependencies: OK
) else (
    echo   - Dependencies: FEHLEN
)

echo.
if %NODE_MISSING%==1 (
    echo [NÄCHSTE SCHRITTE]:
    echo   1. Installieren Sie Node.js von https://nodejs.org
    echo   2. Starten Sie WINDOWS_INSTALL.bat erneut
    echo   3. Dann dieses Script verwenden
    echo.
    echo [WARTEN] Dieses Fenster bleibt offen für weitere Diagnose...
    goto :wait_forever
) else (
    echo [FRONTEND STARTEN]:
    echo   Versuche Frontend zu starten...
    echo.
    
    REM Browser nach 15 Sekunden öffnen
    start /min cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:3000 && exit"
    
    if %USE_NPM%==1 (
        npm start
    ) else (
        yarn start
    )
)

:wait_forever
echo.
echo ==========================================
echo    FENSTER BLEIBT OFFEN FÜR DEBUGGING
echo ==========================================
echo.
echo [OPTIONEN]:
echo   R = Neustart des Scripts
echo   Q = Beenden
echo   Enter = System-Info anzeigen
echo.

set /p choice="Ihre Wahl (R/Q/Enter): "
if /i "%choice%"=="R" goto :0
if /i "%choice%"=="Q" exit /b 0

echo.
echo [SYSTEM INFO]:
echo Node.js Status: 
where node 2>nul || echo "Node.js nicht gefunden"
echo.
echo NPM Status:
where npm 2>nul || echo "NPM nicht gefunden"
echo.
echo Yarn Status:
where yarn 2>nul || echo "Yarn nicht gefunden"
echo.
echo Python Status:
where python 2>nul || echo "Python nicht gefunden"
echo.
goto :wait_forever