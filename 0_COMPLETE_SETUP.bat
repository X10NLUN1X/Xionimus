@echo off
chcp 65001 >nul
echo =========================================
echo   XIONIMUS AI - KOMPLETTE INSTALLATION
echo   (für MongoDB Compass)
echo =========================================
echo.
echo [INFO] Dieses Skript führt die komplette Einrichtung durch:
echo   1. MongoDB Compass Setup (bereits installiert)
echo   2. .env Dateien erstellen
echo   3. Dependencies installieren
echo   4. System vorbereiten
echo.
echo [VORAUSSETZUNG] Sie haben MongoDB Compass installiert ✓
echo.
pause

echo.
echo ========================================
echo   SCHRITT 1: MONGODB COMPASS SETUP
echo ========================================
echo.
call 1_INSTALL_MONGODB.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] MongoDB Setup fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SCHRITT 2: ENV DATEIEN ERSTELLEN
echo ========================================
echo.
call 2_SETUP_ENV_FILES.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] .env Dateien Setup fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SCHRITT 3: BACKEND DEPENDENCIES
echo ========================================
echo.
echo [INFO] Installiere Backend Dependencies...
cd backend
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Backend Dependencies Installation fehlgeschlagen!
        pause
        exit /b 1
    )
    echo [SUCCESS] Backend Dependencies installiert
) else (
    echo [ERROR] requirements.txt nicht gefunden!
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo   SCHRITT 4: FRONTEND DEPENDENCIES
echo ========================================
echo.
echo [INFO] Installiere Frontend Dependencies...

REM Prüfen ob yarn installiert ist
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Yarn Installation fehlgeschlagen!
        pause
        exit /b 1
    )
)

cd frontend
if exist "package.json" (
    yarn install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Frontend Dependencies Installation fehlgeschlagen!
        pause
        exit /b 1
    )
    echo [SUCCESS] Frontend Dependencies installiert
) else (
    echo [ERROR] package.json nicht gefunden!
    pause
    exit /b 1
)
cd ..

echo.
echo ==========================================
echo   INSTALLATION ABGESCHLOSSEN!
echo ==========================================
echo.
echo [SUCCESS] Xionimus AI ist bereit für MongoDB Compass!
echo.
echo [MONGODB COMPASS SETUP]:
echo   1. Öffnen Sie MongoDB Compass
echo   2. Verbindungsstring: mongodb://localhost:27017
echo   3. Klicken Sie "Connect"
echo   4. Database wird automatisch erstellt: xionimus_ai
echo.
echo [API KEYS KONFIGURIEREN] (optional):
echo   - Bearbeiten Sie: backend\.env
echo   - Uncomment und fügen Sie Ihre Keys hinzu:
echo     * PERPLEXITY_API_KEY=pplx-your_key_here
echo     * ANTHROPIC_API_KEY=sk-ant-your_key_here
echo.
echo [SYSTEM STARTEN] (benötigt 3 separate Fenster):
echo   a) 3_START_MONGODB.bat     (MongoDB Server)
echo   b) 4_START_BACKEND.bat     (Backend API)
echo   c) 5_START_FRONTEND.bat    (Frontend + Browser)
echo.
echo [WICHTIG] MongoDB Server muss laufen, damit Compass sich verbinden kann!
echo.
echo [TIPP] Starten Sie die Services in dieser Reihenfolge!
echo.
echo [API KEYS HOLEN]:
echo   - Perplexity: https://www.perplexity.ai/settings/api
echo   - Anthropic:  https://console.anthropic.com/
echo.
echo [URLS NACH DEM START]:
echo   - Frontend:     http://localhost:3000
echo   - Backend:      http://localhost:8001/api/health
echo   - API Docs:     http://localhost:8001/docs
echo   - MongoDB:      mongodb://localhost:27017 (für Compass)
echo.
echo [COMPASS NUTZEN]:
echo   - Verbinden Sie sich mit mongodb://localhost:27017
echo   - Database: xionimus_ai
echo   - Collections werden automatisch erstellt
echo.
pause