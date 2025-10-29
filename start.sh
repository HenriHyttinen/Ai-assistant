#!/bin/bash

# Numbers Don't Lie Health App - Startup Script
# This script builds and runs the entire application with Docker

set -e

echo "Numbers Don't Lie Health App"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "Building and starting the application..."
echo ""

# Build and start the application
docker-compose up --build -d

echo ""
echo "Waiting for services to be ready..."

# Wait for the application to be healthy
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost/health &> /dev/null; then
        echo ""
        echo "Application is ready!"
        echo ""
        echo "Frontend: http://localhost"
        echo "Backend API: http://localhost:8000"
        echo "Health Check: http://localhost/health"
        echo ""
        echo "Available endpoints:"
        echo "  - Nutrition Dashboard: http://localhost/nutrition"
        echo "  - Recipe Search: http://localhost/recipes"
        echo "  - Meal Planning: http://localhost/meal-plans"
        echo "  - API Documentation: http://localhost:8000/docs"
        echo ""
        echo "To stop the application, run: docker-compose down"
        echo "To view logs, run: docker-compose logs -f"
        exit 0
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done

echo ""
echo "Warning: Application took longer than expected to start."
echo "Check logs with: docker-compose logs"
echo "Stop with: docker-compose down"
exit 1
