# Docker Troubleshooting Guide

## Issue: `unable to get image 'xionimus-backend'`

This error occurs because Docker Compose is looking for pre-built images that don't exist yet.

## Solutions (Try in order):

### Solution 1: Use the Build Script (Recommended)

#### For Windows:
```cmd
# Run this in PowerShell or Command Prompt
.\build-docker.bat
```

#### For Linux/Mac:
```bash
# Run this in terminal
./build-docker.sh
```

### Solution 2: Manual Build Process

1. **Ensure Docker Desktop is Running**
   - Windows: Start Docker Desktop application
   - Mac: Start Docker Desktop application
   - Linux: Ensure Docker daemon is running

2. **Build Images Manually**
   ```cmd
   # Build backend image
   docker build -t xionimus-backend ./backend
   
   # Build frontend image  
   docker build -t xionimus-frontend ./frontend
   
   # Start services
   docker-compose up -d
   ```

### Solution 3: Use Build-on-Fly Compose File

If you prefer to build images during docker-compose up:

```cmd
# Use the alternative compose file
docker-compose -f docker-compose.build.yml up -d --build
```

### Solution 4: Clean Docker Environment

If you're still having issues:

```cmd
# Stop all containers
docker-compose down

# Clean up Docker system
docker system prune -a -f

# Remove any existing images
docker rmi xionimus-backend xionimus-frontend 2>nul

# Build fresh
docker build -t xionimus-backend ./backend
docker build -t xionimus-frontend ./frontend

# Start services
docker-compose up -d
```

## Common Error Messages and Fixes:

### "The system cannot find the file specified"
- **Cause**: Docker Desktop is not running
- **Fix**: Start Docker Desktop application

### "no such file or directory"
- **Cause**: Running from wrong directory
- **Fix**: Ensure you're in the project root directory (where docker-compose.yml exists)

### "build failed"
- **Cause**: Missing dependencies or network issues
- **Fix**: Check your internet connection and try again

## Verification Steps:

After running any solution, verify everything is working:

```cmd
# Check container status
docker-compose ps

# Check logs if needed
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Test the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001/api/health
```

## Quick Health Check:

```cmd
# Test if backend is responsive
curl http://localhost:8001/api/health

# Or in PowerShell
Invoke-WebRequest http://localhost:8001/api/health
```

## Files Created for This Fix:

1. `build-docker.sh` - Linux/Mac build script
2. `build-docker.bat` - Windows build script  
3. `docker-compose.build.yml` - Alternative compose file with build
4. `DOCKER_TROUBLESHOOTING.md` - This guide

## Contact:

If you're still experiencing issues, please provide:
1. Your operating system
2. Docker Desktop version
3. Complete error message
4. Output of `docker version`