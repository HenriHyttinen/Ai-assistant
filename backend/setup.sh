#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Database settings
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie

# JWT settings
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email settings (SendGrid SMTP)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
# IMPORTANT: replace with a NEW SendGrid API key (rotate if leaked)
MAIL_PASSWORD=REPLACE_WITH_NEW_SENDGRID_API_KEY
# IMPORTANT: set to the exact Single Sender or domain-authenticated address you verified
MAIL_FROM=REPLACE_WITH_VERIFIED_SENDER@example.com
MAIL_FROM_NAME="Numbers Don't Lie"
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
USE_CREDENTIALS=True

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Security settings
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_LENGTH=100
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Logging settings
LOG_LEVEL=INFO
EOL
    echo "Please update the .env file with your actual configuration values."
fi

# Create logs directory
mkdir -p logs

# Create templates directory if it doesn't exist
mkdir -p templates

echo "Setup complete! Please update the .env file with your actual configuration values."
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python main.py" 