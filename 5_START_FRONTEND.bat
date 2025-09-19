@echo off
chcp 65001 >nul
echo =====================================
echo   XIONIMUS AI - FRONTEND STARTER
echo =====================================
echo.

REM Prüfen ob frontend Verzeichnis existiert
if not exist "frontend" (
    echo [ERROR] frontend Verzeichnis nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Skript im Xionimus Hauptverzeichnis aus
    pause
    exit /b 1
)

REM Prüfen ob .env Datei existiert
if not exist "frontend\.env" (
    echo [ERROR] frontend\.env Datei nicht gefunden!
    echo [INFO] Bitte erstellen Sie die .env Datei mit: 2_SETUP_ENV_FILES.bat
    pause
    exit /b 1
)

REM Prüfen ob Node.js installiert ist
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js ist nicht installiert oder nicht im PATH!
    echo [INFO] Bitte installieren Sie Node.js 18+ von: https://nodejs.org
    pause
    exit /b 1
)

REM Node.js Version prüfen
echo [INFO] Node.js Version:
node --version

REM Prüfen ob yarn installiert ist
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Yarn ist nicht installiert. Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fehler beim Installieren von Yarn!
        pause
        exit /b 1
    )
    echo [SUCCESS] Yarn installiert
)

echo [INFO] Yarn Version:
yarn --version

REM Ins Frontend Verzeichnis wechseln
cd frontend

REM Prüfen ob package.json existiert
if not exist "package.json" (
    echo [ERROR] package.json nicht gefunden!
    pause
    exit /b 1
)

REM Prüfen ob node_modules existiert
if not exist "node_modules" (
    echo [INFO] node_modules nicht gefunden. Installiere Dependencies...
    yarn install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fehler beim Installieren der Dependencies!
        echo [INFO] Versuchen Sie manuell: cd frontend && yarn install
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installiert
) else (
    echo [SUCCESS] Dependencies bereits installiert
)

REM Prüfen ob Backend läuft
echo [INFO] Prüfe Backend Verbindung...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/api/health' -TimeoutSec 5; Write-Host '[SUCCESS] Backend ist erreichbar' } catch { Write-Host '[WARNING] Backend ist nicht erreichbar auf Port 8001' }"

REM Prüfen ob Port 3000 bereits belegt ist
netstat -an | find "3000" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 3000 ist bereits belegt!
    echo [INFO] Das Frontend wird möglicherweise einen anderen Port verwenden
    echo.
)

echo [INFO] .env Datei Inhalt:
echo ========================
type .env
echo ========================
echo.

echo [INFO] Starte Xionimus AI Frontend...
echo [INFO] React Development Server
echo [INFO] Standard Port: 3000
echo [INFO] Auto-Browser-Öffnung: Aktiviert
echo.
echo [WICHTIG] Lassen Sie dieses Fenster geöffnet!
echo [INFO] Zum Beenden: Ctrl+C
echo.

REM Kurz warten
timeout /t 2 /nobreak >nul

REM Browser automatisch öffnen (nach 10 Sekunden)
start /min cmd /c "timeout /t 10 /nobreak >nul && start http://localhost:3000 && exit"

REM Frontend Server starten
yarn start

REM Falls Fehler auftreten
echo.
echo [ERROR] Frontend Server wurde beendet!
echo [INFO] Mögliche Probleme:
echo   - Port 3000 bereits belegt
echo   - Node.js Dependencies fehlen
echo   - Fehler in der .env Datei
echo   - React Build Fehler
echo.
echo [DEBUG] Für detaillierte Fehlermeldungen führen Sie manuell aus:
echo   cd frontend
echo   yarn start
echo.
echo [INFO] Alternativ können Sie auch verwenden:
echo   cd frontend
echo   npm start
echo.
pause