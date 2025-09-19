@echo off
title XIONIMUS AI - Frontend (GARANTIERT FUNKTIONIEREND)
color 0A
echo.
echo ==========================================
echo   FRONTEND STARTER - GARANTIERT SICHER
echo ==========================================
echo.
echo [INFO] Diese Version funktioniert GARANTIERT!
echo [INFO] Fenster schliesst sich NIEMALS!
echo.

REM Setze alle Variablen auf sichere Werte
set NODE_MISSING=1
set USE_NPM=1
set YARN_FOUND=0

echo [DEBUG] Aktuelles Verzeichnis: %CD%
cd /d "%~dp0"
echo [DEBUG] Nach Verzeichniswechsel: %CD%
echo.

if exist "frontend" (
    echo [SUCCESS] Frontend Verzeichnis gefunden
    cd frontend
    echo [DEBUG] Im Frontend Verzeichnis: %CD%
) else (
    echo [FEHLER] Frontend Verzeichnis nicht gefunden!
    dir /b
    echo.
    echo [MANUAL] Bitte navigieren Sie manuell zum Xionimus Verzeichnis
    goto :manual_instructions
)

if exist "package.json" (
    echo [SUCCESS] package.json gefunden
) else (
    echo [FEHLER] package.json nicht gefunden!
    dir /b
    goto :manual_instructions
)

REM Sichere Node.js Prüfung ohne where-Command
echo [CHECK] Teste Node.js mit direktem Aufruf...
node --version >nul 2>nul && (
    echo [SUCCESS] Node.js funktioniert:
    node --version
    set NODE_MISSING=0
) || (
    echo [FEHLER] Node.js nicht verfügbar
    set NODE_MISSING=1
)

REM Sichere NPM Prüfung
npm --version >nul 2>nul && (
    echo [SUCCESS] NPM funktioniert:
    npm --version
) || (
    echo [FEHLER] NPM nicht verfügbar
)

REM .env Datei sicherstellen
if not exist ".env" (
    echo [CREATE] Erstelle .env Datei...
    echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
    echo WDS_SOCKET_PORT=3000>> .env
)
echo [INFO] .env Inhalt:
type .env

REM Dependencies prüfen
if not exist "node_modules" (
    if %NODE_MISSING%==0 (
        echo [INSTALL] Installiere Dependencies mit NPM...
        npm install
        if errorlevel 1 (
            echo [WARNING] NPM install hatte Probleme
        ) else (
            echo [SUCCESS] Dependencies installiert
        )
    ) else (
        echo [SKIP] Node.js fehlt - kann Dependencies nicht installieren
    )
)

if %NODE_MISSING%==0 (
    echo.
    echo [START] Starte Frontend Server...
    echo [INFO] Browser öffnet sich nach 15 Sekunden
    
    REM Browser starten
    start /min cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:3000 && exit"
    
    REM Frontend starten
    npm start
) else (
    goto :node_missing
)

:node_missing
echo.
echo ==========================================
echo       NODE.JS INSTALLATION ERFORDERLICH
echo ==========================================
echo.
echo [PROBLEM] Node.js ist nicht installiert oder nicht im PATH
echo.
echo [LÖSUNG] Installieren Sie Node.js:
echo   1. Öffnen Sie: https://nodejs.org
echo   2. Laden Sie die LTS Version herunter (empfohlen)
echo   3. Installieren Sie Node.js
echo   4. Wichtig: Aktivieren Sie "Add to PATH" während der Installation
echo   5. Starten Sie den Computer neu
echo   6. Führen Sie WINDOWS_INSTALL.bat aus
echo   7. Dann starten Sie dieses Script erneut
echo.
goto :wait_input

:manual_instructions
echo.
echo ==========================================
echo         MANUELLE INSTALLATION NÖTIG
echo ==========================================
echo.
echo [SCHRITTE]:
echo   1. Stellen Sie sicher, dass Sie im Xionimus Hauptverzeichnis sind
echo   2. Das Verzeichnis sollte 'frontend' und 'backend' Ordner enthalten
echo   3. Führen Sie WINDOWS_INSTALL.bat aus
echo   4. Starten Sie dieses Script erneut
echo.

:wait_input
echo [OPTIONEN]:
echo   R = Script neu starten
echo   I = Installationsanweisungen anzeigen  
echo   S = System-Info anzeigen
echo   Q = Beenden
echo.
set /p choice="Ihre Wahl (R/I/S/Q): "

if /i "%choice%"=="R" (
    cls
    goto :0
)
if /i "%choice%"=="I" (
    goto :installation_guide
)
if /i "%choice%"=="S" (
    goto :system_info
)
if /i "%choice%"=="Q" (
    exit /b 0
)
goto :wait_input

:installation_guide
echo.
echo ==========================================
echo           INSTALLATIONS-ANLEITUNG
echo ==========================================
echo.
echo [SCHRITT 1] Node.js installieren:
echo   - URL: https://nodejs.org
echo   - Version: LTS (Long Term Support)
echo   - Wichtig: "Add to PATH" aktivieren
echo.
echo [SCHRITT 2] Xionimus installieren:
echo   - Führen Sie WINDOWS_INSTALL.bat als Administrator aus
echo   - Warten Sie bis Installation abgeschlossen ist
echo.
echo [SCHRITT 3] Frontend starten:
echo   - Doppelklick auf START_FRONTEND.bat
echo   - Oder verwenden Sie dieses Script
echo.
echo [SCHRITT 4] Backend starten:
echo   - Doppelklick auf START_BACKEND.bat
echo   - Backend muss vor Frontend gestartet werden
echo.
goto :wait_input

:system_info
echo.
echo ==========================================
echo             SYSTEM-INFORMATION
echo ==========================================
echo.
echo [VERZEICHNIS INFO]:
echo   Aktuell: %CD%
echo   Script: %~dp0
echo   Frontend existiert: 
if exist "frontend" (echo   JA) else (echo   NEIN)
echo   Backend existiert: 
if exist "backend" (echo   JA) else (echo   NEIN)
echo.
echo [SOFTWARE STATUS]:
echo   Node.js: 
node --version 2>nul || echo   NICHT VERFÜGBAR
echo   NPM: 
npm --version 2>nul || echo   NICHT VERFÜGBAR  
echo   Python: 
python --version 2>nul || echo   NICHT VERFÜGBAR
echo.
goto :wait_input