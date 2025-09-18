#!/bin/bash

echo "Starting XIONIMUS AI..."

if [ -f docker-compose.yml ]; then
    echo "Using Docker setup..."
    docker-compose up -d
    echo "XIONIMUS AI is starting..."
    echo "Backend: http://localhost:8001"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "Wait 30-60 seconds then open: http://localhost:3000"
else
    echo "docker-compose.yml not found!"
    echo "Please run ./install.sh first"
fi