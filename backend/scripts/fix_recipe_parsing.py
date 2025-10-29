#!/usr/bin/env python3
"""
Fix recipe ingredient parsing and quantities by properly converting units to grams
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeParsingFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = None
        self.sqlite_cursor = None
        
    def connect_sqlite(self):
        """Connect to the original SQLite database"""
        import sqlite3
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()
    
    def parse_ingredients_properly(self, ingredients_text):
        """Parse ingredients text with proper unit recognition"""
        if not ingredients_text:
            return []
        
        ingredients = []
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Ingredient info:'):
                continue
            
            # Look for quantity and unit patterns
            # Pattern: number + optional fraction + unit + ingredient name
            match = re.match(r'^(\d+(?:\s+\d+/\d+)?)\s+(cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|pound|pounds|lb|ounce|ounces|oz|clove|cloves|slice|slices|piece|pieces|large|medium|small)\s+(.+)$', line, re.IGNORECASE)
            
            if match:
                quantity_str = match.group(1)
                unit = match.group(2).lower()
                ingredient_name = match.group(3).strip()
                
                # Parse quantity (handle fractions)
                quantity = self.parse_quantity(quantity_str)
                
                # Convert to grams
                grams = self.convert_to_grams(quantity, unit, ingredient_name)
                
                ingredients.append({
                    'name': ingredient_name,
                    'quantity': grams,
                    'unit': 'g'
                })
            else:
                # Fallback: try to extract just a number at the start
                match = re.match(r'^(\d+(?:\.\d+)?)\s+(.+)$', line)
                if match:
                    quantity = float(match.group(1))
                    ingredient_name = match.group(2).strip()
                    
                    # Default to piece if no unit found
                    grams = self.convert_to_grams(quantity, 'piece')
                    
                    ingredients.append({
                        'name': ingredient_name,
                        'quantity': grams,
                        'unit': 'g'
                    })
        
        return ingredients
    
    def parse_quantity(self, quantity_str):
        """Parse quantity string, handling fractions"""
        if '/' in quantity_str:
            # Handle fractions like "1 1/2" or "1/2"
            parts = quantity_str.split()
            if len(parts) == 2:
                whole = float(parts[0])
                frac_parts = parts[1].split('/')
                fraction = float(frac_parts[0]) / float(frac_parts[1])
                return whole + fraction
            else:
                # Just a fraction like "1/2"
                frac_parts = parts[0].split('/')
                return float(frac_parts[0]) / float(frac_parts[1])
        else:
            return float(quantity_str)
    
    def convert_to_grams(self, quantity, unit, ingredient_name=""):
        """Convert various units to grams with ingredient-specific logic"""
        unit = unit.lower().strip()
        ingredient_name = ingredient_name.lower()
        
        # Volume conversions (approximate)
        if unit in ['cup', 'cups']:
            return quantity * 240  # 1 cup = 240ml
        elif unit in ['tablespoon', 'tablespoons', 'tbsp']:
            return quantity * 15   # 1 tbsp = 15ml
        elif unit in ['teaspoon', 'teaspoons', 'tsp']:
            return quantity * 5    # 1 tsp = 5ml
        elif unit == 'ml':
            return quantity
        elif unit in ['l', 'liter']:
            return quantity * 1000
        
        # Weight conversions
        elif unit in ['pound', 'pounds', 'lb']:
            return quantity * 453.592  # 1 lb = 453.592g
        elif unit in ['ounce', 'ounces', 'oz']:
            return quantity * 28.3495  # 1 oz = 28.3495g
        elif unit in ['kg', 'kilogram']:
            return quantity * 1000
        elif unit in ['g', 'gram', 'grams']:
            return quantity
        
        # Count-based conversions (ingredient-specific)
        elif unit in ['clove', 'cloves']:
            return quantity * 3    # 1 garlic clove ≈ 3g
        elif unit in ['slice', 'slices']:
            return quantity * 25   # 1 slice bread ≈ 25g
        elif unit in ['piece', 'pieces']:
            return quantity * 50   # 1 piece ≈ 50g
        elif unit in ['large']:
            # Ingredient-specific large sizes
            if 'egg' in ingredient_name:
                return quantity * 50   # 1 large egg ≈ 50g
            elif 'bell pepper' in ingredient_name or 'pepper' in ingredient_name:
                return quantity * 200  # 1 large bell pepper ≈ 200g
            elif 'onion' in ingredient_name:
                return quantity * 200  # 1 large onion ≈ 200g
            elif 'tomato' in ingredient_name:
                return quantity * 150  # 1 large tomato ≈ 150g
            else:
                return quantity * 100  # Default large item
        elif unit in ['medium']:
            if 'egg' in ingredient_name:
                return quantity * 40   # 1 medium egg ≈ 40g
            elif 'bell pepper' in ingredient_name or 'pepper' in ingredient_name:
                return quantity * 150  # 1 medium bell pepper ≈ 150g
            elif 'onion' in ingredient_name:
                return quantity * 150  # 1 medium onion ≈ 150g
            elif 'tomato' in ingredient_name:
                return quantity * 100  # 1 medium tomato ≈ 100g
            else:
                return quantity * 80   # Default medium item
        elif unit in ['small']:
            if 'egg' in ingredient_name:
                return quantity * 30   # 1 small egg ≈ 30g
            elif 'bell pepper' in ingredient_name or 'pepper' in ingredient_name:
                return quantity * 100  # 1 small bell pepper ≈ 100g
            elif 'onion' in ingredient_name:
                return quantity * 100  # 1 small onion ≈ 100g
            elif 'tomato' in ingredient_name:
                return quantity * 60   # 1 small tomato ≈ 60g
            else:
                return quantity * 60   # Default small item
        else:
            # Default: assume it's already in grams
            return quantity
    
    def fix_all_recipes(self):
        """Fix all recipes by re-parsing ingredients from SQLite"""
        logger.info("🔧 Re-parsing all recipes from SQLite...")
        
        self.connect_sqlite()
        
        # Get all recipes from SQLite
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, "desc", rating, image
            FROM recipes
            WHERE calories IS NOT NULL AND calories >= 100
        """)
        sqlite_recipes = self.sqlite_cursor.fetchall()
        
        # Get our imported recipes
        imported_recipes = self.db.query(Recipe).all()
        recipe_map = {recipe.title: recipe for recipe in imported_recipes}
        
        fixed_count = 0
        
        for sqlite_recipe in sqlite_recipes:
            sqlite_id, title, ingredients_text, directions, categories, calories, protein, fat, sodium, desc, rating, image = sqlite_recipe
            
            if title in recipe_map:
                recipe = recipe_map[title]
                
                try:
                    # Clear existing ingredients
                    for ri in recipe.ingredients:
                        self.db.delete(ri)
                    
                    # Parse ingredients properly
                    parsed_ingredients = self.parse_ingredients_properly(ingredients_text)
                    
                    # Add new ingredients
                    for ing_data in parsed_ingredients:
                        ingredient = self.get_or_create_ingredient(ing_data['name'])
                        
                        recipe_ingredient = RecipeIngredient(
                            recipe_id=recipe.id,
                            ingredient_id=ingredient.id,
                            quantity=ing_data['quantity'],
                            unit=ing_data['unit']
                        )
                        self.db.add(recipe_ingredient)
                    
                    fixed_count += 1
                    if fixed_count % 50 == 0:
                        logger.info(f"Fixed {fixed_count} recipes...")
                        
                except Exception as e:
                    logger.error(f"Error fixing recipe {title}: {e}")
                    continue
        
        try:
            self.db.commit()
            logger.info(f"✅ Fixed {fixed_count} recipes!")
            
            # Verify fixes
            self.verify_fixes()
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise
    
    def get_or_create_ingredient(self, name):
        """Get or create ingredient"""
        import uuid
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == name).first()
        if not ingredient:
            # Create with default nutrition values
            ingredient = Ingredient(
                id=str(uuid.uuid4()),
                name=name,
                category='other',
                unit='g',
                calories=50.0,  # Default values
                protein=2.0,
                carbs=8.0,
                fats=1.0
            )
            self.db.add(ingredient)
        return ingredient
    
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
    fixer = RecipeParsingFixer()
    fixer.fix_all_recipes()

if __name__ == "__main__":
    main()
