#!/usr/bin/env python3
"""
Fix recipe ingredient quantities by converting units to grams
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeQuantityFixer:
    def __init__(self):
        self.db = SessionLocal()
        
    def convert_to_grams(self, quantity, unit):
        """Convert various units to grams"""
        unit = unit.lower().strip()
        
        # Volume conversions (approximate)
        if unit == 'cup':
            return quantity * 240  # 1 cup = 240ml, assume 1ml = 1g for most ingredients
        elif unit == 'tbsp' or unit == 'tablespoon':
            return quantity * 15   # 1 tbsp = 15ml
        elif unit == 'tsp' or unit == 'teaspoon':
            return quantity * 5    # 1 tsp = 5ml
        elif unit == 'ml':
            return quantity        # 1ml = 1g (approximate)
        elif unit == 'l' or unit == 'liter':
            return quantity * 1000
        
        # Weight conversions
        elif unit == 'lb' or unit == 'pound':
            return quantity * 453.592  # 1 lb = 453.592g
        elif unit == 'oz' or unit == 'ounce':
            return quantity * 28.3495  # 1 oz = 28.3495g
        elif unit == 'kg' or unit == 'kilogram':
            return quantity * 1000
        elif unit == 'g' or unit == 'gram':
            return quantity
        
        # Count-based conversions (approximate)
        elif unit == 'clove':
            return quantity * 3    # 1 garlic clove ≈ 3g
        elif unit == 'slice':
            return quantity * 25   # 1 slice bread ≈ 25g
        elif unit == 'piece':
            return quantity * 50   # 1 piece ≈ 50g (very approximate)
        elif unit == 'large' or unit == 'medium' or unit == 'small':
            return quantity * 100  # Approximate for fruits/vegetables
        else:
            # Default: assume it's already in grams
            return quantity
    
    def fix_all_recipes(self):
        """Fix quantities for all recipes"""
        logger.info("🔧 Fixing ingredient quantities...")
        
        recipes = self.db.query(Recipe).all()
        fixed_count = 0
        
        for recipe in recipes:
            try:
                recipe_fixed = False
                for ri in recipe.ingredients:
                    old_quantity = ri.quantity
                    new_quantity = self.convert_to_grams(ri.quantity, ri.unit)
                    
                    if abs(new_quantity - old_quantity) > 0.1:  # Only update if significantly different
                        ri.quantity = new_quantity
                        ri.unit = 'g'  # Convert all to grams
                        recipe_fixed = True
                
                if recipe_fixed:
                    fixed_count += 1
                    if fixed_count % 50 == 0:
                        logger.info(f"Fixed {fixed_count} recipes...")
                        
            except Exception as e:
                logger.error(f"Error fixing recipe {recipe.title}: {e}")
                continue
        
        self.db.commit()
        logger.info(f"✅ Fixed quantities for {fixed_count} recipes!")
        
        # Verify some fixes
        self.verify_fixes()
    
    def verify_fixes(self):
        """Verify that the fixes worked"""
        logger.info("🔍 Verifying fixes...")
        
        # Check a few recipes
        test_recipes = self.db.query(Recipe).limit(3).all()
        
        for recipe in test_recipes:
            print(f"\nRecipe: {recipe.title}")
            print(f"Servings: {recipe.servings}")
            
            total_calories = 0
            for ri in recipe.ingredients[:3]:  # First 3 ingredients
                ingredient = ri.ingredient
                calories = (ingredient.calories * ri.quantity) / 100 if ingredient.calories else 0
                total_calories += calories
                print(f"  {ingredient.name}: {ri.quantity:.1f}g -> {calories:.1f} cal")
            
            per_serving = total_calories / recipe.servings if recipe.servings > 0 else total_calories
            print(f"  Total (first 3 ingredients): {total_calories:.1f} cal")
            print(f"  Per serving: {per_serving:.1f} cal")

def main():
    fixer = RecipeQuantityFixer()
    fixer.fix_all_recipes()

if __name__ == "__main__":
    main()


