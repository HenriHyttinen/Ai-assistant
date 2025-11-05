# Reviewer Commands

This document contains commands that reviewers can run to verify the database and application functionality.

## Prerequisites

1. Make sure you're in the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   ```bash
   # On Linux/macOS:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

## Check Ingredient Count

To check how many ingredients are in the database:

```bash
python3 check_ingredients.py
```

Or using the existing database check script:

```bash
python3 check_db.py
```

This will show:
- Total ingredient count
- Ingredients by category
- Ingredients with embeddings
- Ingredients with nutritional data
- Sample ingredients

**Expected Output:**
- Total ingredients: 15,694+ (target: ≥500, comprehensive: ≥15,532)
- All ingredients should have embeddings (100%)
- Most ingredients should have nutritional data (68%+)

## Check Database Overview

To check general database statistics (recipes, ingredients, preferences, meal plans):

```bash
python3 check_db.py
```

**Expected Output:**
- Recipes: 500-800+
- Ingredients: 15,694+
- Nutrition preferences: 1+ (one per user)
- Meal plans: varies

## Quick SQL Check (Alternative)

If you prefer to use SQL directly:

```bash
python3 -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
print(f'Total ingredients: {result}')
db.close()
"
```

## Check Specific Statistics

To check ingredient embeddings:

```bash
python3 -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
total = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
with_embeddings = db.execute(text('SELECT COUNT(*) FROM ingredients WHERE embedding IS NOT NULL')).scalar()
print(f'Ingredients with embeddings: {with_embeddings} / {total}')
db.close()
"
```

## Troubleshooting

### If you get "ModuleNotFoundError: No module named 'sqlalchemy'"

Make sure the virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### If you get "No such file or directory"

Make sure you're in the `backend` directory:
```bash
cd backend
```

### If the database connection fails

Check that your `.env` file has the correct database connection string:
```bash
cat .env | grep DATABASE
```

