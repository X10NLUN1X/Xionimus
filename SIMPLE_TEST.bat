@echo off
echo XIONIMUS AI - EINFACHER TEST
echo.
echo Dieses Fenster bleibt IMMER offen!
echo.

echo Test 1: Wo bin ich?
echo %CD%
echo.

echo Test 2: Was ist hier?
dir
echo.

pause
echo.

echo Test 3: Node.js da?
node --version
echo.

pause
echo.

echo Test 4: Frontend Ordner da?
if exist frontend (
  echo JA
) else (
  echo NEIN
)
echo.

pause
echo.

echo Test 5: Gehe ins Frontend
cd frontend
echo Jetzt hier: %CD%
echo.

pause
echo.

echo Test 6: package.json da?
if exist package.json (
  echo JA
) else (
  echo NEIN
)
echo.

pause
echo.

echo Test 7: Starte NPM
npm start
echo.

echo Das war alles.
pause