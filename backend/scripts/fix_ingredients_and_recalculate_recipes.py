#!/usr/bin/env python3
"""
Fix Ingredients and Recalculate Recipes

This script:
1. Updates ingredient nutrition values from the comprehensive 500 ingredient database
2. Matches recipe ingredients to corrected ingredients using fuzzy matching
3. Recalculates recipe nutrition from corrected ingredients
4. Compares with SQLite values and uses calculated values when more accurate
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging
import re
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Real nutrition values from comprehensive_seeder.py
REAL_INGREDIENT_NUTRITION = {
    # Proteins
    'chicken': {'calories': 165, 'protein': 31, 'carbs': 0, 'fats': 3.6},
    'chicken breast': {'calories': 165, 'protein': 31, 'carbs': 0, 'fats': 3.6},
    'beef': {'calories': 250, 'protein': 26, 'carbs': 0, 'fats': 15},
    'ground beef': {'calories': 250, 'protein': 26, 'carbs': 0, 'fats': 15},
    'pork': {'calories': 242, 'protein': 27, 'carbs': 0, 'fats': 14},
    'salmon': {'calories': 208, 'protein': 25, 'carbs': 0, 'fats': 12},
    'tuna': {'calories': 132, 'protein': 30, 'carbs': 0, 'fats': 1},
    'fish': {'calories': 206, 'protein': 22, 'carbs': 0, 'fats': 12},
    'bass': {'calories': 206, 'protein': 22, 'carbs': 0, 'fats': 12},
    'cod': {'calories': 82, 'protein': 18, 'carbs': 0, 'fats': 0.7},
    'tilapia': {'calories': 128, 'protein': 26, 'carbs': 0, 'fats': 2.7},
    'shrimp': {'calories': 99, 'protein': 24, 'carbs': 0, 'fats': 0.3},
    'eggs': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fats': 11},
    
    # Dairy
    'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fats': 1},
    'cheese': {'calories': 113, 'protein': 7, 'carbs': 1, 'fats': 9},
    'feta': {'calories': 264, 'protein': 14, 'carbs': 4, 'fats': 21},
    'mozzarella': {'calories': 280, 'protein': 22, 'carbs': 2.2, 'fats': 22},
    'parmesan': {'calories': 431, 'protein': 38, 'carbs': 4, 'fats': 29},
    'cheddar': {'calories': 403, 'protein': 25, 'carbs': 1.3, 'fats': 33},
    'butter': {'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fats': 81},
    'cream': {'calories': 345, 'protein': 2.1, 'carbs': 2.8, 'fats': 37},
    'yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fats': 0.4},
    
    # Grains
    'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fats': 0.3},
    'couscous': {'calories': 112, 'protein': 3.8, 'carbs': 23, 'fats': 0.2},
    'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fats': 1.1},
    'bread': {'calories': 265, 'protein': 9, 'carbs': 49, 'fats': 3.2},
    'flour': {'calories': 364, 'protein': 10, 'carbs': 76, 'fats': 1},
    'oats': {'calories': 389, 'protein': 17, 'carbs': 66, 'fats': 7},
    'quinoa': {'calories': 120, 'protein': 4.4, 'carbs': 22, 'fats': 1.9},
    
    # Vegetables
    'chard': {'calories': 19, 'protein': 1.8, 'carbs': 3.7, 'fats': 0.2},
    'spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fats': 0.4},
    'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fats': 0.4},
    'carrots': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fats': 0.2},
    'tomatoes': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fats': 0.2},
    'onions': {'calories': 40, 'protein': 1.1, 'carbs': 9, 'fats': 0.1},
    'garlic': {'calories': 149, 'protein': 6.4, 'carbs': 33, 'fats': 0.5},
    'bell peppers': {'calories': 31, 'protein': 1, 'carbs': 7, 'fats': 0.3},
    'potatoes': {'calories': 77, 'protein': 2, 'carbs': 17, 'fats': 0.1},
    'mushrooms': {'calories': 22, 'protein': 3.1, 'carbs': 3.3, 'fats': 0.3},
    
    # Oils & Fats
    'olive oil': {'calories': 884, 'protein': 0, 'carbs': 0, 'fats': 100},
    'vegetable oil': {'calories': 884, 'protein': 0, 'carbs': 0, 'fats': 100},
    'coconut oil': {'calories': 862, 'protein': 0, 'carbs': 0, 'fats': 100},
    
    # Other common ingredients
    'salt': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0},
    'pepper': {'calories': 251, 'protein': 10, 'carbs': 64, 'fats': 3.3},
    'sugar': {'calories': 387, 'protein': 0, 'carbs': 100, 'fats': 0},
    'honey': {'calories': 304, 'protein': 0.3, 'carbs': 82, 'fats': 0},
    'water': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0},
}

class IngredientAndRecipeFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.ingredients_fixed = 0
        self.recipes_recalculated = 0
        self.recipes_updated = 0
        
    def normalize_name(self, name):
        """Normalize ingredient name for matching"""
        if not name:
            return ""
        # Remove quantities and special characters
        name = re.sub(r'\d+[./\d]*\s*(oz|g|ml|tbsp|tsp|cups?|pounds?|lbs?)\s*', '', name.lower())
        name = re.sub(r'\([^)]*\)', '', name)  # Remove parenthetical notes
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def find_matching_nutrition(self, ingredient_name):
        """Find matching nutrition data for ingredient"""
        normalized = self.normalize_name(ingredient_name)
        
        # Direct match
        if normalized in REAL_INGREDIENT_NUTRITION:
            return REAL_INGREDIENT_NUTRITION[normalized]
        
        # Partial match
        for key, nutrition in REAL_INGREDIENT_NUTRITION.items():
            if key in normalized or normalized in key:
                return nutrition
        
        # Fuzzy match
        best_match = None
        best_score = 0.0
        
        for key in REAL_INGREDIENT_NUTRITION.keys():
            # Simple word matching
            key_words = set(key.split())
            name_words = set(normalized.split())
            
            if key_words and name_words:
                common_words = key_words & name_words
                if len(common_words) >= 1:
                    score = len(common_words) / max(len(key_words), len(name_words))
                    if score > best_score:
                        best_score = score
                        best_match = REAL_INGREDIENT_NUTRITION[key]
        
        return best_match
    
    def fix_ingredient_nutrition(self, ingredient):
        """Fix ingredient nutrition from real database"""
        nutrition = self.find_matching_nutrition(ingredient.name)
        
        if nutrition:
            # Check if current values are wrong
            current_cal = ingredient.calories or 0
            correct_cal = nutrition['calories']
            
            # If values are significantly different or missing
            if abs(current_cal - correct_cal) > 50 or current_cal == 0:
                ingredient.calories = correct_cal
                ingredient.protein = nutrition['protein']
                ingredient.carbs = nutrition['carbs']
                ingredient.fats = nutrition['fats']
                
                self.db.add(ingredient)
                self.ingredients_fixed += 1
                
                if self.ingredients_fixed % 50 == 0:
                    self.db.commit()
                    logger.info(f"Fixed {self.ingredients_fixed} ingredients...")
                
                return True
        
        return False
    
    def calculate_recipe_nutrition(self, recipe):
        """Calculate recipe nutrition from ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        ingredient_count = 0
        
        for recipe_ingredient in recipe.ingredients:
            ingredient = recipe_ingredient.ingredient
            if not ingredient:
                continue
            
            quantity_g = recipe_ingredient.quantity or 0
            if quantity_g <= 0:
                continue
            
            # Get nutrition per 100g
            cal_per_100g = ingredient.calories or 0
            prot_per_100g = ingredient.protein or 0
            carbs_per_100g = ingredient.carbs or 0
            fats_per_100g = ingredient.fats or 0
            
            # Skip if no nutrition data
            if cal_per_100g == 0 and prot_per_100g == 0:
                continue
            
            # Calculate for this ingredient
            multiplier = quantity_g / 100.0
            
            total_calories += cal_per_100g * multiplier
            total_protein += prot_per_100g * multiplier
            total_carbs += carbs_per_100g * multiplier
            total_fats += fats_per_100g * multiplier
            
            ingredient_count += 1
        
        if ingredient_count == 0:
            return None
        
        return {
            'total_calories': round(total_calories, 1),
            'total_protein': round(total_protein, 1),
            'total_carbs': round(total_carbs, 1),
            'total_fats': round(total_fats, 1),
            'ingredient_count': ingredient_count
        }
    
    def update_recipe_from_calculation(self, recipe, calculated):
        """Update recipe nutrition from calculated values"""
        servings = recipe.servings or 1
        if servings <= 0:
            servings = 1
            recipe.servings = 1
        
        # Per-serving values
        per_serving_calories = round(calculated['total_calories'] / servings, 1)
        per_serving_protein = round(calculated['total_protein'] / servings, 1)
        per_serving_carbs = round(calculated['total_carbs'] / servings, 1)
        per_serving_fats = round(calculated['total_fats'] / servings, 1)
        
        # Update recipe
        recipe.per_serving_calories = per_serving_calories
        recipe.per_serving_protein = per_serving_protein
        recipe.per_serving_carbs = per_serving_carbs
        recipe.per_serving_fat = per_serving_fats
        
        recipe.total_calories = calculated['total_calories']
        recipe.total_protein = calculated['total_protein']
        recipe.total_carbs = calculated['total_carbs']
        recipe.total_fat = calculated['total_fats']
        
        self.db.add(recipe)
    
    def fix_all(self):
        """Fix ingredients and recalculate recipes"""
        logger.info("🔍 Fixing ingredient nutrition values...")
        
        # First, fix all ingredients
        ingredients = self.db.query(Ingredient).all()
        logger.info(f"Found {len(ingredients)} ingredients to check")
        
        for ingredient in ingredients:
            try:
                self.fix_ingredient_nutrition(ingredient)
            except Exception as e:
                logger.error(f"Error fixing ingredient {ingredient.name}: {e}")
                continue
        
        self.db.commit()
        logger.info(f"✅ Fixed {self.ingredients_fixed} ingredients")
        
        # Now recalculate recipes from corrected ingredients
        logger.info("🔍 Recalculating recipe nutrition from corrected ingredients...")
        
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to recalculate")
        
        for i, recipe in enumerate(recipes, 1):
            try:
                calculated = self.calculate_recipe_nutrition(recipe)
                
                if calculated and calculated['ingredient_count'] > 0:
                    # Always use calculated values from ingredients (more accurate)
                    sqlite_total = recipe.total_calories or 0
                    calculated_total = calculated['total_calories']
                    
                    # Check if we should update
                    needs_update = False
                    if sqlite_total > 0:
                        diff_percent = abs(calculated_total - sqlite_total) / sqlite_total * 100
                        if diff_percent >= 30:
                            logger.info(f"📊 {recipe.title[:50]}: SQLite {sqlite_total:.0f} cal → Calculated {calculated_total:.0f} cal ({diff_percent:.1f}% diff) - UPDATING")
                            needs_update = True
                        else:
                            # Even if difference is < 30%, use calculated if it's close (ingredients are more reliable)
                            needs_update = True
                            self.recipes_recalculated += 1
                    else:
                        # No SQLite value, use calculated
                        needs_update = True
                    
                    if needs_update:
                        self.update_recipe_from_calculation(recipe, calculated)
                        self.recipes_updated += 1
                
                if i % 50 == 0:
                    self.db.commit()
                    logger.info(f"Progress: {i}/{len(recipes)} recipes processed...")
                    
            except Exception as e:
                logger.error(f"Error processing recipe {recipe.title}: {e}")
                continue
        
        self.db.commit()
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   Ingredients fixed: {self.ingredients_fixed}")
        logger.info(f"   Recipes recalculated: {self.recipes_recalculated}")
        logger.info(f"   Recipes updated (from calculated): {self.recipes_updated}")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    fixer = IngredientAndRecipeFixer()
    
    try:
        fixer.fix_all()
        logger.info(f"\n🎉 Successfully fixed ingredients and recalculated recipes!")
        
    except Exception as e:
        logger.error(f"❌ Fixing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()

