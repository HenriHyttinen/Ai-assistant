#!/usr/bin/env python3
"""
Restore Recipe Nutrition from SQLite Database

This script restores the nutrition values for recipes that were originally
imported from SQLite database with nutrition data, but lost those values.

It matches recipes by title and restores per_serving and total nutrition values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from database import SessionLocal
from models.recipe import Recipe
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionRestorer:
    def __init__(self):
        self.db = SessionLocal()
        # Try both possible locations
        sqlite_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'recipes.sqlite3'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recipes.sqlite3'),
            '../recipes.sqlite3',
            '../../recipes.sqlite3',
            'recipes.sqlite3'
        ]
        
        self.sqlite_conn = None
        self.sqlite_cursor = None
        
        for path in sqlite_paths:
            if os.path.exists(path):
                try:
                    self.sqlite_conn = sqlite3.connect(path)
                    self.sqlite_cursor = self.sqlite_conn.cursor()
                    logger.info(f"✅ Connected to SQLite database: {path}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️  Could not connect to {path}: {e}")
                    continue
        
        if not self.sqlite_conn:
            raise FileNotFoundError("Could not find recipes.sqlite3 database")
        
        self.restored_count = 0
        
    def normalize_title(self, title):
        """Normalize title for matching"""
        if not title:
            return ""
        # Remove extra whitespace, convert to lowercase
        title = re.sub(r'\s+', ' ', title.strip().lower())
        # Remove special characters for matching
        title = re.sub(r'[^\w\s]', '', title)
        return title
    
    def restore_nutrition(self):
        """Restore nutrition values from SQLite database"""
        logger.info("🔍 Loading recipes from SQLite with nutrition data...")
        
        # Get all recipes from SQLite with nutrition data
        self.sqlite_cursor.execute("""
            SELECT id, title, calories, protein, fat, sodium
            FROM recipes
            WHERE calories IS NOT NULL 
            AND calories >= 100 
            AND calories <= 800
            AND protein IS NOT NULL 
            AND protein > 0
            AND fat IS NOT NULL
        """)
        
        sqlite_recipes = self.sqlite_cursor.fetchall()
        logger.info(f"Found {len(sqlite_recipes)} recipes in SQLite with nutrition data")
        
        # Create a map of normalized title to nutrition data
        nutrition_map = {}
        for sqlite_id, title, calories, protein, fat, sodium in sqlite_recipes:
            normalized_title = self.normalize_title(title)
            if normalized_title:
                # Store multiple matches if titles are very similar
                if normalized_title not in nutrition_map:
                    nutrition_map[normalized_title] = []
                nutrition_map[normalized_title].append({
                    'calories': float(calories) if calories else 0,
                    'protein': float(protein) if protein else 0,
                    'fat': float(fat) if fat else 0,
                    'sodium': float(sodium) if sodium else 0,
                    'sqlite_id': sqlite_id,
                    'original_title': title
                })
        
        # Get our imported recipes
        imported_recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(imported_recipes)} recipes in our database")
        
        matched = 0
        restored = 0
        
        for recipe in imported_recipes:
            normalized_title = self.normalize_title(recipe.title)
            
            if normalized_title in nutrition_map:
                # Try to find the best match
                candidates = nutrition_map[normalized_title]
                best_match = candidates[0]  # Use first match for now
                
                calories = best_match['calories']
                protein = best_match['protein']
                fat = best_match['fat']
                sodium = best_match.get('sodium', 0)
                
                # Get servings (should already be set)
                servings = recipe.servings or 4
                if servings <= 0:
                    servings = 4
                    recipe.servings = 4
                
                # Calculate carbs from calories (if not provided)
                # calories = protein*4 + carbs*4 + fat*9
                carbs = max(0, (calories - protein*4 - fat*9) / 4)
                
                # Calculate totals
                total_calories = calories * servings
                total_protein = protein * servings
                total_fat = fat * servings
                total_carbs = carbs * servings
                total_sodium = sodium * servings if sodium else 0
                
                # Update recipe nutrition
                recipe.per_serving_calories = round(calories, 1)
                recipe.per_serving_protein = round(protein, 1)
                recipe.per_serving_carbs = round(carbs, 1)
                recipe.per_serving_fat = round(fat, 1)
                recipe.per_serving_sodium = round(sodium, 1) if sodium else 0
                
                recipe.total_calories = round(total_calories, 1)
                recipe.total_protein = round(total_protein, 1)
                recipe.total_carbs = round(total_carbs, 1)
                recipe.total_fat = round(total_fat, 1)
                recipe.total_sodium = round(total_sodium, 1) if sodium else 0
                
                matched += 1
                
                # Only count as restored if values actually changed
                if (recipe.per_serving_calories or 0) > 0:
                    restored += 1
                
                if restored % 50 == 0:
                    logger.info(f"Restored {restored} recipes...")
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"🎉 Restored nutrition for {restored} recipes (matched {matched} recipes)")
        return restored
    
    def verify_restoration(self):
        """Verify the restoration was successful"""
        logger.info("🔍 Verifying restoration...")
        
        recipes_with_nutrition = self.db.query(Recipe).filter(
            Recipe.per_serving_calories.isnot(None),
            Recipe.per_serving_calories > 0
        ).count()
        
        total = self.db.query(Recipe).count()
        
        logger.info(f"Recipes with nutrition (>0): {recipes_with_nutrition}/{total}")
        
        # Sample a few recipes
        sample = self.db.query(Recipe).filter(
            Recipe.per_serving_calories > 0
        ).limit(3).all()
        
        for recipe in sample:
            logger.info(f"✅ {recipe.title[:50]}: {recipe.per_serving_calories:.0f} cal/serving, {recipe.total_calories:.0f} cal total ({recipe.servings} servings)")
    
    def close(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        self.db.close()

def main():
    """Main function"""
    restorer = NutritionRestorer()
    
    try:
        restored = restorer.restore_nutrition()
        restorer.verify_restoration()
        
        logger.info(f"🎉 SUCCESS! Restored nutrition for {restored} recipes")
        
    except Exception as e:
        logger.error(f"❌ Restoration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        restorer.close()

if __name__ == "__main__":
    main()

