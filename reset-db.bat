@echo off
REM Loescht die alte SQLite-Datenbank

echo Loesche alte Datenbank...

del /q "%USERPROFILE%\.xionimus_ai\xionimus.db" 2>nul

if exist "%USERPROFILE%\.xionimus_ai\xionimus.db" (
    echo [FEHLER] Konnte Datenbank nicht loeschen
) else (
    echo [OK] Alte Datenbank geloescht
)

echo.
echo Starten Sie jetzt das Backend mit: start.bat
echo.
pause
