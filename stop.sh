#!/bin/bash

echo "Stopping XIONIMUS AI..."

if [ -f docker-compose.yml ]; then
    echo "Stopping Docker services..."
    docker-compose down
    echo "XIONIMUS AI stopped."
else
    echo "docker-compose.yml not found!"
fi