#!/usr/bin/env python3
"""
Optimize and Calculate Micronutrients

This script:
1. Verifies and fixes macro nutrients (calories, protein, carbs, fats)
2. Ensures calories formula: calories = protein*4 + carbs*4 + fats*9
3. Calculates micronutrients from ingredients (vitamins, minerals)
4. Updates recipes with calculated micronutrients
5. Ensures recipe totals = per_serving * servings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    def __init__(self):
        self.db = SessionLocal()
        self.ingredients_fixed = 0
        self.recipes_fixed = 0
        self.micronutrients_calculated = 0
        
    def verify_calories_formula(self, protein, carbs, fats):
        """Verify calories match formula: calories = protein*4 + carbs*4 + fats*9"""
        calculated = (protein * 4) + (carbs * 4) + (fats * 9)
        return calculated
    
    def fix_ingredient_macros(self, ingredient):
        """Fix ingredient macro nutrients if calories don't match formula"""
        protein = ingredient.protein or 0
        carbs = ingredient.carbs or 0
        fats = ingredient.fats or 0
        calories = ingredient.calories or 0
        
        calculated_calories = self.verify_calories_formula(protein, carbs, fats)
        
        # If difference is significant (>5%), update calories
        if calories > 0 and abs(calories - calculated_calories) / max(calories, 1) > 0.05:
            ingredient.calories = round(calculated_calories, 1)
            self.db.add(ingredient)
            self.ingredients_fixed += 1
            return True
        
        # If calories is 0 but we have macros, calculate it
        if calories == 0 and (protein > 0 or carbs > 0 or fats > 0):
            ingredient.calories = round(calculated_calories, 1)
            self.db.add(ingredient)
            self.ingredients_fixed += 1
            return True
        
        return False
    
    def calculate_recipe_macros_from_ingredients(self, recipe):
        """Calculate macro nutrients from recipe ingredients"""
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
            
            quantity_g = recipe_ingredient.quantity or 0
            if quantity_g <= 0:
                continue
            
            # Calculate multiplier
            multiplier = quantity_g / 100.0
            
            # Macros
            total_calories += (ingredient.calories or 0) * multiplier
            total_protein += (ingredient.protein or 0) * multiplier
            total_carbs += (ingredient.carbs or 0) * multiplier
            total_fats += (ingredient.fats or 0) * multiplier
            total_fiber += (ingredient.fiber or 0) * multiplier
            total_sodium += (ingredient.sodium or 0) * multiplier
            
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
    
    def calculate_recipe_micronutrients_from_ingredients(self, recipe):
        """Calculate micronutrients from recipe ingredients"""
        micronutrients = {
            'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0, 'calcium': 0,
            'vitamin_c': 0, 'magnesium': 0, 'folate': 0, 'zinc': 0,
            'potassium': 0
        }
        
        for recipe_ingredient in recipe.ingredients:
            ingredient = recipe_ingredient.ingredient
            if not ingredient:
                continue
            
            quantity_g = recipe_ingredient.quantity or 0
            if quantity_g <= 0:
                continue
            
            # Calculate multiplier
            multiplier = quantity_g / 100.0
            
            # Sum micronutrients (matching Recipe model fields)
            micronutrients['vitamin_d'] += (ingredient.vitamin_d or 0) * multiplier
            micronutrients['vitamin_b12'] += (ingredient.vitamin_b12 or 0) * multiplier
            micronutrients['iron'] += (ingredient.iron or 0) * multiplier
            micronutrients['calcium'] += (ingredient.calcium or 0) * multiplier
            micronutrients['vitamin_c'] += (ingredient.vitamin_c or 0) * multiplier
            micronutrients['magnesium'] += (ingredient.magnesium or 0) * multiplier
            micronutrients['folate'] += (ingredient.folate or 0) * multiplier
            micronutrients['zinc'] += (ingredient.zinc or 0) * multiplier
            micronutrients['potassium'] += (ingredient.potassium or 0) * multiplier
        
        # Round values
        for key in micronutrients:
            micronutrients[key] = round(micronutrients[key], 2)
        
        return micronutrients
    
    def update_recipe_from_calculations(self, recipe, macros, micronutrients):
        """Update recipe with calculated macros and micronutrients"""
        servings = recipe.servings or 1
        if servings <= 0:
            servings = 1
            recipe.servings = 1
        
        # Update macros (per-serving and total)
        recipe.per_serving_calories = round(macros['total_calories'] / servings, 1)
        recipe.per_serving_protein = round(macros['total_protein'] / servings, 1)
        recipe.per_serving_carbs = round(macros['total_carbs'] / servings, 1)
        recipe.per_serving_fat = round(macros['total_fats'] / servings, 1)
        recipe.per_serving_sodium = round(macros['total_sodium'] / servings, 1)
        
        recipe.total_calories = macros['total_calories']
        recipe.total_protein = macros['total_protein']
        recipe.total_carbs = macros['total_carbs']
        recipe.total_fat = macros['total_fats']
        recipe.total_sodium = macros['total_sodium']
        
        # Update micronutrients (per-serving and total)
        recipe.per_serving_vitamin_d = round(micronutrients['vitamin_d'] / servings, 2)
        recipe.per_serving_vitamin_b12 = round(micronutrients['vitamin_b12'] / servings, 2)
        recipe.per_serving_iron = round(micronutrients['iron'] / servings, 2)
        recipe.per_serving_calcium = round(micronutrients['calcium'] / servings, 2)
        recipe.per_serving_magnesium = round(micronutrients['magnesium'] / servings, 2)
        recipe.per_serving_vitamin_c = round(micronutrients['vitamin_c'] / servings, 2)
        recipe.per_serving_folate = round(micronutrients['folate'] / servings, 2)
        recipe.per_serving_zinc = round(micronutrients['zinc'] / servings, 2)
        recipe.per_serving_potassium = round(micronutrients['potassium'] / servings, 2)
        recipe.per_serving_fiber = round(macros['total_fiber'] / servings, 1)
        
        recipe.total_vitamin_d = round(micronutrients['vitamin_d'], 2)
        recipe.total_vitamin_b12 = round(micronutrients['vitamin_b12'], 2)
        recipe.total_iron = round(micronutrients['iron'], 2)
        recipe.total_calcium = round(micronutrients['calcium'], 2)
        recipe.total_magnesium = round(micronutrients['magnesium'], 2)
        recipe.total_vitamin_c = round(micronutrients['vitamin_c'], 2)
        recipe.total_folate = round(micronutrients['folate'], 2)
        recipe.total_zinc = round(micronutrients['zinc'], 2)
        recipe.total_potassium = round(micronutrients['potassium'], 2)
        recipe.total_fiber = round(macros['total_fiber'], 1)
        
        self.db.add(recipe)
    
    def optimize_all(self):
        """Optimize all ingredients and recipes"""
        logger.info("🔍 Step 1: Fixing ingredient macro nutrients...")
        
        # Fix ingredient macros
        ingredients = self.db.query(Ingredient).all()
        logger.info(f"Found {len(ingredients)} ingredients to check")
        
        for ingredient in ingredients:
            try:
                self.fix_ingredient_macros(ingredient)
            except Exception as e:
                logger.error(f"Error fixing ingredient {ingredient.name}: {e}")
                continue
        
        self.db.commit()
        logger.info(f"✅ Fixed {self.ingredients_fixed} ingredients")
        
        logger.info("🔍 Step 2: Recalculating recipe macros from ingredients...")
        
        # Recalculate recipes from ingredients
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to process")
        
        for i, recipe in enumerate(recipes, 1):
            try:
                # Calculate macros
                macros = self.calculate_recipe_macros_from_ingredients(recipe)
                
                if macros and macros['ingredient_count'] > 0:
                    # Calculate micronutrients
                    micronutrients = self.calculate_recipe_micronutrients_from_ingredients(recipe)
                    
                    # Update recipe
                    self.update_recipe_from_calculations(recipe, macros, micronutrients)
                    self.micronutrients_calculated += 1
                
                if i % 50 == 0:
                    self.db.commit()
                    logger.info(f"Progress: {i}/{len(recipes)} recipes processed...")
                    
            except Exception as e:
                logger.error(f"Error processing recipe {recipe.title}: {e}")
                continue
        
        self.db.commit()
        logger.info(f"✅ Calculated micronutrients for {self.micronutrients_calculated} recipes")
        
        logger.info("🔍 Step 3: Verifying recipe totals match...")
        
        # Verify all totals match
        recipes = self.db.query(Recipe).filter(
            Recipe.per_serving_calories.isnot(None),
            Recipe.per_serving_calories > 0
        ).all()
        
        fixed_totals = 0
        for recipe in recipes:
            servings = recipe.servings or 1
            if servings <= 0:
                servings = 1
                recipe.servings = 1
            
            # Check if totals match
            expected_total_cal = recipe.per_serving_calories * servings
            actual_total_cal = recipe.total_calories or 0
            
            if abs(actual_total_cal - expected_total_cal) > 0.01:
                recipe.total_calories = round(expected_total_cal, 1)
                recipe.total_protein = round((recipe.per_serving_protein or 0) * servings, 1)
                recipe.total_carbs = round((recipe.per_serving_carbs or 0) * servings, 1)
                recipe.total_fat = round((recipe.per_serving_fat or 0) * servings, 1)
                recipe.total_sodium = round((recipe.per_serving_sodium or 0) * servings, 1)
                
                self.db.add(recipe)
                fixed_totals += 1
        
        self.db.commit()
        logger.info(f"✅ Fixed totals for {fixed_totals} recipes")
        
        logger.info(f"\n📊 Final Summary:")
        logger.info(f"   Ingredients fixed: {self.ingredients_fixed}")
        logger.info(f"   Recipes with micronutrients: {self.micronutrients_calculated}")
        logger.info(f"   Recipes with fixed totals: {fixed_totals}")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    optimizer = DatabaseOptimizer()
    
    try:
        optimizer.optimize_all()
        logger.info(f"\n🎉 Database optimization complete!")
        
    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        optimizer.close()

if __name__ == "__main__":
    main()

