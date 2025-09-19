@echo off
title XIONIMUS AI - Frontend Test
echo ==========================================
echo     FRONTEND DIAGNOSE UND TEST
echo ==========================================
echo.

echo [TEST 1] Aktuelles Verzeichnis:
echo %CD%
echo.

echo [TEST 2] Verzeichnis-Inhalt:
dir /b
echo.

echo [TEST 3] Frontend Verzeichnis vorhanden?
if exist "frontend" (
    echo JA - Frontend Verzeichnis gefunden
) else (
    echo NEIN - Frontend Verzeichnis NICHT gefunden!
)
echo.

echo [TEST 4] Node.js installiert?
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo JA - Node.js gefunden
    node --version
) else (
    echo NEIN - Node.js NICHT installiert!
)
echo.

echo [TEST 5] Yarn installiert?
where yarn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo JA - Yarn gefunden
    yarn --version
) else (
    echo NEIN - Yarn nicht installiert (npm verwenden)
)
echo.

echo [TEST 6] Package.json im Frontend?
if exist "frontend\package.json" (
    echo JA - Frontend package.json gefunden
) else (
    echo NEIN - Frontend package.json NICHT gefunden!
)
echo.

echo [TEST 7] .env Datei im Frontend?
if exist "frontend\.env" (
    echo JA - Frontend .env gefunden
    echo Inhalt:
    type frontend\.env
) else (
    echo NEIN - Frontend .env NICHT gefunden!
    echo Erstelle .env Datei...
    echo REACT_APP_BACKEND_URL=http://localhost:8001> frontend\.env
    echo WDS_SOCKET_PORT=3000>> frontend\.env
    echo .env Datei erstellt!
)
echo.

echo [TEST 8] node_modules im Frontend?
if exist "frontend\node_modules" (
    echo JA - Dependencies installiert
) else (
    echo NEIN - Dependencies NICHT installiert!
    echo Installiere Dependencies...
    cd frontend
    where yarn >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        yarn install
    ) else (
        npm install
    )
    cd ..
    echo Dependencies Installation abgeschlossen
)
echo.

echo ==========================================
echo      MANUELLER FRONTEND START
echo ==========================================
echo.
echo Versuche Frontend manuell zu starten...
echo.

cd frontend
echo Aktuelles Verzeichnis: %CD%
echo.

where yarn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Starte mit Yarn...
    yarn start
) else (
    echo Starte mit NPM...
    npm start
)

echo.
echo ==========================================
echo Falls Fehler auftreten, sehen Sie sie oben
echo ==========================================
pause