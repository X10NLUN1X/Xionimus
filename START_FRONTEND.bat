@echo off
title XIONIMUS AI - Frontend Server
color 0B
echo.
echo ==========================================
echo      XIONIMUS AI - FRONTEND SERVER
echo ==========================================
echo.

REM Ins Frontend Verzeichnis wechseln
cd /d "%~dp0frontend"

REM Pruefen ob im richtigen Verzeichnis
if not exist "package.json" (
    echo [ERROR] package.json nicht gefunden!
    echo [INFO] Bitte starten Sie diese Datei aus dem Xionimus Hauptverzeichnis
    pause
    exit /b 1
)

REM Node.js Version anzeigen
echo [INFO] Node.js Version:
node --version
echo [INFO] Yarn Version:
yarn --version
echo.

REM .env Datei pruefen
if not exist ".env" (
    echo [ERROR] .env Datei nicht gefunden!
    echo [INFO] Bitte fuehren Sie zuerst WINDOWS_INSTALL.bat aus
    pause
    exit /b 1
)

echo [INFO] Frontend Konfiguration:
echo ================================
type .env
echo ================================
echo.

REM Backend Verbindung pruefen
echo [CHECK] Pruefe Backend Verbindung...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 5; Write-Host '[SUCCESS] Backend erreichbar' } catch { Write-Host '[WARNING] Backend nicht erreichbar - starten Sie START_BACKEND.bat' }"
echo.

REM Dependencies pruefen
if not exist "node_modules" (
    echo [WARNING] node_modules nicht gefunden
    echo [FIX] Installiere Dependencies...
    yarn install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Yarn install fehlgeschlagen!
        echo [FIX] Versuche mit npm...
        npm install
    )
) else (
    echo [SUCCESS] Dependencies gefunden
)
echo.

REM Port pruefen
netstat -an | find ":3000 " >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 3000 bereits belegt!
    echo [INFO] Frontend laeuft moeglicherweise bereits
    echo [INFO] React wird einen anderen Port verwenden
)
echo.

echo [START] Starte Xionimus AI Frontend...
echo [INFO] React Development Server
echo [INFO] Standard Port: 3000
echo [INFO] Auto-Browser: Aktiviert
echo.
echo [WICHTIG] Lassen Sie dieses Fenster geoeffnet!
echo [STOP] Zum Beenden: Ctrl+C
echo.
echo ==========================================
echo       Frontend Server wird gestartet...
echo ==========================================
echo.

REM Browser automatisch oeffnen nach 15 Sekunden
start /min cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:3000 && exit"

REM Frontend Server starten
yarn start

REM Falls Server beendet wird
echo.
color 0C
echo [STOPPED] Frontend Server wurde beendet!
echo.
echo [TROUBLESHOOTING]:
echo   - Port 3000 belegt: React verwendet automatisch anderen Port
echo   - Backend nicht erreichbar: START_BACKEND.bat starten
echo   - Dependencies Fehler: yarn install oder npm install
echo   - .env Fehler: WINDOWS_INSTALL.bat erneut ausfuehren
echo.
echo [RESTART] Um neu zu starten, doppelklicken Sie erneut auf diese Datei
echo.
pause