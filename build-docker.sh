#!/bin/bash

echo "🔧 Building Xionimus AI Docker containers..."

# Clean up any existing containers and images
echo "🧹 Cleaning up existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true
docker system prune -f 2>/dev/null || true

# Build the images
echo "🏗️  Building backend image..."
docker build -t xionimus-backend ./backend

echo "🏗️  Building frontend image..."
docker build -t xionimus-frontend ./frontend

# Update the docker-compose.yml to use the built images
echo "📝 Updating docker-compose.yml..."

# Start the services
echo "🚀 Starting services with docker-compose..."
docker-compose up -d

echo "✅ Docker build complete!"
echo "📋 Checking container status..."
docker-compose ps

echo "🔍 To check logs, use:"
echo "  docker-compose logs backend"
echo "  docker-compose logs frontend"
echo "  docker-compose logs mongodb"