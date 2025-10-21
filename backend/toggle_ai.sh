#!/bin/bash

# Toggle AI insights on/off for testing
ENV_FILE="/home/deepessence/numbers-dont-lie/backend/.env"

if grep -q "USE_OPENAI=true" "$ENV_FILE"; then
    echo "🔄 Turning OFF AI insights (using mock data)..."
    sed -i 's/USE_OPENAI=true/USE_OPENAI=false/' "$ENV_FILE"
    echo "✅ AI insights are now OFF - using mock data (no credits spent)"
elif grep -q "USE_OPENAI=false" "$ENV_FILE"; then
    echo "🔄 Turning ON AI insights (using real OpenAI)..."
    sed -i 's/USE_OPENAI=false/USE_OPENAI=true/' "$ENV_FILE"
    echo "✅ AI insights are now ON - using real OpenAI API"
else
    echo "❌ Could not find USE_OPENAI setting in .env file"
fi

echo ""
echo "Current status:"
grep "USE_OPENAI" "$ENV_FILE"
echo ""
echo "💡 Restart the server to apply changes:"
echo "   pkill -f uvicorn && cd /home/deepessence/numbers-dont-lie/backend && source venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
