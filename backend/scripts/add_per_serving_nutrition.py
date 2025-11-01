#!/usr/bin/env python3
"""
Add per-serving nutrition fields to Recipe model and populate them
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerServingNutritionUpdater:
    def __init__(self):
        self.db = SessionLocal()
        
    def add_per_serving_fields(self):
        """Add per-serving nutrition fields to existing recipes"""
        logger.info("🔧 Adding per-serving nutrition fields...")
        
        recipes = self.db.query(Recipe).all()
        updated_count = 0
        
        for recipe in recipes:
            try:
                # Extract nutrition from summary
                summary = recipe.summary or ""
                
                # Extract per-serving values from summary
                cal_match = re.search(r'Nutrition per serving: (\d+) cal', summary)
                protein_match = re.search(r'(\d+)g protein', summary)
                fat_match = re.search(r'(\d+)g fat', summary)
                sodium_match = re.search(r'(\d+)mg sodium', summary)
                
                if cal_match:
                    per_serving_calories = int(cal_match.group(1))
                    per_serving_protein = int(protein_match.group(1)) if protein_match else 0
                    per_serving_fat = int(fat_match.group(1)) if fat_match else 0
                    per_serving_sodium = int(sodium_match.group(1)) if sodium_match else 0
                    
                    # Calculate carbs (approximate: calories - protein*4 - fat*9) / 4
                    per_serving_carbs = max(0, (per_serving_calories - per_serving_protein*4 - per_serving_fat*9) / 4)
                    
                    # Update recipe with per-serving values
                    recipe.per_serving_calories = per_serving_calories
                    recipe.per_serving_protein = per_serving_protein
                    recipe.per_serving_carbs = per_serving_carbs
                    recipe.per_serving_fat = per_serving_fat
                    recipe.per_serving_sodium = per_serving_sodium
                    
                    # Calculate total recipe values
                    recipe.total_calories = per_serving_calories * recipe.servings
                    recipe.total_protein = per_serving_protein * recipe.servings
                    recipe.total_carbs = per_serving_carbs * recipe.servings
                    recipe.total_fat = per_serving_fat * recipe.servings
                    recipe.total_sodium = per_serving_sodium * recipe.servings
                    
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error updating recipe {recipe.title}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"✅ Updated {updated_count} recipes with per-serving nutrition!")
            
            # Verify updates
            self.verify_updates()
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise
    
    def verify_updates(self):
        """Verify the updates worked"""
        logger.info("🔍 Verifying updates...")
        
        # Check a few recipes
        sample_recipes = self.db.query(Recipe).limit(3).all()
        
        for recipe in sample_recipes:
            print(f"\nRecipe: {recipe.title}")
            print(f"Servings: {recipe.servings}")
            print(f"Per serving: {recipe.per_serving_calories} cal, {recipe.per_serving_protein}g protein, {recipe.per_serving_carbs:.1f}g carbs, {recipe.per_serving_fat}g fat")
            print(f"Total recipe: {recipe.total_calories} cal, {recipe.total_protein}g protein, {recipe.total_carbs:.1f}g carbs, {recipe.total_fat}g fat")

def main():
    updater = PerServingNutritionUpdater()
    updater.add_per_serving_fields()

if __name__ == "__main__":
    main()







