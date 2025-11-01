#!/usr/bin/env python3
"""
Verify and Fix Recipe Nutrition Values

This script ensures that all recipes have correct per-serving values
and properly calculated total recipe values based on servings.

Rules:
- Per-serving values are the source of truth (from original recipe data)
- Total recipe values = per_serving * servings
- If per-serving is missing, we cannot create placeholder values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeNutritionVerifier:
    def __init__(self):
        self.db = SessionLocal()
        self.fixed_count = 0
        self.error_count = 0
        self.missing_data_count = 0
        
    def verify_and_fix_all_recipes(self):
        """Verify and fix all recipes in the database"""
        logger.info("🔍 Starting recipe nutrition verification and fix...")
        
        recipes = self.db.query(Recipe).filter(Recipe.is_active == True).all()
        total_recipes = len(recipes)
        logger.info(f"📊 Found {total_recipes} active recipes to verify")
        
        for recipe in recipes:
            try:
                self.verify_and_fix_recipe(recipe)
            except Exception as e:
                logger.error(f"❌ Error processing recipe {recipe.id} ({recipe.title}): {str(e)}")
                self.error_count += 1
                continue
        
        self.db.commit()
        
        logger.info(f"\n✅ Verification complete!")
        logger.info(f"   Fixed: {self.fixed_count} recipes")
        logger.info(f"   Missing data: {self.missing_data_count} recipes")
        logger.info(f"   Errors: {self.error_count} recipes")
        logger.info(f"   Total: {total_recipes} recipes")
        
    def verify_and_fix_recipe(self, recipe):
        """Verify and fix a single recipe's nutrition values
        
        Pattern from import_500_correct_recipes.py:
        - Per-serving values are the source of truth
        - Total values = per_serving * servings
        """
        recipe_servings = recipe.servings or 1
        if recipe_servings <= 0:
            recipe_servings = 1
            recipe.servings = 1
            logger.warning(f"⚠️  Recipe {recipe.id} had invalid servings, set to 1")
        
        # Get per-serving values (source of truth - matching import pattern)
        per_serving_calories = recipe.per_serving_calories
        per_serving_protein = recipe.per_serving_protein
        per_serving_carbs = recipe.per_serving_carbs
        per_serving_fat = recipe.per_serving_fat or recipe.per_serving_fats
        per_serving_sodium = recipe.per_serving_sodium
        
        # Check if we have per-serving data
        has_per_serving_data = (
            per_serving_calories is not None and per_serving_calories > 0
        )
        
        if not has_per_serving_data:
            logger.warning(f"⚠️  Recipe {recipe.id} ({recipe.title}) missing per-serving calories - cannot calculate totals")
            self.missing_data_count += 1
            return
        
        # Calculate total recipe values from per-serving * servings
        # Pattern from import_500_correct_recipes.py (lines 616-619):
        # total_calories = calories * servings
        # total_protein = protein * servings
        # total_fat = fat * servings
        # total_sodium = sodium * servings
        total_calories = per_serving_calories * recipe_servings
        total_protein = (per_serving_protein or 0) * recipe_servings
        total_carbs = (per_serving_carbs or 0) * recipe_servings
        total_fat = (per_serving_fat or 0) * recipe_servings
        total_sodium = (per_serving_sodium or 0) * recipe_servings
        
        # Check if totals need to be updated
        needs_update = False
        
        if recipe.total_calories is None or abs(recipe.total_calories - total_calories) > 0.01:
            recipe.total_calories = total_calories
            needs_update = True
            
        if recipe.total_protein is None or abs(recipe.total_protein - total_protein) > 0.01:
            recipe.total_protein = total_protein
            needs_update = True
            
        if recipe.total_carbs is None or abs(recipe.total_carbs - total_carbs) > 0.01:
            recipe.total_carbs = total_carbs
            needs_update = True
            
        if recipe.total_fat is None or abs(recipe.total_fat - total_fat) > 0.01:
            recipe.total_fat = total_fat
            needs_update = True
            
        if recipe.total_sodium is None or abs(recipe.total_sodium - total_sodium) > 0.01:
            recipe.total_sodium = total_sodium
            needs_update = True
        
        # Ensure per_serving_fat is set if per_serving_fats exists
        if recipe.per_serving_fat is None and recipe.per_serving_fats:
            recipe.per_serving_fat = recipe.per_serving_fats
            needs_update = True
        
        if needs_update:
            logger.info(f"✅ Fixed recipe {recipe.id}: {recipe.title}")
            logger.info(f"   Servings: {recipe_servings}")
            logger.info(f"   Per serving: {per_serving_calories:.1f} cal")
            logger.info(f"   Total recipe: {total_calories:.1f} cal ({per_serving_calories:.1f} × {recipe_servings})")
            self.fixed_count += 1
            self.db.flush()
        else:
            logger.debug(f"✓ Recipe {recipe.id} already has correct values")
    
    def generate_report(self):
        """Generate a report of recipe nutrition data quality"""
        recipes = self.db.query(Recipe).filter(Recipe.is_active == True).all()
        
        has_per_serving = 0
        has_total = 0
        has_both = 0
        missing_both = 0
        
        for recipe in recipes:
            has_per = recipe.per_serving_calories is not None and recipe.per_serving_calories > 0
            has_tot = recipe.total_calories is not None and recipe.total_calories > 0
            
            if has_per and has_tot:
                has_both += 1
            elif has_per:
                has_per_serving += 1
            elif has_tot:
                has_total += 1
            else:
                missing_both += 1
        
        logger.info(f"\n📊 Recipe Nutrition Data Quality Report:")
        logger.info(f"   Recipes with both per-serving and total: {has_both}")
        logger.info(f"   Recipes with only per-serving: {has_per_serving}")
        logger.info(f"   Recipes with only total: {has_total}")
        logger.info(f"   Recipes missing both: {missing_both}")
        logger.info(f"   Total recipes: {len(recipes)}")

if __name__ == "__main__":
    verifier = RecipeNutritionVerifier()
    
    # Generate report first
    logger.info("📊 Generating initial report...")
    verifier.generate_report()
    
    # Verify and fix all recipes
    verifier.verify_and_fix_all_recipes()
    
    # Generate final report
    logger.info("\n📊 Generating final report...")
    verifier.generate_report()

