#!/bin/bash

# Numbers Don't Lie Health App - Manual Startup Script
# NOTE: Docker setup is not currently working. Use manual setup instead.
# See SETUP_FOR_REVIEWERS.md for manual setup instructions.

set -e

echo "Numbers Don't Lie Health App"
echo "============================"
echo ""
echo "⚠️  NOTE: Docker setup is not currently working."
echo "Please use manual setup instead."
echo ""
echo "For setup instructions, see: SETUP_FOR_REVIEWERS.md"
echo ""
echo "Quick manual setup:"
echo "1. Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Frontend: cd frontend && npm install && npm run dev"
echo ""
exit 1
