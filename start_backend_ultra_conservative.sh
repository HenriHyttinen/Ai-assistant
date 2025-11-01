#!/bin/bash

# Ultra-Conservative Backend Startup Script for Gaming Environment
# This script uses minimal resources to prevent crashes during gaming

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Numbers Don't Lie Backend (Ultra-Conservative Mode)${NC}"

# Ensure we're in the project root
cd "$(dirname "$0")"

# Kill any existing backend processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn main:app" || true
sleep 3

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source venv/bin/activate

# Set environment variables for minimal resource usage
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export MALLOC_TRIM_THRESHOLD_=65536
export MALLOC_MMAP_THRESHOLD_=65536
export MALLOC_MMAP_MAX_=32768
export PYTHONHASHSEED=0

# Navigate to backend directory
cd backend

# Start backend with ultra-conservative settings
echo -e "${GREEN}🎮 Starting backend with ultra-conservative settings...${NC}"
echo -e "${YELLOW}Settings: 1 worker, 15s timeout, 5 concurrency, 20 backlog${NC}"

# Use nohup to prevent terminal closure from killing the process
nohup python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --timeout-keep-alive 15 \
    --limit-concurrency 5 \
    --backlog 20 \
    --access-log \
    --log-level warning \
    > ../backend.log 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

echo -e "${GREEN}✅ Backend started with PID: $BACKEND_PID${NC}"
echo -e "${YELLOW}📝 Logs are being written to: backend.log${NC}"
echo -e "${YELLOW}🆔 Process ID saved to: backend.pid${NC}"

# Wait a moment for startup
sleep 5

# Test if backend is responding
echo -e "${YELLOW}🔍 Testing backend health...${NC}"
for i in {1..15}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy and responding!${NC}"
        echo -e "${GREEN}🌐 Backend URL: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API Docs: http://localhost:8000/docs${NC}"
        exit 0
    else
        echo -e "${YELLOW}⏳ Waiting for backend to start... (attempt $i/15)${NC}"
        sleep 3
    fi
done

echo -e "${RED}❌ Backend failed to start properly${NC}"
echo -e "${YELLOW}📝 Check backend.log for details${NC}"
exit 1






