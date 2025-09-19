@echo off
title XIONIMUS AI - Frontend Server (Debug)
color 0B
echo.
echo ==========================================
echo      XIONIMUS AI - FRONTEND SERVER
echo ==========================================
echo.

REM Debug-Informationen anzeigen
echo [DEBUG] Aktuelles Verzeichnis: %CD%
echo [DEBUG] Script-Pfad: %~dp0
echo [DEBUG] Ziel-Verzeichnis: %~dp0frontend
echo.

REM Zum Hauptverzeichnis wechseln (falls aus anderem Ordner gestartet)
cd /d "%~dp0"
echo [DEBUG] Nach cd ins Hauptverzeichnis: %CD%
echo.

REM Ins Frontend Verzeichnis wechseln
if exist "frontend" (
    echo [SUCCESS] Frontend Verzeichnis gefunden
    cd frontend
    echo [DEBUG] Im Frontend Verzeichnis: %CD%
) else (
    echo [ERROR] Frontend Verzeichnis nicht gefunden!
    echo [DEBUG] Inhalt des aktuellen Verzeichnisses:
    dir /b
    echo.
    echo [LOSUNG] Starten Sie diese Datei aus dem Xionimus Hauptverzeichnis
    echo [INFO] Druecken Sie eine Taste zum Beenden...
    pause >nul
    exit /b 1
)
echo.

REM Pruefen ob package.json existiert
if not exist "package.json" (
    echo [ERROR] package.json nicht gefunden!
    echo [DEBUG] Inhalt des Frontend-Verzeichnisses:
    dir /b
    echo.
    echo [INFO] Druecken Sie eine Taste zum Beenden...
    pause >nul
    exit /b 1
)

echo [SUCCESS] package.json gefunden
echo.

REM Node.js verfügbarkeit pruefen
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js ist nicht installiert oder nicht im PATH!
    echo [LOSUNG] Installieren Sie Node.js 18+ von: https://nodejs.org
    echo [INFO] Fuehren Sie dann WINDOWS_INSTALL.bat erneut aus
    echo.
    echo [INFO] Druecken Sie eine Taste zum Beenden...
    pause >nul
    exit /b 1
)

echo [INFO] Node.js Version:
node --version
echo.

REM Yarn verfügbarkeit pruefen
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Yarn ist nicht installiert
    echo [FIX] Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Yarn Installation fehlgeschlagen!
        echo [FALLBACK] Verwende npm stattdessen...
        set USE_NPM=1
    ) else (
        echo [SUCCESS] Yarn installiert
    )
) else (
    echo [INFO] Yarn Version:
    yarn --version
)
echo.

REM .env Datei pruefen
if not exist ".env" (
    echo [ERROR] .env Datei nicht gefunden!
    echo [DEBUG] Inhalt des Frontend-Verzeichnisses:
    dir /b *.env 2>nul || echo "Keine .env Dateien gefunden"
    echo.
    echo [FIX] Erstelle .env Datei...
    echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
    echo WDS_SOCKET_PORT=3000>> .env
    echo [SUCCESS] .env Datei erstellt
) else (
    echo [SUCCESS] .env Datei gefunden
)

echo [INFO] Frontend Konfiguration:
echo ================================
type .env
echo ================================
echo.

REM node_modules pruefen
if not exist "node_modules" (
    echo [WARNING] node_modules nicht gefunden
    echo [FIX] Installiere Dependencies...
    if defined USE_NPM (
        npm install
    ) else (
        yarn install
    )
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Dependencies Installation fehlgeschlagen!
        echo [DEBUG] Letzter Exit Code: %ERRORLEVEL%
        echo.
        echo [INFO] Druecken Sie eine Taste zum Beenden...
        pause >nul
        exit /b 1
    )
    echo [SUCCESS] Dependencies installiert
) else (
    echo [SUCCESS] node_modules gefunden
)
echo.

REM Backend Verbindung pruefen (optional)
echo [CHECK] Pruefe Backend Verbindung...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 5; Write-Host '[SUCCESS] Backend ist erreichbar' } catch { Write-Host '[WARNING] Backend nicht erreichbar - starten Sie START_BACKEND.bat zuerst' }" 2>nul
echo.

echo [START] Starte Frontend Development Server...
echo [INFO] Port: 3000 (oder nächster verfügbarer)
echo [INFO] Auto-Browser: Aktiviert
echo.
echo [WICHTIG] Fenster offen lassen!
echo [STOP] Zum Beenden: Ctrl+C
echo.

REM Browser nach 15 Sekunden öffnen
start /min cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:3000 && exit"

echo ======================================
echo   Frontend Server wird gestartet...
echo ======================================
echo.

REM Frontend starten mit detailliertem Output
if defined USE_NPM (
    echo [INFO] Verwende npm start...
    npm start
) else (
    echo [INFO] Verwende yarn start...
    yarn start
)

REM Falls hier angekommen - Fehler aufgetreten
echo.
color 0C
echo [STOPPED] Frontend Server wurde beendet oder ist fehlgeschlagen!
echo [DEBUG] Exit Code: %ERRORLEVEL%
echo.
echo [TROUBLESHOOTING]:
echo   1. Node.js nicht installiert: https://nodejs.org
echo   2. Dependencies fehlen: Loeschen Sie node_modules und starten neu
echo   3. Port 3000 belegt: React wird automatisch anderen Port waehlen
echo   4. .env Datei Problem: Wurde automatisch neu erstellt
echo.
echo [LOGS] Scrollen Sie nach oben um Fehlerdetails zu sehen
echo.
echo [INFO] Fenster bleibt offen fuer Debugging...
pause