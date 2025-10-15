#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create database
PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE numbers_dont_lie;" || true

# Run migrations
alembic upgrade head

echo "Database initialization complete!" 