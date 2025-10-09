@echo off
REM ========================================================================
REM   XIONIMUS AI - DEBUG STARTUP (Simplified Version)
REM   Use this if START.bat fails to identify the problem
REM ========================================================================

echo.
echo ========================================================================
echo    XIONIMUS AI - DEBUG STARTUP
echo ========================================================================
echo.

REM Show current directory
echo Current Directory: %CD%
echo.

REM Check if we're in the right place
echo [STEP 1] Checking directory structure...
if exist "backend" (
    echo ✅ backend folder found
) else (
    echo ❌ backend folder NOT found
    echo You are in: %CD%
    pause
    exit /b 1
)

if exist "frontend" (
    echo ✅ frontend folder found
) else (
    echo ❌ frontend folder NOT found  
    echo You are in: %CD%
    pause
    exit /b 1
)
echo.
pause

REM Check Python
echo [STEP 2] Checking Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found in PATH
    pause
    exit /b 1
) else (
    echo ✅ Python OK
)
echo.
pause

REM Check Node
echo [STEP 3] Checking Node.js...
node --version
if errorlevel 1 (
    echo ❌ Node.js not found in PATH
    pause
    exit /b 1
) else (
    echo ✅ Node.js OK
)
echo.
pause

REM Check .env
echo [STEP 4] Checking .env file...
if exist "backend\.env" (
    echo ✅ backend\.env exists
) else (
    echo ⚠️  backend\.env does NOT exist
    echo.
    echo Checking for .env.example...
    if exist "backend\.env.example" (
        echo ✅ backend\.env.example found
        echo.
        echo Copying to backend\.env...
        copy "backend\.env.example" "backend\.env"
        if exist "backend\.env" (
            echo ✅ Copy successful
        ) else (
            echo ❌ Copy failed
            pause
            exit /b 1
        )
    ) else (
        echo ❌ backend\.env.example NOT found
        pause
        exit /b 1
    )
)
echo.
pause

REM Check backend venv
echo [STEP 5] Checking Python virtual environment...
cd backend
if exist "venv" (
    echo ✅ venv exists
) else (
    echo ⚠️  venv does NOT exist - creating...
    python -m venv venv
    if exist "venv" (
        echo ✅ venv created
    ) else (
        echo ❌ venv creation failed
        cd ..
        pause
        exit /b 1
    )
)
cd ..
echo.
pause

REM Test backend activation
echo [STEP 6] Testing venv activation...
cd backend
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate venv
    cd ..
    pause
    exit /b 1
) else (
    echo ✅ venv activated
    python --version
)
cd ..
echo.
pause

REM Check frontend node_modules
echo [STEP 7] Checking frontend dependencies...
cd frontend
if exist "node_modules" (
    echo ✅ node_modules exists
) else (
    echo ⚠️  node_modules does NOT exist
    echo Run: yarn install or npm install
)
cd ..
echo.
pause

echo.
echo ========================================================================
echo    DEBUG CHECK COMPLETE
echo ========================================================================
echo.
echo All basic checks passed!
echo.
echo If all steps showed ✅, try running START.bat again.
echo If any step showed ❌, fix that issue first.
echo.
pause
