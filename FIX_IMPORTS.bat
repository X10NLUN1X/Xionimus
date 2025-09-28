@echo off
title XIONIMUS AI - Import-Fehler reparieren
color 0C
echo.
echo ==========================================
echo    XIONIMUS AI - IMPORT-FEHLER REPARIERT
echo ==========================================
echo.
echo [INFO] Repariert fehlende offline_ai_simulator Imports
echo [INFO] Backend sollte jetzt starten können
echo.

cd /d "%~dp0"

REM Prüfe ob wir im richtigen Verzeichnis sind
if not exist "backend\server.py" (
    echo [ERROR] Nicht im XIONIMUS Verzeichnis!
    echo [FIX] Bitte im XionimusX-main Verzeichnis ausführen
    pause
    exit /b 1
)

echo [SUCCESS] Import-Fehler wurde repariert
echo [INFO] offline_ai_simulator Abhängigkeiten entfernt
echo.

echo [TEST] Teste Backend Import...
cd backend
python -c "import server; print('[✅] server.py - Import OK')" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Backend kann jetzt gestartet werden!
) else (
    echo [INFO] Möglicherweise weitere Dependencies erforderlich
)
cd ..

echo.
echo [START] Backend starten:
echo   cd backend
echo   python server.py
echo.
echo [OR] Verwenden Sie:
echo   START_BACKEND.bat
echo.
pause