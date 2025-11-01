#!/bin/bash
# Start backend with health monitoring for gaming environment

echo "🚀 Starting Numbers Don't Lie Backend with Health Monitoring"
echo "=============================================================="

# Kill any existing backend processes
echo "🔄 Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
cd /home/deepessence/numbers-dont-lie
source venv/bin/activate

# Install requests if not available
echo "📦 Ensuring dependencies are available..."
pip install requests > /dev/null 2>&1

# Start the health monitor
echo "🏥 Starting backend health monitor..."
cd backend
python health_monitor.py







