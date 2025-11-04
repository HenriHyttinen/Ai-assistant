# Complete Setup Guide for Reviewers

This guide provides step-by-step instructions to set up the Numbers Don't Lie project from scratch, including database initialization, recipe/ingredient seeding, and environment configuration.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (or SQLite for development)
- pip (Python package manager)
- Git

## Quick Setup (One Command)

For the fastest setup experience:

```bash
cd backend
./setup_complete.sh
```

This script will:
1. Create virtual environment
2. Install dependencies
3. Set up environment variables
4. Initialize database
5. Populate 500+ recipes and 500+ ingredients
6. Generate vector embeddings for RAG
7. Create sample user data

## Manual Setup (Step by Step)

### Step 1: Clone and Navigate

```bash
git clone <repository-url>
cd numbers-dont-lie
cd backend
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```bash
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
USE_OPENAI=true

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
```

**Important:** Replace placeholder values with your actual configuration.

### Step 5: Initialize Database

```bash
# Create all database tables
python init_db.py

# Or using the database_setup script
python database_setup/init_db.py
```

### Step 6: Populate Database with Recipes and Ingredients

Choose one of the following seeding scripts:

#### Option A: Comprehensive Seeder (Recommended) ⭐
```bash
python scripts/comprehensive_seeder.py
```
Creates 500+ recipes and 500+ ingredients with comprehensive nutrition data.

**Note**: This is the only seeder you need. Other seeders in the scripts folder are legacy/development scripts.

### Step 7: Generate Vector Embeddings (for RAG)

```bash
python scripts/generate_recipe_embeddings.py
```

This generates embeddings for all recipes to enable RAG (Retrieval-Augmented Generation) functionality.

**Note:** This step requires the `sentence-transformers` package. If not installed:
```bash
pip install sentence-transformers
```

### Step 8: Verify Database Population

```bash
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM recipes')).scalar()
print(f'Recipes in database: {result}')
result = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
print(f'Ingredients in database: {result}')
db.close()
"
```

Expected output:
- Recipes: 500+ (should be ≥500)
- Ingredients: 500+ (should be ≥500, likely 15,000+)

### Step 9: Run the Backend Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Docker Setup (Alternative)

If you prefer Docker:

```bash
# From project root
docker-compose up --build
```

This will:
- Build backend and frontend containers
- Set up PostgreSQL database
- Initialize tables
- Start all services

**Note:** Database seeding must be done after containers are running:

```bash
# Enter backend container
docker-compose exec backend bash

# Run seeder
python scripts/comprehensive_seeder.py
python scripts/generate_recipe_embeddings.py
```

## Verification Checklist

After setup, verify:

- [ ] Database tables created (run `python init_db.py`)
- [ ] Recipes populated (count should be ≥500)
- [ ] Ingredients populated (count should be ≥500)
- [ ] Vector embeddings generated (recipes have embedding column populated)
- [ ] Backend server starts without errors
- [ ] API documentation accessible at `/docs`
- [ ] Health endpoints respond correctly

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:** Ensure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Database connection error"

**Solution:** Check DATABASE_URL in `.env` file:
- PostgreSQL: Ensure PostgreSQL is running
- SQLite: Ensure write permissions in backend directory

### Issue: "No recipes/ingredients found"

**Solution:** Run the seeding script:
```bash
python scripts/comprehensive_seeder.py
```

### Issue: "sentence-transformers not found"

**Solution:** Install the package:
```bash
pip install sentence-transformers
```

### Issue: "OpenAI API errors"

**Solution:** AI features are optional. Either:
1. Set `USE_OPENAI=false` in `.env`
2. Or provide a valid `OPENAI_API_KEY`

### Issue: "Port 8000 already in use"

**Solution:** Change the port:
```bash
uvicorn main:app --reload --port 8001
```

## Database Schema Overview

Key tables:
- `users` - User accounts and authentication
- `health_profiles` - User health information (Project 1)
- `nutrition_preferences` - Dietary preferences and targets
- `recipes` - Recipe database (500+ entries)
- `ingredients` - Ingredient database (500+ entries, 15,000+ available)
- `meal_plans` - User meal plans
- `meal_plan_meals` - Individual meals in plans
- `nutritional_logs` - Daily nutrition tracking
- `shopping_lists` - Generated shopping lists

## Additional Setup Scripts (Optional)

### Essential Scripts Only
For reviewers, only these scripts are needed:
- `scripts/comprehensive_seeder.py` - Main seeder (required)
- `scripts/generate_recipe_embeddings.py` - For RAG (optional but recommended)
- `scripts/seed_goals_direct.py` - Goal templates (optional)

See `scripts/ESSENTIAL_SCRIPTS.md` for details.

### Maintenance Scripts (Only if needed)
- `scripts/audit_and_fix_recipe_nutrition.py` - Validate nutrition (if issues found)
- `scripts/populate_ingredient_micronutrients.py` - Add micronutrient data (optional)

**Note**: Most scripts in `scripts/` are development/maintenance scripts and not needed for review.

## Testing the Setup

1. **Test API endpoints:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test recipe search:**
   ```bash
   curl http://localhost:8000/api/nutrition/recipes/search
   ```

3. **Access API docs:**
   Open `http://localhost:8000/docs` in browser

## Next Steps

After setup is complete:

1. **Frontend Setup:** See `frontend/README.md`
2. **API Documentation:** Visit `http://localhost:8000/docs`
3. **Testing:** Run test suite (if available)
4. **Development:** Start coding!

## Support

If you encounter issues not covered here:

1. Check logs for error messages
2. Verify all environment variables are set
3. Ensure database is accessible
4. Verify all dependencies are installed
5. Check Python version (should be 3.8+)

## Notes for Reviewers

- All database seeding scripts are in `backend/scripts/`
- The main seeder is `comprehensive_seeder.py` which creates 500+ recipes and ingredients
- Vector embeddings are optional but recommended for full RAG functionality
- AI features can be disabled by setting `USE_OPENAI=false`
- Project 1 features (health profiles, wellness scores) are preserved and functional

