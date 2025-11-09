# Setup Guide for Reviewers

This guide will help you get the Numbers Don't Lie project up and running quickly for review.

## Prerequisites

- **Python 3.11 or 3.12** (STRONGLY RECOMMENDED)
  - ⚠️ **Python 3.14 is NOT recommended** - many packages don't have pre-built wheels yet
  - Python 3.14 requires building from source, which often fails on macOS
  - **Use Python 3.11 or 3.12 to avoid compilation issues**
- **Node.js 16+** (for frontend)
- **PostgreSQL 12+** (optional, SQLite works for development)
- **pip** (Python package manager)
- **npm** (Node package manager)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://gitea.kood.tech/henrijuhanihyttinen/counting-calories
cd counting-calories
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

# Copy environment file
cp .env.example .env
# Edit .env with your settings (see Environment Variables below)

# Initialize database
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

Copy `backend/.env.example` to `backend/.env` and configure:

**Required:**
- `DATABASE_URL` - PostgreSQL or SQLite connection string
  - For SQLite: `sqlite:///./numbers_dont_lie.db`
  - For PostgreSQL: `postgresql://postgres:postgres@localhost/numbers_dont_lie`
- `SECRET_KEY` - Random secret key for JWT (generate a random string)

**Optional (for full functionality):**
- `OPENAI_API_KEY` - For AI meal generation features
- `USE_OPENAI` - Set to `false` to disable AI features (default: `true`)
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` - For authentication

Example `.env` file:
```env
DATABASE_URL=sqlite:///./numbers_dont_lie.db
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
USE_OPENAI=true
```

## Database Setup

### Initialize Database

```bash
cd backend
python database_setup/init_db.py
```

This creates all necessary database tables.

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
```
File "backend/database_setup/init_db.py", line 1, in <module>
    from models import Base
ModuleNotFoundError: No module named 'models'
```

**Solution:**
1. **Make sure you're in the `backend/` directory** when running the script:
   ```bash
   cd backend
   python database_setup/init_db.py
   ```

2. **Alternative**: Use the Python one-liner (works from any directory):
   ```bash
   cd backend
   python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
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
