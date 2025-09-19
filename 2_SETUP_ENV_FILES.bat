@echo off
chcp 65001 >nul
echo =====================================
echo   XIONIMUS AI - ENV FILES SETUP
echo =====================================
echo.

REM Prüfen ob wir im richtigen Verzeichnis sind
if not exist "frontend" (
    echo [ERROR] frontend Verzeichnis nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Skript im Xionimus Hauptverzeichnis aus
    pause
    exit /b 1
)

if not exist "backend" (
    echo [ERROR] backend Verzeichnis nicht gefunden!
    echo [INFO] Bitte führen Sie dieses Skript im Xionimus Hauptverzeichnis aus
    pause
    exit /b 1
)

echo [INFO] Erstelle Frontend .env Datei...

REM Frontend .env erstellen (UTF-8 ohne BOM)
(
echo REACT_APP_BACKEND_URL=http://localhost:8001
echo WDS_SOCKET_PORT=3000
) > frontend\.env

if exist "frontend\.env" (
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [ERROR] Fehler beim Erstellen der frontend\.env
)

echo [INFO] Erstelle Backend .env Datei...

REM Backend .env erstellen (UTF-8 ohne BOM)
(
echo MONGO_URL="mongodb://localhost:27017"
echo DB_NAME="xionimus_ai"
echo CORS_ORIGINS="*"
echo.
echo # AI API Keys - Direct API Integration
echo # Get your Perplexity API key from: https://www.perplexity.ai/settings/api (format: pplx-...^)
echo # PERPLEXITY_API_KEY=pplx-your_perplexity_key_here
echo.
echo # Get your Anthropic API key from: https://console.anthropic.com/ (format: sk-ant-...^)
echo # ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
) > backend\.env

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
echo [NÄCHSTE SCHRITTE:]
echo 1. Installieren Sie Dependencies mit: npm install (in frontend und backend)
echo 2. Fügen Sie Ihre API Keys in backend\.env hinzu
echo 3. Starten Sie MongoDB mit: 3_START_MONGODB.bat
echo 4. Starten Sie Backend mit: 4_START_BACKEND.bat
echo 5. Starten Sie Frontend mit: 5_START_FRONTEND.bat
echo.
pause