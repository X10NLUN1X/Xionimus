@echo off
title XIONIMUS AI - Frontend Debug (Fenster bleibt offen)
color 0A
echo ==========================================
echo     FRONTEND DEBUG - FENSTER BLEIBT OFFEN
echo ==========================================
echo.
echo [INFO] Dieses Fenster schliesst sich NIEMALS automatisch!
echo.

:main_loop
echo [DEBUG] Script gestartet um: %time%
echo [DEBUG] Aktuelles Verzeichnis: %CD%
echo [DEBUG] Command Line Args: %*
echo.

REM Teste jede einzelne Komponente mit Fehlerbehandlung

echo [SCHRITT 1] Teste Verzeichnis-Struktur...
if exist "frontend" (
    echo [OK] Frontend Verzeichnis gefunden
) else (
    echo [FEHLER] Frontend Verzeichnis NICHT gefunden!
    echo [DEBUG] Verzeichnis-Inhalt:
    dir /b
    goto :error_exit
)

echo [SCHRITT 2] Wechsle ins Frontend Verzeichnis...
cd frontend 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Kann nicht ins Frontend Verzeichnis wechseln!
    goto :error_exit
)
echo [OK] Im Frontend Verzeichnis: %CD%

echo [SCHRITT 3] Teste Node.js...
node --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Node.js nicht gefunden oder nicht funktional!
    echo [INFO] Installieren Sie Node.js von https://nodejs.org
    goto :error_exit
)
echo [OK] Node.js Version:
node --version

echo [SCHRITT 4] Teste package.json...
if exist "package.json" (
    echo [OK] package.json gefunden
) else (
    echo [FEHLER] package.json nicht gefunden!
    echo [DEBUG] Frontend Verzeichnis Inhalt:
    dir /b
    goto :error_exit
)

echo [SCHRITT 5] Teste .env Datei...
if exist ".env" (
    echo [OK] .env Datei gefunden
    echo [INFO] Inhalt:
    type .env
) else (
    echo [WARNUNG] .env Datei nicht gefunden - erstelle sie...
    echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
    echo WDS_SOCKET_PORT=3000>> .env
    echo [OK] .env Datei erstellt
)

echo [SCHRITT 6] Teste Yarn/NPM...
where yarn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Yarn gefunden
    yarn --version
    set "PACKAGE_MANAGER=yarn"
) else (
    echo [INFO] Yarn nicht gefunden, verwende NPM
    npm --version
    set "PACKAGE_MANAGER=npm"
)

echo [SCHRITT 7] Teste Dependencies...
if exist "node_modules" (
    echo [OK] node_modules gefunden
) else (
    echo [INFO] Installiere Dependencies mit %PACKAGE_MANAGER%...
    if "%PACKAGE_MANAGER%"=="yarn" (
        yarn install
    ) else (
        npm install
    )
    echo [INFO] Dependencies Installation abgeschlossen
)

echo.
echo ==========================================
echo     ALLE TESTS BESTANDEN - STARTE FRONTEND
echo ==========================================
echo.

echo [INFO] Starte Frontend mit %PACKAGE_MANAGER%...
if "%PACKAGE_MANAGER%"=="yarn" (
    yarn start
) else (
    npm start
)

:error_exit
echo.
echo ==========================================
echo     FEHLER ODER BEENDIGUNG
echo ==========================================
echo.
echo [INFO] Exit Code: %ERRORLEVEL%
echo [INFO] Zeit: %time%
echo.
echo [OPTIONEN]:
echo   1. Druecken Sie 'R' und Enter um neu zu starten
echo   2. Druecken Sie 'Q' und Enter um zu beenden
echo   3. Druecken Sie Enter um Details zu sehen
echo.

set /p choice="Ihre Wahl (R/Q/Enter): "
if /i "%choice%"=="R" goto :main_loop
if /i "%choice%"=="Q" exit /b 0

echo.
echo [SYSTEM INFO]:
echo Node.js Status: 
where node 2>nul || echo "Node.js nicht gefunden"
echo.
echo Yarn Status:
where yarn 2>nul || echo "Yarn nicht gefunden"  
echo.
echo NPM Status:
where npm 2>nul || echo "NPM nicht gefunden"
echo.
echo Verzeichnis Status:
echo Frontend Verzeichnis: %CD%
dir /b frontend 2>nul || echo "Frontend Verzeichnis nicht erreichbar"
echo.

goto :error_exit