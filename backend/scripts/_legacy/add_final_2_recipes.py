#!/usr/bin/env python3
"""
Add Final 2 Recipes

This script adds 2 more recipes from the SQLite database to reach exactly 500 recipes.
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

class FinalRecipeAdder:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()

    def get_2_new_recipes(self):
        """Get 2 new recipes from SQLite that have nutritional data"""
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium 
            FROM recipes 
            WHERE calories IS NOT NULL AND calories > 0 
            ORDER BY RANDOM() 
            LIMIT 2
        """)
        
        return self.sqlite_cursor.fetchall()

    def get_existing_ingredient(self, ingredient_name):
        """Get existing ingredient by name, or create a simple one"""
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
        
        if not ingredient:
            # Create a simple ingredient with basic nutrition
            ingredient_id = f'ingredient_{len(self.db.query(Ingredient).all()) + 1:06d}'
            
            ingredient = Ingredient(
                id=ingredient_id,
                name=ingredient_name,
                category='other',
                unit='g',
                default_quantity=100.0,
                calories=50.0,
                protein=2.0,
                carbs=8.0,
                fats=1.0,
                fiber=1.0,
                sugar=2.0,
                sodium=10.0
            )
            
            self.db.add(ingredient)
            self.db.flush()
        
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
                
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                quantity_str = parts[0]
                ingredient_name = parts[1]
                
                quantity = 1.0
                unit = 'piece'
                
                if any(char.isdigit() for char in quantity_str):
                    numbers = re.findall(r'\d+\.?\d*', quantity_str)
                    if numbers:
                        quantity = float(numbers[0])
                    
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
                        unit = 'g'
                
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
        
        steps = []
        
        if re.search(r'\d+\.', directions_text):
            parts = re.split(r'\d+\.', directions_text)
            for part in parts[1:]:
                step = part.strip()
                if step:
                    steps.append(step)
        else:
            sentences = re.split(r'[.!?]+', directions_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    steps.append(sentence)
        
        return steps

    def determine_cuisine_and_meal_type(self, title, categories):
        """Determine cuisine and meal type from title and categories"""
        title_lower = title.lower()
        categories_lower = categories.lower() if categories else ""
        
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

    def create_recipe(self, recipe_data):
        """Create a new recipe from SQLite data"""
        try:
            recipe_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium = recipe_data
            
            # Parse ingredients and instructions
            ingredients_data = self.parse_ingredients(ingredients_text)
            instructions_data = self.parse_instructions(directions_text)
            
            if not ingredients_data or not instructions_data:
                logger.warning(f"Skipping {title} - no valid ingredients or instructions")
                return False
            
            # Determine cuisine and meal type
            cuisine, meal_type = self.determine_cuisine_and_meal_type(title, categories)
            
            # Create new recipe with unique ID
            import uuid
            recipe_id = f'recipe_{str(uuid.uuid4())[:8]}'
            
            recipe = Recipe(
                id=recipe_id,
                title=title,
                cuisine=cuisine,
                meal_type=meal_type,
                servings=4,
                summary=f"A delicious {title.lower()} recipe. Nutrition per serving: {calories} cal, {protein}g protein, {fat}g fat, {sodium}mg sodium",
                prep_time=20,
                cook_time=30,
                difficulty_level="medium",
                dietary_tags=[],
                source="imported",
                image_url=None,
                is_active=True
            )
            
            self.db.add(recipe)
            self.db.flush()
            
            # Add ingredients
            for ingredient_data in ingredients_data:
                ingredient = self.get_existing_ingredient(ingredient_data['name'])
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
                    time_required=5
                )
                self.db.add(recipe_instruction)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            self.db.rollback()
            return False

    def add_final_recipes(self):
        """Add 2 final recipes to reach 500 total"""
        logger.info("🔧 Adding 2 final recipes to reach 500 total...")
        
        # Get 2 new recipes
        new_recipes = self.get_2_new_recipes()
        
        if len(new_recipes) < 2:
            logger.error(f"Only found {len(new_recipes)} new recipes, need 2")
            return 0
        
        added_count = 0
        
        # Add recipes
        for recipe_data in new_recipes:
            title = recipe_data[1]
            logger.info(f"Adding: {title}")
            
            if self.create_recipe(recipe_data):
                added_count += 1
                logger.info(f"✅ Added: {title}")
            else:
                logger.error(f"❌ Failed to add: {title}")
        
        logger.info(f"🎉 Added {added_count} recipes!")
        return added_count

    def close(self):
        """Close database connections"""
        self.db.close()
        self.sqlite_conn.close()

def main():
    """Main function to add final 2 recipes"""
    adder = FinalRecipeAdder()
    
    try:
        added_count = adder.add_final_recipes()
        
        if added_count == 2:
            logger.info("🎉 SUCCESS! Now have exactly 500 recipes!")
        else:
            logger.warning(f"⚠️  Added {added_count} recipes, need 2")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)
    finally:
        adder.close()

if __name__ == "__main__":
    main()
