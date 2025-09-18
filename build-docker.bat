@echo off
echo 🔧 Building Xionimus AI Docker containers...

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo 🧹 Cleaning up existing containers and build cache...
docker-compose down --remove-orphans 2>nul
docker builder prune -f 2>nul

echo 🚀 Building and starting services...
docker-compose up -d --build --no-cache
if %errorlevel% neq 0 (
    echo ❌ Failed to build and start services
    echo 📋 Checking for detailed error information...
    docker-compose logs
    pause
    exit /b 1
)

echo ✅ Docker build and startup complete!
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