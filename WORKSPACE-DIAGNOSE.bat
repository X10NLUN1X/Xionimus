@echo off
title Xionimus AI - Workspace Diagnose
color 0E

echo.
echo ========================================================================
echo    WORKSPACE DIAGNOSE
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1] Workspace-Struktur:
echo.
if exist "backend\workspace" (
    echo ✅ backend\workspace existiert
    dir /b "backend\workspace"
) else (
    echo ❌ backend\workspace fehlt!
)

echo.
echo [2] GitHub Imports:
echo.
if exist "backend\workspace\github_imports" (
    echo ✅ github_imports existiert
    for /d %%d in (backend\workspace\github_imports\*) do (
        echo    User: %%~nxd
        for /d %%r in (backend\workspace\github_imports\%%~nxd\*) do (
            echo       └─ Repo: %%~nxr
        )
    )
) else (
    echo ❌ github_imports fehlt!
)

echo.
echo [3] Agent-Konfiguration:
echo.
if exist ".cursorrules" (
    echo ✅ .cursorrules vorhanden
) else (
    echo ⚠️  .cursorrules fehlt
)

if exist ".cursor\rules\index.mdc" (
    echo ✅ .cursor/rules/index.mdc vorhanden
) else (
    echo ⚠️  .cursor/rules fehlt
)

if exist ".aider.conf.yml" (
    echo ✅ .aider.conf.yml vorhanden
) else (
    echo ⚠️  .aider.conf.yml fehlt
)

if exist ".vscode\settings.json" (
    echo ✅ .vscode/settings.json vorhanden
) else (
    echo ⚠️  .vscode/settings.json fehlt
)

echo.
echo [4] Git-Konfiguration:
git config --global core.longpaths >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Git longpaths aktiviert
) else (
    echo ⚠️  Git longpaths nicht konfiguriert
)

echo.
echo ========================================================================
echo    DIAGNOSE ABGESCHLOSSEN
echo ========================================================================
echo.
echo Probleme gefunden? Fuehre WORKSPACE-FIX-COMPREHENSIVE.bat aus
echo.
pause
