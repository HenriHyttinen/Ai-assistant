#!/bin/bash

# Robust Backend Startup Script for Gaming Environment
# This script provides better resource management and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Numbers Don't Lie Backend (Gaming Optimized)${NC}"

# Ensure we're in the project root
cd "$(dirname "$0")"

# Kill any existing backend processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn main:app" || true
sleep 2

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

# Set environment variables for better performance
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export MALLOC_TRIM_THRESHOLD_=131072
export MALLOC_MMAP_THRESHOLD_=131072
export MALLOC_MMAP_MAX_=65536

# Navigate to backend directory
cd backend

# Check if database exists and is accessible
echo -e "${YELLOW}🗄️ Checking database...${NC}"
if [ ! -f "app.db" ]; then
    echo -e "${YELLOW}📝 Creating database...${NC}"
    python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
fi

# Start backend with optimized settings for gaming
echo -e "${GREEN}🎮 Starting backend with gaming-optimized settings...${NC}"
echo -e "${YELLOW}Settings: 1 worker, 30s timeout, 10 concurrency, 50 backlog${NC}"

# Use nohup to prevent terminal closure from killing the process
nohup python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --timeout-keep-alive 30 \
    --limit-concurrency 10 \
    --backlog 50 \
    --access-log \
    --log-level info \
    > ../backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

echo -e "${GREEN}✅ Backend started with PID: $BACKEND_PID${NC}"
echo -e "${YELLOW}📝 Logs are being written to: backend.log${NC}"
echo -e "${YELLOW}🆔 Process ID saved to: backend.pid${NC}"

# Wait a moment for startup
sleep 3

# Test if backend is responding
echo -e "${YELLOW}🔍 Testing backend health...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy and responding!${NC}"
        echo -e "${GREEN}🌐 Backend URL: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
        exit 0
    else
        echo -e "${YELLOW}⏳ Waiting for backend to start... (attempt $i/10)${NC}"
        sleep 2
    fi
done

echo -e "${RED}❌ Backend failed to start properly${NC}"
echo -e "${YELLOW}📝 Check backend.log for details${NC}"
exit 1