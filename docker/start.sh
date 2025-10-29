#!/bin/bash

# Startup script for Numbers Don't Lie Health App
set -e

echo "Starting Numbers Don't Lie Health App..."

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Database is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    cd /app/backend
    python -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('Database migrations completed')
"
}

# Function to seed initial data
seed_data() {
    echo "Seeding initial data..."
    cd /app/backend
    python -c "
from scripts.seed_goals_direct import seed_goal_templates
try:
    seed_goal_templates()
    print('Goal templates seeded')
except Exception as e:
    print(f'Goal seeding failed: {e}')
"
}

# Function to start backend
start_backend() {
    echo "Starting backend server..."
    cd /app/backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend started with PID $BACKEND_PID"
}

# Function to start nginx
start_nginx() {
    echo "Starting nginx..."
    nginx -g "daemon off;" &
    NGINX_PID=$!
    echo "Nginx started with PID $NGINX_PID"
}

# Function to handle shutdown
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID $NGINX_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Set default environment variables
export DB_HOST=${DB_HOST:-localhost}
export DB_PORT=${DB_PORT:-5432}
export DB_NAME=${DB_NAME:-health_app}
export DB_USER=${DB_USER:-postgres}
export DB_PASSWORD=${DB_PASSWORD:-password}

# Wait for database if using external DB
if [ "$DB_HOST" != "localhost" ]; then
    wait_for_db
fi

# Run database setup
run_migrations
seed_data

# Start services
start_backend
start_nginx

echo "Numbers Don't Lie Health App is running!"
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:8000"
echo "Health Check: http://localhost/health"

# Wait for any process to exit
wait
