@echo off
title XIONIMUS AI - Backend Server
color 0E
echo.
echo ==========================================
echo      XIONIMUS AI - BACKEND SERVER
echo ==========================================
echo.

REM Ins Backend Verzeichnis wechseln
cd /d "%~dp0backend"

REM Pruefen ob im richtigen Verzeichnis
if not exist "server.py" (
    echo [ERROR] server.py nicht gefunden!
    echo [INFO] Bitte starten Sie diese Datei aus dem Xionimus Hauptverzeichnis
    pause
    exit /b 1
)

REM Python Version anzeigen
echo [INFO] Python Version:
python --version
echo.

REM .env Datei pruefen
if not exist ".env" (
    echo [ERROR] .env Datei nicht gefunden!
    echo [INFO] Bitte fuehren Sie zuerst WINDOWS_INSTALL.bat aus
    pause
    exit /b 1
)

echo [INFO] Backend Konfiguration:
echo ================================
type .env
echo ================================
echo.

REM MongoDB Verbindung pruefen
echo [CHECK] Pruefe MongoDB Verbindung...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print('[SUCCESS] MongoDB erreichbar:', client.server_info()['version'])" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] MongoDB nicht erreichbar!
    echo [INFO] Starten Sie MongoDB Compass oder MongoDB Service
    echo [INFO] Backend startet trotzdem...
)
echo.

REM Dependencies pruefen
echo [CHECK] Pruefe Python Dependencies...
python -c "import fastapi, uvicorn, motor, anthropic; print('[SUCCESS] Alle Dependencies gefunden')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Dependencies fehlen oder sind beschaedigt
    echo [FIX] Installiere Dependencies...
    pip install -r requirements.txt
)
echo.

REM Port pruefen
netstat -an | find ":8001 " >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 8001 bereits belegt!
    echo [INFO] Backend laeuft moeglicherweise bereits
    echo [INFO] Beenden Sie den anderen Prozess oder verwenden Sie Ctrl+C
)
echo.

echo [START] Starte Xionimus AI Backend Server...
echo [INFO] Host: localhost
echo [INFO] Port: 8001
echo [INFO] API Docs: http://localhost:8001/docs
echo [INFO] Health Check: http://localhost:8001/api/health
echo.
echo [WICHTIG] Lassen Sie dieses Fenster geoeffnet!
echo [STOP] Zum Beenden: Ctrl+C
echo.
echo ==========================================
echo        Backend Server wird gestartet...
echo ==========================================
echo.

REM Server starten
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

REM Falls Server beendet wird
echo.
color 0C
echo [STOPPED] Backend Server wurde beendet!
echo.
echo [TROUBLESHOOTING]:
echo   - Port 8001 belegt: Anderen Prozess beenden
echo   - MongoDB Fehler: MongoDB Compass starten
echo   - Dependencies Fehler: pip install -r requirements.txt
echo   - .env Fehler: WINDOWS_INSTALL.bat erneut ausfuehren
echo.
echo [RESTART] Um neu zu starten, doppelklicken Sie erneut auf diese Datei
echo.
pause