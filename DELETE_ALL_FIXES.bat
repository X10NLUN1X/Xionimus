@echo off
echo ========================================
echo   LOESCHE ALLE FIX-DATEIEN
echo ========================================
echo.
echo Diese Dateien werden geloescht:
echo.
echo Python Fix-Scripts:
echo   - ALL_IN_ONE_FIX.py
echo   - CHECK_API_KEYS.py
echo   - FIX_ALLINONE.py
echo   - FIX_API_KEYS_PERMANENT.py
echo   - HOTFIX_INDENTATION.py
echo   - SIMPLE_FIX.py
echo   - WORKSPACE_FIX_COMPREHENSIVE.py
echo.
echo BAT Fix-Scripts:
echo   - DIAGNOSE.bat
echo   - FIX-GITHUB-WORKSPACE.bat
echo   - FIX-UVICORN-WINDOWS.bat
echo   - FIX_ALL.bat
echo   - FIX_CHAT_ONECLICK.bat
echo   - QUICK-FIX-BACKEND.bat
echo   - WINDOWS-FINAL-FIX.bat
echo   - WORKSPACE-DIAGNOSE.bat
echo   - WORKSPACE-FIX-COMPREHENSIVE.bat
echo   - check-windows.bat
echo.
echo Test-Dateien:
echo   - comprehensive_backend_health_check.py
echo   - developer_mode_fixes_test.py
echo   - developer_modes_fixes_test.py
echo   - test_anthropic_fix.py
echo   - bare_except_fixes_test.py
echo   - anthropic_fix_verification_test.py
echo   - post_fixes_backend_test.py
echo.
echo ========================================
pause

REM Python Fix-Scripts loeschen
del /Q ALL_IN_ONE_FIX.py 2>nul
del /Q CHECK_API_KEYS.py 2>nul
del /Q FIX_ALLINONE.py 2>nul
del /Q FIX_API_KEYS_PERMANENT.py 2>nul
del /Q HOTFIX_INDENTATION.py 2>nul
del /Q SIMPLE_FIX.py 2>nul
del /Q WORKSPACE_FIX_COMPREHENSIVE.py 2>nul

REM BAT Fix-Scripts loeschen
del /Q DIAGNOSE.bat 2>nul
del /Q FIX-GITHUB-WORKSPACE.bat 2>nul
del /Q FIX-UVICORN-WINDOWS.bat 2>nul
del /Q FIX_ALL.bat 2>nul
del /Q FIX_CHAT_ONECLICK.bat 2>nul
del /Q QUICK-FIX-BACKEND.bat 2>nul
del /Q WINDOWS-FINAL-FIX.bat 2>nul
del /Q WORKSPACE-DIAGNOSE.bat 2>nul
del /Q WORKSPACE-FIX-COMPREHENSIVE.bat 2>nul
del /Q check-windows.bat 2>nul

REM Test-Dateien loeschen
del /Q comprehensive_backend_health_check.py 2>nul
del /Q developer_mode_fixes_test.py 2>nul
del /Q developer_modes_fixes_test.py 2>nul
del /Q test_anthropic_fix.py 2>nul
del /Q bare_except_fixes_test.py 2>nul
del /Q anthropic_fix_verification_test.py 2>nul
del /Q post_fixes_backend_test.py 2>nul

echo.
echo ========================================
echo   FERTIG! Alle Fix-Dateien geloescht.
echo ========================================
echo.
echo WICHTIGE Dateien wurden NICHT geloescht:
echo   - START.bat
echo   - INSTALL.bat
echo   - setup-env.bat
echo   - SETUP_API_KEYS.bat
echo.
pause
