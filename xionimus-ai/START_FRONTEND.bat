@echo off
title Xionimus AI Frontend
echo Starting Xionimus AI Frontend Development Server...

cd /d "%~dp0\frontend"

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    yarn install
)

echo Starting Vite development server...
yarn dev

pause
