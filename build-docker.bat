@echo off
echo 🔧 Building Xionimus AI Docker containers...

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo 🧹 Cleaning up existing containers...
docker-compose down --remove-orphans 2>nul
docker system prune -f 2>nul

echo 🏗️  Building backend image...
docker build -t xionimus-backend ./backend
if %errorlevel% neq 0 (
    echo ❌ Failed to build backend image
    pause
    exit /b 1
)

echo 🏗️  Building frontend image...
docker build -t xionimus-frontend ./frontend
if %errorlevel% neq 0 (
    echo ❌ Failed to build frontend image
    pause
    exit /b 1
)

echo 🚀 Starting services with docker-compose...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo ✅ Docker build complete!
echo 📋 Checking container status...
docker-compose ps

echo.
echo 🔍 To check logs, use:
echo   docker-compose logs backend
echo   docker-compose logs frontend
echo   docker-compose logs mongodb
echo.
echo 🌐 Application should be available at:
echo   Frontend: http://localhost:3000
echo   Backend: http://localhost:8001
echo.
pause