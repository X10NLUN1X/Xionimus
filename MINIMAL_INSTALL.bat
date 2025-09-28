@echo off
title XIONIMUS AI - Minimal Installation
color 0B
echo.
echo ==========================================
echo    XIONIMUS AI - MINIMAL INSTALLATION
echo ==========================================
echo.
echo [INFO] Nur die absolut notwendigen Dependencies
echo [INFO] Für Systeme mit Installationsproblemen
echo.

echo [STEP 1/4] BACKEND MINIMAL DEPENDENCIES
cd backend

echo [INSTALL] Core Web Framework...
pip install fastapi==0.110.1 uvicorn==0.25.0 starlette==0.37.2

echo [INSTALL] Data Models...
pip install pydantic==2.11.7 typing_extensions==4.15.0

echo [INSTALL] Async Network (KRITISCH für aiohttp Fehler)...
pip install aiohttp==3.12.15 anyio==4.10.0

echo [INSTALL] Database...
pip install motor==3.3.1 pymongo==4.5.0

echo [INSTALL] AI APIs...
pip install anthropic==0.68.0 openai==1.99.9 httpx==0.28.1

echo [INSTALL] Basic Utils...
pip install python-dotenv==1.1.1 requests==2.32.5 click==8.2.1

echo.
echo [STEP 2/4] .ENV DATEIEN
if not exist ".env" (
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    ) > .env
    echo [SUCCESS] .env erstellt
)

cd ..
if not exist "frontend\.env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
    echo [SUCCESS] frontend\.env erstellt
)

echo.
echo [STEP 3/4] FRONTEND MINIMAL
cd frontend
npm install --production

echo.
echo [STEP 4/4] TEST
cd ..\backend
echo [TEST] Teste Backend Import...
python -c "import aiohttp, fastapi, motor; print('✅ Minimal Installation erfolgreich')"

echo.
echo [SUCCESS] Minimal Installation abgeschlossen!
echo.
echo [START] System starten:
echo   Backend:  cd backend ^&^& python server.py
echo   Frontend: cd frontend ^&^& npm start
echo   Browser:  http://localhost:3000
echo.
pause