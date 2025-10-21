# Database Setup for Reviewers

## Quick Setup (Recommended)

### Option 1: Simple Shell Script
```bash
cd /path/to/numbers-dont-lie/backend
./database_setup/quick_setup.sh
```

### Option 2: Python Script
```bash
cd /path/to/numbers-dont-lie/backend
python database_setup/simple_setup.py
```

### Option 3: Manual Setup
```bash
cd /path/to/numbers-dont-lie/backend
source venv/bin/activate
python -c "
from database import SessionLocal, engine
from models import Base
Base.metadata.create_all(bind=engine)
print('Database setup complete!')
"
```

## Troubleshooting

### Error: "No module named 'database'"
**Solution:** Make sure you're in the backend directory:
```bash
cd /path/to/numbers-dont-lie/backend
```

### Error: "Virtual environment not found"
**Solution:** Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Permission denied"
**Solution:** Make the script executable:
```bash
chmod +x database_setup/quick_setup.sh
```

## What the Setup Does

1. **Creates database file** (`dev.db`) if it doesn't exist
2. **Creates all database tables** using SQLAlchemy models
3. **Tests database connection** to ensure everything works
4. **Provides clear error messages** if something goes wrong

## Database Location

- **Database file:** `backend/dev.db`
- **Database type:** SQLite (no external database server needed)
- **Tables created:** All tables defined in `models.py`

## Verification

After setup, you can verify it worked by:
```bash
cd /path/to/numbers-dont-lie/backend
source venv/bin/activate
python -c "
from database import SessionLocal
db = SessionLocal()
result = db.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = [row[0] for row in result]
print('Tables created:', tables)
db.close()
"
```

## Common Issues

1. **Wrong directory:** Always run from `backend/` directory
2. **Missing venv:** Make sure virtual environment is activated
3. **Missing dependencies:** Run `pip install -r requirements.txt`
4. **Permission issues:** Use `chmod +x` on shell scripts

## Support

If you encounter issues:
1. Check you're in the correct directory (`backend/`)
2. Ensure virtual environment is activated
3. Verify all dependencies are installed
4. Try the manual setup option above
