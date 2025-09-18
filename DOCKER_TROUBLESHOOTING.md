# Docker Troubleshooting Guide

## Issue: `unable to get image 'xionimus-backend'`

This error occurs because Docker Compose was trying to use pre-built images that don't exist.

## ✅ FIXED Solution:

The docker-compose.yml has been updated to build images automatically. Now you can simply run:

### For Windows:
```cmd
# Option 1: Use the build script (Recommended)
.\build-docker.bat

# Option 2: Direct docker-compose command
docker-compose up -d --build
```

### For Linux/Mac:
```bash
# Option 1: Use the build script (Recommended)
./build-docker.sh

# Option 2: Direct docker-compose command
docker-compose up -d --build
```

## Pre-requisites:

1. **Docker Desktop must be running**
   - Windows/Mac: Start Docker Desktop application
   - Linux: Ensure Docker daemon is running (`sudo systemctl start docker`)

2. **Check Docker is working**:
   ```cmd
   docker version
   docker-compose --version
   ```

## What the fix does:

- The docker-compose.yml now includes `build` context for both backend and frontend
- Images are built automatically when you run `docker-compose up -d --build`
- No need to manually build images first

## Verification Steps:

After running the build command, verify everything is working:

```cmd
# Check container status (should show 3 running containers)
docker-compose ps

# Check logs if needed
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Test the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001/api/health
```

## Common Issues and Solutions:

### "Docker is not running"
- **Windows/Mac**: Start Docker Desktop
- **Linux**: `sudo systemctl start docker`

### "Build failed" or dependency errors
- Check internet connection
- Try: `docker-compose down && docker-compose up -d --build --no-cache`

### "yarn.lock not found" error
- **Cause**: Docker build context vs runtime volume mount conflict
- **Fix**: This has been fixed by removing the conflicting volume mount from docker-compose.yml
- **Root cause**: The volume mount `./frontend:/app` was interfering with Docker's build process
- **Solution**: Removed the frontend volume mount, kept only `/app/node_modules` for performance

### Port conflicts (ports already in use)
- Stop conflicting services or change ports in docker-compose.yml
- Check what's using ports: `netstat -an | findstr :3000` (Windows) or `lsof -i :3000` (Linux/Mac)

### Permission issues (Linux/Mac)
```bash
sudo chmod +x build-docker.sh
./build-docker.sh
```

## Quick Health Check:

```cmd
# Test backend health endpoint
curl http://localhost:8001/api/health

# Or in PowerShell (Windows)
Invoke-WebRequest http://localhost:8001/api/health
```

## Clean Start (if issues persist):

```cmd
# Stop and remove everything
docker-compose down --volumes --remove-orphans

# Clean Docker system
docker system prune -a -f

# Rebuild from scratch
docker-compose up -d --build
```