#!/usr/bin/env python3
"""
Fix Nutritional Display

This script ensures that recipe-level nutritional data is properly structured
and easily accessible for the frontend to display correctly.
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

class NutritionalDisplayFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.updated_count = 0

    def extract_recipe_nutrition(self, summary):
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
                'carbs': 0.0,  # We don't have carbs in the original data
                'fats': float(match.group(3)),
                'sodium': float(match.group(4))
            }
        
        return None

    def calculate_carbs_from_ingredients(self, recipe):
        """Calculate carbs from ingredients if not available in recipe data"""
        total_carbs = 0.0
        
        for ingredient in recipe.ingredients:
            # Calculate carbs based on ingredient quantity (assuming per 100g)
            ingredient_carbs = ingredient.ingredient.carbs * (ingredient.quantity / 100)
            total_carbs += ingredient_carbs
        
        return round(total_carbs, 1)

    def fix_recipe_nutrition_display(self, recipe):
        """Fix nutritional display for a single recipe"""
        try:
            # Extract current nutrition data
            nutrition = self.extract_recipe_nutrition(recipe.summary)
            
            if not nutrition:
                logger.warning(f"No nutrition data found for {recipe.title}")
                return False
            
            # Calculate carbs from ingredients
            carbs = self.calculate_carbs_from_ingredients(recipe)
            nutrition['carbs'] = carbs
            
            # Create a clean summary with proper nutrition display
            clean_summary = f"A delicious {recipe.title.lower()} recipe. Nutrition per serving: {nutrition['calories']:.0f} cal, {nutrition['protein']:.0f}g protein, {nutrition['carbs']:.0f}g carbs, {nutrition['fats']:.0f}g fat, {nutrition['sodium']:.0f}mg sodium"
            
            # Add structured data for easy frontend parsing
            structured_data = f"\n\nNUTRITION_DATA:{nutrition['calories']:.0f}|{nutrition['protein']:.0f}|{nutrition['carbs']:.0f}|{nutrition['fats']:.0f}|{nutrition['sodium']:.0f}"
            
            recipe.summary = clean_summary + structured_data
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing nutrition display for {recipe.title}: {e}")
            return False

    def fix_all_recipes(self):
        """Fix nutritional display for all recipes"""
        logger.info("🍎 Starting to fix nutritional display for all recipes...")
        
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to fix")
        
        for i, recipe in enumerate(recipes):
            if self.fix_recipe_nutrition_display(recipe):
                self.updated_count += 1
                
                if (i + 1) % 50 == 0:
                    logger.info(f"Fixed {i + 1} recipes...")
        
        self.db.commit()
        
        logger.info(f"🎉 Fixed nutritional display for {self.updated_count} recipes!")
        return self.updated_count

    def verify_nutritional_display(self):
        """Verify that nutritional display is correct"""
        logger.info("🔍 Verifying nutritional display...")
        
        # Check a few sample recipes
        sample_recipes = ['Lentil, Apple, and Turkey Wrap', 'Fried Chicken with Bacon and Pepper Cream Gravy', 'Boudin Blanc Terrine with Red Onion Confit']
        
        for recipe_name in sample_recipes:
            recipe = self.db.query(Recipe).filter(Recipe.title == recipe_name).first()
            if recipe:
                print(f"\n🍳 {recipe.title}:")
                print(f"  Cuisine: {recipe.cuisine}")
                print(f"  Meal Type: {recipe.meal_type}")
                print(f"  Prep Time: {recipe.prep_time} min")
                print(f"  Difficulty: {recipe.difficulty_level}")
                
                # Extract nutrition data
                nutrition_match = re.search(r'NUTRITION_DATA:([\d.]+)\|([\d.]+)\|([\d.]+)\|([\d.]+)\|([\d.]+)', recipe.summary)
                if nutrition_match:
                    calories, protein, carbs, fats, sodium = nutrition_match.groups()
                    print(f"  Nutrition: {calories} cal, {protein}g protein, {carbs}g carbs, {fats}g fats, {sodium}mg sodium")
                else:
                    print(f"  Summary: {recipe.summary[:100]}...")

    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to fix nutritional display"""
    fixer = NutritionalDisplayFixer()
    
    try:
        updated_count = fixer.fix_all_recipes()
        fixer.verify_nutritional_display()
        
        logger.info(f"🎉 SUCCESS! Fixed nutritional display for {updated_count} recipes!")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()







