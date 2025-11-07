#!/usr/bin/env python3
"""
Recalculate Recipe Nutrition from Ingredients

This script:
1. Goes through all recipes
2. Calculates nutrition from their ingredients
3. Updates per-serving and total nutrition values
4. Ensures recipes have proper nutrition data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeNutritionRecalculator:
    def __init__(self):
        self.db = SessionLocal()
        self.recalculated_count = 0
        self.skipped_count = 0
        
    def recalculate_recipe_nutrition(self, recipe):
        """Recalculate nutrition for a single recipe from its ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        total_fiber = 0
        total_sodium = 0
        
        ingredient_count = 0
        
        for recipe_ingredient in recipe.ingredients:
            ing_obj = recipe_ingredient.ingredient
            if not ing_obj:
                continue
            
            # Check if ingredient has a valid name
            ing_name = (ing_obj.name or '').strip()
            if not ing_name or len(ing_name) < 2:
                continue
            
            # Get quantity in grams
            quantity_g = recipe_ingredient.quantity or 0
            if quantity_g <= 0:
                continue
            
            # Get nutrition per 100g from ingredient
            cal_per_100g = ing_obj.calories or 0
            prot_per_100g = ing_obj.protein or 0
            carbs_per_100g = ing_obj.carbs or 0
            fats_per_100g = ing_obj.fats or 0
            fiber_per_100g = ing_obj.fiber or 0
            sodium_per_100g = ing_obj.sodium or 0
            
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
        
        # Skip if no valid ingredients
        if ingredient_count == 0:
            self.skipped_count += 1
            return False
        
        # Round totals
        total_calories = round(total_calories, 1)
        total_protein = round(total_protein, 1)
        total_carbs = round(total_carbs, 1)
        total_fats = round(total_fats, 1)
        total_fiber = round(total_fiber, 1)
        total_sodium = round(total_sodium, 1)
        
        # Get servings
        servings = recipe.servings or 1
        if servings <= 0:
            servings = 1
            recipe.servings = 1
        
        # Calculate per-serving values
        per_serving_calories = round(total_calories / servings, 1)
        per_serving_protein = round(total_protein / servings, 1)
        per_serving_carbs = round(total_carbs / servings, 1)
        per_serving_fats = round(total_fats / servings, 1)
        per_serving_fiber = round(total_fiber / servings, 1)
        per_serving_sodium = round(total_sodium / servings, 1)
        
        # Update recipe nutrition
        recipe.total_calories = total_calories
        recipe.total_protein = total_protein
        recipe.total_carbs = total_carbs
        recipe.total_fat = total_fats
        recipe.total_fiber = total_fiber
        recipe.total_sodium = total_sodium
        
        recipe.per_serving_calories = per_serving_calories
        recipe.per_serving_protein = per_serving_protein
        recipe.per_serving_carbs = per_serving_carbs
        recipe.per_serving_fat = per_serving_fats
        recipe.per_serving_fiber = per_serving_fiber
        recipe.per_serving_sodium = per_serving_sodium
        
        self.recalculated_count += 1
        
        if self.recalculated_count % 50 == 0:
            logger.info(f"Recalculated {self.recalculated_count} recipes...")
        
        return True
    
    def recalculate_all_recipes(self):
        """Recalculate nutrition for all recipes"""
        logger.info("🔍 Starting nutrition recalculation from ingredients...")
        
        recipes = self.db.query(Recipe).filter(Recipe.is_active == True).all()
        logger.info(f"Found {len(recipes)} active recipes to process")
        
        for recipe in recipes:
            self.recalculate_recipe_nutrition(recipe)
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"🎉 Recalculation complete!")
        logger.info(f"   ✅ Recalculated {self.recalculated_count} recipes")
        logger.info(f"   ⚠️  Skipped {self.skipped_count} recipes (no valid ingredients)")
        
        return self.recalculated_count
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    recalculator = RecipeNutritionRecalculator()
    
    try:
        recalculated_count = recalculator.recalculate_all_recipes()
        
        logger.info(f"🎉 SUCCESS!")
        logger.info(f"   Recalculated {recalculated_count} recipes with nutrition data")
        
    except Exception as e:
        logger.error(f"❌ Recalculation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        recalculator.close()

if __name__ == "__main__":
    main()

