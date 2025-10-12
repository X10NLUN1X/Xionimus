@echo off
REM ====================================================================
REM QUICK START - API V1 MIGRATION
REM ====================================================================
REM One-click migration solution
REM ====================================================================

echo.
echo ========================================
echo   QUICK API V1 MIGRATION
echo ========================================
echo.

REM Check directory
if not exist "backend" (
    echo [ERROR] Wrong directory! Run from project root.
    pause
    exit /b 1
)

echo [INFO] Starting migration...
echo.

REM Run migration
python migrate_api_to_v1.py .

if %errorlevel% neq 0 (
    echo [ERROR] Migration failed!
    pause
    exit /b 1
)

REM Git operations
echo.
echo [INFO] Committing changes...
git add .
git commit -m "feat: Migrate all API calls to /api/v1/"

echo.
echo [INFO] Pushing to GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   MIGRATION COMPLETE!
    echo ========================================
    echo.
    echo All API calls migrated to /api/v1/
    echo Changes pushed to GitHub
    echo.
    echo Next: Restart backend and test!
    echo.
) else (
    echo.
    echo [WARNING] Push failed, but migration succeeded.
    echo You can push manually later with:
    echo   git push origin main
    echo.
)

pause
