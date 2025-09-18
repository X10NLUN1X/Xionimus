#!/bin/bash

echo "🔧 Building Xionimus AI Docker containers..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Clean up any existing containers and build cache
echo "🧹 Cleaning up existing containers and build cache..."
docker-compose down --remove-orphans 2>/dev/null || true
docker builder prune -f 2>/dev/null || true

# Build and start services
echo "🚀 Building and starting services..."
docker-compose up -d --build --no-cache

echo "✅ Docker build and startup complete!"
echo "📋 Checking container status..."
docker-compose ps

echo ""
echo "🔍 To check logs, use:"
echo "  docker-compose logs backend"
echo "  docker-compose logs frontend"
echo "  docker-compose logs mongodb"
echo ""
echo "🌐 Application should be available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend: http://localhost:8001"