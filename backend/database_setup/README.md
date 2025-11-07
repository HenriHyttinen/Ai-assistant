# Database Setup Scripts

This directory contains all database-related setup and migration scripts.

## Quick Setup (Recommended)

### Option 1: Using init_db.py (Recommended)

```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
```

This creates all necessary database tables.

### Option 2: Using Python One-liner

```bash
cd backend
source venv/bin/activate
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine); print('Database setup complete!')"
```

## Seed Database (Optional but Recommended)

After initializing the database, seed it with recipes and ingredients:

```bash
cd backend
source venv/bin/activate
python scripts/comprehensive_seeder.py
```

This seeds:
- 500+ recipes with vector embeddings
- 15,532+ ingredients with nutritional data
- Vector embeddings for RAG functionality

## Available Scripts

### Core Setup Scripts
- `init_db.py` - Main database initialization (creates all tables)
- `setup_achievements.py` - Achievement system setup
- `create_test_account.py` - Test account creation
- `create_achievements.py` - Achievement creation

### Migration Scripts
- `migrate_activity_logs.py` - Activity logs migration
- `migrate_encrypt_data.py` - Data encryption migration
- `fix_performed_at_column.py` - Column fix migration

### Shell Scripts
- `init_db.sh` - Shell script for database setup
- `quick_setup.sh` - Quick setup script
- `setup.sh` - Complete setup script

## Documentation

- `DATABASE_SETUP.md` - Database setup documentation
- `REVIEWER_SETUP.md` - Reviewer-specific setup guide
- `README.md` - This file

## Usage Examples

### Basic Setup
```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
```

### Full Setup with Seeding
```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
python scripts/comprehensive_seeder.py
python database_setup/setup_achievements.py
```

### Create Test Account
```bash
cd backend
source venv/bin/activate
python database_setup/create_test_account.py
```

### Fix Database Issues
```bash
cd backend
source venv/bin/activate
python database_setup/fix_performed_at_column.py
```

## Troubleshooting

If you encounter issues:
1. Make sure you're in the `backend/` directory
2. Ensure virtual environment is activated
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. See `REVIEWER_SETUP.md` for detailed troubleshooting steps
5. See `DATABASE_SETUP.md` for complete setup guide
