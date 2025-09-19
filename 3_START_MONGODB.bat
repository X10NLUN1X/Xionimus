@echo off
echo =====================================
echo   XIONIMUS AI - MONGODB SERVER STARTER
echo   (für MongoDB Compass)
echo =====================================
echo.

REM Prüfen ob MongoDB bereits läuft
netstat -an | find "27017" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] MongoDB Server läuft bereits auf Port 27017!
    echo [INFO] Compass kann sich verbinden mit: mongodb://localhost:27017
    echo.
    goto :show_compass_info
)

echo [INFO] MongoDB Server läuft nicht. Starte Server...
echo.

REM Prüfen ob mongod verfügbar ist
where mongod >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] MongoDB Server (mongod) nicht im PATH gefunden!
    echo.
    echo [LÖSUNGEN]:
    echo   1. MongoDB Community Server installieren:
    echo      https://mongodb.com/try/download/community
    echo.
    echo   2. MongoDB Service starten (falls installiert):
    echo      - Drücken Sie Win+R
    echo      - Eingeben: services.msc
    echo      - Suchen Sie nach "MongoDB" Service
    echo      - Klicken Sie "Start"
    echo.
    echo   3. Compass mit Cloud/Atlas verbinden:
    echo      - MongoDB Atlas Account erstellen
    echo      - Cloud-Cluster verwenden
    echo.
    goto :show_compass_info
)

REM Datenverzeichnis erstellen
if not exist "C:\data\db" (
    echo [INFO] Erstelle MongoDB Datenverzeichnis...
    mkdir "C:\data\db"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Konnte Datenverzeichnis nicht erstellen!
        echo [INFO] Versuchen Sie als Administrator zu starten
        pause
        exit /b 1
    )
    echo [SUCCESS] Datenverzeichnis C:\data\db erstellt
)

echo [INFO] Starte MongoDB Server...
echo [INFO] Datenverzeichnis: C:\data\db
echo [INFO] Port: 27017
echo [INFO] Zum Beenden: Ctrl+C
echo.
echo [WICHTIG] Lassen Sie dieses Fenster geöffnet!
echo.

REM MongoDB Server starten
mongod --dbpath C:\data\db --port 27017

:show_compass_info
echo.
echo ==========================================
echo   MONGODB COMPASS VERBINDUNG
echo ==========================================
echo.
echo [COMPASS EINSTELLUNGEN]:
echo   Connection String: mongodb://localhost:27017
echo   Host: localhost  
echo   Port: 27017
echo   Authentication: None (für lokale Entwicklung)
echo.
echo [DATENBANK FÜR XIONIMUS AI]:
echo   Database Name: xionimus_ai
echo   Collections: projects, sessions, files, etc.
echo.
echo [COMPASS ANLEITUNG]:
echo   1. Öffnen Sie MongoDB Compass
echo   2. Verbindungsstring eingeben: mongodb://localhost:27017
echo   3. Klicken Sie "Connect"  
echo   4. Neue Database erstellen: "xionimus_ai"
echo   5. Erste Collection wird automatisch von Xionimus AI erstellt
echo.
echo [TESTEN]:
echo   - Compass zeigt verfügbare Databases
echo   - Nach dem ersten Xionimus AI Start erscheint "xionimus_ai"
echo   - Collections: projects, chat_sessions, uploaded_files
echo.
echo [TROUBLESHOOTING]:
echo   - Compass kann sich nicht verbinden?
echo     → MongoDB Server nicht gestartet
echo     → Firewall blockiert Port 27017
echo     → Windows Service nicht aktiv
echo.
pause