@echo off
REM ============================================================================
REM Xionimus AI - Installation Diagnostic Script
REM Check if installation completed successfully
REM ============================================================================

setlocal enabledelayedexpansion

color 0E
title Xionimus AI - Installation Check

echo.
echo ========================================================================
echo    Xionimus AI - Installation Diagnostic
echo ========================================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo [INFO] Checking installation in: %SCRIPT_DIR%
echo.

REM ============================================================================
REM 1. CHECK PROJECT STRUCTURE
REM ============================================================================
echo [1/5] Checking project structure...
echo.

set "ERRORS=0"
set "WARNINGS=0"

if exist "%SCRIPT_DIR%\backend\" (
    echo [OK] Backend directory found
) else (
    echo [ERROR] Backend directory NOT found
    set /a ERRORS+=1
)

if exist "%SCRIPT_DIR%\frontend\" (
    echo [OK] Frontend directory found
) else (
    echo [ERROR] Frontend directory NOT found
    set /a ERRORS+=1
)

REM ============================================================================
REM 2. CHECK BACKEND INSTALLATION
REM ============================================================================
echo.
echo [2/5] Checking backend installation...
echo.

if exist "%SCRIPT_DIR%\backend\venv\" (
    echo [OK] Virtual environment exists
    
    REM Check if venv has Python
    if exist "%SCRIPT_DIR%\backend\venv\Scripts\python.exe" (
        echo [OK] Python found in venv
    ) else (
        echo [ERROR] Python NOT found in venv
        set /a ERRORS+=1
    )
    
    REM Check if venv has pip
    if exist "%SCRIPT_DIR%\backend\venv\Scripts\pip.exe" (
        echo [OK] pip found in venv
    ) else (
        echo [WARNING] pip NOT found in venv
        set /a WARNINGS+=1
    )
) else (
    echo [ERROR] Virtual environment NOT created
    echo [INFO] You need to run: install-windows.bat
    set /a ERRORS+=1
)

REM Check requirements files
if exist "%SCRIPT_DIR%\backend\requirements-windows.txt" (
    echo [OK] requirements-windows.txt found
) else (
    echo [WARNING] requirements-windows.txt NOT found
    set /a WARNINGS+=1
)

REM ============================================================================
REM 3. CHECK FRONTEND INSTALLATION
REM ============================================================================
echo.
echo [3/5] Checking frontend installation...
echo.

if exist "%SCRIPT_DIR%\frontend\node_modules\" (
    echo [OK] node_modules directory exists
) else (
    echo [ERROR] node_modules NOT found
    echo [INFO] You need to run: install-windows.bat
    set /a ERRORS+=1
)

if exist "%SCRIPT_DIR%\frontend\package.json" (
    echo [OK] package.json found
) else (
    echo [ERROR] package.json NOT found
    set /a ERRORS+=1
)

REM ============================================================================
REM 4. CHECK START SCRIPTS
REM ============================================================================
echo.
echo [4/5] Checking start scripts...
echo.

if exist "%SCRIPT_DIR%\START_BACKEND.bat" (
    echo [OK] START_BACKEND.bat exists
) else (
    echo [WARNING] START_BACKEND.bat NOT found
    set /a WARNINGS+=1
)

if exist "%SCRIPT_DIR%\START_FRONTEND.bat" (
    echo [OK] START_FRONTEND.bat exists
) else (
    echo [WARNING] START_FRONTEND.bat NOT found
    set /a WARNINGS+=1
)

if exist "%SCRIPT_DIR%\START_ALL.bat" (
    echo [OK] START_ALL.bat exists
) else (
    echo [WARNING] START_ALL.bat NOT found
    set /a WARNINGS+=1
)

REM ============================================================================
REM 5. CHECK SYSTEM REQUIREMENTS
REM ============================================================================
echo.
echo [5/5] Checking system requirements...
echo.

REM Check Python
where python >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] !PYTHON_VERSION! installed
) else (
    echo [ERROR] Python NOT found in PATH
    set /a ERRORS+=1
)

REM Check Node
where node >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
    echo [OK] Node.js !NODE_VERSION! installed
) else (
    echo [ERROR] Node.js NOT found in PATH
    set /a ERRORS+=1
)

REM Check Git (optional)
where git >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=*" %%i in ('git --version') do set GIT_VERSION=%%i
    echo [OK] !GIT_VERSION! installed
) else (
    echo [WARNING] Git NOT found (optional)
    set /a WARNINGS+=1
)

REM ============================================================================
REM SUMMARY
REM ============================================================================
echo.
echo ========================================================================
echo    DIAGNOSTIC SUMMARY
echo ========================================================================
echo.

if %ERRORS% == 0 (
    if %WARNINGS% == 0 (
        echo [SUCCESS] Installation is COMPLETE and READY!
        echo.
        echo You can start Xionimus AI with:
        echo   - START_ALL.bat     (starts both backend and frontend)
        echo   - START_BACKEND.bat (starts backend only)
        echo   - START_FRONTEND.bat (starts frontend only)
    ) else (
        echo [OK] Installation is mostly complete with !WARNINGS! warning(s)
        echo.
        echo You can try starting the application, but some features may not work.
    )
) else (
    echo [ERROR] Installation is INCOMPLETE - !ERRORS! error(s) found
    echo.
    echo REQUIRED ACTION:
    echo   1. Run install-windows.bat to complete installation
    echo   2. If problems persist, try running as Administrator
    echo   3. Check that Python and Node.js are installed correctly
)

echo.
echo ========================================================================
echo.
pause
