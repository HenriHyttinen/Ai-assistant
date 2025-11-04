#!/usr/bin/env python3
"""
Fix Remaining Recipes Without Nutrition

This script:
1. Tries to match remaining recipes with SQLite data using fuzzy matching
2. If no match, calculates nutrition from ingredients (if available)
3. Ensures total = per_serving * servings for all recipes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemainingRecipesFixer:
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
        
        self.fixed_count = 0
        
    def normalize_title(self, title):
        """Normalize title for matching"""
        if not title:
            return ""
        import re
        # Remove extra whitespace, convert to lowercase
        title = re.sub(r'\s+', ' ', title.strip().lower())
        # Remove special characters for matching
        title = re.sub(r'[^\w\s]', '', title)
        return title
    
    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a, b).ratio()
    
    def find_best_match(self, recipe_title, nutrition_map):
        """Find best matching recipe from SQLite using fuzzy matching"""
        normalized_title = self.normalize_title(recipe_title)
        best_match = None
        best_score = 0.0
        
        for sqlite_title, nutrition_data in nutrition_map.items():
            score = self.similarity(normalized_title, sqlite_title)
            if score > best_score and score >= 0.7:  # 70% similarity threshold
                best_score = score
                best_match = nutrition_data
        
        return best_match, best_score
    
    def calculate_from_ingredients(self, recipe):
        """Calculate nutrition from recipe ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
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
            
            # Skip if ingredient has no nutrition data
            if cal_per_100g == 0 and prot_per_100g == 0 and carbs_per_100g == 0 and fats_per_100g == 0:
                continue
            
            # Calculate nutrition for this ingredient
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
            'total_fats': round(total_fats, 1)
        }
    
    def fix_remaining_recipes(self):
        """Fix remaining recipes without nutrition"""
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
                nutrition_map[normalized_title] = {
                    'calories': float(calories) if calories else 0,
                    'protein': float(protein) if protein else 0,
                    'fat': float(fat) if fat else 0,
                    'sodium': float(sodium) if sodium else 0,
                    'sqlite_id': sqlite_id,
                    'original_title': title
                }
        
        # Get recipes without nutrition
        recipes_without_nutrition = self.db.query(Recipe).filter(
            (Recipe.per_serving_calories.is_(None)) | 
            (Recipe.per_serving_calories == 0)
        ).all()
        
        logger.info(f"Found {len(recipes_without_nutrition)} recipes without nutrition")
        
        fixed_from_sql = 0
        fixed_from_ingredients = 0
        
        for recipe in recipes_without_nutrition:
            # Try fuzzy matching first
            best_match, score = self.find_best_match(recipe.title, nutrition_map)
            
            if best_match and score >= 0.7:
                # Use SQLite data
                calories = best_match['calories']
                protein = best_match['protein']
                fat = best_match['fat']
                sodium = best_match.get('sodium', 0)
                
                # Get servings
                servings = recipe.servings or 4
                if servings <= 0:
                    servings = 4
                    recipe.servings = 4
                
                # Calculate carbs
                carbs = max(0, (calories - protein*4 - fat*9) / 4)
                
                # Calculate totals
                total_calories = calories * servings
                total_protein = protein * servings
                total_fat = fat * servings
                total_carbs = carbs * servings
                total_sodium = sodium * servings if sodium else 0
                
                # Update recipe
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
                
                fixed_from_sql += 1
                logger.info(f"✅ Matched '{recipe.title[:50]}' (similarity: {score:.2f})")
                
            else:
                # Try to calculate from ingredients
                nutrition = self.calculate_from_ingredients(recipe)
                
                if nutrition:
                    # Get servings
                    servings = recipe.servings or 4
                    if servings <= 0:
                        servings = 4
                        recipe.servings = 4
                    
                    # Calculate per-serving values
                    per_serving_calories = round(nutrition['total_calories'] / servings, 1)
                    per_serving_protein = round(nutrition['total_protein'] / servings, 1)
                    per_serving_carbs = round(nutrition['total_carbs'] / servings, 1)
                    per_serving_fats = round(nutrition['total_fats'] / servings, 1)
                    
                    # Update recipe
                    recipe.per_serving_calories = per_serving_calories
                    recipe.per_serving_protein = per_serving_protein
                    recipe.per_serving_carbs = per_serving_carbs
                    recipe.per_serving_fat = per_serving_fats
                    recipe.per_serving_sodium = 0  # Can't calculate from ingredients
                    
                    recipe.total_calories = nutrition['total_calories']
                    recipe.total_protein = nutrition['total_protein']
                    recipe.total_carbs = nutrition['total_carbs']
                    recipe.total_fat = nutrition['total_fats']
                    recipe.total_sodium = 0
                    
                    fixed_from_ingredients += 1
                    logger.info(f"✅ Calculated from ingredients: '{recipe.title[:50]}'")
                else:
                    logger.warning(f"⚠️  Could not fix: '{recipe.title[:50]}' (no match, no ingredients)")
            
            if (fixed_from_sql + fixed_from_ingredients) % 10 == 0:
                self.db.commit()
                logger.info(f"Progress: {fixed_from_sql + fixed_from_ingredients} recipes fixed...")
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"🎉 Fixed {fixed_from_sql + fixed_from_ingredients} recipes:")
        logger.info(f"   - {fixed_from_sql} from SQLite (fuzzy match)")
        logger.info(f"   - {fixed_from_ingredients} from ingredients")
        
        return fixed_from_sql + fixed_from_ingredients
    
    def verify_all_totals(self):
        """Verify that all recipes have correct total = per_serving * servings"""
        logger.info("🔍 Verifying all recipes have correct totals...")
        
        recipes = self.db.query(Recipe).filter(
            Recipe.per_serving_calories.isnot(None),
            Recipe.per_serving_calories > 0
        ).all()
        
        fixed_count = 0
        
        for recipe in recipes:
            servings = recipe.servings or 1
            if servings <= 0:
                servings = 1
                recipe.servings = 1
            
            # Expected totals
            expected_total_calories = recipe.per_serving_calories * servings
            expected_total_protein = recipe.per_serving_protein * servings if recipe.per_serving_protein else 0
            expected_total_carbs = recipe.per_serving_carbs * servings if recipe.per_serving_carbs else 0
            expected_total_fat = (recipe.per_serving_fat or 0) * servings
            expected_total_sodium = (recipe.per_serving_sodium or 0) * servings
            
            # Check if totals need updating
            needs_update = False
            
            if abs((recipe.total_calories or 0) - expected_total_calories) > 0.01:
                recipe.total_calories = round(expected_total_calories, 1)
                needs_update = True
            
            if abs((recipe.total_protein or 0) - expected_total_protein) > 0.01:
                recipe.total_protein = round(expected_total_protein, 1)
                needs_update = True
            
            if abs((recipe.total_carbs or 0) - expected_total_carbs) > 0.01:
                recipe.total_carbs = round(expected_total_carbs, 1)
                needs_update = True
            
            if abs((recipe.total_fat or 0) - expected_total_fat) > 0.01:
                recipe.total_fat = round(expected_total_fat, 1)
                needs_update = True
            
            if abs((recipe.total_sodium or 0) - expected_total_sodium) > 0.01:
                recipe.total_sodium = round(expected_total_sodium, 1)
                needs_update = True
            
            if needs_update:
                fixed_count += 1
        
        self.db.commit()
        
        logger.info(f"✅ Fixed totals for {fixed_count} recipes")
        return fixed_count
    
    def verify_all_recipes(self):
        """Verify all recipes have nutrition"""
        recipes_with_nutrition = self.db.query(Recipe).filter(
            Recipe.per_serving_calories.isnot(None),
            Recipe.per_serving_calories > 0
        ).count()
        
        total = self.db.query(Recipe).count()
        
        logger.info(f"\n📊 Final Status:")
        logger.info(f"   Total recipes: {total}")
        logger.info(f"   Recipes with nutrition: {recipes_with_nutrition}")
        logger.info(f"   Recipes without nutrition: {total - recipes_with_nutrition}")
        
        return recipes_with_nutrition == total
    
    def close(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        self.db.close()

def main():
    """Main function"""
    fixer = RemainingRecipesFixer()
    
    try:
        # Fix remaining recipes
        fixed = fixer.fix_remaining_recipes()
        
        # Verify all totals are correct
        fixer.verify_all_totals()
        
        # Verify all recipes have nutrition
        all_fixed = fixer.verify_all_recipes()
        
        if all_fixed:
            logger.info(f"\n🎉 SUCCESS! All 500 recipes now have nutrition values!")
        else:
            logger.warning(f"\n⚠️  Some recipes still don't have nutrition values")
        
    except Exception as e:
        logger.error(f"❌ Fixing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()

