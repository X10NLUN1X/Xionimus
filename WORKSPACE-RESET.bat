@echo off
title Xionimus AI - Workspace Reset
color 0B

echo.
echo ========================================================================
echo    WORKSPACE RESET
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/2] Loesche temporaere Dateien...
if exist "backend\workspace\temp" (
    rmdir /s /q "backend\workspace\temp"
    mkdir "backend\workspace\temp"
    echo ✅ Temp-Ordner geleert
) else (
    echo ⚠️  Temp-Ordner nicht gefunden
)

echo.
echo [2/2] Setze Berechtigungen...
icacls "backend\workspace" /grant Everyone:(OI)(CI)F /T /Q >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Berechtigungen aktualisiert
) else (
    echo ⚠️  Berechtigungen nicht gesetzt (benötigt Admin-Rechte)
)

echo.
echo ========================================================================
echo    ✅ WORKSPACE RESET ABGESCHLOSSEN
echo ========================================================================
echo.
pause
