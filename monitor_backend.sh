#!/bin/bash

# Backend Health Monitor and Auto-Restart Script
# This script monitors the backend and restarts it if it becomes unresponsive

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8000"
CHECK_INTERVAL=15
MAX_RETRIES=3
RETRY_DELAY=5

echo -e "${BLUE}🔍 Starting Backend Health Monitor${NC}"
echo -e "${YELLOW}Backend URL: $BACKEND_URL${NC}"
echo -e "${YELLOW}Check interval: ${CHECK_INTERVAL}s${NC}"
echo -e "${YELLOW}Max retries: $MAX_RETRIES${NC}"

# Function to check backend health
check_backend_health() {
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL" --max-time 5 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        return 0  # Healthy
    else
        return 1  # Unhealthy
    fi
}

# Function to restart backend
restart_backend() {
    echo -e "${YELLOW}🔄 Restarting backend...${NC}"
    
    # Kill existing backend processes
    pkill -f "uvicorn main:app" || true
    sleep 2
    
    # Start backend using the robust script
    ./start_backend_robust.sh
    
    # Wait for startup
    sleep 5
}

# Function to check if backend process is running
is_backend_running() {
    pgrep -f "uvicorn main:app" > /dev/null
}

# Main monitoring loop
retry_count=0
consecutive_failures=0

while true; do
    echo -e "${BLUE}🔍 Checking backend health...${NC}"
    
    if check_backend_health; then
        if [ $consecutive_failures -gt 0 ]; then
            echo -e "${GREEN}✅ Backend is healthy again!${NC}"
        fi
        consecutive_failures=0
        retry_count=0
    else
        consecutive_failures=$((consecutive_failures + 1))
        echo -e "${RED}❌ Backend health check failed (attempt $consecutive_failures)${NC}"
        
        # Check if backend process is still running
        if ! is_backend_running; then
            echo -e "${RED}💀 Backend process is not running${NC}"
        else
            echo -e "${YELLOW}⚠️ Backend process is running but not responding${NC}"
        fi
        
        # Restart if we've had too many consecutive failures
        if [ $consecutive_failures -ge $MAX_RETRIES ]; then
            echo -e "${YELLOW}🔄 Too many consecutive failures, restarting backend...${NC}"
            restart_backend
            consecutive_failures=0
            retry_count=$((retry_count + 1))
            
            if [ $retry_count -ge 5 ]; then
                echo -e "${RED}💥 Too many restart attempts, giving up${NC}"
                exit 1
            fi
        fi
    fi
    
    echo -e "${BLUE}⏳ Waiting ${CHECK_INTERVAL}s before next check...${NC}"
    sleep $CHECK_INTERVAL
done







