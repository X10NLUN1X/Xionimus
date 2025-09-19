@echo off
echo ====================================
echo   XIONIMUS AI - EINFACHES SETUP
echo ====================================
echo.

echo [INFO] Aktuelles Verzeichnis: %CD%
echo.

REM Ins richtige Verzeichnis wechseln falls noetig
if not exist "frontend" (
    echo [WARNUNG] frontend Verzeichnis nicht gefunden!
    echo [INFO] Versuche Xionimus Verzeichnis zu finden...
    
    if exist "C:\Users\Administrator\Xionimus\frontend" (
        echo [GEFUNDEN] Wechsle zu C:\Users\Administrator\Xionimus
        cd /d "C:\Users\Administrator\Xionimus"
    ) else (
        echo [ERROR] Xionimus Verzeichnis nicht gefunden!
        echo [LOESUNG] Bitte navigieren Sie manuell zum Xionimus Verzeichnis:
        echo   1. Oeffnen Sie den Ordner wo Sie Xionimus heruntergeladen haben
        echo   2. Doppelklicken Sie auf diese BAT-Datei im richtigen Ordner
        pause
        exit /b 1
    )
)

echo [SUCCESS] Richtiges Verzeichnis gefunden: %CD%
echo.

REM Frontend .env erstellen
echo [1/2] Erstelle frontend\.env...
echo REACT_APP_BACKEND_URL=http://localhost:8001> frontend\.env
echo WDS_SOCKET_PORT=3000>> frontend\.env
echo [SUCCESS] frontend\.env erstellt

REM Backend .env erstellen
echo [2/2] Erstelle backend\.env...
echo MONGO_URL="mongodb://localhost:27017"> backend\.env
echo DB_NAME="xionimus_ai">> backend\.env
echo CORS_ORIGINS="*">> backend\.env
echo.>> backend\.env
echo # AI API Keys>> backend\.env
echo # PERPLEXITY_API_KEY=pplx-your_key_here>> backend\.env
echo # ANTHROPIC_API_KEY=sk-ant-your_key_here>> backend\.env
echo [SUCCESS] backend\.env erstellt

echo.
echo ========================================
echo   DATEIEN ERFOLGREICH ERSTELLT!
echo ========================================
echo.

echo [FRONTEND ENV:]
type frontend\.env
echo.
echo [BACKEND ENV:]
type backend\.env
echo.

echo [FERTIG] .env Dateien wurden erstellt!
echo.
echo [NAECHSTE SCHRITTE:]
echo 1. Starten Sie: 4_START_BACKEND.bat
echo 2. Starten Sie: 5_START_FRONTEND.bat
echo 3. API Keys hinzufuegen (optional)
echo.
pause