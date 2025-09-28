@echo off
title XIONIMUS AI - Minimal Installation
color 0E

echo.
echo ==========================================
echo    XIONIMUS AI - MINIMAL INSTALLATION
echo ==========================================
echo.
echo [INFO] Installiert nur die absolut notwendigen Dependencies
echo [INFO] Für Systeme mit Installationsproblemen
echo.

cd /d "%~dp0"

if not exist "backend\server.py" (
    echo [ERROR] Backend-Verzeichnis nicht gefunden!
    pause
    exit /b 1
)

REM Backend Minimal Setup
echo [STEP 1] Backend Dependencies (Minimal)...
cd backend

REM Erstelle .env falls nicht vorhanden
if not exist ".env" (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai > .env
    echo ANTHROPIC_API_KEY= >> .env
    echo OPENAI_API_KEY= >> .env
    echo PERPLEXITY_API_KEY= >> .env
)

echo [INSTALL] Kritische Backend-Dependencies...
python -m pip install --no-cache-dir fastapi==0.110.1 uvicorn==0.25.0
python -m pip install --no-cache-dir aiohttp==3.11.10 
python -m pip install --no-cache-dir motor==3.3.1 pymongo==4.5.0
python -m pip install --no-cache-dir python-dotenv==1.1.1
python -m pip install --no-cache-dir anthropic==0.68.1 openai==1.109.1

echo [TEST] Backend Import Test...
python -c "import fastapi, uvicorn, aiohttp, motor, anthropic, openai; print('[SUCCESS] Backend bereit')"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend-Installation fehlgeschlagen
    pause
    exit /b 1
)

cd ..

REM Frontend Minimal Setup  
echo [STEP 2] Frontend Dependencies (Minimal)...
cd frontend

REM Erstelle .env falls nicht vorhanden
if not exist ".env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env
)

echo [CHECK] Prüfe Frontend Dependencies...
if not exist "node_modules" (
    echo [INSTALL] Installiere Frontend Dependencies...
    npm install --no-optional --silent
) else (
    echo [SUCCESS] Frontend Dependencies bereits vorhanden
)

cd ..

echo.
echo ✅ MINIMALE INSTALLATION ABGESCHLOSSEN!
echo.
echo [START] System starten:
echo   Backend: START_BACKEND.bat
echo   Frontend: START_FRONTEND.bat
echo   Browser: http://localhost:3000
echo.
echo [INFO] Bei Problemen verwenden Sie:
echo   WINDOWS_INSTALL.bat (vollständige Installation)
echo.

pause