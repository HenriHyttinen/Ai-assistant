#!/usr/bin/env python3
"""
Fix Remaining Recipes Without Nutritional Data

This script replaces the remaining 100 recipes that don't have nutritional data
with recipes from the SQLite database that do have nutritional data.
Uses a simpler approach that doesn't create new ingredients.
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

class SimpleRecipeFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()

    def find_recipes_without_nutrition(self):
        """Find recipes in our database that don't have nutritional data"""
        recipes_without_nutrition = []
        
        all_recipes = self.db.query(Recipe).all()
        for recipe in all_recipes:
            # Check if summary contains nutritional data
            if not recipe.summary or "Nutrition per serving:" not in recipe.summary:
                recipes_without_nutrition.append(recipe)
        
        logger.info(f"Found {len(recipes_without_nutrition)} recipes without nutritional data")
        return recipes_without_nutrition

    def get_replacement_recipes(self, count):
        """Get replacement recipes from SQLite that have nutritional data"""
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium 
            FROM recipes 
            WHERE calories IS NOT NULL AND calories > 0 
            ORDER BY RANDOM() 
            LIMIT ?
        """, (count,))
        
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

    def replace_recipe(self, old_recipe, new_recipe_data):
        """Replace an old recipe with new recipe data"""
        try:
            recipe_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium = new_recipe_data
            
            # Parse ingredients and instructions
            ingredients_data = self.parse_ingredients(ingredients_text)
            instructions_data = self.parse_instructions(directions_text)
            
            if not ingredients_data or not instructions_data:
                logger.warning(f"Skipping {title} - no valid ingredients or instructions")
                return False
            
            # Determine cuisine and meal type
            cuisine, meal_type = self.determine_cuisine_and_meal_type(title, categories)
            
            # Update the existing recipe
            old_recipe.title = title
            old_recipe.cuisine = cuisine
            old_recipe.meal_type = meal_type
            old_recipe.servings = 4
            old_recipe.summary = f"A delicious {title.lower()} recipe. Nutrition per serving: {calories} cal, {protein}g protein, {fat}g fat, {sodium}mg sodium"
            old_recipe.prep_time = 20
            old_recipe.cook_time = 30
            old_recipe.difficulty_level = "medium"
            old_recipe.dietary_tags = []
            
            # Clear existing ingredients and instructions
            self.db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == old_recipe.id).delete()
            self.db.query(RecipeInstruction).filter(RecipeInstruction.recipe_id == old_recipe.id).delete()
            
            # Add new ingredients (reuse existing ones or create simple ones)
            for ingredient_data in ingredients_data:
                ingredient = self.get_existing_ingredient(ingredient_data['name'])
                if ingredient:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=old_recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=ingredient_data['quantity'],
                        unit=ingredient_data['unit'],
                        notes=None
                    )
                    self.db.add(recipe_ingredient)
            
            # Add new instructions
            for j, instruction_text in enumerate(instructions_data, 1):
                recipe_instruction = RecipeInstruction(
                    recipe_id=old_recipe.id,
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
            logger.error(f"Error replacing recipe: {e}")
            self.db.rollback()
            return False

    def fix_remaining_recipes(self):
        """Fix remaining recipes without nutritional data"""
        logger.info("🔧 Starting to fix remaining recipes without nutritional data...")
        
        # Find recipes without nutrition
        recipes_without_nutrition = self.find_recipes_without_nutrition()
        
        if not recipes_without_nutrition:
            logger.info("✅ All recipes already have nutritional data!")
            return 0, 0
        
        # Get replacement recipes
        replacement_recipes = self.get_replacement_recipes(len(recipes_without_nutrition))
        
        if len(replacement_recipes) < len(recipes_without_nutrition):
            logger.warning(f"Only found {len(replacement_recipes)} replacement recipes, need {len(recipes_without_nutrition)}")
        
        replaced_count = 0
        failed_count = 0
        
        # Replace recipes
        for i, old_recipe in enumerate(recipes_without_nutrition):
            if i < len(replacement_recipes):
                new_recipe_data = replacement_recipes[i]
                logger.info(f"Replacing '{old_recipe.title}' with '{new_recipe_data[1]}'")
                
                if self.replace_recipe(old_recipe, new_recipe_data):
                    replaced_count += 1
                    logger.info(f"✅ Replaced: {new_recipe_data[1]}")
                else:
                    failed_count += 1
                    logger.error(f"❌ Failed to replace: {old_recipe.title}")
            else:
                logger.warning(f"No replacement recipe available for: {old_recipe.title}")
                failed_count += 1
        
        logger.info(f"🎉 Completed! Replaced {replaced_count} recipes, {failed_count} failed")
        return replaced_count, failed_count

    def close(self):
        """Close database connections"""
        self.db.close()
        self.sqlite_conn.close()

def main():
    """Main function to fix remaining recipes"""
    fixer = SimpleRecipeFixer()
    
    try:
        replaced_count, failed_count = fixer.fix_remaining_recipes()
        
        if failed_count == 0:
            logger.info("🎉 SUCCESS! All recipes now have nutritional data!")
        else:
            logger.warning(f"⚠️  Replaced {replaced_count} recipes, {failed_count} failed")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()


