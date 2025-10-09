@echo off
REM ========================================================================
REM   XIONIMUS AI - QUICK INSTALLER
REM   Installiert nur Dependencies ohne zu starten
REM ========================================================================

echo.
echo ========================================================================
echo    XIONIMUS AI - Installation
echo ========================================================================
echo.
echo Dieser Script wird automatisch von START.bat aufgerufen.
echo Sie muessen ihn normalerweise NICHT manuell ausfuehren.
echo.
echo Druecken Sie eine Taste um trotzdem zu installieren...
pause >nul

cd /d "%~dp0"

echo.
echo Installiere Backend Dependencies...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo.
echo Installiere Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo ✅ Installation abgeschlossen!
echo.
echo Starten Sie das System mit: START.bat
echo.
pause