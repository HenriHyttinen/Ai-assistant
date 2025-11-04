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

