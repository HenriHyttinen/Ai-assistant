#!/usr/bin/env python3
"""
Fix Ingredient Nutrition Data

This script updates ingredient nutritional values with realistic data
instead of the generic 50 cal, 2g protein, 8g carbs, 1g fats values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Ingredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngredientNutritionFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.updated_count = 0

    def get_realistic_nutrition(self, ingredient_name):
        """Get realistic nutritional values for common ingredients"""
        # Common ingredient nutrition per 100g
        nutrition_data = {
            # Proteins
            'chicken': {'calories': 165, 'protein': 31, 'carbs': 0, 'fats': 3.6, 'fiber': 0, 'sugar': 0, 'sodium': 74},
            'beef': {'calories': 250, 'protein': 26, 'carbs': 0, 'fats': 15, 'fiber': 0, 'sugar': 0, 'sodium': 72},
            'pork': {'calories': 242, 'protein': 27, 'carbs': 0, 'fats': 14, 'fiber': 0, 'sugar': 0, 'sodium': 62},
            'fish': {'calories': 206, 'protein': 22, 'carbs': 0, 'fats': 12, 'fiber': 0, 'sugar': 0, 'sodium': 61},
            'salmon': {'calories': 208, 'protein': 25, 'carbs': 0, 'fats': 12, 'fiber': 0, 'sugar': 0, 'sodium': 44},
            'tuna': {'calories': 132, 'protein': 30, 'carbs': 0, 'fats': 1, 'fiber': 0, 'sugar': 0, 'sodium': 37},
            'shrimp': {'calories': 99, 'protein': 24, 'carbs': 0, 'fats': 0.3, 'fiber': 0, 'sugar': 0, 'sodium': 111},
            'eggs': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fats': 11, 'fiber': 0, 'sugar': 1.1, 'sodium': 124},
            
            # Dairy
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5, 'fats': 1, 'fiber': 0, 'sugar': 5, 'sodium': 44},
            'cheese': {'calories': 113, 'protein': 7, 'carbs': 1, 'fats': 9, 'fiber': 0, 'sugar': 1, 'sodium': 621},
            'butter': {'calories': 717, 'protein': 0.9, 'carbs': 0.1, 'fats': 81, 'fiber': 0, 'sugar': 0.1, 'sodium': 11},
            'cream': {'calories': 345, 'protein': 2.1, 'carbs': 2.8, 'fats': 37, 'fiber': 0, 'sugar': 2.8, 'sodium': 11},
            'yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fats': 0.4, 'fiber': 0, 'sugar': 3.6, 'sodium': 36},
            
            # Grains
            'rice': {'calories': 130, 'protein': 2.7, 'carbs': 28, 'fats': 0.3, 'fiber': 0.4, 'sugar': 0.1, 'sodium': 1},
            'pasta': {'calories': 131, 'protein': 5, 'carbs': 25, 'fats': 1.1, 'fiber': 1.8, 'sugar': 0.6, 'sodium': 1},
            'bread': {'calories': 265, 'protein': 9, 'carbs': 49, 'fats': 3.2, 'fiber': 2.7, 'sugar': 5.7, 'sodium': 681},
            'flour': {'calories': 364, 'protein': 10, 'carbs': 76, 'fats': 1, 'fiber': 2.7, 'sugar': 0.3, 'sodium': 2},
            'oats': {'calories': 389, 'protein': 17, 'carbs': 66, 'fats': 7, 'fiber': 11, 'sugar': 1, 'sodium': 2},
            
            # Vegetables
            'onion': {'calories': 40, 'protein': 1.1, 'carbs': 9.3, 'fats': 0.1, 'fiber': 1.7, 'sugar': 4.2, 'sodium': 4},
            'garlic': {'calories': 149, 'protein': 6.4, 'carbs': 33, 'fats': 0.5, 'fiber': 2.1, 'sugar': 1, 'sodium': 17},
            'tomato': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fats': 0.2, 'fiber': 1.2, 'sugar': 2.6, 'sodium': 5},
            'carrot': {'calories': 41, 'protein': 0.9, 'carbs': 9.6, 'fats': 0.2, 'fiber': 2.8, 'sugar': 4.7, 'sodium': 69},
            'potato': {'calories': 77, 'protein': 2, 'carbs': 17, 'fats': 0.1, 'fiber': 2.2, 'sugar': 0.8, 'sodium': 6},
            'spinach': {'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fats': 0.4, 'fiber': 2.2, 'sugar': 0.4, 'sodium': 79},
            'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 7, 'fats': 0.4, 'fiber': 2.6, 'sugar': 1.5, 'sodium': 33},
            'mushroom': {'calories': 22, 'protein': 3.1, 'carbs': 3.3, 'fats': 0.3, 'fiber': 1, 'sugar': 2, 'sodium': 5},
            'pepper': {'calories': 20, 'protein': 0.9, 'carbs': 4.6, 'fats': 0.2, 'fiber': 1.5, 'sugar': 2.4, 'sodium': 3},
            'lettuce': {'calories': 15, 'protein': 1.4, 'carbs': 2.9, 'fats': 0.2, 'fiber': 1.3, 'sugar': 0.8, 'sodium': 28},
            
            # Fruits
            'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fats': 0.2, 'fiber': 2.4, 'sugar': 10, 'sodium': 1},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fats': 0.3, 'fiber': 2.6, 'sugar': 12, 'sodium': 1},
            'orange': {'calories': 47, 'protein': 0.9, 'carbs': 12, 'fats': 0.1, 'fiber': 2.4, 'sugar': 9, 'sodium': 0},
            'lemon': {'calories': 29, 'protein': 1.1, 'carbs': 9, 'fats': 0.3, 'fiber': 2.8, 'sugar': 2.5, 'sodium': 2},
            'lime': {'calories': 30, 'protein': 0.7, 'carbs': 11, 'fats': 0.2, 'fiber': 2.8, 'sugar': 1.7, 'sodium': 2},
            
            # Legumes
            'lentils': {'calories': 116, 'protein': 9, 'carbs': 20, 'fats': 0.4, 'fiber': 8, 'sugar': 1.8, 'sodium': 2},
            'beans': {'calories': 127, 'protein': 8.7, 'carbs': 22.8, 'fats': 0.5, 'fiber': 6.4, 'sugar': 0.3, 'sodium': 2},
            'chickpeas': {'calories': 164, 'protein': 8.9, 'carbs': 27, 'fats': 2.6, 'fiber': 8, 'sugar': 4.8, 'sodium': 7},
            
            # Nuts
            'almonds': {'calories': 579, 'protein': 21, 'carbs': 22, 'fats': 50, 'fiber': 12, 'sugar': 4.4, 'sodium': 1},
            'walnuts': {'calories': 654, 'protein': 15, 'carbs': 14, 'fats': 65, 'fiber': 6.7, 'sugar': 2.6, 'sodium': 2},
            'peanuts': {'calories': 567, 'protein': 26, 'carbs': 16, 'fats': 49, 'fiber': 8.5, 'sugar': 4.7, 'sodium': 18},
            
            # Oils
            'olive oil': {'calories': 884, 'protein': 0, 'carbs': 0, 'fats': 100, 'fiber': 0, 'sugar': 0, 'sodium': 2},
            'vegetable oil': {'calories': 884, 'protein': 0, 'carbs': 0, 'fats': 100, 'fiber': 0, 'sugar': 0, 'sodium': 0},
            'coconut oil': {'calories': 862, 'protein': 0, 'carbs': 0, 'fats': 100, 'fiber': 0, 'sugar': 0, 'sodium': 0},
            
            # Spices
            'salt': {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0, 'fiber': 0, 'sugar': 0, 'sodium': 38758},
            'pepper': {'calories': 251, 'protein': 10, 'carbs': 64, 'fats': 3.3, 'fiber': 25, 'sugar': 0.6, 'sodium': 20},
            'sugar': {'calories': 387, 'protein': 0, 'carbs': 100, 'fats': 0, 'fiber': 0, 'sugar': 100, 'sodium': 1},
            'honey': {'calories': 304, 'protein': 0.3, 'carbs': 82, 'fats': 0, 'fiber': 0.2, 'sugar': 82, 'sodium': 4},
        }
        
        # Try to match ingredient name to nutrition data
        ingredient_lower = ingredient_name.lower()
        
        for key, nutrition in nutrition_data.items():
            if key in ingredient_lower:
                return nutrition
        
        # Default nutrition for unknown ingredients
        return {'calories': 50, 'protein': 2, 'carbs': 8, 'fats': 1, 'fiber': 1, 'sugar': 2, 'sodium': 10}

    def fix_ingredient_nutrition(self):
        """Fix nutritional values for all ingredients"""
        logger.info("🍎 Starting to fix ingredient nutrition data...")
        
        ingredients = self.db.query(Ingredient).all()
        logger.info(f"Found {len(ingredients)} ingredients to update")
        
        for ingredient in ingredients:
            # Get realistic nutrition data
            nutrition = self.get_realistic_nutrition(ingredient.name)
            
            # Update ingredient with realistic values
            ingredient.calories = nutrition['calories']
            ingredient.protein = nutrition['protein']
            ingredient.carbs = nutrition['carbs']
            ingredient.fats = nutrition['fats']
            ingredient.fiber = nutrition['fiber']
            ingredient.sugar = nutrition['sugar']
            ingredient.sodium = nutrition['sodium']
            
            self.updated_count += 1
            
            if self.updated_count % 50 == 0:
                logger.info(f"Updated {self.updated_count} ingredients...")
        
        self.db.commit()
        
        logger.info(f"🎉 Updated {self.updated_count} ingredients with realistic nutrition data!")
        return self.updated_count

    def verify_nutrition_fix(self):
        """Verify that nutrition data is now realistic"""
        logger.info("🔍 Verifying nutrition data...")
        
        # Check a few ingredients
        sample_ingredients = ['chicken', 'onion', 'tomato', 'rice', 'cheese']
        
        for name in sample_ingredients:
            ingredient = self.db.query(Ingredient).filter(Ingredient.name.like(f'%{name}%')).first()
            if ingredient:
                print(f"\n🥕 {ingredient.name}:")
                print(f"  Calories: {ingredient.calories}")
                print(f"  Protein: {ingredient.protein}g")
                print(f"  Carbs: {ingredient.carbs}g")
                print(f"  Fats: {ingredient.fats}g")

    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to fix ingredient nutrition"""
    fixer = IngredientNutritionFixer()
    
    try:
        updated_count = fixer.fix_ingredient_nutrition()
        fixer.verify_nutrition_fix()
        
        logger.info(f"🎉 SUCCESS! Updated {updated_count} ingredients with realistic nutrition data!")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()


