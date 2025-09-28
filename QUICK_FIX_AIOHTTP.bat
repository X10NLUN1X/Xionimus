@echo off
title XIONIMUS AI - Quick aiohttp Fix
color 0C

echo.
echo ==========================================
echo    XIONIMUS AI - QUICK AIOHTTP FIX
echo ==========================================
echo.
echo [INFO] Behebt ModuleNotFoundError: No module named 'aiohttp'
echo [INFO] Installiert kritische async/network Dependencies
echo.

cd /d "%~dp0"

if not exist "backend\server.py" (
    echo [ERROR] Backend-Verzeichnis nicht gefunden!
    echo [INFO] Führen Sie dieses Script im XIONIMUS Hauptverzeichnis aus
    pause
    exit /b 1
)

echo [STEP 1] Wechsle ins Backend-Verzeichnis...
cd backend

echo [STEP 2] Update pip...
python -m pip install --upgrade pip

echo [STEP 3] Installiere aiohttp und verwandte Dependencies...
python -m pip install aiohttp==3.11.10 aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache

echo [STEP 4] Installiere FastAPI und Web Framework...
python -m pip install fastapi uvicorn starlette

echo [STEP 5] Installiere andere kritische Dependencies...
python -m pip install motor pymongo python-dotenv anthropic openai

echo [VALIDATION] Teste aiohttp Import...
python -c "import aiohttp; print('[SUCCESS] aiohttp erfolgreich installiert!')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ AIOHTTP FIX ERFOLGREICH!
    echo.
    echo [INFO] Backend kann jetzt gestartet werden:
    echo    START_BACKEND.bat
    echo.
    echo [INFO] Für vollständige Installation verwenden Sie:
    echo    WINDOWS_INSTALL.bat
    echo.
) else (
    echo.
    echo ❌ AIOHTTP FIX FEHLGESCHLAGEN!
    echo.
    echo [FALLBACK] Verwenden Sie stattdessen:
    echo    WINDOWS_INSTALL.bat
    echo.
)

pause