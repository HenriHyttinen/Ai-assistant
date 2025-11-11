# Setup Guide for Reviewers

Quick guide to get the project running. I recommend using SQLite for the database - it's simpler and doesn't require setting up PostgreSQL.

## Prerequisites

- **Python 3.11 or 3.12** (important - Python 3.14 causes issues with some packages)
- **Node.js 16+** (for frontend)
- **SQLite** (comes with Python - no setup needed) or PostgreSQL (optional)
- **pip** and **npm** installed

## Quick Start

### 1. Clone the Repository

```bash
git clone https://gitea.kood.tech/henrijuhanihyttinen/ai-assistant
cd ai-assistant
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment file
cp .env.example .env

# IMPORTANT: Edit .env and set DATABASE_URL
# For SQLite (easiest - recommended):
# DATABASE_URL=sqlite:///./numbers_dont_lie.db
# 
# For PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie

# Create database tables
# Make sure you're in the backend/ directory when running this!
python database_setup/init_db.py

# Seed basic recipes and ingredients
python scripts/comprehensive_seeder.py

# Import full ingredient database (IMPORTANT - adds 5,388 ingredients)
python scripts/import_ingredients_from_json.py

# Generate embeddings (REQUIRED for recipe search and RAG)
python scripts/generate_recipe_embeddings.py
python scripts/generate_ingredient_embeddings.py

# Recalculate recipe nutrition from ingredients (IMPORTANT - fixes 0 calorie issue)
python scripts/recalculate_recipe_nutrition.py

# Start the backend server
uvicorn main:app --reload
```

