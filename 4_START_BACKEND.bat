@echo off
chcp 65001 >nul
echo =====================================
echo   XIONIMUS AI - BACKEND STARTER
echo =====================================
echo.

REM Prüfen ob backend Verzeichnis existiert
if not exist "backend" (
    echo [ERROR] backend Verzeichnis nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Skript im Xionimus Hauptverzeichnis aus
    pause
    exit /b 1
)

REM Prüfen ob .env Datei existiert
if not exist "backend\.env" (
    echo [ERROR] backend\.env Datei nicht gefunden!
    echo [INFO] Bitte erstellen Sie die .env Datei mit: 2_SETUP_ENV_FILES.bat
    pause
    exit /b 1
)

REM Prüfen ob Python installiert ist
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python ist nicht installiert oder nicht im PATH!
    echo [INFO] Bitte installieren Sie Python 3.9+ von: https://python.org
    pause
    exit /b 1
)

REM Python Version prüfen
echo [INFO] Python Version:
python --version

REM Ins Backend Verzeichnis wechseln
cd backend

REM Prüfen ob requirements.txt existiert
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt nicht gefunden!
    pause
    exit /b 1
)

REM Prüfen ob Dependencies installiert sind
echo [INFO] Prüfe Python Dependencies...
python -c "import fastapi, uvicorn, motor, anthropic" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installiere Python Dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fehler beim Installieren der Dependencies!
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installiert
) else (
    echo [SUCCESS] Dependencies bereits installiert
)

REM Prüfen ob MongoDB läuft
echo [INFO] Prüfe MongoDB Verbindung...
netstat -an | find "27017" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] MongoDB läuft nicht auf Port 27017!
    echo [INFO] Bitte starten Sie MongoDB mit: 3_START_MONGODB.bat
    echo [INFO] Backend startet trotzdem (wird bei Bedarf versuchen zu verbinden)
    echo.
)

REM Prüfen ob Port 8001 bereits belegt ist
netstat -an | find "8001" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 8001 ist bereits belegt!
    echo [INFO] Möglicherweise läuft das Backend bereits
    echo [INFO] Beenden Sie den anderen Prozess oder verwenden Sie einen anderen Port
    echo.
)

echo [INFO] .env Datei Inhalt:
echo ========================
type .env
echo ========================
echo.

echo [INFO] Starte Xionimus AI Backend Server...
echo [INFO] Host: 0.0.0.0 (alle Interfaces)
echo [INFO] Port: 8001
echo [INFO] Reload: Aktiviert (Development Mode)
echo [INFO] API Dokumentation: http://localhost:8001/docs
echo [INFO] Health Check: http://localhost:8001/api/health
echo.
echo [WICHTIG] Lassen Sie dieses Fenster geöffnet!
echo [INFO] Zum Beenden: Ctrl+C
echo.

REM Backend Server starten
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

REM Falls Fehler auftreten
echo.
echo [ERROR] Backend Server wurde beendet!
echo [INFO] Mögliche Probleme:
echo   - Port 8001 bereits belegt
echo   - Python Dependencies fehlen
echo   - Fehler in der .env Datei
echo   - Server.py Syntax Fehler
echo.
echo [DEBUG] Für detaillierte Fehlermeldungen führen Sie manuell aus:
echo   cd backend
echo   python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
echo.
pause