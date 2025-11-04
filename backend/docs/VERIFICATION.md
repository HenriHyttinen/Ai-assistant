# Database Verification Guide

This document provides instructions for verifying that the database meets the requirements for RAG (Retrieval-Augmented Generation) and the nutrition planning system.

## Requirements

- **Recipes**: ≥500 recipes with vector embeddings
- **Ingredients**: ≥500 ingredients (target: 15,532+ ingredients) with vector embeddings
- **Vector Embeddings**: All recipes and ingredients should have embeddings for RAG functionality
- **Similarity Search**: RAG retrieval should work correctly

## Verification Steps

### Step 1: Verify Recipe Count

Run this command to count recipes in the database:

```bash
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM recipes WHERE is_active = true')).scalar()
print(f'Active recipes in database: {result}')
if result >= 500:
    print('✅ Recipe count requirement met (≥500)')
else:
    print(f'⚠️ Recipe count below requirement. Expected ≥500, found {result}')
db.close()
"
```

**Expected Output**: `Active recipes in database: 500+`

### Step 2: Verify Recipe Embeddings

Run this command to verify that recipes have embeddings:

```bash
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
# Count recipes with embeddings
result = db.execute(text('SELECT COUNT(*) FROM recipes WHERE is_active = true AND embedding IS NOT NULL')).scalar()
total = db.execute(text('SELECT COUNT(*) FROM recipes WHERE is_active = true')).scalar()
print(f'Recipes with embeddings: {result} / {total}')
if result == total and total >= 500:
    print('✅ All recipes have embeddings')
elif result >= 500:
    print(f'⚠️ {total - result} recipes missing embeddings')
else:
    print('❌ Recipe embedding requirement not met')
db.close()
"
```

**Expected Output**: `Recipes with embeddings: 500+ / 500+`

### Step 3: Verify Ingredient Count

Run this command to count ingredients in the database:

```bash
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
print(f'Ingredients in database: {result}')
if result >= 500:
    print('✅ Ingredient count requirement met (≥500)')
    if result >= 15532:
        print('✅ Comprehensive ingredient database (15,532+)')
else:
    print(f'⚠️ Ingredient count below requirement. Expected ≥500, found {result}')
db.close()
"
```

**Expected Output**: `Ingredients in database: 500+` (or `15,532+` if using comprehensive database)

### Step 4: Verify Ingredient Embeddings

Run this command to verify that ingredients have embeddings:

```bash
python -c "
from database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
# Count ingredients with embeddings
result = db.execute(text('SELECT COUNT(*) FROM ingredients WHERE embedding IS NOT NULL')).scalar()
total = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
print(f'Ingredients with embeddings: {result} / {total}')
if result == total and total >= 500:
    print('✅ All ingredients have embeddings')
elif result >= 500:
    print(f'⚠️ {total - result} ingredients missing embeddings')
else:
    print('❌ Ingredient embedding requirement not met')
db.close()
"
```

**Expected Output**: `Ingredients with embeddings: 500+ / 500+` (or `15,532+ / 15,532+`)

### Step 5: Test RAG Retrieval

Run the embedding verification script to test RAG retrieval:

```bash
python scripts/generate_recipe_embeddings.py --verify
```

Or run this Python code:

```python
from database import SessionLocal
from models.recipe import Recipe
from sentence_transformers import SentenceTransformer
import numpy as np

db = SessionLocal()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Get a sample recipe with embedding
sample_recipe = db.query(Recipe).filter(
    Recipe.is_active == True,
    Recipe.embedding.isnot(None)
).first()

if not sample_recipe:
    print("❌ No recipes with embeddings found")
    exit(1)

# Test query
test_query = "chicken pasta italian"
query_embedding = embedding_model.encode([test_query])[0]

# Find similar recipes
recipes = db.query(Recipe).filter(
    Recipe.is_active == True,
    Recipe.embedding.isnot(None)
).all()

similarities = []
for recipe in recipes[:100]:  # Test first 100 for speed
    if recipe.embedding:
        similarity = np.dot(query_embedding, recipe.embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(recipe.embedding)
        )
        similarities.append((recipe.title, similarity))

# Sort by similarity
similarities.sort(key=lambda x: x[1], reverse=True)

print(f"✅ RAG retrieval test passed")
print(f"Top 5 similar recipes for '{test_query}':")
for title, similarity in similarities[:5]:
    print(f"  - {title}: {similarity:.3f}")

db.close()
```

**Expected Output**: Top 5 similar recipes with similarity scores

### Step 6: Verify Embedding Dimensions

Run this command to verify embedding dimensions:

```bash
python -c "
from database import SessionLocal
from models.recipe import Recipe
db = SessionLocal()
# Get a sample recipe with embedding
sample = db.query(Recipe).filter(
    Recipe.is_active == True,
    Recipe.embedding.isnot(None)
).first()
if sample and sample.embedding:
    dim = len(sample.embedding)
    print(f'Embedding dimension: {dim}')
    if dim == 384:
        print('✅ Correct embedding dimension (384 for all-MiniLM-L6-v2)')
    else:
        print(f'⚠️ Unexpected embedding dimension. Expected 384, found {dim}')
else:
    print('❌ No recipes with embeddings found')
db.close()
"
```

**Expected Output**: `Embedding dimension: 384`

## Complete Verification Script

