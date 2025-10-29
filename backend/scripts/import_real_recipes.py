#!/usr/bin/env python3
"""
Import Real Recipes from recipes.sqlite3

This script imports the 17,766 real recipes from the existing SQLite database
into our PostgreSQL database with proper structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import re
from database import SessionLocal
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealRecipeImporter:
    def __init__(self):
        self.db = SessionLocal()
        self.ingredient_cache = {}
        self.imported_count = 0
        self.failed_count = 0

    def get_or_create_ingredient(self, ingredient_name, category='other'):
        """Get existing ingredient or create new one"""
        if not ingredient_name or ingredient_name.strip() == '':
            return None
            
        # Clean ingredient name
        ingredient_name = ingredient_name.strip()
        
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
        
        if not ingredient:
            ingredient_id = f'ingredient_{len(self.ingredient_cache) + 1:06d}'
            
            # Basic nutritional values (we'll improve these later)
            nutrition_data = {
                'calories': 50,  # Default
                'protein': 2.0,
                'carbs': 8.0,
                'fats': 1.0,
                'fiber': 1.0,
                'sugar': 2.0,
                'sodium': 10.0
            }
            
            ingredient = Ingredient(
                id=ingredient_id,
                name=ingredient_name,
                category=category,
                unit='g',
                default_quantity=100.0,
                calories=nutrition_data['calories'],
                protein=nutrition_data['protein'],
                carbs=nutrition_data['carbs'],
                fats=nutrition_data['fats'],
                fiber=nutrition_data['fiber'],
                sugar=nutrition_data['sugar'],
                sodium=nutrition_data['sodium']
            )
            
            self.db.add(ingredient)
            self.db.flush()
            self.ingredient_cache[ingredient_name] = ingredient
        
        return ingredient

    def parse_ingredients(self, ingredients_text):
        """Parse ingredients text into structured data"""
        if not ingredients_text:
            return []
        
        ingredients = []
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to extract quantity and ingredient
            # This is a simple parser - could be improved
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                quantity_str = parts[0]
                ingredient_name = parts[1]
                
                # Try to extract quantity and unit
                quantity = 1.0
                unit = 'piece'
                
                # Look for common patterns
                if any(char.isdigit() for char in quantity_str):
                    # Extract number
                    numbers = re.findall(r'\d+\.?\d*', quantity_str)
                    if numbers:
                        quantity = float(numbers[0])
                    
                    # Determine unit
                    if 'cup' in quantity_str.lower():
                        unit = 'cup'
                    elif 'tbsp' in quantity_str.lower() or 'tablespoon' in quantity_str.lower():
                        unit = 'tbsp'
                    elif 'tsp' in quantity_str.lower() or 'teaspoon' in quantity_str.lower():
                        unit = 'tsp'
                    elif 'pound' in quantity_str.lower() or 'lb' in quantity_str.lower():
                        unit = 'lb'
                    elif 'ounce' in quantity_str.lower() or 'oz' in quantity_str.lower():
                        unit = 'oz'
                    elif 'clove' in quantity_str.lower():
                        unit = 'clove'
                    elif 'slice' in quantity_str.lower():
                        unit = 'slice'
                    elif 'piece' in quantity_str.lower():
                        unit = 'piece'
                    else:
                        unit = 'g'  # Default to grams
                
                ingredients.append({
                    'name': ingredient_name,
                    'quantity': quantity,
                    'unit': unit
                })
        
        return ingredients

    def parse_instructions(self, directions_text):
        """Parse directions text into structured steps"""
        if not directions_text:
            return []
        
        # Split by numbered steps or periods
        steps = []
        
        # Try to split by numbered steps first
        if re.search(r'\d+\.', directions_text):
            parts = re.split(r'\d+\.', directions_text)
            for part in parts[1:]:  # Skip first empty part
                step = part.strip()
                if step:
                    steps.append(step)
        else:
            # Split by sentences
            sentences = re.split(r'[.!?]+', directions_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:  # Filter out very short fragments
                    steps.append(sentence)
        
        return steps

    def determine_cuisine_and_meal_type(self, title, categories):
        """Determine cuisine and meal type from title and categories"""
        title_lower = title.lower()
        categories_lower = categories.lower() if categories else ""
        
        # Determine cuisine
        cuisine = "International"
        if any(word in title_lower for word in ['italian', 'pasta', 'pizza', 'risotto', 'bruschetta']):
            cuisine = "Italian"
        elif any(word in title_lower for word in ['mexican', 'taco', 'burrito', 'enchilada', 'quesadilla']):
            cuisine = "Mexican"
        elif any(word in title_lower for word in ['chinese', 'kung pao', 'lo mein', 'stir fry']):
            cuisine = "Chinese"
        elif any(word in title_lower for word in ['thai', 'pad thai', 'curry', 'tom yum']):
            cuisine = "Thai"
        elif any(word in title_lower for word in ['japanese', 'sushi', 'ramen', 'tempura', 'miso']):
            cuisine = "Japanese"
        elif any(word in title_lower for word in ['korean', 'kimchi', 'bulgogi', 'bibimbap']):
            cuisine = "Korean"
        elif any(word in title_lower for word in ['indian', 'curry', 'tikka', 'biryani', 'naan']):
            cuisine = "Indian"
        elif any(word in title_lower for word in ['french', 'coq au vin', 'ratatouille', 'crêpe']):
            cuisine = "French"
        elif any(word in title_lower for word in ['german', 'schnitzel', 'bratwurst', 'sauerkraut']):
            cuisine = "German"
        elif any(word in title_lower for word in ['spanish', 'paella', 'tapas', 'gazpacho']):
            cuisine = "Spanish"
        elif any(word in title_lower for word in ['greek', 'moussaka', 'souvlaki', 'tzatziki']):
            cuisine = "Greek"
        elif any(word in title_lower for word in ['middle eastern', 'hummus', 'falafel', 'kebab']):
            cuisine = "Middle Eastern"
        elif any(word in title_lower for word in ['american', 'burger', 'bbq', 'mac and cheese']):
            cuisine = "American"
        
        # Determine meal type
        meal_type = "main_course"
        if any(word in title_lower for word in ['pancake', 'waffle', 'breakfast', 'oat', 'cereal', 'muffin']):
            meal_type = "breakfast"
        elif any(word in title_lower for word in ['salad', 'soup', 'lunch', 'sandwich']):
            meal_type = "lunch"
        elif any(word in title_lower for word in ['dessert', 'cake', 'pie', 'cookie', 'ice cream', 'pudding']):
            meal_type = "dessert"
        elif any(word in title_lower for word in ['snack', 'appetizer', 'dip']):
            meal_type = "snack"
        
        return cuisine, meal_type

    def import_recipes(self, limit=500):
        """Import recipes from SQLite to PostgreSQL"""
        logger.info(f"🍳 Starting to import {limit} real recipes...")
        
        # Clear existing recipes
        logger.info("🧹 Clearing existing recipes...")
        try:
            self.db.query(RecipeIngredient).delete()
            self.db.query(RecipeInstruction).delete()
            self.db.query(Recipe).delete()
            self.db.commit()
        except Exception as e:
            logger.info(f"Tables were already empty: {e}")
            self.db.rollback()
        
        # Connect to SQLite database
        sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get recipes
        sqlite_cursor.execute(f"SELECT id, title, ingredients, directions, categories, calories FROM recipes LIMIT {limit}")
        recipes = sqlite_cursor.fetchall()
        
        logger.info(f"Found {len(recipes)} recipes to import")
        
        for i, (recipe_id, title, ingredients_text, directions_text, categories, calories) in enumerate(recipes, 1):
            try:
                logger.info(f"Importing recipe {i}/{len(recipes)}: {title}")
                
                # Parse ingredients and instructions
                ingredients_data = self.parse_ingredients(ingredients_text)
                instructions_data = self.parse_instructions(directions_text)
                
                if not ingredients_data or not instructions_data:
                    logger.warning(f"Skipping {title} - no valid ingredients or instructions")
                    self.failed_count += 1
                    continue
                
                # Determine cuisine and meal type
                cuisine, meal_type = self.determine_cuisine_and_meal_type(title, categories)
                
                # Create recipe
                recipe = Recipe(
                    id=f"recipe_{recipe_id:06d}",
                    title=title,
                    cuisine=cuisine,
                    meal_type=meal_type,
                    servings=4,  # Default
                    summary=f"A delicious {title.lower()} recipe.",
                    prep_time=20,  # Default
                    cook_time=30,  # Default
                    difficulty_level="medium",  # Default
                    dietary_tags=[]
                )
                
                self.db.add(recipe)
                self.db.flush()
                
                # Add ingredients
                for ingredient_data in ingredients_data:
                    ingredient = self.get_or_create_ingredient(ingredient_data['name'])
                    if ingredient:
                        recipe_ingredient = RecipeIngredient(
                            recipe_id=recipe.id,
                            ingredient_id=ingredient.id,
                            quantity=ingredient_data['quantity'],
                            unit=ingredient_data['unit'],
                            notes=None
                        )
                        self.db.add(recipe_ingredient)
                
                # Add instructions
                for j, instruction_text in enumerate(instructions_data, 1):
                    recipe_instruction = RecipeInstruction(
                        recipe_id=recipe.id,
                        step_number=j,
                        step_title=f"Step {j}",
                        description=instruction_text,
                        ingredients_used=[],
                        time_required=5  # Default
                    )
                    self.db.add(recipe_instruction)
                
                self.db.commit()
                self.imported_count += 1
                logger.info(f"✅ Imported: {title}")
                
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{len(recipes)} recipes imported")
                
            except Exception as e:
                logger.error(f"❌ Error importing recipe '{title}': {e}")
                self.db.rollback()
                self.failed_count += 1
        
        sqlite_conn.close()
        
        logger.info(f"🎉 Completed! Imported {self.imported_count} recipes, {self.failed_count} failed")
        return self.imported_count, self.failed_count

    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to import real recipes"""
    importer = RealRecipeImporter()
    
    try:
        imported_count, failed_count = importer.import_recipes(limit=500)
        
        if failed_count == 0:
            logger.info("🎉 SUCCESS! All 500 recipes imported!")
        else:
            logger.warning(f"⚠️  Imported {imported_count} recipes, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)
    finally:
        importer.close()

if __name__ == "__main__":
    main()
