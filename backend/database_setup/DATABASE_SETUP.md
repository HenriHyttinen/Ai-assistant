# Database Setup Guide

This guide explains how to set up the database for the Numbers Don't Lie application.

## Quick Setup

If you're getting errors about missing tables, run this command:

```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
```

This will create all necessary database tables.

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

## Manual Setup (Alternative)

If you prefer to set up the database manually:

1. **Initialize the database:**
   ```bash
   cd backend
   source venv/bin/activate
   python database_setup/init_db.py
   ```

2. **Seed recipes and ingredients (optional):**
   ```bash
   python scripts/comprehensive_seeder.py
   ```

3. **Create achievements (optional):**
   ```bash
   python database_setup/setup_achievements.py
   ```

## Troubleshooting

### Error: "no such table: achievements"

This error occurs when the achievements table hasn't been created. The solution is to run the database setup script:

```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
python database_setup/setup_achievements.py
```

### Error: "ModuleNotFoundError: No module named 'sqlalchemy'"

Make sure you're in the virtual environment:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'models'"

Make sure you're in the `backend/` directory when running scripts:

```bash
cd backend
python database_setup/init_db.py
```

### Error: "When initializing mapper..."

This is a circular import issue. Make sure you're running from the `backend/` directory:

```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
```

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
- `recipes` - Recipe database (500+ recipes)
- `ingredients` - Ingredient database (15,532+ ingredients)
- `meal_plans` - User meal plans
- `meal_plan_meals` - Individual meals in meal plans
- `user_nutrition_preferences` - User dietary preferences and allergies
- `shopping_lists` - Shopping lists generated from meal plans
- `nutritional_logs` - Daily nutritional intake tracking

## Verification

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

You can also check achievements:

```bash
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM achievements')).scalar()
print(f'Achievements in database: {result}')
db.close()
"
```

You should see "Achievements in database: 15" if everything is set up correctly.
