#!/usr/bin/env python3
"""
Fix Nutrition Display

This script ensures that recipe-level nutritional data is properly stored
and can be displayed correctly in the frontend.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from database import SessionLocal
from models.recipe import Recipe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionDisplayFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.updated_count = 0

    def extract_nutrition_from_summary(self, summary):
        """Extract nutritional data from recipe summary"""
        if not summary or "Nutrition per serving:" not in summary:
            return None
        
        # Pattern to match: "Nutrition per serving: 426.0 cal, 30.0g protein, 7.0g fat, 559.0mg sodium"
        pattern = r'Nutrition per serving: ([\d.]+) cal, ([\d.]+)g protein, ([\d.]+)g fat, ([\d.]+)mg sodium'
        match = re.search(pattern, summary)
        
        if match:
            return {
                'calories': float(match.group(1)),
                'protein': float(match.group(2)),
                'carbs': 0.0,  # We don't have carbs in summary
                'fats': float(match.group(3)),
                'sodium': float(match.group(4))
            }
        
        return None

    def add_nutrition_fields_to_recipe(self, recipe):
        """Add nutrition fields directly to recipe model"""
        nutrition = self.extract_nutrition_from_summary(recipe.summary)
        
        if nutrition:
            # Add nutrition fields to recipe (if they don't exist in the model, we'll add them)
            # For now, let's store them in the summary in a structured way
            structured_summary = f"{recipe.summary}\n\nNUTRITION_DATA:{nutrition['calories']}|{nutrition['protein']}|{nutrition['carbs']}|{nutrition['fats']}|{nutrition['sodium']}"
            recipe.summary = structured_summary
            return True
        
        return False

    def fix_all_recipes(self):
        """Fix nutrition display for all recipes"""
        logger.info("🍎 Starting to fix nutrition display...")
        
        recipes_with_nutrition = self.db.query(Recipe).filter(Recipe.summary.like('%Nutrition per serving:%')).all()
        
        logger.info(f"Found {len(recipes_with_nutrition)} recipes with nutritional data")
        
        for recipe in recipes_with_nutrition:
            if self.add_nutrition_fields_to_recipe(recipe):
                self.updated_count += 1
                logger.info(f"✅ Updated: {recipe.title}")
        
        self.db.commit()
        
        logger.info(f"🎉 Updated {self.updated_count} recipes with structured nutrition data")
        return self.updated_count

    def verify_nutrition_data(self):
        """Verify that nutrition data is properly structured"""
        logger.info("🔍 Verifying nutrition data structure...")
        
        sample_recipes = self.db.query(Recipe).filter(Recipe.summary.like('%NUTRITION_DATA:%')).limit(3).all()
        
        for recipe in sample_recipes:
            print(f"\n🍳 {recipe.title}:")
            
            # Extract nutrition data from structured summary
            nutrition_match = re.search(r'NUTRITION_DATA:([\d.]+)\|([\d.]+)\|([\d.]+)\|([\d.]+)\|([\d.]+)', recipe.summary)
            if nutrition_match:
                calories, protein, carbs, fats, sodium = nutrition_match.groups()
                print(f"  Calories: {calories}")
                print(f"  Protein: {protein}g")
                print(f"  Carbs: {carbs}g")
                print(f"  Fats: {fats}g")
                print(f"  Sodium: {sodium}mg")

    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to fix nutrition display"""
    fixer = NutritionDisplayFixer()
    
    try:
        updated_count = fixer.fix_all_recipes()
        fixer.verify_nutrition_data()
        
        logger.info(f"🎉 SUCCESS! Updated {updated_count} recipes with structured nutrition data!")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()







