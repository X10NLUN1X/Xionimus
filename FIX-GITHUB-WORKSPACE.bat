@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - GitHub Workspace Fix
color 0B

echo.
echo ========================================================================
echo    GITHUB WORKSPACE FIX - Windows Path Compatibility
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/4] Creating workspace directories...
echo.

REM Create workspace structure
cd backend
if not exist "workspace" mkdir workspace
cd workspace
if not exist "github_imports" mkdir github_imports
if not exist "uploads" mkdir uploads
if not exist "exports" mkdir exports
cd ..\..

echo ✅ Workspace directories created:
echo    - backend\workspace\
echo    - backend\workspace\github_imports\
echo    - backend\workspace\uploads\
echo    - backend\workspace\exports\

echo.
echo [2/4] Verifying Python path compatibility...
echo.

cd backend
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    
    REM Test pathlib
    python -c "from pathlib import Path; from app.core.config import settings; print(f'Workspace: {settings.GITHUB_IMPORTS_DIR}')" 2>nul
    
    if !errorlevel! equ 0 (
        echo ✅ Path configuration working
    ) else (
        echo ⚠️  Path configuration may need adjustment
        echo    But basic structure is created
    )
) else (
    echo ⚠️  Virtual environment not found
    echo    Run START.bat first to create venv
)

cd ..

echo.
echo [3/4] Setting permissions...
echo.

REM Set full permissions for workspace
icacls backend\workspace /grant Everyone:F /T >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Full permissions set for workspace
) else (
    echo ⚠️  Could not set permissions (may need admin rights)
    echo    Workspace should still work for current user
)

echo.
echo [4/4] Creating test structure...
echo.

REM Create a test user directory structure
cd backend\workspace\github_imports
if not exist "test_user" (
    mkdir test_user
    echo Test workspace created > test_user\README.txt
    echo ✅ Test structure created
) else (
    echo ✅ Test structure already exists
)
cd ..\..\..

echo.
echo ========================================================================
echo    ✅ GITHUB WORKSPACE FIX COMPLETED!
echo ========================================================================
echo.
echo Workspace Structure:
echo   backend\workspace\
echo   ├── github_imports\    ← GitHub repos landen hier
echo   │   └── [user_id]\
echo   │       └── [repo_name]\
echo   ├── uploads\           ← File uploads
echo   └── exports\           ← Export files
echo.
echo Naechste Schritte:
echo   1. Backend neu starten (schliessen + START.bat)
echo   2. GitHub Repo importieren
echo   3. Dateien erscheinen automatisch in:
echo      backend\workspace\github_imports\[deine_user_id]\[repo_name]\
echo.
echo Die AI hat jetzt Zugriff auf alle importierten Repos!
echo Sie wird automatisch informiert ueber verfuegbare Repos bei jedem Chat.
echo.
pause
