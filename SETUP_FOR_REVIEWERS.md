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
python init_db.py
python scripts/comprehensive_seeder.py  # Optional: seeds recipes
uvicorn main:app --reload

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

## Prerequisites

- **Docker & Docker Compose** (for Docker setup)
- **Python 3.11 or 3.12** (for manual setup - recommended)
  - ⚠️ **Python 3.14 is not recommended** - pandas 2.1.3 has compilation issues
  - If using Python 3.14, upgrade pandas: `pip install "pandas>=2.2.0"`
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
python init_db.py
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

**Error: `pandas` compilation fails with Python 3.14**
```
error: too few arguments to function call, expected 6, have 5
_PyLong_AsByteArray
```

**Solution:**
1. **Recommended**: Use Python 3.11 or 3.12 instead
   ```bash
   # Check Python version
   python3 --version
   
   # If using Python 3.14, switch to 3.11 or 3.12
   # Using pyenv or similar:
   pyenv install 3.12.0
   pyenv local 3.12.0
   ```

2. **Alternative** (if must use Python 3.14): Upgrade pandas
   ```bash
   pip install "pandas>=2.2.0"
   ```

**Error: `scikit-learn` compilation fails on macOS**
```
clang: error: unsupported option '-fopenmp'
scikit-learn cannot be built with OpenMP
```

**Solution:**
1. **Recommended**: Use Python 3.11 or 3.12 (fewer compilation issues)
2. **Alternative**: Install newer scikit-learn with pre-built wheels
   ```bash
   pip install "scikit-learn>=1.4.0"
   ```
3. **If compilation still fails**: Install via conda or use pre-built wheels
   ```bash
   # Try installing OpenMP support first (macOS)
   brew install libomp
   
   # Then install scikit-learn
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

