#!/usr/bin/env python3
"""
Check ingredient database statistics
Simple script for reviewers to verify ingredient count and status
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from sqlalchemy import text, func
from models.recipe import Ingredient

def check_ingredients():
    """Check ingredient database statistics"""
    db = SessionLocal()
    try:
        # Count all ingredients
        ingredient_count = db.query(Ingredient).count()
        print("=" * 60)
        print("INGREDIENT DATABASE STATISTICS")
        print("=" * 60)
        print(f'\n📊 Total ingredients in database: {ingredient_count:,}')
        
        # Count by category
        category_counts = db.query(
            Ingredient.category,
            func.count(Ingredient.id).label('count')
        ).group_by(Ingredient.category).order_by(func.count(Ingredient.id).desc()).all()
        
        print(f'\n📊 Ingredients by category:')
        for category, count in category_counts:
            percentage = (count / ingredient_count) * 100 if ingredient_count > 0 else 0
            print(f'  - {category}: {count:,} ({percentage:.1f}%)')
        
        # Count ingredients with embeddings
        ingredients_with_embeddings = db.query(Ingredient).filter(
            Ingredient.embedding.isnot(None)
        ).count()
        embedding_percentage = (ingredients_with_embeddings / ingredient_count * 100) if ingredient_count > 0 else 0
        print(f'\n📊 Ingredients with embeddings: {ingredients_with_embeddings:,} / {ingredient_count:,} ({embedding_percentage:.1f}%)')
        
        # Count ingredients with nutritional data
        ingredients_with_nutrition = db.query(Ingredient).filter(
            (Ingredient.calories > 0) | (Ingredient.protein > 0) | (Ingredient.carbs > 0) | (Ingredient.fats > 0)
        ).count()
        nutrition_percentage = (ingredients_with_nutrition / ingredient_count * 100) if ingredient_count > 0 else 0
        print(f'📊 Ingredients with nutritional data: {ingredients_with_nutrition:,} / {ingredient_count:,} ({nutrition_percentage:.1f}%)')
        
        # Show sample ingredients
        sample_ingredients = db.query(Ingredient).limit(10).all()
        print(f'\n🥕 Sample ingredients (first 10):')
        for ing in sample_ingredients:
            print(f'  - {ing.name} ({ing.category})')
        
        # Requirements check
        print(f'\n✅ Requirements Check:')
        if ingredient_count >= 500:
            print(f'   ✅ Minimum requirement met (≥500 ingredients)')
        else:
            print(f'   ❌ Minimum requirement not met (expected ≥500, found {ingredient_count})')
        
        if ingredient_count >= 15532:
            print(f'   ✅ Comprehensive database (15,532+ ingredients)')
        elif ingredient_count >= 500:
            print(f'   ⚠️  Basic database (target: 15,532+ ingredients)')
        
        if ingredients_with_embeddings == ingredient_count and ingredient_count >= 500:
            print(f'   ✅ All ingredients have embeddings')
        elif ingredients_with_embeddings >= 500:
            print(f'   ⚠️  {ingredient_count - ingredients_with_embeddings} ingredients missing embeddings')
        else:
            print(f'   ❌ Embedding requirement not met')
            
    except Exception as e:
        print(f'❌ Error checking ingredients: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_ingredients()

