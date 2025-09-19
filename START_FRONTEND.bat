@echo off
title XIONIMUS AI - Frontend
echo ==========================================
echo   XIONIMUS AI - FRONTEND STARTER
echo ==========================================
echo.

echo Aktuelles Verzeichnis: %CD%
cd /d "%~dp0"
echo Nach Wechsel: %CD%
pause

echo.
echo Gehe ins Frontend Verzeichnis...
cd frontend
echo Jetzt in: %CD%
pause

echo.
echo Erstelle .env falls nicht vorhanden...
if not exist ".env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
    echo WDS_SOCKET_PORT=3000>> .env
    echo .env Datei erstellt
) else (
    echo .env Datei existiert bereits
)
pause

echo.
echo Zeige .env Inhalt:
type .env
pause

echo.
echo Starte Frontend mit NPM...
echo Browser oeffnet sich automatisch
echo WICHTIG: Lassen Sie dieses Fenster offen!
echo.

start /min cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:3000"

npm start

echo.
echo Frontend wurde beendet
pause