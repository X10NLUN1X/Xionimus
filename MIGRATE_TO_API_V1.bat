@echo off
REM ====================================================================
REM API V1 MIGRATION - AUTOMATIC BATCH SCRIPT
REM ====================================================================
REM This script will:
REM   1. Migrate all API calls from /api/ to /api/v1/
REM   2. Create backups (.backup files)
REM   3. Commit changes to Git
REM   4. Push to GitHub
REM ====================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   XIONIMUS API V1 MIGRATION
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo [ERROR] backend/ directory not found!
    echo.
    echo Please run this script from the Xionimus project root directory.
    echo Example: C:\AI\Xionimus\
    echo.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] frontend/ directory not found!
    echo.
    echo Please run this script from the Xionimus project root directory.
    echo Example: C:\AI\Xionimus\
    echo.
    pause
    exit /b 1
)

echo [INFO] Project structure verified
echo [INFO] Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.7+ and try again.
    echo.
    pause
    exit /b 1
)

echo [INFO] Python detected
echo.

REM Check if migrate_api_to_v1.py exists
if not exist "migrate_api_to_v1.py" (
    echo [ERROR] migrate_api_to_v1.py not found!
    echo.
    echo Please download the migration script first:
    echo   1. Download migrate_api_to_v1.py
    echo   2. Place it in the project root directory
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [INFO] Migration script found
echo.

REM ====================================================================
REM STEP 1: Run Python migration script
REM ====================================================================

echo.
echo ========================================
echo   STEP 1: RUNNING MIGRATION
echo ========================================
echo.

python migrate_api_to_v1.py "%CD%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Migration failed!
    echo.
    echo Please check the error messages above and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Migration completed successfully!
echo.

REM ====================================================================
REM STEP 2: Git status
REM ====================================================================

echo.
echo ========================================
echo   STEP 2: CHECKING GIT STATUS
echo ========================================
echo.

git status --short

echo.
echo [INFO] Files changed as shown above
echo.

REM ====================================================================
REM STEP 3: Confirm before committing
REM ====================================================================

echo.
echo ========================================
echo   READY TO COMMIT AND PUSH
echo ========================================
echo.
echo This will:
echo   1. Add all changed files to Git
echo   2. Commit with message: "feat: Migrate all API calls to /api/v1/"
echo   3. Push to GitHub (origin main)
echo.

set /p CONFIRM="Do you want to continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo [INFO] Operation cancelled by user
    echo.
    echo You can manually commit and push later with:
    echo   git add .
    echo   git commit -m "feat: Migrate all API calls to /api/v1/"
    echo   git push origin main
    echo.
    pause
    exit /b 0
)

REM ====================================================================
REM STEP 4: Git add
REM ====================================================================

echo.
echo ========================================
echo   STEP 4: STAGING CHANGES
echo ========================================
echo.

echo [INFO] Adding all changed files...
git add .

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to stage changes!
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Changes staged successfully
echo.

REM ====================================================================
REM STEP 5: Git commit
REM ====================================================================

echo.
echo ========================================
echo   STEP 5: CREATING COMMIT
echo ========================================
echo.

echo [INFO] Creating commit...
git commit -m "feat: Migrate all API calls to /api/v1/"

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] No changes to commit (or commit failed)
    echo.
    echo Possible reasons:
    echo   - All API calls already use /api/v1/
    echo   - Files were not actually changed
    echo.
    git status
    echo.
    pause
    exit /b 0
)

echo [SUCCESS] Commit created successfully
echo.

REM ====================================================================
REM STEP 6: Git push
REM ====================================================================

echo.
echo ========================================
echo   STEP 6: PUSHING TO GITHUB
echo ========================================
echo.

echo [INFO] Pushing to origin main...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to push to GitHub!
    echo.
    echo Possible reasons:
    echo   - No internet connection
    echo   - Authentication required
    echo   - Branch is behind remote
    echo.
    echo You can manually push later with:
    echo   git push origin main
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Pushed to GitHub successfully
echo.

REM ====================================================================
REM FINAL SUCCESS MESSAGE
REM ====================================================================

echo.
echo ========================================
echo   MIGRATION COMPLETED!
echo ========================================
echo.
echo All API calls have been migrated to /api/v1/
echo Changes have been committed and pushed to GitHub
echo.
echo Next steps:
echo   1. Pull changes on other machines: git pull
echo   2. Restart backend: START.bat
echo   3. Refresh frontend: F5 in browser
echo   4. Test all features
echo.
echo Backup files (.backup) were created for safety.
echo You can delete them if everything works:
echo   git clean -f *.backup
echo.

pause
