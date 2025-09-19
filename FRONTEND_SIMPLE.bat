@echo off
echo XIONIMUS AI - Einfacher Frontend Start
echo.

cd /d "%~dp0frontend"
echo Bin jetzt in: %CD%

echo REACT_APP_BACKEND_URL=http://localhost:8001> .env
echo WDS_SOCKET_PORT=3000>> .env

echo .env Datei erstellt:
type .env

echo.
echo Starte NPM...
npm start

pause