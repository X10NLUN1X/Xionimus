@echo off
echo =====================================
echo   XIONIMUS AI - MONGODB STARTER
echo =====================================
echo.

REM Prüfen ob MongoDB installiert ist
where mongod >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] MongoDB ist nicht installiert oder nicht im PATH!
    echo [INFO] Bitte installieren Sie MongoDB mit: 1_INSTALL_MONGODB.bat
    echo [INFO] Oder fügen Sie MongoDB zum PATH hinzu: C:\Program Files\MongoDB\Server\7.0\bin
    pause
    exit /b 1
)

REM Prüfen ob Datenverzeichnis existiert
if not exist "C:\data\db" (
    echo [INFO] Erstelle MongoDB Datenverzeichnis...
    mkdir "C:\data\db"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Konnte Datenverzeichnis nicht erstellen!
        echo [INFO] Bitte als Administrator ausführen oder manuell erstellen: C:\data\db
        pause
        exit /b 1
    )
    echo [SUCCESS] Datenverzeichnis C:\data\db erstellt
)

REM Prüfen ob MongoDB bereits läuft
netstat -an | find "27017" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] MongoDB läuft bereits auf Port 27017
    echo [INFO] Wenn Sie MongoDB neu starten möchten, beenden Sie zuerst den aktuellen Prozess
    echo.
    goto :show_status
)

echo [INFO] Starte MongoDB Server...
echo [INFO] Datenverzeichnis: C:\data\db
echo [INFO] Port: 27017
echo [INFO] Zum Beenden: Ctrl+C
echo.
echo [WICHTIG] Lassen Sie dieses Fenster geöffnet!
echo.

REM MongoDB starten
mongod --dbpath C:\data\db --port 27017

:show_status
echo.
echo [STATUS] MongoDB Server Informationen:
echo =====================================
echo Host: localhost
echo Port: 27017
echo Datenverzeichnis: C:\data\db
echo Verbindungsstring: mongodb://localhost:27017
echo.
echo [INFO] Zum Testen der Verbindung öffnen Sie ein neues Fenster und führen Sie aus:
echo   mongo
echo   oder
echo   mongosh
echo.
pause