# Database Setup for Reviewers

This guide helps reviewers set up the database for the Numbers Don't Lie project.

## Quick Setup

### Option 1: Using init_db.py (Recommended)

```bash
cd backend
source venv/bin/activate  # Make sure virtual environment is activated
python database_setup/init_db.py
```

This script:
- Creates all database tables
- Sets up the database schema
- Verifies the setup

### Option 2: Using Python One-liner

```bash
cd backend
source venv/bin/activate
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine); print('Database setup complete!')"
```

### Option 3: Manual Setup

```bash
cd backend
source venv/bin/activate
python -c "
from database import SessionLocal, engine
from models import Base
Base.metadata.create_all(bind=engine)
print('Database setup complete!')
"
```

## Seed Database (Optional but Recommended)

After initializing the database, you can seed it with recipes and ingredients:

```bash
cd backend
source venv/bin/activate
python scripts/comprehensive_seeder.py
```

This will seed:
- 500+ recipes with vector embeddings
- 15,532+ ingredients with nutritional data
- Vector embeddings for RAG functionality

**Note:** Seeding can take a few minutes depending on your system.

## Verify Database Setup

To verify the database is set up correctly:

```bash
cd backend
source venv/bin/activate
python verify_database.py
```

This checks:
- Recipe count (≥500)
- Ingredient count (≥500, target: 15,532+)
- Embedding coverage (100% for recipes and ingredients)
- Embedding dimensions (384 for all-MiniLM-L6-v2)

## Troubleshooting

### Error: "No module named 'database'"

**Solution:** Make sure you're in the backend directory:
```bash
cd backend
```

### Error: "No module named 'models'"

**Solution:** 
1. Make sure you're in the `backend/` directory
2. Ensure virtual environment is activated
3. Verify all dependencies are installed: `pip install -r requirements.txt`

### Error: "Virtual environment not found"

**Solution:** Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Permission denied"

**Solution:** This usually means the database file location doesn't have write permissions. Check:
- Database file location in `.env` (DATABASE_URL)
- File system permissions
- For SQLite, ensure the directory is writable

### Error: Database already exists

**Solution:** If you want to start fresh:
```bash
# For SQLite, delete the database file
rm numbers_dont_lie.db  # or whatever your database file is named

# Then run init_db.py again
python database_setup/init_db.py
```

## What the Setup Does

1. **Creates database file** (if using SQLite) or connects to PostgreSQL
2. **Creates all database tables** using SQLAlchemy models
3. **Sets up relationships** between tables
4. **Verifies the setup** works correctly

## Database Location

- **SQLite**: Database file is created in the `backend/` directory (location specified in DATABASE_URL)
- **PostgreSQL**: Connects to the PostgreSQL server specified in DATABASE_URL
- **Tables created**: All tables defined in `models/` directory

## Database Schema

The database includes:
- **Users**: User accounts and authentication
- **Health Profiles**: User health data (weight, height, BMI, etc.)
- **Recipes**: 500+ recipes with ingredients and instructions
- **Ingredients**: 15,532+ ingredients with nutritional data
- **Meal Plans**: User meal plans (daily/weekly)
- **Meal Plan Meals**: Individual meals in meal plans
- **Nutrition Preferences**: User dietary preferences and allergies
- **Shopping Lists**: Shopping lists generated from meal plans
- **Nutritional Logs**: Daily nutritional intake tracking
- **Goals**: User nutrition and health goals

## Verification

After setup, you can verify it worked by checking tables:

```bash
cd backend
source venv/bin/activate
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text(\"SELECT name FROM sqlite_master WHERE type='table'\"))
tables = [row[0] for row in result]
print('Tables created:', len(tables))
for table in tables:
    print(f'  - {table}')
db.close()
"
```

## Common Issues

1. **Wrong directory:** Always run from `backend/` directory
2. **Missing venv:** Make sure virtual environment is activated
3. **Missing dependencies:** Run `pip install -r requirements.txt`
4. **Database connection errors:** Check DATABASE_URL in `.env`
5. **Permission issues:** Ensure write permissions for database location

## Support

If you encounter issues:
1. Check you're in the correct directory (`backend/`)
2. Ensure virtual environment is activated
3. Verify all dependencies are installed
4. Check DATABASE_URL in `.env` file
5. Try the manual setup option above
6. Check the main SETUP_FOR_REVIEWERS.md for more troubleshooting
