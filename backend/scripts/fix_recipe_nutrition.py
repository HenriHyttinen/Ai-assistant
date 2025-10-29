#!/usr/bin/env python3
"""
Fix Recipe Nutrition Data

This script updates the imported recipes with the real nutritional data
from the original SQLite database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from database import SessionLocal
from models.recipe import Recipe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.updated_count = 0

    def fix_recipe_nutrition(self):
        """Update recipes with real nutritional data from SQLite"""
        logger.info("🍎 Starting to fix recipe nutrition data...")
        
        # Get all recipes from our database
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to update")
        
        for i, recipe in enumerate(recipes, 1):
            try:
                # Get original recipe ID from our recipe ID (format: recipe_XXXXXX)
                original_id = recipe.id.replace('recipe_', '')
                
                # Get nutritional data from SQLite
                self.sqlite_cursor.execute(
                    "SELECT calories, protein, fat, sodium FROM recipes WHERE id = ?", 
                    (original_id,)
                )
                result = self.sqlite_cursor.fetchone()
                
                if result and result[0] is not None:  # If we have nutritional data
                    calories, protein, fat, sodium = result
                    
                    # Update the recipe with real nutritional data
                    # We'll store this in the recipe's summary or create a nutrition field
                    # For now, let's update the summary to include nutrition info
                    nutrition_info = f"Nutrition per serving: {calories} cal, {protein}g protein, {fat}g fat, {sodium}mg sodium"
                    
                    if recipe.summary:
                        recipe.summary = f"{recipe.summary} {nutrition_info}"
                    else:
                        recipe.summary = nutrition_info
                    
                    self.db.commit()
                    self.updated_count += 1
                    
                    if i % 50 == 0:
                        logger.info(f"Updated {i}/{len(recipes)} recipes")
                    
                    logger.info(f"✅ Updated {recipe.title}: {calories} cal, {protein}g protein")
                else:
                    logger.warning(f"⚠️  No nutritional data for {recipe.title}")
                    
            except Exception as e:
                logger.error(f"❌ Error updating {recipe.title}: {e}")
                self.db.rollback()
        
        logger.info(f"🎉 Completed! Updated {self.updated_count} recipes with real nutritional data")
        return self.updated_count

    def close(self):
        """Close database connections"""
        self.db.close()
        self.sqlite_conn.close()

def main():
    """Main function to fix recipe nutrition"""
    fixer = NutritionFixer()
    
    try:
        updated_count = fixer.fix_recipe_nutrition()
        logger.info(f"✅ Successfully updated {updated_count} recipes with real nutritional data!")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()


