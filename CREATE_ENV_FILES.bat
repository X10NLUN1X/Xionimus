@echo off
title XIONIMUS AI - .env Dateien erstellen
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - .ENV DATEIEN ERSTELLEN
echo ==========================================
echo.

REM Ins richtige Verzeichnis wechseln
cd /d "%~dp0"

echo [CREATE] Erstelle .env Dateien...

REM Backend .env erstellen
echo [INFO] Erstelle backend\.env...
(
echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
echo ANTHROPIC_API_KEY=
echo OPENAI_API_KEY=
echo PERPLEXITY_API_KEY=
) > backend\.env

if exist "backend\.env" (
    echo [SUCCESS] backend\.env erfolgreich erstellt
    echo [INFO] Inhalt:
    type backend\.env
) else (
    echo [ERROR] backend\.env konnte nicht erstellt werden
)

echo.

REM Frontend .env erstellen  
echo [INFO] Erstelle frontend\.env...
echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env

if exist "frontend\.env" (
    echo [SUCCESS] frontend\.env erfolgreich erstellt
    echo [INFO] Inhalt:
    type frontend\.env
) else (
    echo [ERROR] frontend\.env konnte nicht erstellt werden
)

echo.

REM Weitere notwendige Verzeichnisse erstellen
echo [CREATE] Erstelle notwendige Verzeichnisse...
if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads  
if not exist "backend\local_data" mkdir backend\local_data

echo [SUCCESS] Verzeichnisse erstellt
echo.

echo ==========================================
echo    .ENV SETUP ABGESCHLOSSEN
echo ==========================================
echo.
echo [INFO] Jetzt können Sie das Backend starten:
echo   START_BACKEND.bat
echo.
echo [CONFIG] API Keys später konfigurieren in:
echo   http://localhost:3000 → API Configuration
echo.
pause