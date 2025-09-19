@echo off
echo =====================================
echo   XIONIMUS AI - MONGODB COMPASS SETUP
echo =====================================
echo.

echo [INFO] Sie haben MongoDB Compass - das ist perfekt!
echo [INFO] MongoDB Compass ist eine GUI für MongoDB.
echo.

REM Prüfen ob MongoDB Server läuft
echo [INFO] Prüfe ob MongoDB Server bereits läuft...
netstat -an | find "27017" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] MongoDB Server läuft bereits auf Port 27017!
    goto :compass_setup
)

echo [INFO] MongoDB Server läuft nicht. Mögliche Optionen:
echo.
echo [OPTION 1] MongoDB als Windows Service (empfohlen):
echo   - Öffnen Sie Services (services.msc)
echo   - Suchen Sie "MongoDB" oder "Mongo"
echo   - Klicken Sie "Start" wenn vorhanden
echo.
echo [OPTION 2] MongoDB Compass Community Server:
echo   - Compass kann einen lokalen Server starten
echo   - Schauen Sie in Compass nach "Connect to localhost"
echo.
echo [OPTION 3] MongoDB manuell installieren:
echo   - https://mongodb.com/try/download/community
echo   - Community Server Edition herunterladen
echo.

REM Prüfen ob mongod.exe gefunden werden kann
where mongod >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [FOUND] MongoDB Server (mongod) ist installiert!
    echo [INFO] Starte MongoDB Server...
    
    REM Datenverzeichnis erstellen falls nicht vorhanden
    if not exist "C:\data\db" (
        mkdir "C:\data\db"
        echo [SUCCESS] Datenverzeichnis C:\data\db erstellt
    )
    
    echo [INFO] Starte MongoDB Server im Hintergrund...
    start /min cmd /c "mongod --dbpath C:\data\db --port 27017"
    timeout /t 3 /nobreak >nul
    
    REM Prüfen ob jetzt läuft
    netstat -an | find "27017" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] MongoDB Server gestartet!
    ) else (
        echo [WARNING] MongoDB Server Start unsicher - bitte manuell prüfen
    )
) else (
    echo [INFO] MongoDB Server (mongod) nicht im PATH gefunden
    echo [INFO] Möglicherweise ist nur MongoDB Compass installiert (GUI)
    echo [INFO] Sie benötigen auch den MongoDB Community Server
)

:compass_setup
echo.
echo ========================================
echo   MONGODB COMPASS KONFIGURATION
echo ========================================
echo.
echo [INFO] MongoDB Compass Verbindungseinstellungen:
echo   Connection String: mongodb://localhost:27017
echo   Host: localhost
echo   Port: 27017
echo   Database: xionimus_ai
echo.
echo [ANLEITUNG] MongoDB Compass öffnen:
echo   1. Starten Sie MongoDB Compass
echo   2. Verbindungsstring eingeben: mongodb://localhost:27017
echo   3. Klicken Sie "Connect"
echo   4. Neue Database erstellen: "xionimus_ai"
echo.
echo [TEST] Testen Sie die Verbindung in Compass!
echo.
echo [INFO] Wenn Compass sich nicht verbinden kann:
echo   - Starten Sie den MongoDB Server mit: 3_START_MONGODB.bat
echo   - Oder installieren Sie MongoDB Community Server
echo.

REM MongoDB-relevante Umgebungsvariable setzen
echo [INFO] Setze MongoDB Umgebung für Xionimus AI...
echo MONGO_URL=mongodb://localhost:27017 > .mongodb_connection
echo DB_NAME=xionimus_ai >> .mongodb_connection
echo [SUCCESS] Verbindungsinfo gespeichert in .mongodb_connection

echo.
echo [NEXT STEPS] Als nächstes:
echo   1. Prüfen Sie MongoDB Compass Verbindung
echo   2. Führen Sie aus: 2_SETUP_ENV_FILES.bat
echo   3. Starten Sie das System
echo.
echo [SUCCESS] MongoDB Compass Setup abgeschlossen!
echo.
pause