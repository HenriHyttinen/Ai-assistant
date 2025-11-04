#!/bin/bash

# Complete Setup Script for Numbers Don't Lie
# This script sets up the entire backend from scratch

set -e  # Exit on error

echo "🚀 Starting complete setup for Numbers Don't Lie backend..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the backend directory${NC}"
    exit 1
fi

# Step 1: Create virtual environment
echo -e "\n${YELLOW}Step 1: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Step 2: Activate virtual environment
echo -e "\n${YELLOW}Step 2: Activating virtual environment...${NC}"
source venv/bin/activate

# Step 3: Install dependencies
echo -e "\n${YELLOW}Step 3: Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 4: Create .env file if it doesn't exist
echo -e "\n${YELLOW}Step 4: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOL'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie
# OR for SQLite (development):
# DATABASE_URL=sqlite:///./dev.db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI Configuration (Optional - for AI features)
OPENAI_API_KEY=your-openai-api-key-here
USE_OPENAI=false

# Email Configuration (Optional - for email verification)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_FROM=noreply@example.com
MAIL_FROM_NAME=Numbers Don't Lie

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Supabase Configuration (for authentication)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
EOL
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please update .env file with your actual configuration values${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, skipping creation${NC}"
fi

# Step 5: Initialize database
echo -e "\n${YELLOW}Step 5: Initializing database...${NC}"
if python init_db.py 2>/dev/null; then
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Database initialization script not found, trying alternative...${NC}"
    if [ -f "database_setup/init_db.py" ]; then
        python database_setup/init_db.py
        echo -e "${GREEN}✅ Database initialized${NC}"
    else
        echo -e "${YELLOW}⚠️  Manual database initialization required${NC}"
    fi
fi

# Step 6: Populate database with recipes and ingredients
echo -e "\n${YELLOW}Step 6: Populating database with recipes and ingredients...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"

if [ -f "scripts/comprehensive_seeder.py" ]; then
    python scripts/comprehensive_seeder.py
    echo -e "${GREEN}✅ Database populated with recipes and ingredients${NC}"
else
    echo -e "${YELLOW}⚠️  comprehensive_seeder.py not found. Manual seeding required.${NC}"
    echo -e "${YELLOW}   Check scripts/ directory for seeder script${NC}"
fi

# Step 7: Generate vector embeddings (optional)
echo -e "\n${YELLOW}Step 7: Generating vector embeddings for RAG...${NC}"
if [ -f "scripts/generate_recipe_embeddings.py" ]; then
    if python -c "import sentence_transformers" 2>/dev/null; then
        python scripts/generate_recipe_embeddings.py || echo -e "${YELLOW}⚠️  Embedding generation failed (optional step)${NC}"
        echo -e "${GREEN}✅ Vector embeddings generated${NC}"
    else
        echo -e "${YELLOW}⚠️  sentence-transformers not installed. Skipping embedding generation.${NC}"
        echo -e "${YELLOW}   Install with: pip install sentence-transformers${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Embedding generation script not found${NC}"
fi

# Step 8: Verify database population
echo -e "\n${YELLOW}Step 8: Verifying database population...${NC}"
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
try:
    result = db.execute(text('SELECT COUNT(*) FROM recipes')).scalar()
    print(f'   Recipes: {result}')
    result = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
    print(f'   Ingredients: {result}')
    if result >= 500:
        print('✅ Database population verified')
    else:
        print('⚠️  Warning: Fewer than 500 ingredients found')
except Exception as e:
    print(f'⚠️  Could not verify: {e}')
finally:
    db.close()
" || echo -e "${YELLOW}⚠️  Could not verify database population${NC}"

# Final summary
echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Update .env file with your actual configuration values"
echo -e "2. Start the backend server: ${GREEN}uvicorn main:app --reload${NC}"
echo -e "3. Access API documentation: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Note:${NC} If AI features are needed, set OPENAI_API_KEY in .env"
echo -e "${YELLOW}Note:${NC} Database seeding can be re-run anytime with: python scripts/comprehensive_seeder.py"