The backend API will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 3. Frontend Setup (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the frontend development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

## Environment Variables

The `.env` file needs at minimum the `DATABASE_URL`. Here's the simplest setup:

**For SQLite (recommended - no database server needed):**
```env
DATABASE_URL=sqlite:///./numbers_dont_lie.db
SECRET_KEY=any-random-string-here-make-it-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**For PostgreSQL:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie
SECRET_KEY=any-random-string-here-make-it-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Optional (for meal generation features):**
- `OPENAI_API_KEY` - If you want to use meal generation features
- `USE_OPENAI` - Set to `false` if you don't have an API key (project works without it)
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` - For authentication

**Important:** Make sure `DATABASE_URL` is set correctly. If you get "no such table" errors, check that the database was initialized properly.

## Database Setup

### Step 1: Initialize Database

**IMPORTANT:** Make sure you're in the `backend/` directory when running this!

```bash
cd backend
source venv/bin/activate  # Make sure venv is activated
python database_setup/init_db.py
```

This creates all database tables. If you get "ModuleNotFoundError: No module named 'models'", it means you're not in the backend directory. Make sure you `cd backend` first!

### Seed Database (Required for Full Functionality)

**Step 1: Seed Basic Recipes and Ingredients**

```bash
cd backend
python scripts/comprehensive_seeder.py
```

This will seed:
- 500+ recipes
- ~155 basic ingredients

**Step 2: Import Full Ingredient Database (IMPORTANT)**

The comprehensive seeder only creates ~155 ingredients. To get the full ingredient database (5,388 ingredients), you need to import from JSON:

```bash
cd backend
python scripts/import_ingredients_from_json.py
```

This will:
- Import 5,388 ingredients from `ingredients_list.json`
- Add to existing ingredients (total: ~5,543 ingredients)

**Step 3: Generate Embeddings (REQUIRED for RAG)**

Embeddings are required for recipe search and RAG functionality. Generate them after seeding:

```bash
# Generate recipe embeddings (takes ~5-15 minutes)
cd backend
python scripts/generate_recipe_embeddings.py

# Generate ingredient embeddings (takes ~2-5 minutes)
python scripts/generate_ingredient_embeddings.py
```

**Summary:**
1. ✅ Seed basic data: `python scripts/comprehensive_seeder.py` (500 recipes, 155 ingredients)
2. ✅ Import full ingredients: `python scripts/import_ingredients_from_json.py` (adds 5,388 ingredients)
3. ✅ Generate embeddings: Run both embedding scripts (required for search/RAG)

### Verify Database

To verify the database is set up correctly:

```bash
cd backend
python verify_database.py
```

This checks:
- Recipe count (≥500)
- Ingredient count (≥500, target: 15,532+)
- Embedding coverage (100% for recipes and ingredients)

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/
```

Note: Current test coverage is minimal. Manual testing has been performed throughout development.

## Troubleshooting

### Python Version Issues

**⚠️ IMPORTANT: Use Python 3.11 or 3.12**

Python 3.14 is too new and many packages don't have pre-built wheels yet, causing compilation errors:
- `pandas` compilation fails
- `scikit-learn` compilation fails
- `psycopg2-binary` compilation fails
- `pydantic-core` compilation fails

**Solution: Use Python 3.11 or 3.12 (RECOMMENDED)**

```bash
# Check Python version
python3 --version

# If using Python 3.14, switch to 3.11 or 3.12
# Using pyenv:
pyenv install 3.12.0
pyenv local 3.12.0

# Or using Homebrew:
brew install python@3.12
python3.12 -m venv venv
source venv/bin/activate
```

**Error: `psycopg2-binary` or `pydantic-core` compilation fails**
```
Building wheel for psycopg2-binary (pyproject.toml) ... error
Building wheel for pydantic-core (pyproject.toml) ... error
```

**Solution:**
- **Use Python 3.11 or 3.12** - These packages have pre-built wheels for these versions
- Python 3.14 requires building from source, which often fails on macOS

**Error: `ModuleNotFoundError: No module named 'models'` when running `init_db.py`**

This happens when you're not in the right directory. 

**Solution:**
1. Make absolutely sure you're in the `backend/` directory:
   ```bash
   cd backend
   pwd  # Should show .../ai-assistant/backend
   python database_setup/init_db.py
   ```

2. If that doesn't work, try the alternative:
   ```bash
   cd backend
   python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine); print('Done!')"
   ```

3. Check that your virtual environment is activated and dependencies are installed:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

**Error: `scikit-learn` compilation fails on macOS**
```
clang: error: unsupported option '-fopenmp'
scikit-learn cannot be built with OpenMP
```

**Solution:**
1. **Recommended**: Use Python 3.11 or 3.12 (pre-built wheels available)
2. **If using Python 3.14**: Install OpenMP and upgrade scikit-learn
   ```bash
   # Install OpenMP support (macOS)
   brew install libomp
   export LDFLAGS="-L/opt/homebrew/opt/libomp/lib"
   export CPPFLAGS="-I/opt/homebrew/opt/libomp/include"
   
   # Install newer scikit-learn
   pip install "scikit-learn>=1.4.0"
   ```

**Database issues:**
- Check DATABASE_URL in `.env`
- For SQLite, ensure write permissions
- For PostgreSQL, ensure it's running and accessible

**AI features not working:**
- Set `USE_OPENAI=false` to disable (project works without AI)
- Or provide valid `OPENAI_API_KEY`

**Frontend not connecting:**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API URL in frontend configuration

## Verification Checklist

After setup, verify:
- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Can create user account
- [ ] Can generate meal plan
- [ ] Database has recipes (check with: `python verify_database.py`)

## Project Structure

```
counting-calories/
├── backend/          # FastAPI backend
│   ├── models/       # Database models
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   ├── ai/           # AI integration
│   ├── scripts/      # Utility scripts (seeding, etc.)
│   ├── database_setup/  # Database initialization
│   ├── tests/        # Test suite
│   └── .env.example  # Environment template
├── frontend/         # React frontend
├── docs/             # Documentation
└── README.md         # Main README
```

## Key Features to Test

1. **Meal Planning**: Generate daily/weekly meal plans
2. **Recipe Search**: Search and filter 500+ recipes by cuisine, dietary restrictions, macronutrients
3. **Daily Logging**: Log food intake and track nutrition
4. **Shopping Lists**: Generate shopping lists from meal plans
5. **Nutritional Analysis**: View macros and micronutrients
6. **Portion Adjustment**: Adjust serving sizes with automatic recalculation
7. **Meal Swapping**: Swap meals between dates
8. **Meal Alternatives**: Get alternative meal suggestions based on preferences

## Notes

- Test suite is in `backend/tests/`
- All API endpoints are documented at `/docs`
- Project uses SQLite by default (no PostgreSQL required)
- AI features are optional (set `USE_OPENAI=false` if needed)
- Database seeding is optional but recommended for full functionality
- Full database verification: `python backend/verify_database.py`
