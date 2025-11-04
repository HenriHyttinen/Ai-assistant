# Setup Guide for Reviewers

This guide will help you get the Numbers Don't Lie project up and running quickly for review.

## Quick Start (Recommended)

### Option 1: Docker (Easiest)
```bash
# Clone the repository
git clone <repository-url>
cd numbers-dont-lie

# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration if needed

# Start everything
# For Docker Compose v2 (default on newer systems):
docker compose up --build

# OR for Docker Compose v1 (if you have docker-compose installed):
# docker-compose up --build

# The app will be available at:
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup
```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python database_setup/init_db.py
python scripts/comprehensive_seeder.py  # Optional: seeds recipes
uvicorn main:app --reload

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

## Prerequisites

- **Docker & Docker Compose** (for Docker setup)
- **Python 3.11 or 3.12** (for manual setup - **STRONGLY RECOMMENDED**)
  - ⚠️ **Python 3.14 is NOT recommended** - many packages don't have pre-built wheels yet
  - Python 3.14 requires building from source, which often fails on macOS
  - **Use Python 3.11 or 3.12 to avoid compilation issues**
- **Node.js 16+** (for frontend)
- **PostgreSQL 12+** (optional, SQLite works for development)

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

**Required:**
- `DATABASE_URL` - PostgreSQL or SQLite connection string
- `SECRET_KEY` - Random secret key for JWT

**Optional (for full functionality):**
- `OPENAI_API_KEY` - For AI meal generation features
- `USE_OPENAI` - Set to `false` to disable AI features
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` - For authentication

## Database Setup

### With Docker:
Database is automatically set up when you run `docker-compose up`.

### Manual:
```bash
cd backend
python database_setup/init_db.py
python scripts/comprehensive_seeder.py  # Seeds 500+ recipes
```

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/
```

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

**If you must use Python 3.14** (not recommended):
- Expect multiple compilation errors
- May need to install build tools: `brew install gcc libomp`
- May need to upgrade packages: `pip install "pandas>=2.2.0" "scikit-learn>=1.4.0"`
- Compilation may still fail for some packages

**Error: `psycopg2-binary` or `pydantic-core` compilation fails**
```
Building wheel for psycopg2-binary (pyproject.toml) ... error
Building wheel for pydantic-core (pyproject.toml) ... error
```

**Solution:**
- **Use Python 3.11 or 3.12** - These packages have pre-built wheels for these versions
- Python 3.14 requires building from source, which often fails on macOS

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

**Docker issues:**
- Make sure Docker is running
- Check logs: `docker-compose logs -f`

**Database issues:**
- Check DATABASE_URL in .env
- For SQLite, ensure write permissions
- For PostgreSQL, ensure it's running

**AI features not working:**
- Set `USE_OPENAI=false` to disable (project works without AI)
- Or provide valid `OPENAI_API_KEY`

**Frontend not connecting:**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify FRONTEND_URL in backend/.env

## Verification Checklist

After setup, verify:
- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Can create user account
- [ ] Can generate meal plan
- [ ] Database has recipes (check with: `SELECT COUNT(*) FROM recipes`)

## Project Structure

```
numbers-dont-lie/
├── backend/          # FastAPI backend
│   ├── models/       # Database models
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic
│   ├── ai/           # AI integration
│   ├── tests/        # Test suite
│   └── .env.example  # Environment template
├── frontend/         # React frontend
├── docker/           # Docker configuration
├── docker-compose.yml
└── Dockerfile
```

## Key Features to Test

1. **Meal Planning**: Generate daily/weekly meal plans
2. **Recipe Search**: Search and filter 500+ recipes
3. **Daily Logging**: Log food intake and track nutrition
4. **Shopping Lists**: Generate shopping lists from meal plans
5. **Nutritional Analysis**: View macros and micronutrients
6. **Portion Adjustment**: Adjust serving sizes with automatic recalculation
7. **Meal Swapping**: Two-click meal swap functionality

## Notes

- Test suite is in `backend/tests/`
- All API endpoints are documented at `/docs`
- Project uses SQLite by default (no PostgreSQL required)
- AI features are optional (set USE_OPENAI=false if needed)
- Full setup script: `backend/setup_complete.sh`

