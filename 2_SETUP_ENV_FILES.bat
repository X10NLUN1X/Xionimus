@echo off
echo ====================================
echo   XIONIMUS AI - ENV FILES SETUP
echo ====================================
echo.

REM Aktuelles Verzeichnis anzeigen
echo [INFO] Aktuelles Verzeichnis: %CD%
echo.

REM Pruefen ob wir im richtigen Verzeichnis sind
if not exist "frontend" (
    echo [ERROR] frontend Verzeichnis nicht gefunden!
    echo [INFO] Aktuelles Verzeichnis: %CD%
    echo [INFO] Inhalt des aktuellen Verzeichnisses:
    dir /b
    echo.
    echo [LOESUNG] Navigieren Sie zum Xionimus Hauptverzeichnis:
    echo   cd C:\Users\Administrator\Xionimus
    echo   dann fuehren Sie dieses Skript erneut aus
    pause
    exit /b 1
)

if not exist "backend" (
    echo [ERROR] backend Verzeichnis nicht gefunden!
    echo [INFO] Bitte fuehren Sie dieses Skript im Xionimus Hauptverzeichnis aus
    pause
    exit /b 1
)

echo [INFO] Erstelle Frontend .env Datei...

REM Frontend .env erstellen (einfache Ausgabe)
echo REACT_APP_BACKEND_URL=http://localhost:8001> frontend\.env
echo WDS_SOCKET_PORT=3000>> frontend\.env

if exist "frontend\.env" (
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [ERROR] Fehler beim Erstellen der frontend\.env
)

echo [INFO] Erstelle Backend .env Datei...

REM Backend .env erstellen (einfache Ausgabe)
echo MONGO_URL="mongodb://localhost:27017"> backend\.env
echo DB_NAME="xionimus_ai">> backend\.env
echo CORS_ORIGINS="*">> backend\.env
echo.>> backend\.env
echo # AI API Keys - Direct API Integration>> backend\.env
echo # Get your Perplexity API key from: https://www.perplexity.ai/settings/api>> backend\.env
echo # PERPLEXITY_API_KEY=pplx-your_perplexity_key_here>> backend\.env
echo.>> backend\.env
echo # Get your Anthropic API key from: https://console.anthropic.com/>> backend\.env
echo # ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here>> backend\.env

if exist "backend\.env" (
    echo [SUCCESS] backend\.env erstellt
) else (
    echo [ERROR] Fehler beim Erstellen der backend\.env
)

echo.
echo [INFO] Verifiziere .env Dateien...
echo.

echo [FRONTEND .ENV INHALT:]
echo ========================
type frontend\.env
echo ========================
echo.

echo [BACKEND .ENV INHALT:]
echo ======================
type backend\.env
echo ======================
echo.

echo [SUCCESS] Alle .env Dateien wurden erfolgreich erstellt!
echo.
echo [NAECHSTE SCHRITTE:]
echo 1. Installieren Sie Dependencies mit: npm install
echo 2. Fuegen Sie Ihre API Keys in backend\.env hinzu
echo 3. Starten Sie MongoDB mit: 3_START_MONGODB.bat
echo 4. Starten Sie Backend mit: 4_START_BACKEND.bat
echo 5. Starten Sie Frontend mit: 5_START_FRONTEND.bat
echo.
pause