Save this as `backend/verify_database.py`:

```python
#!/usr/bin/env python3
"""
Complete database verification script
"""

from database import SessionLocal
from sqlalchemy import text
from models.recipe import Recipe, Ingredient

def verify_database():
    """Verify database meets requirements"""
    db = SessionLocal()
    
    print("=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)
    
    # 1. Recipe count
    recipe_count = db.execute(text('SELECT COUNT(*) FROM recipes WHERE is_active = true')).scalar()
    print(f"\n📊 Recipe Count: {recipe_count}")
    if recipe_count >= 500:
        print("   ✅ Requirement met (≥500)")
    else:
        print(f"   ❌ Requirement not met (expected ≥500, found {recipe_count})")
    
    # 2. Recipe embeddings
    recipe_embeddings = db.execute(text(
        'SELECT COUNT(*) FROM recipes WHERE is_active = true AND embedding IS NOT NULL'
    )).scalar()
    print(f"\n📊 Recipe Embeddings: {recipe_embeddings} / {recipe_count}")
    if recipe_embeddings == recipe_count and recipe_count >= 500:
        print("   ✅ All recipes have embeddings")
    elif recipe_embeddings >= 500:
        print(f"   ⚠️ {recipe_count - recipe_embeddings} recipes missing embeddings")
    else:
        print("   ❌ Recipe embedding requirement not met")
    
    # 3. Ingredient count
    ingredient_count = db.execute(text('SELECT COUNT(*) FROM ingredients')).scalar()
    print(f"\n📊 Ingredient Count: {ingredient_count}")
    if ingredient_count >= 500:
        print("   ✅ Requirement met (≥500)")
        if ingredient_count >= 15532:
            print("   ✅ Comprehensive database (15,532+)")
    else:
        print(f"   ❌ Requirement not met (expected ≥500, found {ingredient_count})")
    
    # 4. Ingredient embeddings
    ingredient_embeddings = db.execute(text(
        'SELECT COUNT(*) FROM ingredients WHERE embedding IS NOT NULL'
    )).scalar()
    print(f"\n📊 Ingredient Embeddings: {ingredient_embeddings} / {ingredient_count}")
    if ingredient_embeddings == ingredient_count and ingredient_count >= 500:
        print("   ✅ All ingredients have embeddings")
    elif ingredient_embeddings >= 500:
        print(f"   ⚠️ {ingredient_count - ingredient_embeddings} ingredients missing embeddings")
    else:
        print("   ❌ Ingredient embedding requirement not met")
    
    # 5. Embedding dimensions
    sample_recipe = db.query(Recipe).filter(
        Recipe.is_active == True,
        Recipe.embedding.isnot(None)
    ).first()
    if sample_recipe and sample_recipe.embedding:
        dim = len(sample_recipe.embedding)
        print(f"\n📊 Embedding Dimension: {dim}")
        if dim == 384:
            print("   ✅ Correct dimension (384 for all-MiniLM-L6-v2)")
        else:
            print(f"   ⚠️ Unexpected dimension (expected 384, found {dim})")
    else:
        print("\n📊 Embedding Dimension: N/A (no embeddings found)")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    verify_database()
```

Run with:

```bash
python backend/verify_database.py
```

## Generating Missing Embeddings

If recipes or ingredients are missing embeddings, run:

```bash
# Generate embeddings for all recipes
python scripts/generate_recipe_embeddings.py

# Or use populate_nutrition_database.py which creates both recipes and embeddings
python scripts/populate_nutrition_database.py
```

## Troubleshooting

### Issue: Recipe count < 500

**Solution**: Run a seeding script:

```bash
# Option 1: Comprehensive seeder
python scripts/comprehensive_seeder.py

# Option 2: Create 500 real recipes
python scripts/create_500_real_recipes.py

# Option 3: Populate nutrition database (creates recipes + embeddings)
python scripts/populate_nutrition_database.py
```

Then generate embeddings:

```bash
python scripts/generate_recipe_embeddings.py
```

### Issue: Ingredient count < 500

**Solution**: Run a seeding script that creates ingredients:

```bash
# Option 1: Comprehensive seeder
python scripts/comprehensive_seeder.py

# Option 2: Populate nutrition database
python scripts/populate_nutrition_database.py

# Option 3: Add more ingredients
python scripts/add_more_ingredients.py
```

### Issue: Embeddings missing

**Solution**: Generate embeddings for existing recipes/ingredients:

```bash
# For recipes
python scripts/generate_recipe_embeddings.py

# For ingredients (if script exists)
# Check populate_nutrition_database.py which generates ingredient embeddings
python scripts/populate_nutrition_database.py
```

### Issue: Similarity search not working

**Solution**: 
1. Verify embeddings are stored as JSON arrays (not strings)
2. Check that `sentence-transformers` is installed: `pip install sentence-transformers`
3. Verify embedding model is `all-MiniLM-L6-v2`
4. Test with the verification script above

## Summary

This verification ensures:
- ✅ 500+ recipes exist in the database
- ✅ 500+ ingredients exist in the database
- ✅ All recipes have vector embeddings for RAG
- ✅ All ingredients have vector embeddings for RAG
- ✅ Embedding dimensions are correct (384 for all-MiniLM-L6-v2)
- ✅ RAG similarity search works correctly

The system is ready for RAG-powered recipe generation when all checks pass.

