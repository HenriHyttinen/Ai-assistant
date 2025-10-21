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

To set up the database from scratch:
```bash
cd database_setup
./setup.sh
```

Or run individual scripts as needed for specific setup tasks.
