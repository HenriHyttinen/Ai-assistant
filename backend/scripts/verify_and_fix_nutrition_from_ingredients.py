#!/usr/bin/env python3
"""
Verify and Fix Nutrition Values from Ingredients

This script:
1. Recalculates nutrition values from recipe ingredients
2. Compares with SQLite values
3. Updates recipes where SQLite values are clearly incorrect
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionVerifier:
    def __init__(self):
        self.db = SessionLocal()
        self.checked_count = 0
        self.fixed_count = 0
        self.skipped_count = 0
        self.discrepancy_threshold = 0.3  # 30% difference is significant
        
    def calculate_nutrition_from_ingredients(self, recipe):
        """Calculate nutrition from recipe ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        total_fiber = 0
        total_sodium = 0
        ingredient_count = 0
        
        for recipe_ingredient in recipe.ingredients:
            ingredient = recipe_ingredient.ingredient
            if not ingredient:
                continue
            
            # Get quantity in grams
            quantity_g = recipe_ingredient.quantity or 0
            if quantity_g <= 0:
                continue
            
            # Get nutrition per 100g from ingredient
            cal_per_100g = ingredient.calories or 0
            prot_per_100g = ingredient.protein or 0
            carbs_per_100g = ingredient.carbs or 0
            fats_per_100g = ingredient.fats or 0
            fiber_per_100g = ingredient.fiber or 0
            sodium_per_100g = ingredient.sodium or 0
            
            # Skip if ingredient has no nutrition data at all
            if cal_per_100g == 0 and prot_per_100g == 0 and carbs_per_100g == 0 and fats_per_100g == 0:
                continue
            
            # Calculate nutrition for this ingredient
            multiplier = quantity_g / 100.0
            
            total_calories += cal_per_100g * multiplier
            total_protein += prot_per_100g * multiplier
            total_carbs += carbs_per_100g * multiplier
            total_fats += fats_per_100g * multiplier
            total_fiber += fiber_per_100g * multiplier
            total_sodium += sodium_per_100g * multiplier
            
            ingredient_count += 1
        
        if ingredient_count == 0:
            return None
        
        return {
            'total_calories': round(total_calories, 1),
            'total_protein': round(total_protein, 1),
            'total_carbs': round(total_carbs, 1),
            'total_fats': round(total_fats, 1),
            'total_fiber': round(total_fiber, 1),
            'total_sodium': round(total_sodium, 1),
            'ingredient_count': ingredient_count
        }
    
    def verify_and_fix_recipe(self, recipe):
        """Verify recipe nutrition and fix if needed"""
        # Calculate from ingredients
        calculated = self.calculate_nutrition_from_ingredients(recipe)
        
        if not calculated:
            self.skipped_count += 1
            logger.debug(f"⚠️  Skipped {recipe.title[:50]}: No valid ingredients")
            return False
        
        # Get servings
        servings = recipe.servings or 1
        if servings <= 0:
            servings = 1
            recipe.servings = 1
        
        # Calculate per-serving values from ingredients
        per_serving_calories = round(calculated['total_calories'] / servings, 1)
        per_serving_protein = round(calculated['total_protein'] / servings, 1)
        per_serving_carbs = round(calculated['total_carbs'] / servings, 1)
        per_serving_fats = round(calculated['total_fats'] / servings, 1)
        per_serving_fiber = round(calculated['total_fiber'] / servings, 1)
        per_serving_sodium = round(calculated['total_sodium'] / servings, 1)
        
        # Get SQLite values
        sqlite_total_cal = recipe.total_calories or 0
        sqlite_per_serving_cal = recipe.per_serving_calories or 0
        
        # Check for significant discrepancy
        if sqlite_total_cal > 0:
            # Calculate difference percentage
            diff_percent = abs(calculated['total_calories'] - sqlite_total_cal) / max(sqlite_total_cal, 1) * 100
            
            # If SQLite value is significantly different (30%+), update with calculated value
            if diff_percent >= self.discrepancy_threshold * 100:
                logger.info(f"📊 {recipe.title[:50]}")
                logger.info(f"   SQLite: {sqlite_total_cal:.0f} cal (per serving: {sqlite_per_serving_cal:.0f} cal)")
                logger.info(f"   Calculated: {calculated['total_calories']:.0f} cal (per serving: {per_serving_calories:.0f} cal)")
                logger.info(f"   Difference: {diff_percent:.1f}% - FIXING")
                
                # Update recipe with calculated values
                recipe.per_serving_calories = per_serving_calories
                recipe.per_serving_protein = per_serving_protein
                recipe.per_serving_carbs = per_serving_carbs
                recipe.per_serving_fat = per_serving_fats
                recipe.per_serving_fiber = per_serving_fiber
                recipe.per_serving_sodium = per_serving_sodium
                
                recipe.total_calories = calculated['total_calories']
                recipe.total_protein = calculated['total_protein']
                recipe.total_carbs = calculated['total_carbs']
                recipe.total_fat = calculated['total_fats']
                recipe.total_fiber = calculated['total_fiber']
                recipe.total_sodium = calculated['total_sodium']
                
                self.db.add(recipe)
                self.fixed_count += 1
                return True
        
        self.checked_count += 1
        return False
    
    def verify_all_recipes(self):
        """Verify all recipes"""
        logger.info("🔍 Verifying nutrition values from ingredients...")
        
        recipes = self.db.query(Recipe).all()
        total = len(recipes)
        
        logger.info(f"Found {total} recipes to verify")
        
        for i, recipe in enumerate(recipes, 1):
            try:
                self.verify_and_fix_recipe(recipe)
                
                if i % 50 == 0:
                    self.db.commit()
                    logger.info(f"Progress: {i}/{total} recipes checked...")
                    
            except Exception as e:
                logger.error(f"Error verifying {recipe.title}: {e}")
                continue
        
        # Final commit
        self.db.commit()
        
        logger.info(f"\n📊 Verification Summary:")
        logger.info(f"   Total recipes: {total}")
        logger.info(f"   Recipes checked (SQLite values OK): {self.checked_count}")
        logger.info(f"   Recipes fixed (updated from ingredients): {self.fixed_count}")
        logger.info(f"   Recipes skipped (no ingredients): {self.skipped_count}")
        
        return self.fixed_count
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    verifier = NutritionVerifier()
    
    try:
        fixed = verifier.verify_all_recipes()
        
        if fixed > 0:
            logger.info(f"\n🎉 Fixed {fixed} recipes with incorrect nutrition values!")
        else:
            logger.info(f"\n✅ All recipes have correct nutrition values!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        verifier.close()

if __name__ == "__main__":
    main()

