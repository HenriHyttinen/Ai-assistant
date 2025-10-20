# Database Setup Guide

This guide explains how to set up the database for the Numbers Don't Lie application.

## Quick Setup

If you're getting errors about missing tables, run this command:

```bash
cd backend
source venv/bin/activate
python3 setup_database.py
```

This will create all necessary tables and populate the achievements.

## Manual Setup (Alternative)

If you prefer to set up the database manually:

1. **Initialize the database:**
   ```bash
   cd backend
   source venv/bin/activate
   python3 init_db.py
   ```

2. **Create achievements:**
   ```bash
   python3 setup_achievements.py
   ```

## Troubleshooting

### Error: "no such table: achievements"

This error occurs when the achievements table hasn't been created. The solution is to run the database setup script:

```bash
cd backend
source venv/bin/activate
python3 setup_database.py
```

### Error: "ModuleNotFoundError: No module named 'sqlalchemy'"

Make sure you're in the virtual environment:

```bash
cd backend
source venv/bin/activate
```

### Error: "When initializing mapper..."

This is a circular import issue. Use the `setup_database.py` script instead of the ORM-based scripts.

## Database Structure

The application uses the following main tables:

- `users` - User accounts and authentication
- `health_profiles` - User health information
- `activity_logs` - User activity tracking
- `goals` - User fitness goals
- `achievements` - Available achievements
- `user_achievements` - User progress on achievements
- `user_settings` - User preferences
- `data_consent` - User consent for data processing

## Verification

To verify the database is set up correctly:

```bash
cd backend
source venv/bin/activate
python3 -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM achievements')).scalar()
print(f'Achievements in database: {result}')
db.close()
"
```

You should see "Achievements in database: 15" if everything is set up correctly.
