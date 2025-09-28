@echo off
title XIONIMUS AI - Simple Installation
color 0B
echo.
echo ==========================================
echo    XIONIMUS AI - SIMPLE INSTALLATION
echo ==========================================
echo.
echo [INFO] Einfache Installation - behebt aiohttp Fehler
echo [INFO] Für Python 3.13.7 optimiert
echo.

REM Verzeichnis prüfen
if not exist "backend\server.py" (
    echo [ERROR] Nicht im richtigen Verzeichnis!
    echo [INFO] Bitte im XIONIMUS Hauptverzeichnis ausführen
    pause
    exit /b 1
)

REM .env Dateien erstellen (KRITISCH!)
echo [STEP 1/4] .env Dateien erstellen...
(
echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
echo ANTHROPIC_API_KEY=
echo OPENAI_API_KEY=
echo PERPLEXITY_API_KEY=
) > backend\.env
echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
echo [SUCCESS] .env Dateien erstellt

REM Backend Dependencies (MINIMAL aber VOLLSTÄNDIG)
echo.
echo [STEP 2/4] Backend Dependencies (aiohttp Fix)...
cd backend

echo [INSTALL] Core async (behebt aiohttp Fehler)...
pip install aiohttp==3.12.15 anyio==4.11.0 --quiet

echo [INSTALL] Web Framework...
pip install fastapi==0.110.1 uvicorn==0.25.0 --quiet

echo [INSTALL] Database...
pip install motor==3.3.1 pymongo==4.5.0 --quiet

echo [INSTALL] AI APIs...
pip install anthropic==0.68.1 openai==1.109.1 httpx==0.28.1 --quiet

echo [INSTALL] Data Processing...
pip install numpy pandas --quiet

echo [INSTALL] Utilities...
pip install python-dotenv==1.1.1 requests==2.32.5 click==8.2.1 --quiet
pip install PyYAML==6.0.2 Jinja2==3.1.6 rich==14.1.0 --quiet

cd ..

REM Frontend Dependencies
echo.
echo [STEP 3/4] Frontend Dependencies...
cd frontend
npm install --silent
cd ..

REM Test
echo.
echo [STEP 4/4] System Test...
cd backend
python -c "import aiohttp, fastapi, motor; print('[✅] Core modules OK')" || echo [❌] Import-Fehler
cd ..

echo.
echo [SUCCESS] Simple Installation abgeschlossen!
echo.
echo [START] System starten:
echo   Backend:  cd backend ^&^& python server.py
echo   Frontend: cd frontend ^&^& npm start
echo   Browser:  http://localhost:3000
echo.
pause