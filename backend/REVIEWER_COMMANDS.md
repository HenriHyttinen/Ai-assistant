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

## Seed More Ingredients (If Below Minimum)

If you have less than 500 ingredients (minimum requirement), you can seed the database:

### Option 1: Run Comprehensive Seeder (Creates 155 ingredients)

**Note:** This seeder only creates 155 ingredients, which is below the minimum requirement of 500. It will replace existing ingredients.

```bash
python3 scripts/comprehensive_seeder.py
```

**What it does:**
- Creates 155 ingredients with nutritional data
- Creates 500+ recipes
- ⚠️ **WARNING:** This will DELETE all existing ingredients and recipes!

### Option 2: Import Ingredients from JSON File (Recommended)

If you have the `ingredients_list.json` file in the backend directory, you can import more ingredients:

```bash
# Auto-detect and import all ingredients from JSON (can take a few minutes)
python3 scripts/import_ingredients_from_json.py

# Or import a specific number (e.g., 500 to meet minimum requirement)
python3 scripts/import_ingredients_from_json.py --max 500

# Or specify the file path explicitly
python3 scripts/import_ingredients_from_json.py --file ../backend/ingredients_list.json
```

**What it does:**
- Auto-detects `ingredients_list.json` file location (searches in backend directory)
- Reads ingredients from JSON file
- Adds new ingredients without deleting existing ones
- Skips duplicates (by name)
- Preserves existing ingredient IDs

**Note:** 
- The `ingredients_list.json` file should be in the `backend/` directory
- If the file doesn't exist in your repository, it may not have been committed (check `.gitignore`)
- If the file is missing, use Option 1 (comprehensive seeder) instead, which creates 155 ingredients from code
- The script will automatically search for the file in common locations
- **Important:** The JSON file contains 5,388 entries but only ~3,062 unique ingredient names. The script correctly skips duplicates, so you'll get fewer ingredients than the total JSON entries. This is normal and expected behavior.

**Why you might get ~3,161 ingredients:**
- If you run the seeder first: 155 ingredients
- Then import from JSON: ~3,062 unique ingredients
- Some overlap between seeder and JSON (e.g., "butter", "eggs") gets skipped
- Result: ~155 + ~3,006 = ~3,161 ingredients (which exceeds the 500 minimum requirement!)

**About nutritional data:**
- The JSON file contains many entries that are cooking instructions (e.g., "tops and roots trimmed", "plus more to taste") rather than actual food ingredients
- Out of ~3,062 unique ingredient names in JSON, only ~1,322 have nutritional data (~43%)
- If you have 3,161 ingredients, expect ~1,452 with nutritional data (46%)
- This is normal - many entries are recipe parsing artifacts, not actual ingredients
- Your production database (15,694 ingredients) has 68.3% with nutrition because it was cleaned/filtered

### Current Status

- **Minimum requirement:** 500+ ingredients
- **Comprehensive database:** 15,532+ ingredients (production has 15,694)
- **Current seeder:** Only creates 155 ingredients

If you only have 155 ingredients, you're missing the full ingredient database. The production database has 15,694 ingredients imported from a comprehensive source.

### Recommendation

For testing purposes, 155 ingredients from the seeder should be sufficient for basic functionality testing. However, for full RAG functionality with comprehensive ingredient search, you would need the full 15,532+ ingredient database.

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

### If you get "minimum requirement not met"

The seeder script (`comprehensive_seeder.py`) only creates 155 ingredients, which is below the minimum of 500. This is expected - the script is designed for basic testing, not full production data. The production database has 15,694 ingredients from a comprehensive source that is not included in the repository.

### If you get "❌ Embedding requirement not met"

This means fewer than 500 ingredients have vector embeddings. Embeddings are required for RAG (Retrieval-Augmented Generation) functionality, which enables semantic search for similar ingredients.

**To fix this, generate embeddings:**

```bash
cd backend
source .venv/bin/activate  # On macOS/Linux
python3 scripts/generate_ingredient_embeddings.py
```

**Note:** If you get "ModuleNotFoundError: No module named 'database'", make sure you're running from the `backend/` directory and the virtual environment is activated.

**What embeddings do:**
- Vector representations of ingredients for semantic search
- Required for RAG functionality (finding similar ingredients)
- Stored in `Ingredient.embedding` column (384-dimensional vectors)

**Note:** Generating embeddings requires the `sentence-transformers` library. If you get import errors, install dependencies:
```bash
pip install -r requirements.txt
```

**Time:** Generating embeddings for 3,161 ingredients takes ~5-10 minutes.

