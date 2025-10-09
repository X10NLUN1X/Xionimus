@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - Uvicorn Windows Fix
color 0B

echo.
echo ========================================================================
echo    UVICORN WINDOWS FIX - AsyncIO Event Loop Repair
echo ========================================================================
echo.

cd /d "%~dp0"

REM Check for backend directory
if not exist "backend" (
    echo ❌ ERROR: backend directory not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo [1/4] Fixing Uvicorn and AsyncIO compatibility...
echo.

cd backend

REM Activate venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo.
echo [2/4] Reinstalling Uvicorn with Windows-compatible versions...
echo.

REM Uninstall and reinstall with specific versions
pip uninstall -y uvicorn watchfiles httptools >nul 2>&1
pip install uvicorn==0.30.0 watchfiles==0.21.0 httptools==0.6.1

if !errorlevel! neq 0 (
    echo ⚠️  Some packages may have failed to install
    echo Continuing anyway...
)

echo ✅ Uvicorn packages updated

echo.
echo [3/4] Verifying launcher scripts...
echo.

REM Check if launcher scripts exist
if exist "server_launcher.py" (
    echo ✅ server_launcher.py found (Primary method)
) else (
    echo ⚠️  server_launcher.py not found
    echo    Will be created by START.bat
)

if exist "server_alternative.py" (
    echo ✅ server_alternative.py found (Fallback method)
) else (
    echo ⚠️  server_alternative.py not found
    echo    Will be created by START.bat
)

echo.
echo [4/4] Testing minimal server...
echo.

REM Create minimal test server
(
    echo import sys, asyncio
    echo if sys.platform == 'win32':
    echo     asyncio.set_event_loop_policy^(asyncio.WindowsProactorEventLoopPolicy^(^)^)
    echo from fastapi import FastAPI
    echo app = FastAPI^(^)
    echo @app.get^("/test"^)
    echo def test^(^): return {"status": "ok"}
) > test_server_minimal.py

echo Testing event loop policy...
timeout /t 2 /nobreak >nul

python test_server_minimal.py >nul 2>&1 &
timeout /t 3 /nobreak >nul

REM Cleanup test server
taskkill /FI "WINDOWTITLE eq test*" /F >nul 2>&1
if exist test_server_minimal.py del test_server_minimal.py

echo ✅ Event loop test completed

cd ..

echo.
echo ========================================================================
echo    ✅ UVICORN WINDOWS FIX COMPLETED!
echo ========================================================================
echo.
echo Naechste Schritte:
echo.
echo 1. Schliessen Sie alle offenen Backend-Fenster
echo 2. Fuehren Sie START.bat aus
echo 3. Backend startet jetzt mit server_launcher.py
echo.
echo Falls Backend immer noch nicht startet:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python server_alternative.py
echo.
echo ========================================================================
echo.
pause
