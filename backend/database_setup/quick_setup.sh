#!/bin/bash

# Quick database setup script
echo "🔧 Setting up database..."

# Get the backend directory
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "📁 Backend directory: $BACKEND_DIR"

# Change to backend directory
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Please run: python -m venv venv && source venv/bin/activate"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if database file exists
if [ ! -f "dev.db" ]; then
    echo "📁 Creating database file..."
    touch dev.db
fi

# Run the database setup
echo "🔨 Setting up database tables..."
python -c "
import sys
sys.path.insert(0, '.')
from database import SessionLocal, engine
from models import Base
import sqlite3

try:
    # Test connection
    db = SessionLocal()
    print('✅ Database connection successful')
    db.close()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
    print('🎉 Database setup completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Database setup completed successfully!"
else
    echo "❌ Database setup failed!"
    exit 1
fi
