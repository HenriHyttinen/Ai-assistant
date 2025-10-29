#!/usr/bin/env python3
"""
Fix recipe nutrition by using the original nutritional data from SQLite
instead of calculating from ingredients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe
import logging
import sqlite3
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()
        
    def fix_all_recipes(self):
        """Fix all recipes by using original nutrition data"""
        logger.info("🔧 Fixing nutrition data from original SQLite...")
        
        # Get all recipes from SQLite with nutrition data
        self.sqlite_cursor.execute("""
            SELECT id, title, calories, protein, fat, sodium
            FROM recipes
            WHERE calories IS NOT NULL AND calories >= 100
        """)
        sqlite_recipes = self.sqlite_cursor.fetchall()
        
        # Create a map of title to nutrition data
        nutrition_map = {}
        for sqlite_id, title, calories, protein, fat, sodium in sqlite_recipes:
            nutrition_map[title] = {
                'calories': calories,
                'protein': protein,
                'fat': fat,
                'sodium': sodium
            }
        
        # Get our imported recipes
        imported_recipes = self.db.query(Recipe).all()
        fixed_count = 0
        
        for recipe in imported_recipes:
            if recipe.title in nutrition_map:
                try:
                    nutrition = nutrition_map[recipe.title]
                    
                    # Update the summary with correct nutrition data
                    new_summary = f"A delicious recipe. Nutrition per serving: {nutrition['calories']:.0f} cal, {nutrition['protein']:.0f}g protein, {nutrition['fat']:.0f}g fat, {nutrition['sodium']:.0f}mg sodium."
                    recipe.summary = new_summary
                    
                    fixed_count += 1
                    if fixed_count % 50 == 0:
                        logger.info(f"Fixed {fixed_count} recipes...")
                        
                except Exception as e:
                    logger.error(f"Error fixing recipe {recipe.title}: {e}")
                    continue
        
        try:
            self.db.commit()
            logger.info(f"✅ Fixed nutrition for {fixed_count} recipes!")
            
            # Verify fixes
            self.verify_fixes()
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise
    
    def verify_fixes(self):
        """Verify that the fixes worked"""
        logger.info("🔍 Verifying fixes...")
        
        # Check a few recipes
        test_recipes = self.db.query(Recipe).limit(5).all()
        
        for recipe in test_recipes:
            print(f"\nRecipe: {recipe.title}")
            print(f"Servings: {recipe.servings}")
            print(f"Summary: {recipe.summary}")
            
            # Extract nutrition from summary
            import re
            cal_match = re.search(r'(\d+) cal', recipe.summary)
            protein_match = re.search(r'(\d+)g protein', recipe.summary)
            fat_match = re.search(r'(\d+)g fat', recipe.summary)
            
            if cal_match:
                calories = int(cal_match.group(1))
                protein = int(protein_match.group(1)) if protein_match else 0
                fat = int(fat_match.group(1)) if fat_match else 0
                per_serving = calories / recipe.servings if recipe.servings > 0 else calories
                print(f"Per serving: {per_serving:.1f} cal, {protein/recipe.servings:.1f}g protein, {fat/recipe.servings:.1f}g fat")

def main():
    fixer = NutritionFixer()
    fixer.fix_all_recipes()

if __name__ == "__main__":
    main()


