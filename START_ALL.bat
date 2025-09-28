@echo off
title XIONIMUS AI - Start Both Services
color 0A

echo.
echo ==========================================
echo    XIONIMUS AI - START BACKEND + FRONTEND
echo ==========================================
echo.

cd /d "%~dp0"

REM Prüfe ob Installation durchgeführt wurde
if not exist "backend\.env" (
    echo [ERROR] Backend nicht installiert!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         install.bat
    echo.
    pause
    exit /b 1
)

if not exist "frontend\.env" (
    echo [ERROR] Frontend nicht installiert!
    echo [INFO] Bitte führen Sie zuerst die Installation durch:
    echo         install.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Starte Backend und Frontend in separaten Fenstern...
echo.

REM Starte Backend in separatem Fenster
echo [START] Backend-Server wird gestartet...
start "XIONIMUS Backend" START_BACKEND.bat

REM Warte kurz, dann starte Frontend
timeout /t 3 /nobreak >nul

echo [START] Frontend-Server wird gestartet...
start "XIONIMUS Frontend" START_FRONTEND.bat

echo.
echo ✅ BEIDE SERVICES WERDEN GESTARTET!
echo.
echo 🖥️ SERVER-FENSTER:
echo   → Backend:  "XIONIMUS Backend" 
echo   → Frontend: "XIONIMUS Frontend"
echo.
echo 🌐 ZUGRIFF (nach ~10 Sekunden):
echo   → Frontend UI: http://localhost:3000
echo   → Backend API: http://localhost:8001
echo.
echo ⚠️ WICHTIG: 
echo   → Lassen Sie beide Server-Fenster geöffnet!
echo   → Dieses Fenster kann geschlossen werden.
echo.
echo [AUTO] Browser öffnet in 10 Sekunden...
echo.

timeout /t 10 /nobreak >nul
start http://localhost:3000

echo [INFO] XIONIMUS AI gestartet - Browser sollte sich öffnen
echo [INFO] Dieses Fenster kann jetzt geschlossen werden
echo.
pause