# Database Setup Scripts

This directory contains all database-related setup and migration scripts.

## Files:

- `init_db.py` - Main database initialization
- `init_db.sh` - Shell script for database setup
- `setup_database.py` - Database schema setup
- `setup_achievements.py` - Achievement system setup
- `setup_reviewer.py` - Reviewer account setup
- `create_achievements.py` - Achievement creation
- `create_test_account.py` - Test account creation
- `migrate_activity_logs.py` - Activity logs migration
- `migrate_encrypt_data.py` - Data encryption migration
- `fix_performed_at_column.py` - Column fix migration
- `setup.sh` - Complete setup script
- `DATABASE_SETUP.md` - Database setup documentation

## Usage:

### Quick Setup (Recommended for Reviewers)

**Option 1: Simple Shell Script**
```bash
cd /path/to/numbers-dont-lie/backend
./database_setup/quick_setup.sh
```

**Option 2: Python Script**
```bash
cd /path/to/numbers-dont-lie/backend
python database_setup/simple_setup.py
```

**Option 3: Manual Setup**
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

### Manual Setup

For complete setup with all features:
```bash
cd database_setup
./setup.sh
```

Or run individual scripts as needed for specific setup tasks.

### Troubleshooting

If you encounter issues, see `REVIEWER_SETUP.md` for detailed troubleshooting steps.
